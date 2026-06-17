# Phase-3 Adversarial Audit — Cluster 5

> **SUPERSEDED-BY-MERGE NOTE:** where this pre-merge audit advice conflicts with the authoritative
> `phase3/scored_run/edge_manifest.jsonl` (esp. value-split handling and E017 status), the merged
> manifest governs. Specifically for **E017**: the merged manifest is authoritative — E017 is a
> within-a-layer/no-content relabel failure (gate-E.4 `near_intra_layer_result:"failed"`); it carries
> `scored_tier:"E3"` only as a schema **sentinel** plus `within_layer_no_content:true` +
> `excluded_from_foreclosure_count:true`, and is REMOVED from the chargeable foreclosure tally (it is
> NOT an ordinary E3 foreclosure gap; the raw E017 scored record's old `scored_tier:"E1"` is corrected
> to E3 per R2). For **E031** value-split handling: the merged manifest carries `value_split:null`;
> the previously-populated `theorem_run` value_split (with a bespoke `reported_leg` override) was
> REMOVED for violating validator C10 and because E031 is not in
> `CONTRACT.value_split_schema.rows_carrying_value_split` — the cascade-exponents(E0) //
> Navier-Stokes-regularity(E3) distinction is carried as prose only, never as a C10-bound value_split.

Auditor: adversarial Phase-3 edge-typing auditor.
Records: E011, E017, E027a, E031, E036, E042.
Cross-consistency sources: TYPING_RUBRIC.md (§B.7a precedence, §B.8 emittability, §C.5 procedure,
§E.3 value_split + C10, §E.5 conservative-default, §E.7/E.8 up/down firewall, §E.11 near-intra),
CONTRACT.json (canonical_modalities, modality_tier_compat, value_split_schema.reported_tier_rule + C10,
rows_carrying_value_split, recognition_resolution.affected_edges), edge_manifest.jsonl, route.json.

Attack axes applied to every record: (1) tier FORCED vs fitted; (2) for E1 — Xi REAL (declared toy,
two refinements, normalized residual behavior) vs asserted/over-read; (3) PRIMARY modality correct per
precedence (structural beats residual recognition); (4) §9 reductionist relapse (derive-across-layers /
score-within-layer / up=down symmetry); (5) E2 — exactly one non-menu named import frozen; (6) near-intra
E.4 honesty. Numeric reproductions were run independently where load-bearing.

---

## E011  classical_electromagnetism -> geometrical_optics  —  VERDICT: OK

- **Tier E1 (shadow-down): FORCED & honest.** Independently reproduced the declared eikonal/WKB toy:
  xi_rel = 4.80e-6 (h1, N=128, eps=1e-3) -> 4.96e-12 (h2, N=1024, eps=1e-6), matching the record's
  4.82e-6 -> 4.96e-12 to 3 sig figs and going to machine-zero monotonically as eps->0. The residual is
  exactly the O(eps) diffractive amplitude-transport tail (vanishes in the ray limit).
- **Xi REAL.** Two declared refinements, normalized residual read (not raw). Over-read control independently
  reproduced: replacing the third D0 row with a pure sub-wavelength fringe gives xi_rel ~0.378 stable-positive
  (record 0.379) — the source-only coherence/diffractive content is correctly LOCATED as blind-spot currency
  and not absorbed. This is the load-bearing E1 honesty test and it passes.
- **Primary modality correct.** descent (B.1) passes; duality/common-refinement/holonomy/currency all tested
  and FAIL (lossy one-way coarse-graining). shadow-down is primary; (shadow-down, E1) emittable.
- **No §9 relapse.** Down/shadow run as a derivation is legal; no up-inversion; genuinely between-layer
  (distinct Sigma_f, real quotient discarding phase-coherence d.o.f.). No hbar/thermal/out-of-Sigma_f import.
- value_split null (route flag has_value_split=true tested and found non-instantiable; both legs close E1).
  Matches frozen manifest.

## E017  standard_model -> qcd  —  VERDICT: OK

- **Operative verdict FORCED & honest: near-intra E.4 FAILED -> within-a-layer, REMOVED from E1 count.**
  near_intra_layer_result correctly resolved pending -> failed (manifest carries 'pending'). Reproduced both
  scenarios: (B) delete the relabel (SM readout = color tensor factor) -> xi_rel ~1e-16 machine-zero, but it
  is the IDENTITY on a tensor factor (same operators renamed); (A) keep genuine SM color<->EW cross content ->
  xi_rel stable-positive (my 0.83-0.97; record 0.67-0.79; same regime). Both readings => tensor-factor
  restriction, not a between-layer coarse-graining.
