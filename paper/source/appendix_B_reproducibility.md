# Constructions and reproducibility

The historical construction tracks live under `physics_atlas/`; the controlling repairs and probes live under
`review_2026/`; the construction programs live under `open_programs/`. Where a historical headline
and a controlling repair disagree, the repair and the claims registry `review_2026/CLAIMS_REGISTRY.md`
control. Validators vary in strength: many historical scripts check deterministic artifacts, while the strongest
rebuild their entire result in memory and compare every output byte for byte.

## Entry points for the controlling results

| result | artifact directory | validator (`–self`) |
| --- | --- | --- |
| gauge carrier, branch census, scalar pairs | `review_2026/repairs/s1_carrier_reconstruction/` | `run_s1_carrier_reconstruction_v3.py` |
| $SU(5)$ generators, ratios, coset, F27/F48 | `review_2026/repairs/s3_generator_construction/` | `run_s3_generator_construction_v2.py` |
| content quotient, mass rank, $N$-copy probe | `review_2026/repairs/s4_content_quotient/` | `run_s4.py` |
| F24/F47 architecture and surface | `review_2026/repairs/s5_f24_f47/` | `run_s5.py` |
| record-token census and ablations | `review_2026/repairs/s6_record_grammar_ablation/` | `run_s6_record_grammar_ablation_v3.py` |
| field provenance and partition lattice | `review_2026/repairs/q1_access_provenance/` | `run_q1.py` |
| route-mismatch commutation | `review_2026/repairs/q2_route_mismatch/` | `run_q2.py` |
| min-cut LP duality, response, composition | `review_2026/repairs/q5_lp_duality/` | `run_q5.py` |
| adaptive F50 convergence and stability | `review_2026/repairs/q7_f50_convergence/` | `run_q7.py` |
| F34 factorization theorem, rank certificates, partial-readout witness | `review_2026/repairs/f34_exact_factorization/` | `run_exact_factorization.py` |
| five-class P1 quotient search | `review_2026/probes/p1_kernel_quotient/` | `run_active_cut_quotient_v3.py` |
| P1 graph level: forward reachability | `open_programs/prog3_cut_fingerprints/step2_orbit_saturation/` | `run_step2.py` |
| P1 graph level: symmetric-closure obstruction | `open_programs/prog3_cut_fingerprints/step3_symmetric_closure/` | `run_step3.py` |
| P1 state level: finite `C2_L1` classification | `open_programs/prog2_state_underdetermination/step5_family_gauge_classification/` | `run_step5.py` |
| P1 state level: gauge-collapse lemma | `open_programs/prog2_state_underdetermination/step6_exact_gauge_collapse/` | `run_step6.py` |

Each directory contains its design choices, literal dependency pins, schema, result tables, and a findings note; the
caps and conventions stated in the body are also machine-readable there. The F34 directory additionally contains the
written proof of Theorem 7.1 (`PROOF.txt`). The proof is general linear algebra; the Python code
checks exact finite instances and is not a Lean mechanization of the universal statement.

## Independent checks

The mathematics review in `review_2026/mathematics_audit_20261003/` adds checks that do not reuse
production code: the weight-character representation oracle of Section 3.1, tampering
controls for the strengthened validators, regressions of the gauge-collapse certificate on every connected labelled
simple graph with at most four vertices, and a per-claim coverage file for all $42$ registry records. They are
reproduced by
```
python3 review_2026/mathematics_audit_20261003/run_checks.py \
    --output /tmp/sm-qm-gr-audit.json
```
Adding `–all` also sweeps the controlling and historical validators. The runner works in separate scratch
copies built from tracked, non-ignored files, so a missing local artifact cannot silently supply evidence.

## Historical track rebuilds and an external corpus variable

Step validators in a clean checkout resolve repository-internal sources relative to their own files. The usual
pattern is
```
cd physics_atlas/thread_<track>/steps/<step_dir>
python3 run_stepNN.py --self
```
Four historical QM–GR build drivers (steps 51–54) also reproduce hashes of Foundations III/IV corpus `.tex`
files that are not distributed here. Rebuilding those rows requires an explicit external root,
```
SIX_BIRDS_PAPERS_ROOT=/path/to/six-birds-papers \
  python3 <step51--54-build-driver>.py
```
Without it, those drivers stop before writing partial artifacts and name the missing file. The variable is not needed
to validate the released artifacts or to run repairs that only import compute functions; it is a provenance
dependency, not evidence that this checkout contains the external corpus.

## Validator caveats

The repository is not uniformly self-verifying, and it is not a tamper-evident freeze.

- **Summary-reading validators.** The validators of the historical multi-factor window-closure steps
   (steps 43 and 44 of the SM cluster) and some analogues check stored audit tables instead of rebuilding every
   load-bearing computation. The step-43 numerical census counts are also stale relative to the final carrier: a
   current-engine probe supports its $N\le6$ family conclusion, but a final-carrier rebuild remains to be done. By
   contrast, the step-61 validator (single-factor theorem) rebuilds every released non-code artifact in a temporary directory,
   compares bytes, and constructs the actual witness pairs.
- **In-place regeneration.** Some `--self` validators regenerate artifacts in place, so they are not
   idempotent checks of a release tree. A race in a parallel pool was observed once. Run sweeps in isolated scratch
   copies.
- **Pins.** The historical step-69 score source is pinned by a literal reviewed digest, so changing the
   source fails even if the stored conclusion is left unchanged. That step's record implication is superseded by the
   record census of Section 6.3. The preregistration `SHA256SUMS` primer entry
   names a file absent from the release, and the freeze gate is a consistency check, not a cryptographic or externally
   timestamped freeze.
- **Tracked inputs only.** The QM--GR step-27 and step-28 validators reconstruct their operators and histories
   from tracked inputs (step 28 checks every stored history state and potential), and the evidence log required by the
   P1 state-level step-6 validator is tracked. The compatible-clock constraints of steps 27–28 are finite
   constructions whose compatibility is engineered, not a derived clock dynamics.
- **P1 search scope.** The initial P1 probe used a declared three-round $\Delta$--Y/Y--$\Delta$ search. The
   controlling validator rebuilds nineteen exact fibers and exhausts their forward reachability under four directed
   reductions and bidirectional $\Delta$–Y/Y–$\Delta$, up to terminal-label-fixed exact weighted isomorphism.
   Symmetric-closure orbit disjointness, paths through tied-minimizer presentations, and other transformations remain
   open.

The Q5 replay policy separates exact discrete artifacts, which are compared byte for byte, from floating-point
summaries, whose numeric fields use tight declared tolerances while all non-numeric structure stays exact
(`review_2026/repairs/q5_lp_duality/reproducibility_policy.md`). The registry records, for every claim, its
wording, status, evidence type, supersession history, controlling source, and validator.

## Paper build

The modular manuscript builds with `make paper-build`, which compiles `paper/main.tex` and writes
`paper/build/main_flat.tex`; the tracked root `.tex` file is copied from that flattened output. All
figures are drawn in TikZ inside the source, so the flattened file needs no external image files. The Qeios bundle is
regenerated from the same sources.
