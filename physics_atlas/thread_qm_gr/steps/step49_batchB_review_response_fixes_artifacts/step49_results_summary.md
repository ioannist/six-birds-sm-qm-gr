# Step 49 Batch B Review-Response Fixes

This is a review-response patch only. It changes labels, caveats, warrant scope, and framing for Steps 47-48. It does not change any computation, number, control, result, or verdict logic.

## R1/R2/R4 Response Table

| Review item | Requested fix | Files changed | Confirmation |
|---|---|---|---|
| R1 | Reframe Step47 as a criterion-consistent `LANDED * GROUND (conditional)` result and extend the warrant through Step26's semiclassical back-reaction. | `steps/step47_common_carrier_door_test_artifacts/common_carrier_door_test_step47.py`; `run_step47.py`; regenerated Step47 summary, schema, statement, nonclaim, and warrant CSV. | Step47 now states the common-carrier premise is grounded as the down-shadow of the semiclassical co-sourcing layer; Step26 is cited for `V[psi] = background + kappa*T00[psi]`; the residual is narrowed to free gravitational degrees, full QG sector, and trans-semiclassical survival. |
| R2 | Rename the weak RT ladder attempt and caveat that it is not a strong bulk-reconstruction test. | `steps/step48_ladder_vs_fork_resolution_artifacts/ladder_vs_fork_resolution_step48.py`; `run_step48.py`; regenerated Step48 summary, schema, statement, and sim CSV. | The attempt is now `weak_RT_QM_accessible_shadow_ladder`; schema uses `weak_rt_ladder_defect`; summary and statement name strong bulk reconstruction as an untested residual. |
| R4 | Add the structural-audit caveat for the Step47 door-test. | Step47 generator plus regenerated `step47_results_summary.md`. | Summary now states the F37/F51/FoEC/SAU classification is a structural reading of framework sources; the computed teeth are the complementary-pair and non-co-sourcing controls. |

## Number Check

Pinned values are unchanged:

| Step | Value | Expected | Observed |
|---|---:|---:|---:|
| Step47 | complementary-pair commutator | 0.707106781187 | 0.707106781187 |
| Step47 | non-co-sourcing stress residual | 0.380602660378 | 0.380602660378 |
| Step48 | direct ladder defect | 8 | 8 |
| Step48 | weak-RT ladder defect | 8 | 8 |
| Step48 | nested-control defect | 0 | 0 |
| Step48 | direct route mismatch | 0.5 | 0.5 |

## Validation

Validated after regeneration:

- `run_step47.py --self`: PASS
- `run_step47.py --chain`: PASS
- `run_step48.py --self`: PASS
- `run_step48.py --chain`: PASS

`run_step49.py --self` rechecks the required review-response text, pinned values, old weak-RT predecessor name absence in Step48 artifacts, and Step47/48 self validators.
