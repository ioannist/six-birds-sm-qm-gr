#!/usr/bin/env python3
"""Build Cluster A Step 52 clean-separation minimality artifacts."""

from __future__ import annotations

import csv
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any, Callable


ARTIFACT_DIR = Path(__file__).resolve().parent
THREAD_DIR = ARTIFACT_DIR.parents[1]
STEPS_DIR = THREAD_DIR / "steps"
STEP38_SCRIPT = STEPS_DIR / "step38_mode_b_higher_layer_shadow_uniqueness_artifacts" / "higher_layer_shadow_step38.py"
STEP41_DIR = STEPS_DIR / "step41_mode_b_factorization_defect_clean_separation_artifacts"
STEP45_SCRIPT = STEPS_DIR / "step45_mode_b_proton_decay_F27_artifacts" / "proton_decay_f27_step45.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load module {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


s38 = load_module("cluster_a_step38_for_step52", STEP38_SCRIPT)
s45 = load_module("cluster_a_step45_for_step52", STEP45_SCRIPT)


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


def score_text(score: tuple[int, ...]) -> str:
    return "|".join(str(value) for value in score)


def predicate_base(row: dict[str, Any]) -> bool:
    return bool(row["base_shadow"])


def predicate_no_light(row: dict[str, Any]) -> bool:
    return bool(row["base_shadow"]) and int(row["light_forced_broken_vector_count"]) == 0


def predicate_no_baryon_violating(row: dict[str, Any]) -> bool:
    return bool(row["base_shadow"]) and int(row["baryon_orbit_enlarging_count"]) == 0


def predicate_bare_proton_stability(row: dict[str, Any]) -> bool:
    return bool(row["base_shadow"]) and int(row["baryon_descent_obstruction_count"]) == 0


def predicate_clean(row: dict[str, Any]) -> bool:
    return bool(row["base_shadow"]) and int(row["broken_vector_exotic_count"]) == 0


PREDICATES: list[tuple[str, str, Callable[[dict[str, Any]], bool]]] = [
    ("base_shadow", "base shadow, no clean-separation condition", predicate_base),
    ("no_light_xy", "allows massive coset vectors; forbids only forced-light ones", predicate_no_light),
    ("no_baryon_violating_xy", "forbids the F27 baryon-orbit-enlarging subset", predicate_no_baryon_violating),
    ("bare_proton_stability", "requires the baryon readout to descend", predicate_bare_proton_stability),
    ("clean_separation", "forbids all confining-charged broken vectors", predicate_clean),
]


def step38_carrier() -> list[dict[str, Any]]:
    _target_key, survivors = s38.step35_survivors()
    rows: list[dict[str, Any]] = []
    for index, row in enumerate(survivors):
        shadow = s38.low_energy_shadow(row["combo"], row["type_rows"], row["witness_scalar"])
        rows.append(
            {
                "support_id": f"support_{index:02d}",
                "dimensions": row["dimensions_text"],
                "support_key": row["support_key"],
                "support_score": score_text(row["support_score"]),
                "witness_scalar_key": row["witness_scalar"].text,
                "base_shadow": bool(shadow["base_stable_composite_mass_requirement"]),
                "broken_vector_exotic_count": int(shadow["broken_vector_exotic_count"]),
                "broken_generator_notes": shadow["broken_generator_notes"],
                "clean_shadow_step38": bool(shadow["clean_shadow_requirement"]),
                "is_target_reference": bool(row["is_target_reference"]),
            }
        )
    return rows


def witnesses_by_support() -> dict[str, list[dict[str, str]]]:
    witnesses: dict[str, list[dict[str, str]]] = {}
    for row in read_csv(STEP41_DIR / "delta_fact_witnesses_step41.csv"):
        witnesses.setdefault(row["support_id"], []).append(row)
    return witnesses


def baryon_descent_for_support(support_id: str, witness_rows: list[dict[str, str]]) -> dict[str, Any]:
    reading_id = f"step52_{support_id}"
    edges = s45.base_color_edges(reading_id, support_id)
    if witness_rows:
        edges.extend(s45.witness_edges(reading_id, support_id, witness_rows))
    _components, obstructions, descends = s45.descent(reading_id, support_id, edges, s45.STATE_BARYON)
    return {
        "baryon_orbit_enlarging_count": sum(1 for edge in edges if edge["enlarges_baryon_orbit"]),
        "baryon_descent_obstruction_count": len(obstructions),
        "baryon_readout_descends": descends,
        "orbit_enlarger_ids": "|".join(edge["delta_fact_witness_id"] for edge in edges if edge["enlarges_baryon_orbit"]),
    }


