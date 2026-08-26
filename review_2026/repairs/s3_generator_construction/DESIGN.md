# S3-REPAIR-1 design

## Scope and non-import rule

This repair constructs new mathematical objects in this directory. It reads no artifact or build module from `physics_atlas/`; those files are cited below only to identify the assertions being replaced. Consequently there are no imported-script hash pins to maintain and no dependency on a sibling repository. `physics_atlas/` remains untouched.

All Lie-algebra matrices use exact Gaussian rationals (`Fraction` real and imaginary parts). Rank, nullspace, traces, weights, commutators, determinants, and Smith determinantal divisors are exact. No floating-point tolerance enters a scientific result.

## Replaced assertions

| Published counterpart | Assertion in the published construction | Replacement here |
|---|---|---|
| `physics_atlas/thread_cluster_a/steps/step63_mode_b_unification_common_refinement_layer_artifacts/unification_common_refinement_step63.py:55` | A seven-row SM `(T3,Y)` roster is supplied literally. | The 15 basis vectors of `5bar + wedge^2(5)` are acted on by the embedded generators; connected weight components and their charges are computed. |
| same file, line 129 | The five fundamental hypercharge eigenvalues are supplied literally. | The diagonal traceless centralizer of the computed `su(3)+su(2)` block embedding is solved by exact nullspace elimination. |
| same file, line 142 | Parent properties and selection booleans are assigned in a hand-written candidate list. | A bounded diagnostic class of regular `SU(n)`, `n=5..8`, has dimensions, centralizer dimensions, coset dimensions, extra singlets, and package dimensions computed. This does not claim global parent uniqueness. |
| `physics_atlas/thread_cluster_a/steps/step45_mode_b_proton_decay_F27_artifacts/proton_decay_f27_step45.py:26` | Baryon/color state labels are supplied. | Color type is classified from computed SU(3) weights; B follows the declared physical rule on `3`, `3bar`, and `1`. |
| same file, line 94 | Each witness is assigned a quark source and lepton target. | Every transition is read from nonzero entries of the explicit coset-generator action on `5bar+10`. |
| `physics_atlas/thread_cluster_a/steps/step46_mode_b_monopole_F48_artifacts/monopole_f48_step46.py:56` | Coset charges and conjugate pair IDs are assigned from witness order. | The quotient cocharacter lattice is computed from embedded coroot columns; Smith invariants, the primitive loop, and its index against the derived centralizer are computed. |
| same file, line 79 | A charged-pair count is used as the topology obstruction. | The exact-sequence result is stated only after the integer lattice gives `pi_1(H)=Z` and the `Z6` index. |
| `physics_atlas/thread_cluster_a/steps/step47_mode_b_gut_sm_nonfactorization_artifacts/gut_sm_nonfactorization_step47.py:44` | Exactly six witness identifiers are imported. | The coset dimension is obtained from the explicit Lie-algebra complement. |
| same file, line 52 | SM and GUT roles are assigned to named states. | Subalgebra/coset membership and all quantum numbers come from matrix support and commutators. |
| `physics_atlas/thread_cluster_a/steps/step41_mode_b_factorization_defect_clean_separation_artifacts/factorization_defect_clean_separation_step41.py:38` | Six proxy bosons are generated from dimension counts and type labels. | An independent `su(4)->su(3)+u(1)` construction determines whether its six coset directions are identical to, or merely analogous to, SU(5) X/Y directions. |

## Stage A

### Lie algebras and centralizers

`su(n)` is represented by `n(n-1)` off-diagonal Hermitian matrices and `n-1` traceless diagonal matrices. The validator checks Hermiticity, tracelessness, count, and exact span rank. For the regular SU(5) embedding, SU(3) acts on indices `0,1,2` and SU(2) on `3,4`.

For an unknown diagonal `D=diag(x_i)`, every nonzero embedded off-diagonal matrix entry contributes the equation `x_i-x_j=0`; tracelessness contributes `sum_i x_i=0`. Nullspace computation must return one dimension. An orientation rule chooses a positive weak block. Only after this derivation, the continuous coordinate scale is fixed by assigning charge `+1` to the weak-pair basis state of `wedge^2(5)`. This makes the residual normalization choice explicit.

The 12-dimensional real coset is spanned by symmetric and antisymmetric Hermitian cross-block matrices. Quantum numbers are most transparently reported in the complexified root basis `E_iα,E_αi`; their commutators with the computed Cartans give color weights, weak weights, and Y eigenvalues. Conjugate root pairs correspond to the real Hermitian pairs.

### Fermions and ratios

The antifundamental action is `-G^T`; the antisymmetric-ten action is induced algorithmically on wedge pairs. Connected components under the embedded nonabelian generators are classified by their computed Cartan weight sets. The trace sums run over these 15 constructed states, not a pasted particle roster.

