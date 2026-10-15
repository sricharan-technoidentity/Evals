"""Validate the eval fixtures themselves (no model, no API key).

For each ticket this proves the hidden acceptance tests are a fair test:
  1. base commit:      setup + repo checks PASS,  hidden tests FAIL   (ticket not already done)
  2. reference.patch:  repo checks PASS,          hidden tests PASS   (ticket is solvable)

Run it once on any machine before trusting eval scores, and again after editing a fixture.

    python scripts/verify_fixtures.py               # all tickets
    python scripts/verify_fixtures.py PET-001 PET-002
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def sh(cmd: str, cwd: Path, timeout: int = 1800) -> tuple[bool, str]:
    r = subprocess.run(["bash", "-c", cmd], cwd=cwd, capture_output=True, text=True, timeout=timeout)
    return r.returncode == 0, (r.stdout + r.stderr)[-2000:]


def verify(fixture: Path, workdir: Path) -> list[tuple[str, bool, bool, str]]:
    meta = json.loads((fixture / "ticket.json").read_text())
    repo = workdir / meta["id"]
    results = []

    def step(label: str, cmd: str, expect_ok: bool, cwd: Path = repo) -> bool:
        t0 = time.monotonic()
        ok, out = sh(cmd, cwd)
        good = ok == expect_ok
        results.append((label, ok, good, "" if good else out))
        mark = "ok " if good else "BAD"
        print(f"  [{mark}] {label:<44} {'pass' if ok else 'fail'} (expected {'pass' if expect_ok else 'fail'}) {time.monotonic() - t0:5.0f}s")
        return good

    def inject_hidden() -> None:
        for dest, src in meta["hidden_tests"]["files"].items():
            (repo / dest).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(fixture / src, repo / dest)

    def remove_hidden() -> None:
        for dest in meta["hidden_tests"]["files"]:
            (repo / dest).unlink(missing_ok=True)

    print(f"\n{meta['id']}  ({meta['repo']['name']} @ {meta['repo']['commit'][:8]})")
    if not step("clone + checkout", f"git clone -q {meta['repo']['url']} {repo} && git -C {repo} checkout -q {meta['repo']['commit']}", True, cwd=workdir):
        return results
    for cmd in meta["setup"]:
        if not step(f"setup: {cmd[:34]}", cmd, True):
            return results
    for check in meta["checks"]:
        step(f"base   check: {check['name'][:30]}", check["cmd"], True)
    inject_hidden()
    step("base   hidden tests", meta["hidden_tests"]["cmd"], False)
    remove_hidden()

    if not step("apply reference.patch", f"git apply {fixture / 'reference.patch'}", True):
        return results
    for check in meta["checks"]:
        step(f"ref    check: {check['name'][:30]}", check["cmd"], True)
    inject_hidden()
    step("ref    hidden tests", meta["hidden_tests"]["cmd"], True)
    remove_hidden()
    return results


def main() -> None:
    wanted = {a.lower() for a in sys.argv[1:]}
    fixtures = [
        p.parent for p in sorted((ROOT / "fixtures").glob("*/ticket.json"))
        if not wanted or json.loads(p.read_text())["id"].lower() in wanted or p.parent.name.lower() in wanted
    ]
    bad = []
    with tempfile.TemporaryDirectory(prefix="verify-fixtures-") as tmp:
        for fx in fixtures:
            for label, _ok, good, out in verify(fx, Path(tmp)):
                if not good:
                    bad.append((fx.name, label, out))
    print("\n" + ("All fixtures verified." if not bad else f"{len(bad)} unexpected result(s):"))
    for name, label, out in bad:
        print(f"\n--- {name}: {label}\n{out}")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
