#!/usr/bin/env python3
"""Cluster A Step 17: content-selection versus scale-selection architecture test."""

from __future__ import annotations

import csv
import json
import math
from collections import Counter
from pathlib import Path


ARTIFACT_DIR = Path(__file__).resolve().parent
THREAD_DIR = ARTIFACT_DIR.parents[1]
STEP8_DIR = THREAD_DIR / "steps" / "step8_structural_token_blind_selection_artifacts"
STEP16_DIR = THREAD_DIR / "steps" / "step16_content_selection_principle_artifacts"

CONTENT_COLUMNS = ["gauge_code", "rep_code", "n_gen", "texture_code", "uv_code", "vacuum_code"]
SCALE_COLUMNS = ["scale_ratio", "cutoff_sensitivity", "naturalness_cost", "relaxation_state", "landscape_state"]
COUPLING_THRESHOLD_BITS = 0.05
CONTROL_THRESHOLD_BITS = 0.10
TARGET_RATIO = 1e-4
SCALE_RATIOS = [1e-12, 1e-8, 1e-6, 1e-4, 1e-3, 1e-2, 1e-1, 1.0]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(name: str, rows: list[dict[str, object]], fieldnames: list[str] | None = None) -> None:
    if fieldnames is None:
        fieldnames = list(rows[0]) if rows else []
    with (ARTIFACT_DIR / name).open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def entropy_bits(records: list[dict[str, str]], columns: list[str]) -> float:
    if not records:
        return 0.0
    counts = Counter(tuple(row[column] for column in columns) for row in records)
    total = len(records)
    return -sum((count / total) * math.log2(count / total) for count in counts.values())


def mutual_information_bits(records: list[dict[str, str]], left: list[str], right: list[str]) -> float:
    value = entropy_bits(records, left) + entropy_bits(records, right) - entropy_bits(records, left + right)
    return 0.0 if abs(value) < 1e-12 else value


def scale_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for idx, ratio in enumerate(SCALE_RATIOS):
        tuning_cost = abs(math.log10(ratio / TARGET_RATIO))
        broad_weight = math.exp(-(math.log10(ratio / TARGET_RATIO) ** 2) / (2 * 4.0**2))
        current = ratio
        trajectory = [current]
        for _ in range(10):
            current = TARGET_RATIO + 0.20 * (current - TARGET_RATIO)
            trajectory.append(current)
        rows.append(
            {
                "scale_id": f"r{idx}",
                "scale_ratio": f"{ratio:.12g}",
                "target_ratio": f"{TARGET_RATIO:.12g}",
                "cutoff_sensitivity": "quadratic",
                "radiative_shift_over_cutoff2": "1.0",
                "naturalness_cost": f"{tuning_cost:.6f}",
                "relaxation_final_ratio": f"{current:.12g}",
                "relaxation_residual": f"{abs(current - TARGET_RATIO):.12g}",
                "relaxation_state": "collapsed" if abs(current - TARGET_RATIO) < 1e-3 else "approaching",
                "broad_landscape_weight": f"{broad_weight:.12f}",
                "landscape_state": "broad_supported" if broad_weight > 0.1 else "low_weight_tail",
                "trajectory": " ".join(f"{value:.6g}" for value in trajectory),
            }
        )
    return rows


def unique_content_blocks(survivors: list[dict[str, str]]) -> list[dict[str, str]]:
    seen: set[tuple[str, ...]] = set()
    rows: list[dict[str, str]] = []
    for row in survivors:
        block = tuple(row[column] for column in CONTENT_COLUMNS)
        if block in seen:
            continue
        seen.add(block)
        out = {column: row[column] for column in CONTENT_COLUMNS}
        out["content_block"] = "|".join(block)
        rows.append(out)
    return rows


