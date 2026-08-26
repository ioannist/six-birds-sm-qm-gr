# Q5 LP-duality repair results

All 254 nontrivial boundary regions have unique cuts at Step55 seed 101. The global cut margin is `87921164864559/1250000000000000`. Exact max-flow, cut-dual evaluation, and complementary slackness agree for every region; all 3556 central sensitivity checks stay in the chamber and equal the exported `y_e`.

Corrected identity: **Area(min cut) = dual optimum = sum_e c_e y_e; y_e is the per-edge shadow price (the 0/1 cut-incidence variable in this chamber).** The optimum is a scalar; the shadow prices are the separate edge-indexed variables `y_e`.

## Linearized response

The geometry direction and the virtual-bond filter were fixed before evaluating any entropy. The chamber radius is at least `1155027166312429/35000000000000` in the declared direction. Verdict: **HONEST_NON_MATCH**, maximum absolute response error `0.0182861043816` at tolerance `5e-05`. The state-only can-fail control is nonmatching: `True`. Thus the frozen Step45 conclusion is not recovered at an honest generic base point when the deformation is specified independently.

## Composition / Step50

The actual boundary contraction obeys the computed min-plus rule on the area side, but the Born values do not obey that same rule on all probes. Verdict: **DOWNGRADED_SHARED_MMI_CLASS_DIFFERENT_DEPENDENCIES**. What survives is the weaker computed statement that the co-sourced Born and area ledgers satisfy the same MMI inequality class for the tested triple (`I3_Born=-0.0363459273725`, `I3_area=-4.4408920985e-16`), while depending on state amplitudes and graph capacities respectively.

Backlog: Step44-style GENERIC_VIOLATES verdict naming is noted for a separate hygiene fix and is not changed here.
