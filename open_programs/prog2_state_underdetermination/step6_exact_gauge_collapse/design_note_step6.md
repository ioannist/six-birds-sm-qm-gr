# PROG2 Step 6 design — exact connected-copy gauge collapse

## Inputs and scope

This step proves a carrier-general, capacity-general lemma for any fixed connected binary-copy (`C2_L1`) tensor network under the declared capacity convention, then reconstructs the six Step-5 pairs as exact instances from the stored Step-4 algebraic endpoints. The direct inputs are hash-pinned in `dependency_pins_step6.csv`; no Step-6 result table is an input to the computation. The convention is

\[
a_e=\sqrt{\frac{c_e}{1+c_e}},\qquad
b_e=\frac{1}{\sqrt{1+c_e}},\qquad c_e>0.
\]

The staged external review and script in `external_input/` are reproduced as a floating-point control. They do not supply the exact certificate.

## Exact product lemma

Every vertex tensor in the structured binary-copy family is supported only when all of its incident indices agree. On a connected graph, equality propagates along paths, so a globally contracted internal assignment is either all zero or all one. Boundary copy legs inherit that common bit. Thus the unnormalized boundary state is

\[
\left(\prod_e a_e\right)|0\cdots0\rangle+
\left(\prod_e b_e\right)|1\cdots1\rangle
\ \propto\
\sqrt{\prod_e c_e}\,|0\cdots0\rangle+|1\cdots1\rangle.
\]

If `P=prod_e c_e`, the normalized squared amplitudes are `P/(1+P)` and `1/(1+P)`. Therefore the normalized state depends on the capacities only through `P`. The program verifies the support statement by exhaustive binary vertex-assignment enumeration on every carrier and computes `P` and both normalized probabilities exactly in each endpoint's `QQ(alpha)` number field.

## Exact diagonal-intertwiner certificate

Orient every stored edge from its stored endpoint `u(e)` to `v(e)`, matching the repository dressing convention: the capacity coefficient is multiplied into the `u(e)` tensor. Let

\[
r_e=\frac{c'_e}{c_e},\qquad \ell_e=\log r_e.
\]

Let `B` be the oriented vertex-edge incidence matrix, with `+1` at `u(e)` and `-1` at `v(e)`. Let `D` have `1/2` at `(u(e),e)` and zero elsewhere. The target-to-base change of the local zero/one copy-amplitude ratio has formal log vector `D ell`.

Insert `G_e=diag(exp(x_e),1)` at `u(e)` and its inverse at `v(e)`. This changes the local zero/one ratio by formal log vector `B x`. Hence the tensor-level intertwiner condition is

\[
B x=D\ell.
\]

The exact endpoint computation gives `prod_e r_e=1`, so `sum_e ell_e=0`. For a connected graph, exact rational linear algebra gives `rank(B)=|V|-1`, with left kernel spanned by the all-ones vertex vector. Therefore `D ell` is in the image of `B` because its component sum is `(1/2) sum_e ell_e=0`.

This proves the existence statement for every positive equal-product pair on any fixed connected `C2_L1` carrier, not only for the six stored pairs. The implementation avoids using approximate logarithms. It eliminates the final formal log variable with `ell_last=-sum_{e<last} ell_e`, yielding a rational reduction matrix `R`. It then solves over `QQ` for a rational exponent matrix `X` and verifies the exact matrix identity

\[
B X=D R.
\]

Row `e` of `X` defines `G_e` as a positive monomial in the independent ratios with exact rational exponents. The inverse endpoint carries the negated exponent row, and the program verifies their per-edge cancellation exactly. At every vertex the gauged base tensor and target tensor consequently have the same zero/one amplitude ratio and are proportional by a vertex scalar. Contracting all vertices changes only the overall unnormalized scalar.

## Evidence taxonomy

- `COMPUTED`: rebuilt from pinned algebraic endpoints by exact number-field arithmetic, exact rational matrix operations, or exhaustive finite enumeration.
- `PROVED_BY_DEFINITION`: follows from the frozen Step-5 stipulation that capacity labels are ontic and that internal tensor gauge does not act on them.
- `EXTERNAL_REPRODUCED`: the staged external floating-point construction rerun against this checkout; it is a numerical cross-check only.

The distinction is load-bearing: exact differences in `I(c)` are computed, but treating those differences as decorated-object inequivalence under the deliberately narrow frozen relation is proved by that relation's definition, not by a state-level invariant.
