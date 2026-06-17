# CHANGELOG — PAUSE 1 v4 (external re-review remediation, hardened freeze-gate)

**Date:** 2026-06-04 · **Author:** assembler (Stage 1, Pause 1, round v4) ·
**Input contract:** `EXTERNAL_REVIEW_v3.md` (re-review of the remediated bundle; APPROVE-WITH-REQUIRED-CHANGES;
**R1–R6 required, O1–O2 optional**).
**Result:** the hardened executable freeze-gate validator **passes** in `--mode freeze` (exit 0); the
reviewer's **four mutation tests now FAIL as required** in `--mode scored`. 21 theory stubs, 30 closure
cards (21 theory + 9 candidate_substructure nodes), 46 typed edges.

> **Scope discipline (unchanged).** No reductionist content was introduced by any item below. Every change
> *adds enforcement or removes drift* — it wires a machine-check, makes `CONTRACT.json` the single source of
> truth, or aligns one stale prose row to the resolved semantics. **No irreducible runs, no empirical claims,
> no constant derivation; E1 is never summed with E2/E0/E3; the foreclosure-dominant null is the prediction.**
> The up/down asymmetry (MAP and AUDIT, never derive across a layer boundary) is preserved throughout.

The core theme of the re-review: make `CONTRACT.json` the **single source of truth** and make
`validate_freeze_gate.mjs` **actually ENFORCE** every predicate the contract/rubric claim — the reviewer
mutation-tested the prior validator and found scoring-time seams. The validator now carries **four new
hardened checks beyond the original eight (C9–C12)**, and the `value_split` reported-tier semantics (R3) is
encoded as **one** coherent rule across every file. This file maps each item to the **exact** files/ids.

---

## R-item disposition (R1–R6 required; O1–O2 optional)

### R1 — residual blunt QCD slogan → **applied**
The precise wording is in place in both flagged files:
- `SIX_BIRDS_ANTI_REDUCTIONISM_PRIMER.md` §5 (L117–123): "QCD has **no free proton/hadron MASS parameter**;
  quark masses and coupling/scale are fixed independently under the declared physical-quark-mass lattice-QCD
  protocol (scale set by one hadronic input; running by dimensional transmutation / Λ_QCD); the proton-mass /
  hadron-spectrum readout is out-of-sample and not fitted."
