# Method: finite audited carriers, adversarial self-correction

The paper combines exact finite computations with bounded numerical fixed-point and tensor-network probes. The protocol
aims to expose circularity and representation dependence; it does not turn a finite carrier into evidence about nature.
Appendix C records both successful self-demotions and defects found only after publication.

## Finite frozen carriers

Each construction declares a finite carrier (the repaired $1{,}066$-labelled gauge carrier in Section 4;
finite tensor-network/graph geometries and mode-grammars in Section 5), and all quantities — obstruction sets,
factorization defects, entropies, min-cuts, kernels — are computed deterministically on it. Carriers and predicates,
once built, are intended to be frozen under SHA-256 pins. Appendix B lists exceptions: one historical tautological pin,
validators that regenerate in place, and summary-reading validators that do not rebuild load-bearing computations.

Each construction has a validator, but their strength is heterogeneous. The repaired artifacts generally rebuild in
memory and byte-compare outputs; several historical validators only check stored summaries. Validator pass is necessary,
never sufficient. The 27-round campaign therefore inspected semantics, regenerated carriers, and added can-fail and
mutation controls rather than treating the historical validator sweep as certification.

## Can-fail controls

A claim with no way to come out false is not a result. The principal surviving positive computations listed below have explicit can-fail controls.

- the SM selection's “collapse” verdict is paired with a broad-measure landscape control that must *not* collapse
   (and an order-battery of 204 refinement orders, 0 flips);
- the QM–GR directed no-go is paired with a *nested* readout for which the reduction must (and does) succeed;
- the holographic monogamy results are paired with a GHZ state that must (and does) violate them;
- the historical three-round P1 graph probe is paired with exact active-cut quotient regressions; Version 3 recertifies
   nineteen exact fibers and exhausts their five-class move queues modulo terminal-label-fixed exact weighted isomorphism,
   while transformations outside those classes remain open;
- the record-stability ablation requires a scalar-dressed regression operator and excludes the spurious spectator-Cartan
   token; the broader census then produces counterexamples to the former implication.

## Adversarial self-correction --- in both directions

Over the course of the program the audit gates rejected our own constructions repeatedly. Three classes of defect were
caught and killed (full post-mortems in Appendix C):

1. **Tautologies** — a “coincidence” that is an identity. *Example:* an early area–entropy “match” computed the von
   Neumann entropy from the Schmidt spectrum on one side and the Shannon entropy of the squared singular values on the
   other — the same number twice, machine-$\epsilon$ residual. Rejected; the accepted version (§5.4) uses the
   *geometric* min-cut, which is provably independent of the state spectrum (it is invariant under reseeding the state
   while the entropy moves).
1. **Circularities / hardcoding.** Rejected; the surviving §5.4 evidence computes MMI on contracted states and applies the same entropy pipeline to a GHZ can-fail control. It supports only a shared inequality class, not a forcing or shared Born–area ledger.
1. **Rigging toward a desired verdict — in either direction.** The decisive case is the former Prediction 1 (§6.1),
   which took several attempts: one rigged *toward* the positive verdict (a bespoke graph with the invisible mode built in by hand);
   one rigged *toward* the deflationary verdict (a hardcoded “genuine dimension $=0$” plus a scoring filter chosen to
   dismiss the answer); one inflated by a **degeneracy artifact** (a one-sided finite-difference Jacobian taken at a
   maximally tied uniform-weight point, where the apparent kernel is first-order visible — residuals scaling linearly
   with step size betrayed it). All three were rejected. A later exact quotient analysis also showed that every published
   null direction was local-reduction gauge. The later exact program starts from the thirteen historical residual carriers,
   constructs nineteen fibers, and completely exhausts their move queues under five declared classes modulo
   terminal-label-fixed exact weighted isomorphism. It leaves transformations outside those classes open.

We call the intended discipline **symmetric scrutiny**. The post-publication record shows why the aspiration must be
distinguished from success: the three prediction forcings did not survive the completed campaign. Appendix C retains the
failed attempts rather than rewriting them as if the corrections had been present from the start.

## Adversarial review and the anti-contamination guard

The earlier external sequence did not settle the results: it ended v7 approve-with-changes, v8 still-needs-work, and v9
unanswered. The present campaign comprises 27 adversarial rounds and 20 repairs/probes, culminating in the certified
claims map used by Version 2. It is an extensive internal/adversarial audit record, not peer review or independent
replication.

Finally, because a cross-track comparison is meaningful only if the constructions are not copied wholesale, the program ran
under an explicit **anti-contamination guard**: the two substrates were declared structurally different at the outset
(a selection/measure layer vs a co-sourcing common refinement), every SM-track step was validated against importing
co-sourcing structure (build validators fail on field-carrier tokens), and steps that pattern-matched one substrate
onto the other were rejected. Whatever machinery the two tracks share, they share because the *laws* are layer-agnostic
— not because the constructions were allowed to copy each other. This guard is procedural self-report, not independent
blinding, and it does not establish universality.

![**Audit pipeline (protocol).** *One-panel schematic: declare carrier $\to$ freeze (SHA-256) $\to$ construct $\to$ validator recomputes $\to$ can-fail control $\to$ independent re-derivation $\to$ (for reviewed construction results) adversarial review. Side channel: the rejection loop, with the three defect classes of §3.3 feeding back.*](figures/fig_f0_audit_pipeline.png)
