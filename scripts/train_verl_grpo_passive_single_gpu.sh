#!/usr/bin/env bash
set -euo pipefail

# Passive ablation: fixed examples in the prompt, no adaptive environment loop.
# Use this only for the matched-compute Passive baseline.

MODEL="${MODEL:-Qwen/Qwen2.5-3B-Instruct}"
TRAIN_FILE="${TRAIN_FILE:-data/generated/train_passive.parquet}"
VAL_FILE="${VAL_FILE:-data/generated/val_passive.parquet}"
PROJECT_NAME="${PROJECT_NAME:-active-program-induction}"
EXPERIMENT_NAME="${EXPERIMENT_NAME:-qwen-grpo-phase1-passive-single-gpu}"
N_GPUS="${N_GPUS:-1}"
ROLLOUT_N="${ROLLOUT_N:-8}"
MAX_PROMPT_LENGTH="${MAX_PROMPT_LENGTH:-2048}"
MAX_RESPONSE_LENGTH="${MAX_RESPONSE_LENGTH:-1536}"
TOTAL_EPOCHS="${TOTAL_EPOCHS:-1}"
PYTHON="${PYTHON:-python3}"

export PYTHONPATH="${PWD}/src:${PYTHONPATH:-}"

"${PYTHON}" -m verl.trainer.main_ppo \
  algorithm.adv_estimator=grpo \
  data.train_files="${TRAIN_FILE}" \
  data.val_files="${VAL_FILE}" \
  data.train_batch_size=16 \
  data.max_prompt_length="${MAX_PROMPT_LENGTH}" \
  data.max_response_length="${MAX_RESPONSE_LENGTH}" \
  actor_rollout_ref.model.path="${MODEL}" \
  actor_rollout_ref.actor.optim.lr=1e-6 \
  actor_rollout_ref.actor.ppo_mini_batch_size=8 \
  actor_rollout_ref.actor.ppo_micro_batch_size_per_gpu=1 \
  actor_rollout_ref.rollout.name=vllm \
  actor_rollout_ref.rollout.n="${ROLLOUT_N}" \
  actor_rollout_ref.rollout.gpu_memory_utilization=0.6 \
  actor_rollout_ref.ref.log_prob_micro_batch_size_per_gpu=1 \
  custom_reward_function.path="${PWD}/src/active_program_induction/training/verl_reward.py" \
  custom_reward_function.name=compute_score \
  trainer.project_name="${PROJECT_NAME}" \
  trainer.experiment_name="${EXPERIMENT_NAME}" \
  trainer.n_gpus_per_node="${N_GPUS}" \
  trainer.nnodes=1 \
  trainer.save_freq=25 \
  trainer.test_freq=10 \
  trainer.total_epochs="${TOTAL_EPOCHS}"
