# Six Birds × Lattice QCD — round 2: step106–107c results, a crux adjudication, and a request for next-step directions

Follow-up to your earlier advice, which we adopted and verified. The attached zip
`six_birds_lattice_handoff_v3.zip` has the **full current state**; this note summarizes what we built, what we
found, and the one adjudication that gates everything next.

## Recap: your route, adopted + verified against the papers

We verified your route ourselves against `Holonomy_with_Memory` (current quotient `Q` ← predictive quotient `M`,
predictive transport `T^M` = the carrier's native transport) and `Marking_Erasure_and_Recombination` (branchwise `K`
vs recombination `R`; `R≃K` = packageable control; **Obstruction-by-strict-refinement** = `K`-equal-but-`R`-distinct ⇒
no global branchwise factorization, with a concrete finite aligned instance). That last theorem is what dissolved our
earlier "Euclidean = classical = globally packageable" worry: a recombination obstruction is corpus-proven on fixed,
finite, *classical* support. We froze the route as `Q_H←M_H←(K_H,R_H)→𝓔_H→U_H→C(U_H)=m_H` on a local Euclidean slab
grammar (see `SIX_BIRDS_UNDERSTANDING/04 §8`).

## What we built (and the honest verdicts — full record in `lattice_qcd_layer/manager_log.md`)

- **step106 (freeze) — ACCEPTED.** Euclidean slab grammar + four completion contexts (`c_K` branchwise, `c_G`
  gauge-dressed, `c_R` singlet-recombination, `c_T` slab-composition) + `BridgeLevelLawBasis_H=(L_read,L_quad,L_trans)`
  + shared-event rules, all frozen. The forbidden-input contract bans the value-recovery smuggling vectors (no supplied
  ground vector / spectral readout / tail fit / benchmark mass). `L_quad` uses reflection positivity as a *bridge law*
  (which recombination-pair records count as the same event), explicitly **not** as a scalar estimator.
- **step107a (control baseline) — PASS.** Exact tiny ℤ₂ gauge-matter slab; both controls (`decoupled_zero_hopping`,
  `branch_factorized_R=K`) come out **packageable**, with an exact quotient solver == an independent full-enumeration
  comparator. The discriminator's negative pole is established; the machinery does not hallucinate obstruction.
- **step107b (first obstruction attempt) — REJECTED by our audit as a COUNTERFEIT.** Reading the driver, the
  `K`-equal/`R`-distinct structure was **hard-coded in string labels** (both branches `summary="coupled_pair"`;
  `recombination_class` distinct), the ℤ₂ gauge weights were **unused** in the feasibility verdict, and the
  false-positive controls were **vacuous** (identical records). The obstruction was a label artifact, not physics-forced.
- **step107c (repair) — GENUINE code, and the result is the crux.** This time: `K` is computed from per-branch
  predictions (independent of holonomy → `K`-equal); `R` is computed from the **enclosed ℤ₂ holonomy / Wilson loop**
  (→ `R`-distinct); the classes are content-hashes, not labels; the **coupling ablation** (trivial flux) genuinely
  collapses `R→K` to packageable; the **dependency trace** confirms `R` flips with the holonomy (gauge load-bearing);
  and the controls produce genuinely different records. So the obstruction **is physics-forced**. It was classified
  `artifact` for one reason only: the **hidden-record control removes it**.

## The crux adjudication (this gates everything next — your discipline call)

The hidden-record control removes the obstruction by exposing the **joint** (two-branch loop) enclosed ℤ₂ holonomy to
the **branchwise** (per-branch) quotient `K`: once `K` records the holonomy, `K` distinguishes the same configurations
`R` does, so the package becomes feasible.

Two readings, opposite conclusions:

1. **Legitimate hidden-record exposure → `artifact` stands.** The holonomy is a physically accessible
   (gauge-invariant Wilson loop) quantity; if recording it removes the obstruction, the obstruction was an artifact of
   an under-specified lens. **The deeper worry this raises:** on a *classical* Euclidean substrate the
   recombination-distinguishing record (the holonomy) is *always* accessible — so classical gauge recombination
   obstructions may *always* be hidden-record-removable, i.e. never genuine strict extensions. That would re-open the
   feasibility question on the Euclidean side (where the mass lives).
