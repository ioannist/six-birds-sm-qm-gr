# Step 5 Results Summary

## Orientation

Step 5 builds the E009 UV-completion fiber facet. The carrier is a finite UV-fiber, an IR shadow, a toy consistency constraint, a UV-to-IR staging map, and a selector over the admissible realized fiber.

## UV Fiber

The realized IR code `IR_SM_TOY` has `6` UV candidates: `U_SM;U_alt_GUT;U_alt_stringy;U_bad_unitarity;U_bad_positivity;U_bad_anomaly`. Their UV contents differ, so the fiber is non-trivial.

## Non-Descending Test

- UV-content obstruction from IR code: `16`, witness `U_SM-U_alt_GUT;U_SM-U_alt_stringy;U_SM-U_bad_unitarity;U_SM-U_bad_positivity;U_SM-U_bad_anomaly;U_alt_GUT-U_alt_stringy;U_alt_GUT-U_bad_unitarity;U_alt_GUT-U_bad_positivity;U_alt_GUT-U_bad_anomaly;U_alt_stringy-U_bad_unitarity;U_alt_stringy-U_bad_positivity;U_alt_stringy-U_bad_anomaly;U_bad_unitarity-U_bad_positivity;U_bad_unitarity-U_bad_anomaly;U_bad_positivity-U_bad_anomaly;U_alt_IR_A-U_alt_IR_A_bad`.
- Derived IR observable obstruction: `0`, witness `none`.

The IR shadow distinguishes derived IR observables but not which UV completion in the fiber is active.

## P2 Consistency Constraint

The toy consistency functional prunes `U_bad_unitarity;U_bad_positivity;U_bad_anomaly;U_alt_IR_A_bad`. Consistent candidates survive. In the realized IR fiber, `3` candidates remain admissible before selection.

## P4 Staging

Each UV row carries a computed staging string `UV -> threshold data -> IR_EFT_code`; this records the finite UV-to-IR down-shadow used by the fiber test.

## Selector

The selector collapses the admissible realized fiber from `3` to `U_SM`. Non-selected admissible candidates: `U_alt_GUT;U_alt_stringy`.

## Controls

- Many-to-one realized fiber: `True`.
- UV non-descending: `True`.
- Derived IR observable factors: `True`.
- Consistency prunes and preserves: `True`.
- Selection collapses: `True`.
- Carrier guard: finite UV-fiber plus IR shadow plus consistency selector.

## Verdict

`e009_uv_fiber_facet_constructed`.

The finite toy shows UV completion as a non-descending fiber-selection over a shared IR EFT: consistency prunes, staging maps UV rows to IR shadows, and selection chooses one admissible UV candidate.
