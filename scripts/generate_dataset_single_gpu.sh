#!/usr/bin/env bash
set -euo pipefail

# This script is safe on CPU too; the "single GPU" part is the intended rented
# box where pyarrow and the model stack are already installed for veRL training.
N_TRAIN="${N_TRAIN:-2000}"
N_VAL="${N_VAL:-300}"
SEED="${SEED:-42}"
OUT_DIR="${OUT_DIR:-data/generated}"
VENV="${VENV:-.venv-data}"

if [ ! -x "${VENV}/bin/python" ]; then
  python3 -m venv "${VENV}"
fi
"${VENV}/bin/python" -m pip install --upgrade pip
"${VENV}/bin/python" -m pip install -e '.[data]'
mkdir -p "${OUT_DIR}"

"${VENV}/bin/api-bench" generate \
  --n "${N_TRAIN}" \
  --seed "${SEED}" \
  --families automata,boolean_junta \
  --tiers easy,medium \
  --out "${OUT_DIR}/train_tasks.jsonl" \
  --verl-out "${OUT_DIR}/train_verl.jsonl" \
  --parquet-out "${OUT_DIR}/train.parquet"

"${VENV}/bin/api-bench" generate \
  --n "${N_VAL}" \
  --seed "$((SEED + 1))" \
  --families automata,boolean_junta \
  --tiers easy,medium \
  --out "${OUT_DIR}/val_tasks.jsonl" \
  --verl-out "${OUT_DIR}/val_verl.jsonl" \
  --parquet-out "${OUT_DIR}/val.parquet"

echo "Generated veRL parquet files:"
echo "  ${OUT_DIR}/train.parquet"
echo "  ${OUT_DIR}/val.parquet"
