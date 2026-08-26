#!/usr/bin/env python3
"""Build the S5 F24 architecture constructions and F47 measure ablation."""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import itertools
import json
import math
import sys
import time
from collections import Counter, defaultdict, deque
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterable


ARTIFACT_DIR = Path(__file__).resolve().parent
REPO_ROOT = ARTIFACT_DIR.parents[2]
STEPS_DIR = REPO_ROOT / "physics_atlas" / "thread_cluster_a" / "steps"

SOURCE_SCRIPTS = {
    "step8": STEPS_DIR / "step8_structural_token_blind_selection_artifacts" / "structural_token_blind_selection_step8.py",
    "step9": STEPS_DIR / "step9_facet_factorization_test_artifacts" / "facet_factorization_test_step9.py",
    "step17": STEPS_DIR / "step17_two_layer_test_artifacts" / "two_layer_test_step17.py",
    "step18": STEPS_DIR / "step18_two_layer_stress_test_artifacts" / "two_layer_stress_test_step18.py",
    "step19": STEPS_DIR / "step19_layer_multiplicity_F24_artifacts" / "layer_multiplicity_f24_step19.py",
}

PINNED_SHA256 = {
    "step8": "ff1605aa8f12c8793916923a0d54ed4835cb93fec7195487b5947e65ad6ce0a7",
    "step9": "bb60decaf6d2961bd9ec7a094daa7097c6880d036c193878ef3b1ffacfe72de0",
    "step17": "b797626946e731a4df47bcb31351484ea8e838c190eae62964955cb3ae9671e0",
    "step18": "a61e37694aed689b67fb2336c8c84d437ad2c567b272e6bac4cb2f0b3fa6cdfa",
    "step19": "bc230981dd3cdcc7ba39fdd309c451e2559a2e6070c7d0a24be2b066a5a78afc",
}

OUTPUT_FILES = (
    "source_pins_s5.csv",
    "f24_family_objects_s5.csv",
    "f24_mutation_flips_s5.csv",
    "f47_surface_s5.csv",
    "f47_sensitivity_s5.csv",
    "f47_key_cells_s5.csv",
    "f47_headline_s5.csv",
    "controls_s5.csv",
    "schema_s5.json",
    "results_s5.md",
)

DENOMINATORS = (
    "full_product_unweighted",
    "admissible_unweighted",
    "admissible_step8_measure_weighted",
)
THRESHOLDS = tuple(value / 100 for value in range(200, 351, 5))
TARGET_RATIOS = (1e-4, 1e-2, 1.0)
SMALL_THETAS = (0.01, 0.025, 0.05, 0.10, 0.15)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def validate_source_pins() -> list[dict[str, Any]]:
    rows = []
    for source_id, path in SOURCE_SCRIPTS.items():
        actual = sha256_file(path)
        expected = PINNED_SHA256[source_id]
        if actual != expected:
            raise AssertionError(f"source pin mismatch for {path}: expected {expected}, got {actual}")
        rows.append(
            {
                "source_id": source_id,
                "repo_relative_path": str(path.relative_to(REPO_ROOT)),
                "sha256": actual,
                "passes": True,
            }
        )
    return rows


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


validate_source_pins()
s8 = load_module("s5_frozen_step8", SOURCE_SCRIPTS["step8"])
s9 = load_module("s5_frozen_step9", SOURCE_SCRIPTS["step9"])
s17 = load_module("s5_frozen_step17", SOURCE_SCRIPTS["step17"])
s18 = load_module("s5_frozen_step18", SOURCE_SCRIPTS["step18"])
s19 = load_module("s5_frozen_step19", SOURCE_SCRIPTS["step19"])
STEP17_SCALE_CARRIER = tuple(s17.scale_rows())
SCALE_ID_BY_RATIO = {float(row["scale_ratio"]): str(row["scale_id"]) for row in STEP17_SCALE_CARRIER}


def bool_value(value: Any) -> bool:
    return value is True or str(value).lower() == "true"


def candidate_rows() -> list[dict[str, Any]]:
    rows = s8.build_candidate_space()
    if len(rows) != 8640:
        raise AssertionError(f"Step-8 product moved: {len(rows)}")
    return rows


