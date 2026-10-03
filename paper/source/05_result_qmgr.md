# Result II: QM and GR readouts and finite graph duality

This section asks how a quantum description and a gravitational description of one system can relate, using the
quotient vocabulary of Section 2. Three findings emerge. A
much-discussed explanation, that “quantizing” and “curving” are two routes that fail to commute, has no support at
this level: the natural finite versions commute exactly. Instead, the two readouts are *siblings*: neither is a
coarse-graining of the other, but a common refinement carries both. Finally, on finite graphs, the familiar relation
between minimal cuts and entanglement appears as an exact linear-programming duality. Figure 5 illustrates
the second and third findings.

## Route mismatch: the two completions commute

For two idempotent maps $E_1,E_2$ on a finite carrier, the set
$$
\Delta_3^{\mathrm{comp}}(E_1,E_2)=\{c:E_1E_2(c)\ne E_2E_1(c)\}
$$
measures their failure to commute, and non-commuting examples exist
(Appendix A.3). The natural QM–GR instance, however, returns a null verdict.
On the $16$-state Boolean carrier introduced below, the “quantize” and “curve” completions are coordinate
conditional expectations: $16\times16$ averaging projections acting on functions (or distributions) over the
uniformly weighted cube, not maps of its sixteen points. Both are idempotent, and they **commute exactly**:
$E_{\rm QM}E_{\rm GR}=E_{\rm GR}E_{\rm QM}$, so no basis state is sent to different distributions by the two orders
of composition, and the defect set is empty. The reason is that the overlap of the two
coordinate sets factorizes on the Boolean cube. A naive normalized distance between the two encoded tables
($0.5$, or $1/\sqrt2$ after recoding $0/1$ as $\pm1$) depends on the encoding and is not a commutator.

Non-commuting idempotent pairs can be built from non-factorizing partitions or constrained projections, and they serve
as mathematical controls, but none of them arises from the frozen quantize and curve routes. At this level there is
therefore no route-mismatch explanation of why quantizing gravity is hard. The exact matrices and recoding controls are
in `review_2026/repairs/q2_route_mismatch/`.

## A fork, not a ladder

Consider an abstract carrier of four binary coordinates and three readouts:
$$
q_{\rm QM}=(d_0,d_1,d_2),\qquad q_{\rm GR}=(d_0,d_2,d_3),\qquad L=(d_0,d_1,d_2,d_3).
$$
If gravity were a coarse-graining of quantum mechanics (a “ladder”), $q_{\rm GR}$ would be a function of
$q_{\rm QM}$. It is not: in each direction there are eight unordered witness pairs (sixteen ordered pairs in
$\Delta_{\mathrm{fact}}$), pairs of states that one readout identifies and the other separates. A nested control, in which one readout's coordinates contain the other's,
factors as it should, and both readouts factor through $L$ by construction. Exhausting all $16$ coordinate-subset
partitions gives $55$ incomparable pairs among the $120$ unordered pairs of distinct partitions. This is an exact
toy theorem, conditional on the abstract carrier and on reading its coordinates as access. It is consistent with the
commutation result of Section 5.1: commuting completions and
incomparable readouts are different properties.

**Where the coordinates come from.** Bare coordinate labels say nothing about fields, so a separate finite
construction supplies them. On $54$ constructed records, each a field $\psi$ together with a background potential
$V_0$, coarse field functionals and explicit phase-only and potential-only controls realize mutually non-factorizing
QM and GR readouts. The conditions are material. The witness for the forward direction changes $V_0$; the QM readout
includes the probability current as well as the Born density; $d_0$ is constant; and although the coordinate alphabets
have sizes $1,2,8,3$, the $54$ records occupy only $15$ joint coordinate values. These $54$ records and the abstract carrier are
distinct objects. Nine hand-instantiated alternative architectures were tested; two reconcile the readouts, but both
are partition-equivalent to $L$. This is **conditional finite provenance**: it shows that the fork can be
realized under explicit choices, not that the family, type, or instance is unique
(`review_2026/repairs/q1_access_provenance/`).

A related statement, labelled $T_{\mathrm{QG\text{-}NoGo}}$ in the repository, tests two special “fused” or
“stapled” routes. It does not quantify over general fused objects, coherent mediators, or operator algebras, and it
cannot support any statement that quantum gravity is impossible within the grammar.

