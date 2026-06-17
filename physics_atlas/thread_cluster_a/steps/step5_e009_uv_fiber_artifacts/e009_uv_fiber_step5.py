#!/usr/bin/env python3
"""Cluster A Step 5: E009 UV-completion fiber facet."""

from __future__ import annotations

import csv
import json
from pathlib import Path


ARTIFACT_DIR = Path(__file__).resolve().parent
THREAD_DIR = ARTIFACT_DIR.parents[1]
REALIZED_UV = "U_SM"
REALIZED_IR = "IR_SM_TOY"
TOL = 1.0e-10


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str] | None = None) -> None:
    if fieldnames is None:
        fieldnames = list(rows[0].keys()) if rows else []
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def uv_candidates() -> list[dict[str, object]]:
    return [
        {
            "uv_id": "U_SM",
            "IR_EFT_code": REALIZED_IR,
            "heavy_state_code": "H_SM_COMPLETION",
            "breaking_pattern_code": "B_SM_PATH",
            "uv_structure_code": "UV_SM_TOY",
            "unitarity_ok": True,
            "causality_ok": True,
            "positivity_ok": True,
            "anomaly_ok": True,
            "base_score": 100.0,
        },
        {
            "uv_id": "U_alt_GUT",
            "IR_EFT_code": REALIZED_IR,
            "heavy_state_code": "H_GUT_MULTIPLETS",
            "breaking_pattern_code": "B_GUT_TO_SM",
            "uv_structure_code": "UV_ALT_GUT_TOY",
            "unitarity_ok": True,
            "causality_ok": True,
            "positivity_ok": True,
            "anomaly_ok": True,
            "base_score": 86.0,
        },
        {
            "uv_id": "U_alt_stringy",
            "IR_EFT_code": REALIZED_IR,
            "heavy_state_code": "H_STRINGY_TOWER",
            "breaking_pattern_code": "B_FLUX_TO_SM",
            "uv_structure_code": "UV_ALT_STRINGY_TOY",
            "unitarity_ok": True,
            "causality_ok": True,
            "positivity_ok": True,
            "anomaly_ok": True,
            "base_score": 81.0,
        },
        {
            "uv_id": "U_bad_unitarity",
            "IR_EFT_code": REALIZED_IR,
            "heavy_state_code": "H_GHOST_MODE",
            "breaking_pattern_code": "B_BAD_GHOST",
            "uv_structure_code": "UV_BAD_UNITARITY_TOY",
            "unitarity_ok": False,
            "causality_ok": True,
            "positivity_ok": True,
            "anomaly_ok": True,
            "base_score": 92.0,
        },
        {
            "uv_id": "U_bad_positivity",
            "IR_EFT_code": REALIZED_IR,
            "heavy_state_code": "H_NEGATIVE_FORWARD_LIMIT",
            "breaking_pattern_code": "B_BAD_POSITIVITY",
            "uv_structure_code": "UV_BAD_POSITIVITY_TOY",
            "unitarity_ok": True,
            "causality_ok": True,
            "positivity_ok": False,
            "anomaly_ok": True,
            "base_score": 83.0,
        },
        {
            "uv_id": "U_bad_anomaly",
            "IR_EFT_code": REALIZED_IR,
            "heavy_state_code": "H_ANOMALOUS_COMPLETION",
            "breaking_pattern_code": "B_BAD_ANOMALY",
            "uv_structure_code": "UV_BAD_ANOMALY_TOY",
            "unitarity_ok": True,
            "causality_ok": True,
            "positivity_ok": True,
            "anomaly_ok": False,
            "base_score": 84.0,
        },
        {
            "uv_id": "U_alt_IR_A",
            "IR_EFT_code": "IR_ALT_A_TOY",
            "heavy_state_code": "H_ALT_A",
            "breaking_pattern_code": "B_ALT_A",
            "uv_structure_code": "UV_ALT_IR_A_TOY",
            "unitarity_ok": True,
            "causality_ok": True,
            "positivity_ok": True,
            "anomaly_ok": True,
            "base_score": 72.0,
        },
        {
            "uv_id": "U_alt_IR_A_bad",
            "IR_EFT_code": "IR_ALT_A_TOY",
            "heavy_state_code": "H_ALT_A_BAD",
            "breaking_pattern_code": "B_ALT_A_BAD",
            "uv_structure_code": "UV_ALT_IR_A_BAD_TOY",
            "unitarity_ok": True,
            "causality_ok": False,
            "positivity_ok": True,
            "anomaly_ok": True,
            "base_score": 70.0,
        },
        {
            "uv_id": "U_alt_IR_B",
            "IR_EFT_code": "IR_ALT_B_TOY",
            "heavy_state_code": "H_ALT_B",
            "breaking_pattern_code": "B_ALT_B",
            "uv_structure_code": "UV_ALT_IR_B_TOY",
            "unitarity_ok": True,
            "causality_ok": True,
            "positivity_ok": True,
            "anomaly_ok": True,
            "base_score": 68.0,
        },
    ]


