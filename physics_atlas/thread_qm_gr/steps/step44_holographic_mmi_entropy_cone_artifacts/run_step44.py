#!/usr/bin/env python3
"""Validate Step 44 holographic MMI entropy-cone artifacts."""

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
BUILD_SCRIPT = ARTIFACT_DIR / "holographic_mmi_entropy_cone_step44.py"
TOL = 1e-9

REQUIRED_FILES = [
    "holographic_mmi_entropy_cone_step44.py",
    "step44_results_summary.md",
    "step44_schema.json",
    "content_classification_step44.csv",
    "nonclaim_boundary_step44.md",
    "step44_mmi_entropy_cone_statement.tex",
    "mmi_entropy_cone_sim_step44.csv",
    "mmi_entropy_cone_trend_step44.csv",
    "mmi_mincut_step44.csv",
    "mmi_mincut_details_step44.csv",
    "mmi_control_step44.csv",
    "region_entropy_details_step44.csv",
    "contracted_state_summary_step44.csv",
    "sign_convention_step44.csv",
    "generated_vs_input_step44.csv",
    "anti_circularity_step44.csv",
    "six_gate_audit_step44.csv",
    "mode_b_constraint_ledger.csv",
    "mode_b_target_lineage.csv",
    "mode_b_grammar_manifest.csv",
    "run_step44.py",
]

OVERCLAIM_PATTERNS = [
    r"derives\s+1/4G",
    r"derives\s+(?:a\s+)?(?:constant|mass)",
    r"proves\s+quantum\s+gravity",
    r"solves\s+quantum\s+gravity",
    r"derives\s+the\s+Einstein\s+equation\s+unconditionally",
    r"closes\s+E018",
    r"unconditional\s+new[- ]physics",
]


