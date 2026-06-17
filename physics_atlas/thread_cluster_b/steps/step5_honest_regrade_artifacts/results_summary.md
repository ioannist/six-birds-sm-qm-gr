# Step 5 Results Summary

## Orientation

Step 5 is an honest-regrade pass over the Cluster B deliverable. It applies only the accepted external-review fixes R1, R2, and R4. It introduces no new computation.

## Applied Regrades

R1: E042 continuation is now graded `modeled-shape`. The continuation is assigned by the toy (`GR_defined=eps>0`, `L_defined=True`, hand-set post-locus values), not derived from a constraint or evolution law. The computed finite-toy diagnostic remains the divergence/stabilization table.

R2: E021 firm content is narrowed to the selected/run non-factorization on the toy: obstruction `4` with the descending-control contrast at obstruction `0`. The booked UV-to-IR ledger is now explicitly graded as modeled/illustrative P6 bookkeeping, not a firm audit computed from a coarse map, RG flow, or package dynamics. The schema flag `firm_part_missing_audit_ledger` is `false`, and `modeled_p6_ledger_illustrative` is `true`.

R4: Step 1 and the Step 4 statement now disclose that the non-descending `d4_subplanck` and `d5_vacuum` readouts are deliberately instantiated by branch splits in the toy carrier. The controls show the finite tests discriminate, but do not certify physical frame transfer.

## Validators

The Step 3 and Step 4 validators were strengthened to enforce the corrected grades. Step 5's validator re-runs `run_step1.py`, `run_step2.py`, `run_step3.py`, and `run_step4.py` and then checks the Step 5 audit packet.

## Verdict

`honest_regrade_applied_validators_pass`.

The Cluster B deliverable is more honest after this pass: the assigned E042 continuation is no longer overgraded, the E021 ledger is no longer marked firm, and the branch-split instantiation of d4/d5 is explicit. The interpretation documents and framework premise were left untouched, and no richer-carrier battery was added.
