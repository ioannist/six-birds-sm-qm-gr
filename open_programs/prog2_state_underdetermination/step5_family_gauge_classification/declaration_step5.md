# PROG2 Step 5 frozen family-gauge declaration

Frozen on 2026-08-27 before the Step-5 pair classifications were computed.

## Three distinct relations

1. **Cut equivalence** means equality of the complete terminal min-cut
   fingerprint. The PROG3 five-move system belongs here.
2. **Tensor-presentation gauge** consists of internal `g,g^-1` insertions,
   explicitly constructed state-preserving Step-1 series/parallel tensor
   contractions or merges, and products of boundary-local unitaries. Internal
   and boundary changes do not act on capacity labels.
3. **Canonical-family capacity relabeling** for a connected `C2_L1` copy
   carrier consists only of a terminal-label-fixed weighted graph isomorphism
   or the global reciprocal of every edge capacity accompanied by the global
   boundary `X`.

A single-edge reciprocal is not a canonical-family move. A PROG3 graph move is
not state gauge merely because it preserves all cuts. Such a move could enter
the state-gauge relation only after an explicit tensor-level intertwiner is
constructed. Equality of a final boundary state alone is not accepted as a
gauge proof.

## Connected-copy parity lemma

For the binary copy tensor

`C = |0,...,0> + |1,...,1>`,

applying `X` on a subset `S` of its legs sends its two supported bit strings to
the characteristic string of `S` and its complement. This is again supported
on the two constant strings only when `S` is empty or contains every leg.
Therefore a local copy tensor returns to canonical copy form iff the incident
swap bits are all zero or all one.

An edge reciprocal exchanges its two Schmidt labels and hence contributes the
same swap bit at both endpoints. On a connected carrier, the copy constraint at
adjacent vertices forces their local all-zero/all-one choices to agree.
Propagation along paths makes every edge swap bit globally constant. Thus the
only family-returning reciprocal actions are the identity and the global
all-edge reciprocal. The latter induces the corresponding global boundary
`X`. Step 5 encodes this proof by exhaustive local subset checks for every
vertex degree occurring in the six carriers and by solving the resulting
connected parity constraints.

## Exact invariant

For a positive weighted carrier define the unordered pair

`I(c) = { sum_e c_e, sum_e c_e^(-1) }`.

It is invariant under every declared generator:

- a terminal-fixed weighted isomorphism only permutes edge terms;
- internal `g,g^-1` changes do not alter capacities;
- boundary-local unitaries do not alter capacities;
- global reciprocal exchanges the two entries of the unordered pair;
- an explicitly state-identity-proved series/parallel presentation merge would
  require its invariant action to be proved before admission. The six current
  endpoint graphs are checked for applicable Step-1 series or parallel tensor
  reductions. If none exists, this generator is vacuous on their classification
  orbits and no unproved capacity transformation is admitted.

The pair classification is `SURVIVING_FINITE_C2_L1_DECLARED_GAUGE_EXAMPLE` only
when exact terminal-fixed isomorphism checks fail both directly and after global
reciprocal, no admitted Step-1 merge applies, and the two exact invariant pairs
differ. Any exact map is typed as an explicit gauge collapse. An incomplete
comparison remains a candidate, never an example.
