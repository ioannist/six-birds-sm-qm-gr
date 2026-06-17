#!/usr/bin/env python3
"""Validate Step 43 entanglement first-law / area-energy artifacts."""

from __future__ import annotations

import csv
import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path


ARTIFACT_DIR = Path(__file__).resolve().parent
THREAD_DIR = ARTIFACT_DIR.parents[1]
BUILD_SCRIPT = ARTIFACT_DIR / "entanglement_first_law_area_energy_step43.py"
TOL = 1e-9

REQUIRED_FILES = [
    "entanglement_first_law_area_energy_step43.py",
    "step43_results_summary.md",
    "step43_schema.json",
    "content_classification_step43.csv",
    "nonclaim_boundary_step43.md",
    "step43_first_law_area_energy_statement.tex",
    "density_matrices_step43.json",
    "first_law_rows_step43.csv",
    "relative_entropy_step43.csv",
    "area_energy_relation_step43.csv",
    "generated_vs_input_step43.csv",
    "anti_circularity_step43.csv",
    "six_gate_audit_step43.csv",
    "anti_hardcode_step43.csv",
    "mode_b_constraint_ledger.csv",
    "mode_b_target_lineage.csv",
    "mode_b_grammar_manifest.csv",
    "run_step43.py",
]

OVERCLAIM_PATTERNS = [
    r"derives\s+1/4G",
    r"derives\s+Newton\s+G",
    r"proves\s+quantum\s+gravity",
    r"solves\s+quantum\s+gravity",
    r"derives\s+the\s+Einstein\s+equation\s+unconditionally",
    r"closes\s+E018",
    r"unconditional\s+new[- ]physics",
]


