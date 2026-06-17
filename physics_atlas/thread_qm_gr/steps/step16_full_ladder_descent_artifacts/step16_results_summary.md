# Step 16 Results Summary

## Orientation

Step 16 assembles the three finite-carrier rungs into one candidate bridge structure:

```text
L = (compressed currency u, shadow-commuting refinement lift, shared audit A_u)
```

This is a full-ladder descent audit on the declared toy carrier. It is not a root closure.

## Assembled L

Currency:

```text
u = (d0 density, d1 phase, d2 transport, d3 curvature)
d_L = 4
d_union = 6
```

Endpoint shadows:

```text
S_QM(u) = (d0, d1, d2)
S_GR(u) = (d0, d2, d3)
```

Audit:

```text
A_u = (0.70, 0.20, -0.40, 0.35)
```

Refinement:

The Step-14 shadow-commuting lift is used on the currency carrier.

## Full-Ladder Test

The assembled adequacy residual combines:

- endpoint currency recovery,
- endpoint audit recovery and restriction,
- refinement stability,
- audit consistency,
- compression,
- single-layer criterion.

| case | level | adequacy residual | verdict |
|---|---:|---:|---|
| `candidate_L` | 1 | `0.0` | passes |
| `qm_alone` | 1 | `0.47143714685247295` | rejected |
| `gr_alone` | 1 | `0.44578629323337904` | rejected |
| `union_direct_sum` | 1 | `1.4142135623730951` | rejected |
| `candidate_L` | 2 | `0.0` | passes |
| `qm_alone` | 2 | `0.4734736567320079` | rejected |
| `gr_alone` | 2 | `0.45059431243355463` | rejected |
| `union_direct_sum` | 2 | `1.4142135623730951` | rejected |

The union recovers both endpoint shadows, but is rejected because it has `d=6=d_union` and is not one compressed layer.

## Five Constraints

| constraint | status |
|---|---|
| no-union / single-layer | verified |
| compression, `d_L=4<6` | verified |
| currency precedes refinement | verified |
| refinement is a morphism of the two-shadow diagram | verified |
| audit route-consistency on shared modes | verified |

## Verdict

`CANDIDATE BRIDGE STRUCTURE`: the finite ladder assembles into one compressed audited bridge structure on the declared toy carrier, while QM-alone, GR-alone, and union controls all fail.

This is flagged for external review under:

```text
EXTERNAL_REVIEW_FRAME_TRANSFER_GATE
```

The review question is whether the structural content transfers beyond the toy carrier, or whether it is only a coherent finite chart.

