#!/usr/bin/env python3
"""Assemble the "Du Bois Custom-Viz Gallery" AI/BI dashboard from the spec library.

For every chart in specs/<category>.py it builds:
  - a dataset  (ds_<id>)  from the chart's SQL,
  - a custom-vega-viz widget whose spec = the chart's Vega-Lite spec with the
    Du Bois config + {"data":{"name":"databricks_query"}} + container sizing injected,
laid out one page (tab) per category. Then it creates/updates the Lakeview
dashboard (etag-guarded) and publishes it with embedded credentials.

Usage:
  python build/build_dashboard.py --profile <profile> --warehouse <id> \
      [--dashboard-id <id>] [--parent-path /Users/<me>] [--mode dark] [--no-publish]
"""
import argparse, importlib.util, json, os, subprocess, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from palette.dubois import dubois_config, dubois_theme  # noqa: E402

# The specs reference tables as `pb_demo.custom_gallery.<table>`. That literal is the
# retarget placeholder: pass --schema (or set VEGA_SCHEMA) to point the whole
# gallery at any `<catalog>.<schema>`, and every chart's SQL is rewritten at build
# time. Default keeps the original so existing deploys are unaffected.
DEFAULT_SCHEMA = "pb_demo.custom_gallery"

# Tab titles per module.
TAB_TITLES = {
    "bar_column": "Bar & Column", "line_area": "Line & Area",
    "distributions": "Distributions", "correlation": "Correlation & Scatter",
    "part_to_whole": "Part-to-Whole", "radial": "Radial",
    "heatmap_matrix": "Heatmap & Matrix", "ranking": "Ranking",
    "tables": "Tables & Text", "indicators": "Indicators & Dials",
    "maps": "Maps", "advanced": "Advanced & Layered",
    "extreme_viz": "Extreme & Experimental",
    "native_ootb": "Out-of-the-Box Charts",
}

# The gallery spans TWO dashboards (each dashboard stores <=100 datasets). Each
# group is one dashboard with one tab per module.
GROUPS = [
    ("Du Bois Custom-Viz Gallery I — Core Charts",
     ["bar_column", "line_area", "distributions", "correlation", "part_to_whole", "radial"]),
    ("Du Bois Custom-Viz Gallery II — Composite, Indicators & Maps",
     ["heatmap_matrix", "ranking", "tables", "indicators", "advanced", "maps", "extreme_viz"]),
    ("Du Bois AI-BI Out-of-the-Box Charts (Native Widgets)",
     ["native_ootb"]),
]

SCHEMA_URL = "https://vega.github.io/schema/vega-lite/v5.json"
STD_H = 7          # uniform height for standard (third-width) charts
# The AI/BI grid is 6 columns wide. 2-column = w=3+w=3.
GRID_COLS = 6

# schema version per native widgetType (verified from the AI/BI viz editor)
NATIVE_VERSION = {"counter": 2, "table": 2,
                  "choropleth-map": 1, "symbol-map": 2,
                  "sankey": 1, "gantt": 1, "combo": 1, "forecast-line": 1}  # default 3 (pivot, funnel, waterfall, box, ...)

# Only exclude charts that genuinely don't render cleanly (the 100-dataset cap is
# now handled by splitting across two dashboards, so nothing is dropped for space).
EXCLUDE_IDS = {"dist2_rel_freq",   # bin+aggregate+stack -> empty bars
               "dist2_isotype"}    # sized emoji renders as one giant glyph


