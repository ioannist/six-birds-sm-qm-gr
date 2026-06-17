# Step 16 Results Summary: Content-Selection Principle Screen

## Input

This step evaluates structural principles over the `28` irreducible anomaly-free chiral supports emitted by Step 15.

## Per-Principle Results

- `faithfulness`: reference=True, survivors=`16`, non-circular=`True`.
- `sector_diversity`: reference=True, survivors=`4`, non-circular=`True`.
- `weak_doublet_singlet_mixing`: reference=True, survivors=`4`, non-circular=`True`.
- `charge_integrality`: reference=True, survivors=`26`, non-circular=`True`.
- `residual_chiral_complexity`: reference=True, survivors=`28`, non-circular=`True`.
- `simple_group_embedding_pattern`: reference=True, survivors=`2`, non-circular=`True`.
- `minimality_control`: reference=False, survivors=`12`, non-circular=`True`.

## Conjunction Results

All conjunctions of the six non-control structural principles were tested. The best reference-preserving conjunction is `charge_integrality+simple_group_embedding_pattern`, with `2` survivors.

No non-circular principle or conjunction uniquely selects the reference support. The two strongest survivors are the simple-branching orientation pair; choosing one orientation would require an additional input not supplied by the declared token-blind structural principles.

## Can-Fail Control

The carried minimality control does not select the reference support and leaves `12` minimal supports. The screen therefore does not trivially pass every declared principle.

## Verdict

`rigorous_type_limit_negative`.

The SM chiral content is not selected by the declared non-circular structural principles on this bounded carrier. The content-selection facet closes here as a precise type-limit negative: within this finite fixed-gauge test, an additional observed content/orientation input or an independent principle is required.

## Obligation-2 Status

`advanced_as_type_limit_negative`. The independently-checkable consequence was attempted over the Step 15 support set; it returns a negative boundary rather than a positive selection law.
