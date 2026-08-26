# P3-REPAIR-1: Full-carrier Delta_fact findings

## Corrected table

| RS status | clean (evaluated) | breaking (evaluated) | Delta undefined | Total |
|---|---:|---:|---:|---:|
| RS_false | 9222 | 918 | 1826 | 11966 |
| RS_true | 24 | 0 | 0 | 24 |

Headline counts: RS = 24; RS and breaking = 0; breaking total = 918; clean total = 9246; Delta undefined = 1826.

The strong finite-carrier implication survives: every record-stable row has an evaluated empty Delta_fact, and no record-stable row is Delta-undefined.

## Anti-circularity witnesses

“Satisfying conjunct and breaking” means the named RS conjunct is true without requiring either of the other conjuncts. “Exclusive-only” is the stricter subset for which both other conjuncts are false.

| Conjunct | Satisfying conjunct and breaking | Exclusive-only breaking | Example carrier:pair-count |
|---|---:|---:|---|
| substrate | 60 | 0 | carrier_00827:48, carrier_00836:48, carrier_00837:48, carrier_00838:48, carrier_00847:48 |
| capacity | 106 | 8 | carrier_07580:12, carrier_07586:12, carrier_07646:12, carrier_07648:12, carrier_07650:12 |
| distinguishability | 686 | 528 | carrier_00733:12, carrier_00762:12, carrier_00798:12, carrier_00811:12, carrier_00818:48 |

## No-confinement semantics — declaration for reviewer ruling

A structure with no confining factor is not honestly classifiable as either clean or breaking under this Delta_fact construction. Step 41 defines its interference sectors relative to a selected confining subgroup, so without such a factor there is no typed pi_conf projection and therefore no Delta_fact proposition to evaluate. Calling the empty set “clean” would manufacture a vacuous success by extending the function outside its declared domain; calling it “breaking” would manufacture a defect with no interference-sector comparison. This repair therefore records `delta_undefined_no_confinement` as a third outcome. The physically honest reading is that “clean separation” requires confinement as a domain prerequisite; whether the prediction should explicitly include that prerequisite is a semantics declaration reserved for reviewer ruling.

## Determinism and integrity

The carrier order and all RS inputs follow Step 59. Delta_fact is evaluated with Step 41 for every row having a confining subgroup, irrespective of substrate or higher-layer pass status. All five direct or transitive imported build scripts are checked against literal SHA-256 pins before import. `p3_full_carrier_delta_scores.csv` has SHA-256 `c202e246841a9d4bb03bda9f23f3a90a2b862200d5747c9a8cfcc9fd548e907b`. The validator uses seed 20260826 to rederive 32 evaluated rows.