def load_category(mod_name):
    path = ROOT / "specs" / f"{mod_name}.py"
    if not path.exists():
        return []
    spec = importlib.util.spec_from_file_location(f"specs.{mod_name}", path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return getattr(m, "CHARTS", [])


def deep_merge(a, b):
    out = dict(a)
    for k, v in b.items():
        if k in out and isinstance(out[k], dict) and isinstance(v, dict):
            out[k] = deep_merge(out[k], v)
        else:
            out[k] = v
    return out


def build_widget(chart, mode, dataset_name, full=False):
    # Native (non-Vega) widget, e.g. choropleth-map: chart supplies the raw widget
    # spec + query fields; we do NOT wrap in custom-vega-viz or inject a config.
    if chart.get("native"):
        nat = chart["native"]
        spec = {"version": NATIVE_VERSION.get(nat["widgetType"], 3), "widgetType": nat["widgetType"],
                "encodings": nat["encodings"],
                "frame": {"title": f"◆ {chart['title']}  ·  OOTB native ({nat['widgetType']})",
                          "showTitle": True},
                "data": {"queryName": "main_query"}}
        if "mark" in nat:
            spec["mark"] = nat["mark"]
        return {"widget": {
            "name": f"w_{chart['id']}",
            "queries": [{"name": "main_query", "query": {
                "datasetName": dataset_name,
                "fields": chart["query_fields"],
                # box/percentile widgets pre-aggregate (disaggregated=False); most
                # native widgets pass raw rows (True).
                "disaggregated": chart.get("disaggregated", True)}}],
            "spec": spec}}

    vl = dict(chart["spec"])
    vl["$schema"] = SCHEMA_URL
    vl["data"] = {"name": "databricks_query"}
    vl["width"] = "container"
    vl.setdefault("height", "container")
    vl["autosize"] = {"type": "fit", "contains": "padding", "resize": True}
    vl["config"] = deep_merge(dubois_config(mode), vl.get("config", {}))
    fields = chart["fields"]
    return {
        "widget": {
            "name": f"w_{chart['id']}",
            "queries": [{
                "name": "main_query",
                "query": {
                    "datasetName": dataset_name,
                    "fields": [{"name": f, "expression": f"`{f}`"} for f in fields],
                    "disaggregated": True,
                },
            }],
            "spec": {
                "version": 1,
                "widgetType": "custom-vega-viz",
                "jsonSpec": {"type": "vega-lite", "spec": json.dumps(vl)},
                "frame": {"title": chart["title"], "showTitle": True},
                "encodings": {"fields": [{"fieldName": f} for f in fields]},
                "data": {"queryName": "main_query"},
            },
        }
    }


def build_dashboard(mods, mode, schema=DEFAULT_SCHEMA):
    datasets, pages = [], []
    sql_to_ds = {}                      # dedupe identical SQL -> one dataset (100/dashboard limit)
    total = 0
    for mod_name in mods:
        tab_title = TAB_TITLES.get(mod_name, mod_name)
        charts = load_category(mod_name)
        if not charts:
            continue
        layout, x, y, row_h = [], 0, 0, 0
        for ch in charts:
            if ch["id"] in EXCLUDE_IDS:
                continue
            # 2-column layout on the 6-column AI/BI grid.
            # Default: w=3 (half width, two charts per row).
            # Charts that need full width set w=6 in their spec.
            w = ch.get("w", 3)
            h = ch.get("h", 6)
            if x + w > GRID_COLS:           # wrap to next row
                x, y, row_h = 0, y + row_h, 0
            sql = ch["sql"]
            if schema != DEFAULT_SCHEMA:          # retarget the whole gallery
                sql = sql.replace(DEFAULT_SCHEMA, schema)
            key = " ".join(sql.split())          # normalize whitespace for dedupe
            ds_name = sql_to_ds.get(key)
            if ds_name is None:
                ds_name = f"ds_{len(datasets)}"
                sql_to_ds[key] = ds_name
                datasets.append({"name": ds_name, "displayName": ch["title"][:60],
                                 "queryLines": [sql]})
            wdg = build_widget(ch, mode, ds_name, full=(w >= GRID_COLS))
            wdg["position"] = {"x": x, "y": y, "width": w, "height": h}
            layout.append(wdg)
            x += w
            row_h = max(row_h, h)
            total += 1
        pages.append({"name": f"page_{mod_name}", "displayName": tab_title, "layout": layout})
    print(f"  datasets after dedupe: {len(datasets)}")
    # Du Bois theme so NATIVE (out-of-the-box) widgets render in the palette too.
    ui = {"theme": dubois_theme(), "applyModeEnabled": False}
    return {"datasets": datasets, "pages": pages, "uiSettings": ui}, total


def api(method, path, profile, payload=None):
    cmd = ["databricks", "api", method, path, "-p", profile]
    if payload is not None:
        cmd += ["--json", json.dumps(payload)]
    out = subprocess.run(cmd, capture_output=True, text=True)
    txt = (out.stdout + out.stderr).strip()
    try:
        return json.loads(txt)
    except Exception:
        raise SystemExit(f"API {method} {path} failed:\n{txt[:600]}")


def api_soft(method, path, profile, payload=None):
    """Like api() but returns None instead of raising (e.g. a tracked dashboard id
    that doesn't exist in the target workspace -> fall back to create)."""
    cmd = ["databricks", "api", method, path, "-p", profile]
    if payload is not None:
        cmd += ["--json", json.dumps(payload)]
    out = subprocess.run(cmd, capture_output=True, text=True)
    try:
        return json.loads((out.stdout + out.stderr).strip())
    except Exception:
        return None


def current_user(profile):
    out = subprocess.run(["databricks", "current-user", "me", "-p", profile],
                         capture_output=True, text=True)
    try:
        return json.loads(out.stdout).get("userName")
    except Exception:
        return None


def find_existing(name, parent_path, profile):
    """Return the id of an ACTIVE dashboard named `name` that lives directly in
    `parent_path` (folder-scoped so we never adopt a same-named dashboard from a
    different folder). Lets re-deploys stay idempotent even without an ids file."""
    token = None
    while True:
        path = "/api/2.0/lakeview/dashboards?page_size=100" + (f"&page_token={token}" if token else "")
        r = api_soft("get", path, profile) or {}
        for d in r.get("dashboards", []):
            if d.get("display_name") == name and d.get("lifecycle_state") == "ACTIVE":
                full = api_soft("get", f"/api/2.0/lakeview/dashboards/{d['dashboard_id']}", profile) or {}
                if full.get("parent_path") == parent_path:
                    return d["dashboard_id"]
        token = r.get("next_page_token")
        if not token:
            return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--profile", required=True)
    ap.add_argument("--warehouse", required=True)
    ap.add_argument("--parent-path", default=None,
                    help="workspace folder for new dashboards (default: /Users/<caller>)")
    ap.add_argument("--schema", default=os.environ.get("VEGA_SCHEMA", DEFAULT_SCHEMA),
                    help="target <catalog>.<schema> holding the gallery tables")
    ap.add_argument("--ids-file", default=str(ROOT / "build" / "dashboard_ids.json"),
                    help="where to track name->dashboard_id (use a per-workspace path when deploying elsewhere)")
    ap.add_argument("--fresh", action="store_true", help="ignore tracked ids and create new dashboards")
    ap.add_argument("--mode", default="dark", choices=["dark", "light"])
    ap.add_argument("--no-publish", action="store_true")
    a = ap.parse_args()

    # Default the new-dashboard parent folder to the calling user's home.
    parent_path = a.parent_path
    if not parent_path:
        u = current_user(a.profile)
        parent_path = f"/Users/{u}" if u else "/Users"
    print(f"target schema: {a.schema} | parent path: {parent_path} | ids: {a.ids_file}")

    ids_file = pathlib.Path(a.ids_file)
    ids = {} if a.fresh else (json.loads(ids_file.read_text()) if ids_file.exists() else {})

    for name, mods in GROUPS:
        serialized, total = build_dashboard(mods, a.mode, a.schema)
        print(f"[{name}] {total} charts / {len(serialized['datasets'])} datasets / {len(serialized['pages'])} tabs")
        did = ids.get(name)
        cur = api_soft("get", f"/api/2.0/lakeview/dashboards/{did}", a.profile) if did else None
        if not (did and cur and "etag" in cur) and not a.fresh:
            # no valid tracked id -> adopt an existing same-named dashboard in this
            # folder (idempotent re-deploy without the ids file / from a new machine)
            did = find_existing(name, parent_path, a.profile)
            cur = api_soft("get", f"/api/2.0/lakeview/dashboards/{did}", a.profile) if did else None
        if did and cur and "etag" in cur:      # exists in THIS workspace -> update
            r = api("patch", f"/api/2.0/lakeview/dashboards/{did}", a.profile,
                    {"serialized_dashboard": json.dumps(serialized), "etag": cur["etag"],
                     "display_name": name, "warehouse_id": a.warehouse})
            print(f"  updated {did}")
        else:                                   # not tracked / not found here -> create
            r = api("post", "/api/2.0/lakeview/dashboards", a.profile,
                    {"display_name": name, "serialized_dashboard": json.dumps(serialized),
                     "parent_path": parent_path, "warehouse_id": a.warehouse})
            did = r["dashboard_id"]
            print(f"  created {did}")
        ids[name] = did                          # record (create OR adopt/update)
        if not a.no_publish:
            api("post", f"/api/2.0/lakeview/dashboards/{did}/published", a.profile,
                {"embed_credentials": True, "warehouse_id": a.warehouse})
        print(f"  https://{a.profile}.cloud.databricks.com/dashboardsv3/{did}/published")
    ids_file.parent.mkdir(parents=True, exist_ok=True)
    ids_file.write_text(json.dumps(ids, indent=2))


if __name__ == "__main__":
    main()
