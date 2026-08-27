#!/usr/bin/env python3
"""Validate the authoritative claims registry and render its human view."""

from __future__ import annotations

import argparse
import copy
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent
REGISTRY_PATH = HERE / "CLAIMS_REGISTRY.json"
VIEW_PATH = HERE / "CLAIMS_REGISTRY.md"
STATUSES = {"CERTIFIED", "RETYPED", "WITHDRAWN", "OPEN"}
EVIDENCE_TYPES = {
    "COMPUTED",
    "PROVED_BY_DEFINITION",
    "EXTERNAL_REPRODUCED",
    "STIPULATED",
}
TOP_LEVEL_KEYS = {"schema_version", "generated_view", "records"}
REQUIRED_RECORD_KEYS = {
    "id",
    "claim_text",
    "status",
    "evidence_type",
    "controlling_source",
    "superseded_wordings",
    "validators",
}
OPTIONAL_RECORD_KEYS = {"provenance"}
SOURCE_KEYS = {"path", "anchor"}
SUPERSEDED_KEYS = {"path", "quote", "already_edited"}
EXPECTED_RECORD_IDS = (
    "paper_foundational_strength_headline",
    "paper_three_forcing_headlines",
    "paper_external_review_settled",
    "paper_su5_ratios",
    "paper_five_xy_roles",
    "paper_carrier_exclusion",
    "paper_gauge_structure_selection",
    "paper_window_closure",
    "paper_content_blindness",
    "paper_generation_blindness",
    "paper_mass_matrix_rank",
    "paper_record_stability_grounding",
    "paper_lstar_layer",
    "paper_budgetedrole_f47",
    "paper_route_noncommutation",
    "paper_qg_directed_nogo",
    "paper_access_uniqueness",
    "paper_fork_over_ladder",
    "paper_common_carrier_grounding",
    "paper_area_shadow_price_identity",
    "paper_linearized_einstein_response",
    "paper_one_born_area_ledger",
    "paper_cosmological_background_boundary",
    "paper_strict_extension_discriminator",
    "paper_g1_lambda_adjudication",
    "paper_g2_singularity_boundary",
    "paper_prediction_p1",
    "paper_prediction_p2",
    "paper_prediction_p3",
    "paper_method_anti_contamination",
    "paper_one_grammar",
    "paper_support_surfaces",
    "prog2_step6_controlling_outcome",
    "prog3_step3_controlling_floor",
    "prog3_symmetric_closure_open",
    "s1v3_charge_normalization_census",
    "s1v3_branch_typed_selection",
    "s3v2_su5_ratios",
    "s3v2_product_parent_control",
    "q5_exact_lp_identity",
    "q5_linearized_response",
    "q5_shared_mmi_class",
)
EXPECTED_STATUS_COUNTS = {
    "CERTIFIED": 7,
    "OPEN": 3,
    "RETYPED": 23,
    "WITHDRAWN": 9,
}


def normalized(text: str) -> str:
    lines = [re.sub(r"^\s*>\s?", "", line) for line in text.splitlines()]
    return " ".join(" ".join(lines).split())


def repo_path(relative: str) -> Path:
    candidate = (REPO_ROOT / relative).resolve()
    if REPO_ROOT.resolve() not in candidate.parents and candidate != REPO_ROOT.resolve():
        raise ValueError(f"path escapes repository: {relative}")
    return candidate


def source_contains(path: Path, quote: str) -> bool:
    return normalized(quote) in normalized(path.read_text(encoding="utf-8"))


def rendered_heading_slug(heading: str) -> str:
    text = re.sub(r"<[^>]+>", "", heading)
    text = text.replace("`", "").strip().lower()
    text = re.sub(r"[^\w\- ]", "", text)
    return re.sub(r"\s", "-", text)


def rendered_anchors(path: Path) -> set[str]:
    text = path.read_text(encoding="utf-8")
    anchors = set(
        re.findall(r"<a\s+[^>]*(?:id|name)=[\"']([^\"']+)[\"'][^>]*>", text, re.I)
    )
    slug_counts: Counter[str] = Counter()
    for line in text.splitlines():
        match = re.match(r"^#{1,6}\s+(.+?)\s*#*\s*$", line)
        if not match:
            continue
        base = rendered_heading_slug(match.group(1))
        if not base:
            continue
        count = slug_counts[base]
        anchors.add(base if count == 0 else f"{base}-{count}")
        slug_counts[base] += 1
    return anchors


