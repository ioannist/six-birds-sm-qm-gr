# S3 generator-construction results

## Outcome

The regular block embedding on indices `(0,1,2)|(3,4)` has a one-dimensional diagonal centralizer. Exact row reduction gives the primitive direction `(-2,-2,-2,3,3)`. Giving the weak-pair state of `wedge^2(5)` unit charge fixes the displayed convention and produces

`Y = (-1/3,-1/3,-1/3,1/2,1/2)`.

This is a derivation of the direction from the embedding. Its overall sign and scale remain coordinate conventions; the standard scale is `1/6`.

## Ratios and fermions

Acting with the embedded algebra on `5bar + wedge^2(5)` splits its 15 basis states into the computed multiplets `(3bar,1,1/3)`, `(1,2,-1/2)`, `(3bar,1,-2/3)`, `(3,2,1/6)`, and `(1,1,1)`. No SM roster is supplied to the trace computation. In the weak-pair-unit convention,

- `Tr_5(Y^2)=5/6` and `Tr_5(T3^2)=1/2`, hence `k_Y=5/3`;
- `Tr_generation(T3^2)=2` and `Tr_generation(Q^2)=16/3`, hence `sin^2(theta_W)=3/8` for `Q=T3+Y`.

As an explicit alternative admissible abelian coordinate, `Y'=2Y` gives `k_Y=20/3` and, with the correspondingly stated `Q'=T3+Y'`, `sin^2(theta_W)=3/23`. Thus the celebrated values are computed once the standard charge unit and `Q=T3+Y` convention are fixed; that normalization is not forced by the Lie-algebra centralizer alone. Reversing the sign of `Y` is the other harmless direction convention.

## Coset and the step41 object

The 12-dimensional real Hermitian coset is displayed in the CSV through its 12 one-dimensional complex root spaces. Direct commutator eigenvalues group them as six `(3,2,-5/6)` roots and six `(3bar,2,5/6)` roots.

The same construction for `SU(4) -> SU(3)xU(1)` gives primitive centralizer `(-1,-1,-1,3)` and six coset roots `3 + 3bar`. Its computed verdict is `ANALOGUE_AS_FIXED_WEAK_INDEX_SLICE_NOT_IDENTITY`: mapping `E_i3` and `E_3i` into a fixed weak-index slice of the SU(5) roots is an explicit vector-space analogue after a `5/8` charge rescaling, but that slice is not invariant under the full embedded SU(2). The step41 object is therefore not identical to the SU(5) X/Y coset.

## F27: baryon descent

Color representations are read from computed SU(3) weights. On left-chiral fields the assigned physical baryon charges are `B=1/3` for `3`, `B=-1/3` for `3bar`, and `B=0` for singlets. Matrix action, rather than role labels, finds `12/12` real SU(5) coset generators with nonzero-Delta-B transitions. Every embedded `su(3)+su(2)+u(1)` generator preserves B. Removing the coset therefore leaves the SM-clean structure B-conserving at this algebraic vertex level. This does not compute a proton-decay rate or establish that a heavy parent is physically realized.

## F48: monopole lattice

In the SU(5) cocharacter lattice, quotienting by the three embedded SU(3) and SU(2) coroot columns has Smith invariants `1|1|1`: one free primitive loop and no torsion. The computed centralizer loop pairs with that primitive loop with index `6`, yielding the global form `[SU(3)xSU(2)xU(1)]/Z6`. With the standard exact-sequence inputs `pi_1(SU(5))=0` and `pi_2(SU(5))=0`, the result is `pi_2(SU(5)/H)=Z`. For an SM-alone structure modeled with no larger broken parent (`G=H`), `G/H` is a point and the corresponding required charge is `0`. The exact-sequence facts and the choice of global form are stated mathematical assumptions, not outputs of the finite matrix computation.

## Claim ledger

| Claim | Status | Computed result | Residual assumption or convention |
|---|---|---|---|
| SU5 hypercharge direction | LANDED-BY-CONSTRUCTION | centralizer dimension 1; primitive (-2,-2,-2,3,3) | overall sign and scale |
| k_Y and weak-angle ratio | LANDED-BY-CONSTRUCTION | k_Y=5/3; sin2(theta_W)=3/8 | weak-pair state assigned unit abelian charge; Q=T3+Y |
| SU5 X/Y coset | LANDED-BY-CONSTRUCTION | 12 roots: (3,2,-5/6)+(3bar,2,5/6) | regular 3+2 block embedding |
| step41 six-generator identity | LANDED-BY-CONSTRUCTION | ANALOGUE_AS_FIXED_WEAK_INDEX_SLICE_NOT_IDENTITY | charge rescaling required for slice comparison |
| F27 baryon descent | LANDED-BY-CONSTRUCTION | 12/12 coset generators change B; SM subalgebra 0 | B=(1/3,-1/3,0) on 3,3bar,1 left-chiral components |
| F48 monopole | LANDED-BY-CONSTRUCTION | pi2(SU5/H)=Z; SM-alone=0 | standard exact-sequence facts pi2(SU5)=pi1(SU5)=0 |
| unique parent | REMAINING-IMPORT | SU(5) uniquely selected within regular SU(n), n=5..8 | candidate class does not exhaust SO(10), E6, or non-regular embeddings |

The computed parent selector uniquely chooses SU(5) only inside the declared diagnostic family of regular `SU(n)` embeddings for `n=5..8`. A global uniqueness claim across other simple groups remains an import.
