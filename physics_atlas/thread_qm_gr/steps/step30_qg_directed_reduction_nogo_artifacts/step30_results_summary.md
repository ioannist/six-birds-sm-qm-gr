# Step 30 Results Summary

## Orientation

Mode T / bounded-grammar no-go preparation: Lemma 1 for the directed-reduction reading. The tested claim is not an absolute claim. It is scoped to the framework grammar and the finite QM/GR co-sourced-readout model built in the cascade.

## Active Residual

`R_child_E018_after_nonstationary_relational_history`: after building a common-refinement and co-sourcing toy package, Step 30 tests whether either endpoint can instead be treated as a lawful quotient or derivation of the other.

## Structural Factorization Test

Carrier:

```text
L = (d0 density, d1 phase, d2 transport, d3 curvature)
q_QM = (d0,d1,d2)
q_GR = (d0,d2,d3)
```

Computed factorization defects:

| direction | defect count | verdict |
|---|---:|---|
| `q_GR` through `q_QM` | `8` | does not factor |
| `q_QM` through `q_GR` | `8` | does not factor |
| vertical-stack control, coarse through fine | `0` | factors |

The obstruction is concrete: `q_QM` omits `d3`, while `q_GR` omits `d1`.

## Audit Non-Derivability Test

Using the Step 24 derived field audit table, linear held-out diagnostics were computed in both directions.

| direction | target | held-out residual |
|---|---|---:|
| `T[psi]` from `(rho,j)` | joint | `0.5991748529352457` |
| `T00` from `(rho,j)` | component | `0.40156890127173095` |
| `T0i` from `(rho,j)` | component | `0.5443048422989993` |
| `(rho,j)` from `T[psi]` | joint | `0.5776762928080916` |
| `rho` from `T[psi]` | component | `0.33866060907950507` |
| `current_j` from `T[psi]` | component | `0.6503906344364354` |

This extends the Step 24 sourcing result: `T[psi]` is determined by the field, but it is not derived from the Born audit alone, and the Born audit is not recovered from the stress-energy audit alone under this finite held-out diagnostic.

## Route-Mismatch Test

The route diagnostic compares canonical fiber-mean completions of the full `L` carrier from each endpoint quotient:

- route 1: complete from `q_QM`, then read the GR-side content;
- route 2: complete from `q_GR`, then read the QM-side content.

Result:

```text
raw route mismatch = 2.8284271247461903
normalized route mismatch = 0.5
commutes = false
```

Vertical-stack control:

```text
coarse=(x0,x2) factors through fine=(x0,x1,x2)
normalized route mismatch = 0.0
commutes = true
```

The control shows the diagnostic can recognize a genuine directed reduction.

## Verdict

Typed verdict: `lemma1_directed_reduction_blocked_in_bounded_grammar`.

Within the declared grammar and finite carrier:

- neither endpoint quotient factors through the other;
- neither endpoint audit is recovered from the other by the held-out diagnostic;
- the directed route completions do not commute;
- a genuine vertical-stack control passes.

This is Lemma 1 for the bounded no-go program: directed endpoint reduction is blocked in this grammar. It does not claim an absolute result beyond the declared framework and toy model.

## Current Frontier

Next live options for the no-go program:

- Lemma 2: test whether audit fusion into one shared audit is blocked by Step 24 sourcing-vs-sharing.
- Lemma 3: test uniqueness or exhaustive alternatives to the co-sourcing common-refinement.
- Consolidate the bounded no-go only after all lemmas and controls are computed.
