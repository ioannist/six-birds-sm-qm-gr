# Cluster A — PENDING STRUCTURAL PROOFS (self-contained specs for a separate proof-attack session)

> **Purpose.** This track has several verdicts that are **true by enumeration / finite-carrier / cap-conditional
> evidence but are NOT yet structural theorems**. Each such claim is a *door*: a precisely-stated lemma whose proof
> would upgrade "true on the window" → "true, period." This file records each as a **self-contained spec** so a
> future session (or external mathematician) can attack it cold, without re-deriving the context.
>
> **Status legend:** `OPEN` (no proof, recorded here) · `ATTEMPTED→sharpened` (proof attempt reduced it to a
> smaller named lemma) · `LANDED` (a structural theorem was proved — moved to MAIN_RESULTS / manager_log).

## How to attack one of these (binding discipline — read first)

- **Sequential codex only.** One named step per codex dispatch (Mode T = theorem-writing). NO sub-agents, NO
  workflows, NO batching. Manager (Claude) reviews; codex constructs. (See the construction memories.)
- **Freeze the machinery.** Any predicate the proof refers to (Δ_fact, substrate, capacity, the closure chain)
  must be imported **verbatim** from its source step via `importlib` + a **sha256 gate** (mirror
  `steps/step60_*/record_stability_structural_theorem_step60.py`). Retuning a frozen predicate = automatic
  smuggle-reject. Canonical frozen hashes (as of Step 60):
  - Step 57 record requirement (`record_layer_membership`): `8068ff17d5ca911ae12f09cc303c8e67ee47c8c92affd0fad9ca28b61fe2e75f`
  - Step 35 substrate (`higher_layer_mass_closure|mass_completion|scalar_breaks_to_unbroken_u1`): `6a378357c3dea96d4e7a51e54c8dbb94af9785d39cb9622c3469d2f6a6462c06`
  - Step 41 defect (`build_bosons|compute_delta`): `ed5be4969244ae18279a9b6fc5ba73977fc9bc47fcec81ff3c25e8ad076e19c0`
- **Five Mode-T exit states** (terminate in exactly one): `constructed_theorem` (window-independent, zero imports)
  · `conditional_theorem_with_named_imports` · `sharpened_external` (reduce to a smaller named lemma) ·
  `bounded_grammar_saturation_no_go` (prove no argument in a declared proof-grammar discharges it) ·
  `smuggling_reject`.
- **Seven-gate + anti-circularity audit** (see `feedback_construction_mode_T_theorem_writing`): no-smuggling of the
  target (the proof may NOT assume the conclusion or anything extensionally equal to it); anti-circularity (each
  hypothesis independently satisfiable by a structure that fails the conclusion — the Step-39 lesson);
  anti-vacuity (exhibit a populated exemplar class); uniform-parametric-bound (make the dim/charge/cap dependence
  explicit — a window-dependent bound masquerading as uniform is a reject).
- **Converse probe (mandatory can-fail control).** Before claiming any proof, actively try to *construct* a
  counterexample inside AND outside the window. A counterexample is a first-class result (the claim is
  window-conditional, not a theorem), not a failure.
- **Lead with the deflationary truth.** Enumeration is NOT a proof; if you cannot prove it, say so and record the
  sharpened residual here. Hiding "still enumeration" is the worst outcome.

## Status table

| id | claim (one line) | source | landability | status |
|---|---|---|---|---|
| **P1 / L60→L64** | record-stability (substrate ∧ capacity) ⟹ clean-separation (Δ_fact=∅) | Steps 60, 64 | hard (gauge→matter bridge) | `ATTEMPTED→sharpened ×2` (now **L64 charge-orientation cap**) |
| **P2** | single SU(N) with a stable confining substrate ⟹ Δ_fact≠∅ (no clean separation), **all N** | Step 43 | high (pure group theory) | **`LANDED`** (Step 61, `constructed_theorem`) |
| **P3** | ≥3 gauge factors ⟹ no clean separator, **independent of the component cap** | Step 44 | low (currently cap-conditional; may be false uncapped) | `OPEN` |
| **P4** | neutral closure is blind to the SM-vs-alternative content class, **for all carriers** (not just 2 classes) | Steps 48/49/54 | low (shadows not provably independent) | `OPEN` |
| **P5** | the corrected closure chain is blind to generation count N, **all N≥1** (not just N≤6) | Step 51 | medium (per-unit additivity) | **`LANDED`** (Step 62, `constructed_theorem`) |

