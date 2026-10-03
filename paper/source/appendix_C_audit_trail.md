# Audit trail: what was rejected, and why

We publish the program's rejected constructions on purpose. A framework as expressive as this one can manufacture
results in either direction, toward novelty or toward the safety of mere recovery, and the only durable defense is a
record showing both failure modes being caught. Every entry below was detected by the checks of
Section 2.4 and Section 3,
or by line-by-line review against them, and rejected. Some replacements were themselves overturned later; this appendix
keeps that chronology instead of presenting every intermediate replacement as final.

## Tautologies: the target equal to its evidence

| rejected construction | defect | how it was caught | replacement |
| --- | --- | --- | --- |
| area–entropy “law”, first form | area defined as a boundary cell count and $S$ as cells $\times\ln2$: equal by construction | reading the build: no can-fail case was possible | the saturable bound $S(A)\le\mathrm{mincut}$ with strict-gap controls |
| area–entropy “law”, second form | bulk dimensions set equal to state dimensions, forcing the match | same | same |
| Born–area “one ledger” | the F39 entropy from the Schmidt spectrum and the F23 entropy from the eigenvalues of $\rho_A$: the same spectrum twice | agreement to $8.9\times10^{-16}$, an identity true for every pure state | the geometric min-cut as the F39 side: fixed under reseeding ($\log3$) while $S$ varies; the validator now fails on machine-precision equality |
| first-law “consequence” | $\delta S=\delta\langle H_{\rm mod}\rangle$ restated on a density matrix disconnected from the carrier | correct but empty: nothing could have failed | the entropy-cone and monogamy consequence with the GHZ violator |

## Circularity and hardcoding: a load-bearing clause doing no work

| rejected construction | defect | how it was caught | replacement |
| --- | --- | --- | --- |
| monogamy “forcing” (F51) | “forced = compatible and $I_3\le0$” with the compatibility flag constantly true, and the broken-compatibility control written as literal booleans | the forcing reduced to the known fact that holographic states obey monogamy; the control was never computed | a computed compatibility control; a later composition probe refutes a universal shared Born–area law |
| clean-separation “grounding” (SM) | the internal grounding assumed clean separation | anti-circularity: a hypothesis not satisfiable by a violating structure | a record-stability construction, later shown token-definition-sensitive by the complete candidate census |
| SM “candidate-law generation” | a `total_slots = 5` prior and an exterior, GUT-shaped predicate smuggled the answer | adversarial review and internal re-audit | the conjugation-consistent carrier and branch-complete selection |
| assorted (SM) | a shape-flavored `factor_local_breaking` predicate; a minimality “currency” rescue; an $SU(2)$ cubic-anomaly bug | each detected in review; each would have faked a result | the reconstructed carrier; the alias-inflated $11{,}990$-row denominator and its exclusions are discarded |

## Rigging toward a verdict, in both directions: the P1 sequence

The entanglement-kernel question (Section 6.1) passed through four
constructions before the exact program; the fourth was accepted for a time and then overturned by exact quotienting.

1. **Rigged toward the positive.** A bespoke graph, with edge roles literally named
   `active_bottleneck` and `hidden_half`, had three parallel channels: the “invisible mode” was
   engineered into the carrier, and the “bulk invariant” that moved was a single edge weight relabeled as a distance.
   *Defect: manufactured witness.*
1. **Rigged toward the negative.** On the honest carrier, the dimension of genuine modes was hardcoded to zero
   (a dead conditional over an empty basis), and a scoring filter (“only multi-edge geodesics count; volume is slack”)
   was chosen so that the computed kernel could not count. *Defect: verdict by filter.*
1. **Inflated by degeneracy.** At the uniform-weight point (all $14$ edges equal, all cuts tied), a one-sided
   forward-difference Jacobian reported nullity $6$. Every “kernel” direction changed the fingerprint at first
   order, with residuals $2.3\times10^{-1},2.3\times10^{-3},2.3\times10^{-5}$ at steps $10^{-1},10^{-3},10^{-5}$, and
   single edges were invisible in one direction only (cut slack). *Defect: linearization artifact at a non-generic
   point.*
1. **Accepted, then overturned.** Generic tie-broken geometries, two-sided central differences, both-direction
   finite-range invisibility, and a tree control gave nullity $5/5/5$. Exact series–parallel quotienting then showed
   that all five directions were reparametrizations. The exact five-class search leaves $13$ explicitly unclassified
   residual carriers, which are the starting point of the program, not a physical prediction.

## Review record

The review history has three parts. None of them is journal peer review or independent replication.

**An earlier external gate.** A missing-layer gate run with an external reviewer recorded “approve with
changes” (round v7), then “still needs work” (v8), and then no answer (v9). No final approval was issued. The
missing-layer atlas therefore cannot serve as independent preregistration or blinding evidence; its cards are a
historical research record and do not override the claims registry.

**The 2026 verification campaign.** Twenty-seven adversarial review rounds and twenty repair or probe
constructions, completed on 2026-08-26, inspected every load-bearing claim and required repairs to construct missing
objects rather than relabel outcomes. One agent reproduced each review finding, a separate read-only reviewer assessed
the repairs, and implementation was commit-gated. A further model-based adversarial round, with its own reruns and audit
scripts, examined the construction programs; its two central findings were reproduced and accepted. First, forward
reachability had been mistyped as symmetric-orbit closure; the result is now stated as forward-reachability disjointness
only. Second, the review constructed the diagonal intertwiner that makes the six state-level pairs gauge-equivalent,
which led to the general gauge-collapse lemma. The campaign produced strengthened results (the conjugation-consistent
branch carrier, exact $SU(5)$ generator action, the unique content orbit, genuine generic mass ranks, field
provenance, and explicit min-cut duality) as well as decisive negative findings (the commuting routes, the
reparametrization kernel, the token-sensitive record implication, the failed linear response, the unshared Born/area
composition, and the solver-artifact F50 boundary). Its dispositions (keep, restate, retract, open program) are
recorded in `review_2026/CLAIMS_MAP.md` and `review_2026/CLAIMS_REGISTRY.md`.

**The mathematics review.** A subsequent review, recorded in
`review_2026/mathematics_audit_20261003/`, re-examined all $42$ registry records for quantifiers,
hypotheses, and the strength of their support, and repaired what it found: it supplied the general proof of
Theorem 7.1 with exact rank certificates and an exact partial-readout witness, extended the gauge-collapse
certificate to all connected carriers, strengthened several validators, and narrowed the record census to candidate
channels. It is a self-review with a separate adversarial pass.

## What the trail shows

Three things. First, the checks caught failures in both directions, though not always immediately. Second, a passing
validator is necessary but never sufficient: semantic defects survived green validators. Third, the paper accordingly
claims no surviving forced predictions. It reports finite constructions and open programs, and it keeps the specific
failed definitions and controls as regression tests.
