# External Technical Review — *To Kill Three Stones with Six Birds* Version 3 and Verification Campaign

**Review date:** 2026-08-27  
**Repository reviewed:** `six-birds-sm-qm-gr` from `six-birds-sm-qm-gr-review-package.zip`  
**Decision:** **Major revision**  
**SBT assumption:** The Six Birds Theory corpus was treated as correct and in scope only as the framework against which this application should be interpreted. I did not review SBT itself.

## Executive verdict

The repository contains several genuine, reproducible finite results. The strongest are:

1. exact nontrivial fibers of the complete terminal min-cut map on 13 fixed weighted graph topologies;
2. six exact positive-algebraic fibers of a joint map consisting of the complete cut fingerprint and a connected-copy boundary state;
3. a reproducible finite Standard-Model carrier and branch census under an explicit capped grammar;
4. an exact reconstruction of standard regular-embedding `SU(5)` group theory; and
5. exact finite max-flow/min-cut primal-dual certificates on one graph carrier.

Two Version-3 headline closures do **not** survive adversarial inspection in their present wording:

- **PROG3:** the code exhausts a directed forward rewrite system, not a symmetric five-class gauge equivalence. Its first four classes are reduction-only, while only Delta–Y/Y–Delta is bidirectional. Disjoint forward closures therefore do not establish “complete orbit disjointness” or gauge inequivalence. A one-edge inverse-series construction gives an explicit exact fingerprint-preserving state that reduces back to a certified endpoint but is absent from its purported saturated orbit.
- **PROG2:** the six exact joint-map fibers are real, and the proposed invariant is invariant under the authors’ literal frozen relation. But the relation deliberately forbids internal tensor gauge from re-canonicalizing capacity-dependent copy tensors. For every one of the six pairs, a connected-graph incidence construction supplies diagonal internal `g,g^-1` gauges that map the base canonical local tensors to the target canonical local tensors up to harmless vertex scalars. Thus the six pairs are not robustly inequivalent as tensor-network presentations. Their exact noninjectivity survives; the stronger physical or gauge-inequivalence reading does not.

The Standard-Model branch counts and `SU(5)` computations reproduce. The branch result is, however, a theorem of the declared proxy grammar rather than a physical symmetry-breaking selection theorem. The “clean defect” and cleanliness flag are both functions of the same inherited broken-vector count, and every active nontrivial representation is assigned the residual proxy `SU(N-1)` without a stabilizer calculation or multi-VEV alignment analysis.

The paper’s extensive qualifications are unusually candid, but they do not cure the two closure errors because the abstract, introduction, predictions section, README, and discussion repeatedly promote the disputed conclusions. The title is not defensible: no Standard-Model, quantum-mechanical, or gravitational problem is “killed.” The subtitle’s “common grammar” claim is defensible at a modest methodological level.

The strongest SBT-grounded interpretation is not that this paper engineers an emergent SM/QM/GR successor theory. It does not complete strict extension, reclosure, promotion, or physical bridge construction on any of those fronts. Its strongest framework-level contribution is instead an **SBT-guided theory-repair case study**: typed failures were converted into reconstructed carriers, sharper finite theorem objects, explicit countermodels, and successor construction requirements. That is an engineering claim, not merely an audit claim, but it concerns the research package rather than a newly promoted physical theory.

---

## Principal findings

| ID | Finding | Verdict | Confidence |
|---|---|---:|---:|
| P3-1 | Thirteen fixed carriers support 19 exact nondegenerate complete-cut-fingerprint directions | **Holds** | 0.99 |
| P3-2 | The endpoint sets are “complete five-move orbits” and prove declared-gauge inequivalence | **Does not hold as written** | 0.995 |
| P3-3 | Kalman–Krauthgamer makes the five-class repertoire complete at the relevant level | **Incorrect application** | 0.99 |
| P2-1 | Six same-graph positive-algebraic pairs have identical complete cut fingerprints, equal products, and identical `C2_L1` boundary states | **Holds** | 0.995 |
| P2-2 | `I(c)={sum c_e, sum 1/c_e}` is invariant under the literal Step-5 generators | **Holds by direct proof** | 0.99 |
| P2-3 | The pairs are genuinely inequivalent state-level or bulk examples | **Not established; natural broader tensor gauge collapses all six** | 0.96 |
| SM-1 | The repaired finite carrier and singleton/two-scalar census reproduce | **Holds within the declared grammar** | 0.98 |
| SM-2 | `2|3` is the unique physical gauge structure selected by clean breaking | **Overstated** | 0.97 |
| SM-3 | The regular `SU(5)` centralizer, coset decomposition, `3/8`, and `5/3` results are correct under their imports | **Holds conditionally; largely standard** | 0.995 |
| Q5-1 | The finite graph has exact primal/dual equality and edge shadow-price certificates | **Holds** | 0.99 |
| Q5-2 | The advertised Q5 byte-reproducibility validator passes in the snapshot | **False in this environment** | 1.00 |
| M-1 | The modern validators are meaningful rebuild checks | **Mostly true** | 0.95 |
| M-2 | Passing validators establishes semantic completeness or naturalness of the declared equivalence relations | **False** | 0.995 |
| SBT-1 | The paper accurately characterizes SBT as a fixed, non-dynamical finite catalog | **False relative to the supplied corpus** | 0.995 |
| T-1 | The title is proportionate to the surviving contribution | **No** | 0.99 |

“Confidence” rates my confidence in the review finding, not the scientific importance of the underlying result.

---

# 1. Do the surviving claims hold?

## 1.1 PROG3: complete terminal min-cut fibers

