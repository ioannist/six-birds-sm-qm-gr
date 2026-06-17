# Calibration Report — Physics Layer Atlas Blind Typing

**Role:** Adjudicator (non-blind). **Date:** 2026-06-04.
**Blind scored records:** `/home/repos/six-birds-papers/physics_atlas/calibration/scored/*.json`
**Frozen bundle (known answers):** `/home/repos/six-birds-papers/physics_atlas/prereg/`
**Scored run built at:** `/home/repos/six-birds-papers/physics_atlas/calibration/scored_run/`

## Verdict (PAUSE-2 RESOLVED): CALIBRATION PASS — scoring is UNBLOCKED

> **PAUSE-2 UPDATE (2026-06-04).** The external reviewer adjudicated the calibration
> (`/home/repos/six-birds-papers/physics_atlas/prereg/EXTERNAL_REVIEW_PAUSE2.md`):
> **TIER calibration PASSED** (all 9 blind tiers match known; C4 clean); the *only* block
> was a **MODALITY-label ambiguity on E005** (`general_relativity -> black_hole_thermodynamics`).
> The reviewer's resolution is **option (b): a primary + secondary modality with an explicit
> PRECEDENCE rule** — a *structural* modality is **primary**; recognition-landing is a
> **residual**; a structural-E2 edge that still needs a named import records
> `recognition-conditional` as a **SECONDARY** flag (now encoded in `TYPING_RUBRIC.md §B.7a`,
> review fix R-P2). Applying that rule, **E005's primary modality is `currency-shadow-price`**
> (the §B.5 "surface gravity as the price in black-hole thermodynamics" structural test passes,
> and structural beats residual recognition), tier **E2** (unchanged), with
> `recognition-conditional` recorded as a secondary flag. Re-typing E005 this way clears the
> two C11 failures and **the scored freeze-gate now exits 0**. The original FAIL analysis below
> is retained verbatim as the historical record of the block and its diagnosis; it is
> superseded by this resolution.

**RESOLVED STATUS:** All 9 blind **tiers** match the known calibration tiers (C4 tier-equality
blocker clean), AND the scored freeze-gate validator now exits **0** (E005 re-typed to its
primary `currency-shadow-price` modality per §B.7a). `calibration_pass = (all 9 tiers match)
AND scored_pass AND e005_deterministic = TRUE`.

### Historical block (superseded by the Pause-2 resolution above)

All 9 blind **tiers** match the known calibration tiers (C4 tier-equality blocker passes
for every calibration edge). **However** (pre-resolution), the scored freeze-gate validator exited **1**:
the blind agent's **modality** assignment for **E005** tripped check **C11** (R2,
recognition-landing named-import consistency). Calibration PASS requires *both* all-9 tiers
match *and* the scored validator exit 0. Before the Pause-2 re-typing the second condition failed.
Per the rig's own rule, a mismatch (here a modality/contract
inconsistency surfaced at the scored gate) is a publishable calibration **failure that
blocks scoring**, not something to paper over.

## Per-edge calibration table (the 9 blind calibration edges)

| ID   | source -> target                                 | Blind tier | Known tier | MATCH? | Decision path        | Xi (E0/E1 descent) |
|------|--------------------------------------------------|:----------:|:----------:|:------:|----------------------|--------------------|
| E001 | qcd -> hadron-spectrum                            | E0         | E0         | YES    | emergence-run-E0     | Ξ h1=7.83865e8, h2=2.250145e9 (Ξ>0 stably; no finite linear descent → not E1; runs/tests E0) |
| E002 | statistical_mechanics -> thermodynamics          | E1         | E1         | YES    | descent-E1           | n/a (sealed E1 by finite descent; no Ξ logged) |
| E003 | special_relativity -> classical_mechanics        | E1         | E1         | YES    | descent-E1           | n/a |
| E004 | kinetic_theory -> hydrodynamics                  | E1         | E1         | YES    | descent-E1           | n/a |
| E005 | general_relativity -> black_hole_thermodynamics  | E2         | E2         | YES (tier) | recognition-E2   | n/a — **modality mismatch, see below** |
| E018 | quantum_mechanics -> general_relativity          | E3         | E3         | YES    | foreclosed-gap-E3    | n/a |
| E019 | standard_model -> gauge-group-origin             | E3         | E3         | YES    | foreclosed-gap-E3    | n/a |
| E020 | standard_model -> fermion-generations            | E3         | E3         | YES    | foreclosed-gap-E3    | n/a |
| E021 | general_relativity -> cosmological-constant      | E3         | E3         | YES    | foreclosed-gap-E3    | n/a |

