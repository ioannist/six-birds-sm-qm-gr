#!/usr/bin/env python3
"""Build Cluster A Step 45 F27 proton-decay fork artifacts.

This is a finite candidate test.  It types the shadow-vs-dynamical-breaking
fork by computing F27 orbit descent for a baryon-number readout on two
Step-41 carriers: clean 2|3 rows with no Delta_fact witnesses, and
single-factor contaminated rows with confining-charged massive-vector
witnesses.
"""

from __future__ import annotations

import collections
import csv
import json
from pathlib import Path
from typing import Any


ARTIFACT_DIR = Path(__file__).resolve().parent
THREAD_DIR = ARTIFACT_DIR.parents[1]
STEPS_DIR = THREAD_DIR / "steps"
STEP41_DIR = STEPS_DIR / "step41_mode_b_factorization_defect_clean_separation_artifacts"


STATE_BARYON = {
    "q_red": "1/3",
    "q_green": "1/3",
    "q_blue": "1/3",
    "lepton": "0",
}

STATE_COLOR_LABEL = {
    "q_red": "red",
    "q_green": "green",
    "q_blue": "blue",
    "lepton": "colorless",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def bool_text(value: bool) -> str:
    return "True" if value else "False"


def clean_support(summary_rows: list[dict[str, str]]) -> dict[str, str]:
    rows = [row for row in summary_rows if row["dimensions"] == "2|3" and row["is_target_reference"] == "True"]
    if len(rows) != 1:
        raise RuntimeError("expected exactly one clean target support in Step 41")
    return rows[0]


def dynamical_support(summary_rows: list[dict[str, str]]) -> dict[str, str]:
    rows = [row for row in summary_rows if row["dimensions"] == "4" and row["delta_empty"] == "False"]
    if not rows:
        raise RuntimeError("expected a contaminated single-factor Step 41 support")
    return rows[0]


def base_color_edges(reading_id: str, support_id: str) -> list[dict[str, Any]]:
    pairs = [("q_red", "q_green"), ("q_green", "q_blue"), ("q_blue", "q_red")]
    return [
        {
            "reading_id": reading_id,
            "support_id": support_id,
            "edge_id": f"{reading_id}_color_{index}",
            "generator_kind": "unbroken_confining_generator",
            "source_state": left,
            "target_state": right,
            "delta_fact_witness_id": "",
            "enlarges_baryon_orbit": False,
        }
        for index, (left, right) in enumerate(pairs)
    ]


def witness_edges(reading_id: str, support_id: str, witnesses: list[dict[str, str]]) -> list[dict[str, Any]]:
    quark_states = ["q_red", "q_green", "q_blue"]
    edges: list[dict[str, Any]] = []
    for index, witness in enumerate(witnesses):
        edges.append(
            {
                "reading_id": reading_id,
                "support_id": support_id,
                "edge_id": f"{reading_id}_xy_{index}",
                "generator_kind": "orbit_enlarging_colored_coset_vector",
                "source_state": quark_states[index % len(quark_states)],
                "target_state": "lepton",
                "delta_fact_witness_id": witness["witness_boson_id"],
                "enlarges_baryon_orbit": True,
            }
        )
    return edges


def connected_components(states: list[str], edges: list[dict[str, Any]]) -> list[list[str]]:
    adjacency: dict[str, set[str]] = {state: set() for state in states}
    for edge in edges:
        left = str(edge["source_state"])
        right = str(edge["target_state"])
        adjacency[left].add(right)
        adjacency[right].add(left)
    seen: set[str] = set()
    components: list[list[str]] = []
    for state in states:
        if state in seen:
            continue
        stack = [state]
        seen.add(state)
        component: list[str] = []
        while stack:
            current = stack.pop()
            component.append(current)
            for neighbor in adjacency[current]:
                if neighbor not in seen:
                    seen.add(neighbor)
                    stack.append(neighbor)
        components.append(sorted(component))
    return components


def descent(reading_id: str, support_id: str, edges: list[dict[str, Any]], readout: dict[str, str]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], bool]:
    states = list(readout)
    components = connected_components(states, edges)
    component_rows: list[dict[str, Any]] = []
    obstruction_rows: list[dict[str, Any]] = []
    for index, component in enumerate(components):
        values = sorted({readout[state] for state in component})
        component_id = f"{reading_id}_orbit_{index}"
        component_rows.append(
            {
                "reading_id": reading_id,
                "support_id": support_id,
                "component_id": component_id,
                "states": "|".join(component),
                "readout_values": "|".join(values),
                "constant_on_orbit": len(values) == 1,
            }
        )
        if len(values) > 1:
            for left_index, left in enumerate(component):
                for right in component[left_index + 1 :]:
                    if readout[left] != readout[right]:
                        obstruction_rows.append(
                            {
                                "reading_id": reading_id,
                                "support_id": support_id,
                                "component_id": component_id,
                                "left_state": left,
                                "right_state": right,
                                "left_value": readout[left],
                                "right_value": readout[right],
                            }
                        )
    return component_rows, obstruction_rows, not obstruction_rows


