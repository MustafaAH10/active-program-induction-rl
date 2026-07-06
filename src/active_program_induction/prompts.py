from __future__ import annotations

import json

from active_program_induction.env import initial_messages


ACTIVE_SYSTEM = """You are solving an active program induction task.
You may choose probe inputs, observe hidden outputs, and then submit a hypothesis.
For this benchmark completion, emit a single JSON object containing all probes you
would make and your final submission. Do not use markdown.

Required output schema:
{
  "queries": [<input>, ...],
  "submission": <family-specific submission>
}

The evaluator will execute your queries against the hidden oracle in order, then
grade only the final submission. Use as few informative queries as possible.
"""


PASSIVE_SYSTEM = """You are solving a passive program induction task.
You are given fixed examples from a hidden function and must submit a hypothesis.
Emit a single JSON object with this schema and no markdown:
{"submission": <family-specific submission>}
"""


def active_prompt(task: dict) -> str:
    public = task["public"]
    body = {
        "task_id": task["task_id"],
        "family": task["family"],
        "public_spec": public,
    }
    return ACTIVE_SYSTEM + "\nTask:\n" + json.dumps(body, indent=2, sort_keys=True)


def agent_loop_prompt(task: dict) -> str:
    return "\n\n".join(f"{m['role'].upper()}:\n{m['content']}" for m in initial_messages(task))


def passive_prompt(task: dict, examples: list[dict]) -> str:
    public = dict(task["public"])
    public.pop("probe_budget", None)
    body = {
        "task_id": task["task_id"],
        "family": task["family"],
        "public_spec": public,
        "examples": examples,
    }
    return PASSIVE_SYSTEM + "\nTask:\n" + json.dumps(body, indent=2, sort_keys=True)


def fewshot_dfa_submission() -> dict:
    return {
        "states": ["s0", "s1"],
        "alphabet": ["a", "b"],
        "start": "s0",
        "accept": ["s1"],
        "delta": {
            "s0,a": "s1",
            "s0,b": "s0",
            "s1,a": "s1",
            "s1,b": "s0",
        },
    }