**Tier tally: 9/9 match.** (E001 arrow=up; E002–E005 down; E018 bidirectional;
E019–E021 up — consistent with the blind records and the frozen manifest.)

## Modality cross-check (the failure)

| ID   | Blind modality        | Contract-frozen modality (`provisional_modality_guess` / design) | Consistent? |
|------|-----------------------|-------------------------------------------------------------------|:-----------:|
| E001 | emergence-up          | emergence-up                                                      | yes |
| E002 | shadow-down           | shadow-down                                                       | yes |
| E003 | shadow-down           | shadow-down                                                       | yes |
| E004 | shadow-down           | shadow-down                                                       | yes |
| E005 | **recognition-landing** | **currency-shadow-price**                                       | **NO** |
| E018 | emergence-up          | common-refinement (guess) — both E3; no scored modality gate fires | tier-OK |
| E019 | emergence-up          | emergence-up                                                     | yes |
| E020 | emergence-up          | emergence-up                                                     | yes |
| E021 | emergence-up          | emergence-up                                                     | yes |

(Note E018: blind `emergence-up` vs guess `common-refinement`. Both are E3-compatible and
no scored modality-consistency check fires on E018, so it does not block. It is recorded
here for transparency but is not a calibration failure.)

## The blocking mismatch — E005

The contract (`CONTRACT.json`) freezes E005 (`general_relativity -> black_hole_thermodynamics`)
as an **E2 landing via a named import under the currency / shadow-down family**, with the
import frozen at declaration:

> named_import = "QFT in curved spacetime (Hawking thermal flux) + the first law of
> black-hole mechanics, conditional on the no-back-reaction (semiclassical) assumption"

and it is **explicitly excluded** from the `recognition-landing` set. `CONTRACT.json`
(`E2_recognition_landing_subset`, line 231) states verbatim that the 8 recognition-landing
rows are `E007, E022, E025, E026, E027a, E028b, E030, E033`, and that
**"the other 5 E2 rows (E005, E023, E024, E029, E034) land via a named import under
duality/currency/shadow-down without the recognition-landing modality tag."**

The blind agent took E005 down the `recognition-E2` decision path and tagged
`scored_modality = "recognition-landing"`. It got the **tier right (E2)** but routed the
edge through the wrong **modality**. Because `recognition-landing` membership
(`recognition_resolution.affected_edges`) is **rule-driven** (R2) — the validator enumerates
every manifest row whose modality == recognition-landing and asserts the set equals the
frozen `affected_edges` — the E005 row now violates two C11 sub-rules:

1. E005 is **not** listed in `recognition_resolution.affected_edges`.
2. E005 has **no** frozen import in `recognition_resolution.affected_edges_named_imports`.

## Scored validator output (verbatim)

Command:
`node .../scored_run/validate_freeze_gate.mjs --mode scored --dir .../scored_run`

```
Physics Layer Atlas — freeze-gate validator
mode=scored  dir=/home/repos/six-birds-papers/physics_atlas/calibration/scored_run
loaded: 21 theory stub(s), 46 edge(s), 30 closure card(s)

[C11] E005: recognition-landing row has no frozen import in recognition_resolution.affected_edges_named_imports
[C11] E005: recognition-landing row is NOT listed in recognition_resolution.affected_edges (R2: a stale list is rejected)

FREEZE-GATE: FAIL — 2 failure(s): C11=2
```

**Exit code: 1.**

**C4 (the calibration tier-equality blocker) produced ZERO failures** — every calibration
edge's `scored_tier` equals its `calibration_known_tier`. The only failures are C11
(modality/import consistency). C9 (near-intra-layer) passed: E016/E017/E039 were set to
`near_intra_layer_result = "passed"` per the build spec, so their E1 seals are admitted.

## Rig vs. agent: where did the error originate?

**This is a BLIND-AGENT error, not a rig error.** The decision procedure and the contract
are internally consistent and correctly froze E005 as a currency/shadow-down E2 landing
with a single named import; the validator's C11 (R2) rule correctly fires when an edge is
tagged recognition-landing without being in the frozen recognition set. The blind agent,
typing E005 in isolation, found a valid E2 landing but selected the `recognition-landing`
modality where the contract's design intends the currency/shadow-price modality. Diagnosis:

- **Tier judgment (E2): CORRECT** — agrees with the frozen calibration tier; the agent
  correctly recognized no internal descent/duality/common-refinement closes the edge and
  that it lands only via an external named principle.
