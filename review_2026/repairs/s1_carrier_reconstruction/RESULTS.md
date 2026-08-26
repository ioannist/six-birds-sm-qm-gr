# S1-REPAIR-1 results

## Stage-resolved flow

| stage | input population | population | excluded count | exclusion percent |
|---|---|---|---|---|
| neutral_carrier | 281241820 | 281241820 | 0 | 0.000000 |
| genuinely_chiral | 281241820 | 1066 | 281240754 | 99.999621 |
| atomic_packaging | 1066 | 84 | 982 | 92.120075 |
| closure_consistency | 84 | 62 | 22 | 26.190476 |
| chirality_faithfulness | 62 | 52 | 10 | 16.129032 |
| higher_layer_mass_closure_proxy | 52 | 8 | 44 | 84.615385 |
| clean_separation | 8 | 4 | 4 | 50.000000 |

Each exclusion percentage is relative only to the immediately preceding row. The reconstructed corrected-carrier headline is 1,066 genuinely chiral multisets, not 11,990. From that sound chiral denominator through chirality-faithfulness, the exclusion is 95.121951%, replacing the published 99.332777% (11,990 to 80).

## Old versus new

| stage | published count | reconstructed count | count change |
|---|---|---|---|
| neutral_carrier |  | 281241820 |  |
| genuinely_chiral | 11990 | 1066 | -10924 |
| atomic_packaging | 156 | 84 | -72 |
| closure_consistency | 130 | 62 | -68 |
| chirality_faithfulness | 80 | 52 | -28 |
| higher_layer_mass_closure_proxy | 12 | 8 | -4 |
| clean_separation | 8 | 4 | -4 |

The published 280,983 Step-28 count is not shown as a like-for-like neutral denominator: it was already anomaly-filtered and used distinct-field set semantics. The comparable published corrected chiral carrier is 11,990; it moves to 1,066. The later populations move 156→84, 130→62, 80→52, 12→8, and 8→4.

## Selection conclusion

The structural conclusion survives: the higher-layer proxy leaves exactly `2|3` and SU(4)-alone, and clean separation leaves exactly `2|3`. The higher-layer family is split 4+4 rather than the published 8+4. Every repaired `2|3` survivor has coset count 0 and empty Step-41 defect; every SU(4)-alone survivor has coset count 6 and 48 defect pairs. Therefore the 6-vs-0 discriminator survives on the sound carrier. The declared SM reference row survives every stage, including clean separation.

## Representation gate

`representation_model.py: PASS: declared_rep_instances=21 canonical_rep_instances=14 checks=140`

The higher-layer mass-closure stage remains explicitly `PROXY`; this packet repairs the representation carrier and multiset semantics, not that predicate's physical status. The retained route-incidence restriction likewise awaits the roster-based competitor packet.
