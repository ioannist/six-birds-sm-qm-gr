# Step 54 Results Summary

## Honest Grade First

This is a computed F50 demarcation on the finite frozen Step26 semiclassical toy. It does not say anything about the measured value of the real cosmological constant, does not solve the cosmological-constant problem, does not derive Lambda, does not certify frame transfer, and does not close E018. The result is a structural classification: the background/Lambda analog is not selected to a value by the in-layer closure machinery. The closure can constrain the coupling `kappa`, so the audit has teeth.

## F50 Data

- `X`: admissible Step26 semiclassical configurations `(psi, background, kappa)`.
- `mu`: closure-status quotient induced by the frozen Step26 fixed-point convergence criterion.
- `b0`: scalar offset of the matter-independent background term added to the frozen Step26 background vector.
- `target`: self-consistent co-sourcing/back-reaction fixed point.

## Background Sweep

Swept `18` background offsets with frozen `kappa=0.3`, `mix=0.5`, and `60` iterations. Pass count: `15`. Degeneracy among passing backgrounds: `15`.

F50 classification: `bounded_moduli`. The finite pass set is `[-8.0, -2.0, -1.0, -0.5, -0.2, -0.1]` and the fail set includes `[-5.0, -3.0, 10.0]`. The computed background window summary is `{'min_pass_offset': -8.0, 'max_pass_offset': 8.0, 'noncontiguous_finite_pass_set': True}`.

Because more than one background passes, the vacuum singleton clause fails. Because not every swept offset passes under the frozen finite criterion, the honest verdict is bounded/swept moduli, not full blindness.

## Kappa Control

The kappa sweep has `12` rows. Pass examples: `[0.0, 0.1, 0.3, 0.5, 1.0, 2.0]`. Fail examples: `[15.0, 20.0, 30.0]`. Boundary found: `True`.

This is the discrimination tooth: the same closure chain sees `kappa` but does not select a unique background value.

## Structural Note

`No full b-independence theorem: Step26 uses T00[psi]=|grad psi|^2 + background*|psi|^2 and V=background+kappa*T00.` The actual Step26 equation contains `background*|psi|^2`, so scalar background shifts are not proven to cancel from the fixed-point iteration. The classification is enumeration-strength over the declared sweep.

## Forbidden Rule

`no_inlayer_lambda_value_law`: the framework forbids an in-layer Lambda/background value-law on this carrier. Any value law would need an extra vacuum-selection source; the in-layer result is at most an admissibility pattern/window.
