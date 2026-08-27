# PROG3 Step 3 design note

## Corrected transition-system typing

Step 2 drains a finite queue under five proposal classes, but it does not compute an
undirected orbit. Series removal, exact two-terminal module replacement, zero/saturated
contraction, and inseparable contraction are proposed only in their reducing direction.
Delta–Y and Y–Delta are proposed in both directions. Its computed object is therefore a
**queue-exhaustive forward reachability set under four directed reductions and bidirectional
Delta–Y/Y–Delta**, restricted at every admission to presentations with unique active
minimizers and the unchanged complete terminal min-cut fingerprint. Disjoint forward sets do
not imply disjoint symmetric-closure orbits.

## L1 — series normal form on the admissible expansion family

The maintained `transform_series` replaces the two incident capacities `a,b` by
`min(a,b)`; `make_graph` sums that edge with an already-present parallel edge. The inverse
family used here replaces an edge of capacity `c` by a positive path with edge capacities
whose minimum is exactly `c`. For a fixed loopless simple series-reduced presentation and its homeomorphic
edge subdivisions, removal terminates because every rewrite deletes one nonterminal vertex.
Each maximal subdivided path contracts to the minimum of its capacities. Associativity and
commutativity of `min` make removals on one path order-independent, while removals on
different paths have disjoint interiors and commute. Thus this admissible subdivision family
has the original presentation as its unique terminal-fixed weighted series normal form.
The 13 actual carrier-level certificates independently expand the first edge as
`(c,2c,3c)`, remove the two new vertices in both orders, and recover the same endpoint.

For every terminal cut, a two-edge expansion contributes zero when its endpoints lie on the
same side and `min(a,b)=c` when they differ, so the complete fingerprint is unchanged. If the
original minimizer cuts that edge, its lift is unique exactly when `a != b`; for an edge never
used by an active cut, equality `a=b=c` can only tie inactive lifts and does not spoil active
uniqueness. Therefore the exact condition is: `min(a,b)=c`, and either `a != b` or the edge's
active-cut incidence column is zero. The certified `(c,2c)` and `(c,2c,3c)` splits satisfy
the strict case.

This proof is deliberately scoped to genuine homeomorphic subdivisions. It does not assert
confluence for arbitrary simple graphs containing a pendant cycle whose suppression would
require a self-loop representation absent from the maintained graph type.

## L2 — failed subdivided-Y-leg coherence case

The proposed projection fails on the stored `K23_bipartite__b6__leaf_offset0`, seed 31
endpoint (`fiber_008`). The lexicographically first admissible case subdivides
`<Y:<I1+I2>+I0+I3>--<I1+I2>` with exact capacities `19327353111/8589934592|19327353111/4294967296`. Applying
Y–Delta at `<Y:<I1+I2>+I0+I3>` gives the former subdivision vertex two new triangle edges, so
its degree becomes 3. There are no removable internal
bivalent vertices afterward. The two routes are

1. `series_subdivision -> y_delta -> series_normal_form(0 removals)`; and
2. `y_delta -> series_normal_form(0 removals)`.

Both endpoints have the same complete exact fingerprint as the starting endpoint, unique
minimizers, and minimum margin `34359710543/858993459200`. Yet their normal forms
have respectively 9/10
and 8/9 nodes/edges and
are not terminal-fixed weighted isomorphic. A Delta–Y/Y–Delta move replaces three edges by
three edges; exact parallel merging can only lower, never raise, edge count. Hence a
Delta-only path starting from the 9-edge reduced route
cannot reach the 10-edge normal form. This is the exact
local coherence obstruction requested by the dispatch. The CSV exports all three complete exact
weighted-edge presentations, not merely their carrier identifier and differing local capacities.

Because L2 fails, the L3 projection theorem is not invoked. This artifact stops the upgrade
rather than treating the failure of that proof route as evidence for or against the full
symmetric closure.

## Corrected literature reading

Kalman and Krauthgamer, [arXiv:2112.06916, Theorem 3.24](https://arxiv.org/abs/2112.06916),
exclude a universal local degree-`k>3` star-to-clique transformation preserving the terminal
min-cut metric. Their Open Question 4.5 leaves context-dependent and nonlocal transformation
systems open. The result supports only the statement that Delta–Y is the available universal
local star-mesh rule below degree four; it does not prove completeness of this repository's
five-class repertoire.
