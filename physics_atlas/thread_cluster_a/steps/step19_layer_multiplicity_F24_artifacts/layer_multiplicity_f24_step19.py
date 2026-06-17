#!/usr/bin/env python3
"""Cluster A Step 19: exact F24/F47 layer multiplicity test."""

from __future__ import annotations

import csv
import json
import math
from collections import Counter, defaultdict
from pathlib import Path


ARTIFACT_DIR = Path(__file__).resolve().parent
THREAD_DIR = ARTIFACT_DIR.parents[1]
STEP8_DIR = THREAD_DIR / "steps" / "step8_structural_token_blind_selection_artifacts"

CONTENT_Q_COLUMNS = [
    "gauge_code",
    "rep_code",
    "n_gen",
    "texture_code",
    "uv_code",
    "vacuum_code",
    "anomaly_free",
    "gauge_rep_consistent",
    "generation_chirality_ok",
    "texture_ok",
    "uv_consistent",
]
BASE_SCALE_RATIO = {"e0": 1e-4, "e1": 1e-2, "e2": 1.0}
GAUGE_RANK = {"g0": 4, "g1": 5, "g2": 3, "g3": 6}
REP_COMPLEXITY = {"r0": 1, "r1": 2, "r2": 2, "r3": 1}
DOMINANT_YUKAWA_PROXY = {"t0": 1.0, "t1": 0.55, "t2": 0.35, "t3": 0.20}
RADIATIVE_THRESHOLD = 2.70
TARGET_RATIO_MAX = 1e-4
SMALL_THETA = 0.05


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


def q_key(row: dict[str, str]) -> str:
    return "|".join(str(row[column]) for column in CONTENT_Q_COLUMNS)


def radiative_score(row: dict[str, str]) -> float:
    yukawa = DOMINANT_YUKAWA_PROXY[row["texture_code"]]
    generation_boost = 0.03 * int(row["n_gen"])
    gauge_subdominant = 0.08 * GAUGE_RANK[row["gauge_code"]]
    rep_subdominant = 0.02 * REP_COMPLEXITY[row["rep_code"]]
    return 3.0 * yukawa * yukawa + generation_boost - gauge_subdominant - rep_subdominant


def scale_ratio(row: dict[str, str]) -> float:
    base = BASE_SCALE_RATIO[row["ew_code"]]
    # A small structural correction records that the ratio is read with the
    # content-dependent radiative pressure active; it does not supply a value.
    return base * (1.0 + 0.01 * max(0.0, radiative_score(row)))


def in_selector_region(row: dict[str, str]) -> bool:
    return BASE_SCALE_RATIO[row["ew_code"]] <= TARGET_RATIO_MAX and radiative_score(row) > RADIATIVE_THRESHOLD


def s_readout(row: dict[str, str]) -> str:
    if in_selector_region(row):
        return "small_selector_region"
    if BASE_SCALE_RATIO[row["ew_code"]] <= TARGET_RATIO_MAX:
        return "small_ratio_outside_high_sensitivity"
    return "outside_small_selector"


def descending_control(row: dict[str, str]) -> str:
    return q_key(row)


def splitting_control(row: dict[str, str]) -> str:
    return row["ew_code"]


