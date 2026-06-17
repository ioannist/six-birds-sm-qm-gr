# 6. The three falsifiable predictions

The results of Sections 4–5 recover, demarcate, and unify. This section presents the three places where the calculus,
run honestly, **takes a side against a prevailing program and stakes a falsification condition on it**. All three
predictions are *forced* — each is the sharp form of its track's central structural result, not an add-on — and each
was computed under the symmetric-scrutiny protocol of Section 3 (surviving rejected riggings toward *and* against it;
Appendix C). Predictions 1–2 are the sharp forms of the QM–GR fork; Prediction 3, of the SM coset spine. One
record/memory layer ties the prediction set at the grammar level, while the physical claims remain track-specific.

---

## 6.1 Prediction 1 — Entanglement does not determine geometry (strong it-from-qubit fails)

**The contested program.** A prominent line in quantum gravity ("it-from-qubit", ER=EPR, entanglement-builds-geometry)
holds that bulk spacetime is *fully determined by* boundary entanglement: given the complete entanglement data of the
boundary state, the bulk geometry is reconstructible. The fork of §5.2 forces the opposite: the gravitational readout
$d_3$ is a sibling of the entanglement modes, not a function of them, so *some* geometric data must be invisible to
*all* entanglement measures.

**The sharp form.** Let $w \in \mathbb R^{n}_{>0}$ be the bulk geometry (edge weights/capacities of a holographic
graph carrier) and let the **entanglement fingerprint** $\mathcal E(w)$ be the complete boundary data: all
$2^8 - 2 = 254$ boundary-region min-cut entropies, all $3{,}025$ mutual informations, all $7{,}770$ tripartite
informations $I_3$ — $11{,}049$ features. The prediction concerns the kernel of the reconstruction map:

$$
J \;=\; \frac{\partial\, \mathcal E}{\partial\, w}
\qquad\text{and}\qquad
\boxed{\;\dim \ker J \;>\; 0\;}
$$

robustly on non-degenerate geometries — together with the existence of **finite, two-sided invisible deformations**:
single bulk capacities $w_e$ that can be moved by finite $\pm\delta$ with *every one* of the $11{,}049$ entanglement
features unchanged, while named bulk-geometric quantities change.

**The computation (independently reproduced).** On the frozen 14-edge holographic carrier of §5.4, at generic
(tie-broken) geometries, with two-sided central differences, across three seeds:

| seed | $\operatorname{rank} J$ | $\dim\ker J$ | clean shadow edges (both-direction, finite range) |
|---|---|---|---|
| 101 | 9 | **5** | **2** |
| 202 | 9 | **5** | **2** |
| 303 | 9 | **5** | **2** |

An explicit witness pair: two geometries differing by $\delta = \pm 0.15$ on a shadow edge have *identical* fingerprints
(residual $< 10^{-9}$ across all $11{,}049$ features, both signs) while the bulk interior volume differs by $0.15$. The
**can-fail control** is essential and passes: on a boundary-anchored tree (every edge on some boundary min-cut) the
kernel is exactly zero — entanglement *does* determine that geometry — so the test can return the it-from-qubit verdict
and, on the holographic carrier, does not. A degenerate-geometry artifact that initially inflated the kernel (one-sided
differences at a maximally tied point) was caught and removed; the reported numbers are the artifact-free ones
(Appendix C.3).

**The prediction, stated for the community.**

> On any non-trivial holographic / tensor-network geometry, the map from the complete boundary-entanglement fingerprint
> (all subregion entropies, mutual informations, and multipartite informations) to the bulk geometry has a **non-trivial
> kernel**: there is a robust sector of bulk geometric degrees of freedom invisible to every entanglement measure.
> Complete entanglement-only bulk reconstruction is therefore impossible; any reconstruction program must add
> non-entanglement boundary data.
>
> **Falsifier:** exhibit a non-trivial (non-tree, multi-path) holographic or tensor-network geometry whose
> entanglement$\to$geometry map is injective — central-difference kernel zero and no two-sided finite invisible
> deformation. That would refute the fork's sharp form.

**Grade and overlap, honestly.** FORBIDDEN-RULE at toy level; conditional on the grounded premise of §5.3; not a claim
proven about nature. The *phenomenon* overlaps the known "entanglement shadow" of holography — the calculus's
contribution is to *force* it from a structural law (the fork), compute its dimension, exhibit a two-sided witness, and
attach a falsification condition; the overlap is a fact, not a retraction.

---

## 6.2 Prediction 2 — Gravity does not mediate entanglement (BMV-null)