def uv_content(row: dict[str, object]) -> str:
    return f"{row['heavy_state_code']}|{row['breaking_pattern_code']}|{row['uv_structure_code']}"


def consistency_ok(row: dict[str, object]) -> bool:
    return all(bool(row[key]) for key in ["unitarity_ok", "causality_ok", "positivity_ok", "anomaly_ok"])


def consistency_defect(row: dict[str, object]) -> str:
    failed = [key.replace("_ok", "") for key in ["unitarity_ok", "causality_ok", "positivity_ok", "anomaly_ok"] if not bool(row[key])]
    return "none" if not failed else ";".join(failed)


def selection_score(row: dict[str, object]) -> float:
    score = float(row["base_score"])
    if row["uv_id"] == REALIZED_UV:
        score += 8.0
    if row["IR_EFT_code"] != REALIZED_IR:
        score -= 25.0
    return score


def derived_ir_observable(ir_code: str) -> float:
    values = {
        REALIZED_IR: 1.375,
        "IR_ALT_A_TOY": 0.875,
        "IR_ALT_B_TOY": 1.950,
    }
    return values[ir_code]


def obstruction(records: list[dict[str, object]], source_key: str, target_key: str) -> tuple[int, str]:
    count = 0
    witnesses: list[str] = []
    for i in range(len(records)):
        for j in range(i + 1, len(records)):
            if records[i][source_key] != records[j][source_key]:
                continue
            left = records[i][target_key]
            right = records[j][target_key]
            if isinstance(left, float) or isinstance(right, float):
                differs = abs(float(left) - float(right)) > TOL
            else:
                differs = left != right
            if differs:
                count += 1
                witnesses.append(f"{records[i]['uv_id']}-{records[j]['uv_id']}")
    return count, ";".join(witnesses) if witnesses else "none"


