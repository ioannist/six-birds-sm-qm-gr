# Certified Step-1 statement

For finite labelled tensor networks with explicitly declared positive integer bond and boundary dimensions, the explicit
dense numerical Step-1 engine constructs deterministic copy-tensor or independently seeded random-complex vertex tensors,
contracts every internal index, and numerically computes the von Neumann entropy of every boundary subset solely from the resulting normalized boundary state. The entropy includes every strictly positive numerical Schmidt probability; the declared tolerance reports numerical rank, discarded diagnostic mass, and a truncation-error bound rather than altering the reported entropy.

On concrete instances, internal g/g^-1 transformations, bivalent-series absorption, and parallel-index fusion
preserve the boundary state to machine precision; an explicit one-leg boundary unitary produces the predicted
local-unitary-related state and preserves every entropy. The full entropy vector distinguishes a contracted Bell-edge
network from a disconnected product network by ln(2), while agreeing for the internal-gauge pair. A six-boundary survivor-scale tensor mutation also changes the entropy vector, providing a gauge-invariant obstruction to library equivalence. Survivor random-tensor seeds are hashes of `(namespace, carrier_name, D, replicate)` and exclude P1 capacity seeds; provenance mutation leaves states and entropies unchanged. All 13 P1-v3 reduced
survivor carriers are computationally tractable for the declared random family at D=2,3,4 and the structured family at
D=2, with all 2^|T| entropies computed. This certifies the engine and controls only, not underdetermination.
