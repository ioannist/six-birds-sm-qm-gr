#!/usr/bin/env python3
"""Generate the Physics Layer Atlas Mermaid map from Phase 3 manifests.

The output intentionally uses one uniform arrow convention:
more-fundamental / richer layer -> shadow / coarser layer.
"""

from __future__ import annotations

import json
import re
from collections import defaultdict, deque
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ATLAS = ROOT / "physics_atlas"
THEORY_MANIFEST = ATLAS / "phase3" / "scored_run" / "theory_manifest.jsonl"
EDGE_MANIFEST = ATLAS / "phase3" / "scored_run" / "edge_manifest.jsonl"
PHASE3_TABLE = ATLAS / "phase3" / "PHASE3_ATLAS.md"
OUTPUT = ATLAS / "THEORY_MAP.md"


# Directed theory-to-theory backbone edges to render. The generator reads every
# source/target/name/tier/modality from the manifest; this list only declares
# which manifest edges are legible backbone edges rather than foregrounded E3
# foreclosures, non-theory phenomena, or bidirectional/common-refinement notes.
BACKBONE_IDS = [
    "E002",
    "E003",
    "E004",
    "E005",
    "E006",
    "E008",
    "E010",
    "E011",
    "E012",
    "E013",
    "E014",
    "E015",
    "E022",
    "E025",
    "E028a",
    "E033",
]


FORECLOSURE_ATTACHMENTS = {
    # edge id: (theory node to attach to, foreclosure label, constructed layer id or None, open?)
    "E009": ("rg_eft", "UV-completion fiber", "Lstar_sm", False),
    "E019": ("standard_model", "gauge-group origin", "Lstar_sm", False),
    "E020": ("standard_model", "fermion generations", "Lstar_sm", False),
    "E021": ("general_relativity", "cosmological constant", "GR_upper", False),
    "E032": ("quantum_mechanics", "measurement outcome", None, True),
    "E037": ("standard_model", "vacuum selection", "Lstar_sm", False),
    "E041": ("qcd", "confinement", None, True),
    "E042": ("general_relativity", "singularity boundary", "GR_upper", False),
    "E043": ("electroweak_theory", "electroweak hierarchy", "Lstar_sm", False),
}


DOMAIN_GROUPS = [
    (
        "Quantum / Particle",
        [
            "standard_model",
            "electroweak_theory",
            "qcd",
            "qed",
            "relativistic_qft",
            "rg_eft",
            "quantum_mechanics",
            "condensed_matter_spt",
        ],
    ),
    (
        "Gravity / Cosmology",
        [
            "general_relativity",
            "newtonian_gravity",
            "lambda_cdm",
            "black_hole_thermodynamics",
        ],
    ),
    (
        "Statistical / Continuum",
        [
            "statistical_mechanics",
            "thermodynamics",
            "kinetic_theory",
            "hydrodynamics",
            "brownian_langevin",
        ],
    ),
    (
        "Classical Limits",
        [
            "special_relativity",
            "classical_mechanics",
            "classical_electromagnetism",
            "geometrical_optics",
        ],
    ),
]


CONSTRUCTION_SOURCES = {
    "L_qm_gr": [
        "physics_atlas/thread_qm_gr/findings_qm_gr.md",
        "physics_atlas/thread_qm_gr/steps/step35_qgr_uniqueness_theorem_artifacts/T_QGR_Unique.tex",
    ],
    "Lstar_sm": [
        "physics_atlas/thread_cluster_a/findings_cluster_a.md",
        "physics_atlas/thread_cluster_a/steps/step7_consolidated_statement_artifacts/cluster_a_consolidated_statement.tex",
    ],
    "GR_upper": [
        "physics_atlas/thread_cluster_b/findings_cluster_b.md",
        "physics_atlas/thread_cluster_b/steps/step4_consolidated_statement_artifacts/cluster_b_consolidated_statement.tex",
    ],
}


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def normalize_direction(value: str) -> str:
    if value == "bidirectional":
        return "bidir"
    return value