- The retained `scored_tier:"E1"` is the known-physics/schema label only; the row does NOT contribute to the
  E1 tally (anti-padding, C9/E.11/E.13 honored). Conflation with E001's dynamical run-only QCD content is
  explicitly fenced out. No §9 relapse — the 'just a relabel' diagnosis is CORRECT here because the edge is
  within-a-layer (primer §3/§9 trap 4 applied correctly, not as a false deflation).

## E027a  condensed_matter_spt -> spt-phases  —  VERDICT: FIX:value_split (applied) ; tier OK

- **Tier E2 (recognition-landing): FORCED & honest.** Reproduced the declared finite toy: descent foreclosed
  stably (xi_rel ~0.95-0.97 D|L, matching record ~0.97-0.99; reverse L|D ~0.84-0.94) — the topological class
  is non-definable from phase-blind local data (canonical non-factorization). Machinery control D0=A*L0
  reaches ~1e-16 machine-zero (record ~6e-16), confirming the oracle is NOT rigged to always foreclose.
- **Exactly one non-menu named import, frozen.** named_import = group-cohomology / cobordism classification
  (Chen-Gu-Liu-Wen + Kapustin) — matches CONTRACT.recognition_resolution.affected_edges_named_imports['E027a']
  verbatim; a single principle, not a menu. E027a is in the frozen 8-row recognition-landing set.
- **Primary modality correct (residual recognition-landing).** No structural test passes (descent fails; no
  duality/common-refinement/holonomy/currency); the entire landing is the named import. (recognition-landing, E2)
  is the only emittable pair. is_recognition=true confirmed.
- **HARD FIX APPLIED — value_split removed.** The record populated value_split {form_tier:E2, value_tier:E0,
  split_type:form_value}. This VIOLATED validator check C10: split_type=form_value =>
  reported_tier=value_tier=E0, contradicting the E2 headline (a scored_tier != reported_tier row is rejected
  at freeze). E027a is also NOT in the frozen rows_carrying_value_split set, and the realized-value E0 leg is
  ALREADY a separate registered edge (E027b, emergence-up E0). The redundant + C10-inconsistent object was set
  to null (matching the frozen manifest); the form/realized-value split is preserved by the E027a/E027b sibling
  pair. Headline tier UNCHANGED (E2). No honesty weakened.

## E031  hydrodynamics -> turbulence  —  VERDICT: FIX:value_split (applied) ; tier OK

- **Tier E0 (emergence-up): FORCED & honest.** UP edge; gate E.8 forbids sealing E1 by an up-computation
  regardless. Descent gives a stable-positive normalized residual (record xi_rel 0.70->0.87; raw norm FALLS
  4.11->0.50 — correctly read off scale-invariant xi_rel, not raw, per Pause-2). Null gate B reproduced
  (D=linear image of L -> xi_rel ~1e-15, record ~1e-14): the machinery discriminates. My quick cascade build
  gave construction-sensitive magnitudes (h1 low, h2~0.54) but the record candidly documents rejecting a first
  unfaithful toy (undeveloped cascade -> spurious xi_rel~0) and reports seed-robustness (min ~0.28) — the tier
  does not hinge on the exact magnitude.
- **Tier robust regardless of xi_rel magnitude:** arrow=up + recognition-search NEGATIVE (turbulence closure
  problem genuinely open; K41 is dimensional phenomenology, K62/She-Leveque are ansaetze, not derivations) +
  a constructible run-object EXISTS (Navier-Stokes DNS substrate, moment hierarchy non-closure) => E0 forced
  via STEP3. E.7 interlock logged (descent-negative, recognition-negative, run-object exhibited, run_target
  stub frozen). Substrate-agnostic analog of the proton-mass E0 anchor. No §9 relapse (no exponent claimed;
  run treated as irreducible; up/down asymmetry kept).
- **HARD FIX APPLIED — value_split removed.** The record populated value_split {form_tier:E3, value_tier:E0,
  split_type:theorem_run, reported_leg:value_tier} and itself conceded a 'documented divergence flagged for
  adjudication.' This VIOLATED C10: split_type=theorem_run => reported_tier=form_tier=E3, contradicting the E0
  headline; the bespoke 'reported_leg' override is not a CONTRACT field and cannot countermand
  reported_tier_by_split_type. A row may not self-grant a C10 exception (that is the elasticity the firewall
  forbids). E031 is not in the frozen value_split set; the NS regularity (Clay) sub-question is ALREADY carried
  in the frozen run_target_stub/notes prose as 'a SEPARATE open-theorem E3, NOT run-exhibited' (no registered
  regularity edge to bind a theorem_run leg to). Set to null (matching frozen manifest); the cascade-E0 //
  regularity-E3 distinction preserved in prose. Headline tier UNCHANGED (E0). No honesty weakened.

## E036  quantum_mechanics -> berry-phase-holonomy  —  VERDICT: OK

