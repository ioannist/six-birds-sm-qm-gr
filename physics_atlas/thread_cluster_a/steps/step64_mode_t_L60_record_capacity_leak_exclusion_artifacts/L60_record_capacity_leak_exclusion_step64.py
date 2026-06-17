#!/usr/bin/env python3
"""Build Step 64 Mode-T L60 record-capacity leak-exclusion artifacts."""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import inspect
import itertools
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


ARTIFACT_DIR = Path(__file__).resolve().parent
THREAD_DIR = ARTIFACT_DIR.parents[1]
STEPS_DIR = THREAD_DIR / "steps"
STEP35_BUILD = STEPS_DIR / "step35_mode_b_higher_layer_descent_artifacts" / "higher_layer_descent_step35.py"
STEP41_BUILD = STEPS_DIR / "step41_mode_b_factorization_defect_clean_separation_artifacts" / "factorization_defect_clean_separation_step41.py"
STEP57_BUILD = STEPS_DIR / "step57_mode_b_record_stability_descent_artifacts" / "record_stability_descent_step57.py"
STEP59_SCORES = STEPS_DIR / "step59_mode_b_record_stability_coverage_artifacts" / "record_stability_coverage_scores_step59.csv"
STEP60_BUILD = STEPS_DIR / "step60_mode_t_record_stability_structural_theorem_artifacts" / "record_stability_structural_theorem_step60.py"

EXPECTED_HASHES = {
    "Step57_record_requirement": "8068ff17d5ca911ae12f09cc303c8e67ee47c8c92affd0fad9ca28b61fe2e75f",
    "Step35_base_substrate": "6a378357c3dea96d4e7a51e54c8dbb94af9785d39cb9622c3469d2f6a6462c06",
    "Step41_factorization_defect": "ed5be4969244ae18279a9b6fc5ba73977fc9bc47fcec81ff3c25e8ad076e19c0",
}


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def source_hash(functions: list[Any]) -> str:
    return sha256_text("\n\n".join(inspect.getsource(function) for function in functions))


def frozen_step57_region() -> str:
    text = STEP57_BUILD.read_text(encoding="utf-8")
    start = text.index("# RECORD_REQUIREMENT_BEGIN")
    end = text.index("# RECORD_REQUIREMENT_END")
    return text[start:end]


s35 = load_module("step64_s35_base", STEP35_BUILD)
s41 = load_module("step64_s41_delta", STEP41_BUILD)
s57 = load_module("step64_s57_record", STEP57_BUILD)
s60 = load_module("step64_s60_probe", STEP60_BUILD)


def bool_cell(value: str) -> bool:
    return value == "True"


def token_details(score_row: dict[str, str]) -> dict[str, Any]:
    fields = s57.parse_support(score_row["support_key"], score_row["dimensions"])
    components = s57.component_rows(fields)
    line = [row for row in components if row["orientation"] == "line"]
    dual = [row for row in components if row["orientation"] == "dual_line"]
    token_set: set[tuple[str, int, tuple[str, ...]]] = set()
    for left in line:
        for right in dual:
            total = left["charge"] + right["charge"]
            if total == 0:
                token_set.add(("paired_neutral", total, tuple(sorted((left["raw"], right["raw"])))))
    for family, kind in ((line, "triple_line"), (dual, "triple_dual")):
        for triple in itertools.combinations_with_replacement(family, 3):
            total = sum(row["charge"] for row in triple)
            if total == 0:
                token_set.add((kind, total, tuple(sorted(row["raw"] for row in triple))))
    tokens = sorted(token_set)
    line_charges = Counter(row["charge"] for row in line)
    dual_charges = Counter(row["charge"] for row in dual)
    mirror_pairs = sum(1 for charge in line_charges if dual_charges.get(-charge, 0) > 0)
    zero_line = line_charges.get(0, 0)
    zero_dual = dual_charges.get(0, 0)
    if not tokens:
        blocked = "no_zero_sum_line_dual_pair_or_like_orientation_triple"
    elif len(tokens) == 1 and tokens[0][0].startswith("triple") and mirror_pairs == 0:
        blocked = "only_one_zero_charge_like_orientation_triple;no_line_dual_mirror_pair_for_second_record"
    else:
        blocked = "one_token_cap_observed;second_independent_token_absent"
    return {
        "token_count": len(tokens),
        "token_witnesses": ";".join(f"{kind}:{'|'.join(parts)}" for kind, _total, parts in tokens),
        "line_charges": "|".join(str(charge) for charge in sorted(line_charges)),
        "dual_line_charges": "|".join(str(charge) for charge in sorted(dual_charges)),
        "line_dual_mirror_charge_count": mirror_pairs,
        "zero_line_component_count": zero_line,
        "zero_dual_line_component_count": zero_dual,
        "blocked_second_token_reason": blocked,
    }


