# Breadth: one calculus, three more deep problems

This section records additional finite uses of the same vocabulary. They are not evidence that universality has been
demonstrated, and their grades differ. Bell and information-loss rows are finite recoveries; F50 is replaced by adaptive
fixed-point numerics; the measurement row is only a conditional lemma plus a stipulated two-exemplar taxonomy.

## Bell nonlocality: the common carrier is not a hidden variable

The common-carrier premise of §5.3 invites an immediate objection: a single carrier $\psi$ underlying both readouts
*sounds like* a local hidden variable — and local hidden variables are experimentally dead. The calculus's F49 normal
form turns the objection into a computation. For a Bell pair with standard CHSH settings [@Bell1964; @CHSH1969] ($a_0 = Z$, $a_1 = X$,
$b_{0,1} = (Z \pm X)/\sqrt2$), the correlation table is computed from the state, giving

$$
\mathrm{CHSH}_{\mathrm{quantum}} = 2\sqrt2 \approx 2.8284 ,
$$

while the local bound is **enumerated** — all $16$ deterministic local strategies, $\max = 2$ exactly. The F49
common-source test (does any setting-independent source quotient factor both readouts?) therefore fails — the
correlation is a *statused nonlocal residual*, Bell's theorem recovered as a normal form. The can-fail control
discriminates: a classical mixture ($\mathrm{CHSH} = \sqrt2$) **is** locally explainable, with an explicit 16-row
hidden-variable table reproducing its correlations to $1.8\times10^{-15}$.

The calculus-specific content is the reconciliation: F49's “common source” must be an *admissible access quotient*, and F37
(complementarity as non-joint-access) forecloses exactly that for the non-commuting settings — the computed setting
commutators ($0.707$) coincide with the carrier's complementary-pair control. The carrier lives **above** the access
structure; it is not, and cannot be, a local hidden variable. **Forbidden rule:** *any reading of a common-carrier
framework in which the carrier functions as a local hidden variable is excluded* — the premise survives Bell precisely
because the joint quotient it would require does not exist.

## Black-hole information: loss is a property of the readout, not the carrier

The F34 information-loss normal form asks of any transport $\tau: H_0 \to H_1$ with recovery readout $\rho$ and source
information $\sigma$: is the obstruction set

$$
\mathcal O_\rho \;=\; \{(h,h') : \rho(\tau h) = \rho(\tau h') \ \wedge\ \sigma(h) \neq \sigma(h')\}
$$

empty (recoverable) or not (loss)? Instantiated on the holographic carrier with $\tau$ the bulk$\to$boundary
contraction, the verdict is exact and two-sided. The preimage classes of the full boundary state are **precisely the
internal gauge orbits**: $\operatorname{rank} = 27$ = internal dimension (computed), and for any two preimages an
explicit gauge transformation $G$ connecting them is solved for and verified (residual $3\times10^{-15}$). Hence at the
**full boundary**, the only lost interior data is gauge — every gauge-invariant (physical) interior observable is
recoverable: loss is *F34-legitimate*. At a **partial readout** (the reduced state on half the boundary — the
“early radiation only” analog), loss is real: an exact witness applies a unitary on the unobserved half, leaving the
observed reduced state identical ($5\times10^{-16}$) while gauge-invariant physical observables shift ($\approx 10^{-2}$). **Forbidden rule:** *the holographic carrier forbids physical-information loss at the full-boundary
recovery; loss is forced at partial/coarse readouts* — in this toy, the information paradox [@Hawking1976] is a property of the
readout, not of the carrier. (No dynamics, no evaporation, no Page curve [@Page1993] is claimed.)

## The cosmological constant: no in-layer value-law

The F50 carrier contains a cosmological-background analog [@Weinberg1989], the matter-independent term in
$V[\psi]=V_0+\kappa T_{00}[\psi]$. The published $15/18$ split and boundary $\kappa\le10$ versus
$\kappa\ge15$ were artifacts of a 60-iteration, mix-$0.5$ solver budget. Adaptive iteration across damping values
$0.2,0.35,0.5,0.7$ and at least three initial states finds a fixed point for every sampled background and $\kappa$:
there is no fixed-point-existence boundary on the declared sample. Jacobians of the raw fixed-point map provide a
different, non-unique discriminator: spectral stability crosses near background offset $3.6535$ and $\kappa=5.8675$.
Whether that raw-map stability criterion defines physical admissibility is a modeling choice. The sample therefore
supports only: *no unique $\Lambda$ law is selected in-layer, and all sampled backgrounds admit fixed points*.
Artifacts are in `review_2026/repairs/q7_f50_convergence/`.

## The measurement problem: a structural discriminator

(From the SM-track extension.) The certified content is a $§igma_f$-conditional definability lemma on the declared
carrier and a two-exemplar taxonomy stipulated as “ledger-changing” versus “readout-changing.” It is not an
extension-of-quantum-mechanics theorem and is not an operational falsifier for future measurement theories. A broader
generated theory class and physical correspondence would be needed before that language is warranted.

## The pattern

| puzzle | law | verdict | control |
| --- | --- | --- | --- |
| Bell nonlocality | F49 + F37 | nonlocal residual recovered; carrier $\neq$ hidden variable (forbidden rule) | classical mixture: locally explainable, LHV table exhibited |
| BH information | F34 | loss gauge-only at full boundary; real at partial readouts | exact complement-unitary witness |
| cosmological constant | F50 (+F47/F26) | fixed points on all sampled backgrounds; no unique in-layer value-law | raw-map stability crossing, if adopted as criterion |
| measurement | non-factorization | $§igma_f$-conditional lemma; stipulated two-exemplar taxonomy | identical-diagonal witness pair |

These rows are bounded diagnostics on their declared carriers. They do not add three established predictions or a
universality result to the paper.
