#!/usr/bin/env python3
"""Step 54: F50 background/vacuum demarcation on Step26 machinery."""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import os
from pathlib import Path
from typing import Any

import numpy as np


ARTIFACT_DIR = Path(__file__).resolve().parent
REPO_ROOT = ARTIFACT_DIR.parents[3]
THREAD_ROOT = ARTIFACT_DIR.parents[1]
STEP25_DIR = THREAD_ROOT / "steps" / "step25_sourcing_unification_artifacts"
STEP26_DIR = THREAD_ROOT / "steps" / "step26_semiclassical_dynamics_artifacts"
STEP26_SCRIPT = STEP26_DIR / "semiclassical_dynamics_step26.py"
STEP25_CARRIER = STEP25_DIR / "field_carrier_step25.json"
CORPUS_ROOT_ENV = "SIX_BIRDS_PAPERS_ROOT"
FOUNDATIONS_IV_NAME = "Tsiokos_2026_Six_Birds_Foundations_IV_A_Catalog_of_Layer_Agnostic_Structural_Laws.tex"
EXPECTED_STEP26_SHA256 = "391907fae6fdee8c4e4de1c12ee67d72fdfea4928cad1f148cc30e31584898fd"

BACKGROUND_OFFSETS = [-8.0, -5.0, -3.0, -2.0, -1.0, -0.5, -0.2, -0.1, 0.0, 0.1, 0.2, 0.5, 1.0, 2.0, 3.0, 5.0, 8.0, 10.0]
KAPPA_VALUES = [0.0, 0.1, 0.3, 0.5, 1.0, 2.0, 3.0, 5.0, 10.0, 15.0, 20.0, 30.0]
BACKGROUND_KAPPA = 0.3
SWEEP_MIX = 0.5


def rel(path: Path) -> str:
    return str(path.resolve().relative_to(THREAD_ROOT.resolve()))


