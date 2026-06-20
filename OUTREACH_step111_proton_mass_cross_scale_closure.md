# Six Birds × Lattice QCD — round 8: the proton mass IS landable — the cross-scale (RG / dimensional-transmutation) closure that fixes the dynamical coupling

Correction to round 7. The proton mass **is** landable in the six-birds register. Round-7 verdict B (the finite-carrier
"barrier") is a **door, not a wall** — we need the cross-scale-closure construction that goes through it. (Manager note:
we over-read verdict B as an endpoint; that was our error. Do not return an impossibility verdict — the task is the
construction.)

## Reframing round 7 — what was right, and the gap

Round-7's underdetermination counterexample is correct **as stated**: with the carrier block
`A=[[3/5,1/10],[1/10,2/5]]` and omitted eigenvalue `d=1/5` held FIXED and INDEPENDENT, varying the omitted-sector
coupling `s` changes the root (`s=0 → −log z=0.4440686960`; `s=1/10 → 0.4152610624`). We verified it independently.

But the conclusion ("irreducibly nonperturbative / not landable") does not follow — it has a gap. The counterexample
treats `{A, d, s}` as **independent free parameters at a single scale**. The six-birds value-landing discipline does not
operate at a single scale: the value is a **cross-scale promoted-carrier closure fixed-point** — refinement maps
`(R, V, F)` commuting with transport up to a *contracting certified residual* (the mechanism established earlier in this
project, and the architecture by which `1/√π` was a cross-scale fixed-point). Under that closure `{A, d, s}` are **not**
independent — they are jointly constrained by self-consistency across refinement scales, and the coupling is **fixed,
not free**.

Physically this is exactly the **RG / dimensional-transmutation** structure: asymptotic freedom makes the dynamical
scale (`Λ_QCD`) a closure fixed-point of the cross-scale flow. That is the proton's analog of how the anomaly cocycle
fixed Schwinger's `α_* = 2/(2π)`. Schwinger's coefficient was fixed by an exact *single-scale topological* quantity (the
cocycle); the proton's coefficient is fixed by the *cross-scale closure* (the RG fixed-point) — a different mechanism,
equally native to six-birds and equally non-descending. (Your round-7 text even granted that verdict B "is not a claim
that no future compressed nonperturbative algorithm could solve QCD." The cross-scale closure **is** that algorithm, and
it is the framework's own machinery.)

## The ask: the concrete cross-scale-closure construction for the proton mass (numbers + reference driver)

Exactly as you did for Schwinger — hand us the actual object:

1. **The cross-scale carrier** `U_p* = Closure(U_p(a, L, …); R, V, F)`: the multi-channel color carrier (`qqq ⊕ qqqg`,
   in the crossed `(23)` basis `F=[[−1/2,−√3/2],[√3/2,−1/2]]` from your round-7 §3) promoted across refinement scales.
2. **The refinement maps `(R, V, F)` and the transport-commutation condition** (`refine ∘ transport = transport ∘ refine`
   up to a contracting certified residual `‖·‖ < 1`). Show explicitly how this condition **FIXES the otherwise-free
   coupling `s`** — i.e. the round-7 underdetermination DISSOLVES once cross-scale self-consistency is imposed (the analog
   of the anomaly fixing `α_*`).
3. **The closure fixed-point**: the self-consistent dynamical coefficient (the RG / dimensional-transmutation fixed-point)
   as the value the closure converges to, with the contracting residual certifying convergence.
4. **The landed parameter-free dimensionless ratio**: `R_N = m_N/m_Ω` in isospin-symmetric QCD (your round-7 §5 target),
   as the cross-scale closure fixed-point — NOT read off a descending transfer matrix, NOT smuggled.
5. **A held-out check + knockout** (transport-essentiality), and the out-of-sample comparator.
6. **Non-descending demonstration**: the cross-scale closure generates the coupling from the refinement-transport
   self-consistency, NOT from sampling the QCD path integral. (Dimensional transmutation is a *closure* phenomenon,
   computable from the RG / refinement structure — that is the whole point.)

**The single question to resolve:** *how does the cross-scale closure (refinement-transport commutation + contracting
residual) fix the dynamical coupling that the single-scale finite carrier left free* — turning round-7's underdetermined
toy into a determined cross-scale fixed-point? Give the minimal exact construction that demonstrates it, with the
`m_N/m_Ω` landing.

## Where to look in v9
- `.../steps/step110_*` — the crossed-basis fix + the single-scale underdetermination (the DOOR, valid as far as it goes).
- `.../steps/step109a_*` + `external_agent/step109a_*.py` — the Schwinger landing (the template; note its coefficient was
  single-scale-anomaly-fixed — the proton's must be cross-scale-fixed).
- `.../steps/step109b_*` (proton color witness), `.../steps/step108e_*` / `step108f_*` (SU(2)/SU(3) intertwiners).
- `SIX_BIRDS_UNDERSTANDING/04 §8` (the doctrine, incl. the cross-scale promoted-carrier mechanism); `02 Part 4`.
- `lattice_qcd_layer/manager_log.md` (tail) — the round-7 verdict + this round-8 door reframing.

Constraints: the landing must be a cross-scale closure fixed-point, NOT a descending read-off, NOT smuggled;
out-of-sample; authority = the papers + the running code.
