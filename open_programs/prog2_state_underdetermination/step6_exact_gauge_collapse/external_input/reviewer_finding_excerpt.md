### The gauge relation is too narrow to support “genuinely inequivalent” state examples

The central weakness is that Step 5 defines internal tensor gauge not to act on capacities (`declaration_step5.md:9-16`). That is a possible convention for a **decorated graph-plus-capacity object**, but it is not forced by the boundary state or by the tensor-network presentation.

For any connected graph in this copy family, let `c` and `c'` be positive assignments with equal products. Orient each stored edge from `u` to `v`, as the code does when dressing only `edge.u` (`step3_kernel_test/step3_core.py:162-178`). Define

\[
 b_v=\frac12\sum_{e:u(e)=v}\log\frac{c'_e}{c_e}.
\]

Equal total product gives `sum_v b_v=0`. On a connected graph, the oriented incidence matrix has image equal to the sum-zero vertex vectors, so there is an edge vector `x` with

\[
 Bx=b.
\]

Insert on each internal edge

\[
 G_e=\operatorname{diag}(e^{x_e},1),\qquad G_e^{-1}
\]

using the repository’s own internal gauge operation. At every vertex, this changes the local zero-versus-one copy-tensor amplitude ratio by exactly the factor required to convert the `c`-canonical tensor into the `c'`-canonical tensor. The transformed local tensor is proportional to the target local tensor; the product of local scalars only changes the unnormalized global state, not its projective normalized state.

I implemented this construction for all six exact pairs. Maximum numerical residuals are approximately `4.5e-16`, and all six pass. Evidence: `prog2_diagonal_gauge_audit.py` and `.log`.

This has a precise interpretation:

- If capacities are held as external ontic labels and gauge is defined never to relabel them, the pairs are inequivalent by definition and the Step-5 invariant separates them.
- If the object under comparison is the tensor-network presentation of the state, the pairs are connected by a natural internal diagonal gauge plus re-canonicalization; no state-level invariant distinguishes them.
- If the object is the joint observable map `(cuts,state)`, the noninjective fibers remain exact regardless of gauge terminology.

The Step-5 relation was also frozen only after the six candidates were already known. Step 4 had tried a broader generated relation and honestly reported every search budget-truncated, leaving all six as candidates (`step4_finite_continuation/results_step4.md:7-22,35-41`). Step 5 then replaced that unresolved relation with a narrower family relation and an invariant tailored to the permitted capacity actions (`declaration_step5.md:1-3`; `step5_core.py:25-35`). This does not invalidate the finite theorem, but it means “frozen before classification” is not independent preregistration of the gauge concept before candidate selection.

**Finding P2-3: the exact fibers survive; robust state/bulk inequivalence does not. Confidence 0.96.**

### Is excluding weighted Delta–Y legitimate?

The repository’s exact countercheck is useful. On `cand_01`, a particular cut-preserving Delta–Y move changes the copy product by the exact factor

\[
\frac{70406080269220304893479166685119}
{8728637932116993396730243442760}\neq1,
\]

so cut equivalence alone does not imply `C2_L1` state equivalence (`delta_y_countercheck_step5.csv`; `step5_core.py:162-173`). It is therefore legitimate to reject the blanket rule “every cut-preserving Delta–Y move is state gauge.”

It is not legitimate to infer that **no** weighted Delta–Y instance can belong to a state gauge. A special move could preserve the product or admit a tensor-level intertwiner. Admission should be instance-specific and based on the state/tensor map, not excluded by class name.

### Required replacement wording for PROG2

Use:

> In the connected binary-copy convention `C2_L1`, the normalized boundary state depends only on the edge-capacity product. Six exact positive-algebraic same-graph pairs were constructed with identical complete terminal cut functions and equal products, hence identical boundary states. They establish exact noninjectivity of the joint cut/state map. They are separated by `I(c)` only under a deliberately narrow capacity-label-preserving family relation; no physically complete bulk gauge relation or inequivalent tensor-presentation theorem is claimed.

Calling the finite algebraic subproblem “completed” is fair. Calling the original physically quotiented bulk-underdetermination program “resolved” is not.

---

