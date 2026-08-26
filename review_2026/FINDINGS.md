# Findings register buffer (flush to review_2026/FINDINGS.md between rounds)

| ID | Severity | Unit | What | Evidence | Status |
|----|----------|------|------|----------|--------|
| F-001 | MAJOR (portability/self-containment) | infra | Stale absolute paths to /home/repos/six-birds-papers; qm_gr step29+step35 validators FAIL on clean checkout; 34 files carry the string (executable refs + provenance records mixed) | run_step29/35 --self output; grep | CLOSED — Cody fix rounds 1+CR accepted; regression sweep 132/132 PASS (scratch copy, 2026-08-26) |
| F-002 | MINOR (freeze integrity; downgraded) | P3 | step69 pins the load-bearing step59 scores CSV tautologically (expected_sha256 computed from the same file, imported_verbatim hardcoded True); validator pins build scripts only — data unpinned | record_stability_prediction_step69.py:222-228; run_step69.py:120-124 | MITIGATED — scratchpad rebuild regenerates scores CSV byte-identical (sha 36966329…); pin should still become a real constant |
| N-001 | NOTE (asymmetric gate) | P1 | run_step55.py check_tables hard-fails on nullity<=0, entrenching the positive verdict; outcome change surfaces as validator FAIL, not alternative verdict | run_step55.py check_tables | OPEN — pattern likely repo-wide; sweep candidate |

| F-003 | MINOR (process/repo) | infra | Non-idempotent validators: some --self re-execute builds and regenerate artifacts in place; Stage-1 sweep left FP-noise diffs in ~9 artifact files (worktree now differs from HEAD there) | git status; step17 json diff (last-digit) | OPEN — future sweeps in scratch copies; disposition of drifted files at close |
| F-004 | MAJOR (rebuild reproducibility) | infra | qm_gr steps 51-54 drivers hash Foundations III/IV corpus .tex at build time; corpus absent from this repo → rebuild crashes after portability fix (previously depended on a sibling checkout) | f49_bell_nonlocal_residual_step52.py:280 | IN-FIX — Cody CR-1 (env var + loud failure + scratch verification) |

| F-005 | MINOR (provenance) | infra | Published step52 frozen ledger pins Foundations IV at superseded corpus revision (retired-repo df0e8a1); current corpus file hashes differently; byte-identical reproduction confirmed with frozen version | Cody CR round report; ledger sha ccf1a86… | RECORDED — corpus evolution post-publication now documented |

| F-006 | MAJOR (regeneration coherence) | P2/infra | After the F-001 CR-2 overlay, step56 builder still records the historical step52 hash (matches=False on rebuild) while the validator demands the historical value in the ledger — rebuild-then-validate fails | gravitational_mediation_bmv_prediction_step56.py frozen_rows; run_step56.py:218 | OPEN — F-001b packet queued (manager's CR-2 design shares responsibility) |

| F-007 | MAJOR (science bookkeeping) | P3 | step59/69: delta only evaluated when substrate passes, but unevaluated rows counted as breaking; witness gate lacks delta_evaluated/pair_count>0 requirement; F27/F48 global booleans attached to arbitrary sample rows | Eddy P3 findings 1-2-4, manager recount | OPEN — fix packet queued after probes |

| F-008 | MAJOR (assurance) | S2/repo-wide | --self validators for ca steps 43/44/61 read stored artifacts only (step61 audit gates are literal True booleans); drift between driver and stored outputs undetectable | Eddy S2 finding 6 (file:line cited) | OPEN — validator-strengthening packet queued; pattern already seen in qm_gr (Q1 finding 8) |

## Queued Cody packet candidates (beyond F-001)
- Stale-number sweep: for every step, verify each number quoted in results_summary.md/schema regenerates
  from the driver (automated cross-check harness). Catches hand-edited/stale summaries at scale.
- Data-pin sweep: every load-bearing cross-step DATA file (not just build scripts) gets a real pinned hash
  (fixes F-002 class).
- P1 adversarial probe: search small non-tree multi-path carriers for zero-kernel counterexample to the
  universal quantifier in §6.1's community statement.
