# Step 17 Distinguishing Gate

The native distinguishing gate is:

```text
G_nosmuggle
```

Both promotion bridges are strict over `QM_package_toy`:

```text
B_QM_to_L: Delta_fact count = 3
B_QM_to_union: Delta_fact count = 3
```

Strictness therefore does not distinguish the candidate package `L` from the direct-sum package.

The direct-sum package fails `G_nosmuggle` because its object map contains duplicated shared observable rows:

```text
row 0 = row 3 = d0
row 2 = row 4 = d2
extra_coordinate_count = 2
```

The candidate package `L` has no duplicated observable rows:

```text
extra_coordinate_count = 0
row_rank = target_dimension = 4
```

Native statement:

```text
A promotion bridge may be strict and still fail G_nosmuggle.
The direct-sum package is rejected because it carries duplicated shared observables instead of identifying them once.
```

