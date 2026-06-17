# Step 18 Results Summary: Two-Layer Stress Test

## Radiative Content-to-Scale Channel

The scale facet was re-tested with a content-dependent radiative channel: a dominant fermion proxy from the texture/generation data plus subdominant gauge/representation terms. This is a structural sensitivity channel, not a physical solution to the scale problem.

## Coupling With Channel Active

- Step-17 inherited EW-vs-content residual: `0.035998916880` bits.
- Active content-scale coupling with radiative channel: `0.391243563629` bits.
- Gauge-generation reference control: `0.466203233486` bits.

The channel raises the content-scale coupling from borderline-low to non-negligible, but it remains below the gauge-generation reference.

## Coupling-Strength Can-Fail

The coupling-strength sweep is monotone: `True`. Coupling rises from `0` at channel strength `0` to `0.974342959327` bits at the strongest injected channel. This proves the information measure responds to injected coupling.

## Robustness Sweep

- Two-layer fraction: `0.333333333333`.
- Coupled-but-distinct fraction: `0.666666666667`.
- One-layer-break fraction: `0.000000000000`.
- Flip boundary: two_layer only when threshold exceeds the active coupling; no one-layer break at active strength.

## Verdict

`coupled_but_distinct`.

The clean Step-17 two-layer split is not robust once the radiative content-to-scale channel is included. The honest result is the middle architecture: the scale facet is coupled to content by radiative sensitivity, but it remains a distinct kind of selection problem because its measure is naturalness/tuning rather than anomaly/content consistency.

## Honest Scope

Toy-structural only. The hierarchy remains open, no physical Higgs-scale value is supplied, no dominant Yukawa value is derived, and frame transfer remains open.