def fail(message: str) -> None:
    print(f"run_step44.py: FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def as_bool(value: object) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def read_csv(name: str) -> list[dict[str, str]]:
    with (ARTIFACT_DIR / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def load_builder():
    spec = importlib.util.spec_from_file_location("step44_builder", BUILD_SCRIPT)
    if spec is None or spec.loader is None:
        fail("could not import build script")
    module = importlib.util.module_from_spec(spec)
    sys.modules["step44_builder"] = module
    spec.loader.exec_module(module)
    return module


def validate_presence() -> None:
    missing = [name for name in REQUIRED_FILES if not (ARTIFACT_DIR / name).exists()]
    if missing:
        fail(f"missing required artifacts: {missing}")


def validate_schema() -> dict[str, object]:
    schema = json.loads((ARTIFACT_DIR / "step44_schema.json").read_text(encoding="utf-8"))
    expected = {
        "step": 44,
        "orientation": "ModeB_E018_holographic_MMI_entropy_cone",
        "verdict": "HOLOGRAPHIC_MMI_SATISFIED_GENERIC_VIOLATES",
        "mmi_satisfied_holographic": True,
        "mmi_satisfied_mincut": True,
        "mmi_violated_control": True,
        "entropies_from_contracted_state": True,
        "new_physics_claim": False,
        "root_landed": False,
        "frame_transfer_certified": False,
        "dynamical_einstein_response_attempted": False,
    }
    for key, value in expected.items():
        if schema.get(key) != value:
            fail(f"schema field {key!r} expected {value!r}, got {schema.get(key)!r}")
    if float(schema["I3_GHZ_control"]) <= TOL:
        fail("GHZ control does not violate standard MMI")
    by_d = schema["I3_holographic_by_D"]
    for dim in ["D2", "D3", "D4"]:
        if dim not in by_d:
            fail(f"schema lacks holographic I3 for {dim}")
        if float(by_d[dim]["max"]) > TOL:
            fail(f"holographic max I3 positive for {dim}")
    for case_id, value in schema["I3_mincut_by_D"].items():
        if float(value) > TOL:
            fail(f"min-cut I3 positive for {case_id}")
    return schema


def validate_holographic_rows() -> None:
    rows = read_csv("mmi_entropy_cone_sim_step44.csv")
    if len(rows) != 9:
        fail("expected 9 holographic rows: 3 bond dimensions x 3 seeds")
    if not all(as_bool(row["entropies_from_contracted_state"]) for row in rows):
        fail("some holographic rows are not marked as contracted-state entropies")
    if not all(float(row["I3_standard"]) <= TOL for row in rows):
        fail("a contracted holographic row violates standard MMI")
    dims = {int(row["bond_dim"]) for row in rows}
    if dims != {2, 3, 4}:
        fail(f"unexpected bond dimensions in holographic rows: {sorted(dims)}")
    for dim in (2, 3, 4):
        seeds = {int(row["seed"]) for row in rows if int(row["bond_dim"]) == dim}
        if seeds != {101, 202, 303}:
            fail(f"unexpected seed set for D={dim}: {sorted(seeds)}")

    trend = read_csv("mmi_entropy_cone_trend_step44.csv")
    if len(trend) != 3:
        fail("trend table must have D=2,3,4")
    for row in trend:
        if not as_bool(row["mmi_satisfied_all_seeds"]):
            fail(f"trend row does not satisfy all seeds: D={row['bond_dim']}")
        if float(row["max_I3_standard"]) > TOL:
            fail(f"trend max I3 positive: D={row['bond_dim']}")


def validate_mincut_and_control() -> None:
    mincut = read_csv("mmi_mincut_step44.csv")
    if len(mincut) != 3:
        fail("min-cut table must have D=2,3,4")
    for row in mincut:
        if float(row["I3_standard"]) > TOL:
            fail(f"min-cut I3 violates MMI: {row['case_id']}")
        if not as_bool(row["mmi_satisfied_standard"]):
            fail(f"min-cut row not marked satisfied: {row['case_id']}")
    details = read_csv("mmi_mincut_details_step44.csv")
    if len(details) < 21:
        fail("min-cut details should include seven regions for each D")

    control = read_csv("mmi_control_step44.csv")
    if len(control) != 1:
        fail("expected one GHZ control row")
    row = control[0]
    if float(row["I3_standard"]) <= TOL or not as_bool(row["mmi_violated_standard"]):
        fail("GHZ control does not violate standard MMI")
    if not as_bool(row["entropies_from_state"]):
        fail("GHZ control entropies are not marked as state-derived")


def validate_entropy_details_and_sign() -> None:
    details = read_csv("region_entropy_details_step44.csv")
    if not details:
        fail("region entropy details are empty")
    holo = [row for row in details if row["source"] == "contracted_step42_random_tensor"]
    if len(holo) != 63:
        fail("expected seven region entropies for each of nine holographic cases")
    if not all("entropy_from_region" in row["entropy_code_path"] for row in holo):
        fail("holographic entropy details do not cite the partial-trace path")
    sign = read_csv("sign_convention_step44.csv")
    names = {row["name"] for row in sign}
    if "standard_I3_used_for_verdict" not in names or "prompt_expanded_formula_recorded_as_negated" not in names:
        fail("sign convention ledger is incomplete")


def validate_gates_and_paths() -> None:
    for row in read_csv("anti_circularity_step44.csv"):
        if not as_bool(row["passes"]):
            fail(f"anti-circularity gate failed: {row['gate']}")
    for row in read_csv("six_gate_audit_step44.csv"):
        if not as_bool(row["passes"]):
            fail(f"six-gate audit failed: {row['gate']}")
    rows = read_csv("content_classification_step44.csv")
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
    if "G_E018_HolographicEntropyCone_v1" not in manifest:
        fail("grammar manifest missing G_E018_HolographicEntropyCone_v1")
    if "multi-region MMI" not in manifest and "MMI" not in manifest:
        fail("grammar manifest missing MMI grammar delta")
    constraints = (ARTIFACT_DIR / "mode_b_constraint_ledger.csv").read_text(encoding="utf-8")
    if "C_STEP44_MMI_FALSIFIABLE_NOT_UNIVERSAL" not in constraints:
        fail("constraint ledger missing Step44 MMI constraint")


def validate_overclaims() -> None:
    text = "\n".join(
        (ARTIFACT_DIR / name).read_text(encoding="utf-8")
        for name in [
            "step44_results_summary.md",
            "nonclaim_boundary_step44.md",
            "step44_mmi_entropy_cone_statement.tex",
            "mode_b_target_lineage.csv",
            "mode_b_grammar_manifest.csv",
        ]
    )
    for pattern in OVERCLAIM_PATTERNS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            fail(f"forbidden overclaim phrase: {pattern}")


def run_chain() -> None:
    subprocess.run([sys.executable, str(BUILD_SCRIPT)], cwd=str(ARTIFACT_DIR), check=True)


def run_quick_recompute() -> None:
    builder = load_builder()
    builder.BOND_DIMS = [2, 3]
    sim_rows, _detail_rows, _state_rows = builder.contracted_random_rows()
    mincut_rows, _mincut_details = builder.mincut_rows()
    control_rows, _control_details = builder.ghz_control_rows()
    if len(sim_rows) != 6:
        fail("quick recompute expected D=2,3 over three seeds")
    if not all(float(row["I3_standard"]) <= TOL for row in sim_rows):
        fail("quick recompute holographic rows violate MMI")
    if not all(float(row["I3_standard"]) <= TOL for row in mincut_rows):
        fail("quick recompute min-cut rows violate MMI")
    if float(control_rows[0]["I3_standard"]) <= TOL:
        fail("quick recompute GHZ control does not violate MMI")
    print("run_step44.py: QUICK (D=2,3 only) recompute PASS")


def main(argv: list[str]) -> int:
    if len(argv) != 2 or argv[1] not in {"--self", "--chain", "--quick"}:
        print("usage: run_step44.py --self|--chain|--quick", file=sys.stderr)
        return 2
    if argv[1] == "--chain":
        run_chain()
    validate_presence()
    validate_schema()
    validate_holographic_rows()
    validate_mincut_and_control()
    validate_entropy_details_and_sign()
    validate_gates_and_paths()
    validate_overclaims()
    if argv[1] == "--quick":
        run_quick_recompute()
    print(f"run_step44.py: PASS {argv[1]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