---

## P1 / L60 — `record_capacity_leak_exclusion` (the record-stability ⟹ clean-separation bridge)

**Status:** `ATTEMPTED→sharpened` (Step 60, exit `sharpened_external`). The reduction is proved; the core lemma is open.

**Formal claim.** For every genuinely-chiral closer `C` in the Step-33 corrected grammar, with the frozen Step-35
witness scalar:
```
substrate(C) ∧ transition_leak_count(C) > 0  ⟹  neutral_record_token_count(C) < 2.
```
Equivalently (Step-60 verified reduction): `substrate(C) ∧ capacity(C) ⟹ Δ_fact(C)=∅`.

**Physical reading.** A gauge structure that (a) has a stable confining substrate whose masses complete by breaking
a dimension-≥3 factor (creating the X/Y colored coset = confining-charged broken vectors, Δ_fact≠∅) **cannot** also
assemble ≥2 charge-neutral composite "record" tokens (color-singlet, charge-sum-0 fund⊗antifund pairs, or
charge-sum-0 like-orientation triples) from its fermion content. A *gauge-breaking* fact forcing a
*matter-content* fact.

**What is already established (Step 60).**
- The reduction: given substrate, `Δ_fact≠∅ ⟺ transition_leak_count>0 ⟺ the witness scalar breaks a factor of
  dim ≥ 3` (verified on all 376 substrate rows; `steps/step60_*/reduction_check_step60.csv`).
- Anti-circularity holds: substrate alone (60 ¬CS witnesses) and capacity alone (311 ¬CS witnesses) are each
  satisfied by non-clean-sep structures; only the conjunction is empty outside CS.
- Empirical base: **0 counterexamples** across the full **11,990-structure** carrier (Steps 58–59) **plus bounded
  outside probes** (Step 60/64; ~9,185 additional closers across single SU(4)/SU(5)/SU(6) relaxed-field and
  two-factor 3|4 / 4|4 — distinct windows, not a single homogeneous corpus; `steps/step60_*/converse_probe_step60.csv`).

**What is missing (the open lemma).** A representation-theory / anomaly / mass-closure argument for WHY breaking a
big factor (for mass completion) structurally forbids two neutral fermionic records. Intuition (unproven): a
neutral record ≈ a charge-matched fund⊗antifund pair (vector-like-ish), in tension with the genuine-chirality
requirement; and the mass-completing scalar that breaks the big factor consumes the structure that would furnish a
second independent record. Turning that into a theorem in the corrected-chirality grammar is the open work.

**Step 64 update — sharpened to L64 (`charge_orientation_cap`).** A direct attack (data-first near-miss study)
did **not** prove L60 but sharpened it. Pattern across all **60** ¬CS-substrate structures (dims 2|4, 3|4, 4, 4|4 —
all with a broken SU(4)): max neutral-record count = **1** (28 have 0, 32 have exactly one — a single zero-charge
like-orientation **triple**, never two independent line-dual records); **no** leak-positive substrate row has a
**line-dual mirror-charge pair** to seed a second record channel. Sharper residual **L64**: *for leak-positive
substrate closers, mass-closure charge-linking + corrected chirality forbid line-dual mirror doubling and allow ≤1
zero-charge like-orientation triple.* Needs: a structural anomaly/mass-closure proof of that cap, independent of
enumeration. Pointers: `steps/step64_mode_t_L60_record_capacity_leak_exclusion_artifacts/` (near_miss_table, the
sharpened lemma); manager_log Step 64.

**Frozen machinery / pointers.** `capacity`/`neutral_record_token_count`: Step 57
`record_layer_membership` (`steps/step57_*/record_stability_descent_step57.py`, lines ~124–162). `substrate`:
Step 35 `higher_layer_mass_closure` + the `scalar_action_diagnostics` reading (see `steps/step59_*` and
`steps/step60_*`). `Δ_fact`: Step 41 `build_bosons`/`compute_delta`. Carrier: Step 33
`corrected_anomaly_chirality_step33.py`. Full attempt: `steps/step60_mode_t_record_stability_structural_theorem_artifacts/`.