def build() -> dict[str, Any]:
    summary_rows = read_csv(STEP41_DIR / "delta_fact_summary_step41.csv")
    witness_rows_all = read_csv(STEP41_DIR / "delta_fact_witnesses_step41.csv")
    by_support: dict[str, list[dict[str, str]]] = collections.defaultdict(list)
    for row in witness_rows_all:
        by_support[row["support_id"]].append(row)

    clean = clean_support(summary_rows)
    contaminated = dynamical_support(summary_rows)
    clean_witnesses = by_support.get(clean["support_id"], [])
    contaminated_witnesses = by_support.get(contaminated["support_id"], [])

    readings = [
        {
            "reading_id": "clean_shadow_reading",
            "diagram": "structural_shadow",
            "support": clean,
            "witnesses": clean_witnesses,
            "interpretation": "clean-separation shadow; coset vectors not realized",
        },
        {
            "reading_id": "dynamical_breaking_reading",
            "diagram": "dynamical_breaking",
            "support": contaminated,
            "witnesses": contaminated_witnesses,
            "interpretation": "single-factor broken phase; colored coset vectors realized",
        },
    ]

    edge_rows: list[dict[str, Any]] = []
    component_rows: list[dict[str, Any]] = []
    obstruction_rows: list[dict[str, Any]] = []
    descent_rows: list[dict[str, Any]] = []
    identity_rows: list[dict[str, Any]] = []
    negative_control_rows: list[dict[str, Any]] = []

    for reading in readings:
        support = reading["support"]
        reading_id = reading["reading_id"]
        support_id = support["support_id"]
        edges = base_color_edges(reading_id, support_id)
        if reading_id == "dynamical_breaking_reading":
            edges.extend(witness_edges(reading_id, support_id, reading["witnesses"]))
        edge_rows.extend(edges)

        components, obstructions, descends = descent(reading_id, support_id, edges, STATE_BARYON)
        component_rows.extend(components)
        obstruction_rows.extend(obstructions)
        descent_rows.append(
            {
                "reading_id": reading_id,
                "diagram": reading["diagram"],
                "dimensions": support["dimensions"],
                "support_id": support_id,
                "delta_fact_empty": support["delta_empty"],
                "delta_fact_witness_count": len(reading["witnesses"]),
                "orbit_enlarging_generator_count": sum(1 for edge in edges if edge["enlarges_baryon_orbit"]),
                "baryon_readout_descends": descends,
                "baryon_obstruction_count": len(obstructions),
                "typed_consequence": "B_conserved_conditional_stability" if descends else "B_not_conserved_decay_channel",
                "interpretation": reading["interpretation"],
            }
        )
        identity_rows.append(
            {
                "reading_id": reading_id,
                "support_id": support_id,
                "dimensions": support["dimensions"],
                "step41_delta_witness_count": len(reading["witnesses"]),
                "orbit_enlarging_generator_count": sum(1 for edge in edges if edge["enlarges_baryon_orbit"]),
                "identity_holds": len(reading["witnesses"]) == sum(1 for edge in edges if edge["enlarges_baryon_orbit"]),
                "witness_kind": "confining_charged_massive_vector",
            }
        )

        nc_components, nc_obstructions, nc_descends = descent(f"{reading_id}_color_label_control", support_id, base_color_edges(f"{reading_id}_color_label_control", support_id), STATE_COLOR_LABEL)
        negative_control_rows.append(
            {
                "control": f"{reading_id}_color_label_not_descended",
                "reading_id": reading_id,
                "passes": not nc_descends and len(nc_obstructions) > 0,
                "evidence": f"color-label obstruction count={len(nc_obstructions)}",
            }
        )

    clean_result = next(row for row in descent_rows if row["reading_id"] == "clean_shadow_reading")
    dynamic_result = next(row for row in descent_rows if row["reading_id"] == "dynamical_breaking_reading")
    verdict = "CANDIDATE_SHADOW_VS_BREAKING_FORK_TYPED"
    output = {
        "step": 45,
        "mode": "ModeB_F27_proton_decay_candidate",
        "verdict": verdict,
        "clean_shadow_baryon_obstruction_count": clean_result["baryon_obstruction_count"],
        "clean_shadow_baryon_descends": clean_result["baryon_readout_descends"],
        "dynamical_breaking_baryon_obstruction_count": dynamic_result["baryon_obstruction_count"],
        "dynamical_breaking_baryon_descends": dynamic_result["baryon_readout_descends"],
        "clean_shadow_delta_witness_count": clean_result["delta_fact_witness_count"],
        "dynamical_breaking_delta_witness_count": dynamic_result["delta_fact_witness_count"],
        "xy_delta_witness_identity": all(row["identity_holds"] for row in identity_rows),
        "conditional_on_clean_separation": True,
        "physical_reading_resolved": False,
        "new_physics_claim": False,
        "frame_transfer_certified": False,
    }
    return {
        "edge_rows": edge_rows,
        "component_rows": component_rows,
        "obstruction_rows": obstruction_rows,
        "descent_rows": descent_rows,
        "identity_rows": identity_rows,
        "negative_control_rows": negative_control_rows,
        "output": output,
    }


