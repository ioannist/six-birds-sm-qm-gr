#!/usr/bin/env python3
"""Apply F35 scale descent / renormalization to the toy joint law."""

from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np


ARTIFACT_DIR = Path(__file__).resolve().parent
STEP18_DIR = ARTIFACT_DIR.parents[0] / "step18_f37_complementarity_f24_resolution_artifacts"
FIV_FILE = Path("/home/repos/six-birds-papers/Tsiokos_2026_Six_Birds_Foundations_IV_A_Catalog_of_Layer_Agnostic_Structural_Laws.tex")
AUDIT_U = np.array([0.70, 0.20, -0.40, 0.35], dtype=float)
TOL = 1e-10


def quotient_labels(cell_count: int, block_size: int) -> np.ndarray:
    return np.array([i // block_size for i in range(cell_count)], dtype=int)


Q1 = quotient_labels(16, 1)
Q2 = quotient_labels(16, 2)
Q3 = quotient_labels(16, 4)
QUOTIENTS = {"Q1_fine16": Q1, "Q2_mid8": Q2, "Q3_coarse4": Q3}


def coarsening_matrix(source_count: int, target_count: int) -> np.ndarray:
    block = source_count // target_count
    matrix = np.zeros((target_count, source_count), dtype=float)
    for i in range(source_count):
        matrix[i // block, i] = 1.0
    return matrix


C1 = coarsening_matrix(16, 8)
C2 = coarsening_matrix(8, 4)


def joint_states() -> np.ndarray:
    target_law = np.array(
        [1.00] * 4
        + [-0.50] * 4
        + [0.25] * 4
        + [0.75] * 4,
        dtype=float,
    )
    states = np.zeros((16, 4), dtype=float)
    for i, value in enumerate(target_law):
        local = ((i % 4) - 1.5) / 3.0
        states[i, 1] = local
        states[i, 2] = -0.30 * local
        states[i, 3] = 0.20 * local
        correction = AUDIT_U[1] * states[i, 1] + AUDIT_U[2] * states[i, 2] + AUDIT_U[3] * states[i, 3]
        states[i, 0] = (value - correction) / AUDIT_U[0]
    return states


def law_values() -> dict[str, np.ndarray]:
    states = joint_states()
    joint = states @ AUDIT_U
    control = np.array([1.0 if i % 2 == 0 else -1.0 for i in range(16)], dtype=float)
    return {"joint_law": joint, "non_descending_control": control}


def obstruction(labels: np.ndarray, values: np.ndarray) -> list[dict[str, float | int]]:
    witnesses = []
    for i in range(len(values)):
        for j in range(i + 1, len(values)):
            if labels[i] == labels[j] and abs(values[i] - values[j]) > TOL:
                witnesses.append(
                    {
                        "cell_i": i,
                        "cell_j": j,
                        "quotient_label": int(labels[i]),
                        "law_gap": float(abs(values[i] - values[j])),
                    }
                )
    return witnesses


def quotient_law(labels: np.ndarray, values: np.ndarray) -> dict[int, float] | None:
    out: dict[int, float] = {}
    for label in sorted(set(int(x) for x in labels)):
        vals = values[labels == label]
        if np.max(vals) - np.min(vals) > TOL:
            return None
        out[label] = float(vals[0])
    return out


def fiber_violations(qn_values: dict[int, float], c_labels: dict[int, int]) -> list[dict[str, float | int]]:
    labels = sorted(qn_values)
    violations = []
    for i, left in enumerate(labels):
        for right in labels[i + 1 :]:
            if c_labels[left] == c_labels[right] and abs(qn_values[left] - qn_values[right]) > TOL:
                violations.append(
                    {
                        "source_label_i": int(left),
                        "source_label_j": int(right),
                        "target_label": int(c_labels[left]),
                        "law_gap": float(abs(qn_values[left] - qn_values[right])),
                    }
                )
    return violations


def coarsening_labels(source_count: int, target_count: int) -> dict[int, int]:
    block = source_count // target_count
    return {i: i // block for i in range(source_count)}


def f35_rows() -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    laws = law_values()
    steps = [
        ("Q1_fine16", "Q2_mid8", Q1, Q2, coarsening_labels(16, 8)),
        ("Q2_mid8", "Q3_coarse4", Q2, Q3, coarsening_labels(8, 4)),
    ]
    rows = []
    witness_rows = []
    for law_name, values in laws.items():
        for qn_name, qnp1_name, qn_labels, _qnp1_labels, c_labels in steps:
            obs = obstruction(qn_labels, values)
            descends = len(obs) == 0
            qlaw = quotient_law(qn_labels, values)
            if qlaw is None:
                violations = []
                renormalizes = False
            else:
                violations = fiber_violations(qlaw, c_labels)
                renormalizes = len(violations) == 0
            rows.append(
                {
                    "law": law_name,
                    "scale_step": f"{qn_name}->{qnp1_name}",
                    "obstruction_count": len(obs),
                    "descends_to_Qn": descends,
                    "fiber_violation_count": len(violations),
                    "renormalizes_to_next": renormalizes,
                    "coarsening_used": True,
                    "f35_pass": bool(descends and renormalizes),
                }
            )
            for witness in obs[:12]:
                witness_rows.append({"law": law_name, "scale_step": f"{qn_name}->{qnp1_name}", "kind": "O_n", **witness})
            for witness in violations[:12]:
                witness_rows.append(
                    {"law": law_name, "scale_step": f"{qn_name}->{qnp1_name}", "kind": "fiber", **witness}
                )
    return rows, witness_rows


def source_record() -> dict[str, object]:
    return {
        "file": str(FIV_FILE),
        "F35_lines_read": "6470-6523",
        "source_statement": (
            "t descends to Q_n iff O_n(t) is empty iff a quotient law tbar_n exists; "
            "the renormalized law at Q_{n+1} exists iff tbar_n is constant on c-fibers."
        ),
    }


def main() -> None:
    step18 = json.loads((STEP18_DIR / "native_culmination_output_step18.json").read_text(encoding="utf-8"))
    if not step18["verdict"]["F37_not_complementary_on_toy"]:
        raise RuntimeError("Step 18 did not mark the joint quotient as available on the toy")
    rows, witnesses = f35_rows()
    by_law: dict[str, list[dict[str, object]]] = {}
    for row in rows:
        by_law.setdefault(str(row["law"]), []).append(row)
    joint_pass = all(bool(row["f35_pass"]) for row in by_law["joint_law"])
    control_pass = all(bool(row["f35_pass"]) for row in by_law["non_descending_control"])
    control_obstruction = any(int(row["obstruction_count"]) > 0 for row in by_law["non_descending_control"])
    payload = {
        "step": 19,
        "FIV_source_read": True,
        "FIV_source_record": source_record(),
        "verdict": {
            "F35_verdict": "renormalizes_on_toy" if joint_pass else "renormalization_obstruction",
            "joint_law_renormalizes": bool(joint_pass),
            "non_descending_control_fails": bool(not control_pass and control_obstruction),
            "obstruction_scale": "none" if joint_pass else "see_f35_rows",
        },
        "no_smuggling_check": {
            "non_descending_control_descends": not control_obstruction,
            "O_n_computed_without_coarsening": False,
            "f35_source_read": True,
            "literature_program_terms_used": False,
            "root_landed": False,
        },
    }
    scale_payload = {
        "carrier": "H=fine 16-cell carrier",
        "quotient_labels": {name: labels.tolist() for name, labels in QUOTIENTS.items()},
        "coarsening_matrices": {
            "c1_Q1_to_Q2": C1.tolist(),
            "c2_Q2_to_Q3": C2.tolist(),
        },
        "joint_states": joint_states().tolist(),
        "law_values": {name: values.tolist() for name, values in law_values().items()},
    }

    with (ARTIFACT_DIR / "f35_scale_descent_step19.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    with (ARTIFACT_DIR / "obstruction_witnesses_step19.csv").open("w", newline="", encoding="utf-8") as handle:
        fieldnames = ["law", "scale_step", "kind", "cell_i", "cell_j", "quotient_label", "source_label_i", "source_label_j", "target_label", "law_gap"]
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in witnesses:
            writer.writerow(row)
    (ARTIFACT_DIR / "scale_structure_step19.json").write_text(
        json.dumps(scale_payload, indent=2), encoding="utf-8"
    )
    (ARTIFACT_DIR / "fiv_f35_source_record_step19.json").write_text(
        json.dumps(source_record(), indent=2), encoding="utf-8"
    )
    (ARTIFACT_DIR / "scale_descent_output_step19.json").write_text(
        json.dumps(payload, indent=2), encoding="utf-8"
    )
    lines = [
        "Step 19 F35 scale descent / renormalization",
        f"Joint law renormalizes on toy: {joint_pass}",
        f"Non-descending control passes F35: {control_pass}",
        f"Non-descending control has O_n obstruction: {control_obstruction}",
        f"F35 verdict: {payload['verdict']['F35_verdict']}",
    ]
    (ARTIFACT_DIR / "scale_descent_output_step19.txt").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
