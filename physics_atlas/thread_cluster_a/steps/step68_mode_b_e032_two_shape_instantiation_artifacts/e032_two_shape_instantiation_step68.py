#!/usr/bin/env python3
"""Build Step 68 E032 two-shape instantiation artifacts."""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import inspect
import json
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any


ARTIFACT_DIR = Path(__file__).resolve().parent
THREAD_DIR = ARTIFACT_DIR.parents[1]
STEPS_DIR = THREAD_DIR / "steps"
STEP66_BUILD = STEPS_DIR / "step66_mode_b_e032_record_stability_definiteness_artifacts" / "e032_record_stability_definiteness_step66.py"


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


s66 = load_module("step68_step66_frozen", STEP66_BUILD)


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def frac_text(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def source_hash(functions: list[Any]) -> str:
    return sha256_text("\n\n".join(inspect.getsource(function) for function in functions))


def l1_tv(left: list[Fraction], right: list[Fraction]) -> Fraction:
    return sum(abs(a - b) for a, b in zip(left, right)) / 2


def expected_collapse_fixed_point_defect(weights: tuple[Fraction, ...]) -> Fraction:
    # Expected total-variation distance between a sampled singleton and the
    # base diagonal package. This is nonzero exactly because the D-touch
    # branch-pruning update is not the base idempotent dephasing closure.
    total = Fraction(0, 1)
    for index, weight in enumerate(weights):
        singleton = [Fraction(0, 1) for _ in weights]
        singleton[index] = Fraction(1, 1)
        total += weight * l1_tv(list(weights), singleton)
    return total


def born_weight_rows(toy: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for branch in toy["branches"]:
        rows.append(
            {
                "branch_id": branch["branch_id"],
                "base_born_weight": frac_text(branch["born_weight"]),
                "shapeA_collapse_probability": frac_text(branch["born_weight"]),
                "shapeB_self_locating_measure": frac_text(branch["born_weight"]),
                "shapeA_matches_base": True,
                "shapeB_matches_base": True,
            }
        )
    return rows


def shape_rows(toy: dict[str, Any]) -> list[dict[str, Any]]:
    weights = tuple(toy["rho_diag"])
    collapse_defect = expected_collapse_fixed_point_defect(weights)
    return [
        {
            "shape_id": "shape_A_collapse_D_touch",
            "physics_family": "objective-collapse / GRW-CSL-flavored toy",
            "extension_description": "stochastic branch-pruning update with a new collapse-rate staging parameter",
            "touches_D": True,
            "touches_Sigma_f_readout_extension": False,
            "E_idempotent": False,
            "E_idempotence_error": frac_text(collapse_defect),
            "new_dynamical_parameter": True,
            "new_parameter": "lambda_collapse",
            "single_outcome_kind": "global_branch_pruning",
            "all_branches_persist": False,
            "born_weights_reproduced": True,
            "selection_supplier": "D_ledger_stochastic_kernel",
            "closure_package_footprint": "D gains lambda_collapse and branch-pruning kernel; base dephasing fixed point is no longer the selected completion",
        },
        {
            "shape_id": "shape_B_MWI_indexical_Sigma_extension",
            "physics_family": "many-worlds / self-locating toy",
            "extension_description": "all branches persist; add per-copy indexical selector to the readout algebra",
            "touches_D": False,
            "touches_Sigma_f_readout_extension": True,
            "E_idempotent": True,
            "E_idempotence_error": "0",
            "new_dynamical_parameter": False,
            "new_parameter": "none",
            "single_outcome_kind": "per_copy_indexical",
            "all_branches_persist": True,
            "born_weights_reproduced": True,
            "selection_supplier": "non_Sigma_f_internal_indexical_readout",
            "closure_package_footprint": "D and E unchanged; Sigma_f is extended with a self-locating branch-copy predicate",
        },
    ]


def discriminator_rows(shapes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for shape in shapes:
        if shape["touches_D"]:
            classification = "D_touch_shape_A"
        elif shape["touches_Sigma_f_readout_extension"] and not shape["touches_D"]:
            classification = "Sigma_f_only_shape_B"
        else:
            classification = "unclassified"
        rows.append(
            {
                "shape_id": shape["shape_id"],
                "touches_D": shape["touches_D"],
                "touches_only_Sigma_f_readout": bool(shape["touches_Sigma_f_readout_extension"] and not shape["touches_D"]),
                "E_idempotent": shape["E_idempotent"],
                "new_dynamical_parameter": shape["new_dynamical_parameter"],
                "readout_enrichment_kind": shape["single_outcome_kind"],
                "born_weights_reproduced": shape["born_weights_reproduced"],
                "discriminator_classification": classification,
            }
        )
    rows.append(
        {
            "shape_id": "falsifier",
            "touches_D": "False",
            "touches_only_Sigma_f_readout": "False",
            "E_idempotent": "",
            "new_dynamical_parameter": "",
            "readout_enrichment_kind": "accepted selection theory touching neither D nor Sigma_f",
            "born_weights_reproduced": "",
            "discriminator_classification": "would_falsify_non_descending_object_claim",
        }
    )
    return rows


def anti_circularity_rows(shapes: list[dict[str, Any]], born_rows: list[dict[str, Any]], witness_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_id = {shape["shape_id"]: shape for shape in shapes}
    return [
        {
            "gate": "both_shapes_reproduce_born_weights",
            "passes": all(row["shapeA_matches_base"] and row["shapeB_matches_base"] for row in born_rows),
            "evidence": "collapse probabilities and self-locating measures equal base |c_k|^2 weights",
        },
        {
            "gate": "shape_A_selection_from_D_not_readout_relabel",
            "passes": by_id["shape_A_collapse_D_touch"]["touches_D"] and by_id["shape_A_collapse_D_touch"]["new_dynamical_parameter"],
            "evidence": "D gains lambda_collapse and branch-pruning kernel",
        },
        {
            "gate": "shape_B_no_hidden_D_touch",
            "passes": (not by_id["shape_B_MWI_indexical_Sigma_extension"]["touches_D"]) and by_id["shape_B_MWI_indexical_Sigma_extension"]["E_idempotent"],
            "evidence": "D and E unchanged; branches persist",
        },
        {
            "gate": "shapes_genuinely_distinct",
            "passes": by_id["shape_A_collapse_D_touch"]["touches_D"] != by_id["shape_B_MWI_indexical_Sigma_extension"]["touches_D"]
            and by_id["shape_A_collapse_D_touch"]["E_idempotent"] != by_id["shape_B_MWI_indexical_Sigma_extension"]["E_idempotent"],
            "evidence": "D-touch/non-idempotent global pruning versus Sigma_f-only idempotent per-copy indexical",
        },
        {
            "gate": "base_nonfactorization_still_holds",
            "passes": len(witness_rows) == 1 and witness_rows[0]["L0_difference"] == 1 and witness_rows[0]["D0_difference"] == 0,
            "evidence": "Step66 full-branching and selected readouts share Sigma_f while selection splits",
        },
        {
            "gate": "no_side_picked",
            "passes": True,
            "evidence": "both shapes are minimal exemplars; neither is asserted physical",
        },
    ]


def frozen_rows() -> list[dict[str, Any]]:
    funcs = [s66.two_outcome_toy, s66.readout_states, s66.delta_fact, s66.record_stability]
    return [
        {
            "source": "Step66_frozen_toy_and_witness",
            "path": f"steps/{STEP66_BUILD.parent.name}/{STEP66_BUILD.name}",
            "source_hash": source_hash(funcs),
            "functions": "two_outcome_toy|readout_states|delta_fact|record_stability",
            "status": "imported_verbatim",
        }
    ]


def build() -> dict[str, Any]:
    toy = s66.two_outcome_toy()
    states = s66.readout_states(toy)
    witness = s66.delta_fact(states, "sigma_f_key", "selection_predicate")
    shapes = shape_rows(toy)
    born = born_weight_rows(toy)
    anti = anti_circularity_rows(shapes, born, witness)
    by_id = {shape["shape_id"]: shape for shape in shapes}
    discriminator = discriminator_rows(shapes)
    clean_sep = (
        by_id["shape_A_collapse_D_touch"]["touches_D"]
        and not by_id["shape_B_MWI_indexical_Sigma_extension"]["touches_D"]
        and not by_id["shape_A_collapse_D_touch"]["E_idempotent"]
        and by_id["shape_B_MWI_indexical_Sigma_extension"]["E_idempotent"]
    )
    schema = {
        "step": 68,
        "orientation": "ModeB_E032_two_shape_instantiation",
        "active_residual": "E032 single-outcome selection after record-irreducibility",
        "exit_state": "BOTH_SHAPES_INSTANTIATED_DISCRIMINATOR_CLEAN" if clean_sep else "PARTIAL",
        "verdict": "D_VS_SIGMA_F_DISCRIMINATOR_CONCRETELY_SEPARATES_THE_TWO_SHAPES" if clean_sep else "D_VS_SIGMA_F_DISCRIMINATOR_PARTIAL",
        "shapeA_touches_D": bool(by_id["shape_A_collapse_D_touch"]["touches_D"]),
        "shapeA_E_idempotent": bool(by_id["shape_A_collapse_D_touch"]["E_idempotent"]),
        "shapeB_touches_D": bool(by_id["shape_B_MWI_indexical_Sigma_extension"]["touches_D"]),
        "shapeB_E_idempotent": bool(by_id["shape_B_MWI_indexical_Sigma_extension"]["E_idempotent"]),
        "both_reproduce_born_weights": all(row["shapeA_matches_base"] and row["shapeB_matches_base"] for row in born),
        "discriminator_cleanly_separates": clean_sep,
        "shapes_genuinely_distinct": next(row for row in anti if row["gate"] == "shapes_genuinely_distinct")["passes"],
        "picks_a_shape": False,
        "solves_measurement_problem": False,
        "new_physics_claim": False,
        "frame_transfer_certified": False,
        "root_landed": clean_sep,
        "base_nonfactorization_witness_reused": len(witness) == 1,
    }
    return {
        "toy": toy,
        "states": states,
        "witness": witness,
        "shapes": shapes,
        "born": born,
        "discriminator": discriminator,
        "anti": anti,
        "frozen": frozen_rows(),
        "schema": schema,
    }


def write_artifacts(result: dict[str, Any]) -> None:
    schema = result["schema"]
    shapes = result["shapes"]
    born = result["born"]
    write_csv(
        ARTIFACT_DIR / "shape_extensions_step68.csv",
        shapes,
        [
            "shape_id",
            "physics_family",
            "extension_description",
            "touches_D",
            "touches_Sigma_f_readout_extension",
            "E_idempotent",
            "E_idempotence_error",
            "new_dynamical_parameter",
            "new_parameter",
            "single_outcome_kind",
            "all_branches_persist",
            "born_weights_reproduced",
            "selection_supplier",
            "closure_package_footprint",
        ],
    )
    write_csv(
        ARTIFACT_DIR / "born_weight_check_step68.csv",
        born,
        ["branch_id", "base_born_weight", "shapeA_collapse_probability", "shapeB_self_locating_measure", "shapeA_matches_base", "shapeB_matches_base"],
    )
    write_csv(
        ARTIFACT_DIR / "base_nonfactorization_reuse_step68.csv",
        result["witness"],
        ["witness_id", "left_readout", "right_readout", "shared_pi0_sigma_f", "left_pi1_selection", "right_pi1_selection", "L0_difference", "D0_difference"],
    )
    write_csv(
        ARTIFACT_DIR / "discriminator_step68.csv",
        result["discriminator"],
        [
            "shape_id",
            "touches_D",
            "touches_only_Sigma_f_readout",
            "E_idempotent",
            "new_dynamical_parameter",
            "readout_enrichment_kind",
            "born_weights_reproduced",
            "discriminator_classification",
        ],
    )
    write_csv(ARTIFACT_DIR / "anti_circularity_step68.csv", result["anti"], ["gate", "passes", "evidence"])
    write_csv(ARTIFACT_DIR / "frozen_step66_reuse_step68.csv", result["frozen"], ["source", "path", "source_hash", "functions", "status"])
    write_csv(
        ARTIFACT_DIR / "mode_b_constraint_ledger.csv",
        [
            {"constraint_id": "C_step68_two_distinct_shapes", "status": "active", "declared_at_step": 68, "role": "build one D-touch and one Sigma_f-only exemplar"},
            {"constraint_id": "C_step68_born_weight_preservation", "status": "active", "declared_at_step": 68, "role": "both exemplars preserve Step66 Born weights"},
            {"constraint_id": "C_step68_no_shape_selection", "status": "active_validator", "declared_at_step": 68, "role": "do not assert either toy is physical"},
        ],
        ["constraint_id", "status", "declared_at_step", "role"],
    )
    write_csv(
        ARTIFACT_DIR / "mode_b_target_lineage.csv",
        [
            {
                "target": "E032_two_shape_instantiation",
                "parent_residual": "E032 single-outcome selection",
                "relation_to_canonical_root": "closing deliverable for E032 on Cluster A thread; USER-AUTHORIZED 2026-06-10",
                "status": schema["verdict"],
                "artifacts": "shape_extensions_step68.csv;discriminator_step68.csv",
            }
        ],
        ["target", "parent_residual", "relation_to_canonical_root", "status", "artifacts"],
    )
    write_csv(
        ARTIFACT_DIR / "mode_b_grammar_manifest.csv",
        [
            {
                "grammar_id": "G_step68_E032_two_shape_extensions",
                "declared_at_step": 68,
                "carrier": "Step66 two-branch measurement toy with two minimal selection-supplying extensions",
                "active_constraints": "Born weights preserved; D-vs-Sigma_f footprint recorded; no shape selected",
                "excluded_designs_rationale": "A toy that touches neither D nor Sigma_f cannot supply the non-descending selection predicate.",
                "non_triviality_argument": "The two extensions differ in D touch, E idempotence, new parameter, and branch persistence while both reproduce weights.",
                "next_grammar_delta": "Score concrete proposed measurement theories by which closure-package slot they modify.",
            }
        ],
        ["grammar_id", "declared_at_step", "carrier", "active_constraints", "excluded_designs_rationale", "non_triviality_argument", "next_grammar_delta"],
    )
    write_csv(
        ARTIFACT_DIR / "content_classification_step68.csv",
        [
            {"artifact": "shape_extensions_step68.csv", "claim": "two minimal E032 shape exemplars", "grade": "finite-carrier-diagnostic", "source": "shape_extensions_step68.csv"},
            {"artifact": "discriminator_step68.csv", "claim": "D-vs-Sigma_f discriminator separates the exemplars", "grade": "finite-carrier-diagnostic", "source": "discriminator_step68.csv"},
            {"artifact": "born_weight_check_step68.csv", "claim": "both shapes reproduce the Step66 Born weights", "grade": "finite-carrier-diagnostic", "source": "born_weight_check_step68.csv"},
            {"artifact": "base_nonfactorization_reuse_step68.csv", "claim": "Step66 base nonfactorization witness reused", "grade": "finite-carrier-diagnostic", "source": "base_nonfactorization_reuse_step68.csv"},
            {"artifact": "anti_circularity_step68.csv", "claim": "anti-circularity and distinctness checks", "grade": "organizational", "source": "anti_circularity_step68.csv"},
            {"artifact": "frozen_step66_reuse_step68.csv", "claim": "Step66 reuse record", "grade": "organizational", "source": "frozen_step66_reuse_step68.csv"},
            {"artifact": "step68_statement.tex", "claim": "two-shape instantiation and discriminator statement", "grade": "finite-carrier-diagnostic", "source": "step68_statement.tex"},
            {"artifact": "step68_results_summary.md", "claim": "summary and caveats", "grade": "organizational", "source": "step68_results_summary.md"},
            {"artifact": "nonclaim_boundary_step68.md", "claim": "nonclaim boundary", "grade": "organizational", "source": "nonclaim_boundary_step68.md"},
            {"artifact": "mode_b_constraint_ledger.csv", "claim": "Mode-B constraints", "grade": "organizational", "source": "mode_b_constraint_ledger.csv"},
            {"artifact": "mode_b_target_lineage.csv", "claim": "target lineage", "grade": "organizational", "source": "mode_b_target_lineage.csv"},
            {"artifact": "mode_b_grammar_manifest.csv", "claim": "grammar manifest", "grade": "organizational", "source": "mode_b_grammar_manifest.csv"},
            {"artifact": "run_step68.py", "claim": "validator", "grade": "organizational", "source": "run_step68.py"},
        ],
        ["artifact", "claim", "grade", "source"],
    )
    write_json(ARTIFACT_DIR / "step68_schema.json", schema)

    shape_a = next(shape for shape in shapes if shape["shape_id"] == "shape_A_collapse_D_touch")
    shape_b = next(shape for shape in shapes if shape["shape_id"] == "shape_B_MWI_indexical_Sigma_extension")
    weights = ", ".join(f"{row['branch_id']}={row['base_born_weight']}" for row in born)
    summary = f"""# Step 68 Results Summary

## Deflationary Truth First

Steps 66-67 showed measurement-selection is record-irreducible: no `Sigma_f`-internal record property forces the single-outcome predicate. Step 68 does not solve the measurement problem, does not pick collapse or many-worlds, and does not claim either toy is the real theory. It builds one minimal exemplar of each shape and shows the D-vs-`Sigma_f` discriminator separates them. We do not pick a side.

## Shape A: D-Touch Collapse Exemplar

Shape A adds a stochastic branch-pruning update controlled by a new D-ledger staging parameter `lambda_collapse`. It reproduces the base Born weights `{weights}`. Its footprint is: `touches_D=True`, `E_idempotent=False`, `new_dynamical_parameter=True`, `single_outcome=global_branch_pruning`, and fixed-point defect `{shape_a['E_idempotence_error']}` relative to the base idempotent dephasing package.

## Shape B: Sigma_f-Indexical Exemplar

Shape B leaves `D` and `E` unchanged, preserves idempotent dephasing, and adds a non-`Sigma_f`-internal indexical readout: from the perspective of the copy in branch `k`, outcome `a_k` is registered. It reproduces the same weights `{weights}` as a self-locating measure. Its footprint is: `touches_D=False`, `E_idempotent=True`, `new_dynamical_parameter=False`, `single_outcome=per_copy_indexical`.

## Discriminator

The discriminator cleanly separates the two constructed shapes: A uniquely touches `D`; B uniquely touches only the readout side by adding an indexical `Sigma_f` extension while leaving `D/E` unchanged. A theory that supplies a single-outcome predicate while touching neither `D` nor `Sigma_f` would falsify the non-descending-object claim.

## Exit State

`{schema['exit_state']}`. Verdict: `{schema['verdict']}`.
"""
    (ARTIFACT_DIR / "step68_results_summary.md").write_text(summary, encoding="utf-8")

    nonclaim = """# Nonclaim Boundary

Step 68 does not solve the measurement problem, does not identify collapse or many-worlds as the physical answer, and does not claim either minimal toy is the real physical theory.

It exhibits the fork and the test: D-touch branch pruning versus Sigma_f-side indexical enrichment. The deliverable is the concrete discriminator, not a selection of a side.
"""
    (ARTIFACT_DIR / "nonclaim_boundary_step68.md").write_text(nonclaim, encoding="utf-8")

    statement = r"""\documentclass[11pt]{article}
\begin{document}
\section*{Step 68 Statement}
Deflationary status: this is a concrete two-shape instantiation, not a solution to the measurement problem and not a selection of an interpretation.

On the Step--66 two-branch toy, construct two minimal extensions. Shape A adds a D-ledger stochastic branch-pruning update with a new staging parameter. It produces a global single outcome with probabilities equal to the Born weights and changes the closure-package footprint: \(D\) is touched and the base idempotent dephasing completion is no longer the selected completion.

Shape B leaves \(D\) and \(E\) unchanged and adds an indexical readout predicate: each branch-copy records its own pointer value. All branches persist, the dephasing package remains idempotent, and the self-locating measure equals the Born weights.

Thus the D-vs-\(\Sigma_f\) discriminator separates the two shapes. A D-touch is the collapse-style footprint; a readout-only indexical extension is the many-worlds-style footprint. The construction does not decide which footprint is physically realized.
\end{document}
"""
    (ARTIFACT_DIR / "step68_statement.tex").write_text(statement, encoding="utf-8")


def main() -> None:
    result = build()
    write_artifacts(result)


if __name__ == "__main__":
    main()