**The contested program.** The most anticipated near-term probe of quantum gravity is the BMV proposal (Bose et al.;
Marletto–Vedral): place two masses in spatial superpositions, let only gravity couple them, and test whether they
become *entangled*. The widely-stated inference is that gravitationally-induced entanglement would witness a *quantum*
(coherent) gravitational mediator — a graviton-like degree of freedom. The fork of §5.2 forces the opposite: the
gravitational arm is a sibling readout that does not have access to the quantum phase mode and cannot carry it
coherently between parties.

**The sharp form.** Two matter parties $A,B$ are prepared as independent path superpositions $|+\rangle_A|+\rangle_B$
(initial entanglement zero, computed: $6.2\times10^{-18}$). A mediator couples to them *only through their
geometry-visible modes*. The fork grammar fixes the mediator's character — and this is the load-bearing derivation, not
a modeling choice: $q_{\mathrm{GR}} = (d_0,d_2,d_3)$ **excludes** the QM-only phase mode $d_1$, and $T_{\mathrm{QG\text{-}
NoGo}}$ forecloses the fused amplitude-over-geometry object — so the admissible mediator is a **classically-indexed
record channel** (one mediator state per geometry-visible configuration; a record, not a superposition). The prediction
is that such a channel generates no entanglement:

$$
\boxed{\ \mathcal N_{AB}^{\mathrm{fork}} = 0,\qquad \mathrm{CHSH}^{\mathrm{fork}} \le 2,\qquad
\text{local coherence fully damped}\ }
$$

with the *forbidden* coherent mediator built only as a can-fail control that **must** entangle.

**The computation (verified against closed-form QM).** On two path qubits with a mediator of record-dimension 4:

| channel | negativity $\mathcal N$ | CHSH | local-coherence damping |
|---|---:|---:|---:|
| fork-admissible **record** channel | $\mathbf{0}$ | $\mathbf{0}$ | $1.0$ (full decoherence) |
| forbidden **coherent** control (CPhase $\pi/2$) | $\tfrac{1}{2\sqrt2} = 0.3536$ | $\sqrt 6 = 2.4495$ | $1-\tfrac{1}{\sqrt2}=0.2929$ |

with the local bound enumerated to $2$ (16 deterministic strategies). The fork channel is exact dephasing in the joint
path basis (output $\mathbb 1/4$): decoherence *without* entanglement. The control entangles past the classical bound,
so the test discriminates — a channel of this finite model *can* produce gravitational entanglement; the fork's channel
does not. All four numbers match closed form ($\mathcal N = \mathcal C/2$, $\mathrm{CHSH}=2\sqrt{1+\mathcal C^2}$ for
concurrence $\mathcal C$). The **mean-field trap is avoided by construction**: the channel restriction is derived from
the frozen access structure, *not* from the semiclassical back-reaction $V=V_0+\kappa T_{00}$ (an expectation-value
channel through which "no entanglement" would be a LOCC tautology); the validator fails on any $T_{00}$/expectation
coupling.

**The prediction, stated for the community.**