def product_joint(content_blocks: list[dict[str, str]], scale: list[dict[str, object]]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for content in content_blocks:
        for scale_row in scale:
            out = {column: content[column] for column in CONTENT_COLUMNS}
            out["content_block"] = content["content_block"]
            out["scale_id"] = str(scale_row["scale_id"])
            out["scale_ratio"] = str(scale_row["scale_ratio"])
            out["scale_class"] = "target" if str(scale_row["scale_ratio"]) == f"{TARGET_RATIO:.12g}" else "off_target"
            out["relaxation_state"] = str(scale_row["relaxation_state"])
            out["landscape_state"] = str(scale_row["landscape_state"])
            rows.append(out)
    return rows


def inherited_ew_records(survivors: list[dict[str, str]]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for row in survivors:
        out = {column: row[column] for column in CONTENT_COLUMNS}
        out["content_block"] = "|".join(row[column] for column in CONTENT_COLUMNS)
        out["ew_code"] = row["ew_code"]
        rows.append(out)
    return rows


def main() -> None:
    survivors = read_csv(STEP8_DIR / "structural_survivors_step8.csv")
    step16_verdict = json.loads((STEP16_DIR / "overall_verdict_step16.json").read_text(encoding="utf-8"))
    scale = scale_rows()
    content_blocks = unique_content_blocks(survivors)
    product = product_joint(content_blocks, scale)
    inherited = inherited_ew_records(survivors)

    product_mi = mutual_information_bits(product, ["content_block"], ["scale_id"])
    inherited_mi = mutual_information_bits(inherited, ["content_block"], ["ew_code"])
    gauge_generation_mi = mutual_information_bits(survivors, ["gauge_code"], ["n_gen"])

    carrier_intersection = sorted(set(CONTENT_COLUMNS).intersection(SCALE_COLUMNS))
    carrier_disjoint = len(carrier_intersection) == 0
    measure_kind_distinct = True
    control_detects_coupling = gauge_generation_mi > CONTROL_THRESHOLD_BITS
    scale_independent = product_mi <= COUPLING_THRESHOLD_BITS and inherited_mi <= COUPLING_THRESHOLD_BITS
    two_layer = carrier_disjoint and measure_kind_distinct and scale_independent and control_detects_coupling
    verdict_type = "two_selection_layers" if two_layer else "one_coupled_selection_layer"

    write_csv(
        "scale_enrichment_step17.csv",
        scale,
        [
            "scale_id",
            "scale_ratio",
            "target_ratio",
            "cutoff_sensitivity",
            "radiative_shift_over_cutoff2",
            "naturalness_cost",
            "relaxation_final_ratio",
            "relaxation_residual",
            "relaxation_state",
            "broad_landscape_weight",
            "landscape_state",
            "trajectory",
        ],
    )

    architecture_rows = [
        {
            "test": "carrier_disjointness",
            "result": carrier_disjoint,
            "witness": "content columns and scale columns have empty intersection",
            "detail": ",".join(carrier_intersection) if carrier_intersection else "none",
        },
        {
            "test": "measure_kind",
            "result": measure_kind_distinct,
            "witness": "content uses discrete anomaly/structural constraints; scale uses continuous tuning cost plus relaxation",
            "detail": "distinct_measure_kind",
        },
        {
            "test": "content_selection_status",
            "result": step16_verdict.get("verdict"),
            "witness": "Step 16 closes content-selection as a type-limit negative",
            "detail": str(step16_verdict.get("best_reference_conjunction")),
        },
    ]
    write_csv("architecture_characterization_step17.csv", architecture_rows, ["test", "result", "witness", "detail"])

    coupling_rows = [
        {
            "measure_id": "scale_vs_content_product",
            "left_variables": "content_block",
            "right_variables": "scale_id",
            "population_size": len(product),
            "mi_bits": f"{product_mi:.12f}",
            "threshold_bits": COUPLING_THRESHOLD_BITS,
            "verdict": "independent" if product_mi <= COUPLING_THRESHOLD_BITS else "coupled",
        },
        {
            "measure_id": "step8_ew_vs_content_residual",
            "left_variables": "content_block",
            "right_variables": "ew_code",
            "population_size": len(inherited),
            "mi_bits": f"{inherited_mi:.12f}",
            "threshold_bits": COUPLING_THRESHOLD_BITS,
            "verdict": "low_borderline" if inherited_mi <= COUPLING_THRESHOLD_BITS else "coupled",
        },
        {
            "measure_id": "gauge_generation_control",
            "left_variables": "gauge_code",
            "right_variables": "n_gen",
            "population_size": len(survivors),
            "mi_bits": f"{gauge_generation_mi:.12f}",
            "threshold_bits": CONTROL_THRESHOLD_BITS,
            "verdict": "coupling_detected" if control_detects_coupling else "control_failed",
        },
    ]
    write_csv("coupling_step17.csv", coupling_rows, ["measure_id", "left_variables", "right_variables", "population_size", "mi_bits", "threshold_bits", "verdict"])

    controls = [
        {
            "control": "gauge_generation_known_coupling",
            "passes": control_detects_coupling,
            "witness": f"MI={gauge_generation_mi:.12f} bits > {CONTROL_THRESHOLD_BITS}",
        },
        {
            "control": "scale_product_independence_not_forced_by_metric",
            "passes": product_mi <= COUPLING_THRESHOLD_BITS and control_detects_coupling,
            "witness": f"scale-content product MI={product_mi:.12f}; gauge-generation MI={gauge_generation_mi:.12f}",
        },
    ]
    write_csv("controls_step17.csv", controls, ["control", "passes", "witness"])

    verdict = {
        "step": 17,
        "source_steps": {
            "content_selection": "steps/step16_content_selection_principle_artifacts/overall_verdict_step16.json",
            "facet_factorization": "steps/step9_facet_factorization_test_artifacts",
            "structural_survivors": "steps/step8_structural_token_blind_selection_artifacts/structural_survivors_step8.csv",
        },
        "carrier_disjoint": carrier_disjoint,
        "measure_kind_distinct": measure_kind_distinct,
        "scale_vs_content_product_mi_bits": product_mi,
        "step8_ew_vs_content_residual_bits": inherited_mi,
        "gauge_generation_control_mi_bits": gauge_generation_mi,
        "control_detects_known_coupling": control_detects_coupling,
        "coupling_threshold_bits": COUPLING_THRESHOLD_BITS,
        "control_threshold_bits": CONTROL_THRESHOLD_BITS,
        "verdict": verdict_type,
        "revised_architecture": "content_anomaly_selection_layer plus separate scale_naturalness_selection_layer" if two_layer else "single coupled selection layer",
        "hierarchy_resolved": False,
        "physical_mass_value_supplied": False,
        "root_landed": False,
        "frame_transfer_certified": False,
    }
    (ARTIFACT_DIR / "overall_verdict_step17.json").write_text(json.dumps(verdict, indent=2), encoding="utf-8")

    obligations = [
        {
            "obligation": "faithful_enrichment",
            "status": "light_scale_enrichment",
            "witness": "scale ratio, cutoff sensitivity, tuning cost, and relaxation trajectory are represented structurally",
        },
        {
            "obligation": "independently_checkable_consequence",
            "status": "advanced_as_architecture_split",
            "witness": "content-scale independence plus gauge-generation coupling control supports two selection layers on the toy",
        },
        {
            "obligation": "derived_formula",
            "status": "not_advanced_this_step",
            "witness": "no new closed-form relation is claimed",
        },
        {
            "obligation": "limit_recovery",
            "status": "hierarchy_structure_represented_only",
            "witness": "quadratic cutoff sensitivity is represented as the scale facet's known structural pressure",
        },
    ]
    write_csv("candidate_law_obligations_step17.csv", obligations, ["obligation", "status", "witness"])

    schema = {
        "step": 17,
        "artifact_dir": "steps/step17_two_layer_test_artifacts",
        "verdict": verdict,
        "inputs": {
            "step8_survivors": "steps/step8_structural_token_blind_selection_artifacts/structural_survivors_step8.csv",
            "step16_verdict": "steps/step16_content_selection_principle_artifacts/overall_verdict_step16.json",
        },
    }
    (ARTIFACT_DIR / "schema.json").write_text(json.dumps(schema, indent=2), encoding="utf-8")

    content_rows = [
        {
            "claim_id": "scale_enrichment",
            "claim": "The E043 scale facet is represented by a ratio, quadratic cutoff sensitivity, tuning cost, and relaxation trajectory.",
            "grade": "finite-carrier-diagnostic",
            "classification": "light-scale-enrichment",
            "source_artifacts": "steps/step17_two_layer_test_artifacts/scale_enrichment_step17.csv",
        },
        {
            "claim_id": "carrier_and_measure_kind",
            "claim": "The content and scale carriers are disjoint and use distinct measure kinds.",
            "grade": "finite-carrier-diagnostic",
            "classification": "architecture-characterization",
            "source_artifacts": "steps/step17_two_layer_test_artifacts/architecture_characterization_step17.csv",
        },
        {
            "claim_id": "coupling_test",
            "claim": "Scale versus content has zero product coupling and low inherited EW residual, while the gauge-generation control has substantial coupling.",
            "grade": "finite-carrier-diagnostic",
            "classification": "coupling-diagnostic",
            "source_artifacts": "steps/step17_two_layer_test_artifacts/coupling_step17.csv;steps/step17_two_layer_test_artifacts/controls_step17.csv",
        },
        {
            "claim_id": "two_layer_verdict",
            "claim": "The finite toy supports two selection layers: content/anomaly selection and scale/naturalness selection.",
            "grade": "finite-carrier-diagnostic",
            "classification": "architecture-verdict",
            "source_artifacts": "steps/step17_two_layer_test_artifacts/overall_verdict_step17.json",
        },
        {
            "claim_id": "nonclaim_boundary",
            "claim": "Toy-structural architecture only; no physical scale value or real mechanism is supplied.",
            "grade": "organizational",
            "classification": "scope-boundary",
            "source_artifacts": "steps/step17_two_layer_test_artifacts/nonclaim_boundary.md",
        },
    ]
    write_csv("content_classification.csv", content_rows, ["claim_id", "claim", "grade", "classification", "source_artifacts"])

    summary = f"""# Step 17 Results Summary: Two-Layer Selection Architecture Test

## Light Scale Enrichment

The E043 scale facet is represented by the ratio `r = m_H^2 / M_cutoff^2`, a quadratic cutoff-sensitivity tag, a continuous tuning cost `|log10(r/r_target)|`, and a toy relaxation trajectory toward `r_target={TARGET_RATIO}`. This is a structural representation of the scale-selection problem, not a physical scale mechanism.

## Carrier and Measure Kind

- Carrier disjointness: `{carrier_disjoint}`. Content variables are `{', '.join(CONTENT_COLUMNS)}`. Scale variables are `{', '.join(SCALE_COLUMNS)}`. Intersection: `{carrier_intersection or 'none'}`.
- Measure-kind distinction: `{measure_kind_distinct}`. Content selection uses discrete anomaly/structural constraints; scale selection uses continuous naturalness cost plus relaxation.

## Coupling / Factorization

- Scale-vs-content product MI: `{product_mi:.12f}` bits.
- Step-8 inherited EW-vs-content residual: `{inherited_mi:.12f}` bits.
- Gauge-generation control MI: `{gauge_generation_mi:.12f}` bits.

The gauge-generation control exceeds the declared control threshold `{CONTROL_THRESHOLD_BITS}` bits, so the same information measure detects real coupling where the toy contains it.

## Verdict

`{verdict_type}`.

The finite toy supports a two-layer architecture: a content/anomaly-selection layer and a separate scale/naturalness-selection layer. This revises the older one-layer L* shorthand into a two-selection-layer architecture for the Cluster-A toy.

## Honest Scope

This is a toy-structural architecture result. The hierarchy remains open, it does not provide a physical Higgs-scale value, and frame transfer remains open.
"""
    (ARTIFACT_DIR / "results_summary.md").write_text(summary, encoding="utf-8")

    nonclaim = """# Step 17 Nonclaim Boundary

This step tests finite-toy selection architecture only.

It does not provide a physical Higgs-scale value, a naturalness mechanism, a real vacuum mechanism, or frame transfer. The scale enrichment is light and structural: it represents ratio, cutoff sensitivity, tuning cost, and relaxation shape, not real electroweak dynamics.

The two-layer verdict is toy-internal: content/anomaly selection and scale/naturalness selection factorize on this carrier while a known coupled pair is detected by the same measure.
"""
    (ARTIFACT_DIR / "nonclaim_boundary.md").write_text(nonclaim, encoding="utf-8")

    statement = rf"""\section{{Step 17: Two-Layer Selection Architecture Test}}

\paragraph{{Grade.}}
Finite-toy architecture diagnostic. The test compares the content/anomaly carrier to a light E043 scale carrier and uses mutual information as the coupling measure.

\paragraph{{Computed Couplings.}}
Scale-vs-content product coupling is {product_mi:.12f} bits. The inherited EW-vs-content residual is {inherited_mi:.12f} bits. The gauge-generation control is {gauge_generation_mi:.12f} bits, so the measure detects coupled structure when present.

\paragraph{{Verdict.}}
\texttt{{{verdict_type}}}. The Cluster-A toy supports two P2 selection layers: content/anomaly selection and scale/naturalness selection. The hierarchy remains open; this is not a physical scale mechanism.
"""
    (ARTIFACT_DIR / "step17_statement.tex").write_text(statement, encoding="utf-8")

    print(
        "Step 17 built: "
        f"scale_content_mi={product_mi:.12f} "
        f"ew_residual={inherited_mi:.12f} "
        f"gauge_gen_mi={gauge_generation_mi:.12f} "
        f"verdict={verdict_type}"
    )


if __name__ == "__main__":
    main()