def validate_registry(registry: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if set(registry) != TOP_LEVEL_KEYS:
        errors.append(f"top-level keys mismatch: {sorted(registry)}")
    if registry.get("schema_version") != "1.0":
        errors.append("schema_version must be 1.0")
    if registry.get("generated_view") != "review_2026/CLAIMS_REGISTRY.md":
        errors.append("generated_view path mismatch")
    records = registry.get("records")
    if not isinstance(records, list) or not records:
        return errors + ["records must be a nonempty list"]
    actual_ids = [record.get("id") for record in records if isinstance(record, dict)]
    if actual_ids != list(EXPECTED_RECORD_IDS):
        errors.append("reviewed ID inventory mismatch")
    actual_status_counts = Counter(
        record.get("status") for record in records if isinstance(record, dict)
    )
    if dict(sorted(actual_status_counts.items())) != EXPECTED_STATUS_COUNTS:
        errors.append(
            "pinned status census mismatch: "
            f"expected={EXPECTED_STATUS_COUNTS} actual={dict(sorted(actual_status_counts.items()))}"
        )
    ids: set[str] = set()
    for index, record in enumerate(records):
        label = f"record[{index}]"
        if not isinstance(record, dict):
            errors.append(f"{label}: record must be an object")
            continue
        keys = set(record)
        if not REQUIRED_RECORD_KEYS.issubset(keys) or not keys.issubset(
            REQUIRED_RECORD_KEYS | OPTIONAL_RECORD_KEYS
        ):
            errors.append(f"{label}: record keys mismatch")
            continue
        record_id = record["id"]
        if not isinstance(record_id, str) or not re.fullmatch(r"[a-z0-9_]+", record_id):
            errors.append(f"{label}: invalid id {record_id!r}")
        elif record_id in ids:
            errors.append(f"{label}: duplicate id {record_id}")
        ids.add(record_id)
        if record["status"] not in STATUSES:
            errors.append(f"{record_id}: invalid status {record['status']}")
        if record["evidence_type"] not in EVIDENCE_TYPES:
            errors.append(f"{record_id}: invalid evidence_type {record['evidence_type']}")
        if not isinstance(record["claim_text"], str) or not record["claim_text"].strip():
            errors.append(f"{record_id}: empty claim_text")
        source = record["controlling_source"]
        if not isinstance(source, dict) or set(source) != SOURCE_KEYS:
            errors.append(f"{record_id}: controlling_source keys mismatch")
        else:
            path = repo_path(source["path"])
            if not path.is_file():
                errors.append(f"{record_id}: controlling source missing: {source['path']}")
            elif not source_contains(path, record["claim_text"]):
                errors.append(
                    f"{record_id}: claim_text is not verbatim in {source['path']}"
                )
            if not isinstance(source["anchor"], str) or not source["anchor"].strip():
                errors.append(f"{record_id}: empty source anchor")
            elif path.is_file() and source["anchor"] not in rendered_anchors(path):
                errors.append(
                    f"{record_id}: dangling source anchor "
                    f"{source['path']}#{source['anchor']}"
                )
        provenance = record.get("provenance")
        if provenance is not None and (not isinstance(provenance, str) or not provenance.strip()):
            errors.append(f"{record_id}: provenance must be a nonempty string")
        superseded = record["superseded_wordings"]
        if not isinstance(superseded, list):
            errors.append(f"{record_id}: superseded_wordings must be a list")
        else:
            for old_index, old in enumerate(superseded):
                old_label = f"{record_id}: superseded[{old_index}]"
                if not isinstance(old, dict) or set(old) != SUPERSEDED_KEYS:
                    errors.append(f"{old_label}: keys mismatch")
                    continue
                old_path = repo_path(old["path"])
                if not old_path.is_file():
                    errors.append(f"{old_label}: source missing: {old['path']}")
                elif not old["already_edited"] and not source_contains(old_path, old["quote"]):
                    errors.append(f"{old_label}: retired quote no longer present and not marked edited")
                if not isinstance(old["quote"], str) or not old["quote"]:
                    errors.append(f"{old_label}: empty quote")
                if not isinstance(old["already_edited"], bool):
                    errors.append(f"{old_label}: already_edited must be Boolean")
        validators = record["validators"]
        if not isinstance(validators, list):
            errors.append(f"{record_id}: validators must be a list")
        else:
            for command in validators:
                if not isinstance(command, str) or not command.endswith(" --self"):
                    errors.append(f"{record_id}: invalid validator command {command!r}")
                    continue
                validator_path = repo_path(command[: -len(" --self")])
                if not validator_path.is_file():
                    errors.append(f"{record_id}: validator missing: {command}")
    return errors


def run_force_controls(registry: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    deleted = copy.deepcopy(registry)
    del deleted["records"][-1]
    deleted_errors = validate_registry(deleted)
    if "reviewed ID inventory mismatch" not in deleted_errors:
        errors.append("deleted-record control was not rejected by the ID inventory pin")
    else:
        print("CONTROL DELETED-RECORD PASS: reviewed ID inventory mismatch rejected")

    status_mutation = copy.deepcopy(registry)
    status_mutation["records"][0]["status"] = "CERTIFIED"
    status_errors = validate_registry(status_mutation)
    if not any(error.startswith("pinned status census mismatch") for error in status_errors):
        errors.append("status-mutation control was not rejected by the census pin")
    else:
        print("CONTROL STATUS-MUTATION PASS: pinned status census mismatch rejected")

    dangling_anchor = copy.deepcopy(registry)
    dangling_anchor["records"][0]["controlling_source"]["anchor"] = "missing-anchor-control"
    anchor_errors = validate_registry(dangling_anchor)
    if not any("dangling source anchor" in error for error in anchor_errors):
        errors.append("dangling-anchor control was not rejected")
    else:
        print("CONTROL DANGLING-ANCHOR PASS: unresolved source anchor rejected")
    return errors


def markdown(registry: dict[str, Any]) -> str:
    records = registry["records"]
    counts = Counter(record["status"] for record in records)
    lines = [
        "# Authoritative claims registry",
        "",
        "Generated from `review_2026/CLAIMS_REGISTRY.json`; edit the JSON and rerun",
        "`python3 review_2026/build_claims_registry.py` rather than editing this view.",
        "",
        "## Status summary",
        "",
        "| status | count |",
        "|---|---:|",
    ]
    for status in sorted(STATUSES):
        lines.append(f"| {status} | {counts[status]} |")
    lines.extend(
        [
            f"| **TOTAL** | **{len(records)}** |",
            "",
            "## Registry",
            "",
            "| id | status | evidence | controlling source | validators |",
            "|---|---|---|---|---|",
        ]
    )
    for record in records:
        source = record["controlling_source"]
        validators = "<br>".join(f"`{value}`" for value in record["validators"]) or "—"
        lines.append(
            f"| `{record['id']}` | {record['status']} | {record['evidence_type']} "
            f"| `{source['path']}#{source['anchor']}` | {validators} |"
        )
    lines.extend(["", "## Controlling wordings", ""])
    for record in records:
        source = record["controlling_source"]
        lines.extend(
            [
                f"### `{record['id']}`",
                "",
                f"Status: **{record['status']}**. Evidence: **{record['evidence_type']}**. "
                f"Source: `{source['path']}#{source['anchor']}`.",
                "",
            ]
        )
        lines.extend(f"> {line}" if line else ">" for line in record["claim_text"].splitlines())
        if record.get("provenance"):
            lines.extend(["", f"Provenance: {record['provenance']}"])
        lines.extend(["", "Superseded wordings:"])
        if record["superseded_wordings"]:
            for old in record["superseded_wordings"]:
                marker = "already edited from source" if old["already_edited"] else "retained historical quote"
                lines.append(f"- `{old['path']}` — “{old['quote']}” ({marker})")
        else:
            lines.append("- None recorded.")
        lines.append("")
    return "\n".join(lines)


def load_registry() -> dict[str, Any]:
    try:
        value = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise RuntimeError(f"cannot load {REGISTRY_PATH}: {error}") from error
    if not isinstance(value, dict):
        raise RuntimeError("registry root must be an object")
    return value


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="validate and byte-check the generated view")
    args = parser.parse_args()
    registry = load_registry()
    errors = validate_registry(registry)
    if not errors:
        errors.extend(run_force_controls(registry))
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    rendered = markdown(registry) + "\n"
    if args.check:
        if not VIEW_PATH.is_file() or VIEW_PATH.read_text(encoding="utf-8") != rendered:
            print("FAIL: CLAIMS_REGISTRY.md is stale")
            return 1
        mode = "check"
    else:
        VIEW_PATH.write_text(rendered, encoding="utf-8")
        mode = "write"
    counts = Counter(record["status"] for record in registry["records"])
    count_text = ",".join(f"{status}:{counts[status]}" for status in sorted(STATUSES))
    print(
        f"build_claims_registry.py: PASS: records={len(registry['records'])} "
        f"statuses={count_text} mode={mode}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
