# S1 carrier reconstruction design

## Scope

This repair reconstructs the fixed published window with a consistent representation model. It does not widen the dimension, charge, field-count, or component-dimension windows. It also deliberately retains the published closure/route and higher-layer predicates so that representation and carrier semantics are the only foundational changes in this packet. The higher-layer mass predicate remains a `PROXY`; repairing that physical predicate is a separate packet.

## Representation model

`representation_model.py` implements the manager-ruled alphabet

`{singlet, fund, antifund, sym2, conj_sym2, antisym2, conj_antisym2}`

from formulas, rather than importing the published representation code. Dimension-specific isomorphisms are canonicalized before field types are created:

- SU(2): `antifund = fund`, both antisymmetric labels are `singlet`, and both symmetric labels are the real `sym2`/adjoint class.
- SU(3): `antisym2 = antifund` and `conj_antisym2 = fund`.
- SU(4): `antisym2` is real, so its conjugate label canonicalizes to the same class.

These identities make canonicalization exact rather than merely textual. The self-test requires conjugation closure and involution on each canonical set, equal dimensions and twice-Dynkin indices for conjugates, negated cubic anomalies, and zero cubic anomaly for every self-conjugate representation.

The implemented formulas are:

- `dim(fund)=N`, `dim(sym2)=N(N+1)/2`, and `dim(antisym2)=N(N-1)/2`; conjugates have the same dimensions.
- In twice-index normalization, `2T(fund)=1`, `2T(sym2)=N+2`, and `2T(antisym2)=N-2`; conjugates have the same indices.
- For `N>2`, `A(fund)=1`, `A(sym2)=N+4`, and `A(antisym2)=N-4`; conjugates negate these coefficients. All SU(2) cubic anomalies are zero.

Published counterpart: the original alphabet and windows are at `physics_atlas/thread_cluster_a/steps/step28_mode_b_neutral_representation_desmuggle_artifacts/mode_b_neutral_representation_desmuggle_step28.py:25-29`; its formulas and incomplete conjugation are at lines 71-114. The later SU(2) correction and faulty fallback model are at `physics_atlas/thread_cluster_a/steps/step33_mode_b_corrected_anomaly_chirality_artifacts/corrected_anomaly_chirality_step33.py:95-132`.

## Fixed carrier window

- Nonabelian dimensions: 2 through 4.
- One or two factors, with nondecreasing dimension tuples.
- Charge units: `(-6,-4,-3,-2,-1,0,1,2,3,4,6)`.
- At most five fields.
- Per-field component dimension at most six.
- Representation support pattern: singlet, one active factor at a time, and fundamental/antifundamental bifundamentals for two-factor structures. This is the published support pattern, now canonicalized and conjugation-closed; the packet does not broaden it to arbitrary multi-active two-index products.

Published counterparts: constants and factor structures are at Step 28 lines 25-28 and 133-137; the support pattern is at lines 140-155; component filtering, anomaly multiplicities, abelian terms, and Witten parity are at lines 158-195.

## Multiset semantics

A field content is a multiset of canonical `(rep tuple, charge)` field types with size one through five. Repeated canonical field types are allowed and represented by repeated type indices. There is exactly one row per sorted multiset. The neutral population is counted analytically by `sum(C(n+k-1,k), k=1..5)` for each type inventory; its SHA-256 commits to the complete canonical generating specification. Anomaly-closed rows are materialized exactly with a fixed split: sizes 1-3 are enumerated directly, size 4 uses a 1+3 split, and size 5 a 2+3 split. The ordering boundary makes each multiset appear once. There is no truncation.

The published enumeration used `itertools.combinations` and a bit mask, hence distinct-field set semantics, at Step 28 lines 207-216 and 271-307 and Step 33 lines 259-295.

## Selection chain

