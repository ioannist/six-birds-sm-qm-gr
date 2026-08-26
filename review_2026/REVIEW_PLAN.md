# Post-publication verification review — plan (started 2026-08-26)

**Owner directive:** the original experiment process was not well reviewed/gated; assume there are
issues in the code, the scientific results, and the paper. Go back and check every result and the
underlying science, one by one. High-level + staged. Claude manages; codex agents (Cody implement,
Eddy review) do the reviewing/implementing. **Focus: code, experiments, results. Paper rewriting is
DEFERRED** (a claims-consistency map is produced, but no paper edits until the owner asks).

**Scope of review:** the published support surface for
*To Kill Three Stones with Six Birds* (Zenodo 10.5281/zenodo.20713213):
`physics_atlas/` (thread_cluster_a 66 steps, thread_qm_gr 56 steps, thread_cluster_b 11 steps,
phase3/phase4 atlas, calibration, missing_layers, prereg), `retrodiction_atlas/`, `unification_atlas/`.

**Organizing principle:** review by RESULT (the paper's claim units), not by raw step count.
Each result gets a ledger row and passes through the same gate sequence. The step chains behind a
result are pulled in as needed.

## Review units

### R-group P — the three falsifiable predictions (Stage 2; highest stakes)
- **P1** Entanglement does not determine geometry (qm_gr step55).
- **P2** BMV-null / gravity's channel classically-indexed (qm_gr step56).
- **P3** Record-stability forbids proton decay + monopoles (cluster_a step69; feeds on steps 57–60, 64–68).

### R-group S — SM track results (Stage 3; cluster_a MAIN_RESULTS A–J)
- **S1** Conditional selection of su(2)+su(3)+u(1): ~11,990 chiral structures → {2|3, SU(4)} → clean-separation pick (steps 28–39, corrections 40/42; competitor coverage 53).
- **S2** Window closure + single-factor theorem (steps 43–44, 61).
- **S3** X/Y-coset unification spine: proton decay, monopole, GUT↔SM non-factorization as one object (steps 38/41/45/46/47); includes the sin²θW=3/8, k_Y=5/3 recovery.
- **S4** Content blindness / type-limit results (steps 14–16, 48–49, 51, 54, 62): SM content NOT selected, N_gen blindness theorem.
- **S5** Selection/measure layer L* + BudgetedRole/naturalness reframe (steps 1–13, 17–19).
- **S6** Memory-stability grounding of clean-separation (steps 57–59, 60, 64) + E032 arc (66–68).

### R-group Q — QM-GR track results (Stage 4; qm_gr MAIN_RESULTS A–F)
- **Q1** Carrier L construction + T_QG_NoGo + T_QGR_Unique (steps 1–38).
- **Q2** Route-mismatch located (steps 30/32/36/48).
- **Q3** Fork-over-ladder resolution + nested control (steps 30–38, 48).
- **Q4** Common-carrier premise GROUND-landing (step 47 + 26).
- **Q5** RT/area = shadow-price of entanglement landing (steps 39–46).
- **Q6** Born + area one fiber-volume ledger (step 50).

### R-group G — GR upper boundary, cluster_b (Stage 5)
- **G1** E021 cosmological-constant readout (steps 3, 8, 10, 11).
- **G2** E042 singularity-boundary readout (steps 2, 7).

### R-group A — atlas machinery + card atlases (Stage 5)
- **A1** Phase3/phase4 theory map: edge typings, freeze gate, calibration.
- **A2** Missing-layer cards (E018/L*, GR_upper) audits.
- **A3** Retrodiction atlas cards + ledger.
- **A4** Unification atlas cards + tension ledger.

## Stages

- **Stage 0 — infrastructure (manager, now):** this plan; REVIEW_LEDGER.md; bootstrap Cody+Eddy
  threads (.codex/threads absent — fresh box for this repo).
- **Stage 1 — reproduction baseline (manager + background compute, now):** run EVERY executable
  self-check/validator in the atlas (cluster_a run_all_selfcheck.py, per-step run_*.py --self across
  all three threads, verify_mutation_tests.py, prereg freeze gate). Output: green/red map in the
  ledger. Red = immediate Cody fix candidates. This is mechanical and parallelizable (bounded pool).
- **Stage 2 — predictions P1–P3, one at a time:** per-result deep review (gates below).
- **Stage 3 — SM results S1–S6, one at a time** (S1→S3→S2→S4→S6→S5 priority order: the
  selection chain and the coset spine carry the paper).
- **Stage 4 — QM-GR results Q1–Q6, one at a time** (Q1 first — everything conditions on the carrier;
  then Q5 (flagship), Q3/Q4, Q2, Q6).
- **Stage 5 — G + A groups** (lighter: sample-based card audits, machinery checks).
- **Stage 6 — consolidated verdict:** findings report + paper-claims consistency map
  (claim → supported / weakened / unsupported). NO paper edits (deferred).

## Per-result gate sequence (the review contract)

1. **REPRO:** all step artifacts regenerate; validators/self-checks pass; numbers in summaries match
   regenerated outputs (no stale/hand-edited numbers).
2. **CODE:** Eddy read-only review of the step drivers: correctness of the computation itself
   (enumeration completeness, quotient/equivalence-class code, no off-by-one in search windows,
   determinism/seeds, silent exception paths).
3. **SCIENCE:** does the computation actually establish the claimed property? Verify the LOAD-BEARING
   invariant, not the summary gates: controls have teeth (can-fail AND shown-to-fail), anti-circularity
   real (the discriminator does not import the answer), claimed theorems actually proved at claimed
   strength, no smuggled priors (the steps-20–27 total_slots=5 failure mode), no descending bypass.
4. **GRADE:** is the honest-grade label (LANDED/COMPUTE/GROUND/conditional/toy-only) consistent with
   what survived 1–3? Overclaim check against the paper's use of the result.
5. **FIX:** findings triaged; Cody fixes code-level defects; science-level defects produce a
   re-grade + ledger entry (and later a paper-claims delta), not silent repair.
6. **CLOSE:** manager verifies the actual property on the fixed artifact; ledger row goes
   CONFIRMED / CONFIRMED-WITH-FIXES / DOWNGRADED / RETRACTED.

## Workflow rules in force (from standing memories)

- Cody = codex implementer (workspace-write, effort high). Eddy = codex reviewer (read-only, effort
  medium; high for verdict/close rulings). One turn per thread at a time; never mutate the tree while
  Eddy reads. Threads via `.codex/bin/codex-agent.sh`; ids in `.codex/threads/`.
- Long dispatches and suites: `Bash(run_in_background: true)`, never blocking, never hand-rolled nohup.
- Prompts: goal-driven, outcome-first, neutral QA vocabulary (no security terms — content filter).
- Manager verifies reviewer claims against the tree; reviewer prose is never accepted on its own.
- Commits are owner-gated. No memory edits from track work. Findings live here + REVIEW_LEDGER.md;
  manager trail in review_2026/manager_log.md (gitignored pattern).
- Parallelism: Stage-1 repro jobs run in a bounded parallel pool; codex review work stays sequential.

## OWNER DIRECTIVE (2026-08-26) — repair over downgrade
When the review finds overclaims or missing parts, the preferred disposition is to IMPLEMENT the
missing piece so the stronger claim (modified if needed) genuinely lands — not to downgrade the claim.
Downgrade/fix only what is flat-out wrong. North star: land the stronger claims already present with
minimum downgrades; if that takes more thorough work, that IS the project. Gate 5 (FIX) is therefore
extended: science-level gaps spawn REPAIR/LAND construction packets first; re-grade only if repair
fails or the claim is wrong at its core.

Repair tracks opened:
- P1-REPAIR: land a genuine (quotient-surviving) entanglement-invisible sector: P1-PROBE (running)
  → if reducible-only, escalate to richer carriers + fingerprints from actual contracted boundary
  states (true entanglement-shadow construction), not min-cut proxies.
- P2-REPAIR: construct the missing forcing step — derive the record-channel restriction from frozen
  upstream structure (the record/memory layer), with a semantic gate that rejects the
  geometry-diagonal coherent mediator for a stated upstream reason.
- P3-REPAIR: evaluate Δ_fact on ALL 11,990 carriers (remove substrate-gated evaluation), rebuild the
  table with honest three-way semantics aiming to restore a full-carrier RS⇒clean; genuine capacity
  witnesses (evaluated nonempty defects); per-carrier F27/F48; dimension-aware record grammar
  (de-SU(3) the proxy) with the 24/0 nesting re-tested.
