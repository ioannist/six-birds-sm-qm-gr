# Step 14 Structural Constraint

For the Step-13 neutral currency `u = (d0, d1, d2, d3)` with shadows

- `S_QM(u) = (d0, d1, d2)`,
- `S_GR(u) = (d0, d2, d3)`,

a refinement lift is currency-compatible only if it is a morphism of the two-shadow diagram:

```text
S_QM^{n+1} L_u = L_QM S_QM^n
S_GR^{n+1} L_u = L_GR S_GR^n
```

Equivalently, the lift must preserve the shared currency modes `{d0, d2}` and prevent leakage between the two shadow kernels:

```text
ker(S_QM) = span{d3}
ker(S_GR) = span{d1}
```

The stable lift satisfies this by refining each currency mode block separately. The mixing control violates it by mixing shared modes with distinct modes, producing a nonzero shadow-commutator residual.

This constraint is the durable Step-14 output: a refinement compatible with the compressed currency must commute with both endpoint shadows. Compression alone is not enough.

