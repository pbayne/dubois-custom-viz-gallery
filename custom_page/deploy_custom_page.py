#!/usr/bin/env python3
"""Minimal, self-contained helper to deploy an AI/BI (Lakeview) **Custom Page**
(Private Preview) via the Databricks CLI + Lakeview REST API — no MCP, no external
skill dependency. Vendored for the Du Bois D3 Custom-Page Gallery.

A custom page is a normal CANVAS page holding one full-width text widget whose
lines are a `<!-- @custom-page -->` marker + a JSON envelope
{code, manifest.required_modules, datasetMap}. The workspace
**"Custom pages in AI/BI dashboards" preview must be enabled**.
"""
import json, subprocess, time


def custom_page_widget(name, code, dataset_map=None, required_modules=None, w=12, h=14):
    """Build a Custom Page widget from author-supplied React/JSX `code`
    (CommonJS, ending in `module.exports.default = App;`). `require('react')` and
    `require('@databricks/viz')` are built in; `require('d3')` works only if
    "d3@7" is in required_modules (the curated allowlist is effectively d3@7 only)."""
    env = {"code": code,
           "manifest": {"required_modules": required_modules if required_modules is not None else ["d3@7"]},
           "datasetMap": dataset_map or []}
    return {"_w": w, "_h": h, "widget": {
        "name": name,
        "multilineTextboxSpec": {"lines": ["<!-- @custom-page -->", json.dumps(env)]}}}


def _api(method, path, profile, payload=None, soft=False):
    cmd = ["databricks", "api", method, path, "-p", profile]
    if payload is not None:
        cmd += ["--json", json.dumps(payload)]
    out = subprocess.run(cmd, capture_output=True, text=True)
    text = (out.stdout + out.stderr).strip()
    if out.returncode != 0:
        if soft:
            return None
        raise SystemExit(f"API {method} {path} failed:\n{text[:600]}")
    if not text:
        return {}
    try:
        return json.loads(text)
    except Exception:
        if soft:
            return None
        raise SystemExit(f"API {method} {path} returned non-JSON:\n{text[:600]}")


def _current_user(profile):
    r = _api("get", "/api/2.0/preview/scim/v2/Me", profile, soft=True) or {}
    if r.get("userName"):
        return r["userName"]
    raw = subprocess.run(["databricks", "current-user", "me", "-p", profile],
                         capture_output=True, text=True).stdout or "{}"
    return json.loads(raw).get("userName")


def _workspace_host(profile):
    """Resolve the workspace hostname from the CLI profile config so the published
    URL is correct even when the profile name != host subdomain."""
    raw = subprocess.run(["databricks", "auth", "env", "-p", profile],
                         capture_output=True, text=True).stdout.strip()
    host = ""
    try:
        host = (json.loads(raw).get("env", {}) or {}).get("DATABRICKS_HOST", "")
    except Exception:
        host = ""
    if not host:  # fallback: parse ~/.databrickscfg
        import configparser, os
        cfg = configparser.ConfigParser()
        cfg.read(os.path.expanduser("~/.databrickscfg"))
        if cfg.has_option(profile, "host"):
            host = cfg.get(profile, "host")
    return host.replace("https://", "").replace("http://", "").rstrip("/")


def _find_existing(display_name, parent_path, profile):
    token = None
    while True:
        p = "/api/2.0/lakeview/dashboards?page_size=100" + (f"&page_token={token}" if token else "")
        r = _api("get", p, profile, soft=True) or {}
        for d in r.get("dashboards", []):
            if d.get("display_name") == display_name and d.get("lifecycle_state") == "ACTIVE":
                full = _api("get", f"/api/2.0/lakeview/dashboards/{d['dashboard_id']}", profile, soft=True) or {}
                if full.get("parent_path") == parent_path:
                    return d["dashboard_id"]
        token = r.get("next_page_token")
        if not token:
            return None


def _layout(widgets):
    out, x, y, row_h = [], 0, 0, 0
    for wd in widgets:
        w, h = wd["_w"], wd["_h"]
        if x + w > 12:
            x, y, row_h = 0, y + row_h, 0
        out.append({"widget": wd["widget"], "position": {"x": x, "y": y, "width": w, "height": h}})
        x += w
        row_h = max(row_h, h)
    return out


def deploy(display_name, pages, profile, warehouse, parent_path=None,
           publish=True, theme=None, datasets=None):
    """Create (or idempotently update) a Lakeview dashboard and publish it.
    `theme` may be a uiSettings.theme dict, or None for the workspace default.
    `datasets` (optional) = [{"name","displayName","queryLines":[sql]}] to bind governed
    SQL datasets (query inside the page via datasetMap alias + viz.* queries)."""
    if "/" in display_name:
        raise SystemExit("display_name cannot contain '/'")
    parent_path = parent_path or f"/Users/{_current_user(profile)}"
    pg = [{"name": p["name"], "displayName": p["displayName"],
           "pageType": "PAGE_TYPE_CANVAS", "layoutVersion": "GRID_V1",
           "layout": _layout(p["widgets"])} for p in pages]
    ui = {"theme": theme, "applyModeEnabled": False} if theme else {}
    serialized = {"datasets": datasets or [], "pages": pg, "uiSettings": ui}

    did = _find_existing(display_name, parent_path, profile)
    created = False
    if not did:
        payload = {"display_name": display_name, "serialized_dashboard": json.dumps(serialized),
                   "parent_path": parent_path, "warehouse_id": warehouse}
        r = _api("post", "/api/2.0/lakeview/dashboards", profile, payload, soft=True) or {}
        if r.get("dashboard_id"):
            did = r["dashboard_id"]; created = True
            print(f"created {did}")
        else:
            for _ in range(6):
                time.sleep(2)
                did = _find_existing(display_name, parent_path, profile)
                if did:
                    break
            if not did:
                raise SystemExit(f"create failed and could not resolve existing dashboard: {r}")
    if not created:
        cur = _api("get", f"/api/2.0/lakeview/dashboards/{did}", profile) or {}
        _api("patch", f"/api/2.0/lakeview/dashboards/{did}", profile,
             {"serialized_dashboard": json.dumps(serialized), "etag": cur.get("etag"),
              "display_name": display_name, "warehouse_id": warehouse})
        print(f"updated {did}")
    if publish:
        _api("post", f"/api/2.0/lakeview/dashboards/{did}/published", profile,
             {"embed_credentials": True, "warehouse_id": warehouse})
    host = _workspace_host(profile) or f"{profile}.cloud.databricks.com"
    url = f"https://{host}/dashboardsv3/{did}/published"
    print(url)
    return did, url
