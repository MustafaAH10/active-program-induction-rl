from __future__ import annotations

from dataclasses import dataclass
from itertools import product
import random
from typing import Any


Expr = dict[str, Any]


def eval_expr(expr: Expr, x: list[int]) -> int:
    op = expr["op"]
    if op == "var":
        name = expr["var"]
        idx = int(name[1:] if isinstance(name, str) and name.startswith("x") else name)
        return int(bool(x[idx]))
    if op == "not":
        return int(not bool(eval_expr(expr["arg"], x)))
    if op == "and":
        return int(all(bool(eval_expr(arg, x)) for arg in expr["args"]))
    if op == "or":
        return int(any(bool(eval_expr(arg, x)) for arg in expr["args"]))
    if op == "xor":
        out = 0
        for arg in expr["args"]:
            out ^= int(bool(eval_expr(arg, x)))
        return out
    raise ValueError(f"unknown op {op!r}")


def used_vars(expr: Expr) -> set[int]:
    op = expr["op"]
    if op == "var":
        name = expr["var"]
        return {int(name[1:] if isinstance(name, str) and name.startswith("x") else name)}
    if op == "not":
        return used_vars(expr["arg"])
    if op in {"and", "or", "xor"}:
        out: set[int] = set()
        for arg in expr["args"]:
            out |= used_vars(arg)
        return out
    raise ValueError(f"unknown op {op!r}")


@dataclass(frozen=True)
class Junta:
    n_bits: int
    expr: Expr

    def run(self, x: list[int]) -> int:
        if len(x) != self.n_bits or any(bit not in (0, 1) for bit in x):
            raise ValueError(f"expected {self.n_bits} bits")
        return eval_expr(self.expr, x)

    def to_json(self) -> dict:
        return {"n_bits": self.n_bits, "expr": self.expr}

    @classmethod
    def from_json(cls, obj: dict) -> "Junta":
        return cls(n_bits=int(obj["n_bits"]), expr=obj["expr"])


def equivalent(a: Junta, b: Junta) -> tuple[bool, list[int] | None]:
    if a.n_bits != b.n_bits:
        raise ValueError("n_bits differ")
    for bits in product([0, 1], repeat=a.n_bits):
        x = list(bits)
        if a.run(x) != b.run(x):
            return False, x
    return True, None


def random_junta(rng: random.Random, n_bits: int, k: int) -> Junta:
    vars_ = rng.sample(range(n_bits), k)
    leaves = [{"op": "var", "var": f"x{i}"} for i in vars_]
    if k == 1:
        expr = leaves[0]
    elif k == 2:
        expr = {"op": rng.choice(["and", "or", "xor"]), "args": leaves}
    else:
        first = {"op": rng.choice(["and", "or"]), "args": leaves[:2]}
        maybe_not = {"op": "not", "arg": leaves[2]} if rng.random() < 0.5 else leaves[2]
        expr = {"op": "xor", "args": [first, maybe_not]}
        for leaf in leaves[3:]:
            expr = {"op": rng.choice(["and", "xor"]), "args": [expr, leaf]}
    junta = Junta(n_bits=n_bits, expr=expr)
    if not dense_enough(junta):
        return random_junta(rng, n_bits, k)
    return junta


def dense_enough(junta: Junta, low: float = 0.15, high: float = 0.85) -> bool:
    labels = [junta.run(list(bits)) for bits in product([0, 1], repeat=junta.n_bits)]
    rate = sum(labels) / len(labels)
    return low <= rate <= high


def make_task(rng: random.Random, task_id: str, tier: str = "easy") -> dict:
    params = {
        "easy": (5, 2, 8),
        "medium": (7, 3, 12),
        "hard": (9, 4, 16),
    }.get(tier, (5, 2, 8))
    n_bits, k, budget = params
    junta = random_junta(rng, n_bits=n_bits, k=k)
    return {
        "task_id": task_id,
        "family": "boolean_junta",
        "tier": tier,
        "public": {
            "signature": f"f: {{0,1}}^{n_bits} -> {{0,1}}",
            "n_bits": n_bits,
            "probe_budget": budget,
            "actions": ["query", "submit"],
            "submission_format": f"boolean expression AST over variables x0..x{n_bits - 1}",
        },
        "hidden": junta.to_json(),
        "reward": {"query_cost": 0.002, "invalid_penalty": 0.05},
    }