### What is genuinely established

The exact finite-range construction is strong and should be retained. The Step-1 record states that the 13 rows were regenerated from the declared seeded carrier rule rather than inferred from displayed decimals; cut values, margins, ranks, kernels, interval bounds, and endpoint checks use `fractions.Fraction` (`open_programs/prog3_cut_fingerprints/step1_finite_range/results_step1.md:5-17`). It reports the residual-rank histogram through the carrier table and gives 19 nondegenerate exact intervals across all 13 carriers (`results_step1.md:21-35, 45-75`).

For each certified direction, the construction has more content than a single accidental pair. It computes a nondegenerate rational interval on which:

- capacities remain positive;
- the active cut inequalities remain in the same chamber;
- all terminal min-cut values remain fixed along the kernel direction;
- minimizers remain unique; and
- selected distinct endpoints are not related by a terminal-fixed same-graph automorphism.

The strongest accurate mathematical statement is therefore:

> **On 13 fixed exact-rational weighted graph topologies, the complete terminal min-cut map is locally non-injective. Nineteen kernel directions admit nondegenerate rational intervals of positive capacities over which the complete terminal cut-value fingerprint and unique active-minimizer pattern are constant.**

The final Step-2 validator also genuinely regenerates its artifacts in a temporary directory, byte-compares them, and checks the recorded state counts, fingerprints, saturation flags, and verdict fields (`open_programs/prog3_cut_fingerprints/step2_orbit_saturation/run_step2.py:31-117`). My rerun produced:

```text
PASS: fibers=19 endpoints=38 saturated_endpoints=38 complete_disjoint=19
gauge=0 budget_truncated=0 canonical_states_range=1-6
max_replacement_depth=3 recorded_canonical_state_coverage=88
```

Evidence: `prog3_step2.log` in the external evidence bundle.

**Finding P3-1: PASS. Confidence 0.99.**

### Why “complete five-move orbit” is not established

The relevant implementation is not a symmetric move closure.

In `saturation_engine.py:95-157`, the first four move families are directed reductions:

- remove a bivalent nonterminal by `series`;
- replace a two-terminal module only when the candidate has fewer edges;
- contract a zero column;
- contract inseparable vertices.

Only `delta_y_y_delta` supplies both directions through `fifth_candidates`. The breadth-first loop then exhausts this directed proposal system (`saturation_engine.py:160-234`). When two directed closures do not intersect, the code writes the verdict `complete five-move-orbit-disjoint (saturated)` (`saturation_engine.py:237-264`). The validator checks that same label rather than independently establishing that the transition system is an equivalence (`run_step2.py:49-59`).

This is a category error:

- queue exhaustion proves complete **forward reachability** under the coded directed rules;
- an orbit or gauge class normally means the equivalence generated by moves and their inverses, or a separately proved canonical-normal-form theorem;
- disjoint forward-reduction cones do not imply inequivalence unless confluence and completeness of the normal form are proved.

The issue is operational, not philosophical. I constructed an exact inverse-series presentation from the certified endpoint `wheel_W4__b8__leaf_offset0`, seed 47. One edge of capacity `c` was replaced by a boundary-free bivalent path with capacities `c` and `2c`. For terminal min-cuts, the serial path has effective cut capacity `min(c,2c)=c`; exact enumeration confirmed the same full fingerprint and unique minimizers. Applying the repository’s declared series reduction returns the original weighted graph exactly. Yet the expanded graph is absent from the endpoint’s allegedly saturated state set because the engine never proposes inverse series expansion.

The independent audit output is:

```text
fingerprint_equal=True
expanded_unique=True
series_reduces_back_exactly=True
expanded_in_forward_saturation=False
forward_state_count=5 saturated=True
PASS
```

Evidence: `prog3_inverse_series_audit.py` and `prog3_inverse_series_audit.log`.

This counterexample does **not** prove that a particular base/perturbed fiber pair is gauge-equivalent under some broader relation. It proves the narrower but decisive point that the Step-2 sets are not complete symmetric orbits under the generated move relation, so their disjointness cannot certify gauge inequivalence.

The aggregate transition census makes the wording still less defensible. Across all 38 endpoint runs, the first four classes have zero accepted transitions; all 100 accepted transitions and all 50 novel states are Delta–Y/Y–Delta. Thus the actual computation is Delta–Y/Y–Delta saturation of already reduced endpoints, not empirical exploration of five active move classes. Evidence: `prog3_transition_census_audit.py` and `.log`; compare `results_step2.md:11-29`.

The admission policy also requires every intermediate presentation to retain unique minimizers (`schema_step2.json:30-41`; `saturation_engine.py:167-190`). That is a legitimate restricted state space, but it must be named. A path through a degenerate presentation is outside the computed relation even if it preserves the terminal cut values.

**Finding P3-2: FAIL as written. Confidence 0.995.**

### Kalman–Krauthgamer is overapplied

The paper says the local repertoire is “provably complete at the star-mesh level” and uses Theorem 3.24 to argue that the five classes are not an arbitrary stopping point (`paper/source/06_predictions.md:44-46`; `open_programs/prog3_cut_fingerprints/CLOSURE.md:28-35`).

The cited theorem is narrower. Kalman and Krauthgamer define a local `k`-star-mesh transform as removal of a degree-`k` vertex and replacement by a clique whose new edge weights depend only on the incident star. Theorem 3.24 excludes such a **local star-to-clique rule** for `k>3` in the min-cut metric. Their discussion explicitly leaves context-dependent/nonlocal star-mesh transforms open (arXiv:2112.06916, Definitions 3.19–3.21, Theorem 3.24, Open Question 4.5).

