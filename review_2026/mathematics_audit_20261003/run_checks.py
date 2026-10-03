"""Replay the repaired validators in a snapshot containing publishable files.

Use --all to include every current claim-registry/open-program validator and
all historical atlas step validators. Each command gets its own scratch copy,
since some historical --self runners regenerate artifacts. No paper is edited.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[2]
CHANGED = (
    "open_programs/prog2_state_underdetermination/step4_finite_continuation/run_step4.py --self",
    "open_programs/prog2_state_underdetermination/step6_exact_gauge_collapse/run_step6.py --self",
    "physics_atlas/thread_cluster_a/steps/step61_mode_t_single_factor_clean_separation_theorem_artifacts/run_step61.py --self",
    "physics_atlas/thread_cluster_a/steps/step69_mode_t_record_stability_baryon_no_monopole_falsifiable_prediction_artifacts/run_step69.py --self",
    "physics_atlas/thread_qm_gr/steps/step27_constraint_problem_of_time_artifacts/run_step27.py --self",
    "physics_atlas/thread_qm_gr/steps/step28_nonstationary_relational_histories_artifacts/run_step28.py --self",
    "review_2026/repairs/s3_generator_construction/run_s3_generator_construction_v2.py --self",
    "review_2026/repairs/s6_record_grammar_ablation/run_s6_record_grammar_ablation_v3.py --self",
    "review_2026/repairs/f34_exact_factorization/run_exact_factorization.py --self",
    "review_2026/mathematics_audit_20261003/test_gauge_certificate.py",
    "review_2026/mathematics_audit_20261003/test_representation_characters.py",
    "review_2026/mathematics_audit_20261003/test_record_characters.py",
    "review_2026/mathematics_audit_20261003/test_artifact_guards.py",
    "review_2026/build_claims_registry.py --check",
)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--output", type=Path, required=True, help="receipt JSON outside the repository")
    parser.add_argument("--jobs", type=int, default=3)
    args = parser.parse_args()
    if args.jobs < 1:
        parser.error("--jobs must be positive")
    files = subprocess.check_output(
        ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"], cwd=ROOT
    ).decode().split("\0")
    commands = set(CHANGED)
    if args.all:
        registry = json.loads((ROOT / "review_2026/CLAIMS_REGISTRY.json").read_text())
        commands.update(command for row in registry["records"] for command in row["validators"])
        commands.update(str(path.relative_to(ROOT)) + " --self"
                        for path in (ROOT / "open_programs").rglob("run_*.py"))
        commands.add("review_2026/probes/p1_kernel_quotient/run_active_cut_quotient_v3.py --self")
        commands.update(str(path.relative_to(ROOT)) + " --self"
                        for path in (ROOT / "physics_atlas").glob("thread_*/steps/**/run_step*.py"))
    environment = os.environ.copy()
    environment.update(OPENBLAS_NUM_THREADS="1", OMP_NUM_THREADS="1")
    with tempfile.TemporaryDirectory(prefix="sm_qm_gr_math_checks_") as temporary:
        snapshot = Path(temporary) / "snapshot"
        for name in sorted(set(files) - {""}):
            source = ROOT / name
            if source.is_file():
                target = snapshot / name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, target)

        def run(command):
            started = time.monotonic()
            with tempfile.TemporaryDirectory(dir=temporary) as isolated:
                work = Path(isolated) / "repo"
                shutil.copytree(snapshot, work)
                path, *options = command.split()
                source = work / path
                result = subprocess.run([sys.executable, source.name, *options], cwd=source.parent,
                                        capture_output=True, text=True, env=environment)
            receipt = dict(command=command, returncode=result.returncode,
                           seconds=round(time.monotonic() - started, 3),
                           stdout=result.stdout, stderr=result.stderr)
            print(f"{'PASS' if result.returncode == 0 else 'FAIL'} {command}", flush=True)
            return receipt

        with concurrent.futures.ThreadPoolExecutor(max_workers=args.jobs) as pool:
            results = list(pool.map(run, sorted(commands)))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(results, indent=2) + "\n")
    raise SystemExit(any(result["returncode"] for result in results))


if __name__ == "__main__":
    main()
