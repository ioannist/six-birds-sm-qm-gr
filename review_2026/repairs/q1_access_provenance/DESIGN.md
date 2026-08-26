# Q1-REPAIR-1 design

## Scope and pinned inheritance

The repair imports the published four-bit carrier and quotient coordinates from `physics_atlas/thread_qm_gr/steps/step22_f51_unification_common_refinement_artifacts/f51_unification_step22.py:22-43`, the Born audit from `step25_sourcing_unification_artifacts/sourcing_unification_step25.py:27-35`, and normalization/back-reaction from `step26_semiclassical_dynamics_artifacts/semiclassical_dynamics_step26.py:25-46`. All imported scripts have literal SHA-256 pins. Step24 fields, Step28 histories, the Step28 build script, and the F24 family source record are also pinned as source evidence.

This is a computed finite provenance, not a claim that these coarse functionals are uniquely forced by continuum physics.

## Field-to-mode functionals

For an eight-site complex field `psi`, Step25 computes `rho=|psi|^2` and the oriented current `j=Im(conj(psi)*central_gradient(psi))`. Step26 computes `T00=|central_gradient(psi)|^2+V0|psi|^2`. With the inherited moderate coupling `kappa=0.3`, the modes are:

- `d0 = round(sum rho)`, a coarse conserved normalization sector;
- `d1 = 1[sum j >= 0]`, a phase/current-orientation sector determined by the Born audit;
- `d2 = argmax rho`, a Born-visible density sector;
- `d3 = argmax(V0 + 0.3*T00)`, a geometry-visible back-reaction sector.

Every track field is normalized, so the observed population has only `d0=1`; the repair does not claim empirical variation of the normalization coordinate. Ties in `argmax` use NumPy's deterministic lowest-index convention. The population contains all 26 Step25 source fields, all 16 Step28 history fields, eight fresh states from seed 71017, a conjugate phase pair, and a fixed-field/potential-only pair.

Complex conjugation preserves density and `T00` while reversing current, giving a controlled `d1` split inside one `q_GR` fiber. Changing only the background potential preserves the entire Born audit while changing `d3`, giving a controlled split inside one `q_QM` fiber. The stored Step28 potentials are independently recomputed from the pinned formula.

## Declared partition class

The exhausted class consists of the 16 partitions of the complete Boolean four-mode carrier induced by coordinate subsets. Directed factorization is computed from fibers: `A` determines `B` iff no two states in one `A` fiber lie in distinct `B` fibers. Every one of the 120 unordered distinct pairs is checked in both directions. Meets are common refinements; joins are computed by transitive closure of the two fiber equivalence relations. The closure contains exactly the same 16 partitions. The full Bell partition lattice on 16 labelled states is deliberately outside the declared class.

## Generated F24 maps and gates

The eight official family names are read from the pinned Step20 F24 source record. Each family is instantiated as a deterministic map on the 16-state carrier. A ninth fused-duplicate control implements the published direct sum `(d0,d1,d2,d0,d2,d3)` from `step31_qg_fused_object_nogo_artifacts/fused_object_nogo_step31.py:37-59`.

The exact representatives are: `MemoryLayer=(d0,d1,d2,d1 XOR d3)` (a reversible exposed record); `HiddenUpstreamRole=(d0,d1,d2)`; `BridgeMediatedRole=L`; `BudgetedRole=(d0,d1,d2,d0 XOR d2)`; `ScopedRole=(d0,d1,d2,d3)` only for `d0=0`; `CoarsenedRole=(d0,d2,d1 XOR d3)`; `OutsideRoleScope` exposes `d1,d3` only for `d0=0`; and `BlockedNonClosure=(d0,d1,d2,BLOCKED)`. These definitions are also carried as data in the competitor summary.

`G_stability` is exact idempotence of the rational conditional-mean completion induced by the map's fibers. `G_control_QM/GR` are exact fiber factorizations to the two endpoints. `G_audit` requires a formed, total deterministic map. `G_nosmuggle` requires at most four output coordinates and no duplicate coordinate columns. Reconciliation is the conjunction of these computed gates. Partition equivalence to `L` is equality of fiber equivalence relations, not identifier reuse. Status strings are selected from these computed results.

The family maps are finite diagnostic representatives of the declared shapes, not an exhaustion of every set-theoretic map with a family label.
