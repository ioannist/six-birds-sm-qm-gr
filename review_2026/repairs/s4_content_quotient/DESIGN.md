# S4 quotient-corrected content repair design

## Scope and imported foundation

This repair leaves `physics_atlas/` read-only and imports the sound S1 v2 representation/carrier machinery. `representation_model.py`, `carrier_chain.py`, and `carrier_chain_v2.py` are checked against literal SHA-256 constants before import. The packet reconstructs the fixed content window and does not widen the S1 carrier.

The inherited carrier conventions are those declared in `review_2026/repairs/s1_carrier_reconstruction/DESIGN.md:62-76`: freely adjoined fully neutral singlets are deleted, simultaneous nonabelian conjugation and independent global `q -> -q` are equivalences, and equal-dimensional factor slots may be exchanged. Factor exchange is inactive for the selected unequal `2|3` structure.

## Quotient-corrected census

The Step-15 analogue reconstructs its distinct-field alphabet, charge window, anomaly vectors, and exact meet-in-the-middle enumeration rather than reading its output CSV. Published counterparts are `physics_atlas/thread_cluster_a/steps/step15_minimal_anomaly_support_artifacts/minimal_anomaly_support_step15.py:22-26`, `:33-108`, and `:120-158`. The exact reproduction gates are 1,161 raw anomaly-free supports and 28 nonempty irreducible supports.

Step 15 already canonicalized overall U(1) sign (`minimal_anomaly_support_step15.py:146-158`) but did not quotient the independent global color-conjugation automorphism. Applying the full declared group pairs all 28 labelled rows into 14 physical orbits. Unequal factors are not exchanged, and inert singlets have already been removed.

The strongest conjunction ports all six structural predicates from `physics_atlas/thread_cluster_a/steps/step16_content_selection_principle_artifacts/content_selection_principle_step16.py:70-126`. Its two labelled survivors are tested as quotient images, not presumed distinct. The v2 branch-complete clean content is independently grouped with `candidate_orbit_key` and `branch_orbit_key`.

The published Step-48 canonicalizer considered only the identity and the *combined* U(1)-sign/color-conjugation operation (`physics_atlas/thread_cluster_a/steps/step48_mode_b_content_cascade_artifacts/content_cascade_step48.py:71-89`). The repaired group contains those operations independently. Therefore the published “SM + 1 alternative” pair is tested for physical distinctness before any shadow is evaluated. If only one orbit exists, a two-object discrimination test is undefined and the three published shadows are marked not applicable.

## Generic mass rank

The Step-54 object counted whether each charged component was touched by at least one invariant edge (`physics_atlas/thread_cluster_a/steps/step54_mode_b_content_cascade_3_artifacts/content_cascade_3_step54.py:54-145`); it did not construct or rank a matrix.

This repair expands every fermion multiplet occurrence into weak-weight and color components. After choosing the neutral component of the computed clean scalar branch, it inserts every allowed gauge-invariant bilinear into a symmetric Weyl mass matrix. Every allowed generation-to-generation Yukawa channel gets an independent symbolic coefficient. Gauge-related color copies share that coefficient. Electric-charge and color sectors are retained explicitly.

The rank certificate is exact and uses only the Python standard library. Structurally zero rows give an upper bound. Setting each generation Yukawa matrix to the identity is an exact integer specialization evaluated by rational Gaussian elimination; when that specialization reaches the upper bound, a maximal minor polynomial is nonzero and the generic symbolic rank equals the bound. This is stronger than numerical sampling and avoids interpreting edge coverage as rank.

## Genuine N-copy probe

For N=1 through 4 the selected five-field content is copied as an actual multiset and passed to the unmodified v2 compute predicates:

- anomaly closure, Witten parity, and non-vectorlike chirality;
- `atomic_package`, `no_spectator_action`, and `primitive_charge_orbit` separately and as `atomic_rewrite_packaging`;
- `route_incidence_complete`;
- `chirality_faithfulness`;
- branch-complete scalar enumeration, branch-typed clean separation, and production occurrence coverage;
- the explicit generic mass-rank computation.

N>1 exceeds the original five-field enumeration cap. These rows are an explicit extension probe, not additions to the base carrier denominator. The predicates themselves accept materialized multisets of arbitrary finite size, so no surrogate booleans are used. The published surrogate assigned packaging, chirality, clean separation, and mass closure from `N>=1` at `physics_atlas/thread_cluster_a/steps/step51_mode_b_ngen_neutrality_artifacts/ngen_neutrality_step51.py:112-140`; this repair replaces those assignments with actual computations.

## Determinism and validation

`build_s4_content_quotient.py` contains pure compute functions and deterministic writers. `run_s4.py --self` verifies every source pin and control, rebuilds the complete result in a temporary directory, and byte-compares every generated CSV, JSON, and findings note.
