#!/usr/bin/env bash
#
# One-command install of the Du Bois Custom-Viz Gallery into any Databricks
# workspace. Generates the data, builds the geometry tables, and creates +
# publishes all three dashboards.
#
# Usage:
#   ./install.sh --profile <cli-profile>
#
# Everything else is auto-detected. Optional overrides:
#   --warehouse <id>            SQL warehouse (default: auto-pick first running)
#   --schema <catalog.schema>   target schema (default: auto-pick first managed catalog + custom_gallery)
#   --parent-path /Users/<you>  workspace folder for dashboards (default: calling user's home)
#   --mode dark|light           palette mode (default: dark)
#
# Requires: Databricks CLI (v0.2xx+) authenticated, python3, a SQL warehouse.
# Re-running is idempotent: it updates the same dashboards in this workspace.
set -euo pipefail

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'
ok()   { echo -e "${GREEN}✓${NC} $1"; }
warn() { echo -e "${YELLOW}⚠${NC} $1"; }
fail() { echo -e "${RED}✗ $1${NC}" >&2; exit 1; }

PROFILE=""; WAREHOUSE=""; SCHEMA=""; PARENT_PATH=""; MODE="dark"; WITH_CUSTOM_PAGE="false"
while [[ $# -gt 0 ]]; do
  case "$1" in
    --profile)     PROFILE="$2"; shift 2 ;;
    --warehouse)   WAREHOUSE="$2"; shift 2 ;;
    --schema)      SCHEMA="$2"; shift 2 ;;
    --parent-path) PARENT_PATH="$2"; shift 2 ;;
    --mode)        MODE="$2"; shift 2 ;;
    --with-custom-page) WITH_CUSTOM_PAGE="true"; shift ;;
    --help|-h)
      echo "Usage: ./install.sh --profile <cli-profile> [options]"
      echo ""
      echo "Options:"
      echo "  --profile <name>          Databricks CLI profile (optional; prompts to"
      echo "                            pick one, or uses the CLI default, if omitted)"
      echo "  --warehouse <id>          SQL warehouse ID (auto-detected if omitted)"
      echo "  --schema <catalog.schema> Target schema (auto-detected if omitted)"
      echo "  --parent-path <path>      Workspace folder for dashboards"
      echo "  --mode dark|light         Palette mode (default: dark)"
      echo "  --with-custom-page        ALSO deploy the 178-tile D3 Custom Page gallery"
      echo "                            (requires the workspace 'Custom pages in AI/BI"
      echo "                            dashboards' preview to be enabled; see"
      echo "                            custom_page/README.md)"
      echo ""
      echo "Prerequisites:"
      echo "  1. Databricks CLI v0.2xx+ installed and authenticated"
      echo "     (run: databricks configure --profile <name>)"
      echo "  2. A SQL warehouse in your workspace (any size)"
      echo "  3. CREATE SCHEMA permission on at least one managed catalog"
      echo "  4. Serverless jobs enabled (for one-time data generation)"
      echo ""
      echo "Examples:"
      echo "  ./install.sh --profile my-workspace"
      echo "  ./install.sh --profile prod --schema main.vega_gallery --mode light"
      exit 0 ;;
    *) echo "unknown arg: $1 (try --help)" >&2; exit 2 ;;
  esac
done

