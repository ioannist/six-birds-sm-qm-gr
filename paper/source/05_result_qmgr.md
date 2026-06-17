# 5. Result II — quantum mechanics ↔ general relativity as a common refinement (a unification)

## 5.1 Locating the obstruction: the route mismatch

Why do QM and GR not compose? The calculus's answer is structural and exact. Call $E_1$ the completion "quantize" and
$E_2$ the completion "curve". Each is individually consistent — idempotent on the carrier:

$$
E_1^2 = E_1,\qquad E_2^2 = E_2,\qquad\text{but}\qquad E_1 E_2 \neq E_2 E_1 .
$$

A theorem-grade result of the calculus (Foundations III, Thms. 9–10) shows this situation is well-posed and finitely
witnessed: the **route-mismatch defect**

$$
\Delta_3^{\mathrm{comp}}(E_1,E_2) \;=\; \{\,c : E_1E_2(c) \neq E_2E_1(c)\,\}
$$

is non-empty iff the completions fail to commute, *even though each is exact alone* — i.e., route mismatch is a real,
typed, finite defect, not a symptom of sloppiness in either route. The explicit minimal witness is elementary: on
$C=\mathcal P(\{a,b,c\})$ with $E_1(S)=S\cup\{b\}$ iff $a\in S$ and $E_2(S)=S\cup\{c\}$ iff $b\in S$, one has
$E_1E_2(\{a\})=\{a,b\}$ but $E_2E_1(\{a\})=\{a,b,c\}$. On the QM–GR carrier below, the directed route mismatch computes
to $0.5$ (normalized). This is the calculus's typing of *why quantizing gravity fails*: quantize-then-curve and
curve-then-quantize are different objects, and no amount of skill in either route removes the defect of composing them.

## 5.2 The resolution: a fork, not a ladder

The construction models the two theories as **access quotients of one carrier**. The minimal mode-grammar has four
modes $(d_0,d_1,d_2,d_3)$ with

$$
q_{\mathrm{QM}} = (d_0,d_1,d_2), \qquad q_{\mathrm{GR}} = (d_0,d_2,d_3), \qquad L = (d_0,d_1,d_2,d_3),
$$

i.e., the theories share modes $(d_0,d_2)$, while $d_1$ (phase/superposition data) is QM-only and $d_3$ (curvature
readout) is GR-only. Two architectures compete:

- the **ladder** (the emergent-spacetime direction): GR is a lawful quotient of QM, $q_{\mathrm{GR}} = \phi \circ
  q_{\mathrm{QM}}$ for some $\phi$;
- the **fork**: both are quotients of the common refinement $L$.

The computation is decisive on the carrier. The directed ladder **fails**: $\Delta_{\mathrm{fact}}(q_{\mathrm{QM}},
q_{\mathrm{GR}})$ has $8$ witness pairs (row residual $0.577$, route mismatch $0.5$) — and the *strongest* ladder, which
adjoins to QM an RT-shadow functional $A_{\mathrm{RT}} = d_0 + 2d_2$ of its accessible modes, fails identically (defect
$8$): a function of QM-visible modes cannot recover $d_3$. The **fork closes**: $L \to q_{\mathrm{QM}}$ and $L \to
q_{\mathrm{GR}}$ both factor exactly (residuals $0$). The can-fail control flips: replacing GR by a readout genuinely
nested in QM, $q_{\mathrm{GR}}^{\mathrm{nested}} = (d_0,d_2,d_1)$, the ladder defect drops to $0$ — the no-go tracks
real structure, not the test apparatus. Supporting theorems sharpen this into a program-level statement: a directed
reduction *and* a fused "quantum-gravity object" both fail in the grammar ($T_{\mathrm{QG\text{-}NoGo}}$), while $L$ is
the **unique minimal admissible common refinement** ($T_{\mathrm{QGR\text{-}Unique}}$, type- and instance-uniqueness by
adversarial defeat, basis-independent, stable across carriers).

Scope, stated plainly: the ladder no-go covers the **weak-RT** direction (area-type functionals of accessible
entanglement data); *strong* bulk reconstruction — $d_3$ recoverable from richer quantum data — is not refuted here and
is exactly what Section 6.1 turns into a falsifiable test.

> **Fork resolution and RT ledger recognition.** *Left: the failed ladder (QM $\to$ GR arrow struck through, defect 8) vs the closed fork ($L$ above,
> two clean arrows down, residuals 0; nested control shown flipping). Right: panel for §5.4 — a boundary-anchored flow
> network with the minimal cut highlighted; caption "area $=$ shadow price of the entanglement flow (max-flow/min-cut
> $=$ LP duality)."*

## 5.3 Grounding the premise

