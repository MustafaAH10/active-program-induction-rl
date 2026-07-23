#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [[ -f "$repo_root/.env" ]]; then
  set -a
  # shellcheck disable=SC1091
  source "$repo_root/.env"
  set +a
fi

export PYTHONPATH="$repo_root/apps/orchestrator${PYTHONPATH:+:$PYTHONPATH}"
exec "$repo_root/.venv/bin/uvicorn" skyfoundry.main:app --port "${ORCHESTRATOR_PORT:-8000}"