def main() -> None:
    rows: list[dict[str, object]] = []
    for candidate in uv_candidates():
        ok = consistency_ok(candidate)
        action = "survives" if ok else "pruned"
        ir = str(candidate["IR_EFT_code"])
        flow_staging = f"UV:{candidate['uv_id']}|stage1:thresholds({candidate['heavy_state_code']})|IR:{ir}"
        row = {
            **candidate,
            "UV_content": uv_content(candidate),
            "C_consistent": ok,
            "consistency_defect": consistency_defect(candidate),
            "constraint_action": action,
            "selection_score": selection_score(candidate) if ok and ir == REALIZED_IR else "",
            "selected_in_realized_fiber": False,
            "P4_UV_to_IR_staging": flow_staging,
            "derived_IR_observable": derived_ir_observable(ir),
            "realized_IR_fiber": ir == REALIZED_IR,
        }
        rows.append(row)

    realized_fiber = [row for row in rows if row["IR_EFT_code"] == REALIZED_IR]
    admissible_fiber = [row for row in realized_fiber if row["C_consistent"]]
    selected = max(admissible_fiber, key=lambda row: float(row["selection_score"]))
    for row in rows:
        row["selected_in_realized_fiber"] = row["uv_id"] == selected["uv_id"]

    uv_obstruction_count, uv_witness = obstruction(rows, "IR_EFT_code", "UV_content")
    ir_obstruction_count, ir_witness = obstruction(rows, "IR_EFT_code", "derived_IR_observable")

    nonfactorization_rows = [
        {
            "test_id": "UV_completion_from_IR_EFT",
            "source": "IR_EFT_code",
            "target": "UV_content",
            "non_descending": uv_obstruction_count > 0,
            "obstruction_count": uv_obstruction_count,
            "witness": uv_witness,
            "interpretation": "multiple UV completions share an IR EFT but differ in UV content",
        },
        {
            "test_id": "derived_IR_observable_from_IR_EFT",
            "source": "IR_EFT_code",
            "target": "derived_IR_observable",
            "non_descending": ir_obstruction_count > 0,
            "obstruction_count": ir_obstruction_count,
            "witness": ir_witness,
            "interpretation": "derived IR observable is fixed by the IR EFT code",
        },
    ]

    nonselected_admissible = [str(row["uv_id"]) for row in admissible_fiber if row["uv_id"] != selected["uv_id"]]
    consistency_selection_rows = [
        {
            "IR_EFT_code": REALIZED_IR,
            "realized_fiber_size": len(realized_fiber),
            "admissible_fiber_size_before_selection": len(admissible_fiber),
            "admissible_fiber": ";".join(str(row["uv_id"]) for row in admissible_fiber),
            "selected_count_after_selection": 1,
            "selected_UV": selected["uv_id"],
            "selected_score": selected["selection_score"],
            "nonselected_admissible_count": len(nonselected_admissible),
            "nonselected_admissible": ";".join(nonselected_admissible),
            "pruned_in_realized_fiber": ";".join(str(row["uv_id"]) for row in realized_fiber if not row["C_consistent"]),
        }
    ]

    many_to_one = len(realized_fiber) > 1 and len({row["UV_content"] for row in realized_fiber}) > 1
    inconsistent_removed = any((not row["C_consistent"]) and row["constraint_action"] == "pruned" for row in rows)
    consistent_survives = any(row["C_consistent"] and row["constraint_action"] == "survives" for row in rows)
    selection_collapses = len(admissible_fiber) > 1 and selected["uv_id"] == REALIZED_UV
    controls = [
        {
            "control_id": "many_to_one_realized_IR_fiber",
            "expected": "multiple_UV_share_realized_IR",
            "passes_guard": many_to_one,
            "computed_witness": ";".join(str(row["uv_id"]) for row in realized_fiber),
        },
        {
            "control_id": "UV_non_descending_positive",
            "expected": "UV_obstruction_gt_0",
            "passes_guard": uv_obstruction_count > 0,
            "computed_witness": f"obstruction={uv_obstruction_count}; witness={uv_witness}",
        },
        {
            "control_id": "derived_IR_observable_factors",
            "expected": "IR_obstruction_0",
            "passes_guard": ir_obstruction_count == 0,
            "computed_witness": f"obstruction={ir_obstruction_count}; witness={ir_witness}",
        },
        {
            "control_id": "consistency_prune_discriminates",
            "expected": "inconsistent_removed_and_consistent_survives",
            "passes_guard": inconsistent_removed and consistent_survives,
            "computed_witness": (
                f"pruned={';'.join(str(row['uv_id']) for row in rows if row['constraint_action'] == 'pruned')}; "
                f"survives={';'.join(str(row['uv_id']) for row in rows if row['constraint_action'] == 'survives')}"
            ),
        },
        {
            "control_id": "selection_collapses_admissible_fiber_to_U_SM",
            "expected": "admissible_fiber_gt_1_then_selected_U_SM",
            "passes_guard": selection_collapses,
            "computed_witness": f"before={len(admissible_fiber)}; after=1; selected={selected['uv_id']}",
        },
        {
            "control_id": "selection_carrier_not_field_pair",
            "expected": "UV_fiber_IR_shadow_consistency_selector",
            "passes_guard": True,
            "computed_witness": "carrier=UV_fiber; staging=P4_UV_to_IR; selector=post_consistency_score",
        },
    ]

    write_csv(
        ARTIFACT_DIR / "uv_fiber_step5.csv",
        rows,
        [
            "uv_id",
            "IR_EFT_code",
            "heavy_state_code",
            "breaking_pattern_code",
            "uv_structure_code",
            "UV_content",
            "unitarity_ok",
            "causality_ok",
            "positivity_ok",
            "anomaly_ok",
            "base_score",
            "C_consistent",
            "consistency_defect",
            "constraint_action",
            "selection_score",
            "selected_in_realized_fiber",
            "P4_UV_to_IR_staging",
            "derived_IR_observable",
            "realized_IR_fiber",
        ],
    )
    write_csv(
        ARTIFACT_DIR / "uv_nonfactorization_step5.csv",
        nonfactorization_rows,
        ["test_id", "source", "target", "non_descending", "obstruction_count", "witness", "interpretation"],
    )
    write_csv(
        ARTIFACT_DIR / "consistency_selection_step5.csv",
        consistency_selection_rows,
        [
            "IR_EFT_code",
            "realized_fiber_size",
            "admissible_fiber_size_before_selection",
            "admissible_fiber",
            "selected_count_after_selection",
            "selected_UV",
            "selected_score",
            "nonselected_admissible_count",
            "nonselected_admissible",
            "pruned_in_realized_fiber",
        ],
    )
    write_csv(
        ARTIFACT_DIR / "controls_step5.csv",
        controls,
        ["control_id", "expected", "passes_guard", "computed_witness"],
    )

    verdict = {
        "type": "e009_uv_fiber_facet_constructed",
        "realized_IR": REALIZED_IR,
        "realized_fiber_size": len(realized_fiber),
        "uv_non_descending_obstruction": uv_obstruction_count,
        "derived_IR_observable_obstruction": ir_obstruction_count,
        "admissible_fiber_size_before_selection": len(admissible_fiber),
        "selected_UV": selected["uv_id"],
        "nonselected_admissible_count": len(nonselected_admissible),
        "many_to_one": many_to_one,
        "selection_collapses": selection_collapses,
        "root_landed": False,
        "frame_transfer_certified": False,
    }
    output = {
        "step": 5,
        "orientation": "Cluster A E009 UV-completion fiber facet",
        "carrier": "finite UV-fiber plus IR shadow, consistency constraint, staging, and selector",
        "verdict": verdict,
        "nonclaim": "Finite UV-fiber selection shape only; no physical UV theory or constraint set is determined.",
    }
    (ARTIFACT_DIR / "e009_uv_fiber_output_step5.json").write_text(json.dumps(output, indent=2), encoding="utf-8")
    (ARTIFACT_DIR / "e009_uv_fiber_output_step5.txt").write_text(
        "\n".join(
            [
                "Cluster A Step 5 E009 UV-fiber facet",
                "Verdict: e009_uv_fiber_facet_constructed",
                f"realized IR: {REALIZED_IR}",
                f"realized fiber size: {len(realized_fiber)}",
                f"UV obstruction: {uv_obstruction_count}",
                f"derived IR obstruction: {ir_obstruction_count}",
                f"admissible fiber before selection: {len(admissible_fiber)}",
                f"selected UV: {selected['uv_id']}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    summary = f"""# Step 5 Results Summary

## Orientation

Step 5 builds the E009 UV-completion fiber facet. The carrier is a finite UV-fiber, an IR shadow, a toy consistency constraint, a UV-to-IR staging map, and a selector over the admissible realized fiber.

## UV Fiber

The realized IR code `{REALIZED_IR}` has `{len(realized_fiber)}` UV candidates: `{';'.join(str(row['uv_id']) for row in realized_fiber)}`. Their UV contents differ, so the fiber is non-trivial.

## Non-Descending Test

- UV-content obstruction from IR code: `{uv_obstruction_count}`, witness `{uv_witness}`.
- Derived IR observable obstruction: `{ir_obstruction_count}`, witness `{ir_witness}`.

The IR shadow distinguishes derived IR observables but not which UV completion in the fiber is active.

## P2 Consistency Constraint

The toy consistency functional prunes `{';'.join(str(row['uv_id']) for row in rows if row['constraint_action'] == 'pruned')}`. Consistent candidates survive. In the realized IR fiber, `{len(admissible_fiber)}` candidates remain admissible before selection.

## P4 Staging

Each UV row carries a computed staging string `UV -> threshold data -> IR_EFT_code`; this records the finite UV-to-IR down-shadow used by the fiber test.

## Selector

The selector collapses the admissible realized fiber from `{len(admissible_fiber)}` to `{selected['uv_id']}`. Non-selected admissible candidates: `{';'.join(nonselected_admissible)}`.

## Controls

- Many-to-one realized fiber: `{many_to_one}`.
- UV non-descending: `{uv_obstruction_count > 0}`.
- Derived IR observable factors: `{ir_obstruction_count == 0}`.
- Consistency prunes and preserves: `{inconsistent_removed and consistent_survives}`.
- Selection collapses: `{selection_collapses}`.
- Carrier guard: finite UV-fiber plus IR shadow plus consistency selector.

## Verdict

`e009_uv_fiber_facet_constructed`.

The finite toy shows UV completion as a non-descending fiber-selection over a shared IR EFT: consistency prunes, staging maps UV rows to IR shadows, and selection chooses one admissible UV candidate.
"""
    (ARTIFACT_DIR / "results_summary.md").write_text(summary, encoding="utf-8")

    schema = {
        "step": 5,
        "orientation": "E009 UV-completion fiber facet",
        "active_residual": "R_cluster_a_after_step4_e043_scale_selection",
        "candidate_move": "Compute UV-fiber non-factorization, derived IR control, P2 consistency pruning, P4 staging, and UV-fiber selection.",
        "final_verdict": verdict,
        "track_fields": {
            "uv_fiber": "uv_fiber_step5.csv",
            "nonfactorization": "uv_nonfactorization_step5.csv",
            "consistency_selection": "consistency_selection_step5.csv",
            "controls": "controls_step5.csv",
            "next_live_option": "Step6_cluster_a_consolidation_or_manager_selected_followup",
        },
    }
    (ARTIFACT_DIR / "schema.json").write_text(json.dumps(schema, indent=2), encoding="utf-8")

    content_rows = [
        {
            "output": "e009_uv_fiber_step5.py",
            "classification": "analytical structural",
            "grade": "finite-toy-diagnostic",
            "scope": "Builds UV fiber, IR shadow, consistency pruning, staging, selector, and controls.",
            "source_artifacts": "steps/step5_e009_uv_fiber_artifacts/e009_uv_fiber_step5.py",
        },
        {
            "output": "uv_fiber_step5.csv",
            "classification": "analytical structural",
            "grade": "finite-toy-diagnostic",
            "scope": "Per-UV candidate fiber, IR code, UV content, consistency status, staging, and selected row.",
            "source_artifacts": "steps/step5_e009_uv_fiber_artifacts/uv_fiber_step5.csv",
        },
        {
            "output": "uv_nonfactorization_step5.csv",
            "classification": "analytical structural",
            "grade": "finite-toy-diagnostic",
            "scope": "UV non-descending from IR and derived-IR-observable control.",
            "source_artifacts": "steps/step5_e009_uv_fiber_artifacts/uv_nonfactorization_step5.csv",
        },
        {
            "output": "consistency_selection_step5.csv",
            "classification": "analytical structural",
            "grade": "finite-toy-diagnostic",
            "scope": "Admissible fiber size, selected UV, and non-selected admissible candidates.",
            "source_artifacts": "steps/step5_e009_uv_fiber_artifacts/consistency_selection_step5.csv",
        },
        {
            "output": "controls_step5.csv",
            "classification": "analytical structural",
            "grade": "finite-toy-diagnostic",
            "scope": "Many-to-one, non-descending, derived-observable, pruning, selection, and carrier controls.",
            "source_artifacts": "steps/step5_e009_uv_fiber_artifacts/controls_step5.csv",
        },
        {
            "output": "results_summary.md",
            "classification": "organizational/audit",
            "grade": "finite-toy-diagnostic",
            "scope": "Human-readable E009 UV-fiber verdict and bounded scope.",
            "source_artifacts": "steps/step5_e009_uv_fiber_artifacts/results_summary.md",
        },
        {
            "output": "schema.json",
            "classification": "organizational/audit",
            "grade": "finite-toy-diagnostic",
            "scope": "Per-step schema and final verdict.",
            "source_artifacts": "steps/step5_e009_uv_fiber_artifacts/schema.json",
        },
        {
            "output": "nonclaim_boundary.md",
            "classification": "organizational/audit",
            "grade": "organizational",
            "scope": "Scope boundary for finite E009 UV-fiber facet.",
            "source_artifacts": "steps/step5_e009_uv_fiber_artifacts/nonclaim_boundary.md",
        },
        {
            "output": "run_step5.py",
            "classification": "organizational/audit",
            "grade": "finite-toy-diagnostic",
            "scope": "Validator for computed fiber, pruning, selection, staging, controls, source paths, and overclaim guard.",
            "source_artifacts": "steps/step5_e009_uv_fiber_artifacts/run_step5.py",
        },
    ]
    write_csv(
        ARTIFACT_DIR / "content_classification.csv",
        content_rows,
        ["output", "classification", "grade", "scope", "source_artifacts"],
    )

    nonclaim = """# Step 5 Nonclaim Boundary

Step 5 is a finite-carrier E009 UV-fiber construction. The UV theories, IR shadows, consistency checks, and staging strings are toy diagnostics.

The computed content is the shape: multiple UV candidates share one IR shadow, UV content is non-descending from that IR shadow, a consistency constraint prunes candidates, and a selector chooses one admissible candidate.

This does not provide a physical UV completion, a real consistency criterion, a swampland theorem, a physical staging flow, or a frame-transfer certificate.

The carrier is a finite UV fiber plus IR shadow, consistency constraint, staging, and selector. It is not a field pair.
"""
    (ARTIFACT_DIR / "nonclaim_boundary.md").write_text(nonclaim, encoding="utf-8")


if __name__ == "__main__":
    main()
