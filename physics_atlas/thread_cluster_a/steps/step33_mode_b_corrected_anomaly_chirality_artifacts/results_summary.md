Deflationary truth first: Step 32 had a real physics bug. It used the formal `cubic_a(rep, dim) != 0` proxy as the test for complex non-abelian chirality. That proxy is wrong for rank-one non-abelian factors: their local cubic anomaly vanishes and their consistency is controlled by Witten parity. Step 33 corrects the anomaly bookkeeping and redoes the carrier and predicate stack.

## Corrected Bookkeeping

- Rank-one non-abelian cubic anomaly: set to `0` for all reps.
- Witten parity: retained.
- Higher-rank cubic coefficients: retained as `fund=+1`, `antifund=-1`, `antisym2=N-4`, `sym2=N+4`, `adjoint=0`, `singlet=0`.
- Complexness test: self-conjugacy of the non-abelian representation, not cubic-anomaly value.
- The correction is physics-principled bookkeeping, not a target-shape rule.

## Corrected Carrier

- Old Step-28 carrier count: 280,983.
- Corrected carrier count: 11,990.

Per-structure corrected carrier counts:

| dimensions | corrected carrier |
| --- | ---: |
| 2 | 730 |
| 2\|2 | 6,656 |
| 2\|3 | 2,153 |
| 2\|4 | 1,754 |
| 3 | 85 |
| 3\|3 | 170 |
| 3\|4 | 226 |
| 4 | 56 |
| 4\|4 | 160 |

## Corrected Trajectory

| stage | survivors | reference passes |
| --- | ---: | --- |
| corrected neutral carrier | 11,990 | true |
| atomic rewrite packaging | 156 | true |
| closure consistency completeness | 130 | true |
| corrected chirality faithfulness | 80 | true |

Final per-structure counts:

| dimensions | final survivors | reference passes |
| --- | ---: | ---: |
| 2 | 0 | 0 |
| 2\|2 | 0 | 0 |
| 2\|3 | 15 | 1 |
| 3 | 49 | 0 |
| 4 | 16 | 0 |

The old Step-32 `2|2` dominance is broken: it falls from 272 old survivors to 0 corrected final survivors. The final dominant structure is `3` with 49 survivors, so the target structure is not dominant and the reference is not unique.

## Correctness Checks

- Rank-one fundamental cubic: `0`.
- Rank-one symmetric cubic: `0`.
- Higher-rank fundamental cubic: `1|1`.
- Higher-rank antifundamental cubic: `-1|-1`.
- Rank-two antisymmetric in dimension 4: `0`.
- Complexness test uses self-conjugacy: rank-one fundamental is self-conjugate; higher fundamental is not.

## Gates

- Primitive exclusion: pass.
- Dependency trace: pass, traced to P2, P5/P1/F27, P3/P6, and P3.
- Ablation: pass.
- Negative controls: pass. The predicate is not a target-row picker and fails some corrected Step-31 survivors.
- Stage II: pass. The reference is present and both pass/fail channels are detected.
- Correctness self-check: pass.

## Verdict

`NARROW`: the corrected physics bookkeeping sharply changes the carrier and breaks the old `2|2` dominance while keeping the reference support. It still does not uniquely distinguish the reference.

Next grammar delta: conjoin an F24 role-obstruction selector or P6 audit-saturation ledger over the corrected chirality-faithful pool.

Grade: finite-carrier correctness re-derivation / narrowed intrinsic-discriminator result. No physical gauge-structure theorem, value derivation, or frame-transfer status upgrade is supplied.
