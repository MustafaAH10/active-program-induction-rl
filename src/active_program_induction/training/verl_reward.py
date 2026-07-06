from __future__ import annotations

import json
from typing import Any

from active_program_induction.scoring import score_completion


def compute_score(
    data_source: str,
    solution_str: str,
    ground_truth: str,
    extra_info: dict[str, Any] | None = None,
) -> float:
    """veRL custom reward function.

    veRL calls this as `compute_score(data_source, solution_str, ground_truth,
    extra_info=None)`. `ground_truth` is the serialized task JSON produced by
    `api-bench generate --parquet-out ...`; `solution_str` is the model's JSON
    transcript completion.
    """
    try:
        task = json.loads(ground_truth)
        mode = "graded"
        if extra_info and extra_info.get("reward_mode"):
            mode = str(extra_info["reward_mode"])
        result = score_completion(task, solution_str, mode=mode)
        return float(result["reward"])
    except Exception:
        return -0.1


def compute_score_exact(
    data_source: str,
    solution_str: str,
    ground_truth: str,
    extra_info: dict[str, Any] | None = None,
) -> float:
    try:
        task = json.loads(ground_truth)
        return float(score_completion(task, solution_str, mode="exact")["reward"])
    except Exception:
        return -0.1
