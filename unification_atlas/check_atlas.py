#!/usr/bin/env python3
"""Parse every atlas JSON file and verify candidate/card coverage."""

from __future__ import annotations

import json
import re
from pathlib import Path


ATLAS_DIR = Path(__file__).resolve().parent
ID_PATTERN = re.compile(r"U\d{3}")


def fail(message: str) -> None:
    raise SystemExit(f"check_atlas.py: FAIL: {message}")


def main() -> None:
    parsed = {}
    for path in sorted(ATLAS_DIR.rglob("*.json")):
        try:
            parsed[path] = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            fail(f"cannot parse {path.relative_to(ATLAS_DIR)}: {exc}")

    candidates_payload = parsed.get(ATLAS_DIR / "unif_candidates.json")
    if not isinstance(candidates_payload, dict) or not isinstance(candidates_payload.get("candidates"), list):
        fail("unif_candidates.json has no candidates list")
    candidate_ids = [row.get("id") for row in candidates_payload["candidates"]]
    if any(not isinstance(value, str) or ID_PATTERN.fullmatch(value) is None for value in candidate_ids):
        fail("candidate ID does not match Uddd")
    if len(candidate_ids) != len(set(candidate_ids)):
        fail("candidate IDs are not unique")

    card_ids = []
    for path in sorted((ATLAS_DIR / "cards").glob("*.json")):
        if ID_PATTERN.fullmatch(path.stem) is None:
            fail(f"malformed card filename {path.name}")
        payload = parsed[path]
        if not isinstance(payload, dict) or payload.get("id") != path.stem:
            fail(f"card ID mismatch in {path.name}")
        card_ids.append(path.stem)
    unexpected = sorted(set(card_ids) - set(candidate_ids))
    if unexpected:
        fail(f"cards without candidates: {unexpected}")

    coverage = parsed.get(ATLAS_DIR / "card_coverage.json")
    if not isinstance(coverage, dict):
        fail("missing card_coverage.json")
    missing = sorted(set(candidate_ids) - set(card_ids))
    checks = {
        "candidate_ids": candidate_ids,
        "cards_present": sorted(card_ids),
        "cards_missing": missing,
    }
    for field, actual in checks.items():
        if coverage.get(field) != actual:
            fail(f"coverage field {field} is stale")
    if coverage.get("candidate_source") != "unif_candidates.json":
        fail("coverage candidate_source is stale")
    if coverage.get("card_directory") != "cards":
        fail("coverage card_directory is stale")
    if coverage.get("missing_status") != "declared_candidate_no_card_yet":
        fail("missing-card status is not typed")
    if set(card_ids) | set(missing) != set(candidate_ids) or set(card_ids) & set(missing):
        fail("coverage does not partition the candidate IDs")

    print(
        "check_atlas.py: PASS: "
        f"json_files={len(parsed)} candidates={len(candidate_ids)} "
        f"cards={len(card_ids)} missing={len(missing)} coverage={len(card_ids) + len(missing)}"
    )


if __name__ == "__main__":
    main()
