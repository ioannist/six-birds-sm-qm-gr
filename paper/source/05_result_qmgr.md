# Result II --- conditional QM--GR access structures and graph duality

## Route-mismatch correction

For idempotent endomorphisms $E_1,E_2$, the finite defect
$$
\Delta_3^{\mathrm{comp}}(E_1,E_2)=\{c:E_1E_2(c)\ne E_2E_1(c)\}
$$
is a legitimate mathematical measure of non-commutation. Non-commuting examples exist. They are not, however, what the
published QM–GR computation constructed. On its 16-state Boolean carrier, the two conditional-mean completions are
idempotent and **commute exactly**: $E_{\rm QM}E_{\rm GR}=E_{\rm GR}E_{\rm QM}$, so the defect set is empty. The
reported $0.5$ is the normalized distance between two encoded tables; under $0/1\to\pm1$ recoding it becomes
$1/\sqrt2$. It is not a conjugacy-invariant commutator magnitude.

Coordinate conditional means commute here because the Boolean-cube overlap factorizes. The repair constructs
non-commuting idempotent pairs from non-factorizing partitions and constrained projections as mathematical controls,
but none is derived from the frozen “quantize” and “curve” routes. The paper's claim that those routes explain why
quantizing gravity fails is therefore retracted. Exact matrices and recoding controls are in
`review_2026/repairs/q2_route_mismatch/`.

## Fork-over-ladder, with finite provenance

The separate access-factorization result survives narrowly. On the abstract four-coordinate carrier
$$
q_{\rm QM}=(d_0,d_1,d_2),\qquad q_{\rm GR}=(d_0,d_2,d_3),\qquad L=(d_0,d_1,d_2,d_3),
$$
$q_{\rm GR}$ is not a deterministic quotient of $q_{\rm QM}$: the two directed defects each have eight witnesses.
The nested coordinate control factors, while both readouts factor through $L$ by definition. Exhausting all 16
coordinate-subset partitions gives 55 incomparable pairs among the 120 unordered distinct pairs. This is an exact toy
theorem conditional on the abstract carrier and its access interpretation; it is not evidence that the published
conditional-mean completions fail to commute.

Post-publication work supplies a finite provenance construction rather than the previously declared mode labels. On 54
constructed $(\psi,V_0)$ records, coarse field functionals and explicit phase-only and potential controls realize
mutually non-factorizing QM and GR readouts. Its conditions are material: the forward witness changes $V_0$, the QM
audit includes density and current rather than Born density alone, $d_0$ is constant, and the realized coordinate
image is $1\times2\times8\times3$, not the published $2^4$ carrier. Nine hand-instantiated F24 representatives were
tested; two reconcile but are partition-equivalent to $L$. Thus this is **conditional finite provenance**, not
family, type, or instance uniqueness. See `review_2026/repairs/q1_access_provenance/`.

The theorem named $T_{\mathrm{QG\text{-}NoGo}}$ is also narrower than its original prose: it tests two special fused or
stapled routes and does not quantify over general fused objects, coherent mediators, or operator algebras. It cannot
support the statement that quantum gravity is “illegal” in the grammar.

![**Finite fork and graph-duality constructions.** Left: the declared abstract access fork, for which the
directed quotient fails and the common refinement closes. Right: a boundary-anchored flow network; in Version 2 the
corrected identity distinguishes the dual optimum from its per-edge shadow prices.](figures/fig_f3_fork_rt.png)

## The common carrier is a hypothesis

The common-carrier premise is not computationally grounded by the published tests. Semiclassical co-sourcing—one field
$\psi$ supplying a Born-type readout and stress-energy for a potential—remains a plausible named recognition source,
but the existing controls test different predicates and the “door test” is prose. The GROUND landing is therefore
withdrawn and replaced by a declared hypothesis. The 54-record construction above shows that a finite realization can
be built under explicit choices; it does not establish that nature, the free gravitational sector, or a deep
quantum-gravity regime shares such a carrier.

## Finite-graph min-cut/LP-duality recognition

The graph-level core survives after correcting the flagship equation. At nondegenerate seeded capacities, every tested
boundary region has a unique minimum cut with an exported margin. The max-flow primal and cut dual are exported as
matrices, and exact certificates verify strong duality and complementary slackness. If $y_e$ denotes the dual
variable associated with edge capacity $c_e$, then the correct identity is
$$
\operatorname{Area}(\operatorname{mincut}A)
=\operatorname{OPT}_{\rm dual}(A)
=\sum_e c_e y_e,
$$
where the $y_e$—not the dual optimum—are per-edge shadow prices. In the unique-cut chamber they are the $0/1$
cut-incidence variables and satisfy $y_e=\partial F^*/\partial c_e$, verified by two-sided perturbations.

Independently contracted random-tensor states obey $S(A)\le\operatorname{mincut}(A)$ on the sampled carrier. The ratios
$S/\operatorname{mincut}=0.729,0.904,0.941$ for bond dimensions $D=2,3,4$ are a *finite sampled saturation
trend*, not convergence or equality; sampled contracted-state entropies remain below the cuts. The min-cut entropy
vectors satisfy monogamy, and a fairly compared GHZ control violates it. These results support a
**finite-graph recognition** of RT-related structure, conditional on the graph/tensor-network model; they do not
derive holography [@RyuTakayanagi2006; @Maldacena1998], $1/4G$, or a continuum law.

Two published extensions are withdrawn. First, the linearized-Einstein pass was true by construction at a degenerate
point. At the honest nondegenerate base point, an independently specified geometry deformation does not match the
contracted-state $\delta S$ under the declared pairing; uniqueness margins and a can-fail deformation are exported.
Second, Born and area do not carry one universal composition law: area follows min-plus composition on all four tested
gluing probes, while Born fails all four. The surviving cross-ledger statement is only that the two sampled ledgers
obey the same monogamy inequality class, with different dependencies. See
`review_2026/repairs/q5_lp_duality/`.

## Certified summary

| question | status | certified scope |
| --- | --- | --- |
| published route mismatch | retracted | completions commute; $0.5$ is encoding-dependent table distance |
| fork-over-ladder | keep narrowly | exact coordinate-partition non-factorization on the declared Boolean carrier |
| field provenance | conditional finite construction | 54 records with named coarse functionals and stated limitations |
| common-carrier GROUND | retracted/hypothesis | semiclassical co-sourcing is a named physical motivation, not a landing |
| $T_{\mathrm{QG\text{-}NoGo}}$ | narrowed | two special fused/stapled routes only |
| RT/LP relation | corrected recognition | exact dual certificate and sensitivities on finite nondegenerate graph cuts |
| linearized Einstein | retracted | honest tested response does not match under the declared deformation pairing |
| one Born–area ledger | retracted | area passes four min-plus gluings; Born fails all four |
