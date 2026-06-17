# CHANGELOG — PAUSE 2 (Calibration Gate) remediation

**Date:** 2026-06-04 · **Scope:** minimal, surgical — resolve the single E005 MODALITY-label
ambiguity flagged by the external Pause-2 review, and repair the SHA256SUMS integrity drift.
**Verdict source:** `prereg/EXTERNAL_REVIEW_PAUSE2.md`
(**CALIBRATION-PASS (tier)**; modality resolution = option (b): primary + secondary modality
with a precedence rule). **No tier changed; E1 is never summed with E2/E0; the 9 calibration
tiers are unchanged.**

---

## Verdict item -> exact change

### 1. E005 modality ambiguity -> option (b): primary + secondary modality with a PRECEDENCE rule

**Verdict (review §"REQUIRED FIX"):** *Each edge has exactly one `primary_modality` (the existing
`modality` field), used for `(modality,tier)` emittability and headline reporting; it may also
carry `secondary_modalities` / `conditionality_flags`. If a structural test passes
(duality / common-refinement / holonomy / currency / descent / emergence), that structural modality
is primary. `recognition-landing` is primary only when no structural modality closes the edge.
A structural E2 edge that still needs a named import records `recognition-conditional` as a
SECONDARY flag, not as primary `recognition-landing`.*

**Exact changes:**

- **`prereg/TYPING_RUBRIC.md` §B.7a (new subsection, review fix R-P2):** encodes the MODALITY
  PRECEDENCE RULE verbatim. It **does not rename** the existing per-edge `modality` field — that
  field **IS the `primary_modality`**. Adds the optional `secondary_modalities` /
  `conditionality_flags` arrays as *descriptive residual annotations only* (never used for
  emittability or for the registered-null tally). Includes the worked E005 exemplar:
  `primary_modality = currency-shadow-price` (B.5), tier `E2`,
  `conditionality_flags = ["recognition-conditional"]`, named import frozen to the E034
  construction. (Also §B.8 clarifies the emittability table reads the `primary_modality`;
  secondary flags do not enter it.)

- **`prereg/edge_manifest.jsonl` E005 row:** `provisional_modality_guess` = **`currency-shadow-price`**
  (the structural B.5 modality), `provisional_tier_guess` = **`E2`** (unchanged),
  `secondary_modalities` = `["recognition-conditional"]`,
  `conditionality_flags` = `["recognition-conditional"]`,
  `named_import` = "QFT in curved spacetime (Hawking thermal flux) + the first law of black-hole
  mechanics, conditional on the no-back-reaction (semiclassical) assumption",
  `named_import_source_edge` = `E034`. Notes document the §B.7a precedence application and that
  the secondary flag's single frozen import is enforced by the parallel check **C13**, not C11.

- **`prereg/CONTRACT.json`:** E005 remains EXCLUDED from
  `recognition_resolution.affected_edges` (still the 8 rows
  `E007, E022, E025, E026, E027a, E028b, E030, E033`) — correct, because E005's **primary**
  modality is structural (currency-shadow-price), not `recognition-landing`. The
  `(currency-shadow-price, E2)` pair is emittable per `modality_tier_compat`. The secondary
  recognition-conditional flag's import-hygiene is the parallel **C13** check (= C11 hygiene
  applied to the secondary flag).

- **Blind scored card `calibration/scored/E005.json`:** re-typed under the **updated** rubric
  precedence rule. `scored_modality` = **`currency-shadow-price`** (was the blind
  `recognition-landing`), `scored_tier` = **`E2`** (unchanged),
  `secondary_modalities` / `conditionality_flags` = `["recognition-conditional"]`. The
  re-typing is **deterministic**: exactly one structural test (currency/shadow-price, §B.5)
  passes, and §B.7a clause 1 selects it as primary — no free knob.

- **`calibration/scored_run/edge_manifest.jsonl`:** rebuilt from the 9 blind scored cards
  (E005 now `currency-shadow-price`) + provisional typing for the other 37 rows +
  `near_intra_layer_result = "passed"` for E016/E017/E039. The authoritative prereg artifacts
  (`CONTRACT.json`, `TYPING_RUBRIC.md`, `closure_card_manifest.jsonl`, `theory_manifest.jsonl`,
  `edge_manifest_notes.md`, `FREEZE_NOTES.md`, `SCIENCE_DIGEST.md`, `validate_freeze_gate.mjs`)
  were copied into `scored_run/`.

