# External Review v3 (re-review of remediated bundle) — VERDICT + Required Changes

**Date:** 2026-06-04 · **Reviewer:** independent external agent (zip-only) · **Verdict:** **APPROVE-WITH-REQUIRED-CHANGES**
· **Integrity:** `sha256sum -c` OK on all 16 files; `validate_freeze_gate.mjs --mode freeze` PASS (exit 0); `--mode scored` fails as expected.

> **Reviewer summary:** v3 is integrity-clean and materially stronger. Most v1 fixes are genuinely present (full
> cards, E022, E007 Gleason, node may_source_E1, E028 split, E043). **The dangerous remaining weakness is
> contract/prose/validator DRIFT** — several hashed prose files still describe the v2/44-edge state, and the
> validator does not enforce all predicates the contract/rubric claim. The reviewer **mutation-tested** the
> validator and found real scoring-time seams.

## REQUIRED CHANGES

- **R1 — residual blunt QCD slogan.** R8 not fully propagated: `SIX_BIRDS_ANTI_REDUCTIONISM_PRIMER.md` (§5,
  L117-120) and `theory_manifest_notes.md` (L89-91) still say "QCD has no free mass parameter." → Replace with the
  precise wording already in the qcd row: "no free **proton/hadron mass** parameter; quark masses + coupling/scale
  fixed independently under the physical-quark-mass lattice-QCD protocol; spectrum readout out-of-sample, not
  fitted." Re-hash.
- **R2 — contract/rubric drift vs edge rows (R2/R4 incomplete in the contract).** `CONTRACT.recognition_resolution.affected_edges`
  lists only 7 recognition rows, omitting **E028b** (there are 8). The contract still describes E007's import as a
  **menu** ("Gleason / envariance / decision-theoretic") though the row freezes Gleason only. → Enumerate all 8
  recognition rows (or avoid a hard-coded count); replace the E007 contract menu with the single frozen Gleason
  import. **Add a validator check**: every `recognition-landing` row is in the contract, has exactly one non-empty
  `named_import`, and the contract import is not a menu.
- **R3 — value_split semantics internally inconsistent.** Contract says `reported_tier = form_tier`; but E029
  (ChPT) has `form_tier=E1` yet the row + ChPT card say the **whole edge lands E2** (predictive content needs
  imported run-generated LECs). → Choose ONE semantics and encode it across CONTRACT, TYPING_RUBRIC, SCIENCE_DIGEST,
  edge_manifest, closure_card_manifest, and the registered-null counts. **Add a validator check** that a row's tier
  and its `value_split.reported_tier` cannot silently disagree.
- **R4 — O2 not actually enforced (mutation-test failure).** Contract/rubric say unresolved near-intra-layer rows
  may not be sealed E1, but the validator has only C1–C8. Mutation test (set every `scored_tier=provisional`) PASSED
  in scored mode while **E016, E017, E039** remained unresolved E1. → Add **C9**: in scored mode, any edge with
  unresolved `near_intra_layer_check` and `scored_tier="E1"` fails unless it carries `near_intra_layer_result:"passed"`;
  a gate-E.4 failure must be removed from the E1 count / marked "within-a-layer, no SBT content."
- **R5 — O4 only partially enforced (mutation-test failure).** Contract says an E3 anti-control may pass via E0
  only with a pre-frozen `run_target_stub` AND a logged E.7 double-run interlock; the validator checks only stub
  presence. Mutation test (E018 → `scored_tier=E0`, `scored_modality=emergence-up`, arbitrary stub, no E.7 log)
  PASSED. → Add explicit machine fields `descent_test_logged_negative`, `recognition_search_logged_negative`,
  `non_descending_run_object_exhibited`, `run_target_stub_frozen_pre_scoring`; make **C5** reject anti-control E0
  unless all are present and true.
- **R6 — stale frozen prose (firewall-relevant, not cosmetic).** `edge_manifest_notes.md`, `SCIENCE_DIGEST.md`,
  `TYPING_RUBRIC.md`, parts of `FREEZE_NOTES.md` still describe the pre-v2 **44-edge** state / the old single E028
  value-split row, while the manifest is 46 edges. The registered null + no-summing ledger are part of the freeze.
  → Update every frozen prose count/row-list to the v3 state (**46 edges; E1/E2/E3/E0 per R3**; E028 split into
  E028a/E028b; no current E028 value-split row). **Add a generated consistency check** so prose counts cannot drift
  from `edge_manifest.jsonl`.

## OPTIONAL

- **O1 — tighten C7** to require full cards for all 9 registered `candidate_substructure` nodes (catch deletion of a
  target-only card).
- **O2 — normalize `accepted_observables`** to a list everywhere (qcd, chiral-perturbation-theory, classical-probability
  are sometimes string, sometimes array).

## Reviewer's mutation tests (we must make these now FAIL)
1. scored copy, all `scored_*`=provisional → currently PASSES with E016/E017/E039 unresolved E1 (must fail: C9).
2. E018 `scored_tier=E0`+arbitrary stub, no E.7 log → currently PASSES (must fail: hardened C5).
3. (new) a recognition row with no/menu `named_import` → must fail: C11.
4. (new) row tier ≠ `value_split.reported_tier` → must fail: C10.

*(Per-axis findings + the R1–R8 remediation check are in the conversation record; this file is the actionable v3
remediation contract + provenance.)*
