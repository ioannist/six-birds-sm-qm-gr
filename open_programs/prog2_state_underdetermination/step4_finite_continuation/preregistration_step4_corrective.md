# PROG2 Step 4 corrective preregistration

Frozen on 2026-08-27 before the corrective finite-continuation solve. The original `preregistration_step4.md` remains untouched as historical evidence of the tangent-plane error. This document replaces only its search-space restriction and downstream stopping logic.

## Corrected search space

The candidate set remains exactly the six deduplicated Step-3 protected directions. For each distinct base, let `K=ker J_cut` be the complete exact integer cut-kernel with ordered basis `B=(b_0,...,b_{k-1})`. Let `g_j=sum_e b_{j,e}/c_e`, the exact derivative of `log(product c)` on that basis. Step 3’s protected space is `S=ker g`, a codimension-one tangent space inside `K`; it is not the full finite search space.

For each protected direction `v in S`, choose the transverse direction `u` deterministically as the first ordered cut-kernel basis vector `b_j` with `g_j != 0`. Since `v in S` and `u notin S`, they are independent. Search the curve

`c'(t)=c+t v+s(t)u`

inside the complete affine cut-kernel space `c+K`, not inside `c+S`.

## Tangent-plane lemma retained with corrected scope

The AM–GM result in the frozen preregistration remains correct only on `c+S`: a nonzero positive `delta in S` cannot preserve the product exactly. It is henceforth named the **tangent-plane lemma**. A curved product-level branch in `c+K` has tangent in `S` but generally develops a transverse `u` component at order `t^2`; the lemma does not exclude it.

Because `d log P(u)=g(u) != 0`, the implicit-function theorem supplies a unique local product-preserving branch `s(t)` through zero for every candidate.

## Exact-algebraic solve and deterministic size rule

Start with exact rational `t=1/10000`. Form over `Q` the univariate polynomial

`F_t(s)=product_e(c_e+t v_e+s u_e)-product_e c_e`.

Isolate every real root using exact SymPy polynomial root isolation to width at most `10^-70`. Select the unique simple root whose isolating interval contains the local branch prediction nearest zero and for which all capacities stay positive. If any rigorous positivity, coordinate-interval, unique-cut, or root-isolation gate fails, replace `t` by `t/2` and repeat, for at most twelve halvings. Publish the first passing point and every attempted `t`; never substitute an outcome-selected convention, direction, or carrier.

The exact endpoint is represented by the polynomial and a rational isolating interval for its selected real root. Product equality is exact algebraic evidence; a high-precision residual is diagnostic only.

## PROG3 interval and full-fingerprint gates

Write the total kernel displacement in exact basis coordinates. Every coordinate interval induced by the isolating interval for `s` must lie strictly inside the corresponding imported PROG3 exact finite-range interval. This coordinate-wise check is reported but is not used as a substitute for full enumeration.

For every one of the `2^|T|-2` ordered terminal regions, enumerate every interior cut assignment at the algebraic endpoint. Compare affine-in-root cut values by rigorous rational interval bounds. The active cut must be unique, its value must equal the base fingerprint exactly because the displacement lies in `K`, and the reported minimum margin is the rigorous positive lower bound across all inactive cuts.

## Independent state and entropy recomputation

For both endpoints, independently build and contract the complete `C2_L1` tensor network and compute all `2^|T|` entropies. Evaluate the algebraic endpoint coefficients at 100 decimal digits using the isolated root. The analytic product symmetry is a cross-check only. State and entropy equality use the inherited preregistered numerical allowance and are graded `DENSE_NUMERICAL_EVIDENCE`; exact product equality remains the exact-algebraic part.

## Executed gauge closure

For every constructed endpoint execute and report separately:

1. same-graph terminal-label-fixed automorphisms with exact algebraic weight comparison;
2. saturated closure under all five PROG3 move classes, using affine algebraic weights and rigorous root-interval cut comparisons, followed by terminal-fixed weighted orbit intersection with the base orbit;
3. internal tensor gauges `g,g^-1`, tested as presentation invariance but not allowed to alter Schmidt spectra;
4. all per-edge `c_e <-> 1/c_e` Schmidt-basis swaps combined with terminal-fixed graph automorphisms, tested exactly against the displaced algebraic capacities;
5. products of boundary-local unitaries: unequal boundary states are rejected immediately; equal states are typed boundary-state equivalent but do not erase a differing bulk invariant.

The saturation safety budgets remain `100000` canonical states and 20 seconds per endpoint. A hit is typed `PENDING_BUDGET_TRUNCATED`, never as disjointness.

## Bulk invariant and proof obligation

Retain the frozen capacity-orbit multiset signature: the lexicographically sorted set of exact sorted capacity multisets over the complete terminal-fixed five-move orbit, enlarged by all finite per-edge reciprocal swaps. Terminal-fixed isomorphisms permute a multiset; starting at another state in the saturated five-move component leaves the complete set unchanged; reciprocal swaps are explicitly quotiented; internal tensor gauges and boundary-local unitaries do not alter capacities. Thus the signature is invariant under every declared gauge generator.

Evaluate both endpoint signatures exactly in the common algebraic number field. A surviving candidate requires different signatures. Equal signatures are `BULK_INVARIANT_FAILURE`; intersecting gauge orbits are `GAUGE_RELATED_COINCIDENCE`.

## Typed outcomes and stopping

Each of the six rows receives exactly one primary outcome:

- `CONTINUATION_CONSTRUCTED__STATE_SPLIT`
- `CONTINUATION_CONSTRUCTED__GAUGE_RELATED_COINCIDENCE`
- `CONTINUATION_CONSTRUCTED__BULK_INVARIANT_FAILURE`
- `CONTINUATION_CONSTRUCTED__SURVIVING_UNDERDETERMINATION_CANDIDATE`
- `ROOT_ISOLATION_FAILURE`
- `POSITIVITY_FAILURE`
- `FINITE_RANGE_FAILURE`
- `FINGERPRINT_FAILURE`
- `STATE_RECONTRACTION_FAILURE`
- `PENDING_BUDGET_TRUNCATED`

All six gauge/bulk obligations must be executed after a finite endpoint passes the fingerprint and state stages. No obligation may remain `NOT_APPLICABLE` for a constructed endpoint. Stop after the first deterministically passing `t` per candidate, complete execution of every downstream obligation, and publication of all attempted sizes and outcomes.
