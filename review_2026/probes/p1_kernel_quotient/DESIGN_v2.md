# P1-REPAIR-2 exact design

- All v1 probe machinery is imported read-only under a literal SHA-256 pin; the frozen Step42/44/55 pins remain enforced transitively.
- For each boundary region, boundary vertices are fixed to opposite cut sides and all interior assignments are enumerated. Exact integerized rational capacities determine the unique minimum, runner-up margin, cut-side assignment, and 0/1 edge-incidence row.
- Saturated-terminal/zero-column contraction and inseparable-vertex contraction identify endpoints never separated by any active cut. Contraction automatically merges parallel edges by capacity sum.
- A bivalent interior vertex is replaced by an edge of capacity equal to the minimum of its two incident capacities. A boundary-free subgraph with exactly two external gateways is replaced by its exact gateway min-cut capacity.
- Reduction moves run to closure. Every proposed graph is independently re-enumerated, and a move is retained only when all boundary-region minimum values are byte-for-byte equal as rational numbers and minimizers remain unique.
- Search weights use moderate rational capacities plus small binary edge perturbations. The perturbations make distinct edge subsets have distinct tie-break contributions, so degenerate active-cut chambers are excluded exactly.
- A residual nullspace is computed by rational RREF and integerized. Finite two-sided checks move within the exact uniqueness margin and re-enumerate every cut; unchanged values are not inferred from a differential calculation.
