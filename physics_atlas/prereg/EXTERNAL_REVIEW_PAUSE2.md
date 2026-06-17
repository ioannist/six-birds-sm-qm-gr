# External Review — PAUSE 2 (Calibration Gate), handoff v5 — VERDICT + Resolution

**Date:** 2026-06-04 · **Verdict:** **CALIBRATION-PASS (tier)**; modality: **both** (primary
`currency-shadow-price`, secondary recognition-conditional); **gate-policy: tier-only hard for calibration**.

## Adjudication

- **Tier:** all 9 blind tiers match known; C4 clean. Tier rig validated. PASS.
- **E005 (GR→black-hole-thermodynamics) modality:** **primary = `currency-shadow-price`**, **secondary =
  recognition-conditional**. The blind agent was right on tier (E2) and right that classical GR alone
  doesn't close the thermal content (its Ξ≈0 is an *over-read* — `ħ` coefficients + thermal reinterpretation
  are not in GR's Σ_f). But the **modality** should be the structural one: the rubric's currency/shadow-price
  def explicitly names "surface gravity as the 'price' in black-hole thermodynamics" as the exemplar
  (TYPING_RUBRIC §B, L177–185), and `recognition-landing` is **residual** — "if a structural modality passes,
  the edge is that structural modality, not recognition" (L243–250). The blind agent under-applied this.
- **Gate policy:** do **not** hard-gate calibration on exact modality-label agreement. Hard-gate **tier**;
  keep hard validation for **canonical modality strings, primary-modality/tier emittability, and
  recognition-import hygiene**; route a blind-vs-frozen **primary**-modality mismatch to adjudication, not auto-fail.
  (E018 likewise: blind `emergence-up` vs frozen `common-refinement`, tier E3 either way — modality is
  empirically less deterministic than tier on hard/faceted edges.)

## REQUIRED FIX (their recommendation (b): primary + secondary modality, with a precedence rule)

Add to rubric + contract:

> Each edge has exactly one `primary_modality`, used for `(modality,tier)` emittability and headline
> reporting; it may also carry `secondary_modalities` / `conditionality_flags`. **If a structural test passes
> — duality, common-refinement, holonomy, currency, descent, emergence — that structural modality is
> primary.** `recognition-landing` is primary **only** when no structural modality closes the edge and the
> imported named principle is the entire landing mechanism. If a structural E2 edge still requires a named
> import, record `recognition-conditional` as a **secondary** flag, not as primary `recognition-landing`.

For **E005**: `primary_modality: currency-shadow-price`, `tier: E2`, `secondary_flag: recognition-conditional`,
`named_import: QFT-in-curved-spacetime (Hawking thermal flux) + first law of BH mechanics, semiclassical
no-back-reaction`. **C11** applies to rows whose **primary** modality is `recognition-landing`; a **parallel
import-hygiene check** must ensure secondary recognition-conditional E2 rows still freeze their named import.
**Do not force-align silently — record the adjudication and rerun the scored gate.** (Confirmed: re-typing
E005's modality to currency-shadow-price makes the scored gate pass cleanly.)

## OTHER FINDINGS

- **E001 Ξ reporting:** raw Ξ grows (7.84e8 → 2.25e9) but the **relative residual shrinks** (0.197 → 0.042)
  while staying positive; the E0 signal is "**stable positive normalized residual + analytic control at
  machine-zero**," not monotone raw growth. **Report both raw and normalized Ξ**, and base the E0-vs-E1
  descent criterion on the **normalized** residual. Keep E005 as the canonical *over-read* example and E001 as
  the *stable-positive-residual* example.
- **Modality < tier in determinism.** Two of nine blind edges (E005, E018) disagreed on modality while
  getting tier right → tier-hard calibration + modality adjudication is the correct policy.

## INTEGRITY (must repair before proceeding)

`SHA256SUMS` lists `closure_cards_part1.jsonl` and `closure_cards_part2.jsonl`, which are **absent from the
review zip** (excluded as intermediate scratch) → `sha256sum -c` fails on those two (19/21 OK). They are
redundant (concatenated into `closure_card_manifest.jsonl`). **Delete them and regenerate `SHA256SUMS` over
the authoritative bundle** so the hash record matches the package.
