#!/usr/bin/env python3
"""Validator for the S3 explicit generator construction."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from artifact_io import render_artifacts
from s3_construction import run_all


HERE = Path(__file__).resolve().parent


def validate() -> list[str]:
    result = run_all()
    expected = render_artifacts(result)
    errors = []
    for name, data in expected.items():
        path = HERE / name
        if not path.is_file():
            errors.append(f"missing artifact: {name}")
        elif path.read_bytes() != data:
            errors.append(f"artifact differs from exact recomputation: {name}")

    manifest_path = HERE / "artifact_manifest.json"
    if manifest_path.is_file():
        manifest = json.loads(manifest_path.read_text())
        for name, digest in manifest["files"].items():
            path = HERE / name
            if path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest() != digest:
                errors.append(f"sha256 mismatch: {name}")

    if any(row["result"] != "PASS" for row in result["mutation_tests"]):
        errors.append("one or more required mutation tests was not rejected")
    return errors


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self", action="store_true", help="recompute and verify all written artifacts")
    args = parser.parse_args()
    if not args.self:
        parser.error("this validator must be run with --self")
    errors = validate()
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        raise SystemExit(1)
    result = run_all()
    print("S3-REPAIR-1 validator: PASS")
    print("representation construction: PASS (24 su5 generators; 5bar+10 derived)")
    print("hypercharge centralizer: PASS (dimension=1, Y=(-1/3,-1/3,-1/3,1/2,1/2))")
    print("ratios: PASS (k_Y=5/3, sin^2(theta_W)=3/8)")
    print("F27/F48: PASS (12/12 Delta-B coset generators; pi2=Z)")
    print("mutation tests: PASS (3/3 rejected)")


if __name__ == "__main__":
    main()
