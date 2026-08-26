# S6-ABLATION-2 design

- V1 artifacts are retained byte-for-byte; every new artifact is prefixed `s6_v2_` or suffixed `_v2`.
- For a scalar VEV in a fundamental or antifundamental of SU(N), the active factor stabilizer is SU(N-1), with SU(1) omitted. All inactive nonabelian factors remain explicit spectators.
- `H=diag(1,...,1,-N+1)`. The residual U(1) is the primitive integer combination `a Q + b H` solving `a q_phi+b h_phi=0`. No inactive-factor Cartan is permitted.
- Record candidates are UV mesons, N-fold epsilon baryons, or mixed epsilon invariants. They count only when restriction to the branch contains a component neutral under U(1)_res and an exact singlet under every residual factor.
- Singlet existence/multiplicity for two- and three-body products calls the pinned v3 Littlewood--Richardson implementation. Distinct records are canonical Fock contents or orthogonal invariant channels.