2. **Illegitimate `K→R` collapse → the obstruction is genuine.** `K` is *definitionally* the branchwise (per-branch)
   quotient; the holonomy is a *joint* (two-branch) property. Handing a joint quantity to a branchwise quotient simply
   collapses `K` into `R`, which trivially removes *any* `K`-equal/`R`-distinct obstruction — making the hidden-record
   control **vacuous** (it would kill *every* Marking recombination obstruction). Since Marking *proves*
   `K`-equal/`R`-distinct is a genuine non-factorization, a control that can always defeat it is overreaching.

**The deciding question: may the hidden-record / no-overread control expose a joint / recombination-level quantity
(the Wilson loop) to a branchwise context — or does the branchwise nature of `K` forbid it?** This is a discipline
question about SBT's hidden-record and no-overreading controls, and it determines whether we have a genuine obstruction
(→ promote the carrier `U_H`, step108) or a real negative (→ ℤ₂ too simple / a classical limitation → repair the rung).

## What we'd like directions on

1. **The adjudication above.** Is the hidden-record control (exposing the joint holonomy to branchwise `K`) legitimate
   or overreaching? What is the correct hidden-record / no-overread discipline here — precisely what may such a control
   expose, and to which contexts?
2. **If `artifact` is correct:** is this ℤ₂-specific simplicity (try richer gauge — U(1) Schwinger, SU(N) — where the
   distinguishing record is not a single accessible Wilson loop), or a deeper *classical* limitation (the recombination
   record is always accessible on a Euclidean substrate)? If the latter, what is the honest path — does a genuine,
   non-removable recombination obstruction require structure the tiny classical slab cannot provide?
3. **If the obstruction is genuine** (the control overreached): confirm the correct hidden-record control to re-run,
   and the criteria for promoting the carrier `U_H` (step108) and then the first audited mass landing (step109 —
   massless Schwinger `M/g = 1/√π`, kept sealed / out-of-sample).
4. **More generally:** given the obstruction must survive a *legitimate* hidden-record / no-overread control **and**
   eventually carry the mass (the mass-bearing obstruction gate: the minimal witness must be necessary for the carrier's
   held-out channel transport), what is the **minimal lattice structure where a non-removable recombination obstruction
   lives where the mass lives**? Concrete next steps welcome — including "the Euclidean recombination route is the wrong
   layer for the mass, here is the right one," if that is where it points.

## Where to look in the zip (v3)

- `six-birds-sm-qm-gr/SIX_BIRDS_UNDERSTANDING/04_THIS_PROJECT_AND_OPEN_QUESTIONS.md` §8 — the adopted route + plan.
- `six-birds-sm-qm-gr/lattice_qcd_layer/manager_log.md` (tail) — the full step106–107c verdicts + this crux.
- `six-birds-sm-qm-gr/lattice_qcd_layer/steps/step107c_physics_forced_obstruction_artifacts/` — the genuine driver
  (`driver/step107c_physics_forced_obstruction.py`), the obstruction table, the engine output, the results summary.
  The hidden-record control is `coupled_hidden_record` / `hidden_holonomy_for` / the `licensed_current_holonomy` field
  added to `branchwise_content` (~line 117).
- `six-birds-sm-qm-gr/lattice_qcd_layer/steps/step107b_coupled_obstruction_test_artifacts/` — the rejected counterfeit,
  for contrast (and as a record of the smuggling failure mode we are guarding against).
- `six-birds-sm-qm-gr/lattice_qcd_layer/steps/step107a_z2_slab_control_baseline_artifacts/` — the packageable baseline.

Standing constraints (unchanged): structural register only (no scalar value/mass yet); certificate-not-recovery (the
obstruction comes first, the value descends last via an audited SAU landing, out-of-sample); the forbidden-input
contract; authority = the papers + the running code, not any synthesis.
