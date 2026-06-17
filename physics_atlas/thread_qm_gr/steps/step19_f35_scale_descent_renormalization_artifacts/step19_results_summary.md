# Step 19 Results Summary

## Orientation

Step 19 applies FIV F35, Scale Descent / Renormalization, to the toy joint law on `L`.

This is a native scale-descent classification on the finite toy. It is not a root closure.

## Scale Structure

Carrier:

```text
H = finest 16-cell carrier
```

Scale quotients:

```text
Q1_fine16   : 16 singleton cells
Q2_mid8     : 8 two-cell blocks
Q3_coarse4  : 4 four-cell blocks
```

Coarsenings:

```text
c1 : Q1_fine16 -> Q2_mid8
c2 : Q2_mid8   -> Q3_coarse4
```

## Laws

Joint law:

```text
t = A_u applied to the joint state on L
```

The joint state is chosen so `t` is constant on each four-cell block.

Control law:

```text
t_control = alternating fine-cell sign
```

The control depends on sub-scale detail that the coarsening erases.

## F35 Results

| law | scale step | O_n count | descends | c-fiber violations | renormalizes |
|---|---|---:|---:|---:|---:|
| `joint_law` | `Q1_fine16->Q2_mid8` | `0` | true | `0` | true |
| `joint_law` | `Q2_mid8->Q3_coarse4` | `0` | true | `0` | true |
| `non_descending_control` | `Q1_fine16->Q2_mid8` | `0` | true | `8` | false |
| `non_descending_control` | `Q2_mid8->Q3_coarse4` | `8` | false | `0` | false |

The control fails F35: first because the quotient law is not constant on coarsening fibers, then because `O_n` is nonempty at the next scale.

## Verdict

```text
F35 verdict: renormalizes_on_toy
```

The joint law descends and renormalizes across both tested scale steps. The non-descending control fails.

Frame transfer beyond the toy remains external review.

