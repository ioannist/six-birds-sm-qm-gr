#!/usr/bin/env python3
"""Validate Step 3 artifacts for the asymptotic-safety P3 audit."""

from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path


ARTIFACT_DIR = Path(__file__).resolve().parent
THREAD_DIR = ARTIFACT_DIR.parents[1]
LINEAGE = THREAD_DIR / "mode_b_target_lineage.csv"


REQUIRED_FILES = [
    "step3_results_summary.md",
    "step3_schema.json",
    "content_classification_step3.csv",
    "nonclaim_boundary_step3.md",
    "step3_structural_statement.tex",
    "simulate_step3_asymptotic_safety_xi.py",
    "simulation_output_step3.json",
    "simulation_output_step3.txt",
    "xi_diagnostic_step3.csv",
    "candidate_imports_step3.csv",
    "recognition_audit_step3.csv",
    "no_smuggling_gates_step3.csv",
]


def forbidden_phrases() -> list[str]:
    return [
        "proves " + "quantum gravity",
        "solves " + "quantum gravity",
        "derives " + "the proton mass",
        "closes " + "QM-GR unconditionally",
        "discovers " + "a new physical law",
        "predicts " + "a new constant",
        "cross-layer " + "DERIVATION",
        "shadow-to-source " + "promotion",
    ]


FORBIDDEN_REGEXES = [
    re.compile(r"\bderive[sd]?\s+(?:a\s+|the\s+)?(?:new\s+)?(?:[A-Za-z-]+\s+){0,3}(?:constant|mass)\b", re.I),
    re.compile(r"\bE2\s*(?:->|to)\s*E1\b", re.I),
    re.compile(r"\bE3\s*(?:->|to)\s*E2\b", re.I),
]


def fail(message: str) -> None:
    print(f"VALIDATION FAILED: {message}", file=sys.stderr)
    sys.exit(1)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def check_required_files() -> None:
    for name in REQUIRED_FILES:
        path = ARTIFACT_DIR / name
        if not path.exists():
            fail(f"missing artifact {name}")
        if path.stat().st_size == 0:
            fail(f"empty artifact {name}")
    if not LINEAGE.exists():
        fail("missing mode_b_target_lineage.csv")


def check_schema() -> None:
    schema = json.loads((ARTIFACT_DIR / "step3_schema.json").read_text(encoding="utf-8"))
    for key in ["step", "orientation", "active_residual", "carrier", "candidate_move", "final_verdict", "track_fields"]:
        if key not in schema:
            fail(f"schema missing {key}")
    if schema["step"] != 3:
        fail("schema step is not 3")
    verdict = schema["final_verdict"]
    if verdict.get("type") not in {"P3_only_E2_conditional_recognition", "typed_obstruction", "smuggling_reject"}:
        fail("schema final_verdict.type not allowed")
    if verdict.get("root_landed") is not False:
        fail("schema must keep root_landed false")
    if verdict.get("p3_only") is not True:
        fail("schema missing p3_only flag")
    xi = schema["track_fields"].get("xi_results", {})
    p3 = xi.get("as_p3_route_mismatch_normalized", {})
    amp = xi.get("as_amplitude_geometry_normalized", {})
    area = xi.get("as_area_shadow_price_normalized", {})
    if float(p3.get("level_2", -1)) != 0.0 or float(p3.get("level_4", -1)) != 0.0:
        fail("schema P3 residuals must be 0.0")
    if float(amp.get("level_2", -1)) != 1.0 or float(amp.get("level_4", -1)) != 1.0:
        fail("schema amplitude residuals must be 1.0")
    if float(area.get("level_2", -1)) != 1.0 or float(area.get("level_4", -1)) != 1.0:
        fail("schema area residuals must be 1.0")


def check_gate_statuses() -> None:
    rows = read_csv(ARTIFACT_DIR / "no_smuggling_gates_step3.csv")
    if len(rows) < 6:
        fail("no_smuggling_gates_step3.csv has fewer than six gates")
    expected = {
        "G1_named_source_declared",
        "G2_target_lineage_non_equivalence",
        "G3_typed_carrier_and_lens",
        "G4_no_silent_status_upgrade",
        "G5_scope_complementarity_recorded",
        "G6_no_answer_row_overread",
    }
    gate_names = {row.get("gate", "") for row in rows}
    missing = expected - gate_names
    if missing:
        fail(f"missing gate rows: {sorted(missing)}")
    for row in rows:
        if not row.get("status"):
            fail("gate row missing status")


def check_simulation_output() -> None:
    payload = json.loads((ARTIFACT_DIR / "simulation_output_step3.json").read_text(encoding="utf-8"))
    stability = payload.get("refinement_stability", {})
    for key in ["as_p3_absolute_delta", "as_amplitude_absolute_delta", "as_area_absolute_delta"]:
        if abs(float(stability.get(key, -1))) > 1e-12:
            fail(f"refinement stability failed for {key}")
    for result in payload.get("results", []):
        p3 = float(result["as_on_p3_route_mismatch"]["normalized_trace"])
        if abs(p3) > 1e-12:
            fail("AS P3 residual is not numerically zero")
        amp = float(result["as_on_amplitude_geometry"]["normalized_trace"])
        if abs(amp - 1.0) > 1e-12:
            fail("AS amplitude residual is not 1.0")
        area = float(result["as_on_area_shadow_price"]["normalized_trace"])
        if abs(area - 1.0) > 1e-12:
            fail("AS area residual is not 1.0")
        checks = result.get("no_overread_check", {})
        if checks.get("amplitude_geometry_used_in_as_native_lens") is not False:
            fail("amplitude overread check failed")
        if checks.get("boundary_entanglement_used_in_as_native_lens") is not False:
            fail("boundary entanglement overread check failed")


def check_lineage() -> None:
    text = LINEAGE.read_text(encoding="utf-8")
    for residual in ["R_child_E018_AS_P3_fixed_point", "R_child_E018_after_HED_LQG_AS_coupled_joint_gap"]:
        if residual not in text:
            fail(f"lineage missing {residual}")


def check_forbidden_text() -> None:
    scan_paths = list(ARTIFACT_DIR.glob("*")) + [LINEAGE]
    phrases = forbidden_phrases()
    for path in scan_paths:
        if path.name == "run_step3.py" or path.is_dir():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        lower = text.lower()
        for phrase in phrases:
            if phrase.lower() in lower:
                fail(f"forbidden phrase in {path.name}: {phrase}")
        for regex in FORBIDDEN_REGEXES:
            if regex.search(text):
                fail(f"forbidden overclaim pattern in {path.name}: {regex.pattern}")


def main() -> None:
    check_required_files()
    check_schema()
    check_gate_statuses()
    check_simulation_output()
    check_lineage()
    check_forbidden_text()
    print("Step 3 validation passed.")


if __name__ == "__main__":
    main()