1. `neutral_carrier`: all canonical field-content multisets in the fixed window; population is exact and analytic.
2. `genuinely_chiral`: zero cubic and mixed anomaly for every factor, zero mixed gravitational-U(1) and U(1)^3 anomaly, correct SU(2) Witten parity, and a non-vectorlike residual after exact conjugate cancellation. Cross-factor representation dimensions multiply anomaly coefficients exactly as in Step 28 lines 170-193.
3. `atomic_packaging`: proper-submultiset atomicity, active action on every factor, and primitive signed charge orbit, ported from Step 33 lines 328-382.
4. `closure_consistency`: the published route-incidence predicate from Step 33 lines 385-404. Its singleton-active-field restriction is intentionally retained for like-for-like chain isolation; roster-based competitor coverage is a later repair.
5. `chirality_faithfulness`: a residual complex nonabelian action after conjugate cancellation, ported from Step 33 lines 407-454.
6. `higher_layer_mass_closure_proxy`: Step 35 lines 75-261. The predicate is ported without a new physical selector. The spelling extension is conjugation-equivariant for the newly explicit conjugate two-index representations, and repeated field types are tracked as distinct occurrences so multiset coverage is well-defined. This stage is explicitly a `PROXY`.
7. `clean_separation`: the low-energy subgroup/coset census from Step 38 lines 53-123 and the factorization-defect count from Step 41 lines 38-122. The maximum confinement factor is used if more than one exists, matching the later full-carrier diagnostic convention; all final repaired survivors have a single confinement factor.

Every stage computation is a pure function returning an exact population and a SHA-256 membership hash (or, for the analytic neutral stage, a SHA-256 of the complete canonical generating specification). File writers are confined to `build_s1_carrier_reconstruction.py`.

## S1-REPAIR-2 foundation conventions

Repair 2 retains all version-1 artifacts as the historical first-scalar record and adds only `*_v2` artifacts. `DESIGN_REPAIR1.md` freezes the exact document hashed by the version-1 schema.

### Inert singlets

Structures are defined modulo freely adjoined fully neutral fields `(singlet,...,singlet; q=0)`. Such a field changes neither anomaly closure, chirality, gauge action, nor any later selection predicate. The canonical map deletes every occurrence before forming the structure key. This convention preserves the 1,066-row genuinely-chiral labelled carrier. For transparency, treating every padding multiplicity within the five-field cap as a distinct structure gives 1,578 rows. Repair 2 enumerates those padded rows independently and requires their normalized key set to equal the 1,066-row unpadded carrier.

### Equivalence and quotient policy

Headline populations quotient the following gauge-description relabellings:

- exchange of equal-dimensional factor slots;
- simultaneous conjugation of all nonabelian representations, viewed as the overall complex-conjugation outer automorphism;
- independent global inversion `q -> -q`, because the sign of the U(1) generator is conventional.

These operations act on every field in a structure. They are not applied field-by-field. Unequal-dimensional factors are not exchanged. Labelled counts are retained beside every quotient count. Neutral-carrier orbit counts use exact Burnside enumeration of fixed multisets, while materialized stages canonicalize explicit orbits and verify closure under every declared operation.

This is the physically standard policy used here because gauge-factor names, complex-conjugate basis choice, and abelian generator orientation cannot distinguish a theory. It does not identify spectra related by arbitrary charge rescaling or by conjugating only a selected field.

### Scalar branches and quantifiers

A complex scalar representation and its conjugate are one branch: the mass predicate already tests both `phi` and `phi-dagger`, so counting them separately would duplicate a physical scalar field. All distinct scalar-conjugacy branches that both complete every fermion occurrence and break U(1) are enumerated. No ordering criterion selects a witness.

The low-energy shadow, residual active factor, coset count, factorization-defect count, and clean/breaking verdict are computed for every `(structure, scalar-branch)` row. A second implementation independently regenerates scalar assignments and occurrence coverage. The validator compares its key set to the written branch table and fails on either a missing or extra branch.

Two clean-separation statements are kept distinct:

- **universal over branches:** a bare structure `C` is clean only if every admissible scalar branch is clean;
- **branch existential:** the selected object is `(C,phi)`, and `C` qualifies when at least one admissible branch is clean.

The published and repair-1 first-by-sort statement is retained only as historical evidence and is not silently reinterpreted as either quantifier.

### Golden formula check

`carrier_chain_v2.py` contains an independent hardcoded table of 13 standard SU(2), SU(3), and SU(4) representation values. Its source and normalization are cited in the function comment. The table is not generated from the representation formulas; it checks dimension, twice-Dynkin index, and cubic anomaly separately on every validator run.
