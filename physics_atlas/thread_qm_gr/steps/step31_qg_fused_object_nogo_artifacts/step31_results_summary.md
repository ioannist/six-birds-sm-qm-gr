# Step 31 Results Summary

## Orientation

Mode T / bounded-grammar no-go preparation: Lemma 2 for the fused-object reading. The tested alternative is a single package with one audit serving both the QM-side Born role and the GR-side stress-energy role.

This is bounded to the framework grammar and finite co-sourced-readout toy model. It is not an absolute claim.

## Active Residual

`R_child_E018_after_directed_reduction_nogo_lemma1`: Lemma 1 blocks directed endpoint reduction. Step 31 tests the other fused-object routes.

## Route 1: Union Package

The direct-sum package uses the object map:

```text
pi_union = (d0,d1,d2,d0,d2,d3)
```

Computed gate diagnostic:

| case | target dimension | rank | extra coordinates | duplicate pairs | `G_nosmuggle` |
|---|---:|---:|---:|---:|---|
| `union_direct_sum` | `6` | `4` | `2` | `2` | fail |
| `nonduplicating_refinement_control` | `4` | `4` | `0` | `0` | pass |

The union route fails because shared observables `d0` and `d2` are duplicated.

## Route 2: Shared Audit

The shared-audit route demands one audit whose restrictions agree with both:

- QM-side Born readout `(rho,j)`;
- GR-side stress-energy readout `(T00,T0i)`.

Using the Step 24 derived field audits:

| mode | equal residual | proportional residual |
|---|---:|---:|
| joint density/transport | `0.9935981568901483` | n/a |
| density `d0` | `0.6944644768578695` | `0.5207123913178113` |
| transport `d2` | `1.2894307568321801` | `0.9994686548331937` |

Thus the derived Born and stress-energy audits do not agree on the shared overlap of this toy. The agreeing-audit control has residual `0.0` and admits a shared audit.

## Route 3: Directed Route

Step 31 cites Lemma 1 from Step 30:

```text
q_GR through q_QM defect count = 8
q_QM through q_GR defect count = 8
route mismatch normalized = 0.5
```

The directed route remains blocked in the bounded grammar by the already-validated Lemma 1 artifact.

## Verdict

Typed verdict: `lemma2_fused_object_blocked_in_bounded_grammar`.

Within the declared finite carrier and grammar:

- union route fails `G_nosmuggle`;
- shared-audit route fails by positive overlap residual;
- directed route is blocked by Lemma 1;
- genuine fusion controls pass.

This is Lemma 2 for the bounded no-go program. It does not stand alone as the full theorem.

## Current Frontier

Next live options:

- Lemma 3: uniqueness or exhaustive search over lawful reconciliation shapes.
- Final bounded theorem only after the no-go routes and uniqueness/exhaustion are all audited.
