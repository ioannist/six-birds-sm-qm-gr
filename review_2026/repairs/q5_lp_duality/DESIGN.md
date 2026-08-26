# Design

- The graph and generic seed weights are imported from frozen Steps 42 and 55 under literal SHA-256 pins.
- Exact cut values are obtained by enumerating only the five interior-node sides (32 cuts per region). Exact rational Edmonds-Karp supplies a primal witness.
- The dual uses node potentials with `p_source=1`, `p_sink=0` and `y_e >= |p_u-p_v|`; the unique cut supplies its integral optimum.
- The response family is non-circular: rational geometry slopes and a virtual-index diagonal filter are declared independently of all measured entropies.
- The composition attempt contracts one physical boundary index between two carrier copies. It tests, rather than assumes, whether the area min-plus gluing rule also governs Born entropy.
