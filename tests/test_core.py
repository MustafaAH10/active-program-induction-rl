from __future__ import annotations

import json

from active_program_induction import agents
from active_program_induction.dataset import generate_tasks, to_verl_rows
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
