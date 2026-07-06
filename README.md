# Active Program Induction RL

Infrastructure for an active program induction benchmark and a veRL/GRPO training loop. The Phase-1 implementation covers the rigorous core from `task.md`: DFA induction and Boolean junta induction with exact graders, online/frozen dataset generation, a true multi-turn active-probing environment, a veRL AgentLoop rollout, CPU smoke tests, and single-GPU/multi-GPU launch scripts.

The first research target is not "better coding benchmark scores." It is:

```text
Active-trained model > Passive-trained model on held-out active induction tasks
```

Coding transfer is downstream upside once the Phase-1 gate is green.

## What Is Implemented

Phase 1 is implemented end to end:

- Family A: DFA induction over `{a,b}` with exact equivalence by product automaton BFS.
- Family C: Boolean junta induction with exact equivalence by exhaustive enumeration.
- Multi-turn environment: the model emits one JSON action, the env executes the query, returns the oracle observation, and the model adapts on the next turn.
- veRL AgentLoop rollout: `ActiveProgramInductionAgentLoop` calls the LLM server turn by turn, appends environment observations with `response_mask=0`, and returns terminal reward.
- Transcript scorer: retained only for CPU debugging and passive/scorer tests.
- Dataset generator: writes internal task JSONL plus veRL-compatible JSONL/parquet rows.
- Passive ablation generator: writes fixed-example prompts over the same hidden task distribution.
- veRL custom reward: `active_program_induction.training.verl_reward.compute_score`, used for transcript/passive debugging; the main active RL path computes reward inside the AgentLoop.
- CPU smoke test: verifies generators, exact graders, and reward round trip without a GPU.
- Single-GPU cold-start evaluator: runs a base HF/Qwen model in a real turn-by-turn loop and scores reward spread.
- Single-GPU and multi-GPU veRL GRPO launch scripts.

The default training path is now true multi-turn RL. The old transcript-in-one-completion format is not the research path; it is kept as a cheap local scorer/debug utility.

## Repository Layout

```text
task.md                                      Design document and worked examples
pyproject.toml                               Python package metadata
src/active_program_induction/
  dfa.py                                     DFA generation, validation, exact equivalence
  junta.py                                   Boolean junta generation and exact equivalence
  prompts.py                                 Active/passive prompt builders
  scoring.py                                 Transcript parser and reward scorer
  env.py                                     True multi-turn active induction environment
  dataset.py                                 Task and veRL row generation
  agents.py                                  Oracle/wrong completions for tests
  cli.py                                     `api-bench` command
  model_eval.py                              Legacy transcript cold-start evaluator
  model_eval_multiturn.py                    True multi-turn cold-start evaluator
  training/verl_reward.py                    veRL custom reward function
  training/verl_agent_loop.py                veRL AgentLoop for adaptive active probing
scripts/
  smoke_cpu.sh                               Local CPU smoke test
  generate_dataset_single_gpu.sh             Generate JSONL/parquet data for veRL
  cold_start_single_gpu.sh                   Run base-model reward distribution
  install_verl_gpu.sh                        Helper for fresh GPU rental box
  train_verl_grpo_single_gpu.sh              Single-GPU veRL GRPO launch
  train_verl_grpo_passive_single_gpu.sh      Single-GPU Passive ablation launch
  train_verl_grpo_multigpu.sh                Multi-GPU veRL GRPO launch
tests/test_core.py                           CPU unit tests
configs/phase1_single_gpu.env.example        Example training env vars
```

## Install Locally

This machine does not need a GPU for generation and smoke tests.

```bash
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -e '.[dev]'
```

Run the tests:

```bash
.venv/bin/python -m pytest -q
```

Run the full CPU smoke path:

```bash
bash scripts/smoke_cpu.sh
```

Expected output includes:

```json
{
  "tasks": 20,
  "perfect_passed": 20,
  "wrong_rejected": 20
}
```

This proves the task generators, exact graders, reward function, and CLI are working locally. It does not prove the base model can solve the tasks; that is the GPU cold-start gate below.

## Generate a Small Dataset Locally

Generate JSONL tasks and veRL-style JSONL rows without parquet:

```bash
.venv/bin/api-bench generate \
  --n 100 \
  --seed 42 \
  --families automata,boolean_junta \
  --tiers easy,medium \
  --out data/generated/tasks.jsonl \
  --verl-out data/generated/verl_rows.jsonl
```

