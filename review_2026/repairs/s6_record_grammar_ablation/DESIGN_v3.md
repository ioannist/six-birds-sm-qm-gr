# S6-ABLATION-3 design

This version keeps every v1/v2 artifact unchanged and imports the accepted v2 residual stabilizer under a literal SHA-256 pin. `physics_atlas/` is not imported or modified by v3.

## Search bound and exact gates

- Fermion arity is 2 through 4. The largest residual factor is SU(3), whose epsilon arity is three; the requested “largest epsilon plus one” bound is therefore four.
- Up to two insertions total of the singleton branch scalar `phi` and its conjugate `phi-dagger` are allowed. Total constituent count is capped at six.
- Repeated field occurrences follow the inherited Fock-content convention. Grassmann, derivative, equations-of-motion, and dynamical-decay relations are not silently imposed.
- Tensor products are decomposed by the pinned S1-v3 Littlewood--Richardson coefficient implementation. Determinant-height columns are removed algorithmically for SU(N). A candidate enters only if its UV U(1) charge is zero, every UV factor has nonzero exact singlet multiplicity, every residual factor has nonzero exact singlet multiplicity, and its computed residual U(1) charge is zero.
- The common channel count is the minimum of the exact UV and residual singlet-space dimensions. This is the declared finite invariant-channel basis; Clebsch projection relations between different Fock contents are outside the available exact machinery and are not guessed.

## VEV quotient and counting conventions

A scalar-dressed residual operator is admissible iff its UV lift is gauge invariant. Lifts with the same residual component multiset and invariant channel, differing only by insertions of the same branch VEV, are identified. Distinct Fock contents are retained; further invariant-ring syzygies are not available in the inherited machinery.

Two capacity conventions are reported: `undressed_only` counts quotient operators possessing a zero-scalar lift; `dressed_inclusive` counts the union of undressed and scalar-dressed quotient operators. The census also reports the overlap and the dressed-new increment, preventing the trivial gauge-singlet `phi*phi-dagger` dressing from being double-counted.
