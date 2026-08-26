# P1 Kernel-Quotient Probe Findings

The probe hash-pins and imports the frozen Step 42, Step 44, and Step 55 Python machinery. It uses Step 55's generic weights, complete boundary-region fingerprint, central difference (`1e-6`), rank tolerance (`1e-6`), and both-direction finite clean-shadow test. Every carrier enumerates all `2^n-2` nontrivial boundary regions; no enumeration is truncated.

## Verdict table

| Carrier | Raw nullity | Reducible redundancy | Residual after quotient | Clean shadows |
|---|---:|---:|---:|---:|
| published_step42_raw | [5, 5, 5] | [5, 5, 5] | [0, 0, 0] | [2, 2, 2] |
| published_step42_aggregate_control | [0, 0, 0] | [0, 0, 0] | [0, 0, 0] | [0, 0, 0] |
| crosslinked_three_path | [8, 8, 8] | [8, 8, 8] | [0, 0, 0] | [6, 6, 6] |
| grid_2x3_multiterminal | [3, 3, 4] | [0, 0, 0] | [3, 3, 4] | [3, 3, 4] |
| k4_well_connected | [0, 0, 0] | [0, 0, 0] | [0, 0, 0] | [0, 0, 0] |
| k4_well_connected_stiff_chord | [3, 3, 3] | [0, 0, 0] | [3, 3, 3] | [1, 1, 0] |

The published carrier reproduces rank/nullity `[9, 9, 9] / [5, 5, 5]`. Replacing its six bridge-half-edge coordinates by `K=sum_i min(w_LMi,w_MiR)` gives nine parameters and rank/nullity `[9, 9, 9] / [0, 0, 0]`. The maximum original-versus-aggregate full-fingerprint residual is `0`; five independent finite slack/K-compensated directions have maximum residual `0`.

The cross-linked carrier has no bivalent interior node but remains an exact two-terminal module, so it is replaced by its computed L-R min-cut capacity before assigning any residual kernel. The grid and K4 carriers have no parallel edges, no bivalent interior nodes, and boundary access through more than two interior gateways. For every raw kernel, a stronger exact-reduction pass attempts to delete each edge and retains the deletion only if every terminal min-cut remains unchanged. For the grid, the clean-shadow edge sets are `['B2-U2;B3-V0;B5-V2', 'B0-U0;B3-V0;B5-V2', 'B0-U0;B2-U2;B3-V0;B5-V2']`, but deleting each candidate changes at least one terminal min-cut; the exact pruning pass therefore removed no edge. The balanced K4 carrier is already full rank. The stiff-chord K4 clean-shadow sets are `['I0-I1', 'I0-I1', '']` and exact-pruning removals are `['', '', '']`. Its seed-303 nullity is three despite zero clean-shadow edges, so that kernel is a coupled invisible subspace rather than a collection of zero Jacobian columns. Finite `0.01` moves along every numerical kernel-basis direction have per-seed maximum full-fingerprint residuals `[2.87947443667e-12, 5.50137713162e-12, 6.91002810527e-12]`.

## Honest conclusion

A residual fingerprint kernel survives the declared exact quotients on grid_2x3_multiterminal, k4_well_connected_stiff_chord. This is finite-carrier evidence that underdetermination is not solely the published carrier's series/parallel parameter redundancy; it is not a universal theorem, and clean-shadow counts identify locally inactive edge directions where present.