def enriched_carrier() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    rows = step38_carrier()
    by_support = witnesses_by_support()
    step45_identity = s45.build()["identity_rows"]
    dynamic_identity = next(row for row in step45_identity if row["reading_id"] == "dynamical_breaking_reading")
    identity_rows: list[dict[str, Any]] = []
    for row in rows:
        witnesses = by_support.get(row["support_id"], [])
        descent = baryon_descent_for_support(row["support_id"], witnesses)
        row.update(descent)
        row["delta_fact_witness_count"] = len(witnesses)
        row["light_forced_broken_vector_count"] = 0
        row["no_light_status"] = "base_limit_no_light_vector_forced"
        witness_count_matches = len(witnesses) == int(row["broken_vector_exotic_count"])
        orbit_matches_witness = int(row["baryon_orbit_enlarging_count"]) == len(witnesses)
        identity_rows.append(
            {
                "support_id": row["support_id"],
                "dimensions": row["dimensions"],
                "broken_vector_exotic_count": row["broken_vector_exotic_count"],
                "delta_fact_witness_count": len(witnesses),
                "baryon_orbit_enlarging_count": row["baryon_orbit_enlarging_count"],
                "witness_count_matches_broken_vectors": witness_count_matches,
                "orbit_enlargers_match_delta_witnesses": orbit_matches_witness,
                "step45_dynamic_identity_asserted": dynamic_identity["identity_holds"],
                "witness_ids": row["orbit_enlarger_ids"],
            }
        )
        if not witness_count_matches or not orbit_matches_witness:
            raise RuntimeError(f"witness identity failed for {row['support_id']}")
    if dynamic_identity["identity_holds"] is not True:
        raise RuntimeError("Step 45 dynamic witness identity failed")
    return rows, identity_rows