- `theory_manifest_notes.md` L89–93: same precise wording ("no free **proton/hadron MASS parameter** … fixed
  independently … out-of-sample and not fitted").
- `FREEZE_NOTES.md` §2 (E001 calibration row) carries the same corrected R8 wording.
The blunt "QCD has no free mass parameter" slogan no longer appears. Files re-hashed in `SHA256SUMS`.

### R2 — contract/rubric drift vs recognition rows → **applied** (+ enforced by **C11**)
- `CONTRACT.recognition_resolution.affected_edges` enumerates all **8** recognition rows
  (`E007, E022, E025, E026, E027a, E028b, E030, E033`) — E028b is included.
- `CONTRACT.recognition_resolution.affected_edges_named_imports.E007` is the **single frozen Gleason import**
  ("Gleason's theorem … the SINGLE frozen import"); the envariance / decision-theoretic alternatives are NOT
  in the contract menu (they live only as `alternatives_not_used` on the edge row).
- **Validator C11** (already in `validate_freeze_gate.mjs`) enforces: every `recognition-landing` row is in
  `affected_edges`, carries **exactly one** non-empty `named_import`, that import is **not a menu**
  (no "or"-alternation, no "to be frozen/choose one/tbd", no 3+-way "/"), the contract's frozen import is
  also non-menu, AND `affected_edges` is **set-equal** to the recognition-landing set (a stale enumeration is
  rejected). Mutation test (c) confirms a blanked **or** menu-ified `named_import` now FAILS C11.
- `FREEZE_NOTES.md` §7 now enumerates the 8 rows explicitly.

### R3 — value_split semantics internally inconsistent → **applied** (ONE semantics; + enforced by **C10**)
The drift was: `edge_manifest.jsonl` + `closure_card_manifest.jsonl` had already adopted E029 =
`form_value_imported` / `value_tier=E2` / `reported_tier=E2`, but `CONTRACT.json` still froze the old E029 =
`form_value` / `value_tier=E0` (and claimed "no current edge instantiates `form_value_imported`"). I chose
**the cleaner single semantics already in the manifest+card** (it satisfies the *strong*
`headline_tier_invariant`: `reported_tier = value_tier = edge_scored_tier = E2`, no nuance exception) and
propagated it to the contract:
- `CONTRACT.value_split_schema.rows_carrying_value_split.E029` → `form_tier=E1, value_tier=E2,
  split_type=form_value_imported, reported_tier=E2, edge_scored_tier=E2`.
- `CONTRACT.value_split_schema` prose (`rationale_form_value`, `headline_tier_invariant`,
  `rows_carrying_value_split_note`, `edges_agent_action`, `E028_supersession_note`) updated: E029 is now the
  canonical `form_value_imported` instantiation (the old "no current edge instantiates it" claim is corrected).
- `TYPING_RUBRIC.md` §E.3 split-type list + R3 consequence paragraph: E029 removed from the `form_value` row
  list and named as the `form_value_imported` canonical row; the stale "no current edge instantiates this"
  text replaced.
- `SCIENCE_DIGEST.md`: the split-type bullet relabelled E028→**E029** for `form_value_imported`, and the
  stale flat "**`form_tier` is the reported tier**" replaced with the split-type-dependent R3 rule.
- `edge_manifest_notes.md`: the "E029 (`form_value`)" line corrected to "E029 (`form_value_imported`) reports
  **E2** (reported_tier = value_tier = edge_scored_tier = E2)".
- `registered_null` already places E029 in the **E2** set (count 13) and excludes its form-descends-E1 leg
  from the E1 null — consistent with the resolved semantics; no count changed.
- **Validator C10** enforces a row's headline tier may not silently report a NON-reported value_split leg as
  its closure (it must equal the contract's frozen per-row `edge_scored_tier`; for `theorem_run` it must equal
  the reported `form_tier`). Mutation test (d) confirms `E041 scored_tier=E0` (the non-reported run leg) now
  FAILS C10.

### R4 — O2 not actually enforced (mutation seam) → **applied** (enforced by **C9**)
- `CONTRACT.near_intra_layer_schema` carries machine fields `near_intra_layer_check` (boolean) +
  `near_intra_layer_result` (enum `pending|passed|failed`); E016/E017/E039 are `pending`.
- **Validator C9** (scored mode): a `near_intra_layer_check` row sealed `scored_tier=E1` FAILS unless
  `near_intra_layer_result == "passed"`. A flagged row is recognised by a boolean `true` OR the legacy
  non-empty `PENDING_E4` string (never a silent skip). Mutation test (a) — every `scored_tier`=provisional —
  confirms E016/E017/E039 now FAIL C9 (they were the seam the reviewer found passing).
- `registered_null.E1_caveat` / `registered_null_caveat` carry the O2 caveat (E1=19 includes 3 pending;
  sealed-eligible = 16).

### R5 — O4 only partially enforced (mutation seam) → **applied** (hardened **C5**)
- `CONTRACT.anti_control_rules.e7_interlock_schema.machine_fields` defines the four booleans
  `descent_test_logged_negative`, `recognition_search_logged_negative`, `non_descending_run_object_exhibited`,
  `run_target_stub_frozen_pre_scoring`; the rule: an anti-control may seal `E0` **only if** a non-empty
  pre-frozen `run_target_stub` is present **AND all four booleans are present and `true`**.
- **Validator C5** (hardened): in scored mode an anti-control sealing E0 with an absent/empty `run_target_stub`
  **or** any missing/false interlock boolean is a conservative-default FAILURE (demote to E3). The interlock
  key set is the **union** of the contract schema keys and a frozen fallback, so the fence cannot be silently
  disabled by editing the schema. Mutation test (b) — E018→E0 with an arbitrary stub but no E.7 log — confirms
  it now FAILS C5 (4 failures, one per absent boolean).

### R6 — stale frozen prose (firewall-relevant) → **applied** (+ enforced by **C12**)
- All frozen-prose edge counts are at the **46-edge** v3 state; E028 is the two-row E028a/E028b split (no
  single E028 value-split row); E1/E2/E0/E3 = 19/13/4/10 per the R3 resolution.
- **Validator C12** (a) cross-checks any frozen `registered_null` tier tally against the actual
  `edge_manifest.jsonl` headline-tier counts and (b) scans the four frozen prose files
  (`edge_manifest_notes.md`, `SCIENCE_DIGEST.md`, `TYPING_RUBRIC.md`, `FREEZE_NOTES.md`) for the obsolete
  pre-v2 forty-four-edge count string — any occurrence FAILS the freeze. (Confirmed: zero occurrences remain;
  the C12 self-description in FREEZE_NOTES is phrased to avoid the literal so the guard does not self-trip.)
- `FREEZE_NOTES.md` updated: v4 banner, the C9–C12 check descriptions (§4 item 8), the value_split
  reported-tier rule table (new §8), the corrected registered null (§7), the mutation-test record (new §9).

### O1 — tighten C7 to require full cards for all 9 candidate_substructure nodes → **applied**
`validate_freeze_gate.mjs` C7 builds `mustHaveCard` from every theory id **plus every** registered
`candidate_substructure` endpoint (source **or** target) **plus** every node in
`CONTRACT.node_established_rule.frozen_statuses`. All 9 nodes
(`chiral-perturbation-theory, classical-probability, conformal-field-theory, decoherence-pointer-basis,
fermi-liquid-theory, lattice-gauge-theory, many-body-quantum, quantum-field-theory-curved, string-theory`)
have full §A cards; deleting a target-only card would fail C7.

### O2 — normalize `accepted_observables` to a list everywhere → **partial**
The **authoritative frozen objects the validator reads** — the 30 closure cards in
`closure_card_manifest.jsonl` — all carry `accepted_observables` as a **list** (verified: qcd,
chiral-perturbation-theory, classical-probability, and every other card). The non-load-bearing
`theory_manifest.jsonl` **stubs** still carry the field as a string; these stubs are the cards' short form and
are not consumed by the freeze gate. Left as-is to avoid touching non-load-bearing artifacts under freeze;
the normalization that mattered for any machine path is done.

---

## Mutation-test record (the proof the hardened gate works)

Harness: copy the loaded bundle (`CONTRACT.json`, `theory_manifest.jsonl`, `edge_manifest.jsonl`,
`closure_card_manifest.jsonl` + the four prose files the C12 guard reads) to a temp dir, mutate the
`edge_manifest.jsonl` copy, run `validate_freeze_gate.mjs --mode scored` on the temp dir, confirm a nonzero
exit with the targeted check firing. The scored baseline (`scored_*` = the provisional guess) already trips
**C9** on the three pending near-intra-layer rows (this IS reviewer mutation-test 1); each further mutation
adds its own targeted code on top of that clean baseline.

| # | Mutation | Required | Now fails as required |
|---|---|---|---|
| (a) | every `scored_tier`=provisional, `scored_modality`=provisional | **C9** | **YES** — exit 1, `C9=3` (E016/E017/E039 unresolved E1) |
| (b) | E018 → `scored_tier=E0`, `scored_modality=emergence-up`, arbitrary `run_target_stub`, E.7 booleans absent | hardened **C5** | **YES** — exit 1, `C5=4` (one per missing interlock boolean) |
| (c) | blank a recognition row's (E025) `named_import`; also tested the menu variant | **C11** | **YES** — exit 1, `C11` on both the blanked and the menu variant |
| (d) | E041 `scored_tier=E0` (the NON-reported run-exhibited leg ≠ frozen reported `edge_scored_tier=E3`) | **C10** | **YES** — exit 1, `C10=1` |

All four exit nonzero with the targeted check firing. (Harness: `/tmp/mut_tests/run_mutations.py`; not part of
the frozen bundle.)

---

## The registered null (unchanged, corrected counts)

> **shadow-heavy (E1-dominant) / emergence-sparse (E0 + foreclosed E3), with E2 a substantial but separate
> conditional band — foreclosure-dominance, the framework working not failing (primer §9 #8). E1 is NEVER
> summed with E2/E0/E3.** Over 46 edges: **E1=19** (of which 3 — E016/E017/E039 — are E1-pending, never sealed
> until gate E.4 passes; sealed-eligible = 16), **E2=13** (E029 in this set via its imported-LEC value leg),
> **E0=4**, **E3=10**.

(Source of truth: `CONTRACT.json` `registered_null`. Pre-audit prediction, NOT the audited verdict; the scored
run must not be tuned toward it.)
