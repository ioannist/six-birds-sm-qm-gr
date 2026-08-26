# Physics Layer Atlas — FREEZE NOTES (Stage 1, Phase-0 bundle)

**Status:** FROZEN. This file records what is frozen, the calibration edges and their known answers, the
binding non-claims, how the elasticity firewall works, the numbered list of Layer-A review fixes applied,
and the predicted shadow-heavy / emergence-sparse shape as the **registered null**. It is the assembler's
freeze record for the Phase-0 bundle produced by `wf_phase0_freeze.mjs`.

> **REVIEW CAMPAIGN ADDENDUM (2026-08-26; round-19 ruling).** The `SHA256SUMS` entry for
> `SIX_BIRDS_ANTI_REDUCTIONISM_PRIMER.md` references a file that is absent from this public release.
> Accordingly, the freeze gate is a consistency validator for the files and policy it can inspect, not a
> tamper-evident freeze: the checksum list and validator are co-located with the checked material and have
> no externally anchored or signed digest. This note does not alter `SHA256SUMS` or the gate script.

> **PAUSE 1 v2 update (2026-06-04, external-review remediation).** The external review
> (`EXTERNAL_REVIEW_v1.md`, APPROVE-WITH-REQUIRED-CHANGES) required R1–R8; the per-item disposition is in
> **`CHANGELOG_PAUSE1_v2.md`**. The two material additions to the frozen bundle are the **full closure-card
> manifest** (`closure_card_manifest.jsonl`, the R1 full-card-freeze artifact) and the **executable
> freeze-gate validator** (`validate_freeze_gate.mjs` + its single-source-of-truth `CONTRACT.json`, R7).
> The previously *declarative* freeze-blocker is now *executable* and **passes**:
> `node validate_freeze_gate.mjs --mode freeze --dir <prereg>` → `FREEZE-GATE: PASS`, exit 0. The edge
> count is now **46** (the O1 split of E028 into E028a/E028b added one row over the prior 44 + the O3
> hierarchy edge E043). See §1, §4, §8 below.

