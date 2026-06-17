#!/usr/bin/env python3
"""Validate Step 68 E032 two-shape instantiation artifacts."""

from __future__ import annotations

import csv
import json
import re
import subprocess
import sys
from fractions import Fraction
from pathlib import Path


ARTIFACT_DIR = Path(__file__).resolve().parent
BUILD_SCRIPT = ARTIFACT_DIR / "e032_two_shape_instantiation_step68.py"

REQUIRED_FILES = [
    "step68_results_summary.md",
    "step68_schema.json",
    "content_classification_step68.csv",
    "nonclaim_boundary_step68.md",
    "step68_statement.tex",
    "run_step68.py",
    "mode_b_constraint_ledger.csv",
    "mode_b_target_lineage.csv",
    "mode_b_grammar_manifest.csv",
    "discriminator_step68.csv",
    "anti_circularity_step68.csv",
    "shape_extensions_step68.csv",
    "born_weight_check_step68.csv",
    "base_nonfactorization_reuse_step68.csv",
    "frozen_step66_reuse_step68.csv",
]

OVERCLAIM_PATTERNS = [
    r"\bsolves\s+the\s+measurement\s+problem\b",
    r"\bcollapse\s+is\s+the\s+answer\b",
    r"\bmany-worlds\s+is\s+the\s+answer\b",
    r"\bderives\s+collapse\b",
    r"\bproves\s+many-worlds\b",
    r"\bmeasurement\s+problem\s+solved\b",
    r"\bunconditional\b",
    r"\bframe\s+transfer\b",
]