- **Tier E1 (holonomy): FORCED & honest.** EXACTLY reproduced the declared two-level toy: raw Xi = 16/64/256
  and K_DD = 16/64/256 at N=16/64/256, so xi_rel = 1.0 at every refinement (record's numbers match to the
  digit). The global holonomy (sum row) is exactly orthogonal to all local parallel-transport difference
  probes — it does NOT Xi-descend; it is a genuine route-mismatch.
- **Primary modality correct.** B.6 ROUTE-MISMATCH passes (full-loop vs trivial-loop differ by a nonzero,
  non-decaying Berry phase converging to the analytic -pi(1-cos th0); null gate: zero-area loop -> gamma->0).
  By B.7a a passing structural modality is primary; holonomy beats the (failed) Xi-descent. (holonomy, E1) =
  the 'computable RM' cell, emittable. The Berry phase is the rubric's own canonical B.6 exemplar.
- **No over-read / no §9 relapse.** xi_rel=1.0 (NOT a Xi=0 descent) explicitly tested; the E1 seal is for the
  computable route-mismatch VALUE, not a local-descent. hbar is a flagged QM layer constant, not smuggled.
  Holonomy value is finite linear algebra (not run-only), correctly NOT promoted to E0. value_split null
  (route flag tested, both form and value close E1). Matches frozen manifest.

## E042  general_relativity -> singularity-theorems  —  VERDICT: OK

- **Tier E3 (emergence-up, sharpened gap): FORCED & honest — the conservative call is correct.** UP edge;
  E.8 forbids E1 by up-computation. Reproduced structure on the Raychaudhuri-focusing toy: null gate B
  collapses to machine-zero (~1e-12, record ~8e-11) and the full-D residual is positive (not machine-zero).
  (Exact magnitudes are normalization-sensitive and not load-bearing for the tier.)
- **The decisive distinction from E001/E031 is correct.** Descent positive (not E1) + recognition-search
  NEGATIVE (singularity theorems are INTERNAL GR — they locate, not close; cosmic censorship is a conjecture;
  QG completions are not_established) + run-search NEGATIVE because the resolving substrate (quantum gravity)
  DOES NOT EXIST — you cannot positively construct a run of a substrate you do not have. Per E.7/E.5, E0 needs
  a positive run-object and is NOT a doubt-haven, so doubt at STEP3 demotes to the conservative terminal E3.
  This correctly REFUSES the flattering 'real emergence, deferred' E0 haven. (emergence-up, E3) emittable.
- **Over-read discipline decisive & correct.** The focal-point LOCATION descends (small Xi) but is an INTERNAL
  GR theorem (Raychaudhuri/Penrose-Hawking) computable from smooth data — reading the descent against it would
  be an E005-style over-read that silently drops the trans-Planckian content GR's Sigma_f excludes. Read against
  the full breakdown readout, the residual is stable-positive -> no E1.
- **No §9 relapse.** Internal-theorem leg (intra-layer, SBT silent) cleanly separated from the cross-layer
  breakdown-readout leg; up/down asymmetry kept; SBT names WHERE the extension is needed, not WHAT. value_split
  correctly null (route flag has_value_split=true tested and found NOT instantiable under the frozen split_type
  enums — the theorem is PROVEN, not an open theorem_run form leg, and there is no run-exhibited value leg).
  Matches frozen manifest. **E042 already did the value_split discipline correctly — no fix needed.**

---

## Summary

| edge  | scored tier | primary modality        | verdict |
|-------|-------------|-------------------------|---------|
| E011  | E1          | shadow-down             | OK |
| E017  | E1 (removed from count) | shadow-down | OK (near-intra E.4 failed, honestly removed) |
| E027a | E2          | recognition-landing     | FIX:value_split (applied) — tier unchanged |
| E031  | E0          | emergence-up            | FIX:value_split (applied) — tier unchanged |
| E036  | E1          | holonomy                | OK |
| E042  | E3          | emergence-up            | OK |

**Flag count: 2** (E027a, E031 — both C10 value_split violations).
**Tier corrections: 0** (all six headline tiers are FORCED and correct; both fixes nulled an out-of-contract,
C10-violating value_split object without changing any headline tier).

**Independent numeric reproductions:** E011 (descent + over-read control), E017 (scenarios A/B), E027a (descent
+ machinery control), E031 (null gate B), E036 (full Xi, exact match), E042 (null gate B) all reproduced the
records' qualitative verdicts; E011, E027a, E036 reproduced to ~3 sig figs. No asserted/over-read Xi found.
No §9 reductionist relapse found (no derive-across-layers, no score-within-a-layer, up/down asymmetry kept
throughout; E017's 'relabel' diagnosis and E042's E0-refusal are both correct conservative calls).