def admissible_rows(rows: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    return [row for row in rows if bool_value(row["structurally_admissible"])]


def string_rows(rows: Iterable[dict[str, Any]]) -> list[dict[str, str]]:
    return [{key: str(value) for key, value in row.items()} for row in rows]


def content_node(row: dict[str, Any]) -> str:
    return "C:" + s19.q_key(row)


def scale_node(row: dict[str, Any]) -> str:
    score = s18.radiative_score(row)
    ratio = float(s19.BASE_SCALE_RATIO[row["ew_code"]])
    return f"S:{SCALE_ID_BY_RATIO[ratio]}:{s18.channel_bin(score, s18.ACTIVE_CHANNEL_STRENGTH)}"


def budget_node(row: dict[str, Any]) -> str:
    return f"B:{row['naturalness_cost']}:{s19.s_readout(row)}"


def graph_from_rows(
    rows: Iterable[dict[str, Any]], right_node: Callable[[dict[str, Any]], str]
) -> tuple[set[str], set[str], dict[str, set[str]], int]:
    left_nodes: set[str] = set()
    right_nodes: set[str] = set()
    adjacency: dict[str, set[str]] = defaultdict(set)
    edge_count = 0
    for row in rows:
        left = content_node(row)
        right = right_node(row)
        left_nodes.add(left)
        right_nodes.add(right)
        if right not in adjacency[left]:
            adjacency[left].add(right)
            adjacency[right].add(left)
            edge_count += 1
    return left_nodes, right_nodes, adjacency, edge_count


def closure_fixed_point(adjacency: dict[str, set[str]], seeds: Iterable[str]) -> dict[str, Any]:
    reached = set(seeds)
    queue = deque(sorted(reached))
    expansion_steps = 0
    while queue:
        node = queue.popleft()
        for neighbor in sorted(adjacency.get(node, ())):
            if neighbor in reached:
                continue
            reached.add(neighbor)
            queue.append(neighbor)
            expansion_steps += 1
    second = set(reached)
    for node in tuple(reached):
        second.update(adjacency.get(node, ()))
    return {
        "reached": reached,
        "expansion_steps": expansion_steps,
        "fixed_point": second == reached,
        "consistent": all(neighbor in reached for node in reached for neighbor in adjacency.get(node, ())),
    }


def partitions(values: tuple[str, ...]) -> list[tuple[tuple[str, ...], ...]]:
    """All set partitions in canonical block order; the readout alphabet is tiny."""
    result: set[tuple[tuple[str, ...], ...]] = set()

    def visit(index: int, blocks: list[list[str]]) -> None:
        if index == len(values):
            normalized = tuple(sorted(tuple(sorted(block)) for block in blocks))
            result.add(normalized)
            return
        value = values[index]
        for block_index in range(len(blocks)):
            blocks[block_index].append(value)
            visit(index + 1, blocks)
            blocks[block_index].pop()
        blocks.append([value])
        visit(index + 1, blocks)
        blocks.pop()

    visit(0, [])
    return sorted(result)


def nontrivial_descending_coarsenings(rows: list[dict[str, Any]]) -> list[str]:
    readouts = tuple(sorted({s19.s_readout(row) for row in rows}))
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[s19.q_key(row)].append(row)
    valid = []
    for partition in partitions(readouts):
        if len(partition) <= 1 or len(partition) >= len(readouts):
            continue
        block_for = {value: index for index, block in enumerate(partition) for value in block}
        if all(len({block_for[s19.s_readout(row)] for row in members}) == 1 for members in groups.values()):
            valid.append("/".join("+".join(block) for block in partition))
    return valid


@dataclass(frozen=True)
class ArchitectureConfig:
    name: str
    active_rows: tuple[dict[str, Any], ...]
    universe_rows: tuple[dict[str, Any], ...]
    budget_enabled: bool
    declared_scope: str | None = None


def family_row(
    family: str,
    construction: str,
    forms: bool,
    admissible: bool,
    closes: bool,
    fires: bool,
    evidence: str,
    config: ArchitectureConfig,
) -> dict[str, Any]:
    return {
        "configuration": config.name,
        "family": family,
        "construction": construction,
        "forms": forms,
        "admissible": admissible,
        "closes": closes,
        "status": "FIRES" if fires else "DOES_NOT_FIRE",
        "fire_rule": "forms AND admissible AND closes" if family != "BlockedNonClosure" else "forms AND admissible AND NOT closes",
        "computed_evidence": evidence,
    }


def construct_families(config: ArchitectureConfig) -> list[dict[str, Any]]:
    rows = list(config.active_rows)
    universe = list(config.universe_rows)
    if not rows:
        raise AssertionError(f"empty architecture carrier for {config.name}")
    row_strings = string_rows(rows)
    all_admissible = all(bool_value(row["structurally_admissible"]) for row in rows)
    role_obstruction, _fibers, _witnesses = s19.obstruction_summary(row_strings, s19.s_readout)
    role_split = role_obstruction > 0
    realized = next((row for row in rows if bool_value(row["is_realized_point"])), rows[0])

    content_nodes, scale_nodes, scale_graph, scale_edges = graph_from_rows(rows, scale_node)
    scale_seed = {content_node(realized), scale_node(realized)}
    memory_closure = closure_fixed_point(scale_graph, scale_seed)
    active_channel = s18.with_channel(row_strings, s18.ACTIVE_CHANNEL_STRENGTH)
    coupling = s18.mutual_information_bits(active_channel, s18.CONTENT_COLUMNS, ["scale_channel_bin"])
    distinct_scale_values = len({row["ew_code"] for row in rows})
    memory_forms = bool(
        len(STEP17_SCALE_CARRIER) == len(s17.SCALE_RATIOS)
        and content_nodes
        and scale_nodes
        and scale_edges
        and distinct_scale_values >= 2
        and coupling > 0
    )
    memory_admissible = all_admissible and all(node.startswith("S:") for node in scale_nodes)
    memory_closes = bool(memory_closure["fixed_point"] and memory_closure["consistent"])

    budget_left, budget_nodes, budget_graph, budget_edges = graph_from_rows(rows, budget_node)
    budget_closure = closure_fixed_point(budget_graph, {content_node(realized), budget_node(realized)})
    budget_forms = bool(config.budget_enabled and role_split and budget_nodes and budget_edges)
    budget_admissible = all_admissible and all(math.isfinite(float(row["naturalness_cost"])) for row in rows)
    budget_closes = bool(budget_closure["fixed_point"] and budget_closure["consistent"])

    # Hidden-upstream candidate: UV/vacuum states are constructed, then rejected as
    # hidden because both coordinates are already explicit components of q.
    hidden_states = {(str(row["uv_code"]), str(row["vacuum_code"])) for row in rows}
    hidden_candidate_constructed = len(hidden_states) > 1
    hidden_independent = not {"uv_code", "vacuum_code"}.issubset(set(s19.CONTENT_Q_COLUMNS))
    hidden_forms = hidden_candidate_constructed and hidden_independent
    hidden_admissible = all_admissible

    # Bridge candidate: the actual radiative driver is constructed, but it is a
    # projection of q and hence not a strict third mediator/common parent.
    driver_columns = ("gauge_code", "rep_code", "n_gen", "texture_code")
    bridge_states = {tuple(str(row[column]) for column in driver_columns) for row in rows}
    bridge_candidate_constructed = len(bridge_states) > 1
    strict_bridge = not set(driver_columns).issubset(set(s19.CONTENT_Q_COLUMNS))
    bridge_forms = bridge_candidate_constructed and strict_bridge
    bridge_admissible = all_admissible

    # Scoped candidate: e0 is a declared proper target-ratio scope. It fires only
    # if the full coupled closure does not escape that scope.
    scope_name = config.declared_scope or "e0"
    scope_rows = [row for row in rows if row["ew_code"] == scope_name]
    universe_scope_count = sum(row["ew_code"] == scope_name for row in universe)
    scope_proper = 0 < universe_scope_count < len(universe)
    scope_nodes = {content_node(row) for row in scope_rows} | {scale_node(row) for row in scope_rows}
    scope_closure = closure_fixed_point(scale_graph, scope_nodes)
    scope_reached = scope_closure["reached"]
    scope_closes = bool(scope_closure["fixed_point"] and scope_closure["consistent"] and scope_reached <= scope_nodes)
    scope_forms = bool(scope_rows and scope_proper)
    scope_admissible = all(bool_value(row["structurally_admissible"]) for row in scope_rows)

    valid_coarsenings = nontrivial_descending_coarsenings(rows)
    coarsened_forms = bool(role_split and valid_coarsenings)
    coarsened_admissible = all_admissible
    coarsened_closes = coarsened_forms

    role_explicit = "ew_code" in s9.FACETS and "naturalness_cost" in rows[0]
    outside_projection_constructed = True
    outside_forms = outside_projection_constructed and not role_explicit
    outside_admissible = all_admissible
    outside_closes = True

    blocked_forms = role_split
    blocked_admissible = all_admissible
    blocked_closes = memory_closes and budget_closes

    facet_edges, facet_components = s9.graph_components(row_strings)
    common = (
        f"rows={len(rows)}; q={len(content_nodes)}; role_obstruction={role_obstruction}; "
        f"facet_edges={len(facet_edges)}; facet_components={len(facet_components)}"
    )
    result = [
        family_row(
            "MemoryLayer",
            "distinct Step-17 scale carrier coupled to content by Step-18 radiative edges",
            memory_forms,
            memory_admissible,
            memory_closes,
            memory_forms and memory_admissible and memory_closes,
            f"{common}; step17_scale_carrier_nodes={len(STEP17_SCALE_CARRIER)}; active_scale_channel_nodes={len(scale_nodes)}; scale_edges={scale_edges}; ew_values={distinct_scale_values}; coupling_bits={coupling:.12f}; fixed_steps={memory_closure['expansion_steps']}",
            config,
        ),
        family_row(
            "HiddenUpstreamRole",
            "UV/vacuum upstream-state carrier joined to q",
            hidden_forms,
            hidden_admissible,
            True,
            hidden_forms and hidden_admissible,
            f"{common}; upstream_candidate_constructed={hidden_candidate_constructed}; upstream_states={len(hidden_states)}; coordinates_already_in_q={not hidden_independent}",
            config,
        ),
        family_row(
            "BridgeMediatedRole",
            "radiative-driver bridge carrier joined to content and scale",
            bridge_forms,
            bridge_admissible,
            True,
            bridge_forms and bridge_admissible,
            f"{common}; bridge_candidate_constructed={bridge_candidate_constructed}; bridge_states={len(bridge_states)}; bridge_is_projection_of_q={not strict_bridge}",
            config,
        ),
        family_row(
            "BudgetedRole",
            "finite naturalness/readout budget ledger attached to the content closure",
            budget_forms,
            budget_admissible,
            budget_closes,
            budget_forms and budget_admissible and budget_closes,
            f"{common}; budget_enabled={config.budget_enabled}; budget_nodes={len(budget_nodes)}; budget_edges={budget_edges}; fixed_steps={budget_closure['expansion_steps']}",
            config,
        ),
        family_row(
            "ScopedRole",
            "proper e0 target-ratio subcarrier with closure tested against the active coupling graph",
            scope_forms,
            scope_admissible,
            scope_closes,
            scope_forms and scope_admissible and scope_closes,
            f"{common}; scope={scope_name}; scope_rows={len(scope_rows)}; universe_scope_rows={universe_scope_count}; reached_nodes={len(scope_reached)}; scope_nodes={len(scope_nodes)}",
            config,
        ),
        family_row(
            "CoarsenedRole",
            "exhaustive nontrivial partitions of the s-readout alphabet tested for descent through q",
            coarsened_forms,
            coarsened_admissible,
            coarsened_closes,
            coarsened_forms and coarsened_admissible and coarsened_closes,
            f"{common}; readouts={len({s19.s_readout(row) for row in rows})}; valid_nontrivial_coarsenings={'|'.join(valid_coarsenings) or 'none'}",
            config,
        ),
        family_row(
            "OutsideRoleScope",
            "projection deleting the explicit scale/naturalness role from the tested carrier",
            outside_forms,
            outside_admissible,
            outside_closes,
            outside_forms and outside_admissible and outside_closes,
            f"{common}; exclusion_projection_constructed={outside_projection_constructed}; role_explicit_in_step8_step9_carrier={role_explicit}",
            config,
        ),
        family_row(
            "BlockedNonClosure",
            "coupled content-scale closure iterated to a fixed point",
            blocked_forms,
            blocked_admissible,
            blocked_closes,
            blocked_forms and blocked_admissible and not blocked_closes,
            f"{common}; memory_fixed={memory_closes}; budget_fixed={budget_closes}",
            config,
        ),
    ]
    if len(result) != 8 or len({row["family"] for row in result}) != 8:
        raise AssertionError("F24 family inventory is not exactly eight")
    return result


def architecture_configs(admissible: list[dict[str, Any]]) -> tuple[ArchitectureConfig, ...]:
    universe = tuple(admissible)
    e0 = tuple(row for row in admissible if row["ew_code"] == "e0")
    return (
        ArchitectureConfig("real_carrier", universe, universe, True),
        ArchitectureConfig("mutation_budget_decoupled", universe, universe, False),
        ArchitectureConfig("mutation_sealed_e0_scope", e0, universe, False, "e0"),
    )


def mutation_rows(all_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_config = {
        config: {row["family"]: row for row in all_rows if row["configuration"] == config}
        for config in {row["configuration"] for row in all_rows}
    }
    baseline = by_config["real_carrier"]
    rows = []
    for mutation in ("mutation_budget_decoupled", "mutation_sealed_e0_scope"):
        mutated = by_config[mutation]
        for family in sorted(baseline):
            before = baseline[family]["status"] == "FIRES"
            after = mutated[family]["status"] == "FIRES"
            if before == after:
                continue
            rows.append(
                {
                    "mutation": mutation,
                    "family": family,
                    "baseline_fires": before,
                    "mutated_fires": after,
                    "flip": f"{'FIRES' if before else 'OFF'} -> {'FIRES' if after else 'OFF'}",
                    "mutation_evidence": mutated[family]["computed_evidence"],
                }
            )
    return rows


def measure_weight(row: dict[str, Any]) -> int:
    weights = {str(vacuum["code"]): int(vacuum["measure_weight"]) for vacuum in s8.VACUA}
    return weights[str(row["vacuum_code"])]


def selected(row: dict[str, Any], threshold: float, target_ratio: float) -> bool:
    return bool(s19.BASE_SCALE_RATIO[row["ew_code"]] <= target_ratio and s19.radiative_score(row) > threshold)


def denominator_rows(
    all_rows: list[dict[str, Any]], admissible: list[dict[str, Any]], denominator: str
) -> tuple[list[dict[str, Any]], Callable[[dict[str, Any]], int]]:
    if denominator == "full_product_unweighted":
        return all_rows, lambda _row: 1
    if denominator == "admissible_unweighted":
        return admissible, lambda _row: 1
    if denominator == "admissible_step8_measure_weighted":
        return admissible, measure_weight
    raise KeyError(denominator)


def f47_cell(
    all_rows: list[dict[str, Any]],
    admissible: list[dict[str, Any]],
    denominator: str,
    threshold: float,
    target_ratio: float,
    theta: float,
) -> dict[str, Any]:
    rows, weight = denominator_rows(all_rows, admissible, denominator)
    denominator_mass = sum(weight(row) for row in rows)
    selected_mass = sum(weight(row) for row in rows if selected(row, threshold, target_ratio))
    fraction = selected_mass / denominator_mass
    realized = next(row for row in all_rows if bool_value(row["is_realized_point"]))
    realized_in = selected(realized, threshold, target_ratio)
    return {
        "denominator": denominator,
        "support_row_count": len(rows),
        "denominator_mass": denominator_mass,
        "radiative_threshold_strict_gt": f"{threshold:.2f}",
        "target_ratio_max_inclusive": f"{target_ratio:.12g}",
        "small_theta": f"{theta:.6f}",
        "selector_mass": selected_mass,
        "selector_fraction": f"{fraction:.12f}",
        "positive_measure": selected_mass > 0,
        "small": selected_mass > 0 and fraction <= theta,
        "realized_score": f"{s19.radiative_score(realized):.6f}",
        "realized_in_selector": realized_in,
        "realized_f47": bool(realized_in and selected_mass > 0 and fraction <= theta),
    }


def build_f47(all_rows: list[dict[str, Any]], admissible: list[dict[str, Any]]) -> dict[str, Any]:
    surface = [
        f47_cell(all_rows, admissible, denominator, threshold, s17.TARGET_RATIO, s19.SMALL_THETA)
        for denominator, threshold in itertools.product(DENOMINATORS, THRESHOLDS)
    ]
    sensitivity = [
        f47_cell(all_rows, admissible, denominator, threshold, target_ratio, theta)
        for denominator, threshold, target_ratio, theta in itertools.product(
            DENOMINATORS, THRESHOLDS, TARGET_RATIOS, SMALL_THETAS
        )
    ]
    headline = f47_cell(
        all_rows,
        admissible,
        "admissible_step8_measure_weighted",
        s18.CHANNEL_THRESHOLD,
        s17.TARGET_RATIO,
        s19.SMALL_THETA,
    )
    headline.update(
        {
            "headline": True,
            "headline_reason": "conditions on declared admissibility, honors Step-8 measure_weight, and uses the upstream Step-18 channel threshold rather than the downstream target-inclusive 2.70 threshold",
        }
    )
    key_cells = []
    for threshold_name, threshold in (("step19_legacy", s19.RADIATIVE_THRESHOLD), ("step18_upstream", s18.CHANNEL_THRESHOLD)):
        for denominator in DENOMINATORS:
            row = f47_cell(all_rows, admissible, denominator, threshold, s17.TARGET_RATIO, s19.SMALL_THETA)
            row["threshold_provenance"] = threshold_name
            key_cells.append(row)
    legacy = f47_cell(
        all_rows,
        admissible,
        "full_product_unweighted",
        s19.RADIATIVE_THRESHOLD,
        s19.TARGET_RATIO_MAX,
        s19.SMALL_THETA,
    )
    realized = next(row for row in all_rows if bool_value(row["is_realized_point"]))
    realized_score = s19.radiative_score(realized)
    if abs(realized_score - 2.75) > 1e-12:
        raise AssertionError(f"realized score moved from the 2.75 boundary: {realized_score}")
    primary_fractions = [float(row["selector_fraction"]) for row in surface]
    sensitivity_fractions = [float(row["selector_fraction"]) for row in sensitivity]
    return {
        "surface": surface,
        "sensitivity": sensitivity,
        "headline": [headline],
        "key_cells": key_cells,
        "legacy": legacy,
        "realized_score": realized_score,
        "primary_range": (min(primary_fractions), max(primary_fractions)),
        "sensitivity_range": (min(sensitivity_fractions), max(sensitivity_fractions)),
    }


def build_data() -> dict[str, Any]:
    pins = validate_source_pins()
    all_rows = candidate_rows()
    admissible = admissible_rows(all_rows)
    if len(admissible) != 468:
        raise AssertionError(f"admissible carrier moved: {len(admissible)}")
    if sum(measure_weight(row) for row in admissible) != 534:
        raise AssertionError("Step-8 weighted admissible mass moved")
    full_role_obstruction, _full_fibers, _full_witnesses = s19.obstruction_summary(
        string_rows(all_rows), s19.s_readout
    )
    admissible_role_obstruction, _admissible_fibers, _admissible_witnesses = s19.obstruction_summary(
        string_rows(admissible), s19.s_readout
    )

    family_rows = []
    for config in architecture_configs(admissible):
        family_rows.extend(construct_families(config))
    baseline = [row for row in family_rows if row["configuration"] == "real_carrier"]
    firing = [row["family"] for row in baseline if row["status"] == "FIRES"]
    mutations = mutation_rows(family_rows)
    f47 = build_f47(all_rows, admissible)

    mutation_firing = {
        config: sorted(row["family"] for row in family_rows if row["configuration"] == config and row["status"] == "FIRES")
        for config in ("mutation_budget_decoupled", "mutation_sealed_e0_scope")
    }
    controls = [
        {"control": "source_hash_pins", "passes": all(row["passes"] for row in pins), "evidence": "five frozen build scripts match literal SHA-256 pins"},
        {"control": "step8_carrier_reproduction", "passes": len(all_rows) == 8640 and len(admissible) == 468, "evidence": f"full={len(all_rows)}; admissible={len(admissible)}"},
        {"control": "step8_measure_used", "passes": sum(measure_weight(row) for row in admissible) == 534, "evidence": "468 admissible support rows have total declared measure mass 534"},
        {"control": "role_obstruction_reproduced", "passes": full_role_obstruction == 5760 and admissible_role_obstruction == 307, "evidence": f"full={full_role_obstruction}; admissible={admissible_role_obstruction}"},
        {"control": "all_eight_families_constructed", "passes": len(baseline) == 8 and len({row['family'] for row in baseline}) == 8, "evidence": "each row reports forms/admissible/closes/status from a materialized object"},
        {"control": "real_verdict_computed", "passes": firing == ["MemoryLayer", "BudgetedRole"], "evidence": f"firing={','.join(firing)}"},
        {"control": "budget_decoupling_flip", "passes": mutation_firing["mutation_budget_decoupled"] == ["MemoryLayer"], "evidence": f"firing={','.join(mutation_firing['mutation_budget_decoupled'])}"},
        {"control": "sealed_scope_flip", "passes": mutation_firing["mutation_sealed_e0_scope"] == ["ScopedRole"], "evidence": f"firing={','.join(mutation_firing['mutation_sealed_e0_scope'])}"},
        {"control": "legacy_3_96_reproduced", "passes": f47["legacy"]["selector_mass"] == 342 and f47["legacy"]["denominator_mass"] == 8640, "evidence": f"fraction={f47['legacy']['selector_fraction']}"},
        {"control": "realized_strict_boundary", "passes": not f47["headline"][0]["realized_in_selector"] and selected(next(row for row in all_rows if bool_value(row['is_realized_point'])), 2.70, 1e-4), "evidence": "score=2.750000; included at threshold 2.70, excluded at strict >2.75"},
        {"control": "ablation_surface_complete", "passes": len(f47["surface"]) == 3 * 31 and len(f47["sensitivity"]) == 3 * 31 * 3 * 5, "evidence": f"primary={len(f47['surface'])}; sensitivity={len(f47['sensitivity'])}"},
        {"control": "headline_cell_exact", "passes": f47["headline"][0]["selector_mass"] == 12 and f47["headline"][0]["denominator_mass"] == 534 and not f47["headline"][0]["realized_f47"], "evidence": f"fraction={f47['headline'][0]['selector_fraction']}; realized_f47={f47['headline'][0]['realized_f47']}"},
    ]
    if not all(row["passes"] for row in controls):
        raise AssertionError(f"S5 controls failed: {[row for row in controls if not row['passes']]}")

    schema = {
        "packet": "S5-REPAIR-1",
        "grade": "FINITE_TOY_ARCHITECTURE_AND_MEASURE_ABLATION",
        "source_pins": PINNED_SHA256,
        "carrier": {"full_product": 8640, "admissible_support_rows": 468, "admissible_step8_measure_mass": 534},
        "role_obstruction_pairs": {"full_product": full_role_obstruction, "admissible_carrier": admissible_role_obstruction},
        "f24_real_firing_families": firing,
        "f24_verdict": "ARCHITECTURE_UNDERDETERMINED_MEMORY_LAYER_AND_BUDGETED_ROLE_BOTH_CLOSE",
        "memory_layer_closure_gate": {
            "status": "EXPERIMENTAL_INSUFFICIENT",
            "ruling": "round-23 verification",
            "limitation": "finite alternating content/scale reachability reaches a graph fixed point, but does not establish a physically sufficient independent scale-layer closure",
            "effect_on_verdict": "MemoryLayer FIRES remains a computed finite-toy diagnostic and is not foundation-grade architecture evidence",
        },
        "mutation_firing_families": mutation_firing,
        "f47_legacy_fraction": f47["legacy"]["selector_fraction"],
        "f47_headline": f47["headline"][0],
        "f47_primary_fraction_range": [f"{value:.12f}" for value in f47["primary_range"]],
        "f47_full_sensitivity_fraction_range": [f"{value:.12f}" for value in f47["sensitivity_range"]],
        "realized_inclusion_rule": "strict radiative_score > threshold; realized score is exactly 2.75, hence included iff threshold < 2.75",
        "naturalness_verdict": "MEASURE_AND_THRESHOLD_SENSITIVE_FINITE_TOY_REFRAME_NOT_A_STABLE_3_96_PERCENT_NUMBER",
        "output_files": list(OUTPUT_FILES),
    }
    return {
        "pins": pins,
        "family_rows": family_rows,
        "baseline": baseline,
        "mutations": mutations,
        "f47": f47,
        "controls": controls,
        "schema": schema,
    }


def write_csv(path: Path, rows: Iterable[dict[str, Any]], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def results_note(data: dict[str, Any]) -> str:
    schema = data["schema"]
    headline = data["f47"]["headline"][0]
    legacy = data["f47"]["legacy"]
    baseline = data["baseline"]
    table = "\n".join(
        f"| {row['family']} | {row['forms']} | {row['admissible']} | {row['closes']} | {row['status']} |"
        for row in baseline
    )
    mutation_lines = "\n".join(
        f"- `{name}` fires: `{', '.join(families)}`."
        for name, families in schema["mutation_firing_families"].items()
    )
    key_table = "\n".join(
        f"| {row['threshold_provenance']} | {row['radiative_threshold_strict_gt']} | {row['denominator']} | {row['selector_mass']}/{row['denominator_mass']} | {row['selector_fraction']} | {row['small']} | {row['realized_in_selector']} |"
        for row in data["f47"]["key_cells"]
    )
    return f"""# S5 F24 architecture verdict and F47 measure ablation

## F24 computed architecture

| Family | Forms | Admissible | Closes | Status |
|---|---:|---:|---:|---|
{table}

Both `MemoryLayer` and `BudgetedRole` fire on the real 468-row admissible carrier. The MemoryLayer is not a boolean placeholder: it is the distinct Step-17 scale carrier, coupled to content by the Step-18 radiative channel, with alternating content/scale reachability iterated to a graph fixed point. **Round-23 ruling: this MemoryLayer closure gate is EXPERIMENTAL/INSUFFICIENT.** Fixed-point reachability on the finite carrier does not establish a physically sufficient independent scale-layer closure, so `MemoryLayer: FIRES` is retained as a computed finite-toy diagnostic, not foundation-grade architecture evidence. The BudgetedRole is a separate finite naturalness/readout ledger attached to the content closure and also reaches a fixed point. At this diagnostic grade the verdict remains `ARCHITECTURE_UNDERDETERMINED_MEMORY_LAYER_AND_BUDGETED_ROLE_BOTH_CLOSE`; the published unique BudgetedRole conclusion does not survive the explicit competitor construction, but the MemoryLayer leg cannot carry a stronger claim without a repaired closure gate.

## Mutation flips

{mutation_lines}

The first mutation removes the budget ledger without altering the coupled scale carrier, leaving a genuine MemoryLayer-only resolution. The second evaluates a sealed proper `e0` subcarrier with the budget disabled: the coupled closure cannot escape the declared scope, so ScopedRole fires while the multi-scale MemoryLayer no longer forms. The validator asserts both firing-set changes.

## F47 surface

| Threshold source | Threshold | Denominator | Selector mass | Fraction | Small at 0.05 | Realized in region |
|---|---:|---|---:|---:|---:|---:|
{key_table}

The legacy Step-19 cell is reproduced exactly: `{legacy['selector_mass']}/{legacy['denominator_mass']} = {legacy['selector_fraction']}` at threshold `2.70`, full-product counting, target ratio `1e-4`, and `theta=0.05`.

The defensible headline conditions on the declared 468 admissible rows, weights them by Step-8 `measure_weight` (total measure mass {headline['denominator_mass']}), and uses the upstream Step-18 channel threshold `2.75` rather than Step 19's later `2.70`. Its selector mass is `{headline['selector_mass']}/{headline['denominator_mass']} = {headline['selector_fraction']}`. It is positive and small at `theta=0.05`, but the realized point is **not** in the region: its score is exactly `2.75`, while the predicate is strict `score > threshold`.

Across denominators and the declared threshold sweep at target ratio `1e-4`, the selector fraction ranges from `{schema['f47_primary_fraction_range'][0]}` to `{schema['f47_primary_fraction_range'][1]}`. Including target-ratio sensitivity (`1e-4`, `1e-2`, `1`) expands the range to `{schema['f47_full_sensitivity_fraction_range'][0]}` through `{schema['f47_full_sensitivity_fraction_range'][1]}`. `SMALL_THETA` changes only the `small` classification, and the full sensitivity CSV reports `theta=0.01,0.025,0.05,0.10,0.15` separately.

## Honest conclusion

F47 remains a finite-toy naturalness reframe, but `3.96%` is not a stable selector number. It moves to `2.247191011236%` in the defensible weighted-admissible/upstream-threshold cell, changes discontinuously across score support points, reaches zero above the largest score, and is sensitive to both the target-ratio convention and `theta`. The realized-point statement is likewise threshold-sensitive: it holds for thresholds below `2.75` and fails at `2.75` under the published strict comparison.
"""


def write_outputs(data: dict[str, Any], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    write_csv(output_dir / "source_pins_s5.csv", data["pins"], ["source_id", "repo_relative_path", "sha256", "passes"])
    write_csv(
        output_dir / "f24_family_objects_s5.csv",
        data["family_rows"],
        ["configuration", "family", "construction", "forms", "admissible", "closes", "status", "fire_rule", "computed_evidence"],
    )
    write_csv(
        output_dir / "f24_mutation_flips_s5.csv",
        data["mutations"],
        ["mutation", "family", "baseline_fires", "mutated_fires", "flip", "mutation_evidence"],
    )
    f47_fields = [
        "denominator", "support_row_count", "denominator_mass", "radiative_threshold_strict_gt",
        "target_ratio_max_inclusive", "small_theta", "selector_mass", "selector_fraction", "positive_measure",
        "small", "realized_score", "realized_in_selector", "realized_f47",
    ]
    write_csv(output_dir / "f47_surface_s5.csv", data["f47"]["surface"], f47_fields)
    write_csv(output_dir / "f47_sensitivity_s5.csv", data["f47"]["sensitivity"], f47_fields)
    write_csv(output_dir / "f47_key_cells_s5.csv", data["f47"]["key_cells"], ["threshold_provenance"] + f47_fields)
    write_csv(output_dir / "f47_headline_s5.csv", data["f47"]["headline"], f47_fields + ["headline", "headline_reason"])
    write_csv(output_dir / "controls_s5.csv", data["controls"], ["control", "passes", "evidence"])
    (output_dir / "schema_s5.json").write_text(json.dumps(data["schema"], indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (output_dir / "results_s5.md").write_text(results_note(data), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=ARTIFACT_DIR)
    args = parser.parse_args()
    started = time.perf_counter()
    data = build_data()
    write_outputs(data, args.output_dir)
    elapsed = time.perf_counter() - started
    print(
        "build_s5_f24_f47.py: PASS: "
        f"firing={','.join(data['schema']['f24_real_firing_families'])} "
        f"headline={data['f47']['headline'][0]['selector_fraction']} elapsed={elapsed:.3f}s"
    )


if __name__ == "__main__":
    main()