**Exit criteria.** `constructed_theorem` (window-independent proof of the displayed implication) discharges
candidate-law obligation #2 (the forbidden region `substrate ∧ capacity ∧ Δ_fact≠∅` is empty for all chiral
structures). A `conditional_theorem` naming the precise representation/anomaly hypothesis is also a real landing.

**Also underpins the Step-69 falsifiable prediction.** This is the *same* lemma whose enumeration-strength version
(0/11,990 counterexamples) is the toy basis for the **record-stability ⟹ no-proton-decay / no-monopole** prediction
(`MAIN_RESULTS.md` L; `FALSIFICATION_ROUTES.md` Step-69 worked instance). Proving L60→L64 upgrades that prediction from
*enumeration-strength* to an *all-structures structural law* — i.e. the contrarian-to-GUT claim would hold for **every**
record-bearing structure in the grammar, not just the swept carrier.

---

## P3 — factor-count exclusion, cap-independent (≥3 gauge factors ⟹ no clean separator)

**Status:** `OPEN`. **Honest landability: low — currently cap-conditional and possibly false without the cap.**

**Formal claim (the version that WOULD be a theorem).** Any gauge structure with ≥3 non-abelian factors admits no
clean-separation (`Δ_fact=∅`) structure — **without** assuming the component cap.

**What is established (Step 44).** Inside the finite carrier, 3-factor structures are excluded because the Step-31
route-completeness "all-factor incidence row" has dimension ≥ 2^k (≥ 8 for k=3), which exceeds the inherited
**component cap 6** — so no 3-factor structure even reaches the mass-closure/clean-separation stage. Verdict
`FACTOR_COUNT_CLOSED`, but graded `structural-arguable-within-finite-component-cap`: *"It is not a statement about
carriers with a different cap or a different representation alphabet."*

**Why it is not (yet) a theorem.** The exclusion **rides entirely on cap 6** (= the SM's own all-factor-row dim,
which *just* fits). With a larger cap, Pati–Salam (`SU(4)×SU(2)×SU(2)`), left–right, trinification re-enter the
comparison (Step 53). So the cap-independent claim may be **false**; the honest open question is whether a
*different* cap-independent argument excludes ≥3-factor clean separators, or whether the SM's 2-factor structure is
genuinely cap-selected. Recorded as an open question, NOT a landable lemma.

**Exit criteria.** Either (a) a cap-independent structural exclusion of 3-factor clean separators
(`constructed_theorem`), or (b) a `bounded_grammar_saturation_no_go` proving the cap is load-bearing (the
exclusion cannot be made cap-independent), with a named next-grammar delta. **Pointers:**
`steps/step44_mode_b_window_closure_factor_count_artifacts/`, `steps/step53_*` (competitor table), §5/§10 of
`SM_TRACK_CLOSEOUT_QUESTIONS.md`.

---

## P4 — content-blindness, structural (neutral closure cannot distinguish the SM-vs-alternative content class)

**Status:** `OPEN`. **Honest landability: low.**

**Formal claim.** No neutral closure invariant distinguishes the two SM-signature content classes — for **all**
carriers, not just the Steps-48/49 2-class quotient.

**What is established (Steps 48/49/54).** On the 2-class carrier, three definitionally-distinct neutral shadows
(integer charge-quantization; Yukawa-texture connectivity; full mass-matrix rank) are **all blind** to the
SM-vs-alternative distinction. Verdict `CONTENT_TYPE_LIMIT` / `CONTENT_TYPE_LIMIT_3_SHADOWS_BLIND`.

**Why it is not (yet) a theorem.** (i) Finite carrier (2 classes); (ii) the Step-54 rank shadow coincides
**extensionally** with the Step-49 connectivity shadow on this carrier, so the "3 shadows" are not provably
independent — confirmatory, not strongly-independent evidence. A structural proof would have to characterize the
full algebra of neutral closure invariants and show none separates the classes — substantially harder than the
finite check.

**Exit criteria.** A structural characterization of neutral-closure-invariants + a proof none distinguishes the
classes (`constructed_theorem`), or a `sharpened_external` naming the minimal separating-invariant candidate that
must be ruled out. **Pointers:** `steps/step48_*`, `steps/step49_*`, `steps/step54_*`; §7 of
`SM_TRACK_CLOSEOUT_QUESTIONS.md`.

---

---

## P2 — single-factor clean-separation exclusion — ✅ LANDED (Step 61, `constructed_theorem`)

