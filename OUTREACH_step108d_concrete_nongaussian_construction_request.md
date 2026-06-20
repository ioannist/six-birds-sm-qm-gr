# Six Birds × Lattice QCD — round 5: the engine is hardened; we need a CONCRETE non-Gaussian U(1) construction (numbers, not criteria)

Follow-up to round 4. The attached `six_birds_lattice_handoff_v6.zip` is the full current state.

## Since round 4 — your two rulings, both implemented

1. **The PERMANENT semantic-K fix** (`ker E_K = ker q_M`; K defined extensionally as the one-branch predictive quotient
   by partition refinement) — IMPLEMENTED and ACCEPTED (step108c). The engine now computes K by partition refinement to
   a fixed point, asserts `ker E = ker M` in both directions, has a separated determinant backend and stencil-generated
   paths. The recurring "what's admissible in K" failure family is closed IN CODE. We re-tested step108b's pair under the
   semantic K: it correctly **factorizes** (direct `{M0,M3}` ≠ exchange `{M1,M2}`). This was the right fix — thank you.

2. **The two-line connected residue** `Γ² = A² − Alt(A¹⊗A¹)` as the genuine target — we built the boundary-Grassmann
   -tensor search (step108d).

## The honest result: step108d is an artifact — it walked into your Gaussian-determinant lemma

step108d returned `genuine_u1_two_line_exterior_obstruction`. On audit it is an artifact, on four grounds — the first
being exactly the failure you predicted:

- **`A² ≡ det(A¹)` by construction.** The driver defines the two-line response as the 2×2 determinant of the one-line
  kernel (`grassmann_two_line_tensor` = `grassmann_wedge_two(one_line_matrix)`, line 128). So at fixed background
  `A²_U = ∧²A¹_U` identically (the "null" is vacuous), and the only nonzero `Γ²` is the character-sum cumulant
  `⟨det A¹_U⟩ − det⟨A¹_U⟩` — a pure Gaussian-determinant cumulant. This is precisely your lemma: *"if K_sat contains the
  complete one-particle kernel G, ∧²G is a function of K_sat ⇒ factorizes."*
- **K computed on the gauge-AVERAGED `A¹`** (the coarse-K failure again, now hidden in the character sum): the two
  configs have different per-background one-line kernels but average to the identity, so they were called "K-equal" only
  after the average washed out the difference (`semantic_k_signature` reads the averaged matrix, line 235).
- The "independent" determinant was the **same 2×2 formula twice**; the two "configs" were two flux **prescriptions**
  (`all_generated_stencil_bridges` vs `oriented_boundary_flux_sector`), not physical configurations.

So a Gaussian / free-fermion-in-background U(1) boundary tensor **always** factorizes. We have no genuine U(1)
obstruction.

## The meta-problem: criteria keep being satisfied degenerately

This is the **sixth** construction (107b, 107c, 108, 108b, 108d) where our constructor produces an object that passes
every stated gate and then dies on audit — each time by building the *easiest* object the criteria allow (a coarse K, a
literal label, `A²=det A¹`). The engine is now trustworthy; the constructor's *creativity* is the bottleneck. We expect
another criterion would be satisfied degenerately again.

## The ask: hand us the actual object, with numbers

We are not asking for more criteria. We are asking for a **concrete minimal worked construction** we can run through the
(now hardened) engine. EITHER:

**(A) a genuine non-Gaussian U(1) Schwinger obstruction**, specified numerically:
1. the exact tiny lattice (`Lx`, `Lt`, `p_max`, boundary conditions, the seam);
2. the two specific configurations `B`, `B'` — what physically differs (NOT a prescription switch);
3. their per-background one-line kernels `A¹_U(B)` and `A¹_U(B')` — the actual entries — demonstrating they are
   **identical** (genuinely K-equal under the saturated per-background quotient);
4. the **non-Gaussian** two-line responses `A²(B)`, `A²(B')` — the actual entries — demonstrating `A² ≠ det(A¹)`
   (genuine four-fermion correlation, gauge-mediated) and `A²(B) ≠ A²(B')`;
5. the gauge-action weight that makes `A²` non-Gaussian (the specific plaquette weights / character sum, NOT a uniform
   average);
6. the connected residues `Γ²(B)`, `Γ²(B')` — the numbers — the genuine obstruction;
7. a held-out continuation that separates `B` from `B'` (for the step108e transport-essentiality test).

**OR (B) the verdict that U(1) cannot host it.** If the massless Schwinger model's exact solvability (it bosonizes to a
free boson of mass `e/√π`) means every two-line response factorizes through the right one-body / branch-local data, say
so DEFINITIVELY — and give us instead the concrete minimal **multiple-intertwiner** construction (the smallest SU(2)
four-leg or SU(3) meson-meson recoupling with the same one-branch representation content but ≥2 fusion channels), with the
same numeric specification (the two configs; the identical one-branch content; the distinct intertwiner-channel response;
the residue).

## The sharp physics question behind it

Does the massless Schwinger model actually **contain** a genuine non-factorizable two-line obstruction, or does its exact
solvability force factorization — so that `M/g = 1/√π` must be landed via the **bosonization recombination itself** (the
fermion-bilinear → boson map as the genuine `R`), or only at non-abelian recoupling? You are better placed than us to
settle this from the physics; it decides whether step108e runs on U(1) or on the SU(N) rung.

## Where to look in v6
- `SIX_BIRDS_UNDERSTANDING/04 §8` (route + the `Γ²` mechanism + the now-realized Gaussian-determinant trap);
  `02` Part 4 (the semantic-K rule).
- `lattice_qcd_layer/manager_log.md` (tail): step108c (ACCEPTED, hardened engine) + step108d (REJECTED, artifact)
  verdicts in full.
- `.../steps/step108c_semantic_K_hardened_engine_artifacts/` — the trustworthy engine (semantic K, partition refinement).
- `.../steps/step108d_u1_boundary_tensor_connected_residue_artifacts/` — the artifact (see `A²=det(A¹)` at driver line
  128; K on averaged `A¹` at line 235).

Constraints unchanged: structural register (no scalar value yet); certificate-not-recovery (obstruction first, value last
via an audited out-of-sample SAU landing); the forbidden-input contract; authority = the papers + the running code.