Install the data extra if you want parquet locally:

```bash
.venv/bin/python -m pip install -e '.[data]'
.venv/bin/api-bench generate \
  --n 100 \
  --seed 42 \
  --out data/generated/tasks.jsonl \
  --parquet-out data/generated/train.parquet
```

## Single-GPU Dataset Generation

On the rented GPU box, clone the repo and generate the Phase-1 train/val parquet files:

```bash
bash scripts/generate_dataset_single_gpu.sh
```

Useful knobs:

```bash
N_TRAIN=5000 N_VAL=500 SEED=123 OUT_DIR=data/generated \
  bash scripts/generate_dataset_single_gpu.sh
```

Outputs:

```text
data/generated/train_tasks.jsonl    Internal task records with hidden oracles
data/generated/val_tasks.jsonl      Internal validation records
data/generated/train_agent_verl.jsonl Agent-loop veRL-shaped JSONL for inspection/debugging
data/generated/val_agent_verl.jsonl
data/generated/train_agent.parquet  Multi-turn AgentLoop training file
data/generated/val_agent.parquet    Multi-turn AgentLoop validation file
data/generated/train_passive.parquet Passive ablation training file
data/generated/val_passive.parquet  Passive ablation validation file
```

The veRL rows include:

- `prompt`: string fallback prompt.
- `raw_prompt`: chat messages used by veRL AgentLoop when `data.return_raw_chat=True`.
- `agent_name`: `active_program_induction`, selecting the custom AgentLoop.
- `data_source`: `active_program_induction`.
- `ability`: task family.
- `ground_truth`: serialized full task JSON used by the reward function.
- `reward_model`: rule-based metadata.
- `extra_info`: split/task metadata.

Use agent files for the main active experiment and passive files for the matched-compute ablation.

For the active path, veRL's AgentLoop API runs the loop and returns `reward_score` directly. The docs require `data.return_raw_chat=True`, `actor_rollout_ref.rollout.mode=async`, an `agent_name` field, and `actor_rollout_ref.rollout.agent.agent_loop_config_path`; the training scripts set those. The custom reward hook remains available for transcript/passive debugging.

## Cold-Start Gate on One GPU

Before spending on RL, run the base model over a small validation set and inspect reward spread:

```bash
MODEL=Qwen/Qwen2.5-3B-Instruct \
TASKS=data/generated/val_tasks.jsonl \
LIMIT=50 \
OUT=data/generated/cold_start_multiturn_results.jsonl \
bash scripts/cold_start_single_gpu.sh
```

Interpretation:

- Some exact solves and a spread of partial rewards: green light for GRPO.
- All invalid JSON or all near-zero rewards: fix prompt format, task difficulty, or model size before training.
- All perfect on easy tasks: increase difficulty or add medium tasks so GRPO still has learning signal.

The output JSONL stores every assistant action and environment observation, so you can inspect whether failures are format failures, bad probe choices, or bad final hypotheses.

## Install veRL on a GPU Box

If you are not using an official/managed veRL image:

```bash
bash scripts/install_verl_gpu.sh
```

Then activate or point scripts at the environment:

```bash
export PYTHON=.venv-gpu/bin/python
```

If you are using a veRL Docker image, install this repo inside the image instead:

```bash
python3 -m pip install -e '.[data]'
export PYTHON=python3
```

## Single-GPU GRPO Training

After dataset generation and a green cold-start gate:

```bash
MODEL=Qwen/Qwen2.5-3B-Instruct \
TRAIN_FILE=data/generated/train_agent.parquet \
VAL_FILE=data/generated/val_agent.parquet \
PYTHON=.venv-gpu/bin/python \
bash scripts/train_verl_grpo_single_gpu.sh
```

Useful overrides:

```bash
ROLLOUT_N=8 TOTAL_EPOCHS=1 N_GPUS=1 \
EXPERIMENT_NAME=qwen-phase1-smoke \
bash scripts/train_verl_grpo_single_gpu.sh
```

The training script passes:

```text
algorithm.adv_estimator=grpo
data.return_raw_chat=True
actor_rollout_ref.rollout.mode=async
actor_rollout_ref.rollout.agent.agent_loop_config_path=$PWD/configs/agent_loop.yaml
```

The reward is computed inside `ActiveProgramInductionAgentLoop` after the model submits or exhausts the turn cap. Environment observation tokens are included in the trajectory with `response_mask=0`, so the policy is updated only on model-generated action tokens.