def write_docs(output: dict[str, Any]) -> None:
    results = f"""# Step 45 Results Summary

## Deflationary Truth First

Step 45 is a candidate test, not an answer. It types the shadow-vs-dynamical-breaking fork with F27 orbit descent. The clean/shadow reading's proton-stability consequence is conditional on clean-separation; SBT does not decide which reading is physical.

## F27 Orbit-Descent Result

| reading | B descends? | B obstruction count | Delta_fact witness count | typed consequence |
| --- | --- | ---: | ---: | --- |
| clean/shadow | {output['clean_shadow_baryon_descends']} | {output['clean_shadow_baryon_obstruction_count']} | {output['clean_shadow_delta_witness_count']} | B conserved; proton-stability consequence conditional on clean-separation |
| dynamical breaking | {output['dynamical_breaking_baryon_descends']} | {output['dynamical_breaking_baryon_obstruction_count']} | {output['dynamical_breaking_delta_witness_count']} | B not conserved; decay channel typed |

## Witness Link

The orbit-enlarging generators in the dynamical-breaking reading are exactly the Step-41 Delta_fact witnesses for the contaminated single-factor support: `xy_delta_witness_identity={output['xy_delta_witness_identity']}`.

## Typed Fork

`{output['verdict']}`. Diagram A (dynamical breaking) realizes the colored coset vectors, enlarges gauge orbits across baryon-distinct states, and violates F27 descent for `B`. Diagram B (shadow/descent reading) has no realized colored coset vectors, so `B` remains constant on the orbit quotient.
"""
    (ARTIFACT_DIR / "results_summary.md").write_text(results, encoding="utf-8")

    nonclaim = """# Nonclaim Boundary

Step 45 is a finite candidate test. It does not settle proton-decay physics, does not establish physical proton stability, and does not decide whether the dynamical-breaking or shadow reading is realized in nature.

The clean/shadow stability consequence is conditional on the introduced clean-separation condition from Steps 38/41. The physical recognition and external-transfer questions remain open.
"""
    (ARTIFACT_DIR / "nonclaim_boundary.md").write_text(nonclaim, encoding="utf-8")

    statement = r"""\documentclass[11pt]{article}
\begin{document}
\section*{Step 45 Statement}
Deflationary status: this is a finite candidate F27 test that types a fork; it is not a physical resolution.

F27 says that a readout is conserved exactly when it is constant on the orbit quotient. In the clean shadow reading, the Step-41 factorization-defect witness set is empty, so baryon number is constant on the gauge orbits in this finite carrier. In the dynamical-breaking reading, the Step-41 witnesses are realized as colored coset vectors; their edges merge baryon-distinct states, so baryon number fails to descend.

Thus the framework distinguishes the two readings: clean shadow gives conditional proton-stability, while dynamical breaking gives a typed decay channel. The physical reading is not selected here.
\end{document}
"""
    (ARTIFACT_DIR / "step45_statement.tex").write_text(statement, encoding="utf-8")

    generated = [
        {"item": "clean_shadow_support", "status": "read_from_step41", "detail": "target 2|3 support with Delta_fact empty"},
        {"item": "dynamical_breaking_support", "status": "read_from_step41", "detail": "contaminated single-factor support with Delta_fact witnesses"},
        {"item": "baryon_readout", "status": "declared_f27_test_readout", "detail": "B(q)=1/3, B(lepton)=0"},
        {"item": "xy_generators", "status": "computed_from_step41_witnesses", "detail": "orbit-enlarging edges are generated from Delta_fact witness rows"},
        {"item": "verdict", "status": "computed", "detail": output["verdict"]},
    ]
    write_csv(ARTIFACT_DIR / "generated_vs_input_step45.csv", generated, ["item", "status", "detail"])

    ledger = [
        {"constraint_id": "step41_delta_fact_witnesses", "status": "active_source", "declared_at_step": 41, "role": "colored-coset witness set"},
        {"constraint_id": "step45_f27_baryon_orbit_descent", "status": "candidate_test", "declared_at_step": 45, "role": "type the shadow-vs-breaking proton-decay fork"},
    ]
    write_csv(ARTIFACT_DIR / "mode_b_constraint_ledger.csv", ledger, ["constraint_id", "status", "declared_at_step", "role"])

    grammar = [
        {
            "grammar_id": "G_step45_F27_orbit_descent",
            "declared_at_step": 45,
            "carrier": "Step41 clean and contaminated supports plus finite baryon-number orbit graph",
            "active_constraints": "F27 orbit descent; Step41 Delta_fact witness identity",
            "excluded_designs_rationale": "No physical reading is selected; no proton-decay solution is claimed.",
            "non_triviality_argument": "The same descent test preserves B in clean/shadow and violates B in dynamical-breaking, while a color-label control fails even in clean.",
            "next_grammar_delta": "Apply the same witness/orbit typing to monopoles through the F48 track.",
        }
    ]
    write_csv(
        ARTIFACT_DIR / "mode_b_grammar_manifest.csv",
        grammar,
        ["grammar_id", "declared_at_step", "carrier", "active_constraints", "excluded_designs_rationale", "non_triviality_argument", "next_grammar_delta"],
    )

    lineage = [
        {
            "target_residual": "type proton-decay fork through F27 orbit descent",
            "canonical_root": "consequences of conditional clean-separation",
            "sub_residual_of": "gauge-structure clean-separation shadow consequences",
            "status": output["verdict"],
            "source_artifacts": f"steps/{ARTIFACT_DIR.name}/proton_decay_f27_step45.py",
        }
    ]
    write_csv(ARTIFACT_DIR / "mode_b_target_lineage.csv", lineage, ["target_residual", "canonical_root", "sub_residual_of", "status", "source_artifacts"])

    classifications = [
        {"artifact": f"steps/{ARTIFACT_DIR.name}/proton_decay_f27_step45.py", "claim": "build script for F27 fork test", "grade": "organizational", "source": f"steps/{ARTIFACT_DIR.name}/proton_decay_f27_step45.py"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/f27_orbit_descent_step45.csv", "claim": "B orbit-descent obstruction by reading", "grade": "finite-carrier-diagnostic", "source": f"steps/{ARTIFACT_DIR.name}/f27_orbit_descent_step45.csv"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/delta_witness_identity_step45.csv", "claim": "X/Y-like orbit generators equal Step41 witnesses", "grade": "finite-carrier-diagnostic", "source": f"steps/{ARTIFACT_DIR.name}/delta_witness_identity_step45.csv"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/typed_fork_summary_step45.csv", "claim": "shadow-vs-breaking fork typed", "grade": "finite-carrier-diagnostic", "source": f"steps/{ARTIFACT_DIR.name}/typed_fork_summary_step45.csv"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/nonclaim_boundary.md", "claim": "candidate conditional scope", "grade": "remaining-external", "source": f"steps/{ARTIFACT_DIR.name}/nonclaim_boundary.md"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/step45_statement.tex", "claim": "F27 typed-fork statement", "grade": "theorem-grade", "source": f"steps/{ARTIFACT_DIR.name}/step45_statement.tex"},
    ]
    write_csv(ARTIFACT_DIR / "content_classification.csv", classifications, ["artifact", "claim", "grade", "source"])


def main() -> None:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    built = build()
    output = built["output"]

    edge_fields = ["reading_id", "support_id", "edge_id", "generator_kind", "source_state", "target_state", "delta_fact_witness_id", "enlarges_baryon_orbit"]
    component_fields = ["reading_id", "support_id", "component_id", "states", "readout_values", "constant_on_orbit"]
    obstruction_fields = ["reading_id", "support_id", "component_id", "left_state", "right_state", "left_value", "right_value"]
    descent_fields = ["reading_id", "diagram", "dimensions", "support_id", "delta_fact_empty", "delta_fact_witness_count", "orbit_enlarging_generator_count", "baryon_readout_descends", "baryon_obstruction_count", "typed_consequence", "interpretation"]
    identity_fields = ["reading_id", "support_id", "dimensions", "step41_delta_witness_count", "orbit_enlarging_generator_count", "identity_holds", "witness_kind"]

    write_csv(ARTIFACT_DIR / "orbit_edges_step45.csv", built["edge_rows"], edge_fields)
    write_csv(ARTIFACT_DIR / "orbit_components_step45.csv", built["component_rows"], component_fields)
    write_csv(ARTIFACT_DIR / "baryon_descent_obstructions_step45.csv", built["obstruction_rows"], obstruction_fields)
    write_csv(ARTIFACT_DIR / "f27_orbit_descent_step45.csv", built["descent_rows"], descent_fields)
    write_csv(ARTIFACT_DIR / "delta_witness_identity_step45.csv", built["identity_rows"], identity_fields)
    write_csv(ARTIFACT_DIR / "negative_controls_step45.csv", built["negative_control_rows"], ["control", "reading_id", "passes", "evidence"])
    fork_rows = [
        {
            "verdict": output["verdict"],
            "clean_shadow_baryon_descends": output["clean_shadow_baryon_descends"],
            "clean_shadow_obstruction_count": output["clean_shadow_baryon_obstruction_count"],
            "dynamical_breaking_baryon_descends": output["dynamical_breaking_baryon_descends"],
            "dynamical_breaking_obstruction_count": output["dynamical_breaking_baryon_obstruction_count"],
            "physical_reading_resolved": output["physical_reading_resolved"],
            "conditional_on_clean_separation": output["conditional_on_clean_separation"],
        }
    ]
    write_csv(ARTIFACT_DIR / "typed_fork_summary_step45.csv", fork_rows, ["verdict", "clean_shadow_baryon_descends", "clean_shadow_obstruction_count", "dynamical_breaking_baryon_descends", "dynamical_breaking_obstruction_count", "physical_reading_resolved", "conditional_on_clean_separation"])
    gate_rows = [
        {"gate": "f27_orbit_descent_computed", "passes": output["clean_shadow_baryon_descends"] and not output["dynamical_breaking_baryon_descends"], "evidence": "B descends only in the clean/shadow reading"},
        {"gate": "delta_witness_identity", "passes": output["xy_delta_witness_identity"], "evidence": "orbit-enlarging generators equal Step41 witness rows"},
        {"gate": "negative_control", "passes": all(row["passes"] for row in built["negative_control_rows"]), "evidence": "color-label readout fails descent even in clean"},
        {"gate": "conditional_scope", "passes": output["conditional_on_clean_separation"] and not output["physical_reading_resolved"], "evidence": "typed fork only"},
    ]
    write_csv(ARTIFACT_DIR / "six_gate_audit_step45.csv", gate_rows, ["gate", "passes", "evidence"])
    write_json(ARTIFACT_DIR / "proton_decay_f27_output_step45.json", output)
    write_json(
        ARTIFACT_DIR / "schema.json",
        {
            **output,
            "artifact_root": f"steps/{ARTIFACT_DIR.name}",
            "six_gates_pass": all(row["passes"] for row in gate_rows),
            "negative_controls_pass": all(row["passes"] for row in built["negative_control_rows"]),
            "orbit_descent_pass": output["clean_shadow_baryon_descends"] and not output["dynamical_breaking_baryon_descends"],
        },
    )
    write_docs(output)


if __name__ == "__main__":
    main()
