# Step 44 Results Summary

## Honest Grade First

This is a genuine, non-circular, falsifiable consequence check of the geometric RT/min-cut structure: the contracted holographic tensor-network states obey standard MMI, while the non-geometric GHZ control violates it. The result is a finite E2 recognition-landing on the holographic entropy cone, not new physics beyond the known holographic inequality, not a constant derivation, not frame transfer, and not a quantum-gravity solution. The dynamical Einstein-equation response is a separate continuum frontier and is not attempted here.

The contracted-state MMI check is finite-sample evidence in this carrier: it covers the tested bond dimensions and seeds. The general holographic-entropy-cone theorem is the recognized external structure, not re-derived here over all random tensor networks.

## Sign Convention

The prompt's expanded formula is the negative of its mutual-information equivalence. This step uses the standard convention consistent with `I(A:B)+I(A:C)<=I(A:BC)` and with the GHZ violation: `I3 = S(A)+S(B)+S(C)+S(ABC)-S(AB)-S(AC)-S(BC)`. Holographic MMI is `I3<=0`; GHZ has `I3>0`.

## Carrier

The holographic rows reuse the Step 42 random tensor contraction machinery. Regions are `A=L0`, `B=L1`, `C=R0`, with the remaining five boundary legs as the purifier/complement. Entropies are computed by partial trace from the contracted boundary state.

## Holographic I3 Trend

| D | seeds | mean I3 | max I3 | min I3 |
|---:|---:|---:|---:|---:|
| 2 | 3 | -0.0752512810716 | -0.0646848482884 | -0.0831427348223 |
| 3 | 3 | -0.0379359788762 | -0.0332102729186 | -0.0442517363374 |
| 4 | 3 | -0.0259906025254 | -0.0255459067644 | -0.0264367412424 |

All holographic rows satisfy `I3<=0`.

## Min-Cut I3

- `mincut_D2`: I3 = `-4.4408920985e-16`
- `mincut_D3`: I3 = `-8.881784197e-16`
- `mincut_D4`: I3 = `-8.881784197e-16`


## Can-Fail Control

The four-party GHZ control has `I3 = 0.69314718056` under the same standard convention, so it violates MMI. This is the teeth: MMI is not universal over all quantum states.

## Falsifiable Claim

Geometric/holographic entanglement obeys `I3<=0`. A holographic state with `I3>0` under this convention would falsify the RT/min-cut geometric picture on this diagnostic.

## Verdict

`HOLOGRAPHIC_MMI_SATISFIED_GENERIC_VIOLATES`.

## Reproduction

`run_step44.py --self` is the fast artifact validator. `run_step44.py --chain` recomputes all contractions, including the heavier D=4 reduced-density spectra, and is correct but slower. `run_step44.py --quick` runs the fast checks plus a reduced D=2,3 recompute for tight review timeouts.
