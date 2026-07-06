from __future__ import annotations

import json
from pathlib import Path
import random
from typing import Iterable

from active_program_induction import dfa, junta
from active_program_induction.env import initial_messages
from active_program_induction.prompts import active_prompt, agent_loop_prompt, passive_prompt


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


def sample_examples(task: dict, n: int = 8, seed: int = 0) -> list[dict]:
    rng = random.Random(seed)
    examples = []
    if task["family"] == "automata":
        oracle = dfa.DFA.from_json(task["hidden"]["dfa"])
        candidates = dfa.enumerate_words(task["public"]["alphabet"], max_len=4)
        rng.shuffle(candidates)
        for word in candidates[:n]:
            examples.append({"input": word, "output": oracle.run(word)})
        return examples
    if task["family"] == "boolean_junta":
        oracle = junta.Junta.from_json(task["hidden"])
        seen = set()
        while len(examples) < n:
            x = tuple(rng.randint(0, 1) for _ in range(oracle.n_bits))
            if x in seen:
                continue
            seen.add(x)
            examples.append({"input": list(x), "output": oracle.run(list(x))})
        return examples
    raise ValueError(f"unknown family {task['family']!r}")


def to_verl_rows(tasks: Iterable[dict], split: str = "train", mode: str = "agent") -> list[dict]:
    if mode not in {"agent", "active", "passive"}:
        raise ValueError("mode must be agent, active, or passive")
    rows = []
    for idx, task in enumerate(tasks):
        ground_truth = json.dumps(task, sort_keys=True)
        prompt = agent_loop_prompt(task) if mode == "agent" else active_prompt(task)
        if mode == "passive":
            prompt = passive_prompt(task, sample_examples(task, seed=idx))
        row = {
            "data_source": "active_program_induction",
            "prompt": prompt,
            "ability": task["family"],
            "reward_model": {"style": "rule", "ground_truth": ground_truth},
            "ground_truth": ground_truth,
            "extra_info": {
                "split": split,
                "mode": mode,
                "task_id": task["task_id"],
                "family": task["family"],
                "tier": task["tier"],
            },
        }
        if mode == "agent":
            row["agent_name"] = "active_program_induction"
            row["raw_prompt"] = initial_messages(task)
        rows.append(row)
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
