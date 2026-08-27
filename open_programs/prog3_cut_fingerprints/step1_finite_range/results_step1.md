# PROG3 Step 1 — exact finite-range cut-fingerprint fibers

## Exact reconstruction and lift

The 13 rows in the pinned P1-v3 survivor artifact were rebuilt from the declared carrier generator, not
from its decimal display columns. For edge index `i` in an `m`-edge carrier, the exact seeded rule is
`randint(85,115)/100 + 2^i/2^(m+24)`, with the PRNG initialized from the declared SHA-256-derived seed.
Thus no decimal-to-rational guess enters the certification path. Every cut value, margin, rank, kernel
direction, crossing bound, and perturbed fingerprint comparison uses `fractions.Fraction`.

All 13 v3 survivor statuses reproduce exactly. The three formerly near-tolerance margins are:

- `wheel_W4__b8__leaf_offset0`, seed 47: `135/274877906944` (genuinely positive).
- `wheel_W4__b8__leaf_offset1`, seed 17: `113/274877906944` (genuinely positive).
- `K23_bipartite__b8__dual_gateway`, seed 47: `79/17179869184` (genuinely positive).

No row changes cell or becomes degenerate under exact arithmetic.

## Per-carrier recertification

| carrier | seed | raw exact margin | reduced rank/edges | kernel dim | direction fibers | circular planar raw/reduced | v3 status |
|---|---:|---:|---:|---:|---:|---|---|
| wheel_W4__b8__leaf_offset0 | 47 | `135/274877906944` | 11/14 | 3 | 3/3 | False/False | REPRODUCED |
| wheel_W4__b8__leaf_offset1 | 17 | `113/274877906944` | 10/12 | 2 | 2/2 | False/True | REPRODUCED |
| wheel_W4__b8__leaf_offset1 | 31 | `68719477861/6871947673600` | 10/12 | 2 | 2/2 | False/True | REPRODUCED |
| K23_bipartite__b6__leaf_offset0 | 31 | `34359710543/858993459200` | 8/9 | 1 | 1/1 | False/True | REPRODUCED |
| K23_bipartite__b6__dual_gateway | 47 | `34359672093/1717986918400` | 8/9 | 1 | 1/1 | False/True | REPRODUCED |
| K23_bipartite__b7__leaf_offset1 | 47 | `17179890559/1717986918400` | 9/10 | 1 | 1/1 | False/True | REPRODUCED |
| K23_bipartite__b8__leaf_offset0 | 17 | `68719474211/6871947673600` | 12/13 | 1 | 1/1 | False/False | REPRODUCED |
| K23_bipartite__b8__leaf_offset1 | 17 | `137438951697/6871947673600` | 11/12 | 1 | 1/1 | False/True | REPRODUCED |
| K23_bipartite__b8__leaf_offset1 | 31 | `137438900347/6871947673600` | 12/13 | 1 | 1/1 | False/False | REPRODUCED |
| K23_bipartite__b8__leaf_offset1 | 47 | `34359651393/3435973836800` | 12/13 | 1 | 1/1 | False/False | REPRODUCED |
| K23_bipartite__b8__dual_gateway | 17 | `68719475661/6871947673600` | 10/12 | 2 | 2/2 | False/True | REPRODUCED |
| K23_bipartite__b8__dual_gateway | 31 | `68719478661/6871947673600` | 11/13 | 2 | 2/2 | False/False | REPRODUCED |
| K23_bipartite__b8__dual_gateway | 47 | `79/17179869184` | 13/14 | 1 | 1/1 | False/False | REPRODUCED |

The circular-planarity decision uses the cofacial augmentation criterion: append one new apex joined
to every terminal, then apply the exact combinatorial Left-Right Planarity Test. All 13 raw carriers
fail this test. After certified reductions, 7 are circular planar and 6 are not; this status change is
a property of the reduced presentations, not an arithmetic discrepancy.
The observable is a terminal min-cut function, not a Dirichlet-to-Neumann response matrix; electrical
criticality was not checked. The seven reduced circular-planar rows show that circular planarity alone
does not remove min-cut fibers. This is not a counterexample to the electrical uniqueness theorem.

## Exact finite-range intervals

