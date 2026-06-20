# Six Birds × Lattice QCD — round 3: ℤ₂ concluded, a schematic U(1) nonseparable witness, and the toy-vs-lattice question

Follow-up to round 2 (your hidden-record adjudication, which we accepted). The attached zip
`six_birds_lattice_handoff_v4.zip` has the full current state; this note covers what happened since, two accumulated
subtleties, and the strategic question we'd like your direction on.

## Since round 2

Your round-2 ruling (the hidden-record control was overreaching — exposing the joint Wilson loop to the branchwise `K`
is currentization `K→K^W`, not artifact removal) was accepted and folded into the base (`02` Part 4 addendum). Then:

- **step107d (ℤ₂, the K-saturation repair) — `z2_factorizes_through_saturated_K`.** With `K` saturated from
  admissible branch-local records (provenance-typed; the joint holonomy explicitly rejected), the two-branch ℤ₂ loop
  **factorizes**: the per-branch transporters `u_a` (relative to a frozen boundary frame) determine `W = u₁·u₂`, so no
  `K_sat`-equal/`R`-distinct pair survives. This is the legitimate collapse you anticipated — the ℤ₂ two-branch loop is
  too decomposable. (Verified in the driver: `K_sat` genuinely branch-local; `joint_holonomy_field` rejected; solver ==
  full-enumeration comparator.) The ℤ₂ rung is concluded.
- **step108 (U(1) Schwinger, a genuinely nonseparable recombination) — reached the *shape*, but schematic.** A joint
  Grassmann pairing parity that is rejected from `K` and **survives saturated `K` + branch-local completion** with `K`
  genuinely equal across the pair (`direct` vs `exchange`), and a differing held-out response. This **beats the ℤ₂
  failure mode** — a nonseparable witness exists in principle. But on audit it is too schematic to trust as a U(1)
  result (details below). Honest classification: `schematic_nonseparable_witness_needs_hardening`.

## The questions we want your direction on

### (1) The step107d frozen-frame sub-caveat (the ℤ₂ collapse's hinge)

The ℤ₂ collapse rests on **open branch parallel-transports `u_a`, relative to a frozen/licensed boundary frame, being
admissible `K`-records.** But open Wilson lines are gauge-*variant*; only the closed loop is gauge-invariant. So which
is the correct discipline:
- the branchwise quotient *may* record gauge-variant open transports relative to a frozen, licensed boundary
  trivialization (→ ℤ₂ factorizes, as we found); or
- only gauge-*invariant* quantities are admissible `K`-records (→ the ℤ₂ obstruction would *survive*)?

We judged it does not change the next step (even a surviving ℤ₂ witness spans only `c_K`/`c_R`/`L_quad` — not
mass-transport-bearing), but the rule matters for the general acceptance criterion. What is the correct typing?

### (2) Is step108's "contraction-topology-as-primitive" legitimate, or must the parity be *derived*?

step108 represents the recombination distinction as a **bare label** `pairing ∈ {direct, exchange}` with
`pairing_parity` a **literal** (`direct→+1`, `exchange→−1`), **not computed from an actual ≥2-fermion-line Wick
contraction graph**. Also `joint_flux_closure ≡ 0` (the U(1) flux does no work) and the held-out continuation is the
parity *multiplied in*, not a computed correlator. Two readings:
- the contraction topology *is* a genuine fermionic configuration degree of freedom, so a binary primitive plus its
  permutation sign is a legitimate finite *abstraction* of the nonseparable mechanism; or
- it is the recurring literal-label smuggle (the same pattern we rejected in step107b/107c): the parity must be
  **computed** from an actual worldline contraction graph — e.g. **connected vs disconnected meson contraction, with
  the relative fermion-loop sign** — with load-bearing flux and an actual Grassmann-determinant correlator.

Which is correct? If the latter, is connected-vs-disconnected (the fermion-loop sign) the right genuine nonseparable
observable, and what is the minimal exactly-enumerable construction that **computes** it (worldline connectivity → sign;
Grassmann determinant → correlator)?

### (3) The toy-vs-lattice question (the big one)

**Can a tiny exact toy genuinely LAND `M/g = 1/√π`, or can it only exhibit the mechanism's *shape* while the scalar
value requires a real (larger) lattice computation?** Concretely: does the predictive-recombination carrier `U_H`, on a
finite exactly-enumerable slab, generate a held-out meson correlator whose decay root *converges to* `1/√π` — or is the
finite toy fundamentally a proof-of-mechanism, with the value landing only at scale? If the latter, what is the honest
deliverable of the toy rung, and what is the minimal real-lattice step where the SAU mass landing becomes meaningful
(out-of-sample, sealed)?

### (4) Concrete next step

Given the above, is the right move (i) **harden step108** into a genuine computed-contraction U(1) construction
(step108b), (ii) go straight to a **small but genuine Schwinger lattice correlator** carrying the
predictive-recombination carrier, or (iii) something else? And what acceptance criterion makes the eventual
`M/g = 1/√π` landing a genuine out-of-sample SAU result rather than a recovered value?

## Where to look in v4

- `six-birds-sm-qm-gr/SIX_BIRDS_UNDERSTANDING/04 §8` (the route) and `02` Part 4 addendum (the hidden-record discipline
  adopted from your round-2 ruling).
- `six-birds-sm-qm-gr/lattice_qcd_layer/manager_log.md` (tail) — the step107d + step108 verdicts in full.
- `.../steps/step107d_branchwise_M_saturation_artifacts/` — the ℤ₂ factorization (driver + table).
- `.../steps/step108_u1_schwinger_nonseparable_obstruction_artifacts/` — the schematic U(1) witness; the driver
  `driver/step108_u1_schwinger_nonseparable.py` (see `pairing_parity` = literal, `joint_flux_closure ≡ 0`, `trans_payload`).
- `.../steps/step107a..c_*` — the ℤ₂ control baseline, the rejected counterfeit (107b), and the currentization
  adjudication (107c), for the full audit trail.

Constraints unchanged: structural register (no scalar value yet); certificate-not-recovery (obstruction first, value
last via an audited SAU landing, out-of-sample); the forbidden-input contract; authority = the papers + the running code.
