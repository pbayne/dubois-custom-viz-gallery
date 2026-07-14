#!/usr/bin/env bash
#
# One-command install of the Du Bois Custom-Viz Gallery into any Databricks
# workspace. Generates the data, builds the geometry tables, and creates +
# publishes all three dashboards.
#
# Usage:
#   ./install.sh --profile <cli-profile> --warehouse <warehouse-id> \
#       [--schema <catalog.schema>] [--parent-path /Users/<you>] [--mode dark|light]
#
# Requires: the Databricks CLI (v0.2xx) authenticated for --profile, python3,
# a running SQL warehouse, and serverless jobs enabled (for the data-gen run).
# Re-running is idempotent: it updates the same dashboards in this workspace.
set -euo pipefail

PROFILE=""; WAREHOUSE=""; SCHEMA="pb_demo.custom_gallery"; PARENT_PATH=""; MODE="dark"
while [[ $# -gt 0 ]]; do
  case "$1" in
    --profile)     PROFILE="$2"; shift 2 ;;
    --warehouse)   WAREHOUSE="$2"; shift 2 ;;
    --schema)      SCHEMA="$2"; shift 2 ;;
    --parent-path) PARENT_PATH="$2"; shift 2 ;;
    --mode)        MODE="$2"; shift 2 ;;
    *) echo "unknown arg: $1" >&2; exit 2 ;;
  esac
done
[[ -z "$PROFILE" || -z "$WAREHOUSE" ]] && { echo "error: --profile and --warehouse are required" >&2; exit 2; }

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CATALOG="${SCHEMA%%.*}"; SCHEMA_ONLY="${SCHEMA#*.}"
export VEGA_SCHEMA="$SCHEMA"

# Default the workspace parent folder to the calling user's home.
if [[ -z "$PARENT_PATH" ]]; then
  USER_NAME="$(databricks current-user me -p "$PROFILE" | python3 -c 'import sys,json;print(json.load(sys.stdin)["userName"])')"
  PARENT_PATH="/Users/${USER_NAME}"
fi
IDS_FILE="${HOME}/.dubois-vega-gallery/ids-${PROFILE}.json"
NB_WS_PATH="${PARENT_PATH}/dubois_vega_gallery_datagen"

echo "==> target schema : ${SCHEMA}"
echo "==> warehouse     : ${WAREHOUSE}"
echo "==> parent path   : ${PARENT_PATH}"
echo

# 1. Import the data-generation notebook into the workspace.
echo "==> [1/4] importing data-generation notebook -> ${NB_WS_PATH}"
databricks workspace import "${NB_WS_PATH}" \
  --file "${ROOT}/data_generation/00_generate_vega_datasets.ipynb" \
  --format JUPYTER --overwrite -p "${PROFILE}"

# 2. Run it as a one-time serverless job (creates the schema + 20 tables), then wait.
echo "==> [2/4] running data-generation job (serverless)"
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
    TERMINATED) [[ "$RS" == "SUCCESS" ]] && { echo "    data-gen SUCCESS"; break; } || { echo "    data-gen FAILED ($RS)"; exit 1; } ;;
    INTERNAL_ERROR|SKIPPED) echo "    data-gen $LC"; exit 1 ;;
    *) sleep 15 ;;
  esac
done

# 3. Build the two geometry tables for the filled choropleths.
echo "==> [3/4] building geometry tables"
python3 "${ROOT}/data_generation/10_generate_geo_tables.py" \
  --profile "${PROFILE}" --warehouse "${WAREHOUSE}" --schema "${SCHEMA}"

# 4. Build + publish all three dashboards (idempotent per workspace via IDS_FILE).
echo "==> [4/4] building + publishing dashboards"
python3 "${ROOT}/build/build_dashboard.py" \
  --profile "${PROFILE}" --warehouse "${WAREHOUSE}" --schema "${SCHEMA}" \
  --parent-path "${PARENT_PATH}" --mode "${MODE}" --ids-file "${IDS_FILE}"

echo; echo "Done. Dashboard ids tracked in ${IDS_FILE}"
