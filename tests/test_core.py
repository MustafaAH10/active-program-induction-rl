from __future__ import annotations

import json

from active_program_induction import agents
from active_program_induction.dataset import generate_tasks, sample_examples, to_verl_rows
from active_program_induction.env import ActiveInductionEnv
from active_program_induction.scoring import score_completion
from active_program_induction.training.verl_reward import compute_score


def test_generated_tasks_oracle_completion_scores_high() -> None:
    tasks = generate_tasks(n=8, seed=123, families=("automata", "boolean_junta"), tiers=("easy",))
    for task in tasks:
        result = score_completion(task, agents.oracle_completion(task))
        assert result["equivalent"] is True
        assert result["reward"] > 0.9


def test_wrong_completion_is_rejected() -> None:
    tasks = generate_tasks(n=8, seed=456, families=("automata", "boolean_junta"), tiers=("easy",))
    for task in tasks:
        result = score_completion(task, agents.deliberately_wrong_completion(task))
        assert result["equivalent"] is False


def test_verl_rows_and_reward_function_round_trip() -> None:
    task = generate_tasks(n=1, seed=789, families=("automata",), tiers=("easy",))[0]
    row = to_verl_rows([task])[0]
    completion = json.dumps(agents.oracle_completion(task))
    reward = compute_score(
        data_source=row["data_source"],
        solution_str=completion,
        ground_truth=row["ground_truth"],
        extra_info=row["extra_info"],
    )
    assert reward > 0.9


def test_passive_rows_include_examples_and_score() -> None:
    task = generate_tasks(n=1, seed=321, families=("boolean_junta",), tiers=("easy",))[0]
    examples = sample_examples(task, n=4, seed=0)
    assert len(examples) == 4
    row = to_verl_rows([task], mode="passive")[0]
    assert '"examples"' in row["prompt"]
    completion = json.dumps({"submission": task["hidden"]["expr"]})
    reward = compute_score(row["data_source"], completion, row["ground_truth"], row["extra_info"])
    assert reward > 0.9


def test_agent_rows_include_agent_loop_fields() -> None:
    task = generate_tasks(n=1, seed=654, families=("automata",), tiers=("easy",))[0]
    row = to_verl_rows([task], mode="agent")[0]
    assert row["agent_name"] == "active_program_induction"
    assert isinstance(row["raw_prompt"], list)
    assert row["extra_info"]["mode"] == "agent"


def test_multiturn_env_returns_observation_before_submit() -> None:
    task = generate_tasks(n=1, seed=987, families=("automata",), tiers=("easy",))[0]
    env = ActiveInductionEnv(task)
    env.reset()
    step = env.step({"tool": "query", "input": ""})
    assert step.done is False
    assert "observation" in step.observation
    final = env.step({"tool": "submit", "submission": task["hidden"]["dfa"]})
    assert final.done is True
    assert final.info["equivalent"] is True
    assert final.reward > 0.9
