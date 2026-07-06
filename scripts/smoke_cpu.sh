#!/usr/bin/env bash
set -euo pipefail

python3 -m pip install -e .
api-bench smoke --n 20 --seed 7
api-bench generate \
  --n 12 \
  --seed 7 \
  --out data/generated/smoke_tasks.jsonl \
  --verl-out data/generated/smoke_verl.jsonl

echo "CPU smoke test passed."