**Result:** the scored freeze-gate
(`node calibration/scored_run/validate_freeze_gate.mjs --mode scored --dir .../scored_run`)
now exits **0** (was exit 1 with two C11 failures on E005). Tier calibration unchanged: 9/9
match (E001=E0, E002/E003/E004=E1, E005=E2, E018/E019/E020/E021=E3).

### 2. Gate policy (review §"Adjudication"): tier-hard, modality adjudicated

**Verdict:** hard-gate **tier**; keep hard validation for canonical modality strings,
primary-modality/tier emittability, and recognition-import hygiene; route a blind-vs-frozen
**primary**-modality mismatch to **adjudication**, not auto-fail.

**Exact change:** the E005 mismatch was adjudicated (not silently force-aligned) and recorded
in `calibration/CALIBRATION_REPORT.md` (Pause-2 resolution section) and in the re-typed
`scored/E005.json` `pause2_retyping` block. The C11 hard check on the **primary** recognition
set is unchanged; the parallel C13 hygiene on the **secondary** flag is the mechanism for the
recognition-conditional import. (E018's blind `emergence-up` vs frozen `common-refinement`,
tier E3 either way, is likewise modality-adjudicated, not auto-failed — recorded in the
report.)

### 3. INTEGRITY (review §"INTEGRITY"): SHA256SUMS drift

**Verdict:** `SHA256SUMS` listed `closure_cards_part1.jsonl` and `closure_cards_part2.jsonl`,
which are absent from the review zip (excluded as intermediate scratch), so `sha256sum -c`
failed on those two (19/21 OK). They are redundant (concatenated into
`closure_card_manifest.jsonl`). **Delete them and regenerate `SHA256SUMS` over the authoritative
bundle.**

**Exact changes:**

- **Deleted** `prereg/closure_cards_part1.jsonl` (11 cards) and
  `prereg/closure_cards_part2.jsonl` (19 cards) — verified to be byte-redundant intermediates
  whose 30-card union is exactly `prereg/closure_card_manifest.jsonl` (same id set).

- **Regenerated** `prereg/SHA256SUMS` over the AUTHORITATIVE bundle ONLY, repo-root-relative
  paths: every remaining `prereg/*.md`, `prereg/*.jsonl`, `prereg/*.json`, `prereg/*.mjs`,
  plus the primer (`SIX_BIRDS_ANTI_REDUCTIONISM_PRIMER.md`) and the workflow generators
  (`physics_atlas/wf_*.mjs`). The two deleted intermediates are no longer listed.

- **Verified:** `sha256sum -c prereg/SHA256SUMS` run from the repo root reports **all OK**.

### 4. Ξ reporting (review §"OTHER FINDINGS") — already encoded; no new change

The Pause-2 raw-vs-normalized Ξ finding (E001 raw Ξ grows 7.84e8 -> 2.25e9 while the
normalized residual `ξ_rel` shrinks 0.197 -> 0.042 and stays positive) was already encoded in
`TYPING_RUBRIC.md §D.1.1` (review fix R-P2) and the worked E001/E005 examples. No further change
in this remediation; recorded here for completeness.

---

## Gate verification after remediation

| Gate | Command | Result |
|------|---------|--------|
| Scored | `node calibration/scored_run/validate_freeze_gate.mjs --mode scored --dir .../scored_run` | **PASS (exit 0)** |
| Freeze | `node prereg/validate_freeze_gate.mjs --mode freeze --dir .../prereg` | **PASS (exit 0)** |
| Mutation seams | `python3 physics_atlas/verify_mutation_tests.py` | **all 5 seams still FAIL correctly** (C9, C5, C11 blank, C11 menu, C10) |
| Integrity | `sha256sum -c prereg/SHA256SUMS` (from repo root) | **all OK** |

**calibration_pass = (all 9 tiers still match known) AND scored_pass AND e005_deterministic = TRUE.**

---

*Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>*
