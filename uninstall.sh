#!/usr/bin/env bash
#
# Explicitly remove what install.sh created for the Du Bois Custom-Viz Gallery.
# SAFE BY DEFAULT: this is a DRY RUN unless you pass --yes. It only ever touches
# things this gallery created, and it NEVER drops data tables unless you also
# pass --drop-schema.
#
# Usage:
#   ./uninstall.sh --profile <cli-profile>              # dry run — shows what WOULD be removed
#   ./uninstall.sh --profile <cli-profile> --yes        # actually remove dashboards + datagen notebook
#   ./uninstall.sh --profile <cli-profile> --yes --drop-schema   # ALSO drop the data schema (destructive)
#
# What it removes:
#   • the 3 gallery dashboards tracked in ~/.dubois-vega-gallery/ids-<profile>.json
#   • the data-generation notebook (dubois_vega_gallery_datagen) in the parent path
#   • (only with --drop-schema) the <catalog>.<schema> holding the generated tables
#   • any extra dashboard you name with --dashboard-id <id> (e.g. the D3 custom
#     page, which is not tracked in the ids file)
#
# What it will NOT do:
#   • touch any dashboard NOT listed in the ids file (so hand-shared / team copies
#     with other ids are safe — pass --dashboard-id <id> to target one explicitly)
#   • drop a schema unless you explicitly pass --drop-schema
set -euo pipefail

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; NC='\033[0m'
ok()   { echo -e "${GREEN}✓${NC} $1"; }
warn() { echo -e "${YELLOW}⚠${NC} $1"; }
info() { echo -e "${BLUE}•${NC} $1"; }
fail() { echo -e "${RED}✗ $1${NC}" >&2; exit 1; }

PROFILE=""; APPLY="false"; DROP_SCHEMA="false"; PARENT_PATH=""; SCHEMA=""
EXTRA_IDS=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    --profile)       PROFILE="$2"; shift 2 ;;
    --yes|--apply)   APPLY="true"; shift ;;
    --drop-schema)   DROP_SCHEMA="true"; shift ;;
    --schema)        SCHEMA="$2"; shift 2 ;;
    --parent-path)   PARENT_PATH="$2"; shift 2 ;;
    --dashboard-id)  EXTRA_IDS+=( "$2" ); shift 2 ;;
    --help|-h)
      sed -n '2,30p' "$0" | sed 's/^# \{0,1\}//'
      exit 0 ;;
    *) echo "unknown arg: $1 (try --help)" >&2; exit 2 ;;
  esac
done
[[ -z "$PROFILE" ]] && fail "error: --profile is required (try --help)"

# Auth check
if ! databricks current-user me -p "$PROFILE" &>/dev/null; then
  fail "Cannot authenticate with profile '$PROFILE'. Run: databricks auth login --profile $PROFILE"
fi
USER_EMAIL="$(databricks current-user me -p "$PROFILE" | python3 -c 'import sys,json;print(json.load(sys.stdin)["userName"])')"
[[ -z "$PARENT_PATH" ]] && PARENT_PATH="/Users/${USER_EMAIL}"
IDS_FILE="${HOME}/.dubois-vega-gallery/ids-${PROFILE}.json"
NB_WS_PATH="${PARENT_PATH}/dubois_vega_gallery_datagen"

echo ""
if [[ "$APPLY" == "true" ]]; then
  warn "APPLY MODE — the items below WILL be deleted from workspace '${PROFILE}'."
else
  info "DRY RUN — nothing will be deleted. Re-run with --yes to apply."
fi
echo "  profile : ${PROFILE}"
echo "  user    : ${USER_EMAIL}"
echo "  ids file: ${IDS_FILE}"
echo ""

