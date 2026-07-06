from __future__ import annotations

import json
from pathlib import Path
import random
from typing import Iterable

from active_program_induction import dfa, junta
from active_program_induction.prompts import active_prompt


def generate_tasks(
    n: int,
    families: Iterable[str] = ("automata", "boolean_junta"),
    tiers: Iterable[str] = ("easy", "medium", "hard"),
    seed: int = 0,
) -> list[dict]:
    rng = random.Random(seed)
    families_t = tuple(families)
    tiers_t = tuple(tiers)
    tasks = []
    for idx in range(n):
        family = families_t[idx % len(families_t)]
        tier = tiers_t[(idx // len(families_t)) % len(tiers_t)]
        task_id = f"{family}_{tier}_{idx:06d}"
        if family == "automata":
            task = dfa.make_task(rng, task_id=task_id, tier=tier)
        elif family == "boolean_junta":
            task = junta.make_task(rng, task_id=task_id, tier=tier)
        else:
            raise ValueError(f"unknown family {family!r}")
        tasks.append(task)
    return tasks


def write_jsonl(rows: Iterable[dict], path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, sort_keys=True) + "\n")


def read_jsonl(path: str | Path) -> list[dict]:
    with Path(path).open("r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def to_verl_rows(tasks: Iterable[dict], split: str = "train") -> list[dict]:
    rows = []
    for task in tasks:
        ground_truth = json.dumps(task, sort_keys=True)
        rows.append(
            {
                "data_source": "active_program_induction",
                "prompt": active_prompt(task),
                "ability": task["family"],
                "reward_model": {"style": "rule", "ground_truth": ground_truth},
                "ground_truth": ground_truth,
                "extra_info": {
                    "split": split,
                    "task_id": task["task_id"],
                    "family": task["family"],
                    "tier": task["tier"],
                },
            }
        )
    return rows


def write_parquet(rows: list[dict], path: str | Path) -> None:
    try:
        import pyarrow as pa
        import pyarrow.parquet as pq
    except ImportError as exc:
        raise RuntimeError("Install pyarrow or use JSONL output: pip install '.[data]'") from exc
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    table = pa.Table.from_pylist(rows)
    pq.write_table(table, path)
