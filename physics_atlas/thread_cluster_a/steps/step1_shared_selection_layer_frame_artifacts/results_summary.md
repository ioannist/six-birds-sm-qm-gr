# Step 1 Results Summary

## Orientation

Cluster A starts from a finite candidate space `W` of SM-structure worlds plus a measure `mu`. This is a selection/measure construction: the carrier is the candidate space plus measure, and the non-descending object is the selection functional.

## Candidate Space

`W` has `9` admissible toy worlds. The realized token is `w_SM`. Each world carries stand-in attributes for gauge/rep, generation/texture, EW scale, UV-completion, and vacuum facets. These are toy codes, not real group theory or physical values.

## Selection Measure

The measure `mu_score` is computed for every world. `w_SM` is the genuine argmax with score `106.0`. The selection is therefore made by the measure, not by a hand tag.

## SM Selection-Forgetting Shadow

The SM Sigma readout is modeled as `SM_FIXED_REALIZED_INPUTS`: it reads the realized inputs as fixed and carries no predicate over `W` and no measure over alternatives.

## Non-Descending Signatures

- `joint_structure_variable`: obstruction `36`, witnesses `w_SM-w_alt_gauge;w_SM-w_alt_rep;w_SM-w_two_gen;w_SM-w_four_gen;w_SM-w_high_ew;w_SM-w_alt_uv;w_SM-w_alt_vacuum;w_SM-w_joint_alt;w_alt_gauge-w_alt_rep;w_alt_gauge-w_two_gen;w_alt_gauge-w_four_gen;w_alt_gauge-w_high_ew;w_alt_gauge-w_alt_uv;w_alt_gauge-w_alt_vacuum;w_alt_gauge-w_joint_alt;w_alt_rep-w_two_gen;w_alt_rep-w_four_gen;w_alt_rep-w_high_ew;w_alt_rep-w_alt_uv;w_alt_rep-w_alt_vacuum;w_alt_rep-w_joint_alt;w_two_gen-w_four_gen;w_two_gen-w_high_ew;w_two_gen-w_alt_uv;w_two_gen-w_alt_vacuum;w_two_gen-w_joint_alt;w_four_gen-w_high_ew;w_four_gen-w_alt_uv;w_four_gen-w_alt_vacuum;w_four_gen-w_joint_alt;w_high_ew-w_alt_uv;w_high_ew-w_alt_vacuum;w_high_ew-w_joint_alt;w_alt_uv-w_alt_vacuum;w_alt_uv-w_joint_alt;w_alt_vacuum-w_joint_alt`.
- `E019_gauge_group`: obstruction `21`, witnesses `w_SM-w_alt_gauge;w_SM-w_alt_rep;w_SM-w_joint_alt;w_alt_gauge-w_alt_rep;w_alt_gauge-w_two_gen;w_alt_gauge-w_four_gen;w_alt_gauge-w_high_ew;w_alt_gauge-w_alt_uv;w_alt_gauge-w_alt_vacuum;w_alt_gauge-w_joint_alt;w_alt_rep-w_two_gen;w_alt_rep-w_four_gen;w_alt_rep-w_high_ew;w_alt_rep-w_alt_uv;w_alt_rep-w_alt_vacuum;w_alt_rep-w_joint_alt;w_two_gen-w_joint_alt;w_four_gen-w_joint_alt;w_high_ew-w_joint_alt;w_alt_uv-w_joint_alt;w_alt_vacuum-w_joint_alt`.
- `E020_generations_texture`: obstruction `21`, witnesses `w_SM-w_two_gen;w_SM-w_four_gen;w_SM-w_joint_alt;w_alt_gauge-w_two_gen;w_alt_gauge-w_four_gen;w_alt_gauge-w_joint_alt;w_alt_rep-w_two_gen;w_alt_rep-w_four_gen;w_alt_rep-w_joint_alt;w_two_gen-w_four_gen;w_two_gen-w_high_ew;w_two_gen-w_alt_uv;w_two_gen-w_alt_vacuum;w_two_gen-w_joint_alt;w_four_gen-w_high_ew;w_four_gen-w_alt_uv;w_four_gen-w_alt_vacuum;w_four_gen-w_joint_alt;w_high_ew-w_joint_alt;w_alt_uv-w_joint_alt;w_alt_vacuum-w_joint_alt`.
- `E043_EW_scale`: obstruction `14`, witnesses `w_SM-w_high_ew;w_SM-w_joint_alt;w_alt_gauge-w_high_ew;w_alt_gauge-w_joint_alt;w_alt_rep-w_high_ew;w_alt_rep-w_joint_alt;w_two_gen-w_high_ew;w_two_gen-w_joint_alt;w_four_gen-w_high_ew;w_four_gen-w_joint_alt;w_high_ew-w_alt_uv;w_high_ew-w_alt_vacuum;w_alt_uv-w_joint_alt;w_alt_vacuum-w_joint_alt`.
- `E009_UV_completion`: obstruction `14`, witnesses `w_SM-w_alt_uv;w_SM-w_joint_alt;w_alt_gauge-w_alt_uv;w_alt_gauge-w_joint_alt;w_alt_rep-w_alt_uv;w_alt_rep-w_joint_alt;w_two_gen-w_alt_uv;w_two_gen-w_joint_alt;w_four_gen-w_alt_uv;w_four_gen-w_joint_alt;w_high_ew-w_alt_uv;w_high_ew-w_joint_alt;w_alt_uv-w_alt_vacuum;w_alt_vacuum-w_joint_alt`.
- `E037_vacuum`: obstruction `14`, witnesses `w_SM-w_alt_vacuum;w_SM-w_joint_alt;w_alt_gauge-w_alt_vacuum;w_alt_gauge-w_joint_alt;w_alt_rep-w_alt_vacuum;w_alt_rep-w_joint_alt;w_two_gen-w_alt_vacuum;w_two_gen-w_joint_alt;w_four_gen-w_alt_vacuum;w_four_gen-w_joint_alt;w_high_ew-w_alt_vacuum;w_high_ew-w_joint_alt;w_alt_uv-w_alt_vacuum;w_alt_uv-w_joint_alt`.
- `selection_underdetermination`: obstruction `1`, witnesses `mu_A-mu_B`.

The five target edges are facets of the joint selection variable. The selection underdetermination row uses two different measures with the same selected realized world but different off-selected scores, so the measure is not determined by the realized SM values.

## Controls

- Descending observable control: obstruction `0`.
- Argmax control: `True`.
- Carrier guard: candidate-space plus measure, no field-readout pair.

## Verdict

`shared_selection_layer_frame_established`.

The SM's free inputs are selected/read out from `L*` and are non-descending from the SM selection-forgetting Sigma on this finite carrier. The five edges are facets of one selection/measure layer. The single-layer coincidence remains a flagged hypothesis; the per-facet non-descending computation does not depend on that coincidence.
