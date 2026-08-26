# Q7 numerical design

- Step26 and Step54 are imported under literal SHA-256 pins; no corpus-reading build path is called.
- The undamped map sends a normalized state to the phase-aligned lowest eigenvector of the self-sourced Hamiltonian. Relaxed iteration uses the declared mix only as a solver.
- Convergence requires projective fixed-map residual below 1e-10. Period-2 through period-8 cycles, flat residual windows, nonfinite states, and residual growth are typed separately.
- Jacobians act on the 2N-2 dimensional normalized/projective tangent space and use centered finite differences. Relaxed-map radii are derived as eigenvalues of `(1-mix)I + mix J`.
- Converged states are clustered with the global-phase-invariant ray distance. The undamped Jacobian is evaluated for every distinct fixed point found across all mixes and initial states; this exposes three stable attractors at offset -8.
- The kappa boundary is refined by bisection on the undamped spectral radius while continuing the fixed-point solution with mix 0.2.
