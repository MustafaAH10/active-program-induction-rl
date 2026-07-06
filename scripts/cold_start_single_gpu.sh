#!/usr/bin/env bash
set -euo pipefail

# Run after scripts/generate_dataset_single_gpu.sh on a CUDA machine.
MODEL="${MODEL:-Qwen/Qwen2.5-3B-Instruct}"
TASKS="${TASKS:-data/generated/val_tasks.jsonl}"
OUT="${OUT:-data/generated/cold_start_multiturn_results.jsonl}"
LIMIT="${LIMIT:-50}"
PYTHON="${PYTHON:-python3}"

export PYTHONPATH="${PWD}/src:${PYTHONPATH:-}"

"${PYTHON}" -m active_program_induction.model_eval_multiturn \
  --model "${MODEL}" \
  --tasks "${TASKS}" \
  --out "${OUT}" \
  --limit "${LIMIT}"
