# Step 37 - Uniqueness Stress-Test

## Record Correction: Manager Override

MANAGER-OVERRIDDEN. The prior verdict `GENUINE_NEUTRAL_STRUCTURE_UNIQUENESS_WITH_CONTENT_LIMIT` is REJECTED. The accepted Step-37 verdict is `SMALL_NEUTRAL_FAMILY_currency_rescue_REJECTED`.

The precise unbroken-subgroup test leaves the small neutral family `{2|3, 4}`: the single-factor `4` family survives. The `scalar_stage_currency_minimum` row is diagnostic_only/REJECTED because the manager determined that it reduces to "smallest broken factor" and is minimality-like. No Step-37 uniqueness is accepted.

Deflationary truth first: the Step-36 `factor_local_breaking` rule was too strong for a uniqueness claim. It rejected single-factor candidates by construction because it required an untouched factor. This step drops that rule and replaces it with a precise neutral unbroken-subgroup test.

## Carrier

The Step-35 higher-layer mass-closure survivors were rederived:

- Reproduced survivors: `12`.
- Structure split before stress-test: `2|3`: `8`, `4`: `4`.

## Neutral Subgroup Test

The replacement test computes whether the scalar witness leaves any unbroken non-abelian subgroup, including partial breaking inside a factor.

Result:

- Precise unbroken-subgroup survivors: `12`.
- The single-factor `4` family survives: yes.
- Reason: the scalar witness can leave a dimension-3 subgroup under partial breaking.

This confirms the manager's concern: Step 36's unique-structure cut depended on the imprecise factor-local rule.

## Non-Shape Principles Tested

| principle | survivors | structures | single-factor survives | result |
|---|---:|---|---|---|
| precise unbroken subgroup | 12 | `2|3:8;4:4` | yes | no uniqueness |
| unbroken low-energy consistency | 12 | `2|3:8;4:4` | yes | no uniqueness |
| full cascade consistency | 12 | `2|3:8;4:4` | yes | no uniqueness |
| scalar-stage currency minimum | 8 | `2|3:8` | no, but finite currency was computed | diagnostic_only/REJECTED |

The old Step-36 factor-local rule is retained only as a flagged diagnostic: it is shape-flavored because it is unsatisfiable for single-factor structures by construction.

## Verdict

`SMALL_NEUTRAL_FAMILY_currency_rescue_REJECTED`.

The precise neutral test gives the honest corrected family `{2|3, 4}`. The scalar-stage currency row still computes `8` diagnostic survivors in `2|3`, but that rescue is rejected and does not carry a uniqueness verdict. The Step-14 reference support is not selected at Step 37.

Next grammar delta: accept the small neutral family and continue to Step 38's introduced clean-separation condition or to the matter-content boundary.

## Gates

- Primitive exclusion: pass.
- Dependency trace: pass.
- Ablation: pass.
- Negative controls: pass; precise subgroup admits single-factor partial breaking, while currency is not a target-row picker.
- Stage II: pass; Step-35 residual is reproduced and the old rule is demoted.
- Shape-flavored detector: pass; old rule and scalar-stage currency rescue are both flagged, and the currency row is diagnostic-only/rejected.
