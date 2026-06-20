# Six Birds × Lattice QCD — round 4: a genuine Grassmann engine, a premature U(1) obstruction, and the saturated-K admissibility rule

Follow-up to round 3 (your equivariant-K, Grassmann-derivation, and cross-scale rulings — all accepted and folded into
the base). The attached `six_birds_lattice_handoff_v5.zip` is the full current state.

## Since round 3

step108b built the genuine engine you specified: an exact local Grassmann compiler (input schema **label-free**;
contraction graph / cycles / sign / link current / flux completion all **computed**, not labeled), U(1) flux with a
gauge ablation, the ℤ₂ gate-0 frame-equivariance audit (passed — `W` frame-invariant), and a minimal-geometry search.
The crux pair is the genuine **connected-vs-disconnected meson contraction** (direct = two cycles, `+1`, flux 0;
exchange = one cycle, **−1 fermion-loop sign**, flux 1). The Grassmann↔determinant polynomials match. The mechanism
*shape* is right and the engine is a real advance over the schematic step108.

## The honest problem: the obstruction is premature (coarse K)

On audit, step108b's `genuine` verdict does **not** survive a properly saturated `K`:

- the branch signature it hashes is `{charge, catalog, hop_power}` only — it **omits the per-line link current**;
- but the direct lines carry current `{0, 0}` while the exchange lines carry `{(1,0,1,0), (0,1,0,−1)}`;
- the per-line current is a **branch-local, gauge-covariant** quantity, so by your own equivariant-`K` rule it should
  enter a saturated `K`. Including it makes `K_sat(direct) ≠ K_sat(exchange)` ⇒ the pair is no longer `K`-equal ⇒ it
  **factorizes — exactly the ℤ₂ collapse from step107d.**

**Root cause:** step108b used *distinguishable* worldlines (different per-line currents) for direct vs exchange. We
believe the genuine nonseparable obstruction is the **identical-fermion exchange antisymmetry**: *identical* per-line
data (so genuinely `K`-equal even when saturated), connectable two ways, with the exchange contributing a Grassmann
`−1` and **no** per-line difference (Pauli). step108b did not capture that.

(Two lesser items, already flagged for hardening: the "Dirac determinant comparator" re-uses the same graph machinery
rather than being a truly independent determinant of `D[U]`; and the transport check is a schematic `sign·(flux+2)`, not
an actual glued-slab Grassmann correlator.)

## The pattern we want you to close off

This is the **fourth consecutive** subtle correction, and all four are the same family — **what is admissible in the
saturated branch-local quotient `K`:**

| step | what slipped into / out of `K` | your / our ruling |
|---|---|---|
| 107c | a joint Wilson loop exposed *to* `K` | currentization, not artifact removal |
| 107d | an open transport relative to a *frozen frame* in `K` | framed-`K`; equivariant rule |
| 108  | a bare contraction-parity *label* | schematic, not derived |
| 108b | the per-line link current *omitted from* `K` | coarse `K` |

We keep rediscovering the boundary per rung. **Could you give a crisp, general admissibility criterion for the
saturated branch-local `K`** — precisely what a record must satisfy (stage; branch-support; gauge-covariance typing;
dependency on recombination/slab-composition; frame-equivariance) to be admitted — plus a short checklist that would have
caught all four cases? That would let us stop relitigating it per rung and bake it into the validator.

## The questions

1. **Is the per-line link current branch-local-admissible in `K_sat`?** If yes (our reading), step108b's pair
   factorizes and U(1) with *distinguishable* worldlines does not give the obstruction.
2. **Is identical-fermion exchange the right genuine nonseparable observable** (identical per-line data, different joint
   Grassmann sign)? If so, what is the minimal exactly-enumerable U(1) Schwinger construction that realizes it — e.g.
   ≥2 identical-charge fermion legs admitting two contraction matchings that differ *only* by an antisymmetry sign, with
   all per-line data identical?
3. **Or is abelian U(1) fundamentally too decomposable**, so a genuine nonseparable obstruction requires **SU(N)
   three-branch color-singlet recoupling** (relative color orientation being irreducibly joint)? If so, we should jump
   the rung ladder accordingly.
4. **The general `K`-admissibility criterion** (above) + the **hardening spec** (a genuinely independent `det D[U]`
   backend; an actual glued-slab correlator for transport-essentiality).

## Where to look in v5

- `six-birds-sm-qm-gr/SIX_BIRDS_UNDERSTANDING/04 §8` (route + the cross-scale mass-landing answer) and `02` Part 4
  addendum (the hidden-record + equivariant-`K` discipline adopted from rounds 2–3).
- `.../lattice_qcd_layer/manager_log.md` (tail) — the step108 and step108b verdicts in full.
- `.../steps/step108b_exact_grassmann_u1_recombination_artifacts/` — the genuine engine; driver
  `driver/step108b_exact_grassmann_u1.py` (see `branch_signature_multiset` omitting the per-line current;
  `graph_from_terms`; `determinant_expansion` re-using it).
- `.../steps/step107d_branchwise_M_saturation_artifacts/` — the ℤ₂ saturated-`K` factorization (the precedent).

Constraints unchanged: structural register (no scalar value yet); certificate-not-recovery (obstruction first, value
last via an audited SAU landing, out-of-sample); the forbidden-input contract; authority = the papers + the running code.
