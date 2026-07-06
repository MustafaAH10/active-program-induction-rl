from __future__ import annotations

import json
import re
from typing import Any

from active_program_induction import dfa as dfa_mod
from active_program_induction import junta as junta_mod


def extract_json_object(text: str) -> dict[str, Any]:
    """Extract the first JSON object from a model completion."""
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start < 0 or end <= start:
            raise
        parsed = json.loads(text[start : end + 1])
    if not isinstance(parsed, dict):
        raise ValueError("completion JSON must be an object")
    return parsed


def score_completion(task: dict, completion: str | dict[str, Any], mode: str = "exact") -> dict:
    parsed = extract_json_object(completion) if isinstance(completion, str) else completion
    family = task["family"]
    if family == "automata":
        return _score_dfa(task, parsed, mode=mode)
    if family == "boolean_junta":
        return _score_junta(task, parsed, mode=mode)
    raise NotImplementedError(f"family {family!r} is not implemented in scorer")


def _queries(parsed: dict) -> list:
    queries = parsed.get("queries", [])
    if queries is None:
        return []
    if not isinstance(queries, list):
        raise ValueError("queries must be a list")
    return queries


def _score_dfa(task: dict, parsed: dict, mode: str) -> dict:
    hidden = dfa_mod.DFA.from_json(task["hidden"]["dfa"])
    query_cost = float(task.get("reward", {}).get("query_cost", 0.002))
    invalid_penalty = float(task.get("reward", {}).get("invalid_penalty", 0.05))
    budget = int(task["public"]["probe_budget"])
    observations = []
    penalty = 0.0
    for query in _queries(parsed)[: budget + 1]:
        if not isinstance(query, str):
            penalty += invalid_penalty
            continue
        try:
            observations.append({"input": query, "output": hidden.run(query)})
        except Exception:
            penalty += invalid_penalty
    if len(_queries(parsed)) > budget:
        penalty += invalid_penalty * (len(_queries(parsed)) - budget)

    submission = parsed.get("submission", parsed.get("dfa"))
    equivalent = False
    witness = None
    partial = 0.0
    try:
        submitted = dfa_mod.DFA.from_json(submission)
        equivalent, witness = dfa_mod.equivalent(hidden, submitted)
        if mode == "graded" and not equivalent:
            partial = _dfa_fraction_agree(hidden, submitted, max_len=4)
    except Exception as exc:
        return _result(False, 0.0, observations, penalty + invalid_penalty, str(exc), None)

    correct = 1.0 if equivalent else partial
    reward = correct - query_cost * min(len(_queries(parsed)), budget) - penalty
    return _result(equivalent, reward, observations, penalty, None, witness)


def _score_junta(task: dict, parsed: dict, mode: str) -> dict:
    hidden = junta_mod.Junta.from_json(task["hidden"])
    query_cost = float(task.get("reward", {}).get("query_cost", 0.002))
    invalid_penalty = float(task.get("reward", {}).get("invalid_penalty", 0.05))
    budget = int(task["public"]["probe_budget"])
    observations = []
    penalty = 0.0
    for query in _queries(parsed)[: budget + 1]:
        if not isinstance(query, list):
            penalty += invalid_penalty
            continue
        try:
            observations.append({"input": query, "output": hidden.run(query)})
        except Exception:
            penalty += invalid_penalty
    if len(_queries(parsed)) > budget:
        penalty += invalid_penalty * (len(_queries(parsed)) - budget)

    submission = parsed.get("submission", parsed.get("expr"))
    if isinstance(submission, dict) and "expr" in submission:
        submission = submission["expr"]
    equivalent = False
    witness = None
    partial = 0.0
    try:
        submitted = junta_mod.Junta(n_bits=hidden.n_bits, expr=submission)
        equivalent, witness = junta_mod.equivalent(hidden, submitted)
        if mode == "graded" and not equivalent:
            partial = _junta_fraction_agree(hidden, submitted)
    except Exception as exc:
        return _result(False, 0.0, observations, penalty + invalid_penalty, str(exc), None)

    correct = 1.0 if equivalent else partial
    reward = correct - query_cost * min(len(_queries(parsed)), budget) - penalty
    return _result(equivalent, reward, observations, penalty, None, witness)


def _result(
    equivalent: bool,
    reward: float,
    observations: list[dict],
    penalty: float,
    error: str | None,
    witness: Any,
) -> dict:
    return {
        "equivalent": equivalent,
        "reward": round(float(reward), 6),
        "num_queries": len(observations),
        "observations": observations,
        "penalty": round(float(penalty), 6),
        "error": error,
        "counterexample": witness,
    }


def _dfa_fraction_agree(a: dfa_mod.DFA, b: dfa_mod.DFA, max_len: int) -> float:
    words = dfa_mod.enumerate_words(a.alphabet, max_len)
    agree = sum(1 for word in words if a.run(word) == b.run(word))
    return agree / len(words)


def _junta_fraction_agree(a: junta_mod.Junta, b: junta_mod.Junta) -> float:
    total = 2 ** a.n_bits
    agree = 0
    for n in range(total):
        bits = [(n >> i) & 1 for i in range(a.n_bits)]
        agree += int(a.run(bits) == b.run(bits))
    return agree / total
