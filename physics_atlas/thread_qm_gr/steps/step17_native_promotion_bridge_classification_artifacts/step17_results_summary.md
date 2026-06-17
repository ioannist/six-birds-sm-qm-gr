# Step 17 Results Summary

## Orientation

Step 17 re-grounds the finite construction in native Foundations-III vocabulary.

The classified objects are promotion bridges:

```text
B_QM_to_L
B_QM_to_union
```

The targets are packages:

```text
L_package_toy
union_package_toy
```

## Object Maps

Common finite carrier:

```text
S = finite set of 8 source states in modes (d0,d1,d2,d3)
```

Object maps:

```text
pi_QM    : S -> O_QM       = (d0,d1,d2)
pi_GR    : S -> O_GR       = (d0,d2,d3)
pi_L     : S -> O_L        = (d0,d1,d2,d3)
pi_union : S -> O_union    = (d0,d1,d2,d0,d2,d3)
```

## Strictness

Both promotion bridges are strict over `pi_QM`.

`Delta_fact` witnesses:

```text
L:     3 witness pairs
union: 3 witness pairs
```

Each witness has `pi_QM(s)=pi_QM(s')` and different target observables. Therefore strictness is not the distinguishing gate.

## Eight-Gate Classification

`B_QM_to_L`:

```text
G_suff       pass
G_desc       pass
G_stab       pass
G_ctrl       pass
G_nosmuggle  pass
G_vis        pass
G_audit      pass
G_strict     pass
status       candidate
```

`B_QM_to_union`:

```text
G_suff       pass
G_desc       pass
G_stab       pass
G_ctrl       pass
G_nosmuggle  fail
G_vis        pass
G_audit      pass
G_strict     pass
status       failed_G_nosmuggle
```

## Distinguishing Gate

The native gate excluding the direct-sum package is:

```text
G_nosmuggle
```

Computed defect:

```text
duplicate_pair_count = 2
extra_coordinate_count = 2
row_rank = 4
target_dimension = 6
```

The direct-sum package duplicates the shared observables `d0` and `d2`. Candidate package `L` identifies them once.

## Verdict

`B_QM_to_L` has native status `candidate` on the finite toy.

`B_QM_to_union` has native status `failed_G_nosmuggle`.

The durable correction is: the lawful-package-vs-direct-sum distinction is not strictness. It is the native no-smuggling gate detecting duplicated shared observables.

External review remains required for frame transfer beyond the finite toy.

