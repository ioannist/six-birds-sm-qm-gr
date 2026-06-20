# Theory ↔ pica code — where each strict-extension concept actually lives in code

Grounds the synthesis (`02`) in running code. Two code bodies:
- **The engine (Rust):** `six-birds-pica` (vendored at `lattice_qcd_layer/vendor/six-birds-pica`; canonical at
  `/home/repos/six-birds-pica`). Crates: `six_primitives_core`, `dynamics` (`six_dynamics`), `graph`, `runner`.
- **The strict-extension driver (Python):** `sixbirds_event` in `/home/repos/six-birds-event-package/src/` — runs
  the Rust engine via `pica_bridge` and computes the strict-extension / global-packaging-obstruction verdict.
- The 321-line `closurelab/numeric.py` is the **discarded** python toy (NOT the engine) — listed only to map names.

Citations below are from this session's verified reads + the `engine_study/01–08` notes. Where a line number is
approximate it is marked `~`. Authority is the code itself; re-verify before relying.

---

## A. The substrate / theory package (lens + completion + audit)

| Theory (papers) | Code |
|---|---|
| Theory package = lens `f:Z→X` + completion + audit (primer §2; Found I `def:tk-theory-package`) | Rust `MarkovKernel` + `Lens` + `Substrate` in `six_primitives_core/src/substrate.rs:13,319,367` |
| Minimal substrate class `S_min` (To_Lay_a_Stone): autonomous finite stochastic dynamics, deterministic lenses, packaging endomaps, intrinsic audits `Σ_T` + ACC | `substrate.rs` IS `S_min`: `Lens` (deterministic surjection), `path_reversal_asymmetry` (:460), `acc_affinity` (:499), `cycle_chirality` (:515) |
| Micro kernel `P`, enable matrix `E_pica∈{0,1}^{6×6}`, 36 actor←informant interactions (To_Create_a_Stone) | `dynamics` crate: `PicaConfig` (the 6×6 enable matrix), `dynamics/src/pica/` cells; runner `EXP-100` family builds these |

## B. The packaging endomap `E_{τ,f}` — THE shared engine object (this is P5)

The single most important identity across the whole project:
> `E_{τ,f}(μ) = lift( pushforward( evolve(μ, τ) ) )`

- **Cantor paper:** `E_{τ,ℓ}(μ) = U_ℓ(Q_ℓ(μ K^τ))` (Cantor `.tex:683`).
- **Rust engine:** `Substrate::packaging_endomap` — `lift(pushforward(evolve(dist, tau)))`, `substrate.rs:381`.
- **closurelab (discarded):** `numeric.empirical_endomap`, `E = P^τ Q U`.
All three are the same object. Its **fixed points** (small TV idempotence defect) are the packaged "objects":
`Substrate::idempotence_defect` `substrate.rs:397`; `find_fixed_points` `:407`. (Found I `D-IC-02`.)
The **macro kernel** at a blocking scale is `build_macro_from_ktau(K^τ, lens)` (`six_primitives_core/src/helpers.rs:111`,
uniform within-fiber lift at `:132`), swept over scales by `multi_scale_scan` (`dynamics/src/audit.rs:485`).

## C. The six primitives P1–P6 (Found III names them: descent, representability, route-mismatch, refinement, packaging, audit)

| Primitive (Found I/III defs) | Code realization |
|---|---|
| P1 operator rewrite | `dynamics` action `P1Perturb` (`mixture.rs` `p1_step`); kernel-row perturbation under budget |
| P2 gating/constraints | `P2GateFlip` (`mixture.rs` `p2_step`); `primitives::p2_gate` zeros+renormalizes edges |
| P3 protocol holonomy | protocol phase in `AugmentedState`; `protocol::phase_bias`; route-mismatch `pica/mod.rs` `compute_rm_for_partition` |
| P4 sectors/refinement/lens | `spectral_partition` (`dynamics/src/spectral.rs:94`); lens selection w/ hysteresis `pica/lens_cells.rs` |
| P5 packaging | `build_macro_from_ktau` + `p5_from_p4` (`pica/p5_cells.rs`); the packaging endomap (§B) |
| P6 accounting/audit | budget ledger `drive.rs` `modification_cost` (row-wise KL), `can_afford`; arrow audits `Σ_T`, EP |

## C′. The construction ingredients of strict extension (Cantor `02` Part 2) in code

