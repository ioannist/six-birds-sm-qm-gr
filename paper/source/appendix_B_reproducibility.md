# Constructions and reproducibility

The historical construction tracks live under `physics_atlas/`; the post-publication repairs and probes live
under `review_2026/`. The repaired results, not superseded historical headline rows, control Version 2.
Validators are heterogeneous: many historical scripts check deterministic artifacts, while the strongest repair
validators rebuild their entire result in memory and byte-compare every output.

## Certified repair and probe entry points

| Version-2 result | artifact directory | validator |
| --- | --- | --- |
| gauge carrier, branch census, scalar pairs | `review_2026/repairs/s1_carrier_reconstruction/` | `run_s1_carrier_reconstruction_v3.py –self` |
| $SU(5)$ generators, ratios, coset, F27/F48 | `review_2026/repairs/s3_generator_construction/` | `run_s3_generator_construction_v2.py –self` |
| content quotient, mass rank, $N$-copy probe | `review_2026/repairs/s4_content_quotient/` | `run_s4.py –self` |
| F24/F47 architecture and surface | `review_2026/repairs/s5_f24_f47/` | `run_s5.py –self` |
| record-token ablations | `review_2026/repairs/s6_record_grammar_ablation/` | `run_s6_record_grammar_ablation_v3.py –self` |
| field-to-mode provenance and partition lattice | `review_2026/repairs/q1_access_provenance/` | `run_q1.py –self` |
| route-mismatch correction | `review_2026/repairs/q2_route_mismatch/` | `run_q2.py –self` |
| min-cut LP duality, response, composition | `review_2026/repairs/q5_lp_duality/` | `run_q5.py –self` |
| adaptive F50 convergence and stability | `review_2026/repairs/q7_f50_convergence/` | `run_q7.py –self` |
| five-class P1 quotient search | `review_2026/probes/p1_kernel_quotient/` | `run_active_cut_quotient_v3.py –self` |

Each directory contains its design choices, literal dependency pins, schema, result tables, and findings note. The exact
caps and conventions stated in the body are also machine-readable there.

## Historical track rebuilds and the external corpus variable

Step validators in a clean checkout resolve repository-internal sources relative to their own files. Four historical
QM–GR build drivers—steps 51 through 54—also reproduce hashes of Foundations III/IV corpus `.tex` files that
are not distributed in this repository. Rebuilding those corpus-dependent rows therefore requires an explicit external
root:

```
SIX_BIRDS_PAPERS_ROOT=/path/to/six-birds-papers \
  python3 <step51--54-build-driver>.py
```

Without `SIX_BIRDS_PAPERS_ROOT`, those drivers fail before writing partial artifacts and name the missing file.
This variable is not needed to validate the published artifacts or to run repairs that import compute functions only.
It is a provenance dependency, not evidence that this checkout contains the external corpus.

The usual historical validator pattern is:

```
cd physics_atlas/thread_<track>/steps/<step_dir>
python3 run_stepNN.py --self
```

Because some validators regenerate in place, full historical sweeps should be performed on a scratch copy rather than
the release working tree.

## Support-integrity caveats

The repository must not be described as uniformly self-verifying or as a tamper-evident freeze.

- **F-002, mitigated:** the historical step69 data pin was computed from the same file it purported to pin.
   A byte-identical rebuild was demonstrated, but the pin remains to be made literal.
- **F-003:** some `--self` validators regenerate artifacts in place and are non-idempotent as checks of a
   release tree. A parallel-pool race was observed once (N-003). Use isolated scratch copies for sweeps.
- **F-008:** steps 43, 44, and 61 and analogues validate stored audit tables instead of rebuilding all
   load-bearing computations. Step61's mathematical result survives separate review, but its audit gates include literal
   booleans.
- The preregistration `SHA256SUMS` primer entry names a file absent from the release. The freeze gate is a
   consistency validator, not a cryptographic or externally timestamped tamper-evident freeze.
- P1 v3 does rebuild in memory and byte-compare its tables. Its residual statement is nevertheless relative to five
   named exact reductions and a three-round $\Delta$–Y/Y–$\Delta$ presentation search, not all possible quotients.

## Paper build

The modular manuscript builds with `make paper-build`. That target compiles `paper/main.tex` and creates
`paper/build/main_flat.tex`; the tracked root TeX file is copied from that flattened output for release.
The Qeios bundle is a separate submission surface regenerated from the Version-2 sources; its manuscript and notes must remain synchronized with the modular paper.
