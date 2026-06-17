# Canonical naming map — physics construction tracks & review packets

**Why this file exists.** During the construction sessions the working labels "Cluster A / Cluster B" were
used **inverted relative to the Physics Layer Atlas's own labels** (`missing_layers/MISSING_LAYER_ATLAS.md`,
where "Cluster A" = the *trans-Planckian* group). To remove all ambiguity, **review packets are named by
content** (descriptive names), not by "Cluster A/B". The internal construction tracks keep their
session-working directory names as the historical record, mapped here. **When in doubt, identify a deliverable
by its EDGE LIST, not by any "Cluster" word.**

| Content (descriptive)             | Edges                                  | Construction track dir            | Session label | Atlas label (MISSING_LAYER_ATLAS) | Review packet (current)        |
|-----------------------------------|----------------------------------------|-----------------------------------|---------------|-----------------------------------|--------------------------------|
| **QM↔GR program**                 | E018                                   | `thread_qm_gr/`                   | (—)           | part of atlas "Cluster A" (trans-Planckian) | `qm_gr_program_v2/`            |
| **GR upper-boundary**             | E021 (cosmological constant), E042 (singularities) | `thread_cluster_b/`     | "Cluster B"   | part of atlas "Cluster A" (trans-Planckian) | `gr_upper_boundary_v3/`        |
| **SM selection/measure layer**    | E009, E019, E020, E037, E043           | `thread_cluster_a/`               | "Cluster A"   | atlas "Cluster B" (SM-selection family)     | `sm_selection_layer_v1/`       |

**Key point:** the session label "Cluster A" (our SM-selection work, `thread_cluster_a/`) is the atlas's
"Cluster B"; and the session label "Cluster B" (`thread_cluster_b/`, E021+E042) is part of the atlas's
"Cluster A". The descriptive packet names (`sm_selection_layer`, `gr_upper_boundary`, `qm_gr_program`) sidestep
the collision entirely — use those.

**Remaining atlas E3 edge (not yet constructed):** E032 — quantum_mechanics → measurement-outcome (the atlas's
"near-singleton").

**Internal artifacts** (the `thread_cluster_a/` and `thread_cluster_b/` manager logs, cascade maps, and the
consolidated-statement `.tex` files) still use the session "Cluster A/B" words in their bodies — that is the
honest construction record. Each is internally consistent and is mapped by this table; every review packet's
cover letter states its scope by edge list + this mapping, so no reviewer is left guessing.
