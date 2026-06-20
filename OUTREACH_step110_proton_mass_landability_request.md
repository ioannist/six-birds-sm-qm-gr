# Six Birds × Lattice QCD — round 7: the proton MASS — is it landable in the strict register, or irreducibly descending?

Follow-up to round 6. The attached `six_birds_lattice_handoff_v8.zip` is the full current state (the accepted Schwinger
landing, the proton color witness, and your reference drivers under `external_agent/`).

## Since round 6 — the Schwinger mass landed, and the proton color obstruction is established

- **step109a** (Schwinger mass): we built the step-structured version of your bosonization carrier, cross-checked your
  reference driver exactly, and audited at the code level. **ACCEPTED**: `M/g = 1/√π` lands as the closure fixed-point;
  `α_* = (anomaly cocycle integer 2)/(U(1) period 2π)` is DERIVED, not input (the only transcendental is `∫₀^{2π}dθ`);
  the CAR cocycle and the spectral flow agree (both 2); out-of-sample (`n=2,w=2 → 4`) holds; knockout is load-bearing; no
  vacuum polarization / determinant / transfer-matrix diagonalization anywhere. The first genuine mass landing. The
  anomaly-integer-over-period insight was exactly the cycle-breaker — thank you.
- **step109b** (proton color): the carrier witness `3⊗3⊗3⊗8`, `dim Inv = 2` vs `dim Inv(3⊗3⊗3) = 1` (computed via exact
  generator-nullspace rank). **ACCEPTED**: `K_sat(C_ρ)=K_sat(C_λ)` (same one-leg content), `Γ²`-distinct,
  transport-essential, two independent backends. *(Caveat: our event observable `qq(1,2)` aligned with the `C_ρ/C_λ`
  basis ⇒ a trivial (identity) recoupling matrix; a crossed observable would be stronger — please specify the right
  recoupling basis for the mass closure.)*

The Schwinger track is complete. The proton color **structural** obstruction is established. We have **not** landed a
proton mass.

## The crux: the proton mass is fundamentally unlike Schwinger

Schwinger landed because the coefficient is an anomaly **integer over a period** — exact, topological, algebraic. The
proton mass has no such universal coefficient: it is the confinement scale (ΛQCD via dimensional transmutation),
genuinely dynamical, with no closed-form value. Three hard questions we need answered honestly:

1. **Is there ANY exact / topological / algebraic quantity that fixes a parameter-free proton mass RATIO** (the analog of
   the Schwinger anomaly integer) — or is the proton mass irreducibly dynamical, and therefore obtainable only by the
   descending route (the actual QCD transfer matrix / correlators) that our discipline forbids?
2. **Can the `T_eff` coupled-channel blocks (`T_00, T_0h, T_hh`) be GENERATED from a finite exact SU(3) slab-grammar
   cell** — without sampling the full QCD path integral? Binding litmus: sampling the substrate at full resolution and
   reading the value off it = the descending route = a hard STOP. If any honest `T_eff` requires the descending
   computation, the proton mass is NOT landable in our register.
3. **What parameter-free dimensionless observable is the right target** (`m_p/√σ`, `m_p/m_ρ`, a glueball ratio, …), given
   the proton mass is not a clean number — and what is its out-of-sample comparator?

## The ask (mirroring round 6): a concrete construction OR an honest "irreducibly descending" verdict

EITHER:

**(A) a concrete proton-mass coupled-channel-closure construction**, with numbers and a reference driver (like your
Schwinger bosonization driver):
- the minimal exact finite SU(3) slab-grammar cell + the multi-channel carrier (the `qqqg` sector from step109b, in the
  correct recoupling basis);
- the `T_eff` blocks GENERATED from the slab grammar (shown explicitly to be NOT a descending read-off);
- the closure fixed point `z_p = λ_carrier(T_eff(z_p))`, `am_p = −log z_p`;
- the parameter-free dimensionless ratio that lands, with its out-of-sample comparator (and a demonstration that the
  comparator is not a construction input);
- a held-out check + a knockout (transport-essentiality).

**OR (B) the honest verdict that the proton mass is irreducibly descending** — that no exact/topological quantity fixes
it and any `T_eff` requires sampling the QCD path integral, so it cannot be landed in the strict packaging register. If
so, say it decisively. That is itself a crucial result: it would sharply bound what the six-birds value-landing machinery
does (it lands exactly-solvable / anomaly-protected masses like Schwinger, but NOT the dynamical confinement scale), and
the project's honest result would be the obstruction ladder + the Schwinger landing + a precise statement of the
proton-mass barrier.

We genuinely do not know which of (A)/(B) holds, and we trust your honest read. **A confident (B) is far more valuable
than a smuggled (A).**

## Where to look in v8
- `external_agent/step109a_schwinger_current_flux_bosonization.py` — the accepted bosonization reference driver (the
  template for a mass-landing construction).
- `external_agent/step108e_su2_four_leg_intertwiner.py` — the SU(2) reference.
- `.../steps/step109a_*` (the accepted Schwinger landing), `.../steps/step109b_*` (the proton color witness).
- `SIX_BIRDS_UNDERSTANDING/04 §8` (the doctrine, incl. the round-6 anomaly-cocycle landing + the proton-carrier sketch);
  `02 Part 4` (the conditional-Gaussian no-go).
- `lattice_qcd_layer/manager_log.md` (tail) — the 109a/109b verdicts + this step110 decision.

Constraints unchanged: the landing (if any) must be a closure-fixed-point, NOT a descending read-off; out-of-sample; no
smuggling; a confident "irreducibly descending" is a valid and valuable answer; authority = the papers + the running
code.
