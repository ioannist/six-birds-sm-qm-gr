#!/usr/bin/env python3
"""Write S3 construction artifacts from the pure computation."""

from pathlib import Path

from artifact_io import render_artifacts
from s3_construction import run_all


HERE = Path(__file__).resolve().parent


def main() -> None:
    result = run_all()
    rendered = render_artifacts(result)
    for name, data in rendered.items():
        (HERE / name).write_bytes(data)
    print(f"S3-REPAIR-1 build: PASS ({len(rendered)} artifacts)")


if __name__ == "__main__":
    main()