Two abelian coordinates are reported: the standard weak-pair-unit coordinate and `Y'=2Y`. The second is not advocated physically; it demonstrates exactly which ratios depend on the residual scale convention when electric charge is correspondingly declared to be `T3+Y'`.

### SU(4) comparison

The identical centralizer procedure gives the SU(4) six-root coset. `E_i3 -> E_i3` and its reverse provide a fixed-weak-index vector-space map into SU(5), after a computed charge-unit rescaling of `5/8`. The fixed slice is moved by SU(2), so it is not the complete SU(5) X/Y representation.

## Stage B

### F27

The computation uses left-chiral fields, so color `3bar` states carry baryon number `-1/3`, while color `3` states carry `+1/3` and singlets carry zero. A generator mediates Delta-B precisely when a nonzero action-matrix entry joins states with different computed B. The same test is run on every embedded SM generator to establish algebraic B conservation after the coset is removed.

### F48

SU(5) cocharacters use the integer basis `e0-e4,...,e3-e4`. The embedded SU(3) and SU(2) derived subgroup contributes three coroot columns. Exact minors give their Smith invariants. The primitive annihilating character is paired with the centralizer vector obtained in Stage A; index six is therefore a cross-stage computation, not a separately supplied quotient label.

The inference `pi_2(G/H)=ker[pi_1(H)->pi_1(G)]` imports the standard long exact homotopy sequence and the facts that SU(5) is simply connected and has vanishing `pi_2`. These assumptions are named in the results. “SM alone” means no larger broken parent: `G=H`, so the quotient is a point. It means no topologically required GUT monopole, not a proof that every possible SM global form or UV completion is monopole-free.

## Parent-scope ruling

The computed selector is deliberately bounded to regular `SU(n)` embeddings for `5<=n<=8`. It repairs hand-assigned booleans within that diagnostic class. It does not enumerate SO(10), E6, exceptional embeddings, or arbitrary representation packages, so global uniqueness is recorded as `REMAINING-IMPORT` rather than silently promoted.

## Validation and mutations

`run_s3_generator_construction.py --self` recomputes all stages in memory, byte-compares every written result to deterministic serialization, checks the artifact hash manifest, and requires rejection of three mutations:

1. perturb two hypercharge eigenvalues while preserving trace;
2. exchange a computed quark and lepton role;
3. add a traceful diagonal entry to an SU(5) generator.

Each mutation targets a formerly asserted input and must fail its independent structural gate.

## S3-REPAIR-1b verification closure

The version-2 artifacts preserve every version-1 output and replace four proof gaps found in
verification. First, the centralizer calculation now expands an unknown matrix in all 24
traceless Hermitian SU(5) generators and solves every real and imaginary component of its
commutator with the embedded SU(3) and SU(2) generators. Diagonality is therefore an output,
not an ansatz. A fixed exact rational SO(5) conjugation supplies an embedding-covariance test:
the commutant dimension, normalized trace, coset charges, and extracted lattice must be
unchanged after conjugation.

Second, the F48 input columns are extracted from the matrices named `B0_D_1`,
`(B0_D_2-B0_D_1)/2`, and `B1_D_1`. Only after extracting their integer diagonal entries does
the code express them in the cocharacter basis `e_i-e_4` and perform Smith/annihilator/index
computations. The topology inference explicitly declares its non-matrix inputs: H is connected,
`pi_1(SU(5))=0`, and `pi_2(SU(5))=0`.

Third, all six SU(4) roots are explicit matrices. Their charges under the constructed SU(4)
and SU(5) centralizers determine the `5/8` rescaling. The commutator `[E_34,E_03]=-E_04`
is computed, and the code independently tests that `E_04` lies outside the fixed slice. This
refutes identity while establishing the narrower fixed-slice analogue relation.

Fourth, the product-parent control replaces the unsupported `3/23` control in
`paper/sections/sec_04_result_sm.tex:85` (expanded in
`paper/appendices/app_a_formal_calculus.tex:160` and generated by
`physics_atlas/thread_cluster_a/steps/step63_mode_b_unification_common_refinement_layer_artifacts/unification_common_refinement_step63.py:142-157`). The natural well-posed semisimple
product construction is Pati-Salam `SU(4)xSU(2)_LxSU(2)_R`: its B-L direction, hypercharge
coefficient, sixteen weights, and trace ratio are constructed. Independent product-factor
couplings remain an explicit convention. A reductive `SU(3)xSU(2)xU(1)` rescaling family is
also evaluated only to show that `3/23` at scale two is freely selectable rather than derived.

The version-2 validator adds four load-bearing tests to the original three mutations: generic
embedding conjugation invariance, rejection of a corrupted extracted coroot, rejection of a
deleted X/Y action in F27, and rejection of a mutated SU(4) slice. It recomputes the entire
construction and byte-compares all version-2 artifacts.