For each unique active cut `a`, every enumerated competing cut `c` supplies the exact inequality
`(c-a)·(w+t v) >= 0`. Intersecting all such inequalities gives the maximal fingerprint interval.
The positive-capacity interval is reported separately in `kernel_intervals_step1.csv`.

| carrier | seed | basis | maximal exact fingerprint interval | chosen interior t* | fiber |
|---|---:|---:|---|---:|---|
| wheel_W4__b8__leaf_offset0 | 47 | 0 | `[-5222680276311/6871947673600,3161096009431/3435973836800]` | `3161096009431/6871947673600` | True |
| wheel_W4__b8__leaf_offset0 | 47 | 1 | `[-5222680276311/6871947673600,738734416087/858993459200]` | `738734416087/1717986918400` | True |
| wheel_W4__b8__leaf_offset0 | 47 | 2 | `[-5222680276311/6871947673600,738734416087/858993459200]` | `738734416087/1717986918400` | True |
| wheel_W4__b8__leaf_offset1 | 17 | 0 | `[-1563368178519/1717986918400,3023657110359/3435973836800]` | `3023657110359/6871947673600` | True |
| wheel_W4__b8__leaf_offset1 | 17 | 1 | `[-18966575764311/6871947673600,3023657110359/3435973836800]` | `3023657110359/6871947673600` | True |
| wheel_W4__b8__leaf_offset1 | 31 | 0 | `[-51539610863/68719476736,6322192019287/6871947673600]` | `6322192019287/13743895347200` | True |
| wheel_W4__b8__leaf_offset1 | 31 | 1 | `[-2336462265399/858993459200,51539610863/68719476736]` | `51539610863/137438953472` | True |
| K23_bipartite__b6__leaf_offset0 | 31 | 0 | `[-798863956181/1717986918400,1065151899783/3435973836800]` | `1065151899783/6871947673600` | True |
| K23_bipartite__b6__dual_gateway | 47 | 0 | `[-148176378637/429496729600,1391569492679/3435973836800]` | `1391569492679/6871947673600` | True |
| K23_bipartite__b7__leaf_offset1 | 47 | 0 | `[-678604849443/1717986918400,4088809044167/6871947673600]` | `4088809044167/13743895347200` | True |
| K23_bipartite__b8__leaf_offset0 | 17 | 0 | `[-1443109144831/13743895347200,137439086947/6871947673600]` | `137439086947/13743895347200` | True |
| K23_bipartite__b8__leaf_offset1 | 17 | 0 | `[-154618828241/343597383680,1443109082971/2748779069440]` | `1443109082971/5497558138880` | True |
| K23_bipartite__b8__leaf_offset1 | 31 | 0 | `[-292057808803/3435973836800,7352984368327/13743895347200]` | `7352984368327/27487790694400` | True |
| K23_bipartite__b8__leaf_offset1 | 47 | 0 | `[-8589936567/858993459200,6253472740551/13743895347200]` | `6253472740551/27487790694400` | True |
| K23_bipartite__b8__dual_gateway | 17 | 0 | `[-1511828559707/1374389534720,223338327367/1717986918400]` | `223338327367/3435973836800` | True |
| K23_bipartite__b8__dual_gateway | 17 | 1 | `[-910533094677/858993459200,223338327367/1717986918400]` | `223338327367/3435973836800` | True |
| K23_bipartite__b8__dual_gateway | 31 | 0 | `[-34359747123/1374389534720,1236950652763/2748779069440]` | `1236950652763/5497558138880` | True |
| K23_bipartite__b8__dual_gateway | 31 | 1 | `[-34359747123/1374389534720,34359743963/687194767360]` | `34359743963/1374389534720` | True |
| K23_bipartite__b8__dual_gateway | 47 | 0 | `[-79/34359738368,5291400066247/13743895347200]` | `5291400066247/27487790694400` | True |

All **19** basis directions have nondegenerate two-sided intervals. Exact full cut
enumeration at every selected interior point certifies **19**
direction-level fibers across **13 of 13** carriers.
For every pair, the weights differ; no graph automorphism maps one weighting
to the other; all minimizers remain unique; and each endpoint is returned as the minimum of the
declared depth-three closure objective.

## Exact depth-three five-move orbit audit