- **Modality judgment (recognition-landing vs currency-shadow-price): WRONG (vs contract).**
  E005 lands on Hawking's QFT-in-curved-spacetime flux plus the first law of black-hole
  mechanics under the semiclassical no-back-reaction assumption — the contract treats this
  as a *currency/shadow-price* import (a priced first-law/thermal-currency relation), not a
  bare "remove-the-import-and-nothing-remains" recognition landing. The recognition-landing
  basket is reserved for the 8 enumerated rows (e.g., E007 Gleason, the Jacobson edge E022),
  and E005 is by design one of the 5 non-recognition E2 imports.

Note: the rig *could* be hardened so a recognition-vs-currency confusion is caught earlier
(e.g., a scored-mode pre-check that an edge's modality is compatible with its frozen
`named_import` family before C11). But that is a robustness improvement, not the cause: the
contract already encodes the correct answer, and the gate correctly refused to freeze the
inconsistent typing. The fix is on the agent side — re-type E005's modality to the
currency/shadow-price landing (tier stays E2).

## What would make calibration PASS

Either (a) the blind agent re-scores E005 with the contract-consistent modality
(currency/shadow-price, tier E2), after which C11 clears and, with all 9 tiers already
matching, the scored validator exits 0; or (b) the contract is formally amended to admit
E005 into the recognition-landing set with its named import frozen there (a design change,
not a calibration repair, and one that contradicts the frozen `E2_recognition_landing_subset`
rationale). Until then, scoring is blocked.

## Pause-2 resolution — E005 re-typed, scored gate now GREEN

Per the external Pause-2 verdict and the new `TYPING_RUBRIC.md §B.7a` MODALITY PRECEDENCE
RULE (review fix R-P2), E005 was re-typed by applying the rule's precedence to
`general_relativity -> black_hole_thermodynamics`:

- **STRUCTURAL beats RESIDUAL recognition.** The currency/shadow-price structural test (§B.5)
  PASSES — the rubric's own currency exemplar is "surface gravity as the price in black-hole
  thermodynamics." A structural test passing makes that modality **primary** (§B.7a clause 1;
  §B.7), so **`primary_modality = currency-shadow-price`**, **NOT** the residual
  `recognition-landing`.
- **Tier unchanged: E2.** The priced first-law content still needs a named import to fix its
  thermodynamic meaning (classical GR's `Ξ≈0` is an **over-read**: `ħ`/thermal predicates are
  not in GR's `Σ_f`), so the edge sits at the `(currency-shadow-price, E2)` cell of the §B.8
  table.
- **Secondary flag: `recognition-conditional`.** Because the E2 closure leans on a named
  import (QFT-in-curved-spacetime Hawking flux + the first law of black-hole mechanics, under
  the semiclassical no-back-reaction assumption = the E034 construction), the edge carries
  `secondary_modalities = conditionality_flags = ["recognition-conditional"]`. This secondary
  flag is **never** counted in the registered null and **never** emittability-checked; its
  single frozen named import is enforced in parallel by **check C13** (= C11 hygiene applied to
  the secondary flag), **not** by C11 (E005 is correctly excluded from the primary
  recognition-landing set `affected_edges`).
- **Determinism.** Given the frozen `(S, T, M, modality-tests)`, the §B.7a precedence rule
  yields `primary_modality = currency-shadow-price` with **no free knob** — exactly one
  structural test passes (currency/shadow-price), and the rule deterministically selects it as
  primary. `e005_deterministic = TRUE`.

Re-running the scored freeze-gate after the re-typing:

```
node .../scored_run/validate_freeze_gate.mjs --mode scored --dir .../scored_run
Physics Layer Atlas — freeze-gate validator
mode=scored  dir=/home/repos/six-birds-papers/physics_atlas/calibration/scored_run
loaded: 21 theory stub(s), 46 edge(s), 30 closure card(s)

FREEZE-GATE: PASS — all checks clean (mode=scored)
```

**Exit code: 0.** The two C11 failures are cleared; C4 (tier-equality) remains clean; C9
(near-intra-layer) remains clean (E016/E017/E039 `near_intra_layer_result = "passed"`).

## Summary

9/9 blind **tiers** match the known calibration tiers and the C4 tier-equality blocker is
clean — the rig's tier-discrimination calibration holds. After the **Pause-2 resolution**
(re-typing E005 to its **primary** `currency-shadow-price` modality with a
`recognition-conditional` **secondary** flag, per the new §B.7a precedence rule), the scored
freeze-gate now **exits 0** — the historical C11 (R2) block is cleared. Calibration requires
both all-tiers-match AND validator-exit-0; **both now hold**.
**Overall: CALIBRATION PASS** (tier calibration validated; the E005 modality ambiguity
resolved deterministically as a primary structural modality + secondary recognition-conditional
flag); **scoring is UNBLOCKED.**
