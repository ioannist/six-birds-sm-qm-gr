# S3-REPAIR-1b verification closure

## Full commutant

The centralizer is now computed over all 24 traceless Hermitian SU(5) directions, not a diagonal ansatz. The exact commutator system has 312 nonzero rational component equations, coefficient rank 23, and nullity 1. Its unique direction is diagonal only as an output, with primitive pattern `(-2, -2, -2, 3, 3)`. Therefore the proved centralizer dimension is 1.

## Extracted F48 lattice

The three coroot columns are extracted from the constructed Cartans as `B0_D_1`, `(B0_D_2-B0_D_1)/2`, and `B1_D_1`. Their coordinates in `e_i-e_4` are `[(1, -1, 0, 0), (0, 1, -1, 0), (0, 0, 0, 1)]`. Exact Smith reduction gives rank 3, invariants `(1, 1, 1)`, annihilator `(1, 1, 1, 0)`, free rank 1, and centralizer-loop index 6.

With the explicitly supplied topology inputs `H connected`, `pi_1(SU(5))=0`, and `pi_2(SU(5))=0`, the exact sequence has kernel free rank 1 and yields `pi_2(SU(5)/H)=Z`.

## SU(4) fixed-slice ruling

All six SU(4) roots are mapped as matrices into the fixed weak-index SU(5) slice. The SU(4) root charges are `±4/3`; the mapped SU(5) charges are `±5/6`; their computed ratio is `5/8` for all six roots.

The decisive witness is computed directly:

`[E_34,E_03] = -1*E_04`,

and `E_04` is outside the six-dimensional slice. Hence the slice is not SU(2)-invariant. The six-generator identity is refuted; the fixed-slice analogue relation lands.

## Product-parent control

The well-posed semisimple product attempt is Pati-Salam `SU(4)xSU(2)_LxSU(2)_R`. The SU(4) centralizer constructs `B-L=(1/3,1/3,1/3,-1)`. Requiring the colorless right-doublet neutral state fixes `Y=T3_R+(B-L)/2`. On the constructed `(4,2,1)+(4bar,1,2)` weights,

- `Tr(T3_L^2)=2`;
- `Tr(Y^2)=10/3`;
- `Tr(Q^2)=16/3`;
- `Tr(T3_L^2)/Tr(Q^2)=3/8`.

Thus this product parent gives `3/8`, not `3/23`. Moreover, a product group does not force equality of its independent factor couplings. The only reproduced `3/23` is recomputed at the freely inserted choice `lambda=2` in the reductive `SU(3)xSU(2)xU(1)` model. That model is not semisimple and does not derive the U(1) scale. No well-posed `3/23` product parent was found, so the paper's product-parent statement remains an unsupported import and requires correction; this does not prove that every exotic product embedding is impossible.

## Updated claim ledger

| Claim | Status | Computed result | Residual assumption or convention |
|---|---|---|---|
| SU5 hypercharge direction | LANDED-BY-CONSTRUCTION | full commutant rank=23 nullity=1; primitive (-2, -2, -2, 3, 3) | regular 3+2 embedding; overall sign and charge unit |
| k_Y and weak-angle ratio | LANDED-BY-CONSTRUCTION | k_Y=5/3; sin2(theta_W)=3/8 | weak-pair unit; Q=T3+Y |
| SU5 X/Y coset | LANDED-BY-CONSTRUCTION | 12 roots: (3,2,-5/6)+(3bar,2,5/6) | regular block embedding |
| step41 six-generator identity | REFUTED-BY-CONSTRUCTION | six-root slice is not SU2-invariant and is not the 12-root X/Y coset | none within constructed embeddings |
| step41 fixed-slice analogue relation | LANDED-BY-CONSTRUCTION | 6/6 roots mapped; charge rescale=5/8; [E_34,E_03]=-E_04 outside slice | chosen fixed weak index |
| F27 baryon descent | LANDED-BY-CONSTRUCTION | 12/12 coset actions change B; SM subalgebra preserves B | left-chiral baryon assignment from color type |
| F48 monopole | LANDED-BY-CONSTRUCTION | extracted coroot rank=3; free rank=1; index=6; pi2=Z | H connected; pi1(SU5)=0; pi2(SU5)=0 |
| product parent yields 3/23 | REMAINING-IMPORT | constructed Pati-Salam trace ratio=3/8; 3/23 only from arbitrary Y->2Y | no well-posed 3/23 parent found; exotic product embeddings not exhausted |
| unique parent | REMAINING-IMPORT | SU(5) selected only in bounded regular-SU diagnostic | SO(10), E6, and arbitrary embeddings not exhausted |

## Mutation suite

| Mutation/test | Expected | Result | Evidence |
|---|---|---|---|
| perturb_hypercharge_eigenvalue | rejected | PASS | perturbed eigenvalue left the centralizer |
| swap_quark_lepton_role | rejected | PASS | role mismatch at fermion state 0 |
| break_generator_tracelessness | rejected | PASS | basis contains a non-traceless matrix |
| generic_SO5_conjugated_embedding | all invariants unchanged | PASS | commutant/coset/fermion ratios/F27/F48 invariant |
| corrupt_extracted_coroot | rejected | PASS | F48 Smith invariants changed |
| zero_one_coset_action | rejected | PASS | not every SU(5) coset generator mediates Delta B |
| enlarge_SU4_fixed_slice_with_E04 | rejected | PASS | SU2 action no longer proves fixed-slice non-invariance |
