from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

from active_program_induction import dfa as dfa_mod
from active_program_induction import junta as junta_mod
from active_program_induction.scoring import extract_json_object, score_completion


MULTITURN_SYSTEM = """You are solving an active program induction task.
On each turn, output exactly one JSON action and no markdown.

Allowed actions:
  {"tool":"query","input":<input>}
  {"tool":"submit","submission":<family-specific hypothesis>}

After a query, the environment will return the hidden function output. Use
those observations to adapt your next query. Submit when you have inferred the
hidden program. Fewer queries are better.
"""


def initial_user_message(task: dict) -> str:
    return "Task:\n" + json.dumps(
        {
            "task_id": task["task_id"],
            "family": task["family"],
            "public_spec": task["public"],
        },
        indent=2,
        sort_keys=True,
    )


def initial_messages(task: dict) -> list[dict[str, str]]:
    return [
        {"role": "system", "content": MULTITURN_SYSTEM},
        {"role": "user", "content": initial_user_message(task)},
    ]


@dataclass
class StepResult:
    observation: str
    reward: float
    done: bool
    info: dict[str, Any] = field(default_factory=dict)


class ActiveInductionEnv:
    """True adaptive environment for one active program induction task."""

    def __init__(self, task: dict, reward_mode: str = "graded"):
        self.task = task
        self.reward_mode = reward_mode
        self.queries: list[Any] = []
        self.done = False
        self.final_score: dict[str, Any] | None = None

    @property
    def budget(self) -> int:
        return int(self.task["public"]["probe_budget"])

    def reset(self) -> str:
        self.queries = []
        self.done = False
        self.final_score = None
        return initial_user_message(self.task)

    def step_text(self, action_text: str) -> StepResult:
        try:
            action = extract_json_object(action_text)
        except Exception as exc:
            return self._invalid(f"invalid JSON action: {exc}")
        return self.step(action)

    def step(self, action: dict[str, Any]) -> StepResult:
        if self.done:
            return StepResult("Episode is already done.", 0.0, True, {"error": "already_done"})
        tool = action.get("tool")
        if tool == "query":
            return self._query(action.get("input"))
        if tool == "submit":
            return self._submit(action.get("submission", action.get("dfa", action.get("expr"))))
        return self._invalid("unknown tool; expected query or submit")

    def _query(self, value: Any) -> StepResult:
        if len(self.queries) >= self.budget:
            return self._invalid("probe budget exhausted")
        try:
            output = self._run_oracle(value)
        except Exception as exc:
            return self._invalid(f"invalid query input: {exc}")
        self.queries.append(value)
        obs = json.dumps({"observation": {"input": value, "output": output}, "queries_used": len(self.queries)})
        return StepResult(obs, 0.0, False, {"query_output": output, "queries_used": len(self.queries)})

    def _submit(self, submission: Any) -> StepResult:
        self.done = True
        completion = {"queries": self.queries, "submission": submission}
        self.final_score = score_completion(self.task, completion, mode=self.reward_mode)
        obs = json.dumps({"final": self.final_score}, sort_keys=True)
        return StepResult(obs, float(self.final_score["reward"]), True, self.final_score)

    def _invalid(self, message: str) -> StepResult:
        penalty = -float(self.task.get("reward", {}).get("invalid_penalty", 0.05))
        obs = json.dumps({"error": message, "queries_used": len(self.queries)})
        return StepResult(obs, penalty, False, {"error": message})

    def _run_oracle(self, value: Any) -> Any:
        family = self.task["family"]
        if family == "automata":
            return dfa_mod.DFA.from_json(self.task["hidden"]["dfa"]).run(value)
        if family == "boolean_junta":
            return junta_mod.Junta.from_json(self.task["hidden"]).run(value)
        raise NotImplementedError(f"family {family!r}")