> **PAUSE 1 v4 update (2026-06-04, external re-review remediation).** The external re-review
> (`EXTERNAL_REVIEW_v3.md`, APPROVE-WITH-REQUIRED-CHANGES) required R1–R6 (O1–O2 optional); the per-item
> disposition + the mutation-test record are in **`CHANGELOG_PAUSE1_v4.md`**. The core theme was to make
> `CONTRACT.json` the **single source of truth** and make the validator **actually enforce** every predicate
> the contract/rubric claim. The validator now carries **four new hardened checks beyond the original eight**:
> **C9 (R4)** the near-intra-layer seal gate, **C10 (R3)** value_split reported-tier consistency, **C11 (R2)**
> recognition-landing named_import (single non-menu import, set-equal to `affected_edges`), **C12 (R6)** the
> registered-null tally + stale-prose guard. The **value_split reported-tier rule (R3)** is now ONE coherent
> semantics across CONTRACT / TYPING_RUBRIC / SCIENCE_DIGEST / edge_manifest / closure_card_manifest /
> registered_null: `reported_tier` is split-type-dependent (`value_tier` for `form_value`/`form_value_imported`,
> `form_tier` for `theorem_run`); **E029 (ChPT) is the canonical `form_value_imported` row — form-descends-E1
> skeleton + imported-E2 run-generated LECs, so reported_tier = value_tier = edge_scored_tier = E2, and E029 is
> in the E2 set, NEVER the E1 set.** The **corrected registered null** (foreclosure-dominant) is restated in §7.
> The **R1 QCD wording** ("no free **proton/hadron** mass parameter; quark masses + coupling/scale fixed
> independently under the physical-quark-mass lattice-QCD protocol; spectrum readout out-of-sample, not fitted")
> is propagated to the primer §5 and `theory_manifest_notes.md`. The reviewer's **four mutation tests now FAIL
> as required** (see §9). Freeze gate: `--mode freeze` → **PASS, exit 0**.

> **Provenance.** Built on the frozen bootstrap: the anti-reductionism primer
> (`/home/repos/six-birds-papers/SIX_BIRDS_ANTI_REDUCTIONISM_PRIMER.md`) and the SBT science digest
> (`/home/repos/six-birds-erdos/docs/methodology/02_sbt_science_digest.md`), with the Erdős
> mode/exit-state/tier vocabulary (`enums.md`) adapted to edge-tiers. Where this bundle and an SBT paper
> would disagree, **the paper governs** — flag the discrepancy.

---

## 1. What is frozen

The Phase-0 bundle, in `/home/repos/six-birds-papers/physics_atlas/prereg/`:

| File | What it freezes |
|---|---|
| `SCIENCE_DIGEST.md` | the physics-framed SBT machinery: closure package `T=(Z,f,Σ_f,E,D)`; the Ξ adequacy residual (Schur complement) on declared finite toy models; route-mismatch & idempotence-defect; the up/down asymmetry; foreclosure / recognition-mode landing; the worked proton-mass E0 example. |
| `TYPING_RUBRIC.md` | the elasticity firewall: the card schema (§A) + node registry (§A.7); the modality taxonomy (§B) + modality↔tier emittability table (§B.8); the edge-tier definitions and the **deterministic foreclosure decision-procedure** (§C.5); the finite diagnostics (§D); the **no-smuggling gates E.0–E.11** (§E); the calibration protocol + freeze-gate predicate (§F); non-claims + banned language (§G). |
| `theory_manifest.jsonl` | **21** closure-package **stubs** (the lawful physics layers), snake_case canonical ids. The `provisional_Z/f/E` stubs are NOT sufficient for scoring (gate E.12). |
| `closure_card_manifest.jsonl` | **(R1, new)** the **30 full §A closure-package cards** — every field (`Z, f, Sigma_f, E, D, accepted_observables, lawful_layer_note, casting_justification, casting_alternatives, status:"frozen"`) — for all **21** theory ids **plus the 9 casting-bearing `candidate_substructure` nodes**. The authoritative frozen casting object; the theory_manifest stubs are its short form. Concatenated + de-duplicated (by id, first-wins) from `closure_cards_part1.jsonl` (11) + `closure_cards_part2.jsonl` (19). |
| `theory_manifest_notes.md` | inclusions/exclusions + the FROZEN canonical id convention. |
| `edge_manifest.jsonl` | **46** typed inter-theory edges (42 original + the E027/E035/E028 splits + the O3 hierarchy edge E043). |
| `edge_manifest_notes.md` | the FROZEN id-alias table, the non-peer node registry, the calibration set, the splits, the per-edge field schema, the registered-null distribution. |
| `CONTRACT.json` | **(R2/R5/R6/R7, new in hash set)** the machine single-source-of-truth the validator reads: `canonical_modalities`, `modality_tier_compat`, `recognition_resolution`, `value_split_schema`, `node_established_rule`, `calibration_rules`, `anti_control_rules`, `full_card_freeze_rule`, `registered_null_caveat`, `freeze_gate_predicate`. Where prose and this file disagree, the validator reads this file; where an SBT paper and this file disagree, the paper governs. |
| `validate_freeze_gate.mjs` | **(R7; hardened R2–R6, v4)** the executable freeze-gate validator (Node built-ins only). **12** collected machine checks (C1–C12); exits nonzero on any failure. |
| `CHANGELOG_PAUSE1_v2.md` | **(new)** the per-item R1–R8 / O1–O4 disposition for the external-review remediation. |
| `SHA256SUMS` | integrity manifest; updated to cover `closure_card_manifest.jsonl`, `CONTRACT.json`, `validate_freeze_gate.mjs`, and the edited `edge_manifest.jsonl` / `FREEZE_NOTES.md` / `CHANGELOG_PAUSE1_v2.md`. |
| `FREEZE_NOTES.md` | this file. |

**Counts:** n_theories = **21**, n_closure_cards = **30** (21 theory + 9 candidate_substructure nodes),
n_edges = **46**, n_calibration_edges = **9** (5 known-tier controls + 4 E3 anti-controls).

**What "frozen" means here.** The cards, the node registry, the edge endpoints, the calibration set with
its machine-checkable `calibration_known_tier`s, and the rubric/gates are frozen. The `provisional_*`
tier/modality guesses on the edges are the **pre-audit registered null** (§7), **not** the audited
verdict — a later scored audit must force each tier through §C.5, and may not be tuned toward the
predicted shape.

---

## 2. The calibration edges and their KNOWN answers (the freeze-blocker)

**9 calibration edges.** The atlas freezes only if the freeze-gate predicate (§4 below) holds.

*Known-tier controls (computed tier must EQUAL `calibration_known_tier`):*

| id | edge | `calibration_known_tier` | rule | known answer / spec |
|----|------|---------------------------|------|---------------------|
| E001 | qcd → hadron-spectrum (proton mass) | **E0** | must_seal_E0 | the resolved emergent constant. **Corrected R8 wording:** *physical-quark-mass lattice QCD* (not chiral-limit, not pure-gauge); **no free proton/hadron MASS parameter**; quark masses and coupling/scale fixed **independently** under the declared lattice-QCD protocol (overall scale set by **one hadronic input**, running by **dimensional transmutation / Λ_QCD**); the **proton-mass / hadron-spectrum readout is out-of-sample and NOT fitted**. DEFERRED, **not run, not derived**. THE anchor. |
| E002 | statistical_mechanics → thermodynamics | **E1** | must_seal_E1 | Ξ=0 descent on a finite ensemble→macrostate toy; refinement-stable. |
| E003 | special_relativity → classical_mechanics | **E1** | must_seal_E1 | clean v/c→0 limit-descent (Wigner–İnönü). |
| E004 | kinetic_theory → hydrodynamics | **E1** | must_seal_E1 | Chapman–Enskog Ξ=0 for the EQUATIONS; transport coeffs are a value_split E0 sub-target. |
| E005 | general_relativity → black_hole_thermodynamics | **E2** | must_seal_E2 | **PAUSE-2 (R-P2):** `primary_modality = currency-shadow-price` (structural B.5 exemplar passes), `conditionality_flags = ["recognition-conditional"]` (secondary). Lands conditional on the **single frozen named import = QFT-in-curved-spacetime (Hawking thermal flux) + the first law of BH mechanics** (= E034); GR's Ξ≈0 is an OVER-READ. NOT a primary recognition-landing, NOT Jacobson (that is E022), NOT a derivation. |

*E3 anti-controls (computed tier must satisfy `must_not_seal_E1_or_E2`, i.e. land in {E3, E0}):*

| id | edge | `calibration_known_tier` | rule | what an E1/E2 here would mean |
|----|------|---------------------------|------|-------------------------------|
| E018 | quantum_mechanics → general_relativity | **E3** | must_not_seal_E1_or_E2 | "unify by deriving both from shared math" (primer trap #1) |
| E019 | standard_model → gauge-group-origin | **E3** | must_not_seal_E1_or_E2 | "derived" SU(3)×SU(2)×U(1) — smuggling |
| E020 | standard_model → fermion-generations | **E3** | must_not_seal_E1_or_E2 | "derived" generations / mass hierarchy — smuggling |
| E021 | general_relativity → cosmological-constant | **E3** | must_not_seal_E1_or_E2 | "predicted" Λ — tuning (retro R025 is synthetic) |

A wrong-tier proton mass (E1 "derived") is defined as the **worst** failure — a reductionist relapse.

---

## 3. Non-claims (binding)

- **No derivation across a layer boundary.** Edges are typed and audited, never reduced/derived/factored.
- **No empirical claim.** Every Ξ/RM/ID is a statement about a **declared finite toy model** on the
  closure-algebraic side; the bridge to a measured observable is a separate, **un-realized** assertion.
- **No constant is derived.** E0 edges are **deferred** to the Run-Target Manifest; the atlas specs the
  run, never executes it, never reports a number. "derive the proton mass" never appears.
- **Conditional results are reported separately.** E2 (recognition-conditional) edges are labeled
  "conditional under the named principle" and are **NEVER summed with E1**. E0 is never summed with E1
  either. The four tiers live on separate ledgers; even *within a single edge*, a `value_split`'s
  value_tier is never summed with its form_tier.
- **The up arrow is never run as a derivation.** Emergence is certified as a *gap* (non-factorization),
  never closed (gate E.8 + the §B.8 emittability table forbidding `emergence-up E1`).
- **Within-a-layer silence.** Where an "edge" is intra-layer, the rubric declares itself silent
  ("textbook in costume"), it does not manufacture a tier (primer §3; gate E.11 for the near-cases).
- **Using the map is not asserting the territory.** Casting physics through SBT does not presuppose SBT
  is "true"; it is an organizing instrument judged by what it usefully charts and audits.
- **Hard scope (never crossed):** no computationally-irreducible runs, no empirical predictions, no
  derivation of any constant. Cartography + triage, calibrated on the proton mass.

---

## 4. How the elasticity firewall works

Castings and tiers are **forced by audited tests**, never tunable to flatter SBT. The load-bearing parts:

1. **One descent oracle.** Ξ = `K_DD − K_DL·K_LL†·K_LD` (Schur complement), finite linear algebra on a
   declared finite toy model; `Ξ=0 ⟺ ker-containment ⟺ factorization` (the E1 sealing condition), taken
   verbatim from the adequacy paper. "Computable descent" has exactly one meaning.
2. **The deterministic procedure (§C.5).** Given frozen `(S, T, M, modality)` the same tier is produced
   every time: descent-test → recognition-search → run-search → else E3. No free tier knob.
3. **The single conservative ordering (review fix #4).** `E1 > E2 > E0 > E3`; **E3 is the unique
   conservative terminal**; every doubt demotes strictly toward E3. **E0 is NOT a doubt-haven** — sealing
   E0 requires the *positive* construction of a non-descending run-object (E.7).
4. **The `M`-tuning fence (review fix #5).** Gate **E.9** (refinement-stability: same verdict at two
   finite stages, still finite linear algebra, not a run) + gate **E.10** (second-annotator faithfulness
   before the hash) + the `no_faithful_M` E3 sub-reason (vacuous descent-test recorded distinctly).
5. **The up/down firewall.** Gate **E.8** (no E1 via an up computation; no emergence-by-iteration) + the
   §B.8 modality↔tier emittability table (rejects `shadow-down E0` and `emergence-up E1` at freeze).
6. **No-over-read + value-split (review fix #8).** Gate **E.3**: a descent's recovered answer must lie in
   `target.accepted_observables`; where the *form* descends (E1) but the *numbers* are run-only, a
   `value_split` carries the value_tier separately into the Run-Target Manifest, never summed.
7. **Near-intra-layer guard (gate E.11).** SM gauge-factor restrictions (E016, E017) and SR↔EM (E039) must
   pass the E.4 relabeling test explicitly; a within-layer restriction is marked "no SBT content" and
   REMOVED from the E1 count (no flattering-by-padding).
8. **The calibration freeze-gate predicate (review fix #7), now EXECUTABLE (external review fix R7):**
   > **FREEZE iff** *(a)* every `must_seal_*` calibration row's computed tier == its
   > `calibration_known_tier`, **AND** *(b)* every E3 anti-control's computed tier ∈ {E3, E0} (and any E0
   > carries a pre-frozen `run_target_stub` + logged E.7 interlock, O4), **AND** *(c)* every edge endpoint
   > resolves (registry §A.7), every `(modality, tier)` pair is emittable (§B.8), every modality string is
   > canonical, and every E1 from a candidate_substructure has that node `experimentally_established`,
   > **AND** *(d)* every casting-bearing card was frozen in full before any M/Ξ (gate E.12), **AND** *(e)*
   > every E1 count carries the O2 caveat.
   >
   > **This is no longer declarative.** It is enforced by the executable validator
   > **`validate_freeze_gate.mjs`**, which reads `CONTRACT.json` (the machine single source of truth — NOT
   > prose) and runs **12** collected checks: **C1** endpoint resolution, **C2** canonical-modality strings,
   > **C3** `(modality,tier)` emittability, **C4** calibration known-tier (+ equality blocker in scored
   > mode), **C5** anti-control tier rule (+ HARDENED O4/R5 E0 fence: an anti-control sealing E0 needs a
   > pre-frozen non-empty `run_target_stub` AND all four E.7 interlock booleans present and `true`, in scored
   > mode), **C6** value_split schema + no-summing, **C7** full-card freeze (every theory id + **all 9**
   > casting-bearing nodes have a complete frozen card — HARDENED per O1), **C8** `may_source_E1`, **C9 (R4)**
   > near-intra-layer seal gate (scored mode: a `near_intra_layer_check` row may not seal E1 unless
   > `near_intra_layer_result == "passed"`), **C10 (R3)** value_split reported-tier consistency (the headline
   > tier may not silently report a NON-reported value_split leg as the edge's closure), **C11 (R2)**
   > recognition-landing named_import (every `recognition-landing` row is in `affected_edges`, carries exactly
   > one non-empty non-menu `named_import`, and the affected_edges set equals the recognition-landing set),
   > **C12 (R6)** registered-null tally consistency + stale-prose guard (no frozen prose file may carry the
   > obsolete pre-v2 forty-four-edge count string). Every check *collects* its failures; the process exits **1** if
   > any failure is collected, **0** if clean — a missing artifact/field/endpoint is a FAILURE, not a skip.
   >
   > **How to run (the binding freeze gate):**
   > ```
   > node /home/repos/six-birds-papers/physics_atlas/prereg/validate_freeze_gate.mjs \
   >      --mode freeze --dir /home/repos/six-birds-papers/physics_atlas/prereg
   > ```
   > **Current result:** `FREEZE-GATE: PASS — all checks clean (mode=freeze)`, **exit 0**
   > (loaded: 21 theory stubs, 46 edges, 30 closure cards). `--mode scored` is the **next** phase's gate
   > and intentionally fails now (no `scored_tier` exists pre-scoring). `validate_freeze_gate.mjs` and
   > `CONTRACT.json` are in `SHA256SUMS`.

8a. **PAUSE-2 calibration remediation (review fix R-P2; `EXTERNAL_REVIEW_PAUSE2.md`).** The Pause-2
   external review returned **CALIBRATION-PASS on TIER** (all 9 blind tiers match known); the only block was
   a MODALITY-label ambiguity on **E005** (GR → black-hole-thermodynamics), resolved by **option (b):
   primary + secondary modality with a precedence rule**. Three frozen-prereg additions (no field renamed,
   no tier changed, no count changed):
   - **Modality precedence rule + secondary-modality schema** (`CONTRACT.json` `modality_precedence_rule`,
     `secondary_modality_schema`; rubric §B.7a). The existing per-edge **`modality` field IS the
     `primary_modality`** (the only modality used for `(modality,tier)` emittability and the registered-null
     tally). New OPTIONAL fields **`secondary_modalities`** / **`conditionality_flags`** carry residual
     annotations, never counted, never emittability-checked. **Rule:** a structural test that passes is
     PRIMARY; `recognition-landing` is primary only as a residual (no structural test passes); a structural
     E2 edge that still needs a named import records **`recognition-conditional` as a SECONDARY flag**.
     **E005** is the worked case: `primary_modality = currency-shadow-price` (the §B.5 "surface gravity as
     the price in BH thermodynamics" exemplar passes), tier **E2**, `conditionality_flags =
     ["recognition-conditional"]`; its frozen named import (QFT-in-curved-spacetime + first law of BH
     mechanics, semiclassical no-back-reaction = E034) is single, non-substitutable. E005 is NOT a primary
     recognition-landing; it stays in the E2 tally counted once, at currency-shadow-price/E2.
   - **NEW validator check C13** (`secondary_modality_schema.import_hygiene_parallel_check`): the named-import
     hygiene that **C11** enforces for primary recognition-landing rows applies **in parallel** to any E2
     edge carrying a secondary `recognition-conditional` flag (currently E005) — exactly one non-empty,
     single (non-menu), non-substitutable `named_import`. (C12 is the pre-existing R6 registered-null /
     stale-prose guard and is unchanged; the new check is **C13**.) Wiring C13 into
     `validate_freeze_gate.mjs` + re-running `SHA256SUMS` is delegated to the workflow agent (the
     `freeze_gate_predicate` adds clauses (h)=C13 and (i)=gate-policy).
   - **NORMALIZED-Ξ descent criterion** (`CONTRACT.json` `normalized_xi_criterion`; rubric §D.1.1, §C.1,
     §C.5 STEP 1, §E.9; digest §3c). E1 (clean descent) now requires the **NORMALIZED relative residual
     `ξ_rel = ‖Ξ‖/‖K_DD‖ → ~machine-zero STABLY`** across both refinements — NOT a small raw Ξ. E0/E3 =
     `ξ_rel` stays bounded away from zero with analytic control. **E001** is the worked "stable positive
     normalized residual + analytic control" example (raw Ξ grows 7.84e8→2.25e9 while `ξ_rel` 0.197→0.042
     stays positive); **E005** is the "numeric Ξ small is an OVER-READ when ħ/thermal predicates are
     imported" example. Both raw Ξ and `ξ_rel` are reported per refinement; refinement-stability (gate E.9)
     is on `ξ_rel`.

8b. **GATE POLICY (Pause-2, review fix R-P2; `CONTRACT.json` `gate_policy`).** Recorded here per the
   reviewer's adjudication:
   - **Calibration HARD-gates on TIER** (predicate clauses (a)/(b)): a per-row tier mismatch on a
     calibration control, or an anti-control leaving `{E3, E0}`, BLOCKS the freeze.
   - **Modality checks HARD-gate** on (i) canonical PRIMARY-modality strings, (ii) primary-modality/tier
     emittability, and (iii) recognition-import hygiene (**C11** primary recognition-landing rows + **C13**
     secondary recognition-conditional flags).
   - **A blind-vs-frozen PRIMARY-modality MISMATCH is ROUTED TO ADJUDICATION** (recorded, then the scored
     gate re-run), **NOT auto-failed** — modality is empirically less deterministic than tier on
     hard/faceted edges (two of nine Pause-2 blind edges, E005 and E018, disagreed on modality while getting
     tier right). The adjudication is logged, not silently force-aligned.

9. **The full-card-freeze HARD gate (gate E.12; external review fix R1).** No toy model `M` may be
   declared and no `Ξ`/`RM`/`ID` computed until the FULL §A closure-package card (every field: `Z, f,
   Σ_f, E, D, accepted_observables, lawful_layer_note, casting_justification, casting_alternatives,
   status`) is frozen and hashed in a hashed `closure_card_manifest.jsonl` for **every theory id AND every
   casting-bearing node** — *before any `M` declaration or `Ξ` computation*. The `provisional_Z/f/E` stubs
   in `theory_manifest.jsonl` are **NOT** sufficient for scoring; a stub-only casting at scoring time voids
   the incident edges and blocks the freeze. This converts the previously *declarative* card-first
   firewall into an *ordering-enforced* one (the external reviewer's central "still partly declarative"
   weakness). `closure_card_manifest.jsonl` is added to `SHA256SUMS`; the freeze validator asserts every
   casting-bearing card is complete and frozen, and that its hash predates the first `M`/`Ξ` of every
   incident edge.
10. **Established-status / `may_source_E1` rule (external review fix R6).** Every registered node carries a
   machine-readable `established_status ∈ {experimentally_established, not_established}`; a node may source
   an **E1** descent **only if** `experimentally_established`. (E035a/E040 source E1 only because
   `lattice-gauge-theory` / `many-body-quantum` are established; `string-theory` etc. are not and may not.)
11. **Recognition-landing canonical modality + canonical-string check (external review fix R2).**
   **`recognition_resolution.mode = "add_modality"`** (recorded in `CONTRACT.json`): R2 was resolved by
   **ADDING** `recognition-landing` as a first-class canonical modality (rubric §B.6a), **not** by
   retagging (`retag_map: {}`). The rationale: the recognition-landing edges span **both** arrow
   directions (up and down) and **different** underlying mechanisms (a failed descent, a top-down currency,
   a located emergence); a retag map would scatter them across descent/currency/emergence and **erase** the
   single fact that defines them — that the only thing that closes the edge is an imported named principle.
   The modality is **tier-locked to E2** (`modality_tier_compat["recognition-landing"] = ["E2"]`). The **8**
   frozen recognition-landing edges (E007, E022, E025, E026, E027a, **E028b**, E030, E033 =
   `CONTRACT.json` `recognition_resolution.affected_edges`; E028b is the O1 imported-Λ/dark-matter/measure
   split row) all carry modality `recognition-landing` / tier E2. Validator CHECK 2 rejects any modality
   string not among the **7 canonical modality strings**; CHECK 3 rejects any non-emittable
   `(modality,tier)` pair.
12. **Anti-control E0 fence (external review fix O4).** An E3 anti-control may pass via E0 **only if** its
   `run_target_stub` was frozen before scoring **and** the E.7 double-run interlock is logged; else demote
   to E3.

The intended bias: **flattering tiers are expensive, unflattering ones cheap.** Foreclosure-dominance is
the predicted result of the firewall working, not a failure. The machine-readable single source of truth
for every gate above is `CONTRACT.json` (the freeze validator reads it, not this prose).

---

## 5. The numbered list of review fixes applied (verdict: freeze-with-required-fixes; 8 required)

All **8** required fixes from `REVIEW_FIXES.md` are applied:

1. **(BLOCKER) Manifest join / id scheme** — all edges rewritten to canonical snake_case card ids; the
   6 renamed peers + EFT/Brownian reconciliations applied; frozen alias table added to BOTH notes files;
   freeze-time endpoint-resolution assertion added (rubric §A.7). *Verified: all 46 edges × 2 = 92
   endpoints resolve.*
2. **(BLOCKER) Non-peer nodes typed** — a frozen node registry with `node_kind ∈ {observable_readout,
   open_question, candidate_substructure}` (rubric §A.7, notes §2); per-edge `source_kind`/`target_kind`
   fields; rubric §C.5 STEP 0 rewritten to the node-kind-aware precondition (open_question ⇒ E0/E3 only;
   observable_readout inherits source casting; non-established candidate_substructure may not source E1);
   `effective-field-theory` promoted to the `rg_eft` card (E008/E009), orphan resolved.
3. **(REDUCTIONIST RELAPSE) E2 calibration anchor named import** — E005's named import frozen to ONE
   principle = **QFT-in-curved-spacetime + the first law of BH mechanics** (= E034, cited as the source);
   Jacobson removed from E005/§F and assigned only to E022 (the opposite-arrow edge); stated identically
   in `SCIENCE_DIGEST.md` §5, `TYPING_RUBRIC.md` §C.2/§F, and `edge_manifest.jsonl`; gate E.0 forbids
   substituting the named import at typing time; `arrow_direction` added (O2) to make the opposite arrows
   visible.
4. **(ELASTICITY HOLE) Conservative ordering** — the contradictory "E0 < E3 < E2 < E1" string deleted
   from §A; a single ordering `E1 > E2 > E0 > E3` with **E3 the unique conservative terminal** adopted in
   §E.5 and §C.5 (monotone fall-through); E0 explicitly NOT a doubt-haven; mirrored in `SCIENCE_DIGEST.md`.
5. **(ELASTICITY HOLE) Toy-model adequacy** — gate **E.9** (refinement-stability across two finite stages,
   in-scope), gate **E.10** (second-annotator `M`-faithfulness before the hash), and the `no_faithful_M`
   E3 sub-reason (vacuous-test E3 recorded distinctly from run-and-failed E3) added; §H "unresolved
   tension" rewritten as RESOLVED.
6. **(DETERMINISM / MODALITY HOLE) modality/tier consistency** — E035 split into E035a (shadow-down,
   E1-candidate) + E035b (emergence-up, E0); E027 split into E027a (recognition-landing, E2) + E027b
   (emergence-up, E0); a modality↔tier **emittability table** (§B.8) added and enforced at freeze; after
   the splits all four E0 rows are `emergence-up`.
7. **(CALIBRATION ADEQUACY) E3 anti-controls + wiring** — E018/E019/E020/E021 flagged
   `is_calibration:true` with `calibration_known_tier:"E3"` + `calibration_rule:"must_not_seal_E1_or_E2"`;
   `calibration_known_tier` added to all 5 existing controls; the freeze-gate predicate stated in §F and
   here (§4.8), to be enforced programmatically by the Assemble phase.
8. **(REDUCTIONISM / SCOPE) over-read / value-splits + near-intra-layer** — structured `value_split`
   fields carried by the 6 current rows **E004, E008, E029, E035a, E038, E041** (the old single E028
   value_split row no longer exists — see the O1 supersession note below), with the reported leg per
   `split_type` and the non-reported leg carried separately (Run-Target Manifest when E0, conditional
   ledger when E2), never summed; gate E.11 added requiring the E.4
   relabeling test be run and recorded for E016/E017 (and E039), with within-layer restrictions removed
   from the E1 count. *(Later superseded for E028: external-review O1 split the single E028
   `form_value_imported` value_split into two separate ledger rows — **E028a** shadow-down E1 (FLRW
   geometry/form) and **E028b** recognition-landing E2 (imported Λ/dark-matter/measure). The form/value
   separation is now the E028a-vs-E028b two-row split, on separate ledgers, never summed; the stale single
   `E028` value_split row was removed from `CONTRACT.json`. R5 also generalized the schema with `split_type`
   ∈ {form_value, form_value_imported, theorem_run}; E041 uses `theorem_run`.)*

**Optional improvements adopted:** O1 (`is_rg_eft_descent` flag — 6 E1 shadows are textbook RG/EFT), O2
(`arrow_direction`), O3 (rg_eft/EFT overlap resolved, folded into fix #2), O4 (registered-null framed as a
prediction, not a result — §7), O5 (`run_target_stub` for E031 turbulence and E041 confinement), O6
(fairness — a second genuine-emergence candidate beyond SPT/turbulence: the BCS/superconducting gap as a
run-generated order parameter, flagged at E040's Fermi-liquid breakdown).

**Assembler integrity note.** No fix introduced reductionist content. Every fix *adds* honesty (resolves
a join, types a node, freezes a named import, removes a tunable ordering, fences `M`, splits an
inconsistent row, wires a freeze-blocker, separates form from value). No fix required deriving, reducing,
or factoring across a layer boundary; none was flagged-instead-of-applied.

---

## 6. The Run-Target Manifest stub (E0 edges, DEFERRED — not run)

The E0 edges and run-only value-splits are flagged OUT and deferred. They are specced, never executed:

| run-target | source edge(s) | substrate | run-readout | out-of-sample validator | status |
|---|---|---|---|---|---|
| proton / hadron mass spectrum | E001, E035b | lattice QCD (gauge-field path integral on a grid) | hadron masses, Λ_QCD | masses not fit | **THE anchor**; DEFERRED |
| realized SPT invariant | E027b | a specific lattice Hamiltonian (DMRG / exact diag) | topological invariant value | invariant not fit | DEFERRED |
| turbulence inertial-range exponents | E031 | Navier–Stokes DNS at high Re | anomalous scaling exponents | exponents not fit | DEFERRED (regularity = separate E3) |
| confinement string tension / mass gap | E041 | lattice gauge theory | string tension / mass gap | spectrum not fit | DEFERRED (proof = separate E3, Clay) |
| value-split run-targets | E004, E008, E029, E038 | (the respective microscopic substrate) | transport coeffs / matched couplings / LECs / exponent values | not fit | DEFERRED; value_tier, never summed |

None is run in Stage 1. Hard scope stops here.

---

## 7. The registered null (PRE-AUDIT prediction, NOT the audited result)

**Source of truth: `CONTRACT.json` `registered_null`** (`n_edges` + `per_tier` + `tier_members`,
recomputed from the FINAL `edge_manifest.jsonl` `provisional_tier_guess`). The counts below MUST equal
that object; if this prose and the contract disagree, the contract governs and this prose is stale (a
freeze-blocking drift). The honest prediction is **foreclosure-dominance**: shadow-heavy (E1),
emergence-sparse (E0/E3), with E2 a substantial but **separate** conditional band. The **pre-audit guess**
over the **46** edges (the prior 44-edge state + the O1 E028→E028a/E028b split + the O3 hierarchy edge
E043; **E029 is E2, NOT E1**), recorded so the post-audit run cannot be tuned toward it:

- **E1 (computable descent): 19** — the shadow-heavy bulk (of which 5 E1 rows are flagged
  `is_rg_eft_descent` — exactly textbook RG/EFT moves: E008, E015, E035a, E038, E040; E028a is a further
  RG-type FLRW specialization — not novel SBT content). **Registered-null E1 caveat (external review fix
  O2, enforced in `CONTRACT.json` registered_null_caveat / registered_null.E1_caveat):** this count of 19
  INCLUDES the 3 near-intra-layer candidates (E016, E017, E039) still PENDING the gate E.4 / E.11
  relabeling test, carried as **E1-pending**, never counted as sealed E1; **the audited E1 set must REMOVE
  any that fails gate E.4** (within-a-layer restriction, no residual relation). Sealed-E1-eligible
  (non-pending) = **16**; E1-pending = **3**. An E1 count quoted without this caveat, or one that keeps an
  E.4-failing near-intra-layer row, is a flattering-by-padding violation.
- **E2 (recognition-conditional): 13** — named-import landings, reported separately, never summed
  (the **8** `recognition-landing` rows are exactly `CONTRACT.recognition_resolution.affected_edges` =
  **E007, E022, E025, E026, E027a, E028b, E030, E033** — each carrying a single non-menu `named_import`
  (R2; E007 = Gleason's theorem only, the envariance / decision-theoretic alternatives live only as
  `alternatives_not_used`); the other 5 E2 rows — E005, E023, E024, E029, E034 — land via a named import
  under duality/currency/shadow-down without the recognition-landing tag). **E029 is in this E2 set** via
  its imported-LEC value leg (`form_value_imported`, reported_tier=E2), not in the E1 set.
- **E3 (sharpened gap / foreclosure): 10** — located + typed, not closed (incl. the 4 E3 anti-controls
  E018–E021 and the O3 hierarchy gap E043).
- **E0 (run-only, deferred): 4** — E001, E027b, E031, E035b (all `emergence-up`).

**This is a prediction, not a finding.** It is the registered null shape (SBT working, not failing —
primer §9 #8). The rubric is capable of returning *any* shape; the firewall forbids steering toward this
one. If the audited run comes out emergence-heavy, that is a finding, not a bug. **E1 is never summed with
E2/E0/E3**; the counts are reported per tier, never pooled.

---

## 8. The value_split reported-tier rule (R3 — ONE coherent semantics)

`value_split.reported_tier` is **split-type-dependent** (`CONTRACT.value_split_schema.reported_tier_rule`):

| split_type | reported (headline) leg | rows | headline tier |
|---|---|---|---|
| `form_value` | `value_tier` is the reported leg, BUT the edge's own closure is the **form/structure descent**, so `edge_scored_tier` = the **E1** descent; the **E0** run-only value leg is a separate never-summed Run-Target entry | E004, E008, E035a, E038 | **E1** |
| `form_value_imported` | `value_tier` — the imported predictive leg IS the edge's closure | **E029** | **E2** (reported_tier = value_tier = edge_scored_tier = E2) |
| `theorem_run` | `form_tier` — the open-theorem status is the headline; the run-exhibited leg is a separate **E0** ledger entry | E041 | **E3** |

**E029 (ChPT) is the canonical `form_value_imported` row** and the only behavioural change from v3-prose:
the chiral symmetry skeleton descends from QCD (form_tier **E1**, recorded but NOT counted in the E1 null),
while the predictive content (f_π, the chiral condensate, the LECs) is the **imported** run-generated
low-energy constants from lattice QCD under a stated closure assumption (value_tier **E2**). So
`reported_tier = value_tier = edge_scored_tier = E2` (the strong `headline_tier_invariant`, validator C10,
no nuance exception). The two legs are **NEVER summed**; E029 contributes to the **E2** count, never E1.
This one semantics is now encoded identically across `CONTRACT.json`, `TYPING_RUBRIC.md`,
`SCIENCE_DIGEST.md`, `edge_manifest.jsonl`, `closure_card_manifest.jsonl`, and `registered_null`.

---

## 9. Mutation-test record (proving the hardened gate actually enforces)

The external reviewer mutation-tested the prior validator and found scoring-time seams. Each test below was
run by copying the loaded bundle (`CONTRACT.json`, `theory_manifest.jsonl`, `edge_manifest.jsonl`,
`closure_card_manifest.jsonl`, and the four prose files the C12 stale-guard reads) to a temp dir, mutating
the `edge_manifest.jsonl` copy, and running `validate_freeze_gate.mjs --mode scored` on the temp dir. The
scored baseline (every `scored_tier`/`scored_modality` = the provisional guess) already trips **C9** on the
three pending near-intra-layer rows (E016, E017, E039) — which is exactly the reviewer's mutation-test-1
finding; each further mutation adds its **own** targeted code on top of that clean baseline:

| # | Mutation | Required failure | Result (exit ≠ 0; codes) |
|---|---|---|---|
| (a) | every edge `scored_tier`=provisional, `scored_modality`=provisional | **C9** (E016/E017/E039 unresolved E1) | **FAIL** exit 1, `C9=3` |
| (b) | E018 → `scored_tier=E0`, `scored_modality=emergence-up`, arbitrary `run_target_stub`, E.7 interlock booleans absent | hardened **C5** | **FAIL** exit 1, `C5=4` (+ baseline C9) |
| (c) | blank (and, separately, menu-ify) a recognition row's (E025) `named_import` | **C11** | **FAIL** exit 1, `C11` on both the blanked and the menu variant (+ baseline C9) |
| (d) | E041 `scored_tier=E0` (the NON-reported run-exhibited leg ≠ frozen reported `edge_scored_tier=E3`) | **C10** | **FAIL** exit 1, `C10=1` (+ baseline C9) |

All four now **exit nonzero with the targeted check firing** — the seams are closed. (The harness is
`/tmp/mut_tests/run_mutations.py`; it is not part of the frozen bundle.)
