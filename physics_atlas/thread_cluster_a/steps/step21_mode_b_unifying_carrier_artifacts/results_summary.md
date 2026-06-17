# Step 21 Results Summary

> **⚠ SUPERSEDED + DEMOTED — see `SUPERSEDED.md`.** Part of the demoted Steps 21-26 arc: this carrier
> HARDCODES the SU(5)/exterior-algebra five-slot `color3|weak2` shape and generates only the (convention-relative,
> per Step 27) normalization. Corrected grade: **finite GUT/exterior recognition recovery, NOT neutral
> generation** (v3 review + Step 28). The honest, un-smuggled result is the neutral hunt (Steps 28-39) + the
> Step-41 Δ_fact recognition-source restatement.

## Mode-B carrier

This step replaces the Step-20 recognition shortcut with a finite Mode-B generation attempt. The carrier primitives are a five-slot operational kernel, a sector lens `q`, bridge operators forgotten by `q`, a primitive trace-neutral integer generator, a trace metric, and dual/pair rewrite operations. The build script excludes the target constants and recognition labels from the carrier definition.

## Computed outputs

- `U` is non-descending: `U_a` and `U_b` have the same `q` readout (`color3|weak2|trace0`) but different bridge readouts, giving obstruction count `1`.
- `C(U)` descends through `q`: the same witness pair has identical audited expression, so the `C(U)` obstruction count is `0`.
- The generated primitive weights are `color=-2`, `weak=3`, with charge unit `1/6`.
- The generated trace audit gives `Tr(charge^2)=5/6`, `Tr(T3^2)=1/2`, normalization ratio `5/3`, and weak-mixing relation `3/8`.
- This matches the Step-20 SU(5)-normalized value after generation. The recognition is downstream of the audit, not a carrier primitive.
- Stage II reproduction passes: the generated dual/pair rewrite content has zero mixed color-charge, mixed weak-charge, cubic-charge, and charge-gravity anomaly sums.

## Six no-smuggling gates

All six gates pass:

1. Primitive exclusion: target constants and recognition names are absent from the build-script carrier definition.
2. Dependency trace: `dependency_trace_step21.csv` lists axioms `A1` through `A7`.
3. Ablation: each axiom removal blocks at least one required closure component; no single axiom is equivalent to the target.
4. Negative controls: two nearby false ratios and one non-grid charge are rejected.
5. Stage II earning: anomaly-balance reproduction is computed before accepting the target relation.
6. No single-axiom equivalence: every ablation row marks `single_axiom_equivalent_to_target=False`.

## Verdict

`PASS-with-recognition`: the finite Mode-B kernel generates the coupling-normalization relation and charge grid from its operational trace signature, and recognition-lands on the SU(5)-shaped value after the audit. This is a finite generated carrier result, not a claim that physical unification is closed. The Step-20 real-world non-SUSY near-miss still stands.