> Under the fork/co-sourcing reading, the gravitational interaction is a classically-indexed record channel:
> gravitationally-coupled masses in spatial superposition **decohere without becoming entangled**. BMV-type experiments
> will return a **null** entanglement result, accompanied by which-path decoherence.
>
> **Falsifier:** a confirmed BMV-type detection of gravitationally-induced entanglement between masses. (Secondary,
> practically out of reach: a confirmed quantization of the free gravitational field / single-graviton detection — by
> Dyson's argument this is not a realistic test, so BMV is the operative one.) Either of the *first* kind refutes the
> fork reading of gravity directly.

**Grade and overlap, honestly.** FORBIDDEN-RULE at toy level; conditional on the grounded premise of §5.3; not a claim
proven about nature. The lemma that an expectation-value/classical channel cannot create entanglement is standard
(LOCC; the Kafri–Taylor–Milburn classical-channel-gravity model is in this camp) — the calculus's contribution is to
*force* gravity onto that side of the dichotomy from the frozen fork and no-go (with the foreclosed coherent control
demonstrating it was not assumed), and to tie the gravitational channel's classicality to the *same record layer* that
grounds §4 and §6.3. This is the most near-term falsifiable of the three predictions.

## 6.3 Prediction 3 — Record-stability forbids proton decay and magnetic monopoles (contra grand unification)

**The contested program.** Grand unification generically predicts that the proton decays (lifetimes $\sim
10^{34\text{–}36}$ yr in surviving models) and that monopoles exist: both are mediated by the $X/Y$-type coset bosons
of the unified parent. The spine of §4 forces the opposite — not "decay is slow" but "decay is structurally forbidden,
for a reason no other framework names."

**The sharp form.** Define, on the frozen $11{,}990$-structure carrier of §4: $\mathrm{RS}(C)$ — structure $C$ is
**record-stable** (stable confining substrate $\wedge$ capacity for $\ge 2$ neutral records $\wedge$
distinguishability); and the branch split by the factorization defect, $\Delta_{\mathrm{fact}}(C) = \varnothing$
(clean: baryon number descends, F27 obstruction $0$; monopole gluing obstruction, F48, $=0$) versus
$\Delta_{\mathrm{fact}}(C) \neq \varnothing$ (breaking: $X/Y$ coset present; proton decay and monopoles mediated if
realized). The prediction is the implication

$$
\boxed{\;\mathrm{RS}(C) \;\Longrightarrow\; \Delta_{\mathrm{fact}}(C) = \varnothing\;}
\qquad\text{i.e.}\qquad
\#\{\, C : \mathrm{RS}(C) \wedge \Delta_{\mathrm{fact}}(C)\neq\varnothing \,\} = 0 .
$$

**The computation (independently reproduced).**

| | clean ($\Delta_{\mathrm{fact}}=\varnothing$) | breaking ($\Delta_{\mathrm{fact}}\neq\varnothing$) |
|---|---:|---:|
| record-stable | 24 | **0** |
| not record-stable | 292 | 11,674 |

Non-circularity is computed, in two ways. First, the hypothesis is not the conclusion in disguise:
record-stability and clean-separation are *different* sets ($24 \subsetneq 316$ — most clean structures cannot bear
records; the implication is strictly directional). Second, each conjunct of record-stability *alone* admits decaying
structures — $60$ substrate-only and $311$ capacity-only breaking-branch witnesses — so only the conjunction forces the
clean branch. The implication has content; it is not definitional.

**The prediction, stated for the community.**

> The capacity of a universe to bear stable records is structurally tied to baryon-number conservation and the absence
> of magnetic monopoles: any record-bearing structure lies in the clean branch, in which the coset that would mediate
> proton decay and monopoles is absent. The proton of a record-bearing universe is **exactly stable** — not long-lived
> — and no monopole exists. The distinctive content is the **link**: no other framework ties record-bearing capacity
> to baryon conservation; grand unification predicts the opposite on both counts.
>
> **Falsifier:** a confirmed proton-decay event (e.g., Hyper-Kamiokande) or a confirmed magnetic monopole. Our universe
> manifestly bears stable records; either observation severs the predicted link.

**Grade and scope, honestly.** FORBIDDEN-RULE / DEMARCATION at enumeration strength: $0/11{,}990$ on the frozen
carrier, with the all-structures theorem upgrade (lemma L60$\to$L64) open; conditional on record-stability as the
grounding source (§4.5); frame-transfer-limited — this does not *prove* the physical proton stable. The surface
statement "the proton does not decay" coincides with the unadorned Standard Model; the falsifiable novelty is the
*structural reason* and the *link*, which GUTs contradict.

---

## 6.4 What makes these predictions rather than retrodictions

Three properties, shared by all three. **(i) Forced:** each is the sharp form of its track's central theorem (the fork,
for Predictions 1–2; the coset spine + grounding, for Prediction 3), not a tunable add-on — the machinery that produces
it was frozen before the question was asked. **(ii) Contrarian:** each contradicts a live mainstream program (strong
it-from-qubit; the BMV-positive expectation; grand unification), so agreement with existing data cannot have been fitted
in. **(iii) Falsifiable at stated cost:** each names a concrete observation or construction that kills it — and in every
case the falsifier would also destroy the track's central result, so the framework genuinely has skin in the game.
Prediction 2 is the nearest-term: BMV-class experiments are funded and advancing, and a result is plausible within the
decade.

> **Three prediction panels.** *Left (Prediction 1): two bulk graphs with visibly different interior weights, identical
> boundary-entanglement fingerprint table beside each; a struck-through arrow "entanglement $\Rightarrow$ geometry."
> Center (Prediction 2): two superposed masses, a gravitational channel drawn as a meter/record (not a wavy coherent
> line), output state $\mathbb 1/4$; "decoherence, $\mathcal N = 0$"; a struck-through "entanglement". Right
> (Prediction 3): the $2\times2$ record-stable $\times$ branch table as a population map — the record-stable column
> entirely inside the clean branch; arrows to "no proton decay (F27 $=0$)" and "no monopole (F48 $=0$)"; a
> struck-through GUT arrow labeled "$X/Y$ mediation." A thin band beneath all three: "one record/memory layer" (the
> cross-track tie, §8).*
