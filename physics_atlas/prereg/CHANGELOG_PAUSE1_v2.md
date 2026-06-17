# CHANGELOG — PAUSE 1 v2 (external-review remediation, freeze-gate assembly)

**Date:** 2026-06-04 · **Author:** assembler (Stage 1, Pause 1) ·
**Input contract:** `EXTERNAL_REVIEW_v1.md` (APPROVE-WITH-REQUIRED-CHANGES; R1–R8 required, O1–O4 optional).
**Result:** the executable freeze-gate validator passes in `--mode freeze` (exit 0). 21 theory cards, 30
closure cards (21 theory + 9 candidate_substructure nodes), 46 typed edges.

> **Scope discipline (unchanged).** No reductionist content was introduced by any item below. Every change
> *adds* honesty — freezes a card, wires a machine-check, fixes an endpoint direction, separates form from
> value, names an import — and none derives/reduces/factors across a layer boundary. The up/down asymmetry
> and the no-summing rule are preserved throughout. Foreclosure-dominance remains the registered null.

This file maps each review item to the **exact** files and ids changed. The bulk of R1–R8 / O1–O4 had
already been encoded into the frozen bundle (CONTRACT.json, TYPING_RUBRIC.md §A.7.1/§B.6a/§B.8/§E.12,
the split edge rows, the closure-card parts) by the edges/rubric agents; the assembler's job here was to
**assemble the full-card manifest, build/prove the executable gate, and close the residual machine-check
and provenance gaps**. Each row states the disposition (applied | partial | deferred) and what the
*assembler* did versus what was already encoded.

---

## REQUIRED CHANGES

### R1 — Freeze full closure-package cards (full §A schema, before any M/Ξ). — **applied**
- **What was already encoded:** the full §A cards live in `closure_cards_part1.jsonl` (11 cards) and
  `closure_cards_part2.jsonl` (19 cards), each carrying `Z, f, Sigma_f, E, D, accepted_observables,
  lawful_layer_note, casting_justification, casting_alternatives, status:"frozen"`; gate **E.12** is in
  `TYPING_RUBRIC.md §A` intro/§E.12 and `CONTRACT.json full_card_freeze_rule`.
- **Assembler action:** concatenated and de-duplicated (by `id`, first-wins) the two parts into the hashed
  **`closure_card_manifest.jsonl`** (30 cards). Verified every one of the 21 `theory_manifest.jsonl` ids
  has a full card, plus the 9 casting-bearing `candidate_substructure` nodes
  (`conformal-field-theory`, `string-theory`, `lattice-gauge-theory`, `quantum-field-theory-curved`,
  `chiral-perturbation-theory`, `fermi-liquid-theory`, `many-body-quantum`, `classical-probability`,
  `decoherence-pointer-basis`). The validator's CHECK 7 enforces a complete frozen card for every theory
  id and every candidate_substructure that **sources** an edge; CHECK 7 passes.
- **Files:** `closure_card_manifest.jsonl` (new), `SHA256SUMS` (added).

### R2 — `recognition-landing` is not a canonical modality. — **applied** (resolution = add_modality)
- **Resolution:** `CONTRACT.json recognition_resolution.mode = "add_modality"` — `recognition-landing` was
  **added as a first-class canonical modality** (rubric §B.6a), NOT retagged (`retag_map: {}`). Rationale
  recorded in the contract: the affected edges span both arrow directions and different mechanisms; a
  retag would scatter them and erase the single defining fact (the edge closes only by a named import).
- **Tier-lock:** `modality_tier_compat["recognition-landing"] = ["E2"]` — the only emittable tier.
- **Canonical-string check:** validator CHECK 2 rejects any modality string not in
  `CONTRACT.canonical_modalities` (the 7 strings); CHECK 3 rejects any non-emittable `(modality,tier)`.
- **Affected edges (carry modality `recognition-landing`, tier E2):** E007, E022, E025, E026, E027a,
  E030, E033 (the 7 frozen) **plus** E028b (the O1-split imported-content row). All pass CHECK 2/CHECK 3.
- **Files:** `CONTRACT.json` (canonical_modalities, modality_tier_compat, recognition_resolution),
  `TYPING_RUBRIC.md §B.6a/§B.8`, `edge_manifest.jsonl` (the 8 rows).

### R3 — E022 endpoints reversed (Jacobson is thermo → GR, arrow up). — **applied**
- E022 in `edge_manifest.jsonl` carries `source_theory_id: "thermodynamics"`,
  `target_theory_id: "general_relativity"`, `arrow_direction: "up"`, modality `recognition-landing`, tier
  E2, with `named_import` = Jacobson's equation of state (Clausius dQ=TdS + Bekenstein-Hawking S=A/4 +
  local Rindler thermality). The note states explicitly that E022 is the **opposite arrow** to E005 and
  that conflating them is the route-direction error the up/down asymmetry forbids.
- **Files:** `edge_manifest.jsonl` (E022); cross-referenced in `CONTRACT.json calibration_rules E005`
  ("Jacobson is NOT this edge (that is E022)").

