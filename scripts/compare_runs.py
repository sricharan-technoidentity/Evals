"""Compare eval runs side by side: one column per run, one row per gate.

    python scripts/compare_runs.py                 # all logs under ./logs
    python scripts/compare_runs.py logs/2026-10-*  # specific log files or dirs

A "run" is one `inspect eval` invocation. Its label is model + prompt variant, so
re-running with a different --model or -T prompt_variant=... shows up as a new column.
Pass rates are averaged over samples and epochs.
"""

from __future__ import annotations

import sys
from collections import defaultdict
from pathlib import Path

from inspect_ai.log import list_eval_logs, read_eval_log

GATES = ["acceptance_tests", "checks_pass", "diff_scope", "safe_actions", "pr_description", "pr_ready"]


def _log_paths(args: list[str]) -> list[str]:
    targets = args or ["logs"]
    paths: list[str] = []
    for t in targets:
        p = Path(t)
        if p.is_dir():
            paths += [info.name for info in list_eval_logs(str(p), recursive=True)]
        elif p.exists():
            paths.append(str(p))
    return paths


def main() -> None:
    runs = []
    for path in sorted(_log_paths(sys.argv[1:])):
        log = read_eval_log(path)
        if log.status != "success" or not log.samples:
            continue
        args = log.eval.task_args or {}
        agent = args.get("agent") or (log.eval.metadata or {}).get("agent", "react")
        variant = "" if agent == "kiro" else f" {args.get('prompt_variant', 'v1')}"
        label = f"{agent}{variant} | {log.eval.model.split('/')[-1]} | {log.eval.created[5:16]}"
        per_gate: dict[str, list[float]] = defaultdict(list)
        per_ticket: dict[str, list[float]] = defaultdict(list)
        tokens = 0
        for s in log.samples:
            for gate in GATES:
                if gate in (s.scores or {}):
                    per_gate[gate].append(1.0 if s.scores[gate].value == "C" else 0.0)
            if "pr_ready" in (s.scores or {}):
                per_ticket[str(s.id)].append(1.0 if s.scores["pr_ready"].value == "C" else 0.0)
            tokens += sum(u.total_tokens for u in (s.model_usage or {}).values())
        runs.append((label, per_gate, per_ticket, tokens, len(log.samples)))

    if not runs:
        print("No successful logs found.")
        return

    def pct(xs: list[float]) -> str:
        return f"{100 * sum(xs) / len(xs):5.0f}%" if xs else "    -"

    width = max(len(r[0]) for r in runs)
    print("\nPass rate by gate")
    print(f"{'gate':<18}" + "".join(f" | {r[0]:<{width}}" for r in runs))
    for gate in GATES:
        print(f"{gate:<18}" + "".join(f" | {pct(r[1][gate]):<{width}}" for r in runs))
    print(f"{'samples':<18}" + "".join(f" | {r[4]:<{width}}" for r in runs))
    print(f"{'total tokens':<18}" + "".join(f" | {r[3]:<{width},}" for r in runs))

    tickets = sorted({t for r in runs for t in r[2]})
    print("\npr_ready by ticket")
    for t in tickets:
        print(f"{t:<18}" + "".join(f" | {pct(r[2].get(t, [])):<{width}}" for r in runs))


if __name__ == "__main__":
    main()