> **Figure (drawn in TikZ; see the PDF).** **The QM–GR constructions.** (a) On the abstract Boolean carrier, the QM and GR readouts are
incomparable, yet both factor through the common refinement $L$. (b) A schematic boundary-anchored network: the
minimum cut separating region $A$ from the rest has value equal to the dual optimum, and the cut-incidence variables
$y_e$ are the per-edge shadow prices. (c) Entropies of independently contracted random tensor states, as a fraction of
the min cut, at bond dimensions $D=2,3,4$: means over five seeds on the sampled carrier.

## The common carrier is a hypothesis

Nothing above shows that nature has a common carrier for the two readouts. Semiclassical co-sourcing, in which one
field $\psi$ supplies both a Born-type readout and the stress-energy that sources a potential, is a plausible
physical motivation. But the available controls test different predicates, and the argument linking them is prose
rather than a computation. The premise is therefore carried as a declared hypothesis, not as a grounded result. The
$54$-record construction shows that a finite realization can be built under explicit choices; it does not show that
nature, the free gravitational sector, or a deep quantum-gravity regime shares such a carrier.

## Minimal cuts as an exact linear program

In holography, the Ryu–Takayanagi formula relates the entanglement entropy of a boundary region to the area of a
minimal surface [@RyuTakayanagi2006; @Maldacena1998]. Its simplest discrete analogue replaces the surface by a
minimum cut in a weighted graph, and the max-flow/min-cut theorem [@FordFulkerson1956] makes the cut value the
optimum of a linear program. This section realizes that analogue exactly.

At nondegenerate seeded capacities, every tested boundary region has a unique minimum cut, with an exported margin to
the next-best cut. The max-flow primal and the cut dual are exported as matrices, and exact certificates verify strong
duality and complementary slackness. Writing $y_e$ for the dual variable attached to the capacity $c_e$ of edge
$e$,
$$
\operatorname{Area}(\operatorname{mincut}A)
=\operatorname{OPT}_{\rm dual}(A)
=\sum_e c_e y_e .
$$
The per-edge *shadow prices* are the $y_e$, not the optimum itself. Within a chamber of capacities where the
minimum cut is unique, the $y_e$ are the $0/1$ indicators of the cut edges and equal the sensitivities
$\partial F^*/\partial c_e$, which are verified by two-sided perturbations.

**Entropies of contracted states.** Random tensors placed on the same graphs and contracted independently give
boundary states whose entropies obey $S(A)\le\operatorname{mincut}(A)$ on the sampled carrier. The mean
ratios $S/\operatorname{mincut}=0.729,\,0.904,\,0.941$ over five seeds at bond dimensions $D=2,3,4$ are a sampled finite trend toward
saturation. They do not show convergence or equality, and every sampled entropy stays below its cut. The min-cut entropy
vectors satisfy monogamy of mutual information [@HaydenHeadrickMaloney2013], and a fairly compared GHZ
state [@GHZ1989] violates it. Together these support a **finite-graph recognition** of RT-type structure,
conditional on the graph and tensor-network model. They do not derive holography, the coefficient $1/4G$, or a
continuum law.

**Two extensions that fail.** Both failures are informative. First, there is no linearized-Einstein match. A
pass can be manufactured at a degenerate base point, but at an honest nondegenerate point an independently specified
geometric deformation does not reproduce the contracted-state $\delta S$ under the declared pairing; uniqueness
margins and a can-fail deformation are exported. Second, the Born and area ledgers do not obey one composition law.
Area follows min-plus composition on all four tested gluing probes, while the Born ledger fails all four. What the two
sampled ledgers share is only the monogamy inequality class, with different dependencies
(`review_2026/repairs/q5_lp_duality/`).

## Summary

| question | status | scope |
| --- | --- | --- |
| route mismatch | exact null result | the completions commute; $0.5$ is an encoding-dependent table distance |
| fork, not ladder | exact toy theorem | coordinate-partition non-factorization on the declared Boolean carrier |
| field provenance | conditional finite construction | $54$ records with named coarse functionals and stated limitations |
| common carrier | hypothesis | semiclassical co-sourcing is a motivation, not a result |
| $T_{\mathrm{QG\text{-}NoGo}}$ | narrow | two special fused or stapled routes only |
| min-cut/LP identity | finite-graph recognition | exact dual certificates and sensitivities on nondegenerate finite graphs |
| contracted-state entropies | sampled | bound holds on the sample; saturation trend only |
| linearized Einstein | negative result | no match under the declared deformation pairing |
| one Born–area ledger | negative result | area passes four min-plus gluings; Born fails all four |