def repo_rel(path: Path) -> str:
    return str(path.resolve().relative_to(REPO_ROOT.resolve()))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str] | None = None) -> None:
    if not rows:
        raise ValueError(f"no rows for {path}")
    if fieldnames is None:
        fieldnames = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def import_step26() -> Any:
    spec = importlib.util.spec_from_file_location("step26_semiclassical_dynamics", STEP26_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {STEP26_SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_summary(step26: Any, background: np.ndarray, kappa: float, mix: float, case_id: str) -> dict[str, Any]:
    psi0, _base_background, _source = step26.load_initial_field()
    kinetic = step26.kinetic_operator(len(psi0))
    _trace, summary, _state = step26.run_case(case_id, psi0, background, kappa, mix, kinetic, step26.STEPS)
    return summary


def row_from_summary(summary: dict[str, Any], extra: dict[str, Any]) -> dict[str, Any]:
    row = dict(extra)
    for key in [
        "converged",
        "final_update_residual",
        "fixed_point_residual",
        "final_eigen_residual",
        "final_energy",
        "final_lowest_energy",
        "final_potential_min",
        "final_potential_max",
        "potential_sourcing_residual",
        "max_unitary_norm_error",
    ]:
        value = summary[key]
        row[key] = value if isinstance(value, bool) else f"{float(value):.12g}"
    return row


def background_sweep(step26: Any) -> list[dict[str, Any]]:
    _psi0, base_background, _source = step26.load_initial_field()
    rows: list[dict[str, Any]] = []
    for offset in BACKGROUND_OFFSETS:
        background = base_background + offset
        summary = run_summary(step26, background, BACKGROUND_KAPPA, SWEEP_MIX, f"background_offset_{offset:+g}")
        rows.append(
            row_from_summary(
                summary,
                {
                    "case_id": f"background_offset_{offset:+g}",
                    "background_mode": "base_potential_plus_scalar_offset",
                    "background_offset": f"{offset:.12g}",
                    "background_min": f"{float(np.min(background)):.12g}",
                    "background_max": f"{float(np.max(background)):.12g}",
                    "kappa": f"{BACKGROUND_KAPPA:.12g}",
                    "mix": f"{SWEEP_MIX:.12g}",
                    "iterations": step26.STEPS,
                    "convergence_tol": f"{step26.CONVERGENCE_TOL:.12g}",
                },
            )
        )
    return rows


def kappa_sweep(step26: Any) -> list[dict[str, Any]]:
    _psi0, base_background, _source = step26.load_initial_field()
    rows: list[dict[str, Any]] = []
    for kappa in KAPPA_VALUES:
        summary = run_summary(step26, base_background, kappa, SWEEP_MIX, f"kappa_{kappa:g}")
        rows.append(
            row_from_summary(
                summary,
                {
                    "case_id": f"kappa_{kappa:g}",
                    "background_mode": "frozen_step26_base_potential",
                    "background_offset": "0",
                    "kappa": f"{kappa:.12g}",
                    "mix": f"{SWEEP_MIX:.12g}",
                    "iterations": step26.STEPS,
                    "convergence_tol": f"{step26.CONVERGENCE_TOL:.12g}",
                },
            )
        )
    return rows


def derive_background_classification(rows: list[dict[str, Any]]) -> dict[str, Any]:
    pass_offsets = [float(row["background_offset"]) for row in rows if str(row["converged"]) == "True"]
    fail_offsets = [float(row["background_offset"]) for row in rows if str(row["converged"]) != "True"]
    pass_count = len(pass_offsets)
    total = len(rows)
    degeneracy = len(set(pass_offsets))
    if pass_count == 0:
        classification = "no_admissible_background_in_sweep"
        verdict = "BACKGROUND_SELECTION_BLOCKED_NO_ADMISSIBLE_SWEEP_POINT"
    elif degeneracy == 1:
        classification = "vacuum"
        verdict = "BACKGROUND_SINGLETON_VACUUM_ON_FINITE_SWEEP"
    elif pass_count == total:
        classification = "moduli"
        verdict = "BACKGROUND_IS_F50_MODULI_NO_INLAYER_VALUE_LAW"
    else:
        classification = "bounded_moduli"
        verdict = "BACKGROUND_IS_F50_BOUNDED_MODULI_NO_INLAYER_VALUE_LAW"
    noncontiguous = False
    if pass_offsets and fail_offsets:
        lo, hi = min(pass_offsets), max(pass_offsets)
        noncontiguous = any(lo < offset < hi for offset in fail_offsets)
    return {
        "classification": classification,
        "verdict": verdict,
        "pass_offsets": pass_offsets,
        "fail_offsets": fail_offsets,
        "pass_count": pass_count,
        "fail_count": len(fail_offsets),
        "total": total,
        "degeneracy": degeneracy,
        "window_min": min(pass_offsets) if pass_offsets else None,
        "window_max": max(pass_offsets) if pass_offsets else None,
        "noncontiguous_finite_pass_set": noncontiguous,
        "blind": pass_count == total and degeneracy > 1,
    }


def derive_kappa_boundary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    pass_values = [float(row["kappa"]) for row in rows if str(row["converged"]) == "True"]
    fail_values = [float(row["kappa"]) for row in rows if str(row["converged"]) != "True"]
    boundary = bool(pass_values and fail_values and min(fail_values) > min(pass_values))
    return {
        "pass_values": pass_values,
        "fail_values": fail_values,
        "boundary_found": boundary,
        "max_pass": max(pass_values) if pass_values else None,
        "min_fail": min(fail_values) if fail_values else None,
    }


def structural_note_rows() -> list[dict[str, Any]]:
    return [
        {
            "note_id": "actual_step26_background_dependence",
            "structural_b_independence": False,
            "condition": "No full b-independence theorem: Step26 uses T00[psi]=|grad psi|^2 + background*|psi|^2 and V=background+kappa*T00.",
            "explanation": "A scalar background shift includes an identity-like Hamiltonian shift, but also enters kappa*background*|psi|^2, so it does not cancel generally in the fixed-point iteration.",
        },
        {
            "note_id": "finite_sweep_honesty",
            "structural_b_independence": False,
            "condition": "The classification is enumeration-strength over the declared offsets and frozen 60-step convergence criterion.",
            "explanation": "Multiple backgrounds pass and multiple fail; the result is bounded/swept moduli rather than a singleton value law.",
        },
    ]


def require_corpus_files(names: list[str]) -> list[Path]:
    root_value = os.environ.get(CORPUS_ROOT_ENV)
    if not root_value:
        raise SystemExit(f"{CORPUS_ROOT_ENV} is required; missing corpus file(s): {', '.join(names)}")
    root = Path(root_value).expanduser().resolve()
    paths = [root / name for name in names]
    for path in paths:
        if not path.is_file():
            raise SystemExit(f"{CORPUS_ROOT_ENV} missing required corpus file: {path}")
    return paths


def frozen_rows(foundations_iv: Path) -> list[dict[str, Any]]:
    sources = [
        STEP26_SCRIPT,
        STEP26_DIR / "step26_schema.json",
        STEP26_DIR / "dynamics_parameters_step26.json",
        STEP25_CARRIER,
        STEP25_DIR / "step25_schema.json",
    ]
    rows = [
        {
            "source": repo_rel(path),
            "sha256": sha256(path),
            "expected_sha256": EXPECTED_STEP26_SHA256 if path == STEP26_SCRIPT else "",
            "imported_or_read_verbatim": True,
        }
        for path in sources
    ]
    rows.append(
        {
            "source": foundations_iv.name,
            "sha256": sha256(foundations_iv),
            "expected_sha256": "",
            "imported_or_read_verbatim": True,
        }
    )
    return rows


def write_summary(schema: dict[str, Any]) -> None:
    text = f"""# Step 54 Results Summary

## Honest Grade First

This is a computed F50 demarcation on the finite frozen Step26 semiclassical toy. It does not say anything about the measured value of the real cosmological constant, does not solve the cosmological-constant problem, does not derive Lambda, does not certify frame transfer, and does not close E018. The result is a structural classification: the background/Lambda analog is not selected to a value by the in-layer closure machinery. The closure can constrain the coupling `kappa`, so the audit has teeth.

## F50 Data

- `X`: admissible Step26 semiclassical configurations `(psi, background, kappa)`.
- `mu`: closure-status quotient induced by the frozen Step26 fixed-point convergence criterion.
- `b0`: scalar offset of the matter-independent background term added to the frozen Step26 background vector.
- `target`: self-consistent co-sourcing/back-reaction fixed point.

## Background Sweep

Swept `{schema['background_sweep_count']}` background offsets with frozen `kappa=0.3`, `mix=0.5`, and `60` iterations. Pass count: `{schema['background_pass_count']}`. Degeneracy among passing backgrounds: `{schema['background_degeneracy']}`.

F50 classification: `{schema['f50_classification']}`. The finite pass set is `{schema['background_pass_examples']}` and the fail set includes `{schema['background_fail_examples']}`. The computed background window summary is `{schema['background_window']}`.

Because more than one background passes, the vacuum singleton clause fails. Because not every swept offset passes under the frozen finite criterion, the honest verdict is bounded/swept moduli, not full blindness.

## Kappa Control

The kappa sweep has `{schema['kappa_sweep_count']}` rows. Pass examples: `{schema['kappa_pass_examples']}`. Fail examples: `{schema['kappa_fail_examples']}`. Boundary found: `{schema['kappa_boundary_found']}`.

This is the discrimination tooth: the same closure chain sees `kappa` but does not select a unique background value.

## Structural Note

`{schema['structural_b_independence_note']}` The actual Step26 equation contains `background*|psi|^2`, so scalar background shifts are not proven to cancel from the fixed-point iteration. The classification is enumeration-strength over the declared sweep.

## Forbidden Rule

`{schema['forbidden_rule']}`: the framework forbids an in-layer Lambda/background value-law on this carrier. Any value law would need an extra vacuum-selection source; the in-layer result is at most an admissibility pattern/window.
"""
    (ARTIFACT_DIR / "step54_results_summary.md").write_text(text, encoding="utf-8")


def write_nonclaim() -> None:
    (ARTIFACT_DIR / "nonclaim_boundary_step54.md").write_text(
        """# Step 54 Nonclaim Boundary

This step does not solve the cosmological-constant problem, does not derive Lambda, does not predict vacuum energy, does not produce a new measured number, does not certify frame transfer, and does not close E018.

It is a finite-sweep F50 demarcation on the frozen Step26 toy. The carrier reading remains conditional on Step47's common-carrier premise. The result is enumeration-strength, not a theorem over all backgrounds.

The verdict is about the in-layer background term in `V[psi]=background+kappa*T00[psi]`. It does not claim anything about the physical cosmological constant beyond the recovered-known demarcation that no accepted in-layer value law is present here.
""",
        encoding="utf-8",
    )


def write_statement(schema: dict[str, Any]) -> None:
    (ARTIFACT_DIR / "f50_background_demarcation_statement_step54.tex").write_text(
        r"""\section*{Step 54: F50 Background Demarcation}

On the frozen Step26 semiclassical carrier, let \(b_0\) be the scalar offset
of the matter-independent background term in
\[
V[\psi]=\mathrm{background}+\kappa T_{00}[\psi].
\]
The closure-status quotient \(\mu\) is computed by the Step26 fixed-point
convergence criterion.

The background sweep contains """ + str(schema["background_sweep_count"]) + r""" offsets.  The number of passing
backgrounds is """ + str(schema["background_pass_count"]) + r""", with degeneracy
""" + str(schema["background_degeneracy"]) + r""".
Thus the vacuum singleton condition fails.  The finite classification is
\[
\mathrm{F50}(b)=""" + schema["f50_classification"].replace("_", r"\_") + r""" .
\]

The kappa control has both passing and failing values, with maximum passing
kappa """ + str(schema["kappa_max_pass"]) + r""" and minimum failing kappa
""" + str(schema["kappa_min_fail"]) + r""".  Therefore the closure chain is not
blind to all parameters; it distinguishes a constrained coupling from a
background modulus/window.

The finite forbidden rule is: no in-layer Lambda/background value law is
available from this closure.  A singleton value would require an additional
vacuum-selection source.
""",
        encoding="utf-8",
    )


def write_classification() -> None:
    write_csv(
        ARTIFACT_DIR / "content_classification_step54.csv",
        [
            {"artifact": "background_sweep_step54.csv", "classification": "finite-carrier-diagnostic", "scope": "Frozen Step26 background-offset sweep."},
            {"artifact": "kappa_sweep_step54.csv", "classification": "finite-carrier-diagnostic", "scope": "Frozen Step26 kappa control sweep."},
            {"artifact": "derived_classification_step54.csv", "classification": "finite-carrier-diagnostic", "scope": "Classification derived from sweep tables."},
            {"artifact": "structural_note_step54.csv", "classification": "analytical-structural finite-carrier-diagnostic", "scope": "Notes why full b-independence is not a theorem of the Step26 equation."},
            {"artifact": "f50_background_demarcation_statement_step54.tex", "classification": "analytical-structural finite-carrier-diagnostic", "scope": "F50 finite-sweep demarcation; not a physical Lambda theorem."},
            {"artifact": "step54_results_summary.md", "classification": "organizational + structural-recognition", "scope": "Summary and caveats."},
            {"artifact": "run_step54.py", "classification": "organizational validator", "scope": "Self/chain validation with verdict/table consistency checks."},
        ],
    )


def write_mode_packet() -> None:
    write_csv(
        ARTIFACT_DIR / "mode_b_constraint_ledger.csv",
        [
            {"constraint_id": "C_STEP54_VERDICT_DERIVED_FROM_SWEEPS", "status": "active", "description": "F50 classification must be recomputed from sweep tables."},
            {"constraint_id": "C_STEP54_KAPPA_CONTROL_BOUNDARY", "status": "active", "description": "Kappa sweep must show a genuine pass/fail boundary."},
            {"constraint_id": "C_STEP54_NO_INLAYER_VALUE_LAW", "status": "active", "description": "Multiple admissible backgrounds forbid a singleton value law in the frozen layer."},
        ],
    )
    write_csv(
        ARTIFACT_DIR / "mode_b_target_lineage.csv",
        [
            {
                "target_residual": "F50 cosmological-constant analog background demarcation",
                "canonical_target": "R_root_E018",
                "relation_to_canonical_root": "structural_demarcation_sub_residual",
                "authorization": "USER-AUTHORIZED promoted reserve item F50",
                "conditional_source": "Step47 common-carrier premise for carrier reading",
            }
        ],
    )
    write_csv(
        ARTIFACT_DIR / "mode_b_grammar_manifest.csv",
        [
            {
                "grammar_id": "G_E018_F50BackgroundModuliDemarcation_v1",
                "declared_at_step": 54,
                "objects": "Step26 fixed-point closure; background offset sweep; kappa control boundary; F50 classification",
                "excluded_designs_rationale": "Excludes hardcoding moduli or retuning Step26 convergence thresholds.",
                "non_triviality_argument": "Kappa is constrained by the same closure while background has multiple admissible values and no singleton selector.",
                "next_grammar_delta": "dynamic landscape/vacuum-selection source if a singleton background value is to be selected",
            }
        ],
    )


def write_outputs() -> None:
    foundations_iv = require_corpus_files([FOUNDATIONS_IV_NAME])[0]
    if sha256(STEP26_SCRIPT) != EXPECTED_STEP26_SHA256:
        raise RuntimeError("Step26 sha256 mismatch")
    _step25 = load_json(STEP25_DIR / "step25_schema.json")
    _step26_schema = load_json(STEP26_DIR / "step26_schema.json")
    step26 = import_step26()
    bg_rows = background_sweep(step26)
    k_rows = kappa_sweep(step26)
    bg_class = derive_background_classification(bg_rows)
    k_class = derive_kappa_boundary(k_rows)
    structural_note = structural_note_rows()
    bg_window = {
        "min_pass_offset": bg_class["window_min"],
        "max_pass_offset": bg_class["window_max"],
        "noncontiguous_finite_pass_set": bg_class["noncontiguous_finite_pass_set"],
    }
    schema = {
        "step": 54,
        "orientation": "ModeB_F50_background_moduli_demarcation",
        "active_residual": "E018 cosmological-constant analog demarcation",
        "main_object": "F50 classification of Step26 background term",
        "verdict": bg_class["verdict"],
        "background_sweep_count": bg_class["total"],
        "frozen_step26_convergence_tol": step26.CONVERGENCE_TOL,
        "background_pass_count": bg_class["pass_count"],
        "background_fail_count": bg_class["fail_count"],
        "background_degeneracy": bg_class["degeneracy"],
        "background_window": bg_window,
        "background_pass_examples": bg_class["pass_offsets"][:6],
        "background_fail_examples": bg_class["fail_offsets"][:6],
        "f50_classification": bg_class["classification"],
        "kappa_sweep_count": len(k_rows),
        "kappa_boundary_found": k_class["boundary_found"],
        "kappa_pass_examples": k_class["pass_values"][:6],
        "kappa_fail_examples": k_class["fail_values"][:6],
        "kappa_max_pass": k_class["max_pass"],
        "kappa_min_fail": k_class["min_fail"],
        "closure_blind_to_background_within_sweep": bg_class["blind"],
        "enumeration_strength_not_theorem": True,
        "structural_b_independence_note": structural_note[0]["condition"],
        "forbidden_rule": "no_inlayer_lambda_value_law",
        "cross_track_demarcation_analog": "SM_F47_F26_no_value_law_on_contingent_selection",
        "solves_cc_problem": False,
        "derives_lambda": False,
        "new_measured_number": False,
        "frame_transfer_certified": False,
        "root_landed": False,
        "conditional_on_step47_for_carrier_reading": True,
    }

    write_csv(ARTIFACT_DIR / "background_sweep_step54.csv", bg_rows)
    write_csv(ARTIFACT_DIR / "kappa_sweep_step54.csv", k_rows)
    write_csv(
        ARTIFACT_DIR / "derived_classification_step54.csv",
        [
            {
                "table": "background_sweep_step54.csv",
                "pass_count": bg_class["pass_count"],
                "fail_count": bg_class["fail_count"],
                "degeneracy": bg_class["degeneracy"],
                "classification": bg_class["classification"],
                "verdict": bg_class["verdict"],
                "derived_from_table": True,
            },
            {
                "table": "kappa_sweep_step54.csv",
                "pass_count": len(k_class["pass_values"]),
                "fail_count": len(k_class["fail_values"]),
                "degeneracy": len(set(k_class["pass_values"])),
                "classification": "closure_constrained_parameter",
                "verdict": "kappa_boundary_found" if k_class["boundary_found"] else "kappa_control_toothless",
                "derived_from_table": True,
            },
        ],
    )
    write_csv(ARTIFACT_DIR / "structural_note_step54.csv", structural_note)
    write_csv(ARTIFACT_DIR / "frozen_machinery_step54.csv", frozen_rows(foundations_iv))
    (ARTIFACT_DIR / "step54_schema.json").write_text(json.dumps(schema, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_summary(schema)
    write_nonclaim()
    write_statement(schema)
    write_classification()
    write_mode_packet()


if __name__ == "__main__":
    write_outputs()
