# S1-REPAIR-3 condition typing

This document extends the frozen `DESIGN.md` version-2 record. Version 3 preserves every
version-1 and version-2 artifact. In the version-2 record, the unqualified term “scalar branch”
meant exactly one complex scalar field, with that field and its Hermitian conjugate treated as
one physical branch. Version 3 calls this a **singleton complex-scalar branch** everywhere. The
inherited scalar alphabet uses the same representation support, charge table, and
component-dimension cap of six as the fermion construction. Thus the historical “44 structures
without branches” statement is typed as “44 chirality-faithful structures without an admissible
singleton complex-scalar branch.”

## Two-scalar appendix

The appendix enumerates unordered multisets of exactly two complex scalar fields; repeated
scalar species are allowed. Each member independently belongs to the inherited scalar alphabet
and independently obeys the component-dimension cap of six. The cap is per scalar, matching the
production alphabet, rather than an unmotivated sum-of-dimensions cap. Each complex field is
identified with its conjugate branch before pair multisets are formed.

Joint Yukawa coverage is the union of the occurrence-coverage masks supplied by either scalar
and either conjugate orientation. Joint breaking requires at least one nonzero scalar charge and
at least one nontrivial nonabelian scalar representation; these two roles may be supplied by
different fields. The residual and `Delta_fact` calculation is the inherited finite-toy proxy:
on each carrier-active factor, no active scalar leaves SU(N), while one or more active scalars
use the inherited SU(N-1) residual label. Multiple VEV alignment is not derived, so this appendix
does not promote that proxy. Pair results are reported beside, and never substituted for, the
singleton headline.

## Charge-normalization conventions

Two orbit conventions are reported in parallel:

1. **Declared-charge orbits** retain the finite charge table literally and quotient only
   equal-factor exchange, simultaneous nonabelian conjugation, and global U(1) sign inversion.
2. **Primitive-normalized orbits** additionally divide every structure's nonzero charges by
   their common positive gcd before orbit canonicalization.

The declared-charge result is retained for exact comparison with the bounded enumeration. The
primitive-normalized result is preferred for the community-facing population because an overall
U(1) generator scale is conventional; counting distinct integer multiples as different carrier
objects overstates the denominator. Both percentages remain visible, together with the fully
labelled count. The atomic stage already demands primitive signed charges, so the downstream
37/27/24 orbit populations are invariant between the two conventions.

## Independent singleton gate

The version-3 gate declares a second canonical representation table containing SU(2), SU(3),
and SU(4) Young diagrams, dimensions, and conjugates. It independently regenerates the scalar
support and charge alphabet without calling production `neutral_rep_assignments()` or
`scalar_representations()`. For every representation triple, the singlet multiplicity is the
Littlewood-Richardson coefficient of the conjugate target in the first two factors, including
explicit removal of determinant-height columns. Singleton occurrence coverage then uses these
exact multiplicities and charge conservation without calling production `yukawa_invariant()` or
`factor_invariant()`. The validator requires the independently generated singleton branch keys
to equal the written singleton table exactly.
