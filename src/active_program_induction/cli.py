from __future__ import annotations

import argparse
import json
from pathlib import Path

from active_program_induction import agents
from active_program_induction.dataset import generate_tasks, to_verl_rows, write_jsonl, write_parquet
from active_program_induction.scoring import score_completion


def main() -> None:
    parser = argparse.ArgumentParser(prog="api-bench")
    sub = parser.add_subparsers(dest="cmd", required=True)

    gen = sub.add_parser("generate", help="generate benchmark tasks")
    gen.add_argument("--n", type=int, default=100)
    gen.add_argument("--seed", type=int, default=0)
    gen.add_argument("--families", default="automata,boolean_junta")
    gen.add_argument("--tiers", default="easy,medium,hard")
    gen.add_argument("--out", default="data/generated/tasks.jsonl")
    gen.add_argument("--verl-out", default=None, help="optional veRL JSONL rows")
    gen.add_argument("--parquet-out", default=None, help="optional veRL parquet rows")
    gen.add_argument("--mode", choices=["active", "passive"], default="active")

    smoke = sub.add_parser("smoke", help="run CPU scorer smoke test")
    smoke.add_argument("--n", type=int, default=20)
    smoke.add_argument("--seed", type=int, default=0)

    score = sub.add_parser("score", help="score one completion against one task JSON")
    score.add_argument("--task-json", required=True)
    score.add_argument("--completion-json", required=True)
    score.add_argument("--mode", choices=["exact", "graded"], default="exact")

    args = parser.parse_args()
    if args.cmd == "generate":
        tasks = generate_tasks(
            n=args.n,
            seed=args.seed,
            families=[x for x in args.families.split(",") if x],
            tiers=[x for x in args.tiers.split(",") if x],
        )
        write_jsonl(tasks, args.out)
        print(f"wrote {len(tasks)} tasks to {args.out}")
        if args.verl_out:
            rows = to_verl_rows(tasks, mode=args.mode)
            write_jsonl(rows, args.verl_out)
            print(f"wrote {len(rows)} veRL JSONL rows to {args.verl_out}")
        if args.parquet_out:
            rows = to_verl_rows(tasks, mode=args.mode)
            write_parquet(rows, args.parquet_out)
            print(f"wrote {len(rows)} veRL parquet rows to {args.parquet_out}")
    elif args.cmd == "smoke":
        run_smoke(args.n, args.seed)
    elif args.cmd == "score":
        task = json.loads(Path(args.task_json).read_text(encoding="utf-8"))
        completion = Path(args.completion_json).read_text(encoding="utf-8")
        print(json.dumps(score_completion(task, completion, mode=args.mode), indent=2, sort_keys=True))


def run_smoke(n: int, seed: int) -> None:
    tasks = generate_tasks(n=n, seed=seed, families=("automata", "boolean_junta"), tiers=("easy",))
    ok = 0
    wrong_ok = 0
    for task in tasks:
        perfect = score_completion(task, agents.oracle_completion(task))
        wrong = score_completion(task, agents.deliberately_wrong_completion(task))
        if perfect["equivalent"] and perfect["reward"] > 0.9:
            ok += 1
        if not wrong["equivalent"] and wrong["reward"] < perfect["reward"]:
            wrong_ok += 1
    print(json.dumps({"tasks": n, "perfect_passed": ok, "wrong_rejected": wrong_ok}, indent=2))
    if ok != n or wrong_ok != n:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
