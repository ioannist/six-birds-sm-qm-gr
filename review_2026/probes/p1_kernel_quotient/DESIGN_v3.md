# P1-HYGIENE v3 design

- `active_cut_quotient_v2.py` is imported under a literal SHA-256 pin; v2 artifacts are retained unchanged.
- Delta-to-Y replaces exactly three triangle edges by three star legs `w01+w02`, `w01+w12`, `w02+w12`. Y-to-Delta is admitted only when all inverse half-sum capacities are strictly positive.
- A proposed replacement is certified only if full exact boundary-cut re-enumeration preserves every rational value and all minimizers remain unique. The original four moves then run to closure, with the same check after each accepted move.
- The maintained finite closure explores every verified presentation through three Delta-Y/Y-Delta replacement rounds, including equal/intermediate presentations. The declared depth is exhaustive for this search family and prevents inverse-replacement oscillation.
- The named K2,3 regression exports an audit row after every accepted move. Region count, exact value preservation, uniqueness, and rational incidence rank are recomputed at every row.
- Experimental K2,3 directions are alternating plus/minus redistributions on four-cycle transportation cells. Experimental K4 directions transfer equal capacity between opposite perfect matchings. A direction could explain a residual only if it lies exactly in the incidence nullspace, survives finite perturbations at both signs with every active cut unchanged, and the accepted-direction span equals the full residual deficiency.
- Experimental rules are diagnostics only and are never passed into the certified five-move closure.
