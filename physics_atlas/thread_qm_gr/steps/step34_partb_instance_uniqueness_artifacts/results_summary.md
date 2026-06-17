# Step 34 Results Summary

## Orientation

Step 34 is Part B instance-uniqueness inside the already selected F24 family `BridgeMediatedRole`.  It tests whether the constructed co-sourcing package `L` is the unique minimal admissible common refinement of `q_QM` and `q_GR`, up to equivalence, on the declared finite carrier.

The computation uses the actual Step 17/18/21/33 finite maps:

- `q_QM = (d0_density,d1_phase,d2_transport)`.
- `q_GR = (d0_density,d2_transport,d3_curvature)`.
- `L = (d0_density,d1_phase,d2_transport,d3_curvature)`.

## Join Computation

`instance_uniqueness_step34.py` computes linear row-span factorization of quotient maps.  Both endpoint quotients factor through `L` with residual `0.0`, so `L` refines both endpoint accesses.

The modes of `L` are exactly the union of endpoint-distinguished directions:

`{d0_density,d1_phase,d2_transport} ∪ {d0_density,d2_transport,d3_curvature} = {d0_density,d1_phase,d2_transport,d3_curvature}`.

Thus `L` is the finite coordinate-lattice join of `q_QM` and `q_GR`.

## Exhaustion

The mediator candidate table partitions the tested space:

- `L_join`: admissible, minimal, relation `is_join`.
- Four drop-one-mode candidates: all fail to carry both endpoints by positive linear obstruction.  The endpoint residuals are `0.5773502691896258` for each missing required mode case.
- `M_super_5mode = L + d4_extra`: admissible but non-minimal.  `L` factors through `M` with residual `0.0`; `M` does not factor through `L` with residual `0.4472135954999579`.
- `union_direct_sum = (d0,d1,d2,d0,d2,d3)`: both endpoints factor through it, but it is non-admissible because rank is `4` in dimension `6`, with `extra_coordinate_count = 2`.
- `L_prime_relabel`: isomorphic to `L` by an explicit permutation, with residual `0.0` in both directions.

Finite-pair obstruction witnesses are also reported.  Some dropped-mode failures have no pair witness on this sparse carrier; in those rows the positive linear row-span residual is the deciding quotient-lattice obstruction.

## Verdict

Typed verdict: `instance_uniqueness_minimal_common_refinement_up_to_equivalence`.

On the declared finite coordinate-lattice carrier, `L` is the unique minimal admissible common refinement of `q_QM` and `q_GR`, up to isomorphism:

- sub-minimal objects fail to carry both endpoints;
- super-minimal admissible objects are non-minimal refinements of `L`;
- the direct-sum union is non-admissible;
- other minimal 4-mode presentations are equivalent to `L` by relabeling.

Combined with Step 33 type-uniqueness, this establishes bounded-grammar uniqueness of the co-sourcing reconciliation in the precise sense supported here: unique minimal mediated common refinement, up to equivalence.

## Frontier

This does not say `L` is the only admissible object.  The 5-mode object proves admissible refinements above `L` exist.  The uniqueness notion is minimality up to equivalence.  Frame transfer to richer carriers and physical models remains external review.
