#!/usr/bin/env bash
set -euo pipefail

API_BASE_URL="${API_BASE_URL:-http://localhost:7000}"
STATE_URL="${API_BASE_URL%/}/api/state"

python - "$STATE_URL" <<'PY'
import json
import sys
import urllib.request

state_url = sys.argv[1]

try:
    with urllib.request.urlopen(state_url, timeout=5) as response:
        state = json.load(response)
except Exception as error:
    raise SystemExit(f"Could not read API state from {state_url}: {error}")

floors = state.get("floors")
if not isinstance(floors, list):
    raise SystemExit("API state does not contain a floors list")

basement_entries = [floor for floor in floors if floor.get("floor") == -1]
if len(basement_entries) != 1:
    raise SystemExit(f"Expected exactly one basement floor with floor -1, found {len(basement_entries)}")

basement = basement_entries[0]
label = basement.get("label")
if label != "B1":
    raise SystemExit(f"Expected basement label B1, found {label!r}")

floor_numbers = {floor.get("floor") for floor in floors}
missing = {-1, 1, 2, 3, 4, 5} - floor_numbers
if missing:
    raise SystemExit(f"API state is missing expected floors: {sorted(missing)}")

print("Basement API state check passed")
PY