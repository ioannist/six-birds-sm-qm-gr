# adversarial audit trail: what was rejected, and why

We publish the program's rejected constructions deliberately. A framework as expressive as this one can manufacture
results in either direction — toward novelty or toward the safety of recovery — and the only durable defense is a
record showing both failure modes being caught. Every entry below was detected by the audit gates of §2.4/§3 (or by
line-by-line review against them) and rejected. Some replacements were themselves overturned by the post-publication
campaign; this appendix preserves that chronology rather than calling every intermediate replacement certified.

## Tautologies (the target equal to its evidence)

| rejected construction | the defect | the tell | the accepted replacement |
| --- | --- | --- | --- |
| area–entropy “law” v1 (QM–GR) | *area* defined as boundary cell-count and $S$ as cells $\times \ln 2$ — equality by construction | validator would have passed; caught by reading the build: no can-fail case possible | saturable bound $S(A)\le\mathrm{mincut}$ with required strict-gap controls (§5.4) |
| area–entropy “law” v2 | bulk dimensions set equal to state dimensions, forcing the match | same | same |
| Born–area “one ledger” v1 | $S_{F39}$ computed from the Schmidt spectrum, $H_{F23}$ from eigenvalues of $\rho_A$ — *the same spectrum twice* (von Neumann $=$ Shannon of squared singular values) | machine-$\epsilon$ “coincidence” ($8.9\times10^{-16}$) — an identity, true for any pure state, zero co-sourcing content | geometric min-cut as the $F39$ side: seed-invariant ($\log 3$) while $S_{\mathrm{Born}}$ varies; strict saturation gaps; validator now **fails on** machine-equality (§5.4) |
| first-law “consequence” (δS relabeling) | $\delta S = \delta\langle H_{\mathrm{mod}}\rangle$ restated on a density matrix disconnected from the carrier — no new checkable content | correct but empty: nothing could have failed | the entropy-cone/MMI consequence with the GHZ violator (§5.4) |

## Circularity and hardcoding (the load-bearing clause doing no work)

| rejected construction | the defect | the tell | the accepted replacement |
| --- | --- | --- | --- |
| monogamy forcing v1 (F51) | “forced$\,=\,$compatible $\wedge\, I_3\le0$” with the compatibility flag **constantly true**; broken-compatibility control written as **literal** booleans | the forcing reduced to the known fact “holographic states obey MMI”; the control never computed | historical computed compatibility control; the later composition probe still refutes a universal shared Born–area law (§5.4) |
| clean-separation “grounding” v1 (SM) | the internal grounding assumed clean separation | anti-circularity gate: a hypothesis not independently satisfiable by a violating structure | historical record-stability repair; later scalar-dressed token census refutes the forcing (§4.5) |
| SM “candidate-law generation” (early) | a `total_slots\ =\ 5` prior and an exterior/GUT-shaped predicate smuggled the answer | caught by adversarial review + internal re-audit; demoted | the post-publication conjugation-consistent carrier and branch-complete selection (§4.2–4.3) |
| assorted (SM) | a shape-flavored `factor_local_breaking` predicate; a minimality “currency” rescue; an $SU(2)$-cubic-anomaly bug | each detected in review; each would have faked a landing | reconstructed carrier; the published $11{,}990$ denominator and exclusions do not survive (§4.2) |

## Rigging toward a desired verdict --- both directions (the P1 sequence)

The entanglement-kernel claim (§6.1) passed through four historical constructions; the fourth was accepted before exact
quotient review and is now superseded.

1. **Rigged toward the positive.** A bespoke hand-built graph (edge roles literally named `active_bottleneck`,
   `hidden_half`) with three parallel channels — the “invisible mode” engineered into the carrier; and the “bulk
   invariant” that moved was a single edge's weight relabeled as a distance. *Defect class: manufactured witness.*
1. **Rigged toward the deflationary.** On the honest carrier, the genuine-mode dimension was **hardcoded to zero**
   (a dead conditional over an empty basis), and the scoring filter (“only multi-edge geodesics count; volume is
   slack”) was chosen so the computed kernel could not count. *Defect class: verdict-by-filter; hardcoded score.*
1. **Inflated by a degeneracy artifact.** At the uniform-weight base point (all 14 edges equal, all cuts tied), a
   one-sided forward-difference Jacobian reported nullity 6 — but every “kernel” direction changed the fingerprint at
   first order (residuals scaling linearly with step: $2.3\times10^{-1}, 2.3\times10^{-3}, 2.3\times10^{-5}$ at
   $\epsilon = 10^{-1,-3,-5}$), and single edges were invisible in one direction only (cut slack). *Defect class:
   linearization artifact at a non-generic point.*
1. **Historically accepted, then overturned.** Generic tie-broken geometries; two-sided central differences;
   both-direction finite-range invisibility and a tree control produced nullity $5/5/5$. Exact series/parallel quotienting
   later showed all five directions were parameterization gauge. The maintained five-class search leaves 13 explicitly
   unclassified residual carriers, not a physical prediction.

## What the trail shows

Three observations. (i) The gates caught failures in both directions, but not always before publication. (ii)
Validator-pass is necessary, never sufficient: semantic defects survived green historical validators. (iii) Version 2
therefore has no “surviving three predictions.” It reports repaired finite constructions and open programs, with the
specific failed definitions and controls retained as regressions.