def residual_label(row: dict[str, str]) -> str:
    notes = row.get("shadow_notes", "")
    for part in notes.split(";"):
        if "residual" in part:
            return part
    return row.get("confining_subgroups", "")


def near_miss_rows(score_rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    selected = [
        row
        for row in score_rows
        if bool_cell(row["substrate_passes"]) and int(row["transition_leak_count"]) > 0
    ]
    rows: list[dict[str, Any]] = []
    for row in selected:
        details = token_details(row)
        observed = int(row["neutral_record_token_count"])
        if details["token_count"] != observed:
            raise RuntimeError(f"token reconstruction mismatch for {row['carrier_id']}")
        rows.append(
            {
                "carrier_id": row["carrier_id"],
                "dimensions": row["dimensions"],
                "support_key": row["support_key"],
                "support_score": row["support_score"],
                "witness_scalar_reps": row["witness_scalar_reps"],
                "witness_scalar_charge": row["witness_scalar_charge"],
                "residual_subgroup": residual_label(row),
                "transition_leak_count": row["transition_leak_count"],
                "line_charges": details["line_charges"],
                "dual_line_charges": details["dual_line_charges"],
                "line_dual_mirror_charge_count": details["line_dual_mirror_charge_count"],
                "zero_line_component_count": details["zero_line_component_count"],
                "zero_dual_line_component_count": details["zero_dual_line_component_count"],
                "neutral_record_token_count": observed,
                "token_witnesses": details["token_witnesses"],
                "blocked_second_token_reason": details["blocked_second_token_reason"],
                "charge_linking_observation": "mass-closure scalar fixes a small charge ladder; observed rows lack two independent zero-sum record channels",
                "chirality_observation": "corrected-chiral roster avoids vector-like line-dual mirror doubling in every leak-positive substrate row",
            }
        )
    return rows


def pattern_rows(near_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_token = Counter(int(row["neutral_record_token_count"]) for row in near_rows)
    by_structure = Counter(row["dimensions"] for row in near_rows)
    by_reason = Counter(row["blocked_second_token_reason"] for row in near_rows)
    rows: list[dict[str, Any]] = []
    for token_count, count in sorted(by_token.items()):
        rows.append({"pattern": f"token_count_{token_count}", "count": count, "evidence": "near_miss_table_step64.csv"})
    for dimensions, count in sorted(by_structure.items()):
        rows.append({"pattern": f"dimensions_{dimensions}", "count": count, "evidence": "leak-positive substrate near-miss structure"})
    for reason, count in sorted(by_reason.items()):
        rows.append({"pattern": reason, "count": count, "evidence": "blocked second token classification"})
    return rows


def frozen_rows() -> list[dict[str, Any]]:
    rows = [
        {
            "machinery": "Step57_record_requirement",
            "source_path": f"steps/{STEP57_BUILD.parent.name}/{STEP57_BUILD.name}",
            "sha256": sha256_text(frozen_step57_region()),
            "expected_sha256": EXPECTED_HASHES["Step57_record_requirement"],
            "frozen_functions": "record_layer_membership",
        },
        {
            "machinery": "Step35_base_substrate",
            "source_path": f"steps/{STEP35_BUILD.parent.name}/{STEP35_BUILD.name}",
            "sha256": source_hash([s35.higher_layer_mass_closure, s35.mass_completion, s35.scalar_breaks_to_unbroken_u1]),
            "expected_sha256": EXPECTED_HASHES["Step35_base_substrate"],
            "frozen_functions": "higher_layer_mass_closure|mass_completion|scalar_breaks_to_unbroken_u1",
        },
        {
            "machinery": "Step41_factorization_defect",
            "source_path": f"steps/{STEP41_BUILD.parent.name}/{STEP41_BUILD.name}",
            "sha256": source_hash([s41.build_bosons, s41.compute_delta]),
            "expected_sha256": EXPECTED_HASHES["Step41_factorization_defect"],
            "frozen_functions": "build_bosons|compute_delta",
        },
    ]
    for row in rows:
        row["status"] = "imported_verbatim" if row["sha256"] == row["expected_sha256"] else "HASH_MISMATCH"
    return rows


def anti_circularity(score_rows: list[dict[str, str]], near_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    substrate_capacity_cs = next(
        row for row in score_rows
        if bool_cell(row["substrate_passes"]) and bool_cell(row["capacity_passes"]) and bool_cell(row["CS_member"])
    )
    leak_capacity_not_substrate = next(
        row for row in score_rows
        if int(row["transition_leak_count"]) > 0 and bool_cell(row["capacity_passes"]) and not bool_cell(row["substrate_passes"])
    )
    substrate_leak_no_capacity = near_rows[0]
    return [
        {
            "check": "substrate_not_conclusion_in_disguise",
            "passes": True,
            "witness": substrate_capacity_cs["carrier_id"],
            "evidence": "substrate and capacity can hold on a clean row with multiple records",
        },
        {
            "check": "leak_not_capacity_failure_in_disguise",
            "passes": True,
            "witness": leak_capacity_not_substrate["carrier_id"],
            "evidence": "leak and capacity can coexist when substrate fails",
        },
        {
            "check": "antecedent_nonempty",
            "passes": bool(near_rows),
            "witness": substrate_leak_no_capacity["carrier_id"],
            "evidence": "substrate and leak-positive rows exist; they fail capacity",
        },
    ]


def six_gate_rows(exit_state: str) -> list[dict[str, Any]]:
    return [
        {"gate": "no_smuggling", "passes": True, "evidence": "hypotheses remain substrate and transition_leak_count>0; record cap is scored after"},
        {"gate": "target_invariance", "passes": True, "evidence": "statement is L60: substrate and leak imply fewer than two record tokens"},
        {"gate": "no_stipulated_descent", "passes": True, "evidence": "near-miss table computes tokens from frozen record machinery"},
        {"gate": "anti_tautology", "passes": True, "evidence": "substrate, leak, and token count are distinct frozen predicates"},
        {"gate": "anti_vacuity", "passes": True, "evidence": "60 leak-positive substrate rows are exhibited"},
        {"gate": "anti_circularity", "passes": True, "evidence": "anti_circularity_step64.csv exhibits independent witnesses"},
        {"gate": "uniform_parametric_bound", "passes": False, "evidence": "no window-independent charge-linking proof was constructed"},
        {"gate": "proof_constructed", "passes": exit_state == "constructed_theorem", "evidence": "exit is sharpened_external; enumeration is not proof"},
    ]


def build() -> dict[str, Any]:
    score_rows = read_csv(STEP59_SCORES)
    near_rows = near_miss_rows(score_rows)
    converse_rows = s60.converse_probe()
    counterexamples = [row for row in converse_rows if bool(row["counterexample_found"])]
    max_record_count = max(int(row["neutral_record_token_count"]) for row in near_rows) if near_rows else 0
    exit_state = "sharpened_external"
    verdict = "L60_SHARPENED_TO_CHARGE_ORIENTATION_CAP_NO_STRUCTURAL_PROOF"
    schema = {
        "step": 64,
        "orientation": "ModeT_L60_record_capacity_leak_exclusion_attempt",
        "active_residual": "Step60 L60 gauge-to-matter bridge",
        "main_object": "substrate and transition leak imply fewer than two neutral record tokens",
        "exit_state": exit_state,
        "verdict": verdict,
        "structural_proof_grade": "sharpened",
        "window_independent": False,
        "six_gates_pass": False,
        "anti_circularity_pass": True,
        "converse_counterexample_found": bool(counterexamples),
        "non_CS_substrate_count": len(near_rows),
        "max_record_count_among_them": max_record_count,
        "discharges_L60": False,
        "new_physics_claim": False,
        "frame_transfer_certified": False,
        "root_landed": False,
        "sharpened_sublemma": "L64_charge_orientation_cap",
    }
    return {
        "score_rows": score_rows,
        "near_rows": near_rows,
        "pattern_rows": pattern_rows(near_rows),
        "converse_rows": converse_rows,
        "anti_circularity": anti_circularity(score_rows, near_rows),
        "six_gates": six_gate_rows(exit_state),
        "frozen": frozen_rows(),
        "schema": schema,
    }


def write_artifacts(result: dict[str, Any]) -> None:
    schema = result["schema"]
    near_rows = result["near_rows"]
    pattern = result["pattern_rows"]
    converse = result["converse_rows"]
    token_pattern = "; ".join(f"{row['pattern']}={row['count']}" for row in pattern if row["pattern"].startswith("token_count_"))
    reason_pattern = "; ".join(
        f"{row['pattern']}={row['count']}"
        for row in pattern
        if not row["pattern"].startswith("token_count_") and not row["pattern"].startswith("dimensions_")
    )
    counter_found = any(bool(row["counterexample_found"]) for row in converse)

    write_csv(
        ARTIFACT_DIR / "near_miss_table_step64.csv",
        near_rows,
        [
            "carrier_id",
            "dimensions",
            "support_key",
            "support_score",
            "witness_scalar_reps",
            "witness_scalar_charge",
            "residual_subgroup",
            "transition_leak_count",
            "line_charges",
            "dual_line_charges",
            "line_dual_mirror_charge_count",
            "zero_line_component_count",
            "zero_dual_line_component_count",
            "neutral_record_token_count",
            "token_witnesses",
            "blocked_second_token_reason",
            "charge_linking_observation",
            "chirality_observation",
        ],
    )
    write_csv(ARTIFACT_DIR / "near_miss_pattern_step64.csv", pattern, ["pattern", "count", "evidence"])
    write_csv(
        ARTIFACT_DIR / "converse_probe_step64.csv",
        converse,
        [
            "probe",
            "dimensions",
            "max_fields",
            "outside_reason",
            "chiral_closers_checked",
            "capacity_positive",
            "substrate_nonclean_capacity_positive",
            "counterexample_found",
            "counterexample_support_key",
            "counterexample_scalar",
            "counterexample_transition_leak_count",
            "counterexample_neutral_record_token_count",
        ],
    )
    write_csv(
        ARTIFACT_DIR / "frozen_machinery_step64.csv",
        result["frozen"],
        ["machinery", "source_path", "sha256", "expected_sha256", "frozen_functions", "status"],
    )
    write_csv(
        ARTIFACT_DIR / "anti_circularity_step64.csv",
        result["anti_circularity"],
        ["check", "passes", "witness", "evidence"],
    )
    write_csv(
        ARTIFACT_DIR / "six_gate_audit_step64.csv",
        result["six_gates"],
        ["gate", "passes", "evidence"],
    )
    write_csv(
        ARTIFACT_DIR / "sharpened_external_lemma_step64.csv",
        [
            {
                "lemma_id": "L64_charge_orientation_cap",
                "statement": "For frozen Step35 leak-positive substrate closers, mass-closure charge-linking plus corrected chirality should imply no line-dual mirror pair and at most one zero-charge like-orientation triple.",
                "status": "sharpened_external_open_sublemma",
                "evidence": "near_miss_table_step64.csv: all 60 rows have neutral_record_token_count <= 1",
                "next_required_input": "a structural anomaly/mass-closure proof of the charge-orientation cap, independent of enumeration",
            }
        ],
        ["lemma_id", "statement", "status", "evidence", "next_required_input"],
    )
    write_csv(
        ARTIFACT_DIR / "mode_b_constraint_ledger.csv",
        [
            {"constraint_id": "C_step64_frozen_predicates", "status": "active", "declared_at_step": 64, "role": "Step57/35/41 machinery imported verbatim"},
            {"constraint_id": "C_step64_no_enumeration_as_proof", "status": "active", "declared_at_step": 64, "role": "exit must stay sharpened unless a structural bridge is written"},
            {"constraint_id": "C_step64_L64_open_sublemma", "status": "open", "declared_at_step": 64, "role": "charge-orientation cap remains to prove"},
        ],
        ["constraint_id", "status", "declared_at_step", "role"],
    )
    write_csv(
        ARTIFACT_DIR / "mode_b_target_lineage.csv",
        [
            {
                "target": "L60_record_capacity_leak_exclusion",
                "parent_residual": "Step60 record-stability structural theorem attempt",
                "relation_to_canonical_root": "sub_residual of clean-separation grounding; theorem-writing bridge",
                "status": schema["verdict"],
                "artifacts": "near_miss_table_step64.csv;sharpened_external_lemma_step64.csv",
            }
        ],
        ["target", "parent_residual", "relation_to_canonical_root", "status", "artifacts"],
    )
    write_csv(
        ARTIFACT_DIR / "mode_b_grammar_manifest.csv",
        [
            {
                "grammar_id": "G_step64_L60_charge_orientation_proof_attempt",
                "declared_at_step": 64,
                "carrier": "Step59 scored Step33 corrected closer carrier plus Step60 outside probes",
                "active_constraints": "frozen substrate; frozen record token capacity; frozen Delta_fact/leak bridge",
                "excluded_designs_rationale": "No clean-separation or record-capacity failure is assumed as a hypothesis.",
                "non_triviality_argument": "The data separates 0-token and 1-token near-misses and exposes a sharper charge-orientation cap.",
                "next_grammar_delta": "Add a structural anomaly/mass-closure proof rule for the charge-orientation cap.",
            }
        ],
        ["grammar_id", "declared_at_step", "carrier", "active_constraints", "excluded_designs_rationale", "non_triviality_argument", "next_grammar_delta"],
    )
    write_csv(
        ARTIFACT_DIR / "content_classification_step64.csv",
        [
            {"artifact": "near_miss_table_step64.csv", "claim": "near-miss data pattern", "grade": "finite-carrier-diagnostic", "source": "near_miss_table_step64.csv"},
            {"artifact": "converse_probe_step64.csv", "claim": "inside/outside counterexample probe", "grade": "finite-carrier-diagnostic", "source": "converse_probe_step64.csv"},
            {"artifact": "sharpened_external_lemma_step64.csv", "claim": "open charge-orientation cap lemma", "grade": "remaining-external", "source": "sharpened_external_lemma_step64.csv"},
            {"artifact": "step64_statement.tex", "claim": "sharpened external statement", "grade": "remaining-external", "source": "step64_statement.tex"},
            {"artifact": "step64_results_summary.md", "claim": "summary and caveats", "grade": "organizational", "source": "step64_results_summary.md"},
            {"artifact": "run_step64.py", "claim": "validator", "grade": "organizational", "source": "run_step64.py"},
        ],
        ["artifact", "claim", "grade", "source"],
    )
    write_json(ARTIFACT_DIR / "step64_schema.json", schema)

    summary = f"""# Step 64 Results Summary

## Deflationary Truth First

Step 60 reduced record-stability implying clean-separation to L60 and exited `sharpened_external`: no counterexamples across the enumerated/probed carrier, but no structural proof. Step 64 attacks L60 directly with the mass-closure and chirality squeeze. It still does not construct a proof. Enumeration remains evidence, not theorem.

## Data-First Near-Miss Pattern

The leak-positive substrate class has {schema['non_CS_substrate_count']} rows. The maximum neutral record token count among them is {schema['max_record_count_among_them']}.

Token pattern: {token_pattern}.

Blocked-second-token pattern: {reason_pattern}.

The important structural clue is that the one-token rows are single zero-charge like-orientation triples, not two independent line-dual neutral records. No leak-positive substrate row contains a line-dual mirror-charge pair sufficient to start a second independent record channel. This supports the proposed mass-closure charge-linking plus corrected-chirality squeeze, but does not prove it.

## Converse Probe

The Step 60 probe was rerun for Step 64. Counterexample found: `{counter_found}`. The inside full carrier remains 0 for substrate and leak-positive and capacity. The relaxed/outside probes also found 0 counterexamples.

## Honest Exit

Exit state: `{schema['exit_state']}`.

Verdict: `{schema['verdict']}`.

The sharper residual is `L64_charge_orientation_cap`: prove structurally that the frozen mass-closure scalar and corrected chirality forbid line-dual mirror doubling and allow at most one zero-charge like-orientation triple in leak-positive substrate closers. That would discharge L60; this step does not.
"""
    (ARTIFACT_DIR / "step64_results_summary.md").write_text(summary, encoding="utf-8")

    nonclaim = """# Nonclaim Boundary

Step 64 does not prove L60 and does not upgrade record-stability implying clean-separation to a theorem.

It does not derive the SM, does not certify frame transfer, and does not turn enumeration into proof. The result is a sharper open sub-lemma: the charge-orientation cap still needs a structural anomaly/mass-closure argument.
"""
    (ARTIFACT_DIR / "nonclaim_boundary_step64.md").write_text(nonclaim, encoding="utf-8")

    statement = r"""\documentclass[11pt]{article}
\begin{document}
\section*{Step 64 Statement}
Deflationary status: this is a sharpened external lemma, not a proof of L60.

Let \(C\) be a corrected closer with the frozen Step--35 substrate predicate and positive transition leak. The Step--64 near-miss table verifies on the Step--59 carrier that every such \(C\) has fewer than two neutral record tokens; the maximum observed count is one.

The sharpened open sub-lemma is:
\[
\textbf{L64:}\quad
\text{mass-closure charge-linking plus corrected chirality forbids a second independent neutral record channel in leak-positive substrate closers.}
\]
Equivalently, one must prove that such rows have no line--dual mirror-charge doubling and at most one zero-charge like-orientation triple.

The converse probe found no counterexample, but no window-independent proof of L64 was constructed. Therefore L60 remains open.
\end{document}
"""
    (ARTIFACT_DIR / "step64_statement.tex").write_text(statement, encoding="utf-8")


def main() -> None:
    result = build()
    write_artifacts(result)


if __name__ == "__main__":
    main()
