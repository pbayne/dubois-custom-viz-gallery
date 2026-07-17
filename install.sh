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

PROFILE=""; WAREHOUSE=""; SCHEMA=""; PARENT_PATH=""; MODE="dark"
while [[ $# -gt 0 ]]; do
  case "$1" in
    --profile)     PROFILE="$2"; shift 2 ;;
    --warehouse)   WAREHOUSE="$2"; shift 2 ;;
    --schema)      SCHEMA="$2"; shift 2 ;;
    --parent-path) PARENT_PATH="$2"; shift 2 ;;
    --mode)        MODE="$2"; shift 2 ;;
    --help|-h)
      echo "Usage: ./install.sh --profile <cli-profile> [options]"
      echo ""
      echo "Options:"
      echo "  --profile <name>          Databricks CLI profile (REQUIRED)"
      echo "  --warehouse <id>          SQL warehouse ID (auto-detected if omitted)"
      echo "  --schema <catalog.schema> Target schema (auto-detected if omitted)"
      echo "  --parent-path <path>      Workspace folder for dashboards"
      echo "  --mode dark|light         Palette mode (default: dark)"
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
[[ -z "$PROFILE" ]] && fail "error: --profile is required (try --help)"

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

# Auto-detect catalog if schema not provided
if [[ -z "$SCHEMA" ]]; then
  AUTO_CATALOG="$(databricks api get /api/2.1/unity-catalog/catalogs -p "$PROFILE" 2>/dev/null \
    | python3 -c '
import sys, json
cats = json.loads(sys.stdin.read()).get("catalogs", [])
managed = [c for c in cats if c.get("catalog_type") == "MANAGED_CATALOG"]
if managed:
    print(managed[0]["name"])
else:
    print("")
' 2>/dev/null || echo "")"
  if [[ -z "$AUTO_CATALOG" ]]; then
    fail "No managed catalogs found.
  Either:
    • Ask your workspace admin to create a catalog and grant you CREATE SCHEMA
    • Pass --schema <catalog>.<schema> for a catalog you have access to"
  fi
  SCHEMA="${AUTO_CATALOG}.custom_gallery"
  ok "schema: ${SCHEMA} (auto-detected)"
else
  ok "schema: ${SCHEMA} (user-specified)"
fi

# Test catalog write access by trying to create the schema
CATALOG="${SCHEMA%%.*}"; SCHEMA_ONLY="${SCHEMA#*.}"
SCHEMA_CHECK="$(databricks api post /api/2.1/unity-catalog/schemas -p "$PROFILE" \
  --json "{\"catalog_name\":\"${CATALOG}\",\"name\":\"${SCHEMA_ONLY}\",\"comment\":\"Du Bois Custom-Viz Gallery data\"}" 2>&1 || echo "{}")"
if echo "$SCHEMA_CHECK" | python3 -c "
import sys, json
d = json.loads(sys.stdin.read())
# Success if schema was created or already exists
if 'name' in d or 'SCHEMA_ALREADY_EXISTS' in str(d) or 'already exists' in str(d):
    exit(0)
exit(1)
" 2>/dev/null; then
  ok "schema ${SCHEMA} ready"
else
  ERR_MSG="$(echo "$SCHEMA_CHECK" | python3 -c "import sys,json;d=json.loads(sys.stdin.read());print(d.get('message',d.get('error_code','unknown error')))" 2>/dev/null || echo "unknown error")"
  fail "Cannot create schema ${SCHEMA}: ${ERR_MSG}
  You need CREATE SCHEMA permission on catalog '${CATALOG}'.
  Either:
    • Ask your workspace admin: GRANT CREATE SCHEMA ON CATALOG ${CATALOG} TO \`your@email\`
    • Pass --schema <catalog>.<schema> for a catalog you own"
fi

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

echo ""
ok "Done! Dashboard IDs tracked in ${IDS_FILE}"
echo ""
echo "  Open your workspace and look for the dashboards in ${PARENT_PATH}"