### R4 — E007 (Born rule) import menu → ONE frozen named import. — **applied**
- E007 freezes a **single** `named_import` = "Gleason's theorem" under an explicit `closure_assumption`
  (noncontextuality + dim(H) ≥ 3). The former menu (envariance, decision-theoretic) is demoted to an
  `alternatives_not_used` field documenting only that the recognition-search returns a non-empty named set;
  the note states they may **not** be substituted at typing time (gate E.0 frozen-named-import clause).
- **Files:** `edge_manifest.jsonl` (E007); `CONTRACT.json recognition_resolution.affected_edges_named_imports.E007`
  flags the one-to-be-frozen choice.

### R5 — `value_split` schema overloaded → generalized with `split_type`. — **applied**
- `CONTRACT.json value_split_schema` carries `split_type_enum: ["form_value", "form_value_imported",
  "theorem_run"]` with `form_tier_enum`/`value_tier_enum` each {E1,E2,E0,E3}. Validator CHECK 6 enforces a
  valid `split_type`, valid form/value tiers, a `value_node`, and the no-summing invariant (rejects
  form_tier=E1 ∧ value_tier=E1), and cross-checks each present split against the frozen per-row contract.
- **E041** uses `split_type: "theorem_run"` (`form_tier: E3` open Yang-Mills/Clay theorem vs
  `value_tier: E0` lattice-exhibited string tension) — the open-theorem-vs-run distinction R5 called out.
- **Assembler action (provenance fix):** the pre-O1 single-row `E028` `form_value_imported` value_split
  entry in `CONTRACT.json` was **stale** (O1 had already split E028 into two separate ledger rows
  E028a/E028b in the manifest, so no edge with id `E028` exists). Removed the stale `E028` row from
  `value_split_schema.rows_carrying_value_split` and added an `E028_supersession_note` documenting that the
  form/value separation is now carried as the E028a (E1) vs E028b (E2) two-row split, on separate ledgers,
  never summed. The `form_value_imported` enum member is retained for general use. This makes CONTRACT and
  the manifest consistent (CHECK 6 has no `E028` row to require a now-nonexistent edge to carry).
- **Files:** `CONTRACT.json value_split_schema` (removed stale E028 row, added supersession note);
  `edge_manifest.jsonl` (E004, E008, E029, E035a, E038, E041 carry value_splits; E028a/E028b carry none).

### R6 — `candidate_substructure` sourcing E1 needs `established_status`. — **applied**
- `CONTRACT.json node_established_rule.frozen_statuses` freezes an `established_status` for every node;
  `may_source_E1_rule` permits an E1 source only if `experimentally_established`. The two E1-sourcing
  candidate_substructure nodes are established and justified per node: `lattice-gauge-theory` (sources
  E035a) and `many-body-quantum` (sources E040). `string-theory`, `conformal-field-theory`,
  `quantum-field-theory-curved`, `decoherence-pointer-basis`, `classical-probability` are
  `not_established` and source only E2/E3 (E037, E023, E034, E026, E007).
- **Enforcement:** validator CHECK 8 rejects any E1 sourced from a candidate_substructure whose frozen
  status ≠ `experimentally_established`; CHECK 8 passes.
- **Files:** `CONTRACT.json node_established_rule`, `TYPING_RUBRIC.md §A.7.1`, the node cards in
  `closure_card_manifest.jsonl`, `edge_manifest.jsonl` (E035a/E040 sources).

### R7 — Calibration gate must be executable, not declarative. — **applied**
- The executable validator **`validate_freeze_gate.mjs`** (Node built-ins only) reads `CONTRACT.json` as
  the single source of truth and enforces 8 machine checks: C1 endpoint resolution, C2 canonical-modality
  strings, C3 `(modality,tier)` emittability, C4 calibration known-tier/equality, C5 anti-control
  tier-rule, C6 value_split schema + no-summing, C7 full-card freeze, C8 `may_source_E1`. Every check
  **collects** failures and the process exits nonzero if any fail (no skips, no silent passes).
- **Run command (the binding freeze gate):**
  `node /home/repos/six-birds-papers/physics_atlas/prereg/validate_freeze_gate.mjs --mode freeze --dir /home/repos/six-birds-papers/physics_atlas/prereg`
  → `FREEZE-GATE: PASS — all checks clean (mode=freeze)`, exit 0.
- **Assembler action:** added `validate_freeze_gate.mjs` and `CONTRACT.json` to `SHA256SUMS`; closed the
  last machine-check gap (see R-residual below) that previously made the anti-control rule non-emittable.
- **Files:** `validate_freeze_gate.mjs`, `CONTRACT.json`, `SHA256SUMS`.

### R8 — QCD calibration slogan too blunt. — **applied**
- The blunt "QCD has no free mass parameter" is replaced everywhere with the precise wording:
  **physical-quark-mass lattice QCD** (not chiral-limit, not pure-gauge); **no free proton/hadron MASS
  parameter**; quark masses and coupling/scale **fixed independently** under the declared lattice-QCD
  protocol (overall scale set by **one hadronic input**, running by **dimensional transmutation /
  Λ_QCD**); the **proton-mass / hadron-spectrum readout is out-of-sample and NOT fitted**. Stated
  identically in `theory_manifest.jsonl` (qcd note), `closure_card_manifest.jsonl` (qcd card `D` +
  casting_justification), `edge_manifest.jsonl` (E001 known_physics_relation + notes), and
  `CONTRACT.json calibration_rules E001.spec`.
