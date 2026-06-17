# Step 22 Nonclaim Boundary

1. This step applies F51 on a declared finite carrier.

2. The verdict is scoped: `unification_holds_on_carrier`.

3. The complete 16-state carrier is used to test strict refinement in both child directions; broader carriers remain external review.

4. This step computes status compatibility from audit restrictions and overlap agreement; it does not assert compatibility without the computation.

5. The status-conflict control fails, showing the F51 test can reject a parent with incompatible descent statuses.

6. This step does not assert root-level physical closure.
