# 7. Breadth: one calculus, three more deep problems

The universality thesis (§8) gains most of its force from breadth: the *same* obstruction/defect/moduli machinery that
produced Sections 4–6, applied without modification, classifies three further foundational puzzles. Each result below
is a computed forbidden-rule or demarcation with its own can-fail control. None is new physics — each recovers or
classifies known structure — and that is their role: they show the grammar is one object, not a per-problem retrofit.

## 7.1 Bell nonlocality: the common carrier is not a hidden variable

The common-carrier premise of §5.3 invites an immediate objection: a single carrier $\psi$ underlying both readouts
*sounds like* a local hidden variable — and local hidden variables are experimentally dead. The calculus's F49 normal
form turns the objection into a computation. For a Bell pair with standard CHSH settings ($a_0 = Z$, $a_1 = X$,
$b_{0,1} = (Z \pm X)/\sqrt2$), the correlation table is computed from the state, giving

$$
\mathrm{CHSH}_{\mathrm{quantum}} = 2\sqrt2 \approx 2.8284 ,
$$

while the local bound is **enumerated** — all $16$ deterministic local strategies, $\max = 2$ exactly. The F49
common-source test (does any setting-independent source quotient factor both readouts?) therefore fails — the
correlation is a *statused nonlocal residual*, Bell's theorem recovered as a normal form. The can-fail control
discriminates: a classical mixture ($\mathrm{CHSH} = \sqrt2$) **is** locally explainable, with an explicit 16-row
hidden-variable table reproducing its correlations to $1.8\times10^{-15}$.

The SBT-native content is the reconciliation: F49's "common source" must be an *admissible access quotient*, and F37
(complementarity as non-joint-access) forecloses exactly that for the non-commuting settings — the computed setting
commutators ($0.707$) coincide with the carrier's complementary-pair control. The carrier lives **above** the access
structure; it is not, and cannot be, a local hidden variable. **Forbidden rule:** *any reading of a common-carrier
framework in which the carrier functions as a local hidden variable is excluded* — the premise survives Bell precisely
because the joint quotient it would require does not exist.

## 7.2 Black-hole information: loss is a property of the readout, not the carrier

The F34 information-loss normal form asks of any transport $\tau: H_0 \to H_1$ with recovery readout $\rho$ and source
information $\sigma$: is the obstruction set

$$
\mathcal O_\rho \;=\; \{(h,h') : \rho(\tau h) = \rho(\tau h') \ \wedge\ \sigma(h) \neq \sigma(h')\}
$$

empty (recoverable) or not (loss)? Instantiated on the holographic carrier with $\tau$ the bulk$\to$boundary
contraction, the verdict is exact and two-sided. The preimage classes of the full boundary state are **precisely the
internal gauge orbits**: $\operatorname{rank} = 27 = $ internal dimension (computed), and for any two preimages an
explicit gauge transformation $G$ connecting them is solved for and verified (residual $3\times10^{-15}$). Hence at the
**full boundary**, the only lost interior data is gauge — every gauge-invariant (physical) interior observable is
recoverable: loss is *F34-legitimate*. At a **partial readout** (the reduced state on half the boundary — the
"early radiation only" analog), loss is real: an exact witness applies a unitary on the unobserved half, leaving the
observed reduced state identical ($5\times10^{-16}$) while gauge-invariant physical observables shift ($\approx
10^{-2}$). **Forbidden rule:** *the holographic carrier forbids physical-information loss at the full-boundary
recovery; loss is forced at partial/coarse readouts* — in this toy, the information paradox is a property of the
readout, not of the carrier. (No dynamics, no evaporation, no Page curve is claimed.)

## 7.3 The cosmological constant: no in-layer value-law

The F50 vacuum/background-selection law classifies a background quantity as **necessary** (closure fixes one value),
**moduli** (closure is blind — contingent), or **vacuum-selected** (a singleton selector). The carrier of §5.3 contains
the cosmological-constant analog explicitly: the matter-independent background term in $V[\psi] = V_0 + \kappa\,
T_{00}[\psi]$. Sweeping it through the frozen closure chain: $15$ of $18$ background values pass (degeneracy $15$, no
singleton selector; the pass set is bounded and non-contiguous), so the background is **F50 bounded-moduli** — the
closure does not select its value. The discrimination control is the coupling $\kappa$, which the same chain *does*
constrain (a computed admissibility boundary: $\kappa \le 10$ converges, $\kappa \ge 15$ runs away) — so the audit
distinguishes closure-constrained parameters from genuine moduli; it is not an everything-is-contingent verdict.
**Demarcation:** *no in-layer $\Lambda$ value-law exists; any claimed in-layer derivation of $\Lambda$'s value must
smuggle a selection; the in-layer content is at most an admissibility window.* This is the same F47/F26 demarcation
pattern the SM track exhibits for its contingent quantities — the cross-track recurrence is itself evidence for §8.

## 7.4 The measurement problem: a structural discriminator

(From the SM-track extension; included for completeness of the breadth claim.) Measurement-selection — "which outcome
becomes the fact" — is proven an **irreducible strict extension** of quantum mechanics in the calculus: records are
$\Sigma_f$-definable, selection is not, by an explicit non-factorization witness. The constructive payoff is a
*no-fitting* discriminator: any future single-outcome theory must either modify the defect ledger $D$
(objective-collapse family) or only the readout $\Sigma_f$ (many-worlds family); a community-accepted single-outcome
theory touching *neither* would falsify the claim. This stakes a structural prediction about *where any future theory
must land*, before such a theory exists.

## 7.5 The pattern

| puzzle | law | verdict | control |
|---|---|---|---|
| Bell nonlocality | F49 + F37 | nonlocal residual recovered; carrier $\neq$ hidden variable (forbidden rule) | classical mixture: locally explainable, LHV table exhibited |
| BH information | F34 | loss gauge-only at full boundary; real at partial readouts | exact complement-unitary witness |
| cosmological constant | F50 (+F47/F26) | bounded-moduli; no in-layer value-law | $\kappa$: closure-constrained boundary |
| measurement | non-factorization | irreducible strict extension; $D$-vs-$\Sigma_f$ discriminator | identical-diagonal witness pair |

One grammar; six foundational puzzles (counting §6's three); every verdict computed, controlled, and graded.
