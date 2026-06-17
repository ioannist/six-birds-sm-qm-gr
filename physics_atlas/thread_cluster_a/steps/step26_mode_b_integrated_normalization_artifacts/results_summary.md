# Step 26 Results Summary

## Record Correction After External Review R7

The normalization `sin^2(theta_W) = 3/8` is NOT part of a candidate-law landing. It is convention-relative recovery of the SU(5)-canonical value on the toy sector trace, and Step 27 showed the convention-dependence of that toy trace. This is recovery of known physics, not a derivation of physical gauge couplings or a neutral law landing.

Generated-vs-input breakdown first: the gauge-sector structure is not a Step-26 primitive. The script reads the Step-23 generated minimal closer from `minimal_closures_step23.csv`: structure `r1|2`, ranks `1|2`, dimensions `2|3`, selected charge vector `3|-2`. Step 26 supplies the trace-zero balance rule and dimension-weighted trace metric, then computes the normalization on that generated structure.

## Integrated Normalization

Computed on the Step-23 generated closer:

- charge unit: `1/6`
- `Tr(Y^2) = 5/6`
- `Tr(T3^2) = 1/2`
- normalization ratio: `5/3`
- weak-mixing relation: `sin^2(theta_W) = 3/8 = 0.375000000000`
- verdict: `INTEGRATED`

This closes the bookkeeping partial relative to Step 21, but after the record correction it is graded only as convention-relative recovery inside the declared GUT-exterior audit chain.

## Negative Controls

The same computation was run on non-generated Step-23 structures:

- `r1|3` computes a different weak-mixing relation, `8/11`.
- `r1|1` fails because the rank-one readout is not unique.
- `rnone` fails because it has no dimensions or charge vector.

The controls pass: the audit does not return the integrated value for arbitrary structures.

## Gates

- Primitive exclusion: pass. The build script contains no hardcoded target value, shape string, or charge-vector string.
- Dependency trace: pass. `dependency_trace_step26.csv` lists the Step-23 closer, balance rule, rank-one readout, and trace metric.
- Ablation: pass. Removing any listed dependency blocks the normalization.
- Negative controls: pass.
- Stage II: pass. Charge quantization is reproduced on the generated structure with integer role charge weights `-3|2|6|1|-4`.
- No single-axiom equivalence: pass.

## Verdict

`DEMOTED_RECOGNITION_RECOVERY`: the weak-mixing normalization `3/8` follows from the trace-zero balance rule on the Step-23 minimal closer, but that closer is now disclosed as carrying the exterior-role and slot-five prior. The normalization is not a candidate-law landing; it is convention-relative recovery on the toy trace.

This is finite-grammar generation only. It is not a physical unification theorem, not a derivation of real couplings, and not a frame-transfer status upgrade.
