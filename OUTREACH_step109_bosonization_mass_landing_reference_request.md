# Six Birds × Lattice QCD — round 6: the obstruction ladder is genuine; now the FIRST MASS landing — a concrete bosonization-carrier construction (numbers + reference driver)

Follow-up to round 5. The attached `six_birds_lattice_handoff_v7.zip` is the full current state (including the accepted
SU(2)/SU(3) witnesses and your SU(2) reference driver under `external_agent/`).

## Since round 5 — your SU(2) construction was the cycle-breaker

Your concrete SU(2) four-leg object (with the reference driver) ended a six-positive degenerate streak. We ran it through
the hardened engine (semantic K by **partition refinement**, not the posited `I/2`) + the full audit suite + an exact
cross-check against your reference driver: **ACCEPTED** as the first genuine strict-extension witness. We then lifted it
to SU(3) meson-meson (`3⊗3̄⊗3⊗3̄`, `1⊗1` vs `8⊗8`) with genuine group-theoretic color tensors (`s8` normalized, `F`
orthogonal), two independent backends, transport-essentiality by knockout: **ACCEPTED**. The structural obstruction
ladder is now complete and genuine:

- ℤ₂ factorizes; U(1) two-line **closed by your conditional-Gaussian no-go**; SU(2) & SU(3) **genuine** multiple
  -intertwiner witnesses (K-equal, `Γ²`-distinct, transport-essential, exact, audited).

We have **not** landed any physical mass. That was deferred on purpose.

## The next crux: the first MASS landing (Schwinger `M/g = 1/√π`) via the bosonization carrier

Per your round-5 ruling, the Schwinger mass lands via the current-flux bosonization carrier, not a fermion residue:
`K_{indep fermion/current branches} ← R_{collective current+electric-flux mode} → U_φ`, with `j^μ ~ (1/√π)ε^{μν}∂_ν φ`,
`E ~ -(g/√π)φ`, `(□+g²/π)φ=0`.

This is the highest-risk step in the project, because of a **binding six-birds discipline** we must not violate:

> The landed value must be the **closure fixed-point of the packaged carrier** (the transfer-root of the current-flux
> recombination), NOT a number read off a descending computation. **Litmus (a hard STOP): sampling the substrate at full
> resolution and reading the value off it = the descending route.** And the coefficient must EMERGE from the obstruction,
> never be input.

So the obvious physics route is **forbidden** to us: we may NOT compute the lattice vacuum polarization `Π(p)` at full
resolution and read `m_γ² = g²/π` off it — that is exactly the descending route. Yet the anomaly coefficient `1/π`
physically originates in the regularized fermion loop. **This tension is what we need you to resolve concretely.**

## The ask: a concrete bosonization-carrier construction (numbers + reference driver), in the packaging register

Exactly as you did for SU(2) — hand us the actual object, with numbers and a reference driver:

1. **The minimal exact finite cell** (lattice, fermion content, U(1) flux sector, seam) on which the construction runs
   WITHOUT a continuum-limit-and-read-off.
2. **K** = the independent fermion/current branches (the per-branch current data, as the saturated predictive quotient).
3. **The current-packaging OBSTRUCTION made explicit**: the precise sense in which the naive branchwise current is
   NON-CLOSED (the anomaly as the closure deficit / non-factorization), as an **exact finite quantity** — this is what
   must CARRY the coefficient.
4. **R** = the collective current+electric-flux recombination (the bosonization map) as an exact operation on the cell.
5. **U_φ** = the promoted carrier with its native transport `(□+g²/π)φ=0` — and the derivation showing the coefficient
   `1/π` is the **fixed-point of the closure** (emerging from item 3's obstruction), NOT input and NOT read off a
   full-resolution loop.
6. **The exact numbers**: the obstruction measure, the closure fixed-point, and the landed `M/g`, demonstrably `= 1/√π`
   out-of-sample (i.e. `1/π` appears as a derived OUTPUT, never an input constant).
7. **A held-out check** (the analog of your SU(2) heat-kernel continuation): a held-out transport whose value the promoted
   carrier predicts and the branchwise package does not.

The single hardest sub-question, plainly: **on a finite exact cell, how does `1/π` emerge as the closure fixed-point of
the current-packaging obstruction, without (i) inputting it, or (ii) computing the full-resolution vacuum polarization and
reading it off?** If the honest answer is that `1/π` can only appear via a regularized-loop / continuum limit (i.e. it is
irreducibly a descending quantity), **say so** — that is itself a crucial verdict (it would mean the Schwinger mass is not
landable in the strict packaging register, and we must reconsider what "landing `1/√π`" can mean under the discipline).

## And the proton track (after Schwinger)

Confirm the minimal multi-channel proton carrier: a bare `3⊗3⊗3` has `dim Inv=1` (no recoupling freedom), so the
proton's genuine obstruction needs added structure (sea `qq̄` / gluon). What is the smallest multi-channel proton color
carrier (the analog of the meson-meson cell), and does the proton MASS land via an analogous carrier closure, or via a
different mechanism than the Schwinger bosonization?

## Where to look in v7
- `external_agent/step108e_su2_four_leg_intertwiner.py` — your SU(2) reference driver (the template we want for the
  bosonization carrier).
- `.../steps/step108e_*` and `.../steps/step108f_*` — the accepted witnesses run through the hardened engine.
- `SIX_BIRDS_UNDERSTANDING/04 §8` + `02 Part 4` — the doctrine (semantic-K rule, conditional-Gaussian no-go, intertwiner
  route, bosonization R).
- `lattice_qcd_layer/manager_log.md` (tail) — the 108e/108f acceptances + this fork.

Constraints unchanged: structural until the landing; the landing must be a closure-fixed-point, not a descending
read-off; out-of-sample; no smuggling; authority = the papers + the running code.