- **Saturation** (`c^(n)=c`): `find_fixed_points` convergence; the dynamics scan stops producing new packaged objects.
- **Material P4←P5 forcing** (packaging feeds back into the lens): the dynamics `refresh_informants` recomputes the
  P4 lens from P5 packaging each cycle (`pica/mod.rs` lens-cell selection consuming packaging RM) — the code locus
  where packaging changes the active lens. *(Verify exact cell wiring in `pica/lens_cells.rs` + `p5_cells.rs`.)*
- **Macro-admissibility obstruction** (base too coarse / non-lumpable = the CERTIFICATE): measured as
  route-mismatch / closure-deficit on the macro kernel — `route_mismatch` (`numeric`/`pica` RM), `frob_from_rank1`
  (`observe.rs:62`). **High RM / failure to lump is the success signal, not a defect to drive to zero** (`02` §2.4).

## D. The strict-extension VERDICT — where non-factorization is actually computed

**The genuine worked example = `sixbirds_event` (event-package), running the Rust engine.** Paper:
`Locally_Boolean_Globally_Obstructed`. Mechanism (read this session in `audits/quotient_feasibility.py`):

1. Run the pica substrate → discover **contexts** (stable record tests) — `discovery/`.
2. **Quotient-class ledger** (`quotient_feasibility.py:135–244`): trajectories common to all contexts; each
   trajectory's **signature** = its outcome in every context jointly; identical signatures → a **quotient class**.
   These are the candidate **global-package atoms** (the observed joint realizations).
3. Propose **shared-event identifications** across contexts (empirical-identity quotient).
4. **Feasibility** (`:305–365`): `exact_feasible` iff some quotient class respects every identification AND survivors
   cover every atom (`:345`); else **`accepted_proposal_obstruction`** (`:382`) = **strict non-extendability**.
5. **Witness search** (`:472–519`): minimal subset of identifications whose joint realization is impossible.
6. **False-positive controls** (`02` Part 4 guards): protocol-trap / flattening / hidden-record / noise interventions
   (`pipeline/end_to_end.py` intervention suite); regime classification (`globally_packageable` vs
   `multi_context_but_extendable` vs obstructed).

This computes **non-factorization at the JOINT level** (contexts can't be glued into one global package) — emergent,
invisible in any single locally-Boolean context. THAT is the strict extension, computed, not stamped.

- **Structural strictness `δ_fact ≠ ∅`** (the `02` §3.1 defect): realized as the `non_factorization_witnessed` +
  split-pair in the fixed-support series (`Promotion_Criteria`, `Recombination_Witnesses` Lean no-factorization
  corollary). *[Deep read of the series PENDING.]*

## E. The guards (`02` Part 4 — pending deep read, but the code loci):

- **DPI / no fake arrow** (Found I `thm:dpi_path`): `path_reversal_asymmetry` (`substrate.rs:460`) — coarse-graining
  can't increase it; reversible+stationary ⇒ ~0 (the null control).
- **Bounded-interface saturation** (No-Go): the `|Def(f)|=2^{|im f|}` bound — why fixed-lens laddering is impossible.
- **No-overread / no-smuggle** (SAU fields 6): the event-package controls + nonclaim registers; the audit gates.

## F. HONEST gaps — what is NOT realized in code (do not pretend otherwise)

- **The SAU value-landing `U↛_q, C(U)↓_B a^♯`** (`02` Part 3) is a **math-paper register** (Why-Math, the
  fixed-support series, Lean kernels). It is **not** implemented as a scalar-value extractor in the Rust/python
  pica. The event-package computes an **obstruction verdict**, not a scalar like a mass.
- **No lattice/physics substrate** is wired into `sixbirds_event` — its substrates are the toy contextuality
  benchmarks (classical control, epistemic, parity witness) + autonomous PICA discovery. Mapping a lattice transfer
  operator into "contexts / shared events / global package" is **unsolved** → `04`.
- **`closurelab/numeric.py`** (`Ξ`, `build_U_prototype`, `delta_fact`) is the discarded python toy; the validated `Ξ`
  engine lived in `lattice_qcd_layer/steps/step96–97` (also superseded-frame). Whether/how `Ξ` participates in an
  *upward* strict-extension claim is `02` Part 5 (pending).

## G. Bottom line for the project

The engine (Rust pica) genuinely RUNS the six primitives and produces packaged objects + audits. The driver
(`sixbirds_event`) genuinely COMPUTES a strict-extension (global-packaging-obstruction) verdict on a pica substrate.
What is NOT yet in code: (a) a lattice/physics substrate mapped into that verdict, and (b) a lawful SAU value-landing
that descends a *scalar* (a mass) from the obstruction. Both are the project's real open work — and per `02` §2.5 +
§1.8, whether a scalar mass can be a six-birds value at all is the central open question (`04`).
