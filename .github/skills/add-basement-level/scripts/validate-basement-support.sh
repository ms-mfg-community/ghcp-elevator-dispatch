#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../../.." && pwd)"
WORKSPACE_DIR="$REPO_ROOT/workspace"

if [[ ! -d "$WORKSPACE_DIR" ]]; then
  echo "workspace directory not found: $WORKSPACE_DIR" >&2
  exit 1
fi

cd "$WORKSPACE_DIR"

if [[ ! -d ".venv" ]]; then
  python -m venv .venv
fi

source .venv/bin/activate
python -m pip install -r requirements.txt
python -m compileall .
python -m unittest discover -s tests -v

if [[ -f "package.json" ]]; then
  npm install

  tsc_shim_mode="$(stat -c "%a" node_modules/.bin/tsc)"
  tsc_bin_mode="$(stat -c "%a" node_modules/typescript/bin/tsc)"
  restore_tsc_permissions() {
    chmod "$tsc_shim_mode" node_modules/.bin/tsc
    chmod "$tsc_bin_mode" node_modules/typescript/bin/tsc
  }

  chmod +x node_modules/.bin/tsc node_modules/typescript/bin/tsc
  trap restore_tsc_permissions EXIT
  npm run build
  restore_tsc_permissions
  trap - EXIT
fi