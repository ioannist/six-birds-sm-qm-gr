# Q7 F50 adaptive-convergence result

All 18 sampled background offsets have fixed-point solutions. Fifteen continuation points are linearly stable under the undamped map; offsets `5`, `8`, and `10` are unstable even though suitable damping converges to their solutions. Clustering every converged run by phase-invariant ray distance finds `20` distinct sampled fixed points: `17` stable and `3` unstable. The extra two are stable localized solutions at offset `-8`, so the three initial states are evidence of multistability rather than interchangeable global phases. The continuation radius range is `0.0137104841286` to `2.63231292023`. The positive-offset spectral radius crosses one at offset `3.65353525686` with leading eigenvalue `-0.99999999892`. Thus solution existence gives no sampled value selector, but undamped-map stability types the background family as mixed rather than declaring all points stable.

The frozen legacy settings reproduce the reviewed artifact exactly: `15/18` pass at 60 iterations and `18/18` pass at 120. That split is therefore a budget observation, not an existence boundary.

All 12 sampled kappa values also have fixed-point solutions. The solution branch does not disappear. Its undamped-map spectral radius rises from `0` to `5.96864463731` and crosses one at `kappa=5.86748467933` with leading eigenvalue `-0.999999999778+0i`. This is a genuine raw-map linear-stability boundary, not a loss of solution. Damping changes the relaxed solver stability and therefore the apparent finite-budget boundary; it does not move the fixed-map crossing.

Supported outcome: **MIXED_ALL_BACKGROUND_SOLUTIONS_EXIST_THREE_RAW_MAP_UNSTABLE_AND_KAPPA_STABILITY_BOUNDARY**. All sampled backgrounds possess fixed-point solutions, but only 15/18 are linearly stable under the undamped map; the kappa continuation likewise retains solutions while crossing a raw-map stability boundary.

Doubling the adaptive cap from 2000 to 4000 changes no case classification: `True`.
