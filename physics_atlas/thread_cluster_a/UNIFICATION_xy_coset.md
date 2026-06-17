# The X/Y colored coset — one structural object, several computed roles (paper-ready synthesis)

> **Purpose.** A single, citeable synthesis so the central through-line of the Cluster-A gauge-structure work is
> immediately pickup-able when writing the paper. Everything below is *computed and cross-checked in the step
> records* (the same witness IDs recur across steps); this note just collects it + states the honest grade so
> the paper does not overclaim.

## The object

The **X/Y colored coset**: the broken-coset gauge bosons that are **charged under the unbroken confining
(color) sector**. Concretely, in the worked single-factor example SU(4)→SU(3) (`support_08`), this is the set
of **6 generators** `s08_broken_confining_charged_00 … _05` (3 conjugate pairs, finite U(1) charge ±1). In the
SM-clean structure 2|3 (SU(2)×SU(3)×U(1)), **this set is EMPTY** (the electroweak breaking is colorless;
`Δ_fact = ∅`). These are the GUT "X/Y"-type bosons.

**The whole result turns on a single fact: in the SM-clean structure this coset is absent (empty); in a
single-group dynamical breaking it is present.** Its absence is what simultaneously gives every consequence
below.

## The roles (one object, recurring across 5 step-records)

| # | Role | Step | Computed quantity / cross-check (artifact) |
|---|---|---|---|
| 1 | **What clean-separation forbids** (structure-selection lever) | 38 | `broken_vector_exotic_count` = **0** for the 8 SM-signature 2\|3 survivors, **6** for SU(4)→SU(3); clean-separation = "no such coset". `step38_mode_b_higher_layer_shadow_uniqueness_artifacts/` |
| 2 | **Factorization-defect Δ_fact = ∅ witnesses** *(same condition as #1, in the non-factorization calculus)* | 41 | `Δ_fact = ∅` for SM survivors, `≠∅` with **6 witnesses** for SU(4)→SU(3); faithfulness gate: witnesses = the coset = #1's exotics. `step41_mode_b_factorization_defect_clean_separation_artifacts/` |
| 3 | **Proton-decay mediators** (F27, conservation = orbit descent) | 45 | the coset generators are the **orbit-enlargers** (q↔lepton) → baryon number fails to descend (obstruction 3) → decay; `xy_delta_witness_identity = True`. `step45_mode_b_proton_decay_F27_artifacts/` |
| 4 | **Monopole coset** (F48, topology = global gluing invariant) | 46 | the coset carries the **gluing obstruction** (=3, 3 charged pairs) → monopole; `coset_equals_delta_witnesses = True`. `step46_mode_b_monopole_F48_artifacts/` |
| 5 | **GUT↔SM non-factorization refinement-witness** (descriptive one-vs-two) | 47 | `Δ_fact(SM,GUT) = 15` over the coset (the GUT splits what the SM merges) → GUT is a **genuine structural refinement**, not redundant re-lensing; witness identity = True. `step47_mode_b_gut_sm_nonfactorization_artifacts/` |

The witness IDs `s08_broken_confining_charged_00..05` are **literally the same set** in steps 41, 45, 46, 47
(each step records the identity-check), so the unification is in the data, not just in prose.

## The paper through-line (one sentence)

> The SM-clean gauge structure is exactly the one whose **X/Y colored coset is absent (`Δ_fact = ∅`)**, and that
> single absence is simultaneously (i) why it is the clean-separation survivor, (ii) why **baryon number descends
> in the finite clean-shadow reading** (a conditional finite proton-stability *consequence*, not a physical
> result), (iii) why **the finite gluing obstruction is zero in that reading** (no monopole *in the clean-shadow
> reading*), and (iv) why it is descriptively a genuine refinement of — not a redundant copy of — the GUT.
> **All four are conditional on clean-separation** — which is itself now **grounded one layer up** as the
> down-shadow of a **memory-stability** layer (Steps 57–59) — and the proton/monopole fork (ii)/(iii) is now
> **resolved to the clean branch by that same memory-stability source** (Step 65: a record-bearing structure
> cannot be in the decaying branch). Both are **conditional / enumeration-strength / frame-transfer-limited**:
> the clean reading is structurally *selected*, **not** proven of the physical proton.

## HONEST GRADE (must travel with the result — do not drop in the paper)

- **All five roles are StructDown / structural, and all are CONDITIONAL on clean-separation.** Clean-separation
  was an **introduced recognition source** (Step 39: not toy-derivable *within the gauge layer*), and is now
  **GROUNDED one layer up** as the gauge-shadow of a **memory-stability** layer (Steps 57–59: non-circular,
  enumeration-robust across the 11,990-structure carrier + outside probes; the all-structures theorem **L60→L64**
  is the open upgrade). A relocation up the tower, **not** derivation-from-nothing.
- **Not physically certified — but the fork is now framework-RESOLVED.** Roles 3/4 (the proton/monopole fork) are
  **resolved to the clean branch by memory-stability** (Step 65): no ¬clean-sep structure has both a stable
  substrate and record capacity, so any record-bearing structure is in the clean (no-decay / no-monopole) reading
  — a **SELECT** resolution, **conditional on memory-stability, enumeration-strength, frame-transfer-limited**
  (it selects the *structural* branch, **not** a physical proof the proton is stable). Role 5 (GUT↔SM) is the
  *descriptive* one-vs-two; **Step 63 further GROUNDS the unification parent** (computing the embedding ratio
  `sin²θ_W = 3/8` + `k_Y = 5/3`, conditional on a declared minimal-simple common-refinement source).
- **Frame-transfer unproven; finite toy; bounded window** (conditional window-closure, Steps 43-44: single-factor
  ∞-closed, factor-count cap-conditional).
- So the unification is a **structural / conditional coherence** — a strong, honest *organizing* result — **not**
  a physical theorem. The physical reality of the coset (= would-be proton decay / monopoles, unobserved) is the
  standing open question. Note: an earlier informal write-up said "six roles"; the accurate count is the five
  step-records above (roles 1 and 2 are the same clean-separation condition stated two ways).

## Pointers
`manager_log.md` STEP 38–47 (audit trail); `gut_problems_vs_sbt_laws.md` (F-law map); `TODO.md` (open
directions); the five step artifact dirs above (each with `results_summary.md` + the identity-check CSV).