def fail(message: str) -> None:
    print(f"run_step43.py: FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def as_bool(value: object) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def read_csv(name: str) -> list[dict[str, str]]:
    with (ARTIFACT_DIR / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def load_builder():
    spec = importlib.util.spec_from_file_location("step43_builder", BUILD_SCRIPT)
    if spec is None or spec.loader is None:
        fail("could not import build script")
    module = importlib.util.module_from_spec(spec)
    sys.modules["step43_builder"] = module
    spec.loader.exec_module(module)
    return module


def validate_presence() -> None:
    missing = [name for name in REQUIRED_FILES if not (ARTIFACT_DIR / name).exists()]
    if missing:
        fail(f"missing required artifacts: {missing}")


def validate_schema() -> dict[str, object]:
    schema = json.loads((ARTIFACT_DIR / "step43_schema.json").read_text(encoding="utf-8"))
    expected = {
        "step": 43,
        "orientation": "ModeB_E018_entanglement_first_law_area_energy",
        "verdict": "FIRST_LAW_AND_AREA_ENERGY_DERIVED",
        "new_physics_claim": False,
        "root_landed": False,
        "frame_transfer_certified": False,
        "other_law_landing_legs_attempted": False,
        "full_continuum_einstein_tensor_derived": False,
    }
    for key, value in expected.items():
        if schema.get(key) != value:
            fail(f"schema field {key!r} expected {value!r}, got {schema.get(key)!r}")
    if abs(float(schema["first_law_first_order_residual"])) > TOL:
        fail("first-law first-order residual is too large")
    if float(schema["relative_entropy_second_order"]) <= 1e-9:
        fail("relative entropy second-order witness is not strictly positive")
    if float(schema["large_perturbation_deviation"]) <= float(schema["relative_entropy_second_order"]):
        fail("large perturbation does not show larger nonlinear deviation")
    if not str(schema["RT_coefficient_source"]).startswith("steps/"):
        fail("RT coefficient source is not thread-root-relative")
    if not (THREAD_DIR / str(schema["RT_coefficient_source"])).exists():
        fail("RT coefficient source artifact is missing")
    return schema


def validate_first_law_and_recompute(schema: dict[str, object]) -> None:
    rows = {row["quantity"]: row for row in read_csv("first_law_rows_step43.csv")}
    for key in ["delta_S_from_entropy_path", "delta_H_mod_from_trace_path", "first_order_residual"]:
        if key not in rows:
            fail(f"missing first-law quantity {key}")
    if abs(float(rows["delta_S_from_entropy_path"]["value"]) - float(rows["delta_H_mod_from_trace_path"]["value"])) > TOL:
        fail("delta S and delta H_mod do not agree to first order")
    if rows["delta_S_from_entropy_path"]["code_path"] == rows["delta_H_mod_from_trace_path"]["code_path"]:
        fail("delta S and delta H_mod are not marked as separate code paths")

    builder = load_builder()
    recomputed = builder.build()
    if abs(float(schema["delta_S"]) - recomputed["first_summary"]["delta_S"]) > TOL:
        fail("schema delta_S does not match recomputed value")
    if abs(float(schema["delta_H_mod"]) - recomputed["first_summary"]["delta_H_mod"]) > TOL:
        fail("schema delta_H_mod does not match recomputed value")
    if abs(float(schema["RT_coefficient_used"]) - float(recomputed["coefficient_info"]["coefficient"])) > TOL:
        fail("schema RT coefficient does not match recomputed prior-artifact coefficient")


def validate_relative_entropy_and_can_fail() -> None:
    rows = read_csv("relative_entropy_step43.csv")
    if len(rows) < 4:
        fail("relative-entropy table lacks a perturbation sweep")
    deviations = [abs(float(row["deviation_entropy_minus_linear"])) for row in rows]
    rels = [float(row["relative_entropy"]) for row in rows]
    if not all(value > 0.0 for value in rels):
        fail("relative entropy is not positive on every finite perturbation row")
    if rels[1] <= 1e-9:
        fail("second-order relative entropy witness is not above threshold")
    if not all(as_bool(row["deviation_matches_minus_relative_entropy"]) for row in rows):
        fail("relative entropy does not match minus the finite-t deviation")
    if not (deviations[0] < deviations[1] < deviations[2] < deviations[-2] < deviations[-1]):
        fail(f"large-perturbation can-fail deviation does not grow: {deviations}")


def validate_area_energy_and_gates() -> None:
    area_rows = read_csv("area_energy_relation_step43.csv")
    if not area_rows:
        fail("area-energy relation table is empty")
    coeff = next((row for row in area_rows if row["item"] == "RT_coefficient_area_per_entropy"), None)
    if coeff is None:
        fail("missing RT coefficient row")
    if not coeff["source"].startswith("steps/"):
        fail("RT coefficient row source is not thread-root-relative")
    if not (THREAD_DIR / coeff["source"]).exists():
        fail("RT coefficient row source artifact missing")
    if abs(float(coeff["value"]) - 1.0) > TOL:
        fail("unexpected finite entropy-unit RT coefficient")
    if not any(row["item"] == "linearized_area_energy_relation" and "delta_H_mod" in row["value"] for row in area_rows):
        fail("missing linearized area-energy relation row")

    for row in read_csv("anti_circularity_step43.csv"):
        if not as_bool(row["passes"]):
            fail(f"anti-circularity gate failed: {row['gate']}")
    for row in read_csv("six_gate_audit_step43.csv"):
        if not as_bool(row["passes"]):
            fail(f"six-gate audit failed: {row['gate']}")
    for row in read_csv("anti_hardcode_step43.csv"):
        if not as_bool(row["passes"]):
            fail(f"anti-hardcode gate failed: {row['check']}")


def validate_density_and_paths() -> None:
    density = json.loads((ARTIFACT_DIR / "density_matrices_step43.json").read_text(encoding="utf-8"))
    if abs(float(density["trace_delta_rho"])) > 1e-12:
        fail("delta_rho is not traceless")
    if len(density["rho0"]) != 4 or len(density["delta_rho"]) != 4:
        fail("density matrices have unexpected dimension")

    rows = read_csv("content_classification_step43.csv")
    if not rows:
        fail("content classification is empty")
    for row in rows:
        sources = [source.strip() for source in row["source_artifacts"].split(";") if source.strip()]
        if not sources:
            fail(f"classification row lacks source path: {row}")
        for source in sources:
            if source.startswith("/"):
                fail(f"source path is absolute: {source}")
            if not source.startswith("steps/"):
                fail(f"source path is not thread-root-relative: {source}")
            if not (THREAD_DIR / source).exists():
                fail(f"source path does not exist: {source}")
    manifest = (ARTIFACT_DIR / "mode_b_grammar_manifest.csv").read_text(encoding="utf-8")
    if "G_E018_FirstLawAreaEnergy_v1" not in manifest:
        fail("grammar manifest missing G_E018_FirstLawAreaEnergy_v1")
    if "continuum/dynamical-geometry carrier" not in manifest:
        fail("grammar manifest missing next continuum/dynamical-geometry frontier")
    constraints = (ARTIFACT_DIR / "mode_b_constraint_ledger.csv").read_text(encoding="utf-8")
    if "C_STEP43_FIRST_LAW_LEADING_ORDER_NOT_IDENTITY" not in constraints:
        fail("constraint ledger missing first-law-not-identity constraint")


def validate_hardcode_source() -> None:
    source = BUILD_SCRIPT.read_text(encoding="utf-8")
    for forbidden in ["0" + ".25", "1" + "/4G", "NEWTON" + "_G", "EINSTEIN" + "_CONSTANT"]:
        if forbidden in source:
            fail(f"forbidden hardcoded selector literal in build source: {forbidden}")
    for token in ["central_difference_entropy", "-Tr(delta_rho log rho0)", "relative_entropy(rho_t, rho0)", "STEP41_SIM"]:
        if token not in source:
            fail(f"build source lacks required computation token: {token}")


def validate_overclaims() -> None:
    text = "\n".join(
        (ARTIFACT_DIR / name).read_text(encoding="utf-8")
        for name in [
            "step43_results_summary.md",
            "nonclaim_boundary_step43.md",
            "step43_first_law_area_energy_statement.tex",
            "mode_b_target_lineage.csv",
            "mode_b_grammar_manifest.csv",
        ]
    )
    for pattern in OVERCLAIM_PATTERNS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            fail(f"forbidden overclaim phrase: {pattern}")


def run_chain() -> None:
    subprocess.run([sys.executable, str(BUILD_SCRIPT)], cwd=str(ARTIFACT_DIR), check=True)


def main(argv: list[str]) -> int:
    if len(argv) != 2 or argv[1] not in {"--self", "--chain"}:
        print("usage: run_step43.py --self|--chain", file=sys.stderr)
        return 2
    if argv[1] == "--chain":
        run_chain()
    validate_presence()
    schema = validate_schema()
    validate_first_law_and_recompute(schema)
    validate_relative_entropy_and_can_fail()
    validate_area_energy_and_gates()
    validate_density_and_paths()
    validate_hardcode_source()
    validate_overclaims()
    print(f"run_step43.py: PASS {argv[1]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
