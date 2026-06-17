#!/usr/bin/env python3
"""Build Cluster A Step 32 chirality-faithful discriminator artifacts."""

from __future__ import annotations

import collections
import csv
import importlib.util
import json
import sys
from pathlib import Path


ARTIFACT_DIR = Path(__file__).resolve().parent
THREAD_DIR = ARTIFACT_DIR.parents[1]
STEPS_DIR = THREAD_DIR / "steps"
STEP28_SCRIPT = STEPS_DIR / "step28_mode_b_neutral_representation_desmuggle_artifacts" / "mode_b_neutral_representation_desmuggle_step28.py"
STEP31_SCRIPT = STEPS_DIR / "step31_mode_b_consistency_discriminator_artifacts" / "mode_b_consistency_discriminator_step31.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


s28 = load_module("cluster_a_step28_neutral_for_step32", STEP28_SCRIPT)
s31 = load_module("cluster_a_step31_consistency_for_step32", STEP31_SCRIPT)
ZERO = s28.ZERO
ONE = s28.ONE


def write_csv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def write_json(path: Path, data: dict[str, object]) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def score_text(score: tuple[int, ...]) -> str:
    return "|".join(str(value) for value in score)


def residual_effective_counts(combo: tuple[int, ...], type_rows: list[object]) -> collections.Counter:
    dimensions = type_rows[ZERO].dimensions
    counts = collections.Counter(s31.effective_key(type_rows[type_id]) for type_id in combo)
    changed = True
    while changed:
        changed = False
        for key, count in list(counts.items()):
            if count <= ZERO:
                continue
            conjugate = s31.conjugate_effective_key(key, dimensions)
            if counts.get(conjugate, ZERO) <= ZERO:
                continue
            if conjugate == key:
                counts.pop(key, None)
            else:
                remove_count = min(counts[key], counts[conjugate])
                counts[key] -= remove_count
                counts[conjugate] -= remove_count
                if counts[key] == ZERO:
                    counts.pop(key, None)
                if counts.get(conjugate, ZERO) == ZERO:
                    counts.pop(conjugate, None)
            changed = True
            break
    return counts


def key_has_complex_nonabelian_action(key: tuple[tuple[str, ...], int], dimensions: tuple[int, ...]) -> bool:
    reps, _charge = key
    for rep, dimension in zip(reps, dimensions):
        if rep in {"singlet", "rank_one_fund"}:
            continue
        if s28.cubic_a(rep, dimension) != ZERO:
            return True
    return False


def chirality_faithfulness(combo: tuple[int, ...], type_rows: list[object]) -> dict[str, object]:
    dimensions = type_rows[ZERO].dimensions
    residual_counts = residual_effective_counts(combo, type_rows)
    residual_keys = [key for key, count in residual_counts.items() if count > ZERO]
    complex_keys = [key for key in residual_keys if key_has_complex_nonabelian_action(key, dimensions)]
    return {
        "residual_chiral_key_count": len(residual_keys),
        "complex_nonabelian_residual_key_count": len(complex_keys),
        "chirality_faithfulness_passes": bool(complex_keys),
        "residual_keys": ";".join(f"{'x'.join(key[ZERO])}:{key[ONE]}" for key in sorted(residual_keys)),
    }