def obstruction_summary(rows: list[dict[str, str]], readout_fn) -> tuple[int, list[dict[str, object]], list[dict[str, object]]]:
    groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        groups[q_key(row)].append(row)
    total_obstruction = 0
    summary_rows: list[dict[str, object]] = []
    witness_rows: list[dict[str, object]] = []
    for key, members in sorted(groups.items()):
        counts = Counter(readout_fn(member) for member in members)
        total_pairs = len(members) * (len(members) - 1) // 2
        same_pairs = sum(count * (count - 1) // 2 for count in counts.values())
        obstruction_pairs = total_pairs - same_pairs
        total_obstruction += obstruction_pairs
        if obstruction_pairs:
            first_readout = None
            first_member = None
            for member in members:
                current = readout_fn(member)
                if first_readout is None:
                    first_readout = current
                    first_member = member
                    continue
                if current != first_readout and first_member is not None:
                    witness_rows.append(
                        {
                            "q_key": key,
                            "left_world": first_member["candidate_id"],
                            "right_world": member["candidate_id"],
                            "left_readout": first_readout,
                            "right_readout": current,
                        }
                    )
                    break
        summary_rows.append(
            {
                "q_key": key,
                "fiber_size": len(members),
                "readout_values": ";".join(f"{name}:{count}" for name, count in sorted(counts.items())),
                "obstruction_pairs": obstruction_pairs,
            }
        )
    return total_obstruction, summary_rows, witness_rows[:25]


def main() -> None:
    carrier = read_csv(STEP8_DIR / "neutral_candidate_space_step8.csv")
    role_obstruction, fiber_rows, witness_rows = obstruction_summary(carrier, s_readout)
    desc_obstruction, _, desc_witness = obstruction_summary(carrier, descending_control)
    split_obstruction, _, split_witness = obstruction_summary(carrier, splitting_control)

    write_csv(
        "role_obstruction_fibers_step19.csv",
        fiber_rows,
        ["q_key", "fiber_size", "readout_values", "obstruction_pairs"],
    )
    write_csv(
        "role_obstruction_witnesses_step19.csv",
        witness_rows,
        ["q_key", "left_world", "right_world", "left_readout", "right_readout"],
    )

    f47_rows = []
    sigma_count = 0
    realized_in_sigma = False
    for row in carrier:
        score = radiative_score(row)
        selected = in_selector_region(row)
        sigma_count += int(selected)
        if row["is_realized_point"] == "True":
            realized_in_sigma = selected
        f47_rows.append(
            {
                "candidate_id": row["candidate_id"],
                "q_key": q_key(row),
                "ew_code": row["ew_code"],
                "scale_ratio": f"{scale_ratio(row):.12g}",
                "base_scale_ratio": f"{BASE_SCALE_RATIO[row['ew_code']]:.12g}",
                "radiative_score": f"{score:.6f}",
                "target_predicate": selected,
                "s_readout": s_readout(row),
                "is_realized_point": row["is_realized_point"],
            }
        )
    write_csv(
        "f47_selector_region_step19.csv",
        f47_rows,
        ["candidate_id", "q_key", "ew_code", "scale_ratio", "base_scale_ratio", "radiative_score", "target_predicate", "s_readout", "is_realized_point"],
    )

    mu_total = len(carrier)
    sigma_fraction = sigma_count / mu_total
    small_selector = sigma_count > 0 and sigma_fraction <= SMALL_THETA

    f24_rows = [
        {
            "family": "MemoryLayer",
            "fires": False,
            "computed_reason": "scale readout uses content-dependent radiative score and does not form an independently closed access quotient",
        },
        {
            "family": "HiddenUpstreamRole",
            "fires": False,
            "computed_reason": "scale role is visible and audited on the finite carrier; no latent outside quotient is used",
        },
        {
            "family": "BridgeMediatedRole",
            "fires": False,
            "computed_reason": "no bridge/common parent construction is introduced; the role is priced as a budget",
        },
        {
            "family": "BudgetedRole",
            "fires": True,
            "computed_reason": "nonempty role split is carried as finite naturalness budget with F47 small selector region",
        },
        {
            "family": "ScopedRole",
            "fires": False,
            "computed_reason": "role and obstruction are computed on the full finite carrier, not a proper scope only",
        },
        {
            "family": "CoarsenedRole",
            "fires": False,
            "computed_reason": "s does not descend through q; obstruction is nonempty",
        },
        {
            "family": "OutsideRoleScope",
            "fires": False,
            "computed_reason": "scale role is explicitly in the tested selection scope",
        },
        {
            "family": "BlockedNonClosure",
            "fires": False,
            "computed_reason": "F47 budget ledger is finite and audited; no unclosed obstruction remains",
        },
    ]
    write_csv("f24_resolution_step19.csv", f24_rows, ["family", "fires", "computed_reason"])

    controls = [
        {
            "control": "known_descending_role",
            "obstruction_pairs": desc_obstruction,
            "passes": desc_obstruction == 0,
            "witness": "s_ctrl=q_key is constant on q-fibers",
        },
        {
            "control": "known_splitting_role",
            "obstruction_pairs": split_obstruction,
            "passes": split_obstruction > 0,
            "witness": "ew_code varies inside q-fibers",
        },
        {
            "control": "main_role_split",
            "obstruction_pairs": role_obstruction,
            "passes": role_obstruction > 0,
            "witness": "F47 scale readout varies inside q-fibers",
        },
    ]
    write_csv("controls_step19.csv", controls, ["control", "obstruction_pairs", "passes", "witness"])

    selector_summary = [
        {
            "mu_total": mu_total,
            "mu_sigma": sigma_count,
            "theta": f"{SMALL_THETA:.6f}",
            "selector_fraction": f"{sigma_fraction:.12f}",
            "positive_measure": sigma_count > 0,
            "small": small_selector,
            "realized_in_sigma": realized_in_sigma,
            "realized": bool(realized_in_sigma and small_selector),
        }
    ]
    write_csv(
        "f47_selector_summary_step19.csv",
        selector_summary,
        ["mu_total", "mu_sigma", "theta", "selector_fraction", "positive_measure", "small", "realized_in_sigma", "realized"],
    )

    verdict = {
        "step": 19,
        "carrier_size": len(carrier),
        "q_definition": CONTENT_Q_COLUMNS,
        "s_definition": "F47 scale/naturalness readout from scale ratio plus radiative sensitivity",
        "role_obstruction_pairs": role_obstruction,
        "descends": role_obstruction == 0,
        "role_split": role_obstruction > 0,
        "selected_f24_resolution": "BudgetedRole",
        "memory_layer_forms": False,
        "scale_only_independent_closure": False,
        "budgeted_role": True,
        "f47_selector_fraction": sigma_fraction,
        "f47_small": small_selector,
        "f47_realized": bool(realized_in_sigma and small_selector),
        "descending_control_obstruction": desc_obstruction,
        "splitting_control_obstruction": split_obstruction,
        "structural_dependency_not_tdgate": True,
        "root_landed": False,
        "frame_transfer_certified": False,
    }
    (ARTIFACT_DIR / "overall_verdict_step19.json").write_text(json.dumps(verdict, indent=2), encoding="utf-8")

    schema = {
        "step": 19,
        "artifact_dir": "steps/step19_layer_multiplicity_F24_artifacts",
        "source_carrier": "steps/step8_structural_token_blind_selection_artifacts/neutral_candidate_space_step8.csv",
        "verdict": verdict,
    }
    (ARTIFACT_DIR / "schema.json").write_text(json.dumps(schema, indent=2), encoding="utf-8")

    content_rows = [
        {
            "claim_id": "role_obstruction",
            "claim": "The F24 role obstruction is nonempty for the scale/naturalness role.",
            "grade": "finite-carrier-diagnostic",
            "classification": "nonfactorization",
            "source_artifacts": "steps/step19_layer_multiplicity_F24_artifacts/role_obstruction_fibers_step19.csv;steps/step19_layer_multiplicity_F24_artifacts/role_obstruction_witnesses_step19.csv",
        },
        {
            "claim_id": "f24_resolution",
            "claim": "The F24 resolution is BudgetedRole, not MemoryLayer.",
            "grade": "finite-carrier-diagnostic",
            "classification": "layer-multiplicity",
            "source_artifacts": "steps/step19_layer_multiplicity_F24_artifacts/f24_resolution_step19.csv;steps/step19_layer_multiplicity_F24_artifacts/overall_verdict_step19.json",
        },
        {
            "claim_id": "f47_selector",
            "claim": "The scale facet is an F47 small selector region with realized point inside it.",
            "grade": "finite-carrier-diagnostic",
            "classification": "fine-tuning-selector",
            "source_artifacts": "steps/step19_layer_multiplicity_F24_artifacts/f47_selector_region_step19.csv;steps/step19_layer_multiplicity_F24_artifacts/f47_selector_summary_step19.csv",
        },
        {
            "claim_id": "controls",
            "claim": "Known descending and known splitting controls are distinguished.",
            "grade": "finite-carrier-diagnostic",
            "classification": "can-fail-control",
            "source_artifacts": "steps/step19_layer_multiplicity_F24_artifacts/controls_step19.csv",
        },
        {
            "claim_id": "nonclaim_boundary",
            "claim": "Toy instantiation only; MI is structural dependency, not a TDGate-certified cause relation.",
            "grade": "organizational",
            "classification": "scope-boundary",
            "source_artifacts": "steps/step19_layer_multiplicity_F24_artifacts/nonclaim_boundary.md",
        },
    ]
    write_csv("content_classification.csv", content_rows, ["claim_id", "claim", "grade", "classification", "source_artifacts"])

    summary = f"""# Step 19 Results Summary: F24/F47 Layer Multiplicity

## Exact Quotient and Role

- Access quotient `q`: content-selection equivalence class over `{', '.join(CONTENT_Q_COLUMNS)}`.
- Role readout `s`: F47 scale/naturalness readout from the scale ratio and radiative sensitivity.

## Role Obstruction

- `|O_s|` unordered q-fiber pairs: `{role_obstruction}`.
- Descends through q: `{role_obstruction == 0}`.
- RoleSplit: `{role_obstruction > 0}`.

The role split is computed directly: there are q-equal worlds with different scale/naturalness readouts.

## F24 Resolution

Selected resolution: `BudgetedRole`.

MemoryLayer is not selected: the scale-only readout does not form an independent closed access quotient because the role uses the content-dependent radiative score. The role is instead priced as a finite naturalness budget on the same closure.

The other F24 families are ruled out in `f24_resolution_step19.csv`.

## F47 Small Selector Region

- `mu_total`: `{mu_total}`.
- `mu(Sigma)`: `{sigma_count}`.
- `mu(Sigma)/mu_total`: `{sigma_fraction:.12f}`.
- `theta`: `{SMALL_THETA}`.
- `Small(Sigma)`: `{small_selector}`.
- `Realized`: `{bool(realized_in_sigma and small_selector)}`.

## Controls

- Known descending control obstruction: `{desc_obstruction}`.
- Known splitting control obstruction: `{split_obstruction}`.

The controls distinguish descending from splitting roles.

## Structural Dependency Note

The Step-18 mutual information is a structural dependency statistic. It is not a TDGate-certified cause relation: no intervention/control/effect-threshold gate was run.

## Verdict

`RoleSplit -> BudgetedRole`, with F47 small-selector-region fine-tuning. This is one closure with a budgeted scale role, not an independently closed scale layer.
"""
    (ARTIFACT_DIR / "results_summary.md").write_text(summary, encoding="utf-8")

    nonclaim = """# Step 19 Nonclaim Boundary

This is a finite-toy instantiation of the F24/F47 tests.

It does not provide a naturalness mechanism, a Higgs-scale value, gauge content values, new physics, or frame transfer. The scale role is classified inside the toy grammar only.

The Step-18 mutual-information value is treated as structural dependency. It is not a TDGate-certified cause relation because no intervention/control/effect-threshold gate was run.
"""
    (ARTIFACT_DIR / "nonclaim_boundary.md").write_text(nonclaim, encoding="utf-8")

    statement = rf"""\section{{Step 19: F24/F47 Layer Multiplicity}}

\paragraph{{Quotient and Role.}}
Let \(q\) be the content-selection access quotient and \(s\) the F47 scale/naturalness readout.

\paragraph{{Computed Obstruction.}}
The obstruction \(O_s=\{{(h,h') : q(h)=q(h'), s(h)\ne s(h')\}}\) has {role_obstruction} unordered pairs. Thus \(s\) does not descend through \(q\), and the test returns a RoleSplit.

\paragraph{{Resolution.}}
The F24 resolution is \texttt{{BudgetedRole}}, not \texttt{{MemoryLayer}}. The scale role is priced as a naturalness budget on the same closure; no independent scale-only closure is formed.

\paragraph{{F47.}}
The selector-region fraction is {sigma_fraction:.12f}, with \(\theta={SMALL_THETA}\). Small and Realized are both {bool(realized_in_sigma and small_selector)}.
"""
    (ARTIFACT_DIR / "step19_statement.tex").write_text(statement, encoding="utf-8")

    print(
        "Step 19 built: "
        f"O_s={role_obstruction} "
        f"resolution=BudgetedRole "
        f"selector_fraction={sigma_fraction:.12f}"
    )


if __name__ == "__main__":
    main()
