from __future__ import annotations

from collections import deque
from dataclasses import dataclass
import random
from typing import Iterable


@dataclass(frozen=True)
class DFA:
    states: tuple[str, ...]
    alphabet: tuple[str, ...]
    start: str
    accept: frozenset[str]
    delta: dict[tuple[str, str], str]

    def run(self, s: str) -> bool:
        state = self.start
        for ch in s:
            if ch not in self.alphabet:
                raise ValueError(f"symbol {ch!r} not in alphabet {self.alphabet}")
            state = self.delta[(state, ch)]
        return state in self.accept

    def to_json(self) -> dict:
        return {
            "states": list(self.states),
            "alphabet": list(self.alphabet),
            "start": self.start,
            "accept": sorted(self.accept),
            "delta": {f"{q},{a}": r for (q, a), r in sorted(self.delta.items())},
        }

    @classmethod
    def from_json(cls, obj: dict) -> "DFA":
        alphabet = tuple(obj.get("alphabet", ["a", "b"]))
        states = tuple(obj["states"])
        raw_delta = obj["delta"]
        delta: dict[tuple[str, str], str] = {}
        for key, value in raw_delta.items():
            if isinstance(key, str):
                left, sym = key.split(",", 1)
                delta[(left, sym)] = value
            else:
                delta[tuple(key)] = value
        dfa = cls(
            states=states,
            alphabet=alphabet,
            start=obj["start"],
            accept=frozenset(obj["accept"]),
            delta=delta,
        )
        dfa.validate()
        return dfa

    def validate(self) -> None:
        state_set = set(self.states)
        if self.start not in state_set:
            raise ValueError("start state is not in states")
        if not self.accept <= state_set:
            raise ValueError("accept contains unknown states")
        for q in self.states:
            for a in self.alphabet:
                target = self.delta.get((q, a))
                if target not in state_set:
                    raise ValueError(f"missing/invalid transition for {(q, a)}")


def reachable_states(dfa: DFA) -> set[str]:
    seen = {dfa.start}
    queue = deque([dfa.start])
    while queue:
        q = queue.popleft()
        for a in dfa.alphabet:
            nxt = dfa.delta[(q, a)]
            if nxt not in seen:
                seen.add(nxt)
                queue.append(nxt)
    return seen


def equivalent(a: DFA, b: DFA) -> tuple[bool, str | None]:
    if a.alphabet != b.alphabet:
        raise ValueError("alphabets differ")
    queue = deque([((a.start, b.start), "")])
    seen = {(a.start, b.start)}
    while queue:
        (qa, qb), word = queue.popleft()
        if (qa in a.accept) != (qb in b.accept):
            return False, word
        for sym in a.alphabet:
            pair = (a.delta[(qa, sym)], b.delta[(qb, sym)])
            if pair not in seen:
                seen.add(pair)
                queue.append((pair, word + sym))
    return True, None


def _distinguishable_table(dfa: DFA) -> set[tuple[str, str]]:
    states = list(dfa.states)
    marked: set[tuple[str, str]] = set()
    for i, p in enumerate(states):
        for q in states[i + 1 :]:
            if (p in dfa.accept) != (q in dfa.accept):
                marked.add(tuple(sorted((p, q))))
    changed = True
    while changed:
        changed = False
        for i, p in enumerate(states):
            for q in states[i + 1 :]:
                pair = tuple(sorted((p, q)))
                if pair in marked:
                    continue
                for sym in dfa.alphabet:
                    nxt = tuple(sorted((dfa.delta[(p, sym)], dfa.delta[(q, sym)])))
                    if nxt in marked:
                        marked.add(pair)
                        changed = True
                        break
    return marked


def is_minimal(dfa: DFA) -> bool:
    if reachable_states(dfa) != set(dfa.states):
        return False
    n = len(dfa.states)
    marked = _distinguishable_table(dfa)
    return len(marked) == n * (n - 1) // 2


def random_dfa(
    rng: random.Random,
    num_states: int,
    alphabet: Iterable[str] = ("a", "b"),
    max_tries: int = 5000,
) -> DFA:
    alphabet_t = tuple(alphabet)
    states = tuple(f"q{i}" for i in range(num_states))
    for _ in range(max_tries):
        delta = {
            (q, a): rng.choice(states)
            for q in states
            for a in alphabet_t
        }
        accept = frozenset(q for q in states if rng.random() < 0.5)
        if not accept or len(accept) == len(states):
            continue
        dfa = DFA(states=states, alphabet=alphabet_t, start=states[0], accept=accept, delta=delta)
        if is_minimal(dfa) and dense_enough(dfa):
            return dfa
    raise RuntimeError(f"failed to sample a minimal dense DFA with {num_states} states")


def dense_enough(dfa: DFA, max_len: int = 5, low: float = 0.15, high: float = 0.85) -> bool:
    labels = [dfa.run(word) for word in enumerate_words(dfa.alphabet, max_len)]
    rate = sum(labels) / len(labels)
    return low <= rate <= high


def enumerate_words(alphabet: Iterable[str], max_len: int) -> list[str]:
    alphabet_t = tuple(alphabet)
    words = [""]
    frontier = [""]
    for _ in range(max_len):
        frontier = [prefix + sym for prefix in frontier for sym in alphabet_t]
        words.extend(frontier)
    return words


def make_task(rng: random.Random, task_id: str, tier: str = "easy") -> dict:
    states_by_tier = {"easy": 3, "medium": 4, "hard": 5}
    num_states = states_by_tier.get(tier, 3)
    dfa = random_dfa(rng, num_states=num_states)
    budget = {"easy": 8, "medium": 12, "hard": 16}.get(tier, 8)
    return {
        "task_id": task_id,
        "family": "automata",
        "tier": tier,
        "public": {
            "signature": "f: string over {a,b} -> bool",
            "alphabet": list(dfa.alphabet),
            "empty_string_allowed": True,
            "probe_budget": budget,
            "actions": ["query", "submit"],
            "submission_format": "DFA JSON",
        },
        "hidden": {"dfa": dfa.to_json()},
        "reward": {"query_cost": 0.002, "invalid_penalty": 0.05},
    }
