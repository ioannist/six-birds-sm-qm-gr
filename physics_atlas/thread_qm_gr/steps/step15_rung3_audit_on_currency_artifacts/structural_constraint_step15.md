# Step 15 Structural Constraint

For the neutral currency

```text
u = (d0, d1, d2, d3)
QM shadow = (d0, d1, d2)
GR shadow = (d0, d2, d3)
shared modes = {d0, d2}
```

a single bridge audit `A` on `u` exists exactly when the endpoint audits agree on the shared modes:

```text
A_QM|_{d0,d2} = A_GR|_{d0,d2}
```

When this condition holds, `A` is formed by taking the shared coefficients once and appending the two endpoint-specific coefficients:

```text
A_u = (shared d0, QM-specific d1, shared d2, GR-specific d3)
```

The audit must also commute with the refinement lift from Step 14:

```text
A_u^{n+1} L_u = L_A A_u^n
```

The route-mismatch control violates the shared-mode equality. It still has endpoint audits, but no single audit on `u` restricts to both. This recovers the framework-side P3 condition: route consistency is equality of audit prices on the shared currency overlap.

