"""Turn fixtures/<ticket>/ into Inspect Samples.

Each fixture directory holds:
  ticket.md        - what the agent sees (the "GitHub issue")
  ticket.json      - repo + pinned commit, setup, checks, allowed scope, hidden-test command
  hidden_tests/    - acceptance tests injected only at scoring time
  reference.patch  - a known-good fix, used only by scripts/verify_fixtures.py
"""

from __future__ import annotations

import json
from pathlib import Path

from inspect_ai.dataset import MemoryDataset, Sample

FIXTURES_DIR = Path(__file__).resolve().parent.parent / "fixtures"


def load_fixture(fixture_dir: Path) -> dict:
    meta = json.loads((fixture_dir / "ticket.json").read_text())
    meta["fixture_dir"] = str(fixture_dir)
    meta["ticket_md"] = (fixture_dir / "ticket.md").read_text()
    return meta


def ticket_dataset(tickets: str | list[str] | None = None) -> MemoryDataset:
    """All fixtures, optionally filtered by ticket id or directory name (comma-separated)."""
    wanted = None
    if tickets:
        wanted = {t.strip().lower() for t in (tickets.split(",") if isinstance(tickets, str) else tickets)}

    samples = []
    for d in sorted(p for p in FIXTURES_DIR.iterdir() if (p / "ticket.json").exists()):
        meta = load_fixture(d)
        if wanted and meta["id"].lower() not in wanted and d.name.lower() not in wanted:
            continue
        samples.append(
            Sample(
                id=meta["id"],
                input=meta["ticket_md"],
                # target = the ticket's acceptance criteria; the PR-description grader reads it
                target=meta["ticket_md"],
                metadata={k: v for k, v in meta.items() if k != "ticket_md"},
            )
        )
    if not samples:
        raise ValueError(f"No fixtures matched tickets={tickets!r} in {FIXTURES_DIR}")
    return MemoryDataset(samples, name="ticket-to-pr")
