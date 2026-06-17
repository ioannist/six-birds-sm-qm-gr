# Step 3 Results Summary

## Orientation

Step 3 builds the P6 decaying-degeneracy audit for the Cluster A selection layer. The degeneracy `g(n)` is the number of anomaly-free Step-2 survivors still in play at refinement level `n`.

## Genuine Selection Refinement

The genuine selection sequence is `9->5->4->2->1->1`. It starts from the Step-2 survivor count `9` and ends at `1`, the selected world `w_SM`.

Removed candidates by level:

- level 0 `level_0_post_anomaly_survivors`: removed `none`; survivors `w_SM;w_alt_gauge;w_alt_rep;w_two_gen;w_four_gen;w_high_ew;w_alt_uv;w_alt_vacuum;w_joint_alt`.
- level 1 `level_1_gauge_generation_resolution`: removed `w_alt_gauge;w_two_gen;w_four_gen;w_joint_alt`; survivors `w_SM;w_alt_rep;w_high_ew;w_alt_uv;w_alt_vacuum`.
- level 2 `level_2_rep_texture_resolution`: removed `w_alt_rep`; survivors `w_SM;w_high_ew;w_alt_uv;w_alt_vacuum`.
- level 3 `level_3_scale_uv_resolution`: removed `w_high_ew;w_alt_uv`; survivors `w_SM;w_alt_vacuum`.
- level 4 `level_4_vacuum_resolution`: removed `w_alt_vacuum`; survivors `w_SM`.
- level 5 `level_5_stabilized_selected_point`: removed `none`; survivors `w_SM`.

The selection degeneracy is monotone non-increasing: `True`.

## Unselected Landscape Control

The landscape control uses the same Step-2 survivor set but receives no selection-resolution predicate. Its sequence is `9->9->9->9->9->9` and final degeneracy remains `9`.

## P6 Audit

- Genuine selection: stabilizes to selected point `True`.
- Landscape: non-decaying degeneracy `True`.
- Final selection increment: `0`.
- Final landscape increment: `0`.

## Controls

- Decays-vs-not: `True`.
- Monotone: `True`.
- Lands on `w_SM`: `True`.
- Landscape not secretly selecting: `True`.
- Carrier guard: candidate-space plus measure-refinement audit.

## Verdict

`p6_decaying_degeneracy_audit_constructed`.

The finite toy distinguishes a genuine selection layer from an unselected landscape: genuine selection drives degeneracy down to the selected point, while the landscape remains multiply degenerate.