For each endpoint, every exact accepted replacement state and every intermediate deterministic-fold
state visited to replacement depth three is retained. Weighted presentations are canonicalized with
terminal labels fixed pointwise, non-terminal labels free, and exact `Fraction` weights included.
The two canonical state sets are intersected; an intersection is reported as gauge with explicit paths
from both endpoints.

| carrier | seed | basis | accepted moves base/perturbed | canonical orbit states base/perturbed | cross isomorphisms | verdict |
|---|---:|---:|---:|---:|---:|---|
| wheel_W4__b8__leaf_offset0 | 47 | 0 | 8/8 | 5/5 | 0 | depth-three five-move-orbit-disjoint |
| wheel_W4__b8__leaf_offset0 | 47 | 1 | 8/8 | 5/5 | 0 | depth-three five-move-orbit-disjoint |
| wheel_W4__b8__leaf_offset0 | 47 | 2 | 8/8 | 5/5 | 0 | depth-three five-move-orbit-disjoint |
| wheel_W4__b8__leaf_offset1 | 17 | 0 | 0/0 | 1/1 | 0 | depth-three five-move-orbit-disjoint |
| wheel_W4__b8__leaf_offset1 | 17 | 1 | 0/0 | 1/1 | 0 | depth-three five-move-orbit-disjoint |
| wheel_W4__b8__leaf_offset1 | 31 | 0 | 0/0 | 1/1 | 0 | depth-three five-move-orbit-disjoint |
| wheel_W4__b8__leaf_offset1 | 31 | 1 | 0/0 | 1/1 | 0 | depth-three five-move-orbit-disjoint |
| K23_bipartite__b6__leaf_offset0 | 31 | 0 | 5/5 | 3/3 | 0 | depth-three five-move-orbit-disjoint |
| K23_bipartite__b6__dual_gateway | 47 | 0 | 5/5 | 3/3 | 0 | depth-three five-move-orbit-disjoint |
| K23_bipartite__b7__leaf_offset1 | 47 | 0 | 0/0 | 1/1 | 0 | depth-three five-move-orbit-disjoint |
| K23_bipartite__b8__leaf_offset0 | 17 | 0 | 8/8 | 5/5 | 0 | depth-three five-move-orbit-disjoint |
| K23_bipartite__b8__leaf_offset1 | 17 | 0 | 0/0 | 1/1 | 0 | depth-three five-move-orbit-disjoint |
| K23_bipartite__b8__leaf_offset1 | 31 | 0 | 0/0 | 1/1 | 0 | depth-three five-move-orbit-disjoint |
| K23_bipartite__b8__leaf_offset1 | 47 | 0 | 0/0 | 1/1 | 0 | depth-three five-move-orbit-disjoint |
| K23_bipartite__b8__dual_gateway | 17 | 0 | 0/0 | 1/1 | 0 | depth-three five-move-orbit-disjoint |
| K23_bipartite__b8__dual_gateway | 17 | 1 | 0/0 | 1/1 | 0 | depth-three five-move-orbit-disjoint |
| K23_bipartite__b8__dual_gateway | 31 | 0 | 0/0 | 1/1 | 0 | depth-three five-move-orbit-disjoint |
| K23_bipartite__b8__dual_gateway | 31 | 1 | 0/0 | 1/1 | 0 | depth-three five-move-orbit-disjoint |
| K23_bipartite__b8__dual_gateway | 47 | 0 | 9/9 | 6/6 | 0 | depth-three five-move-orbit-disjoint |

Headline: **19 of 19** fibers are depth-three five-move-orbit-disjoint; **0 of 19**
have a cross-presentation gauge witness in the declared bounded orbit.

## Anti-bypass and scope

Every perturbed fingerprint is recomputed by exhaustive enumeration of all interior vertex-side
assignments for all nontrivial terminal subsets. The Jacobian is used only to choose candidate kernel
directions; it is never used to synthesize or extrapolate a perturbed fingerprint.

**EXACT_FINITE_RANGE_FIBERS_WITH_DEPTH_THREE_ORBIT_AUDIT_ON_ALL_13_PINNED_CARRIERS.** This is a finite-carrier result
for the terminal min-cut fingerprint and the declared depth-three five-move orbit audit. It is not a
state-level entanglement result, an unbounded irreducibility result, or a uniqueness theorem for
arbitrary graphs or non-local equivalences.