**Status:** `LANDED`. A window-independent structural theorem in the frozen toy grammar.

**Theorem (proved).** For a single non-abelian factor SU(N): **`substrate(C) ⟹ Δ_fact(C) ≠ ∅`** — no single SU(N),
for any N, can have both a stable confining substrate and clean separation.

**Proof (3 symbolic steps from the frozen code, no enumeration).**
1. Single-factor substrate ⟹ the witness scalar breaks the factor: `higher_layer_mass_closure` passes only via the
   branch requiring `scalar_breaks_to_unbroken_u1`, which requires `action_active` — for one factor, on that factor.
2. Scalar acts + a confining residual ⟹ residual = N−1 ≥ 2 ⟹ N ≥ 3.
3. residual ≥ 2 ⟹ `transition_leak_count = 2(N−1) > 0` ⟹ Step-41 `compute_delta` pairs the massless confining
   gluons with the massive charged coset vectors (same confining readout, different mass) ⟹ Δ_fact ≠ ∅.

**Honest nuance (kept in the record).** The implication is window-independent (proved symbolically); its antecedent
(single-factor substrate) is non-vacuously populated only at **N=4** in this carrier (12 structures, all ¬clean-sep)
— N=3,5,6 have none, N≥7 have no chiral closers. So it is a valid all-N implication, non-vacuous at N=4. **Scope:
single-factor axis only** — the multi-factor / component-cap bound (P3) is a separate, still-open, cap-conditional item.

**Pointers.** `steps/step61_mode_t_single_factor_clean_separation_theorem_artifacts/` (proof_chain, statement.tex,
converse_probe, audits); manager_log Step 61. Upgrades Step 43's "structural-arguable" single-factor bound.

---

## P5 — N_gen-blindness for all N — ✅ LANDED (Step 62, `constructed_theorem`)

**Status:** `LANDED`. A window-independent structural theorem (proven-blindness type-limit).

**Theorem (proved).** For a content unit `u` that is **local-anomaly-free** and has an **even per-unit
`su2_doublet_count`**, the frozen Step-51 `closure_row(N,u)` passes identically for **every N ≥ 1**:
`full_chain_passes(N) = full_chain_passes(1)`, with all per-gate statuses N-independent. (The SM unit qualifies:
anomaly-free, 4 doublets.)

**Proof (symbolic from `closure_row`).** (1) anomaly coefficients scale linearly `scaled[k]=N·u[k]` → anomaly-free
is N-independent for N≥1; (2) Witten parity `(N·doublet)%2` is the only N-sensitive gate, N-independent iff the
doublet count is even; (3) packaging/chirality/clean-sep/mass-closure are `nonempty=(N≥1)`. Hence all gates pass
identically for all N≥1.

**Anti-circularity / load-bearing hypothesis (proved).** The SM unit passes identically through **N=1000**
(window-independent); an **odd-doublet control** (anomaly-free, doublet=1) is N-sensitive (alternates by Witten
parity) — so the even-doublet hypothesis is genuinely load-bearing.

**Honest scope.** This is **proven-blindness** (a positive type-limit), **NOT** a derivation of N=3. The chain is
blind to N; minimality picks N=1; the CP lower bound N≥3 remains observed-input. Faithfulness to the Step-33
corrected anomaly/parity gates is verified (`faithfulness_step62.csv`).

**Pointers.** `steps/step62_mode_t_ngen_blindness_theorem_artifacts/`; manager_log Step 62. Upgrades Step 51's
finite (N≤6) blindness to an all-N theorem.

---

## Session summary (proof-attack sweep, 2026-06-09)

- **LANDED as constructed theorems:** P2 (single-factor clean-separation exclusion, Step 61) · P5 (N_gen
  blindness for all N, Step 62). Each verified against the frozen code, deterministic, validator-passing,
  seven-gate + anti-circularity audited, no overclaim.
- **Attempted, reduced (not landed):** P1 / L60 (record-stability ⟹ clean-separation, Step 60 →
  `sharpened_external`; the gauge→matter bridge remains open).
- **Recorded OPEN (not attacked this session):** P3 (factor-count exclusion — cap-conditional, possibly false
  uncapped) · P4 (content-blindness, structural — shadows not provably independent). Attack in a future session
  using the self-contained specs above.