def parse_phase3_table() -> dict[str, dict[str, str]]:
    pattern = re.compile(
        r"^\|\s*(E\d+[a-z]?)\s*\|\s*([^|]+?)\s*\|\s*(down|up|bidir)\s*"
        r"\|\s*\*\*(E\d)\*\*\s*\|\s*([^|]+)\|"
    )
    table: dict[str, dict[str, str]] = {}
    for line in PHASE3_TABLE.read_text().splitlines():
        match = pattern.match(line)
        if not match:
            continue
        edge_id, relation, direction, tier, modality = match.groups()
        table[edge_id] = {
            "relation": relation.strip(),
            "direction": direction.strip(),
            "tier": tier.strip(),
            "modality": modality.strip(),
        }
    return table


def orient_edge(edge: dict) -> tuple[str, str]:
    direction = normalize_direction(edge["arrow_direction"])
    source = edge["source_theory_id"]
    target = edge["target_theory_id"]
    if direction == "down":
        return source, target
    if direction == "up":
        return target, source
    raise ValueError(f"Cannot orient bidirectional edge {edge['id']} as a directed backbone edge")


def node_label(theory: dict) -> str:
    name = theory["name"].replace('"', "'")
    return f'{theory["id"]}["{name}<br/><small>{theory["id"]}</small>"]'


def edge_operator(tier: str) -> str:
    if tier in {"E0", "E1"}:
        return "-->"
    return "-.->"


def reachable(edges: list[tuple[str, str]], start: str, goal: str) -> bool:
    graph: dict[str, list[str]] = defaultdict(list)
    for src, dst in edges:
        graph[src].append(dst)
    seen = {start}
    queue = deque([start])
    while queue:
        node = queue.popleft()
        for nxt in graph[node]:
            if nxt == goal:
                return True
            if nxt not in seen:
                seen.add(nxt)
                queue.append(nxt)
    return False


def has_cycle(edges: list[tuple[str, str]]) -> bool:
    graph: dict[str, list[str]] = defaultdict(list)
    nodes = set()
    for src, dst in edges:
        graph[src].append(dst)
        nodes.add(src)
        nodes.add(dst)
    visiting: set[str] = set()
    visited: set[str] = set()

    def dfs(node: str) -> bool:
        if node in visiting:
            return True
        if node in visited:
            return False
        visiting.add(node)
        for nxt in graph[node]:
            if dfs(nxt):
                return True
        visiting.remove(node)
        visited.add(node)
        return False

    return any(dfs(node) for node in sorted(nodes))


def phase3_status(edge: dict, phase3: dict[str, dict[str, str]]) -> str:
    row = phase3.get(edge["id"])
    if not row:
        return "MISSING"
    checks = [
        row["direction"] == normalize_direction(edge["arrow_direction"]),
        row["tier"] == edge["scored_tier"],
        row["modality"] == edge["scored_modality"],
    ]
    return "ok" if all(checks) else "MISMATCH"


def omitted_reason(edge: dict, theory_ids: set[str], rendered_foreclosures: set[str]) -> str:
    edge_id = edge["id"]
    if edge_id in BACKBONE_IDS or edge_id == "E018" or edge_id in rendered_foreclosures:
        return ""
    source_kind = edge.get("source_kind")
    target_kind = edge.get("target_kind")
    direction = normalize_direction(edge["arrow_direction"])
    if edge["scored_tier"] == "E3":
        if source_kind == "theory_card" and target_kind == "theory_card":
            return "E3 theory-to-theory foreclosure/failed near-layer relation; not drawn as an established reduction backbone"
        return "E3 foreclosure not foregrounded in this map"
    if source_kind != "theory_card" or target_kind != "theory_card":
        return f"non-theory endpoint ({source_kind}->{target_kind}); omitted for legibility"
    if edge["source_theory_id"] not in theory_ids or edge["target_theory_id"] not in theory_ids:
        return "endpoint outside theory manifest; omitted from theory backbone"
    if direction == "bidir":
        return "bidirectional/common-refinement relation; omitted from directed acyclic backbone"
    if edge_id == "E028b":
        return "recognition/import leg paired with E028a; omitted to avoid a visual cycle"
    return "not selected for compact backbone"