# ── Resolve profile when not supplied ──────────────────────────────
# --profile is optional. If omitted: on a TTY, offer a numbered menu of the
# profiles configured in ~/.databrickscfg (valid ones first); non-interactively,
# fall back to the CLI's own default resolution (DEFAULT profile / DATABRICKS_*
# env vars) by leaving PROFILE empty and letting the first auth check confirm it.
if [[ -z "$PROFILE" ]]; then
  if [[ -t 0 ]]; then
    # Only offer AUTHENTICATED profiles — an expired/invalid one can't deploy
    # anyway, and the raw list is often 20+ entries of stale junk.
    PROFILES=()
    while IFS= read -r _p; do
      [[ -n "$_p" ]] && PROFILES+=( "$_p" )
    done < <(databricks auth profiles 2>/dev/null | awk 'NR>1 && $1!="" && $NF=="YES" {print $1}')
    if [[ ${#PROFILES[@]} -gt 0 ]]; then
      echo ""
      echo "  No --profile given. Authenticated CLI profiles:"
      _i=1
      for _p in "${PROFILES[@]}"; do echo "    ${_i}) ${_p}"; _i=$((_i+1)); done
      echo "  (expired profiles hidden — run 'databricks auth login --profile <name>' to add one)"
      printf "  Pick a profile [1-%s]: " "${#PROFILES[@]}"
      read -r _pc </dev/tty || _pc=""
      if [[ "$_pc" =~ ^[0-9]+$ ]] && [[ "$_pc" -ge 1 ]] && [[ "$_pc" -le ${#PROFILES[@]} ]]; then
        PROFILE="${PROFILES[$((_pc-1))]}"
        ok "profile: ${PROFILE} (you chose it)"
      else
        fail "No valid selection. Re-run with --profile <name> (try --help)."
      fi
    else
      fail "No --profile given and no authenticated profiles found.
  Run: databricks auth login --profile <name>   (or pass --profile)"
    fi
  else
    # Non-interactive: fall back to the CLI default. 'databricks current-user me'
    # with no -p uses DEFAULT profile / DATABRICKS_HOST+token env if present.
    if databricks current-user me &>/dev/null; then
      PROFILE="DEFAULT"
      warn "no --profile given; using the CLI default profile/credentials"
    else
      fail "error: --profile is required (no CLI default auth found). Try --help."
    fi
  fi
fi

# ── Pre-flight checks ──────────────────────────────────────────────
echo "==> pre-flight checks..."

# Check CLI is authenticated
if ! databricks current-user me -p "$PROFILE" &>/dev/null; then
  fail "Cannot authenticate with profile '$PROFILE'.
  Run: databricks configure --profile $PROFILE
  Then re-run this script."
fi
ok "CLI authenticated (profile: $PROFILE)"

# Auto-detect warehouse if not provided
if [[ -z "$WAREHOUSE" ]]; then
  WAREHOUSE="$(databricks api get /api/2.0/sql/warehouses -p "$PROFILE" 2>/dev/null \
    | python3 -c '
import sys, json
whs = json.loads(sys.stdin.read()).get("warehouses", [])
running = [w for w in whs if w["state"] == "RUNNING"]
pick = running[0] if running else (whs[0] if whs else None)
if pick:
    print(pick["id"])
else:
    print("")
' 2>/dev/null || echo "")"
  if [[ -z "$WAREHOUSE" ]]; then
    fail "No SQL warehouses found in this workspace.
  Create a SQL warehouse in the Databricks UI, then either:
    • Re-run this script (it will auto-detect the new warehouse)
    • Pass --warehouse <id> explicitly"
  fi
  WH_NAME="$(databricks api get /api/2.0/sql/warehouses -p "$PROFILE" \
    | python3 -c "import sys,json;whs=json.loads(sys.stdin.read()).get('warehouses',[]);print(next((w['name'] for w in whs if w['id']=='$WAREHOUSE'),'?'))")"
  ok "warehouse: ${WAREHOUSE} (${WH_NAME})"
else
  ok "warehouse: ${WAREHOUSE} (user-specified)"
fi

# Verify warehouse access
WH_CHECK="$(databricks api get "/api/2.0/sql/warehouses/${WAREHOUSE}" -p "$PROFILE" 2>&1 || echo "{}")"
if echo "$WH_CHECK" | python3 -c "import sys,json;d=json.loads(sys.stdin.read());exit(0 if 'id' in d else 1)" 2>/dev/null; then
  ok "warehouse access verified"
else
  fail "Cannot access warehouse ${WAREHOUSE}.
  You need CAN_USE permission on the SQL warehouse.
  Ask your workspace admin to grant access, or pass --warehouse <id> for one you can use."
fi

# ── Resolve target schema: either user-specified, or auto-detect a ranked list
#    of candidate catalogs and try each until CREATE SCHEMA actually succeeds ──
SCHEMA_NAME="custom_gallery"

if [[ -n "$SCHEMA" ]]; then
  # User pinned a schema explicitly — honor it exactly, no fallback.
  CANDIDATES=( "${SCHEMA%%.*}" )
  SCHEMA_NAME="${SCHEMA#*.}"
  ok "schema: ${SCHEMA} (user-specified)"
else
  # Auto-detect. Build a RANKED, DETERMINISTIC list of candidate catalogs the
  # user is most likely able to CREATE SCHEMA in, best first. The old code took
  # the first managed catalog in arbitrary API order — often someone else's on a
  # FEVM/shared workspace — and failed hard. Now we rank (owned > looks-like-mine
  # > any managed; home/scratch/demo names float to the top) and fall THROUGH the
  # list at create time, so a non-writable top pick doesn't abort the install.
  ME="$(databricks current-user me -p "$PROFILE" 2>/dev/null \
    | python3 -c 'import sys,json;print(json.load(sys.stdin).get("userName",""))' 2>/dev/null || echo "")"
  CANDIDATES=()
  while IFS= read -r _cat; do
    [[ -n "$_cat" ]] && CANDIDATES+=( "$_cat" )
  done < <(databricks api get /api/2.1/unity-catalog/catalogs -p "$PROFILE" 2>/dev/null \
    | ME="$ME" python3 -c '
import sys, json, os
me = os.environ.get("ME", "")
local = me.split("@")[0].replace(".", "_") if me else ""
cats = json.loads(sys.stdin.read()).get("catalogs", [])
managed = [c for c in cats if c.get("catalog_type") == "MANAGED_CATALOG"]
owned = [c for c in managed if c.get("owner") == me]
named = [c for c in managed if local and local in c.get("name", "").lower().replace(".", "_")]
# tier 1: catalogs I own; tier 2: look like mine by name; tier 3: any managed.
# keep tier order but rank WITHIN by scratch/home/demo-ness, then alphabetical.
def score(c):
    n = c.get("name", "").lower()
    s = 0
    if n.startswith(("home_", "home-")): s += 100
    if local and local in n.replace(".", "_"): s += 50
    if any(k in n for k in ("sandbox","scratch","playground","demo","test","dev")): s += 25
    return s
seen, out = set(), []
for tier in (owned, named, managed):
    for c in sorted(tier, key=lambda c: (-score(c), c.get("name", ""))):
        n = c.get("name", "")
        if n and n not in seen:
            seen.add(n); out.append(n)
print("\n".join(out))
' 2>/dev/null)
  if [[ ${#CANDIDATES[@]} -eq 0 ]]; then
    fail "No managed catalogs found.
  Either:
    • Ask your workspace admin to create a catalog and grant you CREATE SCHEMA
    • Pass --schema <catalog>.<schema> for a catalog you have access to"
  fi
  if [[ ${#CANDIDATES[@]} -gt 1 ]]; then
    # Interactive pick when we have a terminal; otherwise keep the auto
    # fall-through (CI / piped runs stay non-interactive and still work).
    if [[ -t 0 ]]; then
      echo ""
      echo "  Multiple catalogs you can target (best first):"
      _i=1
      for _c in "${CANDIDATES[@]}"; do
        if [[ $_i -eq 1 ]]; then echo "    ${_i}) ${_c}   [default]"; else echo "    ${_i}) ${_c}"; fi
        _i=$((_i+1))
      done
      printf "  Pick a catalog [1-%s], or Enter for default (%s): " "${#CANDIDATES[@]}" "${CANDIDATES[0]}"
      read -r _choice </dev/tty || _choice=""
      if [[ -n "$_choice" ]]; then
        if [[ "$_choice" =~ ^[0-9]+$ ]] && [[ "$_choice" -ge 1 ]] && [[ "$_choice" -le ${#CANDIDATES[@]} ]]; then
          _sel="${CANDIDATES[$((_choice-1))]}"
          CANDIDATES=( "$_sel" )          # pin the chosen one (still verified at create)
          ok "catalog: ${_sel} (you chose it)"
        else
          warn "'$_choice' isn't a listed option — using default ${CANDIDATES[0]}"
        fi
      fi
    else
      ok "catalog candidates (best first): ${CANDIDATES[*]} — will use the first I can write to; pass --schema <catalog>.<schema> to pin one"
    fi
  fi
fi

# Try each candidate catalog in order; stop at the first where the schema is
# created OR already exists. The CLI prints "already exists" as plain-text
# stderr with a non-zero exit, so match on the raw string, not JSON.
SCHEMA=""
LAST_ERR=""
for CAT in "${CANDIDATES[@]}"; do
  RESP="$(databricks api post /api/2.1/unity-catalog/schemas -p "$PROFILE" \
    --json "{\"catalog_name\":\"${CAT}\",\"name\":\"${SCHEMA_NAME}\",\"comment\":\"Du Bois Custom-Viz Gallery data\"}" 2>&1 || true)"
  if echo "$RESP" | grep -qiE '"name"|already exists|SCHEMA_ALREADY_EXISTS'; then
    SCHEMA="${CAT}.${SCHEMA_NAME}"
    ok "schema ${SCHEMA} ready"
    break
  else
    LAST_ERR="$(printf '%s' "$RESP" | head -1)"
    [[ ${#CANDIDATES[@]} -gt 1 ]] && warn "can't use ${CAT}.${SCHEMA_NAME} (${LAST_ERR}) — trying next candidate"
  fi
done
if [[ -z "$SCHEMA" ]]; then
  fail "Could not create schema '${SCHEMA_NAME}' in any candidate catalog (tried: ${CANDIDATES[*]}).
  Last error: ${LAST_ERR}
  You need CREATE SCHEMA on a catalog. Either:
    • Ask your workspace admin: GRANT CREATE SCHEMA ON CATALOG <catalog> TO \`${ME:-your@email}\`
    • Pass --schema <catalog>.<schema> for a catalog you own"
fi

# Derive catalog + schema parts from the resolved schema (used by later steps).
CATALOG="${SCHEMA%%.*}"
SCHEMA_ONLY="${SCHEMA#*.}"

export VEGA_SCHEMA="$SCHEMA"

# Default parent path to calling user's home
if [[ -z "$PARENT_PATH" ]]; then
  USER_NAME="$(databricks current-user me -p "$PROFILE" | python3 -c 'import sys,json;print(json.load(sys.stdin)["userName"])')"
  PARENT_PATH="/Users/${USER_NAME}"
fi
IDS_FILE="${HOME}/.dubois-vega-gallery/ids-${PROFILE}.json"
NB_WS_PATH="${PARENT_PATH}/dubois_vega_gallery_datagen"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo ""
echo "  target schema : ${SCHEMA}"
echo "  warehouse     : ${WAREHOUSE}"
echo "  parent path   : ${PARENT_PATH}"
echo "  mode          : ${MODE}"
echo ""

# ── Step 1: Import data-generation notebook ────────────────────────
echo "==> [1/4] importing data-generation notebook -> ${NB_WS_PATH}"
databricks workspace import "${NB_WS_PATH}" \
  --file "${ROOT}/data_generation/00_generate_vega_datasets.ipynb" \
  --format JUPYTER --overwrite -p "${PROFILE}"
ok "notebook imported"

# ── Step 2: Run data-generation job ────────────────────────────────
echo "==> [2/4] running data-generation job (serverless) — creates ~20 tables"
RUN_JSON=$(databricks api post /api/2.1/jobs/runs/submit -p "${PROFILE}" --json "$(cat <<JSON
{ "run_name": "dubois-vega-gallery datagen",
  "tasks": [{ "task_key": "generate",
    "notebook_task": { "notebook_path": "${NB_WS_PATH}",
      "base_parameters": { "catalog": "${CATALOG}", "schema": "${SCHEMA_ONLY}" } } }] }
JSON
)")
RUN_ID=$(echo "$RUN_JSON" | python3 -c 'import sys,json;print(json.load(sys.stdin)["run_id"])')
echo "    run_id=${RUN_ID} — waiting for completion..."
while true; do
  ST=$(databricks api get "/api/2.1/jobs/runs/get?run_id=${RUN_ID}" -p "${PROFILE}" \
       | python3 -c 'import sys,json;s=json.load(sys.stdin)["state"];print(s.get("life_cycle_state",""),s.get("result_state",""))')
  LC="${ST% *}"; RS="${ST#* }"
  case "$LC" in
    TERMINATED)
      if [[ "$RS" == "SUCCESS" ]]; then
        ok "data generation complete"
        break
      else
        fail "Data generation FAILED (${RS}).
  Common causes:
    • Serverless jobs not enabled — ask your workspace admin
    • Insufficient permissions on catalog '${CATALOG}'
    • Notebook execution error — check run ${RUN_ID} in the Jobs UI"
      fi ;;
    INTERNAL_ERROR|SKIPPED)
      fail "Data generation ${LC}.
  Check run ${RUN_ID} in the Jobs UI for details." ;;
    *) sleep 15 ;;
  esac
done

# ── Step 3: Build geometry tables ──────────────────────────────────
echo "==> [3/4] building geometry tables (for choropleth maps)"
python3 "${ROOT}/data_generation/10_generate_geo_tables.py" \
  --profile "${PROFILE}" --warehouse "${WAREHOUSE}" --schema "${SCHEMA}"
ok "geometry tables ready"

# ── Step 4: Build + publish dashboards ─────────────────────────────
echo "==> [4/4] building + publishing 3 dashboards (228 charts)"
python3 "${ROOT}/build/build_dashboard.py" \
  --profile "${PROFILE}" --warehouse "${WAREHOUSE}" --schema "${SCHEMA}" \
  --parent-path "${PARENT_PATH}" --mode "${MODE}" --ids-file "${IDS_FILE}"

# ── Step 5 (optional): Du Bois D3 Custom Page gallery ──────────────
# Offer it interactively if not already requested via --with-custom-page.
if [[ "$WITH_CUSTOM_PAGE" != "true" && -t 0 ]]; then
  echo ""
  echo "  Also deploy the Du Bois D3 Custom Page gallery?"
  echo "    • 178 interactive D3 tiles (incl. generative art & simulations) in one custom page"
  echo "    • CAVEAT: needs the workspace preview 'Custom pages in AI/BI dashboards' ENABLED,"
  echo "      otherwise the page renders blank / shows raw code (see custom_page/README.md)"
  printf "  Deploy it? [y/N]: "
  read -r _cp </dev/tty || _cp=""
  [[ "$_cp" =~ ^[Yy]$ ]] && WITH_CUSTOM_PAGE="true"
fi

if [[ "$WITH_CUSTOM_PAGE" == "true" ]]; then
  echo ""
  echo "==> [5] deploying Du Bois D3 Custom Page gallery (178 D3 tiles, one custom page)"
  warn "requires the workspace preview 'Custom pages in AI/BI dashboards' to be ENABLED"
  warn "(see custom_page/README.md) — the page renders blank otherwise"
  python3 "${ROOT}/custom_page/build_custom_page.py" \
    --profile "${PROFILE}" --warehouse "${WAREHOUSE}" --parent-path "${PARENT_PATH}"
  ok "custom page deployed"
fi

echo ""
ok "Done! Dashboard IDs tracked in ${IDS_FILE}"
echo ""
echo "  Open your workspace and look for the dashboards in ${PARENT_PATH}"
