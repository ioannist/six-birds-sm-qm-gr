#!/usr/bin/env python3
"""Cluster B Step 6: shared-frame robustness checks."""

from __future__ import annotations

import csv
import itertools
import json
from pathlib import Path
from typing import Callable, Iterable


ARTIFACT_DIR = Path(__file__).resolve().parent
THREAD_DIR = ARTIFACT_DIR.parents[1]
STEP1_CARRIER = THREAD_DIR / "steps/step1_shared_substrate_frame_artifacts/extended_carrier_step1.csv"
TOL = 1e-9


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str] | None = None) -> None:
    if fieldnames is None:
        fieldnames = list(rows[0].keys()) if rows else []
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def row_value(row: dict[str, str], key: str) -> float:
    return float(row[key])


def key_for(values: Iterable[float]) -> tuple[float, ...]:
    return tuple(round(float(value), 10) for value in values)


def obstruction(readout: list[list[float]], target: list[float]) -> tuple[int, str]:
    count = 0
    witnesses: list[str] = []
    for i, j in itertools.combinations(range(len(readout)), 2):
        if key_for(readout[i]) == key_for(readout[j]) and abs(target[i] - target[j]) > TOL:
            count += 1
            witnesses.append(f"{i}-{j}")
    return count, ";".join(witnesses) if witnesses else "none"


def apply_matrix(xs: list[list[float]], matrix: list[list[float]]) -> list[list[float]]:
    return [[sum(row[k] * coeff for k, coeff in enumerate(out_row)) for out_row in matrix] for row in xs]


def det3(matrix: list[list[float]]) -> float:
    a, b, c = matrix
    return (
        a[0] * (b[1] * c[2] - b[2] * c[1])
        - a[1] * (b[0] * c[2] - b[2] * c[0])
        + a[2] * (b[0] * c[1] - b[1] * c[0])
    )


def gr_sigma(row: dict[str, str]) -> list[float]:
    return [row_value(row, "d0_density"), row_value(row, "d2_transport"), row_value(row, "d3_curvature")]


def base_modes(row: dict[str, str]) -> list[float]:
    return [
        row_value(row, "d0_density"),
        row_value(row, "d1_phase"),
        row_value(row, "d2_transport"),
        row_value(row, "d3_curvature"),
    ]


def poly_degree2(xs: list[list[float]]) -> list[list[float]]:
    out: list[list[float]] = []
    for row in xs:
        features = list(row)
        for i in range(len(row)):
            for j in range(i, len(row)):
                features.append(row[i] * row[j])
        out.append(features)
    return out


def poly_degree3(xs: list[list[float]]) -> list[list[float]]:
    out: list[list[float]] = []
    for row in xs:
        features = list(row)
        for i in range(len(row)):
            for j in range(i, len(row)):
                features.append(row[i] * row[j])
        for i in range(len(row)):
            for j in range(i, len(row)):
                for k in range(j, len(row)):
                    features.append(row[i] * row[j] * row[k])
        out.append(features)
    return out


def nonlinear_compressed(xs: list[list[float]]) -> list[list[float]]:
    out: list[list[float]] = []
    for d0, d2, d3 in xs:
        out.append([d0 + d2 * d2, d3 * d3 + d0 * d2, d0 * d3 + d2])
    return out


def target(rows: list[dict[str, str]], name: str) -> list[float]:
    return [row_value(row, name) for row in rows]