It does not establish completeness of:

- the repository’s four other reductions;
- inverse expansions;
- context-dependent local replacements;
- nonlocal transformations;
- larger gadgets with retained nonterminals;
- compositions that pass through degenerate presentations; or
- arbitrary mimicking-network equivalences.

The citation can justify excluding a universal local degree-`k>3` star-to-clique rule. It cannot certify a complete gauge repertoire.

**Finding P3-3: incorrect application. Confidence 0.99.**

### Required replacement wording for PROG3

Use:

> On 13 fixed exact-rational graph topologies, 19 kernel directions yield nondegenerate positive-capacity intervals with identical complete terminal min-cut fingerprints and unique active minimizers. Selected endpoints have different weights and are not related by terminal-fixed weighted automorphism. A queue-exhaustive **forward** search under four reduction rules and bidirectional Delta–Y/Y–Delta finds no intersection between the endpoint reachability sets. No completeness or gauge-irreducibility claim is made for the equivalence generated by inverse, nonlocal, degenerate-intermediate, or undeclared transformations.

Do not use “irreducible carriers,” “complete orbit,” or “gauge=0” for the present Step-2 result.

---

## 1.2 PROG2: exact cut-and-state fibers

### The six exact joint-map fibers are real

Step 5 reconstructs each endpoint from the Step-4 algebraic certificate, not from a decimal approximation. It checks exact equality of the edge-capacity product and exact equality of the complete cut fingerprint (`step5_family_gauge_classification/step5_core.py:64-90`). The validator rebuilds all Step-5 artifacts in a temporary directory and byte-compares them (`run_step5.py:15-23`). My rerun passed all six rows.

The underlying `C2_L1` state equality is analytically transparent. The convention assigns edge coefficients

\[
 a_e=\sqrt{\frac{c_e}{1+c_e}},\qquad
 b_e=\frac{1}{\sqrt{1+c_e}}.
\]

The connected copy network has only two globally consistent internal assignments. Its unnormalized boundary state is therefore proportional to

\[
 \left(\prod_e a_e\right)|0\cdots0\rangle
 +
 \left(\prod_e b_e\right)|1\cdots1\rangle,
\]

so the normalized state depends on capacities only through

\[
 \frac{\prod_e a_e}{\prod_e b_e}=\sqrt{\prod_e c_e}.
\]

Thus equal product implies exactly equal normalized boundary state. Step 4 found six exact positive-algebraic intersections of the complete-cut fiber with an equal-product level set (`step4_finite_continuation/results_step4.md:3-5`). Step 5 rechecks them.

The strongest robust statement is:

> **The map from positive capacities to `(complete terminal cut function, normalized connected-copy C2_L1 boundary state)` is non-injective on six explicit fixed finite graphs, with exact positive-algebraic witnesses.**

This claim is independent of whether one calls the capacity assignments physically inequivalent.

**Finding P2-1: PASS. Confidence 0.995.**

### The declared invariant is valid under the declared relation

The Step-5 relation is explicitly split into cut equivalence, tensor-presentation gauge that does not act on capacity labels, and a very small canonical-family capacity relabeling group (`declaration_step5.md:5-22`). Under those literal generators,

\[
 I(c)=\left\{\sum_e c_e,\ \sum_e c_e^{-1}\right\}
\]

is invariant:

- weighted isomorphism permutes terms;
- internal `g,g^{-1}` and boundary unitaries are stipulated to leave capacity labels unchanged;
- global reciprocal exchanges the two entries;
- series/parallel generators are vacuous on the twelve endpoints.

The exact endpoint values differ for all six pairs. The invariant is therefore a valid separator **inside that declared relation** (`declaration_step5.md:46-68`; `step5_core.py:93-113,175-200`).

The implementation’s proof ledger is partly declarative: three rows have `passes=True` hardcoded because the capacity action is defined as identity (`step5_core.py:202-224`). That is acceptable as a direct mathematical proof record, but it is not an independent computational discovery.

**Finding P2-2: PASS relative to the literal relation. Confidence 0.99.**

### The gauge relation is too narrow to support “genuinely inequivalent” state examples

The central weakness is that Step 5 defines internal tensor gauge not to act on capacities (`declaration_step5.md:9-16`). That is a possible convention for a **decorated graph-plus-capacity object**, but it is not forced by the boundary state or by the tensor-network presentation.

For any connected graph in this copy family, let `c` and `c'` be positive assignments with equal products. Orient each stored edge from `u` to `v`, as the code does when dressing only `edge.u` (`step3_kernel_test/step3_core.py:162-178`). Define

