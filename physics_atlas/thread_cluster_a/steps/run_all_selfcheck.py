#!/usr/bin/env python3
"""Run all Cluster A step validators (auto-discovering).

Discovers every `step*/run_step*.py` and runs it with `--self`, sorted by step number.

REPRODUCIBILITY HONESTY (do not over-advertise): `--self` runs each step's *validator*,
which for MOST steps checks artifacts in place, but for SOME steps RE-EXECUTES the build
script and/or prior validators (e.g. Step 14). Several builds are heavy enumerations
(Steps 28/33/43 enumerate hundreds of thousands of closers), so the FULL all-step run can
be slow and may exceed a tight (e.g. 300 s) timeout in some environments. This is NOT a
guaranteed quick artifact-only validator. The new Steps 45-49 (`--self` and `--chain`)
are individually quick and pass. Per-step recursive rebuild = `run_stepK.py --chain`.
Exit code is nonzero if any validator fails.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path


STEPS_DIR = Path(__file__).resolve().parent


def step_key(runner: Path) -> tuple[int, str]:
    m = re.search(r"run_step(\d+)\.py$", runner.name)
    return (int(m.group(1)) if m else 9999, str(runner))


def main() -> None:
    runners = sorted(STEPS_DIR.glob("step*/run_step*.py"), key=step_key)
    rows, failures = [], []
    for runner in runners:
        label = re.search(r"run_(step\d+)\.py$", runner.name).group(1)
        result = subprocess.run(
            [sys.executable, str(runner), "--self"],
            cwd=STEPS_DIR, text=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
        )
        status = "PASS" if result.returncode == 0 else "FAIL"
        rows.append((label, status))
        if result.returncode != 0:
            failures.append((label, runner, result.stdout, result.stderr))

    print("Cluster A self-check table")
    print("step,status")
    for label, status in rows:
        print(f"{label},{status}")
    print(f"\n{sum(1 for _, s in rows if s == 'PASS')}/{len(rows)} PASS")

    if failures:
        print("\nFailures:", file=sys.stderr)
        for label, runner, stdout, stderr in failures:
            print(f"\n[{label}] {runner}\nstdout:\n{stdout}\nstderr:\n{stderr}", file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
