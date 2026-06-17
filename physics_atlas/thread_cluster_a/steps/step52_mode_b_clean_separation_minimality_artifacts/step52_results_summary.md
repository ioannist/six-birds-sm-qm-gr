# Step 52 Results Summary

## Deflationary Caveats First

1. The carrier has only two structure families, `2|3` and `4`; this is a coarse two-class discrimination, not fine-grained uniqueness over all gauge structures.
2. The baryon-number variants relocate the recognition source to proton-stability / F27 baryon descent. They do not derive clean-separation or remove observed input.
3. The coincidence of the baryon variants with clean-separation is computed on this carrier: all six single-factor coset witnesses are baryon-orbit-enlargers. This is not a general theorem for richer carriers.

## Orientation

Step 52 computes whether the introduced clean-separation condition is minimal on the declared Step-35/38 carrier. It tests weaker predicates against the same 12 rows.

## Survivor Table

| predicate | total survivors | `2|3` survivors | `4` survivors |
|---|---:|---:|---:|
| base_shadow | 12 | 8 | 4 |
| no_light_xy | 12 | 8 | 4 |
| no_baryon_violating_xy | 8 | 8 | 0 |
| bare_proton_stability | 8 | 8 | 0 |
| clean_separation | 8 | 8 | 0 |

## Strength Ordering

Extentionally on this carrier, `base_shadow` and `no_light_xy` keep all 12 rows. `no_baryon_violating_xy`, `bare_proton_stability`, and `clean_separation` all cut the carrier to the same 8 rows. Definitionally, clean-separation is stronger than the baryon predicates because it forbids every confining-charged broken vector, while the baryon predicates only forbid the F27 orbit-enlarging subset or its descent obstruction.

## Verdict

`MINIMALITY_MIXED`.

Sufficient weaker predicates: no_baryon_violating_xy, bare_proton_stability.

Insufficient weaker predicates: no_light_xy.

The next frontier is to keep the recognition-source relocation explicit: a proton-stability / baryon-descent predicate can perform this cut on the present carrier, but it imports baryon number as an observed-input readout.