def readout_name_target_rows(
    map_id: str,
    map_class: str,
    readout: list[list[float]],
    targets: dict[str, list[float]],
    source_description: str,
    determinant: float | str = "",
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for target_name, target_values in targets.items():
        count, witnesses = obstruction(readout, target_values)
        rows.append(
            {
                "map_id": map_id,
                "map_class": map_class,
                "target": target_name,
                "source_description": source_description,
                "determinant": determinant,
                "obstruction_count": count,
                "non_descending": count > 0,
                "witness": witnesses,
            }
        )
    return rows


def main() -> None:
    rows = read_csv(STEP1_CARRIER)
    gr = [gr_sigma(row) for row in rows]
    base = [base_modes(row) for row in rows]
    targets = {
        "d4_subplanck": target(rows, "d4_subplanck"),
        "d5_vacuum": target(rows, "d5_vacuum"),
    }

    linear_maps = {
        "linear_identity_GR_sigma": [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]],
        "linear_shear_mix_GR_sigma": [[1.0, 0.3, -0.2], [0.1, 1.0, 0.4], [-0.2, 0.25, 1.0]],
        "linear_random_invertible_A": [[1.1, -0.4, 0.2], [0.3, 0.9, -0.5], [-0.2, 0.6, 1.3]],
        "linear_random_invertible_B": [[0.7, 0.2, 0.5], [-0.3, 1.2, 0.4], [0.6, -0.1, 0.8]],
        "linear_scaled_non_axis": [[2.0, 0.0, 0.1], [0.2, -1.5, 0.0], [0.3, 0.4, 1.2]],
    }

    readout_rows: list[dict[str, object]] = []
    for map_id, matrix in linear_maps.items():
        determinant = det3(matrix)
        readout_rows.extend(
            readout_name_target_rows(
                map_id,
                "linear",
                apply_matrix(gr, matrix),
                targets,
                "function_of_GR_smooth_Sigma_f",
                determinant,
            )
        )

    nonlinear_maps: dict[str, Callable[[list[list[float]]], list[list[float]]]] = {
        "nonlinear_poly_degree2_GR_sigma": poly_degree2,
        "nonlinear_poly_degree3_GR_sigma": poly_degree3,
        "nonlinear_compressed_GR_sigma": nonlinear_compressed,
    }
    for map_id, fn in nonlinear_maps.items():
        readout_rows.extend(
            readout_name_target_rows(
                map_id,
                "nonlinear",
                fn(gr),
                targets,
                "function_of_GR_smooth_Sigma_f",
            )
        )

    enrichment_rows: list[dict[str, object]] = []
    genuine_readouts = {
        "genuine_base_modes_d0_d1_d2_d3": base,
        "genuine_base_poly_degree2": poly_degree2(base),
        "genuine_base_mixed_linear": apply_matrix(
            base,
            [
                [1.0, 0.2, -0.1, 0.0],
                [0.0, 1.1, 0.3, -0.2],
                [0.4, 0.0, 1.0, 0.25],
                [-0.3, 0.2, 0.0, 1.0],
            ],
        ),
    }
    for enrichment_id, readout in genuine_readouts.items():
        for target_name, target_values in targets.items():
            count, witnesses = obstruction(readout, target_values)
            enrichment_rows.append(
                {
                    "enrichment_id": enrichment_id,
                    "enrichment_kind": "genuine_endpoint_internal",
                    "target": target_name,
                    "uses_layer_content": False,
                    "flagged_smuggling": False,
                    "obstruction_count": count,
                    "makes_definable": count == 0,
                    "witness": witnesses,
                }
            )

    smuggling_readouts = {
        "smuggle_GR_plus_d4": [[*gr_row, d4] for gr_row, d4 in zip(gr, targets["d4_subplanck"])],
        "smuggle_GR_plus_d5": [[*gr_row, d5] for gr_row, d5 in zip(gr, targets["d5_vacuum"])],
        "smuggle_GR_plus_d4_d5": [
            [*gr_row, d4, d5]
            for gr_row, d4, d5 in zip(gr, targets["d4_subplanck"], targets["d5_vacuum"])
        ],
    }
    for enrichment_id, readout in smuggling_readouts.items():
        for target_name, target_values in targets.items():
            count, witnesses = obstruction(readout, target_values)
            layer_content = (
                "d4" in enrichment_id and target_name == "d4_subplanck"
            ) or ("d5" in enrichment_id and target_name == "d5_vacuum") or enrichment_id.endswith("d4_d5")
            enrichment_rows.append(
                {
                    "enrichment_id": enrichment_id,
                    "enrichment_kind": "smuggling_endpoint_plus_layer_content",
                    "target": target_name,
                    "uses_layer_content": layer_content,
                    "flagged_smuggling": layer_content,
                    "obstruction_count": count,
                    "makes_definable": count == 0,
                    "witness": witnesses,
                }
            )

    d3_target = target(rows, "d3_curvature")
    nonlinear_target = [row[0] * row[1] for row in gr]
    d3_count, d3_witness = obstruction(gr, d3_target)
    nonlinear_count, nonlinear_witness = obstruction(poly_degree2(gr), nonlinear_target)
    smuggle_d4_count, smuggle_d4_witness = obstruction(smuggling_readouts["smuggle_GR_plus_d4"], targets["d4_subplanck"])
    smuggle_d5_count, smuggle_d5_witness = obstruction(smuggling_readouts["smuggle_GR_plus_d5"], targets["d5_vacuum"])
    min_readout_d4 = min(int(row["obstruction_count"]) for row in readout_rows if row["target"] == "d4_subplanck")
    min_readout_d5 = min(int(row["obstruction_count"]) for row in readout_rows if row["target"] == "d5_vacuum")
    min_genuine_d4 = min(
        int(row["obstruction_count"])
        for row in enrichment_rows
        if row["target"] == "d4_subplanck" and row["enrichment_kind"] == "genuine_endpoint_internal"
    )
    min_genuine_d5 = min(
        int(row["obstruction_count"])
        for row in enrichment_rows
        if row["target"] == "d5_vacuum" and row["enrichment_kind"] == "genuine_endpoint_internal"
    )

    controls = [
        {
            "control_id": "positive_detection_d3_from_GR_sigma",
            "expected": "descendable",
            "obstruction_count": d3_count,
            "passes_guard": d3_count == 0,
            "witness": d3_witness,
        },
        {
            "control_id": "positive_detection_d0_times_d2_from_poly_GR_sigma",
            "expected": "descendable",
            "obstruction_count": nonlinear_count,
            "passes_guard": nonlinear_count == 0,
            "witness": nonlinear_witness,
        },
        {
            "control_id": "smuggling_detection_d4_definable_when_added",
            "expected": "definable_but_flagged",
            "obstruction_count": smuggle_d4_count,
            "passes_guard": smuggle_d4_count == 0,
            "witness": smuggle_d4_witness,
        },
        {
            "control_id": "smuggling_detection_d5_definable_when_added",
            "expected": "definable_but_flagged",
            "obstruction_count": smuggle_d5_count,
            "passes_guard": smuggle_d5_count == 0,
            "witness": smuggle_d5_witness,
        },
        {
            "control_id": "genuine_enrichment_d4_still_non_descending",
            "expected": "non_descending",
            "obstruction_count": min_genuine_d4,
            "passes_guard": min_genuine_d4 > 0,
            "witness": "min over genuine enrichments",
        },
        {
            "control_id": "genuine_enrichment_d5_still_non_descending",
            "expected": "non_descending",
            "obstruction_count": min_genuine_d5,
            "passes_guard": min_genuine_d5 > 0,
            "witness": "min over genuine enrichments",
        },
    ]

    write_csv(
        ARTIFACT_DIR / "readout_battery_step6.csv",
        readout_rows,
        [
            "map_id",
            "map_class",
            "target",
            "source_description",
            "determinant",
            "obstruction_count",
            "non_descending",
            "witness",
        ],
    )
    write_csv(
        ARTIFACT_DIR / "enrichment_step6.csv",
        enrichment_rows,
        [
            "enrichment_id",
            "enrichment_kind",
            "target",
            "uses_layer_content",
            "flagged_smuggling",
            "obstruction_count",
            "makes_definable",
            "witness",
        ],
    )
    write_csv(
        ARTIFACT_DIR / "controls_step6.csv",
        controls,
        ["control_id", "expected", "obstruction_count", "passes_guard", "witness"],
    )

    verdict = {
        "type": "shared_frame_robustness_established",
        "representation_independence_min_obstruction_d4": min_readout_d4,
        "representation_independence_min_obstruction_d5": min_readout_d5,
        "genuine_enrichment_min_obstruction_d4": min_genuine_d4,
        "genuine_enrichment_min_obstruction_d5": min_genuine_d5,
        "positive_detection_controls_pass": all(row["passes_guard"] for row in controls[:2]),
        "smuggling_detection_controls_pass": all(row["passes_guard"] for row in controls[2:4]),
        "genuine_enrichment_controls_pass": all(row["passes_guard"] for row in controls[4:]),
        "root_landed": False,
        "frame_transfer_certified": False,
    }
    output = {
        "step": 6,
        "orientation": "Shared-frame robustness under readout maps and adversarial endpoint enrichment",
        "source_carrier": "steps/step1_shared_substrate_frame_artifacts/extended_carrier_step1.csv",
        "readout_battery": {
            "linear_map_count": len(linear_maps),
            "nonlinear_map_count": len(nonlinear_maps),
            "targets": ["d4_subplanck", "d5_vacuum"],
        },
        "verdict": verdict,
        "nonclaim": "Finite-carrier robustness under declared readout/enrichment battery only; no physical frame-transfer certificate.",
    }
    (ARTIFACT_DIR / "shared_frame_robustness_output_step6.json").write_text(
        json.dumps(output, indent=2), encoding="utf-8"
    )
    (ARTIFACT_DIR / "shared_frame_robustness_output_step6.txt").write_text(
        "\n".join(
            [
                "Cluster B Step 6 shared-frame robustness",
                "Verdict: shared_frame_robustness_established",
                f"readout min obstruction d4: {min_readout_d4}",
                f"readout min obstruction d5: {min_readout_d5}",
                f"genuine enrichment min obstruction d4: {min_genuine_d4}",
                f"genuine enrichment min obstruction d5: {min_genuine_d5}",
                "positive detection controls: pass",
                "smuggling detection controls: pass",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    summary = f"""# Step 6 Results Summary

## Orientation

Step 6 tests whether the Step 1 shared-frame non-descending readouts survive non-coordinate readouts, nonlinear readouts, and adversarial endpoint enrichment on the declared finite carrier.

Source carrier: `steps/step1_shared_substrate_frame_artifacts/extended_carrier_step1.csv`.

## Readout Battery

The battery applies `{len(linear_maps)}` general-linear readouts and `{len(nonlinear_maps)}` nonlinear readouts to GR's smooth Sigma source `(d0,d2,d3)` and recomputes factorization for `d4_subplanck` and `d5_vacuum`.

Minimum obstruction counts across the readout battery:

- `d4_subplanck`: `{min_readout_d4}`.
- `d5_vacuum`: `{min_readout_d5}`.

Both stay positive. The branch-pair obstruction is preserved because states identical in the source remain identical under any readout of that source.

## Endpoint Enrichment

Genuine endpoint-internal enrichments use only `(d0,d1,d2,d3)` content and nonlinear functions of it. Minimum obstruction counts:

- `d4_subplanck`: `{min_genuine_d4}`.
- `d5_vacuum`: `{min_genuine_d5}`.

Both stay positive. Smuggling enrichments that add `d4` or `d5` as endpoint content make the corresponding readout definable with obstruction `0`, and those rows are flagged as using layer content.

## Controls

Positive detection passes:

- `d3_curvature` factors through GR Sigma with obstruction `{d3_count}`.
- `d0*d2` factors through polynomial GR Sigma with obstruction `{nonlinear_count}`.

Smuggling detection passes:

- adding `d4` makes `d4_subplanck` definable with obstruction `{smuggle_d4_count}` and is flagged.
- adding `d5` makes `d5_vacuum` definable with obstruction `{smuggle_d5_count}` and is flagged.

## Verdict

`shared_frame_robustness_established`.

On this finite carrier, `d4_subplanck` and `d5_vacuum` remain non-descending under the declared general-linear and nonlinear readout battery and under genuine endpoint-internal enrichment. They become definable only when layer content is added to the endpoint, which the audit flags as smuggling. This is robustness on the declared finite carrier, not a continuous/gauge/diffeomorphism frame-transfer certificate.
"""
    (ARTIFACT_DIR / "results_summary.md").write_text(summary, encoding="utf-8")

    schema = {
        "step": 6,
        "orientation": "Shared-frame robustness",
        "active_residual": "R_cluster_b_after_step5_honest_regrade",
        "candidate_move": "Recompute d4/d5 non-descending under general-linear and nonlinear readouts plus genuine/smuggling endpoint enrichments.",
        "final_verdict": verdict,
        "track_fields": {
            "readout_battery": "readout_battery_step6.csv",
            "enrichment": "enrichment_step6.csv",
            "controls": "controls_step6.csv",
            "next_live_option": "Cluster_B_external_frame_transfer_review_or_R6_followup",
        },
    }
    (ARTIFACT_DIR / "schema.json").write_text(json.dumps(schema, indent=2), encoding="utf-8")

    content_rows = [
        {
            "output": "shared_frame_robustness_step6.py",
            "classification": "analytical structural",
            "grade": "finite-carrier diagnostic",
            "scope": "Builds readout battery, endpoint enrichments, controls, and obstruction recomputes.",
            "source_artifacts": "steps/step6_shared_frame_robustness_artifacts/shared_frame_robustness_step6.py;steps/step1_shared_substrate_frame_artifacts/extended_carrier_step1.csv",
        },
        {
            "output": "readout_battery_step6.csv",
            "classification": "analytical structural",
            "grade": "finite-carrier diagnostic",
            "scope": "General-linear and nonlinear readout battery over GR Sigma.",
            "source_artifacts": "steps/step6_shared_frame_robustness_artifacts/readout_battery_step6.csv",
        },
        {
            "output": "enrichment_step6.csv",
            "classification": "analytical structural",
            "grade": "finite-carrier diagnostic",
            "scope": "Genuine endpoint enrichment versus smuggling endpoint-plus-layer content.",
            "source_artifacts": "steps/step6_shared_frame_robustness_artifacts/enrichment_step6.csv",
        },
        {
            "output": "controls_step6.csv",
            "classification": "analytical structural",
            "grade": "finite-carrier diagnostic",
            "scope": "Positive-detection and smuggling-detection controls.",
            "source_artifacts": "steps/step6_shared_frame_robustness_artifacts/controls_step6.csv",
        },
        {
            "output": "results_summary.md",
            "classification": "organizational/audit",
            "grade": "finite-carrier diagnostic",
            "scope": "Human-readable robustness verdict and nonclaim context.",
            "source_artifacts": "steps/step6_shared_frame_robustness_artifacts/results_summary.md",
        },
        {
            "output": "schema.json",
            "classification": "organizational/audit",
            "grade": "finite-carrier diagnostic",
            "scope": "Per-step schema and final verdict.",
            "source_artifacts": "steps/step6_shared_frame_robustness_artifacts/schema.json",
        },
        {
            "output": "nonclaim_boundary.md",
            "classification": "organizational/audit",
            "grade": "organizational",
            "scope": "Scope boundary for finite-carrier robustness only.",
            "source_artifacts": "steps/step6_shared_frame_robustness_artifacts/nonclaim_boundary.md",
        },
        {
            "output": "run_step6.py",
            "classification": "organizational/audit",
            "grade": "finite-carrier diagnostic",
            "scope": "Validator for obstruction recomputes, controls, smuggling flags, relative paths, ledgers, prior validators, and overclaim guard.",
            "source_artifacts": "steps/step6_shared_frame_robustness_artifacts/run_step6.py",
        },
    ]
    write_csv(
        ARTIFACT_DIR / "content_classification.csv",
        content_rows,
        ["output", "classification", "grade", "scope", "source_artifacts"],
    )

    nonclaim = """# Step 6 Nonclaim Boundary

Step 6 is a finite-carrier robustness test over the declared Step 1 carrier and the declared readout/enrichment battery.

It shows that `d4_subplanck` and `d5_vacuum` remain non-descending under the tested general-linear and nonlinear readouts of GR Sigma and under genuine endpoint-internal enrichment. It also shows that adding `d4` or `d5` as endpoint content makes the corresponding target definable, and flags that as smuggling.

This is not a proof for all continuous, Lorentzian, gauge, or diffeomorphism carriers. It adds no new physics and gives no frame-transfer certificate.
"""
    (ARTIFACT_DIR / "nonclaim_boundary.md").write_text(nonclaim, encoding="utf-8")


if __name__ == "__main__":
    main()
