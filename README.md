# Active Program Induction RL

Infrastructure for an active program induction benchmark and a veRL/GRPO training loop. The Phase-1 implementation covers the rigorous core from `task.md`: DFA induction and Boolean junta induction with exact graders, online/frozen dataset generation, transcript-style active probing prompts, a veRL custom reward hook, CPU smoke tests, and single-GPU/multi-GPU launch scripts.

The first research target is not "better coding benchmark scores." It is:

```text
Active-trained model > Passive-trained model on held-out active induction tasks
```

Coding transfer is downstream upside once the Phase-1 gate is green.

## What Is Implemented

Phase 1 is implemented end to end:

- Family A: DFA induction over `{a,b}` with exact equivalence by product automaton BFS.
- Family C: Boolean junta induction with exact equivalence by exhaustive enumeration.
- Active prompt format: the model emits a JSON transcript containing `queries` and a final `submission`.
- Reward function: simulates oracle answers for the submitted queries, grades the final hypothesis, subtracts query cost and penalties.
- Dataset generator: writes internal task JSONL plus veRL-compatible JSONL/parquet rows.
- veRL custom reward: `active_program_induction.training.verl_reward.compute_score`.
- CPU smoke test: verifies generators, exact graders, and reward round trip without a GPU.
- Single-GPU cold-start evaluator: runs a base HF/Qwen model on generated tasks and scores reward spread.
- Single-GPU and multi-GPU veRL GRPO launch scripts.

The current training interface uses "transcript-in-one-completion" RL. This is intentional: it fits veRL's standard prompt plus reward-function interface while still training the model to choose informative probes. A later true multi-turn agent-loop version can reuse the same task generators and scorers.

## Repository Layout

```text
task.md                                      Design document and worked examples
pyproject.toml                               Python package metadata
src/active_program_induction/
  dfa.py                                     DFA generation, validation, exact equivalence
  junta.py                                   Boolean junta generation and exact equivalence
  prompts.py                                 Active/passive prompt builders
  scoring.py                                 Transcript parser and reward scorer
  dataset.py                                 Task and veRL row generation
  agents.py                                  Oracle/wrong completions for tests
  cli.py                                     `api-bench` command
  model_eval.py                              Single-GPU base-model cold-start evaluator
  training/verl_reward.py                    veRL custom reward function
scripts/
  smoke_cpu.sh                               Local CPU smoke test
  generate_dataset_single_gpu.sh             Generate JSONL/parquet data for veRL
  cold_start_single_gpu.sh                   Run base-model reward distribution
  install_verl_gpu.sh                        Helper for fresh GPU rental box
  train_verl_grpo_single_gpu.sh              Single-GPU veRL GRPO launch
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
data/generated/train_verl.jsonl     veRL-shaped JSONL for inspection/debugging
data/generated/val_verl.jsonl
data/generated/train.parquet        veRL training file
data/generated/val.parquet          veRL validation file
```

The veRL rows include:

- `prompt`: active transcript prompt.
- `data_source`: `active_program_induction`.
- `ability`: task family.
- `ground_truth`: serialized full task JSON used by the reward function.
- `reward_model`: rule-based metadata.
- `extra_info`: split/task metadata.

veRL's documentation says custom reward functions are passed `data_source`, `solution_str`, `ground_truth`, and `extra_info`; this repo's reward hook follows that interface in `src/active_program_induction/training/verl_reward.py`.

## Cold-Start Gate on One GPU

Before spending on RL, run the base model over a small validation set and inspect reward spread:

```bash
MODEL=Qwen/Qwen2.5-3B-Instruct \
TASKS=data/generated/val_tasks.jsonl \
LIMIT=50 \
OUT=data/generated/cold_start_results.jsonl \
bash scripts/cold_start_single_gpu.sh
```

Interpretation:

- Some exact solves and a spread of partial rewards: green light for GRPO.
- All invalid JSON or all near-zero rewards: fix prompt format, task difficulty, or model size before training.
- All perfect on easy tasks: increase difficulty or add medium tasks so GRPO still has learning signal.

The output JSONL stores each completion and score detail, so you can inspect whether failures are format failures, bad probe choices, or bad final hypotheses.

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
TRAIN_FILE=data/generated/train.parquet \
VAL_FILE=data/generated/val.parquet \
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
custom_reward_function.path=$PWD/src/active_program_induction/training/verl_reward.py
custom_reward_function.name=compute_score
```

The reward starts in graded mode by default, so wrong but behaviorally close submissions can receive partial reward. For exact-only validation, use `compute_score_exact` in the script or set a validation-specific reward path/name.

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

## Reward Format Expected From the Model

For active tasks, the model should output one JSON object:

```json
{
  "queries": ["", "a", "ab", "abb"],
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
  "queries": [[0,0,0,0,0], [1,0,0,0,0]],
  "submission": {
    "op": "xor",
    "args": [{"var": "x0", "op": "var"}, {"var": "x2", "op": "var"}]
  }
}
```

The scorer will:

1. Parse the JSON object.
2. Execute each query against the hidden oracle up to the probe budget.
3. Grade only the final submission against the hidden oracle.
4. Return `correct_or_partial - query_cost * num_queries - penalties`.

## Current Limitations

- Phase 1 only: DFA and Boolean junta are implemented. The DSL and terminal-binary families remain design targets from `task.md`.
- Active interaction is represented as a full transcript completion, not a live multi-turn rollout loop.
- The veRL scripts are launchable templates aligned with the documented custom reward interface, but this CPU machine cannot execute or verify CUDA/vLLM training.
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

The launch scripts follow the current veRL custom reward documentation:

- Datasets are parquet files with a `prompt` column.
- Rule-based rewards can be selected through `custom_reward_function.path` and `custom_reward_function.name`.
- The custom reward signature is `compute_score(data_source, solution_str, ground_truth, extra_info=None)`.

If your installed veRL version has renamed config keys, keep the dataset and reward files unchanged and adjust only the shell script overrides. The core contract is isolated in `training/verl_reward.py`.
