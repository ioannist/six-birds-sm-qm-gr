# PROG2 — track closure (2026-08-27)

> **REOPENED 2026-08-27 (owner direction):** this document stands as the certified checkpoint of
> steps 1–2; the owner directed continuation into the successor steps the same day. Continuation
> is recorded in manager_log.md and the step3+ packets.

**Track question** (open program 2 of `review_2026/CLAIMS_MAP.md`, P1 route 2): build a
state-level example in which independently contracted boundary states — not cut fingerprints
alone — underdetermine a physically quotiented bulk geometry.

**Status at closure: the question remains open; the first preregistered evaluation returned a
convention-scoped negative at dense-numerical-evidence grade.** Two reviewer-PASSED packets (step1_engine/, step2_fiber_states/):

1. **Certified infrastructure** (step1_engine/): an explicit dense numerical contracted-state
   entropy engine — full 2^|T| entropy vectors from the contracted boundary state only, with a
   structurally checkable anti-bypass property (tensor seeds and capacity-independent base
   tensors are independent of cut machinery; stored cut-weight provenance cannot influence
   dimensions, tolerances, or entropy post-processing; in Step 2, capacities enter only through
   the declared edge-state dressing), four
   verified state-level gauge moves, injective and degeneracy controls including a
   survivor-scale gauge-invariant obstruction, and full numerical accountability (no silent
   truncation; discarded mass and error reporting). All 13 PROG3 carriers were tractable for
   random tensors at D=2,3,4 and copy tensors at D=2.

2. **The fiber evaluation** (step2_fiber_states/): the same 19 exact-rational fiber pairs whose
   endpoint orbits PROG3 saturated and found disjoint under the five declared moves were
   confirmed cut-identical by exhaustive exact enumeration and evaluated under the preregistered
   capacity-to-state convention sqrt(c/(1+c))|00> + sqrt(1/(1+c))|11>. Result, graded as dense
   numerical evidence (not a certificate): **all 19 pairs SPLIT**: all 4,314 nontrivial subset
   comparisons lie beyond the preregistered numerical allowance, while the 38 empty/full
   comparisons coincide. The smallest nontrivial split is approximately 4.0e-6 nats against a
   1e-10 allowance. Two named witnesses were reevaluated at 80 dps and agree with the dense
   outputs to approximately 1e-16; the reviewer independently reconstructed the weakest
   fiber-004 witness. Controls: a non-kernel perturbation SPLIT
   (non-vacuousness) and a capacity-dressed gauge pair COINCIDE at ~1e-16 (degeneracy).

**Reading (certified wording):** for this declared convention and tensor family, contracted-state
entropies provide dense numerical evidence of strict refinement of the complete terminal min-cut
fingerprint on every tested fiber. Accordingly, the graph-level fibers do not transfer to
state-level underdetermination by this route. This is a convention-scoped negative search result,
not a proof that no capacity-to-state map or state family can yield a candidate — and the
reviewer's analysis notes SPLIT is the generically expected outcome for an injective
edge-spectrum map, so the negative is informative about the route, not surprising.

**Reopening condition (binding for any successor):** `step2_fiber_states/step3_contract_requirements.md`
(reviewer-authored) — a preregistered, independently motivated convention family with a stopping
rule and all outcomes published; a state-level kernel test characterizing
ker J_cut ∩ ker J_state, with only symmetry-protected or certified-null directions proceeding; a
distinct-capacity analytically coincident can-fail control; an explicit numerical-evidence or
certificate grade; and any COINCIDE candidate must still pass state-level gauge closure and an
independent bulk-invariant test before any underdetermination claim. Sequential convention
shopping is excluded by construction.

**What this closure does NOT claim:** no state-level underdetermination example; no canonical or
uniquely physical capacity-to-state map; no theorem covering other tensor ensembles, bond
dimensions, conventions, or continuum states; no RT equality; and no inference that future
entropy-vector coincidence would establish state equality or bulk inequivalence. Such
coincidence would remain only a candidate pending state-level gauge closure and an independent
bulk invariant. PROG3's graph equivalence result also remains restricted to its five declared
move classes.

**Relation to the published paper:** neither the v2 paper nor `review_2026/CLAIMS_MAP.md` is
modified by this closure. The sought contracted-state underdetermination construction remains
unlanded: this track built the required state engine and tested the 19 graph fibers under one
declared convention, obtaining a convention-scoped negative at dense-numerical-evidence grade.
It does not supersede the P1 OPEN-PROGRAM disposition. Folding these results into any future
claims map or paper version is a separate owner decision.

Track artifacts: manager_log.md, step1_engine/ (with step2_contract_requirements.md),
step2_fiber_states/ (with step3_contract_requirements.md). Validation:
`step1_engine/run_step1.py --self` and `step2_fiber_states/run_step2.py --self`.