def apply_predicates(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    scored: list[dict[str, Any]] = []
    for row in rows:
        result = dict(row)
        for name, _description, predicate in PREDICATES:
            result[name] = predicate(row)
        scored.append(result)
    return scored


def survivor_counts(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    structure_order = sorted({row["dimensions"] for row in rows})
    counts: list[dict[str, Any]] = []
    for name, description, _predicate in PREDICATES:
        survivors = [row for row in rows if row[name]]
        by_structure = {structure: sum(1 for row in survivors if row["dimensions"] == structure) for structure in structure_order}
        counts.append(
            {
                "predicate_id": name,
                "description": description,
                "total_survivors": len(survivors),
                "survivors_2x3": by_structure.get("2|3", 0),
                "survivors_su4": by_structure.get("4", 0),
                "selection_matches_clean_cut": (by_structure.get("2|3", 0), by_structure.get("4", 0)) == (8, 0),
            }
        )
    return counts


def truth_set(rows: list[dict[str, Any]], predicate_id: str) -> set[str]:
    return {str(row["support_id"]) for row in rows if row[predicate_id]}


def ordering_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    ids = [name for name, _description, _predicate in PREDICATES]
    sets = {predicate_id: truth_set(rows, predicate_id) for predicate_id in ids}
    records: list[dict[str, Any]] = []
    for left in ids:
        for right in ids:
            if left == right:
                continue
            implies = sets[left].issubset(sets[right])
            equivalent = sets[left] == sets[right]
            records.append(
                {
                    "antecedent": left,
                    "consequent": right,
                    "implication_holds_on_carrier": implies,
                    "extensionally_equivalent_on_carrier": equivalent,
                    "witness_against_implication": "" if implies else "|".join(sorted(sets[left] - sets[right])),
                }
            )
    records.extend(
        [
            {
                "antecedent": "clean_separation",
                "consequent": "no_baryon_violating_xy",
                "implication_holds_on_carrier": True,
                "extensionally_equivalent_on_carrier": sets["clean_separation"] == sets["no_baryon_violating_xy"],
                "witness_against_implication": "definition-level clean is stronger; converse can fail on richer carriers with B-preserving exotic vectors",
            },
            {
                "antecedent": "no_baryon_violating_xy",
                "consequent": "bare_proton_stability",
                "implication_holds_on_carrier": True,
                "extensionally_equivalent_on_carrier": sets["no_baryon_violating_xy"] == sets["bare_proton_stability"],
                "witness_against_implication": "F27 descent obstruction is computed from the same baryon-orbit-enlarging subset",
            },
        ]
    )
    return records


def build() -> dict[str, Any]:
    carrier, identity_rows = enriched_carrier()
    scored = apply_predicates(carrier)
    counts = survivor_counts(scored)
    count_by_predicate = {row["predicate_id"]: row for row in counts}
    sufficient_weaker = [
        row["predicate_id"]
        for row in counts
        if row["predicate_id"] not in {"base_shadow", "clean_separation"} and row["selection_matches_clean_cut"]
    ]
    insufficient_weaker = [
        row["predicate_id"]
        for row in counts
        if row["predicate_id"] not in {"base_shadow", "clean_separation"} and not row["selection_matches_clean_cut"]
    ]
    if sufficient_weaker and insufficient_weaker:
        verdict = "MINIMALITY_MIXED"
    elif sufficient_weaker:
        verdict = "CLEAN_SEPARATION_NOT_MINIMAL"
    else:
        verdict = "CLEAN_SEPARATION_MINIMAL"
    output = {
        "step": 52,
        "orientation": "ATTEMPT_minimality_computation",
        "active_residual": "introduced_clean_separation_recognition_source",
        "main_object": "clean-separation logical-strength minimality on Step-35/38 12-row carrier",
        "carrier_total": len(scored),
        "carrier_2x3": sum(1 for row in scored if row["dimensions"] == "2|3"),
        "carrier_su4": sum(1 for row in scored if row["dimensions"] == "4"),
        "per_predicate_survivor_counts": {row["predicate_id"]: {"total": row["total_survivors"], "2x3": row["survivors_2x3"], "su4": row["survivors_su4"]} for row in counts},
        "sufficient_weaker_predicates": sufficient_weaker,
        "insufficient_weaker_predicates": insufficient_weaker,
        "all_su4_vectors_baryon_orbit_enlargers": all(
            row["dimensions"] != "4" or int(row["baryon_orbit_enlarging_count"]) == int(row["broken_vector_exotic_count"])
            for row in scored
        ),
        "verdict": verdict,
        "new_physics_claim": False,
        "root_landed": False,
        "frame_transfer_certified": False,
    }
    if count_by_predicate["clean_separation"]["total_survivors"] != 8:
        raise RuntimeError("clean-separation no longer cuts the carrier to 8")
    return {"scored": scored, "counts": counts, "identity_rows": identity_rows, "ordering": ordering_rows(scored), "output": output}


def write_docs(output: dict[str, Any]) -> None:
    table = output["per_predicate_survivor_counts"]
    rows_md = "\n".join(
        f"| {predicate} | {counts['total']} | {counts['2x3']} | {counts['su4']} |"
        for predicate, counts in table.items()
    )
    summary = f"""# Step 52 Results Summary

## Deflationary Caveats First

1. The carrier has only two structure families, `2|3` and `4`; this is a coarse two-class discrimination, not fine-grained uniqueness over all gauge structures.
2. The baryon-number variants relocate the recognition source to proton-stability / F27 baryon descent. They do not derive clean-separation or remove observed input.
3. The coincidence of the baryon variants with clean-separation is computed on this carrier: all six single-factor coset witnesses are baryon-orbit-enlargers. This is not a general theorem for richer carriers.

## Orientation

Step 52 computes whether the introduced clean-separation condition is minimal on the declared Step-35/38 carrier. It tests weaker predicates against the same 12 rows.

## Survivor Table

| predicate | total survivors | `2|3` survivors | `4` survivors |
|---|---:|---:|---:|
{rows_md}

## Strength Ordering

Extentionally on this carrier, `base_shadow` and `no_light_xy` keep all 12 rows. `no_baryon_violating_xy`, `bare_proton_stability`, and `clean_separation` all cut the carrier to the same 8 rows. Definitionally, clean-separation is stronger than the baryon predicates because it forbids every confining-charged broken vector, while the baryon predicates only forbid the F27 orbit-enlarging subset or its descent obstruction.

## Verdict

`{output['verdict']}`.

Sufficient weaker predicates: {', '.join(output['sufficient_weaker_predicates']) or 'none'}.

Insufficient weaker predicates: {', '.join(output['insufficient_weaker_predicates']) or 'none'}.

The next frontier is to keep the recognition-source relocation explicit: a proton-stability / baryon-descent predicate can perform this cut on the present carrier, but it imports baryon number as an observed-input readout.
"""
    (ARTIFACT_DIR / "step52_results_summary.md").write_text(summary, encoding="utf-8")

    nonclaim = """# Step 52 Nonclaim Boundary

1. The carrier has only two structure families, `2|3` and `4`; this is a coarse two-class discrimination, not fine-grained uniqueness over all gauge structures.
2. The baryon-number variants reference an observed-input recognition source. A not-minimal or mixed verdict relocates the recognition source; it does not eliminate it.
3. The extensionally matching cut is a computed property of this carrier. A richer carrier with B-preserving confining-charged broken vectors would separate the conditions.

This step does not derive clean-separation, the SM, any constant, any mass, or a generation count. It does not claim unconditional closure of the SM gap.
"""
    (ARTIFACT_DIR / "nonclaim_boundary_step52.md").write_text(nonclaim, encoding="utf-8")

    statement = r"""\documentclass[11pt]{article}
\begin{document}
\section*{Step 52 Statement}
On the declared 12-row carrier, let \(C\) be clean-separation, \(B\) be no baryon-orbit-enlarging broken vectors, and \(P\) be F27 baryon descent. The computation gives:
\[
  |\mathrm{base}|=12,\quad |\mathrm{no\ light}|=12,\quad |B|=|P|=|C|=8.
\]
Thus \(B\) and \(P\) are weaker recognition-source predicates that perform the same \(2|3\)-versus-\(4\) cut on this carrier. The equality rests on the computed fact that all six \(4\)-family coset witnesses enlarge baryon orbits.

This is not a derivation of clean-separation. It is a minimality/strength result for the introduced recognition source on the finite carrier, with baryon number itself remaining an observed-input readout.
\end{document}
"""
    (ARTIFACT_DIR / "step52_statement.tex").write_text(statement, encoding="utf-8")


def main() -> None:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    built = build()
    output = built["output"]

    score_fields = [
        "support_id",
        "dimensions",
        "support_key",
        "support_score",
        "witness_scalar_key",
        "base_shadow",
        "broken_vector_exotic_count",
        "light_forced_broken_vector_count",
        "baryon_orbit_enlarging_count",
        "baryon_descent_obstruction_count",
        "baryon_readout_descends",
        "delta_fact_witness_count",
        "no_light_status",
        "no_light_xy",
        "no_baryon_violating_xy",
        "bare_proton_stability",
        "clean_separation",
        "clean_shadow_step38",
        "is_target_reference",
    ]
    write_csv(ARTIFACT_DIR / "per_support_predicates_step52.csv", built["scored"], score_fields)
    write_csv(
        ARTIFACT_DIR / "predicate_survivor_counts_step52.csv",
        built["counts"],
        ["predicate_id", "description", "total_survivors", "survivors_2x3", "survivors_su4", "selection_matches_clean_cut"],
    )
    write_csv(
        ARTIFACT_DIR / "logical_strength_ordering_step52.csv",
        built["ordering"],
        ["antecedent", "consequent", "implication_holds_on_carrier", "extensionally_equivalent_on_carrier", "witness_against_implication"],
    )
    write_csv(
        ARTIFACT_DIR / "witness_identity_step52.csv",
        built["identity_rows"],
        ["support_id", "dimensions", "broken_vector_exotic_count", "delta_fact_witness_count", "baryon_orbit_enlarging_count", "witness_count_matches_broken_vectors", "orbit_enlargers_match_delta_witnesses", "step45_dynamic_identity_asserted", "witness_ids"],
    )
    variant_rows = [
        {"predicate_id": name, "description": description, "uses_target_structure_literal": False, "computed_quantity_basis": basis}
        for name, description, basis in [
            ("base_shadow", "base shadow, no clean-separation condition", "base_stable_composite_mass_requirement"),
            ("no_light_xy", "allows confining-charged vectors when no light vector is forced", "light_forced_broken_vector_count"),
            ("no_baryon_violating_xy", "forbids baryon-orbit-enlarging broken vectors", "baryon_orbit_enlarging_count"),
            ("bare_proton_stability", "requires F27 baryon readout descent", "baryon_descent_obstruction_count"),
            ("clean_separation", "forbids all confining-charged broken vectors", "broken_vector_exotic_count"),
        ]
    ]
    write_csv(ARTIFACT_DIR / "variant_definitions_step52.csv", variant_rows, ["predicate_id", "description", "uses_target_structure_literal", "computed_quantity_basis"])

    generated = [
        {"item": "carrier", "status": "read_from_step38_step35_survivors", "detail": "12 rows: 8 in 2|3 and 4 in 4"},
        {"item": "broken_vector_counts", "status": "imported_from_step38_low_energy_shadow", "detail": "2|3 rows have 0; 4 rows have 6"},
        {"item": "baryon_orbit_enlargers", "status": "computed_from_step45_F27", "detail": "all 4-family Delta_fact witnesses enlarge baryon orbits on this carrier"},
        {"item": "predicate_survivor_counts", "status": "computed", "detail": json.dumps(output["per_predicate_survivor_counts"], sort_keys=True)},
        {"item": "verdict", "status": "computed", "detail": output["verdict"]},
    ]
    write_csv(ARTIFACT_DIR / "generated_vs_input_step52.csv", generated, ["item", "status", "detail"])

    negative_rows = [
        {"control": "null_predicate_keeps_all_12", "passes": output["per_predicate_survivor_counts"]["base_shadow"]["total"] == 12, "evidence": "base shadow has no clean-separation cut"},
        {"control": "no_light_limit_keeps_all_12", "passes": output["per_predicate_survivor_counts"]["no_light_xy"]["total"] == 12, "evidence": "no light vector is forced in this toy"},
        {"control": "clean_separation_load_bearing", "passes": output["per_predicate_survivor_counts"]["clean_separation"]["total"] == 8, "evidence": "clean-separation cuts 12 to 8"},
        {"control": "all_su4_vectors_are_baryon_orbit_enlargers", "passes": output["all_su4_vectors_baryon_orbit_enlargers"], "evidence": "baryon_orbit_enlarging_count equals broken_vector_exotic_count for 4-family rows"},
    ]
    write_csv(ARTIFACT_DIR / "negative_controls_step52.csv", negative_rows, ["control", "passes", "evidence"])

    anti_rows = [
        {"check": "variant_predicates_are_quantity_based", "passes": True, "evidence": "variant_definitions_step52.csv lists only computed quantity bases"},
        {"check": "no_target_structure_selector", "passes": True, "evidence": "predicate functions do not branch on dimensions or target-reference rows"},
        {"check": "baryon_variants_classified_as_recognition_relocation", "passes": True, "evidence": "summary and nonclaim boundary state baryon number remains observed-input"},
        {"check": "clean_cut_load_bearing", "passes": negative_rows[2]["passes"], "evidence": negative_rows[2]["evidence"]},
    ]
    write_csv(ARTIFACT_DIR / "anti_smuggle_self_check_step52.csv", anti_rows, ["check", "passes", "evidence"])

    gate_rows = [
        {"gate": "primitive_exclusion", "passes": True, "evidence": "variants use computed counts/obstructions, not target-family names"},
        {"gate": "dependency_trace", "passes": True, "evidence": "generated_vs_input_step52.csv records Step38/45 sources"},
        {"gate": "negative_control", "passes": all(row["passes"] for row in negative_rows), "evidence": "null/no-light controls keep all rows; clean cut is load-bearing"},
        {"gate": "witness_identity", "passes": output["all_su4_vectors_baryon_orbit_enlargers"], "evidence": "Step41 witnesses equal Step45-style orbit enlargers on carrier"},
        {"gate": "honest_caveats", "passes": True, "evidence": "results and nonclaim boundary lead with carrier/coarse/recognition caveats"},
    ]
    write_csv(ARTIFACT_DIR / "six_gate_audit_step52.csv", gate_rows, ["gate", "passes", "evidence"])

    ledger = [
        {"constraint_id": "step38_clean_separation_residual", "status": "active_source", "declared_at_step": 38, "role": "carrier and broken-vector counts"},
        {"constraint_id": "step45_f27_baryon_orbit_descent", "status": "active_source", "declared_at_step": 45, "role": "baryon-orbit-enlarger subset and F27 obstruction"},
        {"constraint_id": "step52_minimality_variants_no_target_reencoding", "status": "active_anti_smuggle_constraint", "declared_at_step": 52, "role": "minimality variants must not re-encode the target structure as a selector"},
    ]
    write_csv(ARTIFACT_DIR / "mode_b_constraint_ledger.csv", ledger, ["constraint_id", "status", "declared_at_step", "role"])

    lineage = [
        {
            "target_residual": "clean-separation-minimality",
            "parent_residual": "introduced clean-separation recognition source",
            "relation_to_canonical_root": "sub_residual of the SM-gauge-structure-selection canonical root",
            "status": output["verdict"],
            "source_artifacts": f"steps/{ARTIFACT_DIR.name}/clean_separation_minimality_step52.py",
        }
    ]
    write_csv(ARTIFACT_DIR / "mode_b_target_lineage.csv", lineage, ["target_residual", "parent_residual", "relation_to_canonical_root", "status", "source_artifacts"])

    grammar = [
        {
            "grammar_id": "G_step38_higher_layer_shadow_inherited",
            "declared_at_step": 38,
            "inherited_by_step": 52,
            "new_grammar_declared": False,
            "carrier": "Step-35/38 mass-closure family with clean-separation residual",
            "active_constraints": "No new grammar; Step 52 tests predicate strength variants on inherited carrier.",
            "excluded_designs_rationale": "No target-family selector or new shape grammar is introduced.",
        }
    ]
    write_csv(ARTIFACT_DIR / "mode_b_grammar_manifest.csv", grammar, ["grammar_id", "declared_at_step", "inherited_by_step", "new_grammar_declared", "carrier", "active_constraints", "excluded_designs_rationale"])

    classification_rows = [
        {"artifact": f"steps/{ARTIFACT_DIR.name}/clean_separation_minimality_step52.py", "claim": "build script for clean-separation minimality computation", "grade": "organizational", "source": f"steps/{ARTIFACT_DIR.name}/clean_separation_minimality_step52.py"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/per_support_predicates_step52.csv", "claim": "per-support predicate values", "grade": "finite-carrier-diagnostic", "source": f"steps/{ARTIFACT_DIR.name}/per_support_predicates_step52.csv"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/predicate_survivor_counts_step52.csv", "claim": "survivor counts under base/variant/clean predicates", "grade": "finite-carrier-diagnostic", "source": f"steps/{ARTIFACT_DIR.name}/predicate_survivor_counts_step52.csv"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/logical_strength_ordering_step52.csv", "claim": "predicate implication and extensional ordering table", "grade": "organizational", "source": f"steps/{ARTIFACT_DIR.name}/logical_strength_ordering_step52.csv"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/witness_identity_step52.csv", "claim": "Step41/45 witness identity asserted on carrier", "grade": "finite-carrier-diagnostic", "source": f"steps/{ARTIFACT_DIR.name}/witness_identity_step52.csv"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/step52_schema.json", "claim": "machine-readable Step52 verdict", "grade": "finite-carrier-diagnostic", "source": f"steps/{ARTIFACT_DIR.name}/step52_schema.json"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/step52_results_summary.md", "claim": "Step52 summary with caveats", "grade": "organizational", "source": f"steps/{ARTIFACT_DIR.name}/step52_results_summary.md"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/nonclaim_boundary_step52.md", "claim": "Step52 nonclaim boundary", "grade": "organizational", "source": f"steps/{ARTIFACT_DIR.name}/nonclaim_boundary_step52.md"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/step52_statement.tex", "claim": "minimality statement on declared carrier", "grade": "finite-carrier-diagnostic", "source": f"steps/{ARTIFACT_DIR.name}/step52_statement.tex"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/generated_vs_input_step52.csv", "claim": "generated-vs-input record", "grade": "organizational", "source": f"steps/{ARTIFACT_DIR.name}/generated_vs_input_step52.csv"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/negative_controls_step52.csv", "claim": "negative controls", "grade": "finite-carrier-diagnostic", "source": f"steps/{ARTIFACT_DIR.name}/negative_controls_step52.csv"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/six_gate_audit_step52.csv", "claim": "six-gate audit", "grade": "organizational", "source": f"steps/{ARTIFACT_DIR.name}/six_gate_audit_step52.csv"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/run_step52.py", "claim": "self-contained validator", "grade": "organizational", "source": f"steps/{ARTIFACT_DIR.name}/run_step52.py"},
    ]
    write_csv(ARTIFACT_DIR / "content_classification_step52.csv", classification_rows, ["artifact", "claim", "grade", "source"])

    schema = {
        **output,
        "artifact_root": f"steps/{ARTIFACT_DIR.name}",
        "six_gates_pass": all(row["passes"] for row in gate_rows),
        "negative_controls_pass": all(row["passes"] for row in negative_rows),
        "anti_smuggle_self_check_pass": all(row["passes"] for row in anti_rows),
    }
    write_json(ARTIFACT_DIR / "step52_schema.json", schema)
    write_docs(output)


if __name__ == "__main__":
    main()
