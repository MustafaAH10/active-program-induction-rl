#!/usr/bin/env bash
set -euo pipefail

VENV="${VENV:-.venv}"
if [ ! -x "${VENV}/bin/python" ]; then
  python3 -m venv "${VENV}"
fi
"${VENV}/bin/python" -m pip install --upgrade pip
"${VENV}/bin/python" -m pip install -e .

"${VENV}/bin/api-bench" smoke --n 20 --seed 7
"${VENV}/bin/api-bench" generate \
  --n 12 \
  --seed 7 \
  --out data/generated/smoke_tasks.jsonl \
  --verl-out data/generated/smoke_verl.jsonl

echo "CPU smoke test passed."
