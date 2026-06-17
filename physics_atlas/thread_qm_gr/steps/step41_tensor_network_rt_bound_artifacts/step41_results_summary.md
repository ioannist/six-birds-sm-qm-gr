# Step 41 Results Summary

## Honest Grade First

The graph and tensor class here are CHOSEN as an RT recognition carrier; this step tests whether SBT's currency/shadow-price machinery lands non-circularly inside that carrier, so it is a recognition-landing rather than an SBT-alone generation of holography.

Steps 39 and 40 were rejected because they made area and entanglement two names for matched inputs. Step 41 changes the target from an identity to a saturable bound: `S(A) <= min-cut`, with saturation for holographic tensors and a strict gap for controls. This is still a finite E2 recognition-landing on the Ryu-Takayanagi/random-tensor-network structure. It does not derive the continuum Newton normalization, is not SBT-alone physics, does not certify frame transfer, and does not attempt faithful enrichment, the entanglement-first-law consequence, or semiclassical limit recovery.

## Carrier

The carrier is an explicit looped two-cluster tensor network. Each bulk vertex carries an explicit tensor-entry rule saved in `tensor_network_tensors_step41.json`. The boundary state is obtained by summing over internal indices; then `rho_A` is formed from the contracted amplitude vector and `S(A)` is computed from its eigenvalues. The area is computed separately by max-flow/min-cut on the graph.

## Bound, Saturation, And Gap

| case | tensor | S(A) | min-cut | gap area-S | ratio S/area | result |
|---|---|---:|---:|---:|---:|---|
| holo_refinement_D2 | copy | 0.69314718056 | 0.69314718056 | -1.11022302463e-16 | 1 | saturated |
| holo_refinement_D3 | copy | 1.09861228867 | 1.09861228867 | 2.22044604925e-16 | 1 | saturated |
| product_control_D2 | fixed_zero | -0 | 0.69314718056 | 0.69314718056 | -0 | strict gap |
| weighted_control_D3 | weighted_copy | 0.830471712436 | 1.09861228867 | 0.268140576232 | 0.755927929263 | strict gap |

The strict-gap witness value is `0.69314718056`. The nontrivial min-cut witness is `holo_refinement_D2`: the cut crosses an internal bridge and uses fewer cut edges than the number of boundary legs in region A.

## Verdict

`RT_BOUND_SATURATED_STRUCTURALLY`. Next frontier: faithful random/perfect tensor enrichment and the entanglement-first-law consequence.