\[
 b_v=\frac12\sum_{e:u(e)=v}\log\frac{c'_e}{c_e}.
\]

Equal total product gives `sum_v b_v=0`. On a connected graph, the oriented incidence matrix has image equal to the sum-zero vertex vectors, so there is an edge vector `x` with

\[
 Bx=b.
\]

Insert on each internal edge

\[
 G_e=\operatorname{diag}(e^{x_e},1),\qquad G_e^{-1}
\]

using the repository’s own internal gauge operation. At every vertex, this changes the local zero-versus-one copy-tensor amplitude ratio by exactly the factor required to convert the `c`-canonical tensor into the `c'`-canonical tensor. The transformed local tensor is proportional to the target local tensor; the product of local scalars only changes the unnormalized global state, not its projective normalized state.

I implemented this construction for all six exact pairs. Maximum numerical residuals are approximately `4.5e-16`, and all six pass. Evidence: `prog2_diagonal_gauge_audit.py` and `.log`.

This has a precise interpretation:

- If capacities are held as external ontic labels and gauge is defined never to relabel them, the pairs are inequivalent by definition and the Step-5 invariant separates them.
- If the object under comparison is the tensor-network presentation of the state, the pairs are connected by a natural internal diagonal gauge plus re-canonicalization; no state-level invariant distinguishes them.
- If the object is the joint observable map `(cuts,state)`, the noninjective fibers remain exact regardless of gauge terminology.

The Step-5 relation was also frozen only after the six candidates were already known. Step 4 had tried a broader generated relation and honestly reported every search budget-truncated, leaving all six as candidates (`step4_finite_continuation/results_step4.md:7-22,35-41`). Step 5 then replaced that unresolved relation with a narrower family relation and an invariant tailored to the permitted capacity actions (`declaration_step5.md:1-3`; `step5_core.py:25-35`). This does not invalidate the finite theorem, but it means “frozen before classification” is not independent preregistration of the gauge concept before candidate selection.

**Finding P2-3: the exact fibers survive; robust state/bulk inequivalence does not. Confidence 0.96.**

### Is excluding weighted Delta–Y legitimate?

The repository’s exact countercheck is useful. On `cand_01`, a particular cut-preserving Delta–Y move changes the copy product by the exact factor

\[
\frac{70406080269220304893479166685119}
{8728637932116993396730243442760}\neq1,
\]

so cut equivalence alone does not imply `C2_L1` state equivalence (`delta_y_countercheck_step5.csv`; `step5_core.py:162-173`). It is therefore legitimate to reject the blanket rule “every cut-preserving Delta–Y move is state gauge.”

It is not legitimate to infer that **no** weighted Delta–Y instance can belong to a state gauge. A special move could preserve the product or admit a tensor-level intertwiner. Admission should be instance-specific and based on the state/tensor map, not excluded by class name.

### Required replacement wording for PROG2

Use:

> In the connected binary-copy convention `C2_L1`, the normalized boundary state depends only on the edge-capacity product. Six exact positive-algebraic same-graph pairs were constructed with identical complete terminal cut functions and equal products, hence identical boundary states. They establish exact noninjectivity of the joint cut/state map. They are separated by `I(c)` only under a deliberately narrow capacity-label-preserving family relation; no physically complete bulk gauge relation or inequivalent tensor-presentation theorem is claimed.

Calling the finite algebraic subproblem “completed” is fair. Calling the original physically quotiented bulk-underdetermination program “resolved” is not.

---

## 1.3 Standard-Model branch selection

### What reproduces

The Version-3 validator rebuilds the representation carrier, scalar branches, pair branches, quotient counts, independent tensor-product gate, and golden checks in memory. My rerun produced:

```text
PASS: singleton=12 singleton_none=44 independent_gate=12/12 tensor=368
golden=14/14 pairs=2824 pair_structures=52 new_pair_structures=44
clean_pairs=68 clean_outside_typed_family=0 charge_orbits=419/195->24
```

The corresponding results report:

- 1,066 labelled genuinely chiral structures;
- 419 declared quotient orbits;
- 195 primitive-charge-normalized orbits;
- 52 chirality-faithful structures;
- 12 admissible singleton branches, 4 clean;
- 2,824 admissible two-scalar pair branches, 68 clean; and
- no clean branch outside the `2|3`/`SU(2)`-active typed family.

These are sound finite counts under the literal alphabet, charge set, field cap, per-scalar component cap, quotient convention, and branch grammar (`paper/source/04_result_sm.md:15-36,38-61`; `review_2026/repairs/s1_carrier_reconstruction/RESULTS_v3.md`).

My direct census of the exported branch tables finds four clean labelled `2|3` structures but one declared carrier orbit. The clean singleton rows form one branch orbit; the 68 clean pair rows form 17 pair-branch orbits. Evidence: `sm_clean_orbit_audit.py` and `.log`.

Thus “`2|3` is the unique structure” is ambiguous. The accurate statement is “one declared `2|3` carrier orbit/dimension family,” not one labelled structure.

**Finding SM-1: PASS within the declared grammar. Confidence 0.98.**

### Why this is not yet physical symmetry-breaking selection

The low-energy proxy is much thinner than the prose term “clean breaking” suggests.

For every admitted nontrivial canonical representation of `SU(N)`, the code assigns residual subgroup dimension `N-1` (`carrier_chain.py:550-555`). In the two-scalar extension it states explicitly that this is an inherited proxy, not a computed simultaneous stabilizer (`carrier_chain_v3.py:315-358`). Multi-VEV alignment is not modeled. The “broken vector exotic count” is then `2*residual`, and the defect count is

\[
\Delta_{\rm pair}=(\dim\mathfrak{su}(N_{\rm conf}))\times
(\text{broken-vector count}).
\]

Cleanliness is defined by the broken-vector count being zero, while `delta_empty` is the same condition multiplied by a positive confining-generator factor (`carrier_chain.py:558-627`). Line 621 explicitly checks the equivalence. The factorization-defect emptiness is therefore not an independent discriminator; it is a repackaging of the clean proxy.

The result is still a valid theorem of the finite grammar:

> Under the inherited `SU(N)->SU(N-1)` residual proxy and the declared capped scalar grammar, only the `2|3` carrier orbit has admissible branches whose scalar action avoids producing the proxy’s charged broken-vector count, and all such clean branches act only on the `SU(2)` factor.

It is not a calculation of the actual vacuum manifold, scalar potential, simultaneous stabilizer of multiple VEVs, mass spectrum, or dynamical vacuum selection.

**Finding SM-2: mathematically sound proxy classification, physically overframed. Confidence 0.97.**

---

## 1.4 `SU(5)` construction

The generator-construction validator passed. It checks the centralizer over all 24 traceless Hermitian directions, not merely a diagonal ansatz, obtaining rank 23, nullity one, and primitive direction `(-2,-2,-2,3,3)` (`review_2026/repairs/s3_generator_construction/RESULTS_v2.md:3-6`). It reconstructs the coset charges, the conditional lattice statement, the `3/8` trace ratio, the `5/3` normalization, the Pati–Salam control, and seven mutation checks.

The conclusions are correctly conditional:

- the hypercharge direction is unique inside the chosen regular `3+2` embedding;
- `3/8` and `5/3` follow after buying the `5bar+10` matter package and weak-pair normalization;
- Pati–Salam also gives `3/8`, so the ratio does not select `SU(5)`;
- no renormalization-group running or low-energy prediction is present; and
- the homotopy result assumes the stated global quotient and connectedness inputs.

This is exact and useful as a reproducible construction, but the underlying group theory is standard. The SBT contribution is the import ledger and correct landing grade, not a novel derivation of the Standard Model.

**Finding SM-3: PASS conditionally. Confidence 0.995.**

---

## 1.5 QM–GR finite LP result and Q5 validator

The exact graph-level LP result survives. The Q5 builder reports 254 nontrivial boundary regions, unique cuts, exact primal and dual feasibility, strong duality, complementary slackness, and 3,556 chamber-sensitivity checks (`review_2026/repairs/q5_lp_duality/RESULTS.md:1-5`). The corrected identity

\[
\operatorname{Area}(\mincut A)=\operatorname{OPT}_{\rm dual}(A)=\sum_e c_e y_e
\]

is correct for the constructed finite graph, with `y_e` the `0/1` edge-incidence shadow variables. This is an exact finite instance of standard max-flow/min-cut and LP sensitivity, not a continuum RT theorem.

However, the advertised command `run_q5.py --self` currently fails its byte comparison. It rebuilds the science in memory, then demands byte identity for every rendered artifact (`run_q5.py:26-37`). In this environment, `q5_linear_response.csv` and `q5_results.json` differ. The exact graph/LP files remain byte-identical, all exact semantic flags remain true, and the scientific verdicts remain unchanged. The maximum observed floating drift in the linear-response table is about `1.78e-10`; the `born_i3` drift is `4.44e-16`. Evidence: `q5.log`, `q5_semantic_audit.py`, and `.log`.

This is not a failure of the exact LP theorem. It is a failure of the repository’s blanket byte-reproducibility claim for floating artifacts. The validator should either pin the complete numerical stack and deterministic contraction backend, or serialize numerical evidence with an explicit canonical rounding/tolerance policy while retaining byte checks for exact artifacts.

**Finding Q5-1: exact LP claim PASS, confidence 0.99.**  
**Finding Q5-2: advertised byte validator FAIL in the reviewed environment, confidence 1.00.**

---

# 2. Is the scoping honest?

## 2.1 What the paper does well

The paper is substantially more candid than the original framing. It repeatedly distinguishes finite construction from nature-level derivation, recognition from selection, conditional channels from derived dynamics, and toy graph results from bulk geometry. The abstract explicitly denies frame transfer and universality (`paper/source/00_title_abstract.md:8-34`); the introduction says a shared vocabulary is not a solution (`01_introduction.md:3-9`); the Standard-Model section names the denominators and imports (`04_result_sm.md:15-36,71-88`); and the record-stability section withdraws its grounding claim (`04_result_sm.md:90-104`).

Those qualifications are substantive, not cosmetic.

## 2.2 Where the remaining wording is still too strong

### “Complete five-class orbits”

This is the most serious remaining overclaim. It appears in the abstract (`00_title_abstract.md:25-30`), predictions (`06_predictions.md:44-54`), discussion (`10_discussion.md:18-22`), repository README (`README.md:140-145`), and PROG3 closure (`CLOSURE.md:7-17`). The code supports complete directed forward closure, not complete orbit closure.

### “The first program is resolved”

The original PROG2 question asks about physically quotiented bulk geometry (`open_programs/prog2_state_underdetermination/CLOSURE.md:3-12`). The appended final result leaves broader physical gauge and bulk interpretation open. The exact finite joint-map construction is completed; the physical program is not. Put the final status at the top and move the historical negative/positive sequence below it.

### “Six underdetermination examples”

“Underdetermination of the declared joint map” is accurate. “State-level inequivalence,” “bulk underdetermination,” or an unqualified “genuinely inequivalent” is not. The diagonal-gauge construction shows why the noun matters.

### “`2|3` is the unique structure”

There are four clean labelled structures and one declared carrier orbit. The abstract should say “the unique declared carrier orbit/dimension family admitting clean branches.” It should also name the residual-subgroup proxy rather than letting “clean breaking” sound like a physical Higgs analysis.

### “The calculus is not dynamical”

The discussion says SBT “is not dynamical” and has only a finite structural evidential role (`paper/source/10_discussion.md:33-38`). The introduction similarly calls it a fixed catalog describing one finite carrier (`01_introduction.md:11-12`). That is incorrect relative to the supplied corpus, which contains explicit strict-theory-extension, endogenous-repair, and dynamical-law programs. The paper is entitled to use only a static finite subset, but it must not identify that subset with SBT as a whole.

Replace with:

> This paper instantiates only SBT’s finite obstruction, quotient, and claim-governance subset. It does not instantiate SBT’s strict-extension, promotion, endogenous-repair, or run-level dynamical machinery, and it supplies no substrate-specific Lagrangian or continuum bridge.

### The title

“To Kill Three Stones” strongly suggests that the SM, QM, and GR problems were solved or jointly forced. The body explicitly denies that. The mismatch is too large for qualifiers to repair.

Suggested titles:

1. **Theory Repair with Six Birds: Audited Finite Constructions for SM and QM–GR Models**
2. **A Common Emergence-Engineering Grammar for Finite SM and QM–GR Constructions**
3. **Six Birds Under Load: Exact Finite Constructions and Failed Forcing Claims in SM/QM/GR Toys**

The second preserves the positive framework claim most directly.

## 2.3 What is understated

The graph-level exact result is stronger than the paper’s pair language. It has nondegenerate exact intervals, not just 19 isolated endpoint coincidences. That deserves theorem-level emphasis.

The verification campaign also has a stronger SBT-relevant interpretation than “audit.” It is a bounded example of theory engineering at the level of a research program: failed typed claims generated successor construction tasks, and those tasks produced replacement theorem objects or explicit no-go boundaries. This should be stated, while making clear that no new physical layer was promoted.

---

# 3. Is the verification methodology trustworthy?

## 3.1 Rerun record

| Validator | My result | Interpretation |
|---|---|---|
| `open_programs/prog3_cut_fingerprints/step2_orbit_saturation/run_step2.py --self` | PASS | Real temporary rebuild and exact semantic checks; conceptual orbit label still wrong |
| `open_programs/prog2_state_underdetermination/step5_family_gauge_classification/run_step5.py --self` | PASS | Exact six-pair reconstruction under the frozen relation |
| `review_2026/repairs/s1_carrier_reconstruction/run_s1_carrier_reconstruction_v3.py --self` | PASS | Rebuilds finite carrier/branches and independent gates |
| `review_2026/repairs/s3_generator_construction/run_s3_generator_construction_v2.py --self` | PASS | Exact full-centralizer and mutation checks |
| `review_2026/repairs/q5_lp_duality/run_q5.py --self` | **FAIL** | Two floating artifacts not byte-identical; exact semantics stable |

I did not complete every historical validator. In particular, full PROG3 Step 1 and PROG2 Step 4 reruns exceeded the review’s practical runtime window. I inspected their source and final exported artifacts, and the later validators reconstructed the load-bearing Step-2/Step-5 objects, but this review is not a claim of an exhaustive repository-wide rerun.

## 3.2 Strengths

The modern repair packets are materially better than superficial “read the summary and compare a verdict” validators:

- PROG3 Step 2 and PROG2 Step 5 rebuild into temporary directories and byte-compare outputs.
- PROG3 re-enumerates exact terminal cuts before admitting each state.
- PROG2 reconstructs algebraic endpoints and verifies exact products and cut functions.
- S1 has an independent representation/tensor-product gate and known golden values.
- S3 searches the full 24-dimensional centralizer and includes mutation tests.
- Q5 separates exact LP certificates from failed linear-response and composition claims.

The campaign’s own findings register also catches real infrastructure and assurance defects (`review_2026/FINDINGS.md:5-18`). The root README and adversarial-review appendix acknowledge that the repository is not uniformly self-verifying and that a campaign freeze is a consistency gate rather than tamper-evident evidence (`README.md:133-154`; `paper/source/appendix_D_adversarial_review.md:49-73`).

## 3.3 Missed failure modes

### Validators can faithfully certify the wrong theorem object

PROG3 is the clearest example. The rebuild is real and exact, but the validator treats the engine’s directed-reachability label as the theorem to be confirmed. No test asks whether the rules generate a symmetric relation or whether inverse moves are represented. Exact implementation correctness does not cure an incorrectly typed claim.

### Positive verdicts are encoded as required outputs

PROG2 Step 5 hardcodes the six candidate specifications, raises an exception unless all six receive `example_earned=True`, and makes its validator require the exact final classification (`step5_core.py:226-240`; `run_step5.py:41-55`). This is a regression test, not an independent discovery test. It is useful after the theorem has been proved, but it should not be presented as separate evidence that the chosen relation was natural.

### The gauge relation was narrowed after candidate discovery

Step 4 honestly failed to saturate a broader generated relation and retained candidates. Step 5 then declared a smaller relation and an invariant after those candidates were known. Again, the finite conditional theorem is valid, but the process is vulnerable to relation selection that pattern-matches the desired survival.

### Proof ledgers mix derived and stipulated checks

The invariant ledger sets `passes=True` for generators whose capacity action is stipulated to be identity (`step5_core.py:211-217`). The statement is mathematically correct, but a machine-readable proof ledger should distinguish `PROVED_BY_DEFINITION`, `COMPUTED`, and `EXTERNALLY_CHECKED` rather than flattening all to `True`.

### Floating reproducibility is oversold

Q5 shows that exact byte comparison and floating tensor contraction should not be governed by one undifferentiated policy. The exact artifacts are stable; numerical last digits are not.

### The closure documents are not clean final authorities

PROG2’s `CLOSURE.md` retains the earlier negative checkpoint and appends a later positive result. A reader can reasonably be unsure which scope is final. The claims map is described as the final Version-2 authority, while Version-3 closures were added later. A single machine-readable Version-3 claim registry should supersede the layered historical documents.

### The SM “defect” lacks independent content

Because the clean flag and defect emptiness are both constructed from the same broken-vector proxy, a validator confirming their equivalence does not provide an independent obstruction test. This should be described as a definitional normal form rather than two convergent diagnostics.

## 3.4 Methodology upgrades required

1. **Separate theorem schemas from expected verdicts.** A validator should recompute premises and output whichever verdict follows, while a release test may separately flag that the manuscript wording needs updating.
2. **Define relations mathematically before search.** State whether moves are directed rewrites, symmetric generators, or a canonicalization system. For gauge claims, include inverses or prove confluence/normal-form completeness.
3. **Adversarially enumerate natural gauge enlargements before freezing a separator.** For PROG2, include continuous diagonal internal gauges and re-canonicalization.
4. **Promote analytic reductions over numerical tables.** The `C2_L1` product theorem and diagonal-gauge theorem should replace much of the dense state-comparison machinery for this family.
5. **Split exact and floating artifact policies.** Byte-compare exact rational/algebraic outputs; use pinned environment plus canonical rounding or semantic tolerances for numerical contractions.
6. **Use a single Version-3 claims authority.** Historical packets should be provenance, not competing current status documents.
7. **Mark evidence type per row.** Use labels such as `EXACT_PROOF`, `EXACT_COMPUTATION`, `NUMERICAL_EVIDENCE`, `DEFINITIONAL`, `REGRESSION_EXPECTATION`, and `OPEN`.

**Overall methodology verdict:** trustworthy for reproducibility of several declared finite computations; not sufficient by itself for semantic completeness, naturalness of equivalence relations, or physical interpretation. Confidence 0.97.

---

# 4. What is the actual contribution?

## 4.1 Genuine, checkable mathematical/computational results

### A. Exact complete-cut-map fibers

This is the strongest standalone result. The repository exhibits exact local noninjectivity of the full terminal min-cut map on 13 fixed topologies, including nondegenerate rational intervals and unique-minimizer chambers. It is independent of SBT and could support a concise graph-theory/data note after the incorrect orbit claim is removed.

A worthwhile standalone paper would ask:

- how active-cut incidence rank controls local identifiability;
- when such fibers exist generically;
- whether a canonical quotient or complete invariant can be constructed;
- how the examples relate to mimicking networks and terminal-cut realizability.

I did not establish literature priority, so novelty should be stated as “explicit examples and a reproducible census” unless a more complete literature review is performed.

### B. Exact intersections of cut fibers and copy-state product fibers

The six algebraic examples are genuine fibers of a joint map. The more general contribution is the analytic `C2_L1` theorem: on a connected copy network, the normalized boundary state depends only on the edge product. The diagonal-gauge analysis shows this family is more degenerate than the current paper recognizes. This could be a short technical note about identifiability and gauge in capacity-dressed copy networks, but not a bulk-geometry result.

### C. Finite carrier and branch census

The corrected chiral carrier, quotient bookkeeping, and exhaustive capped scalar-branch census are reproducible. As a standalone contribution, this is a finite classification/methods result, not Standard-Model derivation. Its significance depends on a stronger physical rationale for the alphabet, caps, scalar potential, and residual-subgroup calculation.

### D. Exact finite LP certificate

The 254-region primal-dual export is a useful reproducibility artifact and a correct finite recognition of standard max-flow/min-cut duality. It is not a new theorem in optimization or holography.

### E. Exact `SU(5)` reconstruction

Correct and useful as an audited construction; not new mathematics or a parent-selection result.

## 4.2 Reasonable physics-flavored toys

- the Boolean QM/GR access fork;
- finite graph min-cut versus contracted tensor entropy comparisons;
- the connected-copy capacity convention;
- the perfect-record LOCC channel conditional;
- the capped branch-cleanliness proxy; and
- finite monogamy/control examples.

These are acceptable as toys when their bridge assumptions are explicit. They do not presently constitute a theory of the SM, quantum gravity, or physical record formation.

## 4.3 Still overclaimed

- complete PROG3 gauge orbits;
- physical or robust tensor-gauge inequivalence of the six PROG2 pairs;
- resolution of the original bulk-underdetermination program;
- “unique structure” without orbit/proxy qualification;
- Standard-Model “selection” without foregrounding that the clean condition is an inherited residual proxy;
- any suggestion that `3/8` or `5/3` selects `SU(5)`;
- the title’s implication that three foundational problems have been solved; and
- the characterization of SBT as intrinsically fixed and non-dynamical.

---

# 5. The strongest valid SBT-based claim

The paper should not retreat to saying merely that SBT was an audit vocabulary. That would miss the framework’s constructive purpose. The campaign did use typed failures to generate successor tasks:

- the alias/quotient failure generated a new carrier;
- the structure-versus-branch failure generated branch-complete enumeration;
- the route-mismatch failure generated an exact commuting recheck and retraction;
- the P1 gauge ambiguity generated exact finite cut-fiber construction;
- the state-level split generated a new convention family and exact equal-product continuation search;
- record-token failure generated a dynamical-invariant-algebra proposal.

That is recognizably an engineering loop. But the object being engineered is the **paper’s theorem package and research program**, not a promoted physical layer. The work does not construct a successor SM/QM/GR theory, prove strict physical non-definability, establish reclosure under native dynamics, or pass an empirical bridge/promotion gate.

The strongest valid framework claim is:

> **Across two finite physics-inspired model families, SBT supplied a reusable theory-repair workflow: typed obstructions were converted into reconstructed carriers, exact replacement constructions, countermodels, and explicit successor design requirements. This is an `n=2` methodological portability result and a reflexive theory-engineering case study, not a physical unification theorem or a promoted next theory of the SM, QM, or GR.**

This formulation is stronger and more faithful to SBT than “a finite audit grammar,” while remaining supported by what the repository actually does.

---

# 6. Publication recommendation and mandatory revisions

## Recommendation: major revision

The paper should not be accepted in its present Version-3 form because two central closure statements are materially wrong or misleading. The underlying repository is worth repairing rather than discarding.

## Mandatory before resubmission

1. **Withdraw “complete five-move orbit” and “gauge=0.”** Recast Step 2 as directed forward saturation. Either add inverse generators and prove exhaustive symmetric closure, or prove confluence/canonical normal forms before restoring an equivalence claim.
2. **Recast PROG2 as joint-map noninjectivity.** Add the analytic `C2_L1` product formula and disclose the diagonal internal-gauge/re-canonicalization construction. Do not call the pairs robustly state-gauge or bulk inequivalent.
3. **Change the title.** Retain “common grammar” or “theory repair,” not “kill three stones.”
4. **Correct the SBT description.** Say that this paper uses only a static finite subset; do not say SBT itself is non-dynamical or only a fixed catalog.
5. **Fix Q5 reproducibility.** Separate exact byte checks from floating semantic checks and document the numerical environment.
6. **Replace “program resolved.”** Say the exact finite algebraic subproblem is completed while physical gauge/bulk interpretation remains open.
7. **Fix the SM quantifier.** Replace “unique structure” with “unique declared carrier orbit/dimension family” and foreground the residual `SU(N-1)` proxy.
8. **Consolidate Version-3 authority.** Put current claims in one registry; retain older closure stages only as history.

## Strongly recommended

9. State theorem objects in mathematical form before giving SBT landing grades.
10. Separate exact theorem, model convention, physical bridge, and nonclaim in every headline result.
11. Turn the min-cut fibers into a standalone graph-theory note or a clearly demarcated theorem section.
12. Present the verification campaign as an SBT theory-repair case study, including where the engineering loop stops before physical promotion.

---

# 7. Proposed replacement abstract-level claims

The following is close to the maximum defensible strength:

> We report a post-publication SBT-guided theory-repair campaign on two finite physics-inspired construction programs. On the Standard-Model track, a conjugation-consistent capped carrier and exhaustive singleton/two-scalar branch census show that one declared `2|3` carrier orbit—and only that orbit—admits clean branches under an inherited `SU(N)->SU(N-1)` residual proxy; this is a finite branch-classification result, not a physical vacuum-selection theorem. Given the regular `SU(5)` embedding, the `5bar+10` matter package, and a weak-pair convention, exact generators recover the standard one-dimensional hypercharge direction, `sin^2 theta_W=3/8`, and `k_Y=5/3`.
>
> On the graph track, 13 fixed exact-rational weighted topologies exhibit 19 nondegenerate local fibers of the complete terminal min-cut map: capacities vary over exact intervals while all terminal cut values and unique active minimizers remain unchanged. A directed forward saturation under four reductions and Delta–Y/Y–Delta finds no intersection between selected endpoint reachability sets, but no complete gauge-orbit claim is made. In the connected binary-copy convention, the normalized boundary state depends only on the product of edge capacities; six exact positive-algebraic same-graph pairs share both the complete cut function and the boundary state. These establish noninjectivity of the declared joint map, not inequivalent bulk geometries.
>
> The common result is methodological: across two finite substrates, SBT converted typed failures into repaired carriers, exact replacement constructions, and explicit open design requirements. No nature-level Standard-Model selection, quantum-gravity solution, physical unification, or promoted successor theory is claimed.

---

# 8. Evidence produced in this review

The external evidence bundle contains:

- `prog3_step2.log` — official final PROG3 validator rerun;
- `prog2_step5.log` — official final PROG2 validator rerun;
- `s1_v3.log` — official Standard-Model carrier/branch validator rerun;
- `s3_v2.log` — official `SU(5)` validator rerun;
- `q5.log` — official Q5 validator failure;
- `q5_semantic_audit.py/.log` — exact-versus-floating mismatch classification;
- `prog3_inverse_series_audit.py/.log` — explicit omitted inverse-series state;
- `prog3_transition_census_audit.py/.log` — aggregate directed-transition census;
- `prog2_diagonal_gauge_audit.py/.log` — diagonal internal-gauge construction for all six pairs; and
- `sm_clean_orbit_audit.py/.log` — clean labelled-structure/orbit counts.

## Review limitations

- I did not rerun every historical construction or every validator in the repository.
- I did not establish priority or novelty against the entire graph-theory or tensor-network literature.
- The PROG3 inverse-series witness refutes the completeness of the claimed symmetric orbit, but does not prove any selected fiber endpoints equivalent under a broader relation.
- The PROG2 diagonal-gauge conclusion treats projectively proportional local tensors and arbitrary invertible internal diagonal gauges as presentation equivalence. If capacities are declared independent ontic labels, the pairs remain different decorated objects by definition; that is why the robust result is joint-map noninjectivity rather than physical inequivalence.
- Physics interpretations beyond the declared finite models were assessed for logical support, not tested experimentally.

---

## Final assessment

There is publishable material here after substantial repair. The exact cut-function fibers are the clearest independent mathematical contribution. The connected-copy result is exact but reveals a highly degenerate state family and, under a natural tensor gauge, weakens rather than strengthens a bulk-underdetermination interpretation. The SM branch census is a legitimate finite proxy classification, and the `SU(5)` and LP sections are exact audited reconstructions of standard mathematics.

The paper’s most credible unifying contribution is an SBT-guided theory-engineering narrative: the framework helped turn failed claims into better theorem objects and better-posed next constructions. That is meaningful. It does not justify the present title, complete-orbit language, or physical underdetermination language.