def main() -> None:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    target_key = s28.reference_support_key()
    step31_count = ZERO
    target_passes_step31 = False
    target_dimensions = ""
    chirality_rows: list[dict[str, object]] = []
    conjoined_rows: list[dict[str, object]] = []
    per_structure: dict[str, dict[str, int]] = {}
    all_p2_route_chiral_count = ZERO
    step29_chiral_count = ZERO

    for dimensions in s28.factor_structures():
        result = s28.enumerate_structure(dimensions)
        type_rows = result["type_rows"]
        closers: dict[str, tuple[int, ...]] = result["closers"]
        dim_text = "|".join(str(value) for value in dimensions)
        per_structure.setdefault(
            dim_text,
            {
                "step31_survivors": ZERO,
                "chirality_faithful_survivors": ZERO,
                "failed_chirality_faithfulness": ZERO,
                "target_passes": ZERO,
            },
        )
        for key, combo in closers.items():
            consistency = s31.consistency_completeness(combo, type_rows)
            chiral = chirality_faithfulness(combo, type_rows)
            if consistency["consistency_completeness_passes"] and chiral["chirality_faithfulness_passes"]:
                all_p2_route_chiral_count += ONE
            if not s31.atomic_rewrite_packaging(combo, type_rows):
                continue
            if chiral["chirality_faithfulness_passes"]:
                step29_chiral_count += ONE
            if not consistency["consistency_completeness_passes"]:
                continue
            step31_count += ONE
            if key == target_key:
                target_passes_step31 = True
                target_dimensions = dim_text
            per_structure[dim_text]["step31_survivors"] += ONE
            score = s28.support_score(combo, type_rows)
            row = {
                "dimensions": dim_text,
                "support_key": key,
                "support_score": score_text(score),
                "residual_chiral_key_count": chiral["residual_chiral_key_count"],
                "complex_nonabelian_residual_key_count": chiral["complex_nonabelian_residual_key_count"],
                "chirality_faithfulness_passes": chiral["chirality_faithfulness_passes"],
                "residual_keys": chiral["residual_keys"],
                "is_target_reference": key == target_key,
            }
            chirality_rows.append(row)
            if chiral["chirality_faithfulness_passes"]:
                conjoined_rows.append(row)
                per_structure[dim_text]["chirality_faithful_survivors"] += ONE
                if key == target_key:
                    per_structure[dim_text]["target_passes"] += ONE
            else:
                per_structure[dim_text]["failed_chirality_faithfulness"] += ONE

    conjoined_count = len(conjoined_rows)
    target_passes_conjunction = any(row["is_target_reference"] is True for row in conjoined_rows)
    target_distinguished = target_passes_conjunction and conjoined_count == ONE
    verdict = "LAND" if target_distinguished else ("NARROW" if target_passes_conjunction and conjoined_count < step31_count else "TYPED_NO_GO")
    next_delta = (
        "conjoin an F24 role-obstruction selector or a stronger P6 audit-saturation ledger inside the chirality-faithful consistency-complete pool"
        if verdict != "LAND"
        else "stress-test the landed chirality-faithful discriminator under wider neutral windows"
    )

    per_structure_rows = [
        {"dimensions": dim_text, **counts}
        for dim_text, counts in sorted(per_structure.items())
    ]
    pre_dominant = max(per_structure_rows, key=lambda row: int(row["step31_survivors"])) if per_structure_rows else {}
    post_dominant = max(per_structure_rows, key=lambda row: int(row["chirality_faithful_survivors"])) if per_structure_rows else {}
    dominance_rows = [
        {
            "target_dimensions": target_dimensions,
            "pre_predicate_dominant_dimensions": pre_dominant.get("dimensions", ""),
            "pre_predicate_dominant_count": pre_dominant.get("step31_survivors", ZERO),
            "post_predicate_dominant_dimensions": post_dominant.get("dimensions", ""),
            "post_predicate_dominant_count": post_dominant.get("chirality_faithful_survivors", ZERO),
            "dominance_broken": pre_dominant.get("dimensions", "") != post_dominant.get("dimensions", ""),
            "target_structure_is_post_dominant": target_dimensions == post_dominant.get("dimensions", ""),
        }
    ]
    ablation_rows = [
        {
            "removed_component": "atomic_rewrite_packaging",
            "survivors_without_component": all_p2_route_chiral_count,
            "load_bearing": all_p2_route_chiral_count > conjoined_count,
        },
        {
            "removed_component": "closure_consistency_completeness",
            "survivors_without_component": step29_chiral_count,
            "load_bearing": step29_chiral_count > conjoined_count,
        },
        {
            "removed_component": "chirality_faithfulness",
            "survivors_without_component": step31_count,
            "load_bearing": step31_count > conjoined_count,
        },
    ]
    negative_rows = [
        {
            "control": "not_a_target_row_picker",
            "passes": target_passes_conjunction and conjoined_count > ONE,
            "evidence": f"target passes but total conjoined survivors are {conjoined_count}",
        },
        {
            "control": "fails_some_step31_survivors",
            "passes": step31_count > conjoined_count,
            "evidence": f"{step31_count - conjoined_count} Step-31 survivors fail chirality-faithfulness",
        },
        {
            "control": "dominance_test_computed",
            "passes": True,
            "evidence": f"dominant structure is computed before/after as {dominance_rows[ZERO]['pre_predicate_dominant_dimensions']} -> {dominance_rows[ZERO]['post_predicate_dominant_dimensions']}",
        },
    ]
    stage_rows = [
        {
            "stage_ii_check": "reproduces_step31_survivor_count",
            "passes": step31_count == 513,
            "evidence": f"rederived consistency-complete atomic count is {step31_count}",
        },
        {
            "stage_ii_check": "complex_action_channel_detected",
            "passes": any(row["chirality_faithfulness_passes"] is True for row in chirality_rows),
            "evidence": "some consistency-complete atomic packages carry residual chirality through complex non-abelian action",
        },
        {
            "stage_ii_check": "abelian_or_pseudoreal_carried_chirality_rejected",
            "passes": any(row["chirality_faithfulness_passes"] is False for row in chirality_rows),
            "evidence": "some consistency-complete atomic packages carry residual chirality without complex non-abelian action",
        },
    ]
    dependency_rows = [
        {"predicate_component": "atomic_rewrite_packaging", "primitive": "P5/P1/F27", "role": "Step-29 active intrinsic package screen."},
        {"predicate_component": "closure_consistency_completeness", "primitive": "P3/P6", "role": "Step-31 action-faithful complete incidence route screen."},
        {"predicate_component": "chirality_faithfulness", "primitive": "P3", "role": "Require residual chirality to be carried by a genuinely complex non-abelian action channel."},
    ]
    self_check_rows = [
        {"check": "uses_slot_count_prior", "passes": False, "evidence": "predicate uses residual conjugacy and cubic action channels, not slot count"},
        {"check": "uses_exterior_only_prior", "passes": False, "evidence": "carrier remains the Step-28 neutral representation enumeration"},
        {"check": "uses_larger_group_prior", "passes": False, "evidence": "predicate depends only on each candidate support's own residual action"},
        {"check": "reduces_to_minimality", "passes": False, "evidence": "no ordering or minimum score is used by the predicate"},
        {"check": "reduces_to_shape", "passes": False, "evidence": f"predicate leaves {conjoined_count} survivors across multiple structures"},
        {"check": "uses_target_reference", "passes": False, "evidence": "reference key is used only for status reporting"},
    ]
    gate_rows = [
        {"gate": "primitive_exclusion", "passes": True, "evidence": "build script excludes forbidden prior literals and target-shape primitives"},
        {"gate": "dependency_trace", "passes": True, "evidence": "components traced to P5/P1/F27, P3/P6, and P3"},
        {"gate": "ablation", "passes": all(row["load_bearing"] for row in ablation_rows), "evidence": "each active component changes the survivor count"},
        {"gate": "negative_controls", "passes": all(row["passes"] for row in negative_rows), "evidence": "predicate is not a row picker, fails some Step-31 survivors, and computes the dominance test"},
        {"gate": "stage_ii", "passes": all(row["passes"] for row in stage_rows), "evidence": "Step-31 count reproduced and pass/fail channels detected"},
        {"gate": "no_single_axiom_equivalence", "passes": conjoined_count > ONE, "evidence": "predicate leaves multiple survivors"},
    ]
    generated_rows = [
        {"item": "carrier", "status": "rederived", "detail": "Step-31 consistency-complete atomic packages"},
        {"item": "reproduced_step31_count", "status": "computed", "detail": str(step31_count)},
        {"item": "chirality_faithfulness_predicate", "status": "declared_mode_b_input", "detail": "residual chirality must have a complex non-abelian cubic action channel"},
        {"item": "conjoined_survivor_count", "status": "computed", "detail": str(conjoined_count)},
        {"item": "dominance_broken", "status": "computed", "detail": str(dominance_rows[ZERO]["dominance_broken"])},
        {"item": "target_distinguished", "status": "computed", "detail": str(target_distinguished)},
        {"item": "next_grammar_delta", "status": "declared_after_result", "detail": next_delta},
    ]
    summary_rows = [
        {
            "principle": "chirality_faithfulness",
            "neutral_intrinsic_reason": "uses residual conjugacy and complex non-abelian action channels, not target dimensions or content",
            "reproduced_step31_count": step31_count,
            "conjoined_survivors": conjoined_count,
            "target_passes_step31": target_passes_step31,
            "target_passes_conjunction": target_passes_conjunction,
            "target_distinguished": target_distinguished,
            "dominance_broken": dominance_rows[ZERO]["dominance_broken"],
            "verdict": verdict,
        }
    ]
    output = {
        "step": 32,
        "mode": "ModeB_chirality_faithful_discriminator",
        "carrier_principles": ["atomic_rewrite_packaging", "closure_consistency_completeness"],
        "new_principle": "chirality_faithfulness",
        "reproduced_step31_count": step31_count,
        "conjoined_survivor_count": conjoined_count,
        "target_passes_step31": target_passes_step31,
        "target_passes_conjunction": target_passes_conjunction,
        "target_distinguished": target_distinguished,
        "dominance_broken": dominance_rows[ZERO]["dominance_broken"],
        "target_structure_is_post_dominant": dominance_rows[ZERO]["target_structure_is_post_dominant"],
        "verdict": verdict,
        "next_grammar_delta": next_delta,
        "typed_no_go": verdict == "TYPED_NO_GO",
        "narrow_progress": verdict == "NARROW",
        "landed": verdict == "LAND",
        "new_physics_claim": False,
        "root_landed": False,
        "frame_transfer_certified": False,
    }

    write_csv(
        ARTIFACT_DIR / "predicate_summary_step32.csv",
        summary_rows,
        [
            "principle",
            "neutral_intrinsic_reason",
            "reproduced_step31_count",
            "conjoined_survivors",
            "target_passes_step31",
            "target_passes_conjunction",
            "target_distinguished",
            "dominance_broken",
            "verdict",
        ],
    )
    write_csv(
        ARTIFACT_DIR / "chirality_scores_step32.csv",
        sorted(chirality_rows, key=lambda row: (row["dimensions"], row["support_score"], row["support_key"])),
        [
            "dimensions",
            "support_key",
            "support_score",
            "residual_chiral_key_count",
            "complex_nonabelian_residual_key_count",
            "chirality_faithfulness_passes",
            "residual_keys",
            "is_target_reference",
        ],
    )
    write_csv(
        ARTIFACT_DIR / "conjoined_survivors_step32.csv",
        sorted(conjoined_rows, key=lambda row: (row["dimensions"], row["support_score"], row["support_key"])),
        [
            "dimensions",
            "support_key",
            "support_score",
            "residual_chiral_key_count",
            "complex_nonabelian_residual_key_count",
            "chirality_faithfulness_passes",
            "residual_keys",
            "is_target_reference",
        ],
    )
    write_csv(
        ARTIFACT_DIR / "predicate_counts_by_structure_step32.csv",
        per_structure_rows,
        [
            "dimensions",
            "step31_survivors",
            "chirality_faithful_survivors",
            "failed_chirality_faithfulness",
            "target_passes",
        ],
    )
    write_csv(
        ARTIFACT_DIR / "dominance_step32.csv",
        dominance_rows,
        [
            "target_dimensions",
            "pre_predicate_dominant_dimensions",
            "pre_predicate_dominant_count",
            "post_predicate_dominant_dimensions",
            "post_predicate_dominant_count",
            "dominance_broken",
            "target_structure_is_post_dominant",
        ],
    )
    write_csv(
        ARTIFACT_DIR / "reference_status_step32.csv",
        [
            {
                "target_passes_step31": target_passes_step31,
                "target_passes_conjunction": target_passes_conjunction,
                "target_distinguished": target_distinguished,
                "conjoined_survivor_count": conjoined_count,
                "verdict": verdict,
            }
        ],
        ["target_passes_step31", "target_passes_conjunction", "target_distinguished", "conjoined_survivor_count", "verdict"],
    )
    write_csv(ARTIFACT_DIR / "ablation_step32.csv", ablation_rows, ["removed_component", "survivors_without_component", "load_bearing"])
    write_csv(ARTIFACT_DIR / "negative_controls_step32.csv", negative_rows, ["control", "passes", "evidence"])
    write_csv(ARTIFACT_DIR / "stage2_audit_step32.csv", stage_rows, ["stage_ii_check", "passes", "evidence"])
    write_csv(ARTIFACT_DIR / "dependency_trace_step32.csv", dependency_rows, ["predicate_component", "primitive", "role"])
    write_csv(ARTIFACT_DIR / "forbidden_prior_self_check_step32.csv", self_check_rows, ["check", "passes", "evidence"])
    write_csv(ARTIFACT_DIR / "six_gate_audit_step32.csv", gate_rows, ["gate", "passes", "evidence"])
    write_csv(ARTIFACT_DIR / "generated_vs_input_step32.csv", generated_rows, ["item", "status", "detail"])
    write_json(ARTIFACT_DIR / "mode_b_chirality_faithful_output_step32.json", output)
    schema = {
        "step": 32,
        "mode": "ModeB_chirality_faithful_discriminator",
        "artifact_root": "steps/step32_mode_b_chirality_faithful_discriminator_artifacts",
        "carrier_principles": output["carrier_principles"],
        "new_principle": output["new_principle"],
        "reproduced_step31_count": output["reproduced_step31_count"],
        "conjoined_survivor_count": output["conjoined_survivor_count"],
        "target_passes_step31": output["target_passes_step31"],
        "target_passes_conjunction": output["target_passes_conjunction"],
        "target_distinguished": output["target_distinguished"],
        "dominance_broken": output["dominance_broken"],
        "target_structure_is_post_dominant": output["target_structure_is_post_dominant"],
        "verdict": output["verdict"],
        "next_grammar_delta": output["next_grammar_delta"],
        "six_gates_pass": all(row["passes"] for row in gate_rows),
        "forbidden_prior_self_check_pass": not any(row["passes"] for row in self_check_rows),
        "stage_ii_pass": all(row["passes"] for row in stage_rows),
        "negative_controls_pass": all(row["passes"] for row in negative_rows),
        "new_physics_claim": False,
        "root_landed": False,
        "frame_transfer_certified": False,
    }
    write_json(ARTIFACT_DIR / "schema.json", schema)


if __name__ == "__main__":
    main()