To train the passive ablation on the same family/tier distribution:

```bash
TRAIN_FILE=data/generated/train_passive.parquet \
VAL_FILE=data/generated/val_passive.parquet \
EXPERIMENT_NAME=qwen-grpo-phase1-passive \
PYTHON=.venv-gpu/bin/python \
bash scripts/train_verl_grpo_passive_single_gpu.sh
```

Compare active and passive runs at matched model, rollout count, batch size, total epochs, and task generator seed. The passive run is still single-prompt because the ablation intentionally removes adaptive feedback.

## Multi-GPU GRPO Training

Only move here after single-GPU data generation and the cold-start gate are green:

```bash
MODEL=Qwen/Qwen2.5-7B-Instruct \
N_GPUS=8 \
TRAIN_BATCH_SIZE=128 \
PPO_MINI_BATCH_SIZE=32 \
PYTHON=.venv-gpu/bin/python \
bash scripts/train_verl_grpo_multigpu.sh
```

This script is intentionally close to the single-GPU script. Change one variable at a time when scaling: GPU count, batch size, rollout count, and model size.

## Per-Turn Action Format Expected From the Model

For active tasks, the model outputs one JSON object per turn:

```json
{
  "tool": "query",
  "input": "ab"
}
```

The environment responds with:

```json
{"observation": {"input": "ab", "output": true}, "queries_used": 1}
```

When ready, the model submits:

```json
{
  "tool": "submit",
  "submission": {
    "states": ["s0", "s1"],
    "alphabet": ["a", "b"],
    "start": "s0",
    "accept": ["s1"],
    "delta": {
      "s0,a": "s1",
      "s0,b": "s0",
      "s1,a": "s1",
      "s1,b": "s0"
    }
  }
}
```

For Boolean junta tasks:

```json
{
  "tool": "submit",
  "submission": {
    "op": "xor",
    "args": [{"var": "x0", "op": "var"}, {"var": "x2", "op": "var"}]
  }
}
```

The scorer will:

1. Parse the JSON object.
2. If it is a query, execute it against the hidden oracle and return the observation to the next model turn.
3. If it is a submission, grade the final hypothesis against the hidden oracle.
4. Return `correct_or_partial - query_cost * num_queries - penalties`.

## Current Limitations

- Phase 1 only: DFA and Boolean junta are implemented. The DSL and terminal-binary families remain design targets from `task.md`.
- This CPU machine cannot execute or verify CUDA/vLLM/veRL AgentLoop training; the local tests verify the environment, dataset fields, and scoring semantics.
- Public benchmark evaluation is not implemented yet. Add it only after the Phase-1 active-vs-passive result exists.

## Recommended Run Order

1. Local CPU verification:

   ```bash
   bash scripts/smoke_cpu.sh
   ```

2. Commit any local changes and move to a GPU box.

3. Generate train/val parquet:

   ```bash
   N_TRAIN=2000 N_VAL=300 bash scripts/generate_dataset_single_gpu.sh
   ```

4. Run the base-model cold-start gate:

   ```bash
   MODEL=Qwen/Qwen2.5-3B-Instruct LIMIT=50 bash scripts/cold_start_single_gpu.sh
   ```

5. If reward spread is healthy, run single-GPU GRPO:

   ```bash
   MODEL=Qwen/Qwen2.5-3B-Instruct PYTHON=.venv-gpu/bin/python \
     bash scripts/train_verl_grpo_single_gpu.sh
   ```

6. Only then scale:

   ```bash
   MODEL=Qwen/Qwen2.5-7B-Instruct N_GPUS=8 \
     bash scripts/train_verl_grpo_multigpu.sh
   ```

## Notes on veRL Compatibility

The active launch scripts follow the current veRL AgentLoop documentation:

- Datasets are parquet files with a `prompt` column.
- Agent-loop datasets include `raw_prompt` and `agent_name`.
- Training sets `data.return_raw_chat=True`.
- Training sets `actor_rollout_ref.rollout.mode=async`.
- Training points `actor_rollout_ref.rollout.agent.agent_loop_config_path` at `configs/agent_loop.yaml`.
- The AgentLoop returns `reward_score`; transcript-style `custom_reward_function.path` is only for the legacy scorer/passive debug path.

If your installed veRL version has renamed config keys, keep the dataset and environment files unchanged and adjust only the shell script overrides. The active rollout contract is isolated in `training/verl_agent_loop.py`.
