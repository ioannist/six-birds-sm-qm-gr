# Step 25 Results Summary

Generated-vs-input breakdown first: this step does not generate a new closer set. It reuses the Step-24 generated closers as the input set, then computes whether the one-factor closers are F51 parent-shadow structures for the split-sector closer. The bounded generated closer set, the finite content-pattern tags, and the generic dual/pair plus even-envelope rewrite grammar remain inputs to this test.

Record correction after external review R5: descent is computed INSIDE a declared parent-pattern rewrite grammar (`PATTERN_REWRITES`). The content-pattern labels are INPUTS. This audits the `SU(5)`/`SO(10)` parent-shadow relation; it does NOT discover that relation without GUT priors.

## Computed Descent

Child split-sector closer from Step 24:

- `structure_id`: `r1|2_u1`
- dimensions: `2|3`
- selected charge vector: `3|-2`

Per-parent F51 descent audit:

| Parent | Computed rewrite | Charged obstruction | Full obstruction | Verdict |
|---|---:|---:|---:|---|
| `SU(5)` | partition dual/pair rewrite | 0 | 0 | `PASS_EXACT_PARENT_SHADOW` |
| `SO(10)` | even-envelope rewrite with neutral residual | 0 | 1 | `PASS_SCOPED_NEUTRAL_RESIDUAL` |
| `SU(6)_chiral_example` | no parent-quotient rewrite in this grammar | 5 | 5 | `FAIL_NOT_PARENT` |

The fork is therefore not an unstructured split between unrelated closers. At finite-grammar grade, it forms a scoped hierarchy: `SU(5)` is an exact parent-shadow relation for the split-sector closer, while `SO(10)` covers the charged child content with one neutral residual. The `SU(6)_chiral_example` closer fails the same parent test and is the negative control.

## Gates

- Primitive exclusion: pass. The branch target is read from Step-24 generated rows.
- Dependency trace: pass. Every axiom family used in the parent-shadow computation is recorded in `dependency_trace_step25.csv`.
- Ablation: pass. Removing the child target roles, dimension relation, content-pattern rewrite, or charge preservation blocks the descent support.
- Negative control: pass. `SU(6)_chiral_example` fails by computed obstruction.
- Stage II: pass. The generated child branch roles reproduce charge-gravity and cubic-charge balance, both zero.
- No single-axiom equivalence: pass. No single declared axiom is equivalent to the answer.

## Verdict

`HIERARCHY_SCOPED`: the Step-24 criterion-dependent fork dissolves into a parent-shadow hierarchy at finite-grammar grade, with a precise caveat. `SU(5)` is exact; `SO(10)` is scoped by a neutral residual; `SU(6)_chiral_example` is not a parent in the declared grammar.

This is not a physical gauge-unification claim, not a new theory, and not frame-transfer certification. It is a computed finite-carrier relation among the generated closers.
