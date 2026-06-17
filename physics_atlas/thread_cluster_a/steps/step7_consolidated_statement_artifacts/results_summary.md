# Step 7 Results Summary

## Orientation

Step 7 consolidates Cluster A into a sourced, graded deliverable. It introduces no new computation.

## Deliverables

- `cluster_a_consolidated_statement.tex`
- `consolidated_findings_clustera.md`
- `content_classification.csv`
- `schema.json`
- `nonclaim_boundary.md`
- `run_step7.py`

## Consolidated Content

- Step 1 frame: finite candidate space plus measure, `w_SM` argmax, five non-descending facets.
- Step 2 P2 mechanics: anomaly-freedom prunes `4` anomalous tokens, leaves `9` survivors, selection collapses to `w_SM`.
- Step 3 P6 audit: genuine selection `9->5->4->2->1->1`; landscape `9->9->9->9->9->9`.
- Step 4 E043 scale facet: scale ratio obstruction `3`, derived observable obstruction `0`, both toy horns reach `r_SM`, no-selection remains unfixed.
- Step 5 E009 fiber: realized IR fiber has `6` UV candidates, consistency leaves `3`, selection collapses to `U_SM`.
- Step 6 E043 adjudication: derivation `6->5->4->2->1->1` certifies; broad measure `6->6->6->6->6->6` fails; sharp measure `3->2->2->1->1` certifies.

## Verdict

`cluster_a_deliverable_consolidated_for_review`.

The deliverable states the shape of one SM-selection/measure layer with five facets and a unified collapse-vs-landscape criterion. It supplies no physical SM values or mechanisms and does not certify frame transfer.

## Validator Interface

`python3 run_step7.py` runs this step's self-check only. `python3 run_step7.py --chain` runs Steps 1-6 once each in self mode, then runs this step's self-check.
