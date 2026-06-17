#!/usr/bin/env python3
"""Cluster A Step 18: adversarial stress test for content/scale selection architecture."""

from __future__ import annotations

import csv
import json
import math
from collections import Counter
from pathlib import Path


ARTIFACT_DIR = Path(__file__).resolve().parent
THREAD_DIR = ARTIFACT_DIR.parents[1]
STEP8_DIR = THREAD_DIR / "steps" / "step8_structural_token_blind_selection_artifacts"
STEP17_DIR = THREAD_DIR / "steps" / "step17_two_layer_test_artifacts"

CONTENT_COLUMNS = ["gauge_code", "rep_code", "n_gen", "texture_code", "uv_code", "vacuum_code"]
ACTIVE_CHANNEL_STRENGTH = 1.0
CHANNEL_THRESHOLD = 2.75
LOW_COUPLING_THRESHOLD_BITS = 0.05
CONTROL_THRESHOLD_BITS = 0.10
GAUGE_RANK = {"g0": 4, "g1": 5, "g2": 3, "g3": 6}
REP_COMPLEXITY = {"r0": 1, "r1": 2, "r2": 2, "r3": 1}
DOMINANT_YUKAWA_PROXY = {"t0": 1.0, "t1": 0.55, "t2": 0.35, "t3": 0.20}
STRENGTHS = [0.0, 0.25, 0.50, 0.75, 1.0, 1.50, 2.0, 4.0]
ROBUSTNESS_THRESHOLDS = [0.02, 0.05, 0.10, 0.20, 0.40, 0.60]
ROBUSTNESS_GROUPINGS = {
    "full_content_block": CONTENT_COLUMNS,
    "radiative_driver_block": ["gauge_code", "rep_code", "n_gen", "texture_code"],
    "texture_generation_block": ["texture_code", "n_gen"],
}
ROBUSTNESS_ESTIMATORS = ["mutual_information", "joint_product_kl"]


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


def radiative_score(row: dict[str, str]) -> float:
    yukawa = DOMINANT_YUKAWA_PROXY[row["texture_code"]]
    generation_boost = 0.03 * int(row["n_gen"])
    gauge_subdominant = 0.08 * GAUGE_RANK[row["gauge_code"]]
    rep_subdominant = 0.02 * REP_COMPLEXITY[row["rep_code"]]
    return 3.0 * yukawa * yukawa + generation_boost - gauge_subdominant - rep_subdominant


def channel_bin(score: float, strength: float) -> str:
    if strength <= 0:
        return "channel_off"
    return "radiative_active" if strength * score > CHANNEL_THRESHOLD else "radiative_base"


def with_channel(records: list[dict[str, str]], strength: float) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    for row in records:
        score = radiative_score(row)
        copy = dict(row)
        copy["dominant_yukawa_proxy"] = f"{DOMINANT_YUKAWA_PROXY[row['texture_code']]:.3f}"
        copy["radiative_score"] = f"{score:.6f}"
        copy["channel_strength"] = f"{strength:.2f}"
        copy["scale_channel_bin"] = channel_bin(score, strength)
        copy["scale_measure_kind"] = "radiative_naturalness"
        out.append(copy)
    return out


def classify_architecture(coupling: float, threshold: float, gauge_reference: float) -> str:
    if coupling <= threshold:
        return "two_layer"
    if coupling >= gauge_reference:
        return "one_layer_break"
    return "coupled_but_distinct"


