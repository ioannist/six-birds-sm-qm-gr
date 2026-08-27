# Step-4 FIX2 generated-gauge closure declaration

This addendum supersedes only the gauge-closure and bulk-invariant portions of
`preregistration_step4_corrective.md`. The original continuation candidate set,
root-selection rule, and endpoint construction remain unchanged.

Each endpoint is represented in its exact number field `QQ(alpha)`, with
elements reduced modulo the exported irreducible minimal polynomial. One
breadth-first worklist applies, in every visited presentation:

1. series reduction;
2. exact two-terminal module replacement;
3. saturated-terminal or zero-column contraction;
4. inseparable-vertex contraction with parallel merge;
5. Delta-Y or Y-Delta replacement;
6. each single-edge reciprocal `c_e -> 1/c_e`;
7. terminal-label-fixed exact weighted canonicalization and deduplication.

Five graph moves are admitted only after exact full terminal-cut re-enumeration
proves preservation of the current state's complete fingerprint and continued
uniqueness. Reciprocal moves are state-level basis swaps and are admitted without
requiring preservation of the cut fingerprint. Sign and comparison decisions use
rational isolating-interval refinement in `QQ(alpha)`.

No finiteness theorem is asserted for the alternating generated system. The hard
budget is **64 canonical states and 20 wall-clock seconds per endpoint**. Hitting
either budget is `PENDING_BUDGET_TRUNCATED`, never saturation. Orbit intersections
are exact within the visited terminal-fixed canonical sets. A capacity-multiset
signature over a truncated explored set is diagnostic only and is not called an
invariant proof.