def fail(message: str) -> None:
    print(f"FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def read_csv(name: str) -> list[dict[str, str]]:
    with (ARTIFACT_DIR / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def boolish(value: object) -> bool:
    return str(value).strip().lower() == "true"


def validate_presence() -> None:
    for name in REQUIRED_FILES:
        if not (ARTIFACT_DIR / name).exists():
            fail(f"missing required artifact {name}")


def validate_schema() -> dict[str, object]:
    schema = json.loads((ARTIFACT_DIR / "step68_schema.json").read_text(encoding="utf-8"))
    expected = {
        "step": 68,
        "orientation": "ModeB_E032_two_shape_instantiation",
        "exit_state": "BOTH_SHAPES_INSTANTIATED_DISCRIMINATOR_CLEAN",
        "verdict": "D_VS_SIGMA_F_DISCRIMINATOR_CONCRETELY_SEPARATES_THE_TWO_SHAPES",
        "shapeA_touches_D": True,
        "shapeA_E_idempotent": False,
        "shapeB_touches_D": False,
        "shapeB_E_idempotent": True,
        "both_reproduce_born_weights": True,
        "discriminator_cleanly_separates": True,
        "shapes_genuinely_distinct": True,
        "picks_a_shape": False,
        "solves_measurement_problem": False,
        "new_physics_claim": False,
        "frame_transfer_certified": False,
        "root_landed": True,
        "base_nonfactorization_witness_reused": True,
    }
    for key, value in expected.items():
        if schema.get(key) != value:
            fail(f"schema field {key!r} expected {value!r}, got {schema.get(key)!r}")
    return schema


def validate_shape_rows() -> None:
    rows = {row["shape_id"]: row for row in read_csv("shape_extensions_step68.csv")}
    for key in ["shape_A_collapse_D_touch", "shape_B_MWI_indexical_Sigma_extension"]:
        if key not in rows:
            fail(f"missing shape row {key}")

    a = rows["shape_A_collapse_D_touch"]
    b = rows["shape_B_MWI_indexical_Sigma_extension"]
    if not boolish(a["touches_D"]):
        fail("Shape A must touch D")
    if boolish(a["touches_Sigma_f_readout_extension"]):
        fail("Shape A should not be a Sigma_f-only readout extension")
    if boolish(a["E_idempotent"]):
        fail("Shape A must be non-idempotent relative to base dephasing")
    if Fraction(a["E_idempotence_error"]) <= 0:
        fail("Shape A idempotence error must be positive")
    if not boolish(a["new_dynamical_parameter"]):
        fail("Shape A must carry a new dynamical parameter")
    if a["single_outcome_kind"] != "global_branch_pruning":
        fail("Shape A must implement global branch pruning")
    if not boolish(a["born_weights_reproduced"]):
        fail("Shape A must reproduce Born weights")

    if boolish(b["touches_D"]):
        fail("Shape B must not touch D")
    if not boolish(b["touches_Sigma_f_readout_extension"]):
        fail("Shape B must enrich the readout outside old Sigma_f")
    if not boolish(b["E_idempotent"]):
        fail("Shape B must preserve idempotent dephasing")
    if Fraction(b["E_idempotence_error"]) != 0:
        fail("Shape B idempotence error must be zero")
    if boolish(b["new_dynamical_parameter"]):
        fail("Shape B must not introduce a new dynamical parameter")
    if b["single_outcome_kind"] != "per_copy_indexical":
        fail("Shape B must be per-copy indexical, not global pruning")
    if not boolish(b["all_branches_persist"]):
        fail("Shape B must preserve all branches")
    if not boolish(b["born_weights_reproduced"]):
        fail("Shape B must reproduce Born weights")


def validate_born_weights() -> None:
    rows = read_csv("born_weight_check_step68.csv")
    expected = {"k0": Fraction(1, 3), "k1": Fraction(2, 3)}
    if len(rows) != len(expected):
        fail("Born-weight check must have two branch rows")
    for row in rows:
        branch = row["branch_id"]
        if branch not in expected:
            fail(f"unexpected branch {branch}")
        values = [
            Fraction(row["base_born_weight"]),
            Fraction(row["shapeA_collapse_probability"]),
            Fraction(row["shapeB_self_locating_measure"]),
        ]
        if values != [expected[branch], expected[branch], expected[branch]]:
            fail(f"Born-weight mismatch for {branch}: {values}")
        if not (boolish(row["shapeA_matches_base"]) and boolish(row["shapeB_matches_base"])):
            fail(f"Born match flags failed for {branch}")


def validate_discriminator() -> None:
    rows = read_csv("discriminator_step68.csv")
    by_shape = {row["shape_id"]: row for row in rows if row["shape_id"]}
    if by_shape["shape_A_collapse_D_touch"]["discriminator_classification"] != "D_touch_shape_A":
        fail("Shape A discriminator classification is not D_touch_shape_A")
    if by_shape["shape_B_MWI_indexical_Sigma_extension"]["discriminator_classification"] != "Sigma_f_only_shape_B":
        fail("Shape B discriminator classification is not Sigma_f_only_shape_B")
    if "falsifier" not in by_shape:
        fail("missing falsifier row")


def validate_anti_circularity() -> None:
    rows = read_csv("anti_circularity_step68.csv")
    required = {
        "both_shapes_reproduce_born_weights",
        "shape_A_selection_from_D_not_readout_relabel",
        "shape_B_no_hidden_D_touch",
        "shapes_genuinely_distinct",
        "base_nonfactorization_still_holds",
        "no_side_picked",
    }
    seen = {row["gate"]: row for row in rows}
    missing = required - set(seen)
    if missing:
        fail(f"missing anti-circularity gates: {sorted(missing)}")
    for gate in required:
        if not boolish(seen[gate]["passes"]):
            fail(f"anti-circularity gate failed: {gate}")


def validate_frozen_reuse_and_base_witness() -> None:
    frozen = read_csv("frozen_step66_reuse_step68.csv")
    if not frozen or frozen[0]["status"] != "imported_verbatim":
        fail("Step 66 reuse must be imported_verbatim")
    source = BUILD_SCRIPT.read_text(encoding="utf-8")
    if "STEP66_BUILD" not in source or "load_module" not in source:
        fail("build script does not visibly import Step 66 machinery")
    witness = read_csv("base_nonfactorization_reuse_step68.csv")
    if not witness:
        fail("missing base nonfactorization witness")
    row = witness[0]
    if row["L0_difference"] != "1" or row["D0_difference"] != "0":
        fail("base witness should share Sigma_f and split by selection predicate")


def validate_content_classification() -> None:
    grades = {row["artifact"]: row["grade"] for row in read_csv("content_classification_step68.csv")}
    if grades.get("step68_statement.tex") != "finite-carrier-diagnostic":
        fail("step68_statement.tex must be finite-carrier-diagnostic")
    if grades.get("discriminator_step68.csv") != "finite-carrier-diagnostic":
        fail("discriminator_step68.csv must be finite-carrier-diagnostic")
    for artifact in [
        "step68_results_summary.md",
        "nonclaim_boundary_step68.md",
        "mode_b_constraint_ledger.csv",
        "mode_b_target_lineage.csv",
        "mode_b_grammar_manifest.csv",
        "run_step68.py",
    ]:
        if grades.get(artifact) != "organizational":
            fail(f"{artifact} must be organizational")


def validate_overclaims(schema: dict[str, object]) -> None:
    text = "\n".join(
        (ARTIFACT_DIR / name).read_text(encoding="utf-8")
        for name in ["step68_results_summary.md", "nonclaim_boundary_step68.md", "step68_statement.tex"]
    )
    for pattern in OVERCLAIM_PATTERNS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            fail(f"overclaim phrase matched: {pattern}")
    for key in ["picks_a_shape", "solves_measurement_problem", "new_physics_claim", "frame_transfer_certified"]:
        if boolish(schema.get(key)):
            fail(f"schema overclaim flag is true: {key}")


def run_chain() -> None:
    subprocess.run([sys.executable, str(BUILD_SCRIPT)], cwd=str(ARTIFACT_DIR), check=True)


def main(argv: list[str]) -> int:
    if len(argv) != 2 or argv[1] not in {"--self", "--chain"}:
        print("usage: run_step68.py --self|--chain", file=sys.stderr)
        return 2
    if argv[1] == "--chain":
        run_chain()
    validate_presence()
    schema = validate_schema()
    validate_shape_rows()
    validate_born_weights()
    validate_discriminator()
    validate_anti_circularity()
    validate_frozen_reuse_and_base_witness()
    validate_content_classification()
    validate_overclaims(schema)
    print(f"PASS step68 {argv[1]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