def build_mermaid(
    theories: dict[str, dict],
    edges_by_id: dict[str, dict],
    backbone_ids: list[str],
) -> tuple[str, list[dict], list[tuple[str, str]], list[str]]:
    lines: list[str] = []
    link_styles: list[str] = []
    provenance: list[dict] = []
    directed_edges: list[tuple[str, str]] = []
    link_index = 0

    lines.append("flowchart TB")
    lines.append('  Title["Physics Layer Atlas<br/><small>Arrows point richer layer -> shadow/readout</small>"]')
    lines.append("")

    assigned: set[str] = set()
    for group_name, ids in DOMAIN_GROUPS:
        present = [theory_id for theory_id in ids if theory_id in theories]
        assigned.update(present)
        lines.append(f"  subgraph {re.sub(r'[^A-Za-z0-9_]', '_', group_name)}[{group_name}]")
        for theory_id in present:
            lines.append(f"    {node_label(theories[theory_id])}")
        lines.append("  end")
        lines.append("")

    other = sorted(set(theories) - assigned)
    if other:
        lines.append("  subgraph Other_Theory_Cards[Other Theory Cards]")
        for theory_id in other:
            lines.append(f"    {node_label(theories[theory_id])}")
        lines.append("  end")
        lines.append("")

    lines.append("  subgraph Built_Missing_Layers[Constructed / Candidate Missing Layers]")
    lines.append('    L_qm_gr["L: QM-GR common-refinement parent<br/><small>E018 finite-toy candidate; frame transfer not certified</small>"]')
    lines.append('    Lstar_sm["L*: SM selection/measure layer<br/><small>E009/E019/E020/E037/E043 finite toy v2</small>"]')
    lines.append('    GR_upper["GR upper-boundary readouts<br/><small>E021/E042 finite toy</small>"]')
    lines.append("  end")
    lines.append("")

    lines.append("  subgraph Foreclosures[E3 Foreclosures / Open Holes]")
    for edge_id, (_, label, _, is_open) in FORECLOSURE_ATTACHMENTS.items():
        suffix = " (open)" if is_open else ""
        lines.append(f'    F_{edge_id}["{edge_id}: {label}{suffix}"]')
    lines.append("  end")
    lines.append("")

    lines.append("  subgraph Legend[Legend]")
    lines.append('    LEG_SOLID["solid: established E0/E1 shadow"]')
    lines.append('    LEG_DASH["dashed: E2 recognition/import or finite-toy candidate"]')
    lines.append('    LEG_RED["thick red: E3 foreclosure/open hole"]')
    lines.append("  end")
    lines.append("")

    for edge_id in backbone_ids:
        edge = edges_by_id[edge_id]
        src, dst = orient_edge(edge)
        operator = edge_operator(edge["scored_tier"])
        label = f'{edge_id} {edge["scored_tier"]}'
        lines.append(f"  {src} {operator}|{label}| {dst}")
        directed_edges.append((src, dst))
        provenance.append(
            {
                "edge_id": edge_id,
                "source": edge["source_theory_id"],
                "target": edge["target_theory_id"],
                "emitted": f"{src} -> {dst}",
                "direction": normalize_direction(edge["arrow_direction"]),
                "tier": edge["scored_tier"],
                "modality": edge["scored_modality"],
            }
        )
        if edge["scored_tier"] == "E2":
            link_styles.append(f"  linkStyle {link_index} stroke:#6c757d,stroke-dasharray:5 5;")
        link_index += 1

    # E018 is intentionally not rendered as a QM<->GR manifest edge.
    lines.append("  L_qm_gr -.->|E018 candidate parent| quantum_mechanics")
    directed_edges.append(("L_qm_gr", "quantum_mechanics"))
    link_styles.append(f"  linkStyle {link_index} stroke:#6c757d,stroke-dasharray:5 5;")
    link_index += 1
    lines.append("  L_qm_gr -.->|E018 candidate parent| general_relativity")
    directed_edges.append(("L_qm_gr", "general_relativity"))
    link_styles.append(f"  linkStyle {link_index} stroke:#6c757d,stroke-dasharray:5 5;")
    link_index += 1

    for edge_id, (theory_id, _, built_id, _) in FORECLOSURE_ATTACHMENTS.items():
        edge = edges_by_id[edge_id]
        lines.append(f"  {theory_id} ==>|{edge_id} {edge['scored_tier']}| F_{edge_id}")
        directed_edges.append((theory_id, f"F_{edge_id}"))
        link_styles.append(f"  linkStyle {link_index} stroke:#c1121f,stroke-width:3px;")
        link_index += 1
        if built_id:
            lines.append(f"  {built_id} -.->|finite-toy response| F_{edge_id}")
            directed_edges.append((built_id, f"F_{edge_id}"))
            link_styles.append(f"  linkStyle {link_index} stroke:#6c757d,stroke-dasharray:5 5;")
            link_index += 1

    lines.append("")
    lines.append("  classDef theory fill:#f8f9fa,stroke:#495057,color:#111;")
    lines.append("  classDef built fill:#e7f5ff,stroke:#1971c2,stroke-width:2px,color:#0b1f33;")
    lines.append("  classDef foreclosure fill:#fff0f0,stroke:#c1121f,stroke-width:2px,color:#3b0000;")
    lines.append("  classDef open fill:#fff3bf,stroke:#e67700,stroke-width:2px,color:#3b2500;")
    lines.append("  classDef legend fill:#ffffff,stroke:#adb5bd,color:#111;")
    lines.append(f"  class {','.join(sorted(theories))} theory;")
    lines.append("  class L_qm_gr,Lstar_sm,GR_upper built;")
    closed = [f"F_{eid}" for eid, (_, _, _, is_open) in FORECLOSURE_ATTACHMENTS.items() if not is_open]
    opened = [f"F_{eid}" for eid, (_, _, _, is_open) in FORECLOSURE_ATTACHMENTS.items() if is_open]
    lines.append(f"  class {','.join(closed)} foreclosure;")
    lines.append(f"  class {','.join(opened)} open;")
    lines.append("  class Title,LEG_SOLID,LEG_DASH,LEG_RED legend;")
    lines.extend(link_styles)

    return "\n".join(lines), provenance, directed_edges, list(sorted(theories))


