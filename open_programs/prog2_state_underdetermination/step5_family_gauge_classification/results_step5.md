# PROG2 Step 5 — corrected C2_L1 family-gauge classification

## Headline

All six pairs are **SURVIVING_FINITE_C2_L1_DECLARED_GAUGE_EXAMPLE**. Each pair has exact-algebraic product, complete-cut-fingerprint, and connected-copy boundary-state equality, while exact terminal-fixed isomorphism, both global-reciprocal comparisons, Step-1 merge applicability, and the exact invariant separate the raw capacity assignments under the frozen corrected family relation.

## Six-row classification

`I(c)` below is the unordered exact pair `{sum c_e, sum c_e^-1}`. Full exact `QQ(alpha)` expressions are exported in `classification_step5.csv`; the table shows leading digits.

| id | I(base), leading digits | I(displaced), leading digits | direct iso | global reciprocal maps | Step-1 merges | exact I differs | classification |
|---|---|---|---:|---:|---:|---:|---|
| cand_01 | `{14.5400000596010067965835 ; 13.5388501520053632251750}` | `{14.5400000596010067965835 ; 13.5388494045343806534866}` | False | False | 0 | True | **SURVIVING_FINITE_C2_L1_DECLARED_GAUGE_EXAMPLE** |
| cand_02 | `{14.5400000596010067965835 ; 13.5388501520053632251750}` | `{14.5400000596010067965835 ; 13.5388493383183409032084}` | False | False | 0 | True | **SURVIVING_FINITE_C2_L1_DECLARED_GAUGE_EXAMPLE** |
| cand_03 | `{15.9200000763648131396621 ; 10.3508614524823826417880}` | `{15.9200000763648131396621 ; 10.3508617543062000536972}` | False | False | 0 | True | **SURVIVING_FINITE_C2_L1_DECLARED_GAUGE_EXAMPLE** |
| cand_04 | `{15.9500000903346517588943 ; 10.2803854442487615595170}` | `{15.9500000903346517588943 ; 10.2803885943751228584537}` | False | False | 0 | True | **SURVIVING_FINITE_C2_L1_DECLARED_GAUGE_EXAMPLE** |
| cand_05 | `{13.9500000856780388858169 ; 11.1191012204453997731438}` | `{13.9500000856780388858169 ; 11.1191092163874226870830}` | False | False | 0 | True | **SURVIVING_FINITE_C2_L1_DECLARED_GAUGE_EXAMPLE** |
| cand_06 | `{13.5500000595719029661268 ; 14.1060373027532140938967}` | `{13.5501527422922021281643 ; 14.1060867902625243636188}` | False | False | 0 | True | **SURVIVING_FINITE_C2_L1_DECLARED_GAUGE_EXAMPLE** |

## Connected-copy parity lemma

The exhaustive local encoding covers copy-tensor ranks 2, 3, 4, and 5. At every rank, exactly two leg subsets return the canonical copy tensor: no legs and all legs. The carrier-level constraint enumeration then finds exactly two assignments on every connected graph: all edge-swap bits zero and all one. Thus only identity and the global reciprocal return to the canonical `C2_L1` family.

## Delta-Y cut/state separation countercheck

For `cand_01`, Delta-Y on `I0+I1+I2` preserves the complete cut fingerprint exactly but changes the copy product by the exact ratio `70406080269220304893479166685119/8728637932116993396730243442760` = `8.06610158615485395649055156008`. Since this is not one, the connected-copy state changes. The move is cut equivalence, not state gauge; no tensor intertwiner is asserted.

## Invariant proof status

The declaration proves `I(c)` generator by generator. Isomorphisms permute terms; internal `g,g^-1` and boundary unitaries do not touch capacities; global reciprocal exchanges the unordered entries. An exact topology census finds no applicable Step-1 series or parallel tensor merge at any of the twelve endpoints, so that generator is vacuous here. All proof checks pass.

## Certified wording

Six exact-algebraic finite `C2_L1` declared-gauge underdetermination examples were constructed. This earns the word *example* because every comparison is exact and the declared invariant proof is complete at this scope. It is not a bulk-geometry theorem and does not extend to other tensor families or gauge relations.