The fork is conditional on the **common-carrier premise** — that QM and GR may be modeled as access quotients of one
carrier at all. The calculus does not let that premise pass silently. A door-test against the framework's own laws
(F37, F51, FoEC, SAU) shows each supplies the *form* of a shared carrier but none *forces* its existence
(form-not-existence in every case). The premise is therefore landed in **GROUND** mode: supplied as the down-shadow of
a named physical source — **semiclassical co-sourcing**: one field $\psi$ carries both the Born readout
$\rho = |\psi|^2$ and the stress-energy $T[\psi]$ that sources geometry, extended through a computed self-consistent
back-reaction $V[\psi] = V_0 + \kappa\, T_{00}[\psi]$ (fixed-point residual $3.5\times 10^{-16}$ at $\kappa=0.3$; a
runaway control at $\kappa=30$ fails, so the consistency is not automatic). Two can-fail controls give the landing
teeth: a complementary (non-commuting) access pair admits **no** joint quotient (commutator residual $0.707$), so the
laws do not manufacture carriers; and removing co-sourcing removes the warrant (stress residual $0.381$). This grounding
was stress-tested in an adversarial review cycle and **settled** as an honest recognition-source landing (Appendix D). The
named residual is real: the warrant reaches matter-sourced geometry, not the free gravitational sector or the deep
quantum-gravity regime.

## 5.4 Recognition: Ryu–Takayanagi as ledger/shadow-price duality

Within the fork, the calculus *recognizes* the central result of holographic entanglement — non-circularly. The claim
(a **RECOGNITION** landing, adversarially reviewed and settled): the Ryu–Takayanagi relation is a special case of the
calculus's currency–constraint law — *a conserved ledger quantity in one layer reappears as the shadow price of its
constraint in the layer above*. Concretely, on tensor-network carriers the entanglement entropy obeys the saturable
bound

$$
S(A) \;\le\; \mathrm{mincut}(A),
$$

and max-flow/min-cut **is** linear-programming duality: the minimal cut (the "area") is the optimal dual variable — the
shadow price — of the boundary entanglement flow. The construction earns the recognition rather than assuming it:
$S(A)$ is computed from contracted random-tensor states (not defined as a cut), saturation *emerges* with bond
dimension ($S/\mathrm{mincut} = 0.729 \to 0.904 \to 0.941$ for $D=2,3,4$, never exact at finite $D$ — exactness would
be the tautology signature and fails the validator), strict-gap controls exist, and the geometric side is
seed-invariant while the entropic side moves ($\mathrm{area} = \log 3$ constant across states; $S_{\mathrm{Born}} =
1.0970, 1.0956, 1.0980$). Two independently checkable consequences computed on the same carrier: the holographic
entropy cone's monogamy facet,

$$
I_3(A{:}B{:}C) = S_A + S_B + S_C + S_{ABC} - S_{AB} - S_{AC} - S_{BC} \;\le\; 0
$$

for min-cut-realizable states, with the GHZ control violating it ($I_3 = +\log 2$); and a discrete linearized-Einstein
**consistency condition** — demanding RT-consistency of a perturbed geometry across all $38$ regions of a $14$-edge
carrier overdetermines the response (rank $10$, cokernel $28$): a geometric perturbation satisfies it (residual
$9\times10^{-17}$), a generic state perturbation violates it ($0.042$). Two unification-grade refinements complete the
picture: the quantum (Born/F23) and gravitational (area/F39) ledgers carry **one composition law** (the monogamy
combiner — shared on co-sourced carriers, broken by GHZ), and the F51 parent *forces* that combiner on admissible
co-readouts while QM alone does not (a computed geometric-dual compatibility test; the forcing disappears under a
broken-compatibility control).

We emphasize the grade: this **recovers and organizes** known holographic structure under one law — it does not derive
holography, the $1/4G$ coefficient, or the continuum Einstein equation (the discrete condition above is the honest
extent; the continuum limit is an open, precisely-typed upgrade).

## 5.5 Summary table

| question | verdict (grade) | basis |
|---|---|---|
| why QM and GR don't compose | **COMPUTE** — route mismatch $\Delta_3^{\mathrm{comp}}\neq\varnothing$ | non-commuting completions; directed mismatch $0.5$ |
| GR a quotient of QM (emergent spacetime, weak form)? | **COMPUTE** — no (defect $8$; control flips) | ladder vs fork |
| QM, GR siblings under one parent? | **COMPUTE**, conditional — fork closes ($0/0$); parent unique | $T_{\mathrm{QGR\text{-}Unique}}$ |
| the common-carrier premise | **GROUND** — semiclassical co-sourcing (review-settled) | door-test + two controls |
| Ryu–Takayanagi | **RECOGNITION** — ledger/shadow-price duality (review-settled) | LP duality; emergent saturation; MMI; discrete Einstein |
| quantum gravity solved / continuum Einstein derived | **not landed** | named open upgrades |

Section 6.1 pushes the fork to its sharpest consequence — and stakes the falsification.