def format_table(headers: list[str], rows: list[list[str]]) -> str:
    out = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    out.extend("| " + " | ".join(row) + " |" for row in rows)
    return "\n".join(out)


def main() -> None:
    theory_rows = read_jsonl(THEORY_MANIFEST)
    edge_rows = read_jsonl(EDGE_MANIFEST)
    phase3 = parse_phase3_table()
    theories = {row["id"]: row for row in theory_rows}
    theory_ids = set(theories)
    edges_by_id = {row["id"]: row for row in edge_rows}

    missing_backbone = [edge_id for edge_id in BACKBONE_IDS if edge_id not in edges_by_id]
    if missing_backbone:
        raise SystemExit(f"Backbone IDs missing from manifest: {missing_backbone}")

    for edge_id in BACKBONE_IDS:
        edge = edges_by_id[edge_id]
        if edge["source_theory_id"] not in theory_ids or edge["target_theory_id"] not in theory_ids:
            raise SystemExit(f"Backbone edge {edge_id} has non-theory endpoint")
        if normalize_direction(edge["arrow_direction"]) == "bidir":
            raise SystemExit(f"Backbone edge {edge_id} is bidirectional and cannot be oriented")

    for source_list in CONSTRUCTION_SOURCES.values():
        for rel in source_list:
            if not (ROOT / rel).exists():
                raise SystemExit(f"Construction source missing: {rel}")

    mermaid, provenance, directed_edges, theory_node_ids = build_mermaid(theories, edges_by_id, BACKBONE_IDS)

    # Required checks.
    all_diagram_edges = directed_edges
    direct_qm_gr = any(
        {src, dst} == {"quantum_mechanics", "general_relativity"}
        for src, dst in all_diagram_edges
    )
    l_to_qm = ("L_qm_gr", "quantum_mechanics") in all_diagram_edges
    l_to_gr = ("L_qm_gr", "general_relativity") in all_diagram_edges
    incoming_reductions_classical = []
    for prov in provenance:
        if prov["tier"] in {"E0", "E1"} and prov["emitted"].endswith(" -> classical_mechanics"):
            incoming_reductions_classical.append((prov["edge_id"], prov["emitted"]))
    classical_ok = sorted(incoming_reductions_classical) == [
        ("E003", "special_relativity -> classical_mechanics"),
        ("E006", "quantum_mechanics -> classical_mechanics"),
    ]
    gr_newton = any(prov["edge_id"] == "E010" and prov["emitted"] == "general_relativity -> newtonian_gravity" for prov in provenance)
    qm_path_to_gr = reachable(all_diagram_edges, "quantum_mechanics", "general_relativity")
    no_cycle = not has_cycle(all_diagram_edges)
    all_backbone_real = all(prov["edge_id"] in edges_by_id for prov in provenance)
    checks = {
        "a_no_qm_gr_direct_edge": not direct_qm_gr,
        "b_L_parent_edges_present": l_to_qm and l_to_gr,
        "c_classical_two_incoming_reductions": classical_ok,
        "d_gr_to_newtonian_present_not_under_qm": gr_newton and not qm_path_to_gr,
        "e_no_directed_cycle": no_cycle,
        "f_backbone_edges_manifest_backed": all_backbone_real,
    }

    phase3_rows = []
    for prov in provenance:
        edge = edges_by_id[prov["edge_id"]]
        phase3_rows.append(
            [
                prov["edge_id"],
                prov["source"],
                prov["target"],
                prov["direction"],
                prov["tier"],
                prov["modality"],
                prov["emitted"],
                phase3_status(edge, phase3),
            ]
        )

    omitted_rows = []
    rendered_foreclosures = set(FORECLOSURE_ATTACHMENTS)
    for edge in edge_rows:
        reason = omitted_reason(edge, theory_ids, rendered_foreclosures)
        if not reason:
            continue
        omitted_rows.append(
            [
                edge["id"],
                f"{edge['source_theory_id']} -> {edge['target_theory_id']}",
                normalize_direction(edge["arrow_direction"]),
                edge["scored_tier"],
                reason,
            ]
        )

    selfcheck_rows = [
        ["a", "No direct quantum_mechanics <-> general_relativity edge anywhere", "PASS" if checks["a_no_qm_gr_direct_edge"] else "FAIL"],
        ["b", "L_qm_gr -.-> quantum_mechanics and L_qm_gr -.-> general_relativity present", "PASS" if checks["b_L_parent_edges_present"] else "FAIL"],
        ["c", "classical_mechanics has exactly two incoming E0/E1 reductions: E006 and E003", "PASS" if checks["c_classical_two_incoming_reductions"] else "FAIL"],
        ["d", "general_relativity -> newtonian_gravity E010 present; GR shadows are not chained under QM", "PASS" if checks["d_gr_to_newtonian_present_not_under_qm"] else "FAIL"],
        ["e", "No directed cycle in emitted directed graph", "PASS" if checks["e_no_directed_cycle"] else "FAIL"],
        ["f", "Every backbone edge maps to a real manifest E-number", "PASS" if checks["f_backbone_edges_manifest_backed"] else "FAIL"],
    ]

    built_source_rows = []
    for layer, sources in CONSTRUCTION_SOURCES.items():
        built_source_rows.append([layer, "<br/>".join(sources)])

    constructed_response_edges = 2 + sum(1 for _, (_, _, built, _) in FORECLOSURE_ATTACHMENTS.items() if built)
    visible_node_count = len(theory_node_ids) + 3 + len(FORECLOSURE_ATTACHMENTS) + 4

    doc = f"""# Physics Layer Atlas Theory Map

Generated by [`physics_atlas/generate_theory_map.py`](generate_theory_map.py) from:

- `physics_atlas/phase3/scored_run/theory_manifest.jsonl`
- `physics_atlas/phase3/scored_run/edge_manifest.jsonl`
- cross-check table in `physics_atlas/phase3/PHASE3_ATLAS.md`

## Reading Guide

Arrow convention: every arrow points from the richer or more-fundamental layer to its shadow, readout, or coarser layer. Manifest `down` edges keep their source-to-target direction. Manifest `up` edges are reoriented as target-to-source when they are included in the directed backbone.

Critical QM/GR rule: `quantum_mechanics` and `general_relativity` are siblings under the constructed finite-toy parent `L_qm_gr`. There is no direct QM-to-GR or GR-to-QM reduction arrow in this map.

E3 cards are not inserted into the reduction backbone as theory layers. They are rendered as foreclosure nodes attached to the relevant manifest theory-card endpoint. For cards whose other endpoint is not a theory-manifest node, such as E037, the attachment uses the manifest theory-card endpoint and the source/provenance remains in the omitted-edge ledger.

Styles:

- Solid arrow: E0/E1 established shadow relation.
- Dashed arrow: E2 recognition/import relation or a finite-toy candidate-layer response.
- Thick red arrow: E3 foreclosure/open hole.
- Blue nodes: constructed finite-toy missing layers.
- Yellow foreclosure nodes: still open here.

## Master Mermaid Map

```mermaid
{mermaid}
```

## Focused QM/GR Inset

```mermaid
flowchart TB
  L_qm_gr["L: common-refinement parent<br/><small>finite-toy candidate; frame transfer not certified</small>"]
  quantum_mechanics["Non-relativistic Quantum Mechanics"]
  general_relativity["General Relativity"]
  newtonian_gravity["Newtonian Gravity"]
  classical_mechanics["Classical Mechanics"]

  L_qm_gr -.->|E018 candidate parent| quantum_mechanics
  L_qm_gr -.->|E018 candidate parent| general_relativity
  general_relativity -->|E010 E1| newtonian_gravity
  quantum_mechanics -->|E006 E1| classical_mechanics

  classDef built fill:#e7f5ff,stroke:#1971c2,stroke-width:2px,color:#0b1f33;
  classDef theory fill:#f8f9fa,stroke:#495057,color:#111;
  class L_qm_gr built;
  class quantum_mechanics,general_relativity,newtonian_gravity,classical_mechanics theory;
```

## Constructed-Layer Sources

{format_table(["Layer node", "Source files"], built_source_rows)}

## Backbone Edge Provenance

Every backbone edge below is generated from `edge_manifest.jsonl`; the last column checks the human-readable Phase 3 table.

{format_table(["E", "manifest source", "manifest target", "direction", "tier", "modality", "emitted orientation", "Phase3 table"], phase3_rows)}

## Omitted Manifest Edges

The backbone is intentionally compact and acyclic. E3 foreclosures that matter for the constructed work are shown as foreclosure nodes. Minor phenomenon/candidate/readout edges are omitted below, with reasons.

{format_table(["E", "manifest relation", "direction", "tier", "reason"], omitted_rows)}

## Self-Verification

{format_table(["Check", "Requirement", "Result"], selfcheck_rows)}

## Generation Stats

- Theory nodes from manifest: `{len(theory_node_ids)}`.
- Visible master-map nodes including built layers, foreclosures, title, and legend: `{visible_node_count}`.
- Built/candidate layer nodes: `3`.
- Foreclosure/open-hole nodes rendered: `{len(FORECLOSURE_ATTACHMENTS)}`.
- Manifest backbone edges rendered: `{len(provenance)}`.
- Constructed/candidate response edges rendered: `{constructed_response_edges}`.
- All six required checks: `{"PASS" if all(checks.values()) else "FAIL"}`.
"""

    if not all(checks.values()):
        failed = [name for name, ok in checks.items() if not ok]
        raise SystemExit(f"Self-checks failed: {failed}")

    OUTPUT.write_text(doc)
    print(f"wrote {OUTPUT}")
    print(f"theory_nodes={len(theory_node_ids)} backbone_edges={len(provenance)} checks=PASS")


if __name__ == "__main__":
    main()