---

# FINAL OUTCOME (2026-08-27, appended after the owner-directed continuation)

The continuation (steps 3–5: kernel test, exact finite continuation, corrected family-gauge
classification) reached a positive terminal result. Terminal reviewer verdict (assignment 51):
CODE/SCIENCE/GRADE PASS, zero adverse findings; the word **example** is certified relative to the
frozen declared relation. The definitive track statement, reviewer-authored verbatim:

> PROG2 constructed an explicit dense-numerical contracted-state entropy engine with four verified
> tensor-presentation moves and non-vacuous controls. Under its first declared injective
> capacity-to-state convention, all 19 exact cut-fiber pairs split at the state level: 4,314 of
> 4,352 subset comparisons split within the preregistered numerical allowance, while the 38
> empty/full comparisons coincide. Across the preregistered five-member convention/tensor family,
> all 76 seeded-random rows have trivial cut/state-kernel intersection; the connected C2_L1 copy
> member has 11 nonzero rows representing six distinct carrier-level directions, explained
> analytically by its product symmetry. The exact tangent-plane lemma excludes nonzero
> product-preserving displacements within the tangent subspace but not within the complete cut
> kernel. Searching the complete kernel constructs six positive exact-algebraic finite
> continuations with identical complete terminal min-cut fingerprints, exactly equal copy
> products, and identical connected-copy boundary states. Under the frozen corrected family
> relation — terminal-fixed weighted isomorphism, tensor-presentation gauge that does not act on
> capacities, boundary-local unitaries, and identity/global all-edge reciprocal as the only
> family-returning reciprocal actions — all six pairs are exact finite C2_L1 declared-gauge
> underdetermination examples, separated by the exact invariant I(c) = {sum_e c_e, sum_e 1/c_e}.
> This conclusion remains specific to these finite carriers, the C2_L1 family, the declared
> capacity convention, and the frozen gauge relation; other tensor families, conventions, broader
> physical gauge relations, continuum limits, and any interpretation as underdetermination of
> bulk geometry remain open.

Artifacts: step3_kernel_test/, step4_finite_continuation/, step5_family_gauge_classification/
(validators: run_step3.py / run_step4.py / run_step5.py, all --self). The intermediate documents
above (the step-2 checkpoint and its reopening note) are retained as the historical record.

---

<a id="step-6-retyping-controlling-terminal-wording"></a>
## STEP 6 RETYPING (2026-08-27) — CONTROLLING TERMINAL WORDING

An external adversarial review of the published Version 3 constructed, for all six Step-5 pairs, an
explicit diagonal internal-bond tensor gauge (float residuals ~1e-16; reproduced on this tree).
Because declaration_step5.md itself admits a move into the state-gauge relation "only after an
explicit tensor-level intertwiner is constructed," Step 6 (step6_exact_gauge_collapse/) exactified
that intertwiner and retyped the track's theorem objects. Reviewer verdict on the packet:
CODE/SCIENCE/GRADE PASS (fix round: general-lemma wording, portable external control, three
can-fail negative controls; manager validator reruns pass in-place and from a foreign checkout).

The literal Step-5 classification above REMAINS CORRECT under its frozen capacity-label-preserving
decorated relation; Step 6 retypes the tensor presentations after constructing the previously
missing intertwiner. The Step-5 statement is retained as the historical record; the CONTROLLING
terminal wording of the track is the following, reviewer-certified verbatim (assignment: STEP6
confirmation round):

> On any fixed connected binary-copy `C2_L1` carrier with positive capacities, the normalized
> boundary state depends only on the total edge-capacity product, and any two equal-product
> assignments admit an exact diagonal internal-bond intertwiner up to vertex-wise scalars. The six
> constructed positive-algebraic same-graph pairs are exact noninjective fibers of the joint
> complete-cut/state map and exact instances of this gauge-collapse lemma. They are therefore not
> inequivalent tensor-network presentations. Their exact `I(c)` separation survives only for the
> frozen capacity-label-preserving decorated-carrier relation; the literal Step-5 classification
> remains correct under that stipulation, while Step 6 retypes the tensor presentations after
> constructing the previously missing intertwiner. No physically complete bulk gauge relation or
> bulk-geometry underdetermination theorem is established.

Retired headline: "six exact finite declared-gauge underdetermination examples." Replacement:
"six exact fibers of the joint cut/state map, gauge-collapsible at the tensor level, separated by
I(c) only under the frozen decorated-carrier relation."

Artifacts: step6_exact_gauge_collapse/ (validator: run_step6.py --self; evidence taxonomy
COMPUTED / PROVED_BY_DEFINITION / EXTERNAL_REPRODUCED; external review materials in
external_input/).
