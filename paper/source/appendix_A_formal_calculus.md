# Appendix A — the calculus, formally (working subset)

This appendix states, at usable precision, every formal object the body relies on. Full development: Foundations II–IV.

## A.1 Descent and obstruction

For a surjection $q:H\to Q$ and readout $t:H\to T$:

$$
t \text{ descends} \iff \mathcal O_q(t) = \{(h,h'): q(h)=q(h') \wedge t(h)\neq t(h')\} = \varnothing
\iff \exists\,\bar t:Q\to T,\ \bar t\circ q = t .
$$

Both directions are finite checks on $H\times H$ (choose representatives; well-definedness is exactly
fiber-constancy).

## A.2 Strict extension and the factorization defect (FIII Thms 12–13)

For maps $\pi_0:S\to O_0$, $\pi_1:S\to O_1$ on a finite carrier:

$$
\Delta_{\mathrm{fact}}(\pi_0,\pi_1) = \{(s,s'): \pi_0(s)=\pi_0(s') \wedge \pi_1(s)\neq\pi_1(s')\},
\qquad
\Delta_{\mathrm{fact}}\neq\varnothing \iff \nexists\,\phi:\ \pi_1 = \phi\circ\pi_0 .
$$

Used as: the $X/Y$ coset (§4: witnesses of the clean-separation defect); GUT$\leftrightarrow$SM non-relabeling
($\Delta_{\mathrm{fact}}(\mathrm{SM},\mathrm{GUT})=15$, reverse $=0$); the QM–GR ladder defect ($8$ witnesses).

## A.3 Non-commuting completions (FIII Thms 9–10)

There exist idempotents $E_1,E_2$ on a finite carrier with $E_1E_2\neq E_2E_1$; the route-mismatch defect
$\Delta_3^{\mathrm{comp}}(E_1,E_2)=\{c: E_1E_2(c)\neq E_2E_1(c)\}$ is non-empty iff they fail to commute. Minimal
witness: $C=\mathcal P(\{a,b,c\})$, $E_1(S)=S\cup\{b\}$ if $a\in S$ else $S$; $E_2(S)=S\cup\{c\}$ if $b\in S$ else $S$;
then $E_1E_2(\{a\})=\{a,b\}\neq\{a,b,c\}=E_2E_1(\{a\})$. Reading: route mismatch is a real typed defect even when each
completion is individually exact — the calculus's typing of non-renormalizability (§5.1).

## A.4 The six primitives and the no-algebra theorem

$\mathbb P=\{P_1,\dots,P_6\}$ (descent, representability, route mismatch, refinement, packaging, audit) are role
labels for typed judgments. Theorem-grade exclusions (FIII): no total binary operation $*:\mathbb P^2\to\mathbb P$
decodes judgment status (no total six-symbol algebra); no universal claim that all structure decomposes into the six.
Directed-cell notation $P_i \leftarrow P_j$ names a typed, individually-audited judgment, never a product.

## A.5 The F-laws used in this paper (one-line formal cores)

| law | statement (core) | used in |
|---|---|---|
| **F23** probability | a readout unresolved on the fiber of $q$ admits a *stable* weight $\Pr_{q,r}(a,v)=m(\lambda(a))(\{h: q(h)=a, r(h)=v\})$ | §5.4 (Born ledger) |
| **F26/F47** contingency & fine-tuning | no value-law lands on a contingent (moduli) selection; fine-tuning = small selector region | §4.6, §7.3, §8.4 |
| **F27** conservation | a charge is conserved iff it descends through the orbit quotient (obstruction $=0$) | §4.4, §6.3 (baryon number) |
| **F34** information loss | $\mathrm{Recoverable}(\sigma,\tau,\rho) \iff \mathcal O_\rho=\{(h,h'):\rho(\tau h)=\rho(\tau h') \wedge \sigma(h)\neq\sigma(h')\}=\varnothing$; loss legitimate iff later identifications are invisible to $\sigma$ | §7.2 |
| **F37** complementarity | $q_A \perp q_B \iff \nexists (J,j,a,b):\ a\circ j=q_A \wedge b\circ j=q_B$ (no admissible joint quotient) | §5.3, §7.1 |
| **F39** entropy | $E(q)$ = fiber volume; chain rule $E(q_C)=E(q_F)\odot m$; monotone under coarsening | §5.4 (area ledger) |
| **F48** gluing/topology | global obstruction as non-trivial gluing class (monopole obstruction $=0$ in the clean branch) | §4.4, §6.3 |
| **F49** common source | $\mathrm{LocallyExplainable}(\kappa) \iff \mathrm{CommonSource}(\sigma) \vee \mathrm{InterfaceFactorization}(\iota)$; else statused nonlocal residual | §7.1 |
| **F50** background selection | descended background $b$: **necessary** ($b$ constant) xor **moduli** ($\exists m,m': b(m)\neq b(m')$); **vacuum** iff $V=\{m_*\}$ | §7.3 |
| **F51** unification | parent $Q_U$ with commuting squares $\pi_A\circ q_U = q_A\circ\iota_A$, $\pi_B\circ q_U = q_B\circ\iota_B$ + status-compatible claim lifts | §4.4, §5.2, §5.4 |

## A.6 Landing modes and audit gates (operational definitions)

**Modes.** COMPUTE (value/verdict from the construction); SELECT (choice on declared conditions); PROVE-BLIND
(invariance theorem ⇒ observed-input); GROUND (condition supplied as down-shadow of a named higher source; carries
source-warrant + theorem-strength caveats); RECOGNITION (known result reproduced as a law-instance, non-circularly);
FORBIDDEN-RULE/DEMARCATION (computed exclusion/classification with can-fail control).

**Gates** (all mechanical; validators enforce): *anti-tautology* — target not definitionally equal to its evidence;
*anti-circularity* — each hypothesis independently satisfiable by a conclusion-violating structure (exhibited);
*frozen-machinery* — imports SHA-256-pinned, no retuning; *can-fail control* — a configuration on which the claim fails;
*no-overclaim* — artifact text checked against a blocklist; *anti-contamination* (cross-track) — substrate-foreign
tokens fail the build.

## A.7 The key derived quantities of the body

- **Embedding ratios** (§4.4): over one SM generation,
  $\operatorname{Tr}T_3^2 = 3\!\cdot\!2\!\cdot\!\tfrac14 + 2\!\cdot\!\tfrac14\!\cdot\!2 = 2$ (quark + lepton doublets),
  $\operatorname{Tr}Q^2 = \tfrac83 + \tfrac23 + 2 = \tfrac{16}{3}$, hence $\sin^2\theta_W = 3/8$; hypercharge
  normalization $k_Y = 5/3$ from $\operatorname{Tr}Y^2 = 5/6$. Control: a non-simple product parent yields $3/23$.
- **RT/shadow price** (§5.4): for entanglement flow with capacities $b$, strong duality gives
  $\max(\text{flow}) = \min(\text{cut})$ and the cut value is the dual optimum — the shadow price
  $\lambda = \partial \Phi^*/\partial b$ of the capacity constraints; "area" is that price.
- **Monogamy** (§5.4, §6.1): $I_3 \le 0$ for min-cut-realizable entropy vectors; GHZ$_4$ has $I_3 = +\log 2$.
- **CHSH** (§7.1): local bound $\max_{\lambda\in\{\pm1\}^4} |E_{00}+E_{01}+E_{10}-E_{11}| = 2$ (16-strategy
  enumeration); Bell state with $a_0=Z, a_1=X, b_{0,1}=(Z\pm X)/\sqrt2$ gives $2\sqrt2$.
- **Prediction kernels** (§6): $J = \partial\mathcal E/\partial w$ (central differences, non-degenerate base);
  $\dim\ker J = 5$; clean-shadow edges = $\{e: \mathcal E(w \pm \delta\,\hat e) = \mathcal E(w)\ \text{exactly},\
  \delta \in [0.05, 0.15]\}$, count $2$ per seed.