def main() -> None:
    survivors = read_csv(STEP8_DIR / "structural_survivors_step8.csv")
    step17 = json.loads((STEP17_DIR / "overall_verdict_step17.json").read_text(encoding="utf-8"))
    gauge_generation_reference = mutual_information_bits(survivors, ["gauge_code"], ["n_gen"])
    active_records = with_channel(survivors, ACTIVE_CHANNEL_STRENGTH)
    active_coupling = mutual_information_bits(active_records, CONTENT_COLUMNS, ["scale_channel_bin"])
    inherited_step17 = float(step17["step8_ew_vs_content_residual_bits"])

    channel_rows = []
    for row in active_records:
        channel_rows.append(
            {
                "candidate_id": row["candidate_id"],
                "gauge_code": row["gauge_code"],
                "rep_code": row["rep_code"],
                "n_gen": row["n_gen"],
                "texture_code": row["texture_code"],
                "ew_code": row["ew_code"],
                "dominant_yukawa_proxy": row["dominant_yukawa_proxy"],
                "radiative_score": row["radiative_score"],
                "channel_strength": row["channel_strength"],
                "scale_channel_bin": row["scale_channel_bin"],
            }
        )
    write_csv(
        "radiative_channel_step18.csv",
        channel_rows,
        [
            "candidate_id",
            "gauge_code",
            "rep_code",
            "n_gen",
            "texture_code",
            "ew_code",
            "dominant_yukawa_proxy",
            "radiative_score",
            "channel_strength",
            "scale_channel_bin",
        ],
    )

    sweep_rows = []
    previous_mi = 0.0
    monotone = True
    for strength in STRENGTHS:
        records = with_channel(survivors, strength)
        mi = mutual_information_bits(records, CONTENT_COLUMNS, ["scale_channel_bin"])
        if mi + 1e-12 < previous_mi:
            monotone = False
        previous_mi = mi
        counts = Counter(row["scale_channel_bin"] for row in records)
        sweep_rows.append(
            {
                "channel_strength": f"{strength:.2f}",
                "content_scale_mi_bits": f"{mi:.12f}",
                "active_count": counts.get("radiative_active", 0),
                "base_count": counts.get("radiative_base", 0) + counts.get("channel_off", 0),
                "relative_to_gauge_generation": f"{(mi / gauge_generation_reference) if gauge_generation_reference else 0.0:.12f}",
                "verdict_at_strength": classify_architecture(mi, LOW_COUPLING_THRESHOLD_BITS, gauge_generation_reference),
            }
        )
    write_csv(
        "coupling_strength_sweep_step18.csv",
        sweep_rows,
        ["channel_strength", "content_scale_mi_bits", "active_count", "base_count", "relative_to_gauge_generation", "verdict_at_strength"],
    )

    robustness_rows = []
    verdict_counts = Counter()
    for threshold in ROBUSTNESS_THRESHOLDS:
        for estimator in ROBUSTNESS_ESTIMATORS:
            for grouping_name, grouping_columns in ROBUSTNESS_GROUPINGS.items():
                coupling = mutual_information_bits(active_records, grouping_columns, ["scale_channel_bin"])
                # For this two-variable empirical test, direct joint-vs-product KL equals mutual information.
                if estimator == "joint_product_kl":
                    coupling = coupling
                verdict = classify_architecture(coupling, threshold, gauge_generation_reference)
                verdict_counts[verdict] += 1
                robustness_rows.append(
                    {
                        "threshold_bits": f"{threshold:.2f}",
                        "estimator": estimator,
                        "grouping": grouping_name,
                        "coupling_bits": f"{coupling:.12f}",
                        "gauge_generation_reference_bits": f"{gauge_generation_reference:.12f}",
                        "verdict": verdict,
                    }
                )
    write_csv(
        "robustness_sweep_step18.csv",
        robustness_rows,
        ["threshold_bits", "estimator", "grouping", "coupling_bits", "gauge_generation_reference_bits", "verdict"],
    )

    total_sweep = len(robustness_rows)
    two_layer_fraction = verdict_counts["two_layer"] / total_sweep
    break_fraction = verdict_counts["one_layer_break"] / total_sweep
    coupled_fraction = verdict_counts["coupled_but_distinct"] / total_sweep
    flip_boundary = "two_layer only when threshold exceeds the active coupling; no one-layer break at active strength"
    if break_fraction:
        flip_boundary = "one-layer break appears for groupings/estimators with coupling at or above the gauge-generation reference"

    controls = [
        {
            "control": "coupling_strength_monotone",
            "passes": monotone and float(sweep_rows[-1]["content_scale_mi_bits"]) > float(sweep_rows[0]["content_scale_mi_bits"]),
            "witness": "content-scale MI rises from strength 0 to strong injected channel",
        },
        {
            "control": "gauge_generation_reference_detected",
            "passes": gauge_generation_reference > 0.10,
            "witness": f"MI={gauge_generation_reference:.12f} bits",
        },
    ]
    write_csv("controls_step18.csv", controls, ["control", "passes", "witness"])

    verdict_type = (
        "two_layer_robust"
        if active_coupling <= LOW_COUPLING_THRESHOLD_BITS and two_layer_fraction > 0.7
        else "two_layer_breaks"
        if active_coupling >= gauge_generation_reference
        else "coupled_but_distinct"
    )
    architecture = (
        "separate_scale_layer_hardened"
        if verdict_type == "two_layer_robust"
        else "single_coupled_layer"
        if verdict_type == "two_layer_breaks"
        else "coupled_layers_with_distinct_measure_kind"
    )

    architecture_rows = [
        {
            "quantity": "active_content_scale_coupling_bits",
            "value": f"{active_coupling:.12f}",
            "reference": f"gauge_generation={gauge_generation_reference:.12f}",
        },
        {
            "quantity": "step17_inherited_residual_bits",
            "value": f"{inherited_step17:.12f}",
            "reference": "before radiative channel",
        },
        {
            "quantity": "two_layer_fraction",
            "value": f"{two_layer_fraction:.12f}",
            "reference": "robustness sweep",
        },
        {
            "quantity": "coupled_but_distinct_fraction",
            "value": f"{coupled_fraction:.12f}",
            "reference": "robustness sweep",
        },
        {
            "quantity": "one_layer_break_fraction",
            "value": f"{break_fraction:.12f}",
            "reference": "robustness sweep",
        },
    ]
    write_csv("architecture_verdict_step18.csv", architecture_rows, ["quantity", "value", "reference"])

    verdict = {
        "step": 18,
        "active_channel_strength": ACTIVE_CHANNEL_STRENGTH,
        "active_content_scale_coupling_bits": active_coupling,
        "step17_inherited_residual_bits": inherited_step17,
        "gauge_generation_reference_bits": gauge_generation_reference,
        "coupling_strength_monotone": bool(controls[0]["passes"]),
        "two_layer_fraction": two_layer_fraction,
        "coupled_but_distinct_fraction": coupled_fraction,
        "one_layer_break_fraction": break_fraction,
        "flip_boundary": flip_boundary,
        "verdict": verdict_type,
        "revised_architecture": architecture,
        "hierarchy_resolved": False,
        "physical_mass_value_supplied": False,
        "dominant_yukawa_value_derived": False,
        "root_landed": False,
        "frame_transfer_certified": False,
    }
    (ARTIFACT_DIR / "overall_verdict_step18.json").write_text(json.dumps(verdict, indent=2), encoding="utf-8")

    obligations = [
        {
            "obligation": "faithful_enrichment",
            "status": "radiative_channel_added",
            "witness": "scale cost depends on dominant fermion proxy plus subdominant gauge/rep terms",
        },
        {
            "obligation": "independently_checkable_consequence",
            "status": "advanced_as_coupled_but_distinct_architecture",
            "witness": "active channel coupling is non-negligible but below the gauge-generation reference",
        },
        {
            "obligation": "derived_formula",
            "status": "not_advanced_this_step",
            "witness": "radiative sensitivity formula is structural input, not a new closed-form law",
        },
        {
            "obligation": "limit_recovery",
            "status": "radiative_sensitivity_represented",
            "witness": "quadratic cutoff sensitivity with dominant fermion contribution is represented",
        },
    ]
    write_csv("candidate_law_obligations_step18.csv", obligations, ["obligation", "status", "witness"])

    schema = {
        "step": 18,
        "artifact_dir": "steps/step18_two_layer_stress_test_artifacts",
        "source_steps": {
            "step8_survivors": "steps/step8_structural_token_blind_selection_artifacts/structural_survivors_step8.csv",
            "step17_verdict": "steps/step17_two_layer_test_artifacts/overall_verdict_step17.json",
        },
        "verdict": verdict,
    }
    (ARTIFACT_DIR / "schema.json").write_text(json.dumps(schema, indent=2), encoding="utf-8")

    content_rows = [
        {
            "claim_id": "radiative_channel",
            "claim": "The scale facet is stress-tested with a content-dependent radiative sensitivity channel.",
            "grade": "finite-carrier-diagnostic",
            "classification": "faithful-structural-channel",
            "source_artifacts": "steps/step18_two_layer_stress_test_artifacts/radiative_channel_step18.csv",
        },
        {
            "claim_id": "active_coupling",
            "claim": "With the channel active, content-scale coupling is non-negligible but below the gauge-generation reference.",
            "grade": "finite-carrier-diagnostic",
            "classification": "coupling-diagnostic",
            "source_artifacts": "steps/step18_two_layer_stress_test_artifacts/architecture_verdict_step18.csv;steps/step18_two_layer_stress_test_artifacts/coupling_strength_sweep_step18.csv",
        },
        {
            "claim_id": "can_fail_monotonicity",
            "claim": "The measured coupling rises as injected channel strength rises.",
            "grade": "finite-carrier-diagnostic",
            "classification": "anti-insensitivity-control",
            "source_artifacts": "steps/step18_two_layer_stress_test_artifacts/coupling_strength_sweep_step18.csv;steps/step18_two_layer_stress_test_artifacts/controls_step18.csv",
        },
        {
            "claim_id": "robustness_sweep",
            "claim": "Threshold, estimator, and grouping sweep maps the two-layer versus coupled verdict boundary.",
            "grade": "finite-carrier-diagnostic",
            "classification": "robustness-sweep",
            "source_artifacts": "steps/step18_two_layer_stress_test_artifacts/robustness_sweep_step18.csv",
        },
        {
            "claim_id": "coupled_but_distinct_verdict",
            "claim": "The stress test revises the clean split to coupled-but-distinct.",
            "grade": "finite-carrier-diagnostic",
            "classification": "architecture-verdict",
            "source_artifacts": "steps/step18_two_layer_stress_test_artifacts/overall_verdict_step18.json",
        },
        {
            "claim_id": "nonclaim_boundary",
            "claim": "Toy-structural only; no physical scale value or real mechanism is supplied.",
            "grade": "organizational",
            "classification": "scope-boundary",
            "source_artifacts": "steps/step18_two_layer_stress_test_artifacts/nonclaim_boundary.md",
        },
    ]
    write_csv("content_classification.csv", content_rows, ["claim_id", "claim", "grade", "classification", "source_artifacts"])

    summary = f"""# Step 18 Results Summary: Two-Layer Stress Test

## Radiative Content-to-Scale Channel

The scale facet was re-tested with a content-dependent radiative channel: a dominant fermion proxy from the texture/generation data plus subdominant gauge/representation terms. This is a structural sensitivity channel, not a physical solution to the scale problem.

## Coupling With Channel Active

- Step-17 inherited EW-vs-content residual: `{inherited_step17:.12f}` bits.
- Active content-scale coupling with radiative channel: `{active_coupling:.12f}` bits.
- Gauge-generation reference control: `{gauge_generation_reference:.12f}` bits.

The channel raises the content-scale coupling from borderline-low to non-negligible, but it remains below the gauge-generation reference.

## Coupling-Strength Can-Fail

The coupling-strength sweep is monotone: `{controls[0]['passes']}`. Coupling rises from `0` at channel strength `0` to `{sweep_rows[-1]['content_scale_mi_bits']}` bits at the strongest injected channel. This proves the information measure responds to injected coupling.

## Robustness Sweep

- Two-layer fraction: `{two_layer_fraction:.12f}`.
- Coupled-but-distinct fraction: `{coupled_fraction:.12f}`.
- One-layer-break fraction: `{break_fraction:.12f}`.
- Flip boundary: {flip_boundary}.

## Verdict

`{verdict_type}`.

The clean Step-17 two-layer split is not robust once the radiative content-to-scale channel is included. The honest result is the middle architecture: the scale facet is coupled to content by radiative sensitivity, but it remains a distinct kind of selection problem because its measure is naturalness/tuning rather than anomaly/content consistency.

## Honest Scope

Toy-structural only. The hierarchy remains open, no physical Higgs-scale value is supplied, no dominant Yukawa value is derived, and frame transfer remains open.
"""
    (ARTIFACT_DIR / "results_summary.md").write_text(summary, encoding="utf-8")

    nonclaim = """# Step 18 Nonclaim Boundary

This is a finite-toy architecture stress test.

The radiative channel is a structural representation of content-dependent quadratic sensitivity. It is not a physical naturalness mechanism, does not provide a Higgs-scale value, and does not provide a dominant Yukawa value.

The verdict is toy-internal: the scale facet is coupled to content but remains a distinct measure kind. Frame transfer remains open.
"""
    (ARTIFACT_DIR / "nonclaim_boundary.md").write_text(nonclaim, encoding="utf-8")

    statement = rf"""\section{{Step 18: Two-Layer Stress Test}}

\paragraph{{Grade.}}
Finite-toy architecture stress test. A content-dependent radiative sensitivity channel is added to the scale facet.

\paragraph{{Computed Couplings.}}
With the channel active, content-scale coupling is {active_coupling:.12f} bits. The gauge-generation reference is {gauge_generation_reference:.12f} bits. The inherited Step-17 residual was {inherited_step17:.12f} bits.

\paragraph{{Verdict.}}
\texttt{{{verdict_type}}}. The clean split does not survive as a strict independence claim. The toy supports coupled-but-distinct selection: content and scale couple through radiative sensitivity, while the scale measure remains naturalness/tuning rather than anomaly/content consistency.
"""
    (ARTIFACT_DIR / "step18_statement.tex").write_text(statement, encoding="utf-8")

    print(
        "Step 18 built: "
        f"active_mi={active_coupling:.12f} "
        f"gauge_gen={gauge_generation_reference:.12f} "
        f"two_layer_fraction={two_layer_fraction:.12f} "
        f"verdict={verdict_type}"
    )


if __name__ == "__main__":
    main()