- **Files:** `theory_manifest.jsonl`, `closure_card_manifest.jsonl`, `edge_manifest.jsonl` (E001),
  `CONTRACT.json` (E001).

---

## R-RESIDUAL (assembler machine-check fix needed to make R7's gate actually pass)

The validator's CHECK 5 (the R7/O4 anti-control machine-check) requires each anti-control edge to carry an
explicit boolean field `must_not_seal_E1_or_E2: true` (and `calibration_known_tier: "E3"`). The edges
carried the **string** `calibration_rule: "must_not_seal_E1_or_E2"` but not the **boolean** field the
machine-check reads, so CHECK 5 failed for E018–E021. This was the only thing blocking the freeze gate.

- **Fix (targeted, non-weakening):** added `"must_not_seal_E1_or_E2": true` to E018, E019, E020, E021 in
  `edge_manifest.jsonl` (the boolean the validator's CHECK 5 + CONTRACT `anti_control_rules` read).
  `calibration_known_tier: "E3"` was already present. No validator code was changed; the contract was not
  weakened. After this fix the freeze gate passes clean.
- **Files:** `edge_manifest.jsonl` (E018, E019, E020, E021).

---

## OPTIONAL IMPROVEMENTS

### O1 — Split E028 into geometry-descent (E1) + imported-content (E2). — **applied**
- `edge_manifest.jsonl` carries **E028a** (`general_relativity → lambda_cdm`, shadow-down, **E1**, the bare
  FLRW geometry/Friedmann form) and **E028b** (`general_relativity → lambda_cdm`, recognition-landing,
  **E2**, the imported Λ + dark-matter + measure content). The contradictory `shadow-down + arrow:up + E2`
  triple on the old single E028 is gone; the two rows sit on separate ledgers and are never summed.
- **Assembler provenance fix:** removed the now-superseded single `E028` value_split row from
  `CONTRACT.json` (see R5) so the contract matches the split manifest.
- **Files:** `edge_manifest.jsonl` (E028a, E028b), `CONTRACT.json value_split_schema`.

### O2 — Registered-null caveat (audited E1 must remove gate-E.4 failures). — **applied**
- `CONTRACT.json registered_null_caveat` + `full_card_freeze_rule.registered_null_caveat` require any E1
  count to carry the caveat and forbid counting an unresolved near-intra-layer row (E016, E017, E039) as a
  sealed E1. Restated in `FREEZE_NOTES.md §7`.
- **Files:** `CONTRACT.json`, `FREEZE_NOTES.md`.

### O3 — Separate Higgs/electroweak-naturalness hierarchy edge. — **applied**
- `edge_manifest.jsonl` carries **E043** (`electroweak_theory → electroweak-hierarchy`, open_question
  target, emergence-up, **E3**) as a **distinct** scalar-sector naturalness gap, kept separate from the
  fermion-generations gap E020 so "mass hierarchy" cannot be read as covering only fermion generations.
- **Files:** `edge_manifest.jsonl` (E043).

### O4 — Tighten the `{E3,E0}` anti-control rule. — **applied**
- `CONTRACT.json anti_control_rules.must_not_seal_E1_or_E2` allows an anti-control to pass via E0 **only**
  if its `run_target_stub` was frozen before scoring **and** the E.7 double-run interlock is logged; else
  it is demoted to E3. The validator's CHECK 5 (scored mode) enforces: anti-control sealed E0 without a
  pre-frozen `run_target_stub` fails. (In freeze mode the anti-controls assert `calibration_known_tier=E3`
  and the boolean rule; the E0 fence binds at scoring.)
- **Files:** `CONTRACT.json anti_control_rules`, `TYPING_RUBRIC.md §E.7`, `edge_manifest.jsonl`
  (E018–E021).

---

## Validator result (the proof)

```
$ node validate_freeze_gate.mjs --mode freeze --dir <prereg>
loaded: 21 theory stub(s), 46 edge(s), 30 closure card(s)
FREEZE-GATE: PASS — all checks clean (mode=freeze)
exit 0
```

`--mode scored` intentionally fails at this stage: it evaluates `scored_tier`, which does **not** yet
exist (Pause 1 is the **pre-scoring** freeze). The scored-mode failures (C3 "tier is empty", C4 "no
scored_tier", C5 "tier undefined") are the correct signal that scoring has not been performed — they are
the gate that will bind the **next** phase, not this one.

**Provisional (registered-null) distribution over the 46 edges:** E1 = 19, E2 = 13, E3 = 10, E0 = 4 —
shadow-heavy, emergence-sparse: the predicted foreclosure-dominant null (SBT working, not failing). The
E1 count carries the O2 caveat (E016/E017/E039 pending gate E.4). Tiers are reported per ledger, never
summed.
