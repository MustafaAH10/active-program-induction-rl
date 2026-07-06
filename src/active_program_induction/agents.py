from __future__ import annotations

import random

from active_program_induction import dfa as dfa_mod
from active_program_induction import junta as junta_mod


def oracle_completion(task: dict) -> dict:
    """Return a perfect completion for smoke testing the scorer."""
    if task["family"] == "automata":
        hidden = task["hidden"]["dfa"]
        queries = ["", "a", "b", "ab"]
        return {"queries": queries, "submission": hidden}
    if task["family"] == "boolean_junta":
        n = task["public"]["n_bits"]
        queries = [[0] * n]
        for i in range(min(n, task["public"]["probe_budget"] - 1)):
            x = [0] * n
            x[i] = 1
            queries.append(x)
        return {"queries": queries, "submission": task["hidden"]["expr"]}
    raise NotImplementedError(task["family"])


def deliberately_wrong_completion(task: dict) -> dict:
    if task["family"] == "automata":
        hidden = dfa_mod.DFA.from_json(task["hidden"]["dfa"])
        accept = set(hidden.accept)
        if hidden.states[0] in accept:
            accept.remove(hidden.states[0])
        else:
            accept.add(hidden.states[0])
        wrong = dfa_mod.DFA(
            states=hidden.states,
            alphabet=hidden.alphabet,
            start=hidden.start,
            accept=frozenset(accept),
            delta=hidden.delta,
        )
        return {"queries": [""], "submission": wrong.to_json()}
    if task["family"] == "boolean_junta":
        expr = {"op": "var", "var": "x0"}
        return {"queries": [[0] * task["public"]["n_bits"]], "submission": expr}
    raise NotImplementedError(task["family"])


def random_completion(task: dict, seed: int = 0) -> dict:
    rng = random.Random(seed)
    if task["family"] == "automata":
        alphabet = task["public"]["alphabet"]
        queries = [
            "".join(rng.choice(alphabet) for _ in range(rng.randint(0, 4)))
            for _ in range(min(4, task["public"]["probe_budget"]))
        ]
        return {"queries": queries, "submission": task["hidden"]["dfa"]}
    if task["family"] == "boolean_junta":
        n = task["public"]["n_bits"]
        queries = [[rng.randint(0, 1) for _ in range(n)] for _ in range(4)]
        return {"queries": queries, "submission": task["hidden"]["expr"]}
    raise NotImplementedError(task["family"])