# ── Collect dashboards to remove: tracked ids + any --dashboard-id ──
declare -a TARGETS=()   # "id<TAB>name<TAB>state"
collect() {
  local did="$1"
  local meta
  meta="$(databricks api get "/api/2.0/lakeview/dashboards/${did}" -p "$PROFILE" 2>/dev/null \
    | python3 -c 'import sys,json
try:
    d=json.load(sys.stdin); print(d.get("display_name","?")+"\t"+d.get("lifecycle_state","?"))
except Exception: print("\t__MISSING__")' 2>/dev/null || echo $'\t__MISSING__')"
  TARGETS+=( "${did}"$'\t'"${meta}" )
}

if [[ -f "$IDS_FILE" ]]; then
  while IFS= read -r did; do
    [[ -n "$did" ]] && collect "$did"
  done < <(python3 -c 'import json,sys
try: print("\n".join(json.load(open("'"$IDS_FILE"'")).values()))
except Exception: pass')
else
  warn "no ids file for this profile — no tracked dashboards to remove (use --dashboard-id to target one explicitly)"
fi
for did in "${EXTRA_IDS[@]:-}"; do [[ -n "$did" ]] && collect "$did"; done

echo "Dashboards:"
if [[ ${#TARGETS[@]} -eq 0 ]]; then
  echo "    (none)"
else
  for t in "${TARGETS[@]}"; do
    did="${t%%$'\t'*}"; rest="${t#*$'\t'}"; nm="${rest%%$'\t'*}"; st="${rest##*$'\t'}"
    echo "    - ${did}  [${st}]  ${nm}"
  done
fi

echo ""
echo "Data-generation notebook:"
if databricks workspace get-status "$NB_WS_PATH" -p "$PROFILE" &>/dev/null; then
  echo "    - ${NB_WS_PATH}"
else
  echo "    (not found)"
fi

echo ""
echo "Data schema:"
if [[ "$DROP_SCHEMA" == "true" ]]; then
  if [[ -z "$SCHEMA" ]]; then
    fail "--drop-schema requires --schema <catalog>.<schema> (so we delete exactly the one you mean)"
  fi
  echo "    - ${SCHEMA}  (WILL be dropped WITH its tables — destructive)"
else
  echo "    (preserved — pass --drop-schema --schema <catalog>.<schema> to also drop data)"
fi

# ── Dry run stops here ──
if [[ "$APPLY" != "true" ]]; then
  echo ""
  info "Dry run complete. Nothing was deleted. Re-run with --yes to apply."
  exit 0
fi

# ── APPLY ──
echo ""
echo "==> removing..."
for t in "${TARGETS[@]:-}"; do
  [[ -z "$t" ]] && continue
  did="${t%%$'\t'*}"; rest="${t#*$'\t'}"; st="${rest##*$'\t'}"
  if [[ "$st" == "__MISSING__" ]]; then
    info "skip ${did} (already gone)"
    continue
  fi
  if databricks api delete "/api/2.0/lakeview/dashboards/${did}" -p "$PROFILE" &>/dev/null; then
    ok "deleted dashboard ${did}"
  else
    warn "could not delete dashboard ${did} (may already be trashed)"
  fi
done

if databricks workspace get-status "$NB_WS_PATH" -p "$PROFILE" &>/dev/null; then
  databricks workspace delete "$NB_WS_PATH" -p "$PROFILE" 2>/dev/null && ok "deleted notebook ${NB_WS_PATH}" || warn "could not delete notebook"
fi

if [[ "$DROP_SCHEMA" == "true" ]]; then
  if databricks api delete "/api/2.1/unity-catalog/schemas/${SCHEMA}?force=true" -p "$PROFILE" &>/dev/null; then
    ok "dropped schema ${SCHEMA} (with tables)"
  else
    warn "could not drop schema ${SCHEMA} (check you own it / it exists)"
  fi
fi

# Clear the local ids file so a future install starts clean.
if [[ -f "$IDS_FILE" ]]; then
  rm -f "$IDS_FILE" && ok "cleared tracked ids (${IDS_FILE})"
fi

echo ""
ok "Done."
