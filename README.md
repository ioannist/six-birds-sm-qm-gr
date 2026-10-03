# Six Birds SM, QM, and GR

This repository contains the public support surface for the paper:

> **To Kill Three Stones with Six Birds: A Common Grammar for the SM, QM, and GR**
>
> DOI (Version 3): [10.5281/zenodo.23120510](https://doi.org/10.5281/zenodo.23120510)
>
> All versions: [10.5281/zenodo.20713211](https://doi.org/10.5281/zenodo.20713211)
>
> Current version: Version 3 (3 October 2026); Version 1: 17 June 2026.

The paper applies the Six Birds emergence calculus to two finite physics tracks:
Standard Model structural selection and the QM-GR interface. It provides
conditional finite constructions and two toy theorems on declared carriers, and
states three sharply typed construction programs rather than forcing
predictions. For each of nineteen exact
same-graph fibers on the thirteen residual min-cut carriers, queue-exhaustive
forward search under four directed reductions and bidirectional Delta-Y/Y-Delta
finds the two endpoint reachability sets disjoint; symmetric-closure orbit
disjointness remains open. Six exact connected `C2_L1` pairs are noninjective
fibers of the joint complete-cut/state map, but all collapse under the constructed
exact diagonal internal-bond gauge. The resulting general lemma says that, on any
fixed connected binary-copy carrier, positive equal-product capacity assignments
are gauge-related up to vertex-wise scalars. No bulk-geometry theorem is claimed.
The other two programs -- dynamical gravitational record formation, and
persistence in the scalar-dressed record algebra -- remain open. No foundational
grade, universality, or frame-transfer claim is made.

## What this repository provides

- Modular LaTeX paper sources under `paper/`, with section files,
  appendices, figures, bibliography, and submission audit notes.
- A tracked flattened manuscript source at the repository root:
  `Tsiokos_2026_To_Kill_Three_Stones_with_Six_Birds_A_Common_Grammar_for_the_SM_QM_and_GR.tex`.
- Mirrored Markdown source under `paper/source/` for review and editing.
- Physics-track construction artifacts and validator outputs under
  `physics_atlas/`.
- The authoritative claims registry and machine-verifiable repairs/probes under
  `review_2026/`, including the external technical review at
  `review_2026/EXTERNAL_TECHNICAL_REVIEW.md`, plus the closure records under
  `open_programs/`.
- Historical re-derivation pointers under
  `physics_atlas/INDEPENDENT_REDERIVATIONS.md`; superseded headline claims there
  do not override the current authoritative claims registry at
  `review_2026/CLAIMS_REGISTRY.md`. `review_2026/CLAIMS_MAP.md` records the
  claim-by-claim disposition against the first version of the paper.
- The mathematics and mechanization review of all 42 registry records, with its
  independent checks and repairs, under `review_2026/mathematics_audit_20261003/`
  (reproduce with `run_checks.py`); the general F34 factorization proof and exact
  certificates are under `review_2026/repairs/f34_exact_factorization/`.
- Retrodiction and unification card atlases under `retrodiction_atlas/` and
  `unification_atlas/`.

Local process logs, build outputs, caches, and large working products are
ignored locally and are not part of this public support surface.

## Build

Build the modular paper PDF:

```bash
cd paper
latexmk -g -pdf -interaction=nonstopmode -halt-on-error main.tex
```

The build writes:

- `paper/build/main.pdf`
- `paper/build/main_flat.tex`

The root flattened TeX file is the tracked release copy of
`paper/build/main_flat.tex`.

A top-level `Makefile` wraps the same build:

```bash
make paper-build        # compile + flatten (paper/build/main.pdf, main_flat.tex)
make paper-clean        # remove build outputs
```

### Qeios single-file bundle

To produce the Qeios submission assets under `paper/build/qeios_single/`:

```bash
make paper-qeios        # or: ./scripts/build_qeios_assets.sh
make paper-qeios-clean  # remove the qeios_single/ outputs
```

This writes:

- `qeios_single.tex` — single-file source (macros inlined, bibliography
  embedded via `.bbl`, an `orcidlink` fallback, and the self-assigned Zenodo
  DOI removed so Qeios mints its own).
- `qeios_single.pdf` — pre-built PDF.
- `figures/` — any raster figures (the current figures are TikZ and are inlined
  into `qeios_single.tex`, so this directory is normally empty).
- `qeios_source_bundle.zip` — upload/archive bundle (single-file deliverables
  plus the full modular source and figures).
- `Qeios_Submission_Notes.md` — copy/paste submission metadata.
- `README_BUILD.txt` — build instructions for the bundle.

The submission-notes and README templates live under `scripts/templates/`.

## Certified Re-Derivation Checks

The principal validator entry points are:

```bash
cd review_2026/repairs/s1_carrier_reconstruction
python3 run_s1_carrier_reconstruction_v3.py --self

cd ../../probes/p1_kernel_quotient
python3 run_active_cut_quotient_v3.py --self

cd ../../repairs/q5_lp_duality
python3 run_q5.py --self

cd ../../../open_programs/prog3_cut_fingerprints/step2_orbit_saturation
python3 run_step2.py --self

cd ../step3_symmetric_closure
python3 run_step3.py --self

cd ../../prog2_state_underdetermination/step6_exact_gauge_collapse
python3 run_step6.py --self
```

See `review_2026/CLAIMS_REGISTRY.md` for the current authoritative claim
dispositions, controlling sources, and validators; `review_2026/CLAIMS_MAP.md`
records the disposition of each claim carried over from the first version.

## Repository Layout

- `paper/main.tex` - LaTeX entry point.
- `paper/sections/` and `paper/appendices/` - modular manuscript source.
- `paper/figures/` - TikZ figure sources included by the paper build.
- `paper/source/` - Markdown mirror of the manuscript.
- `paper/submission/` - citation, claim, presentation, and submission audits.
- `physics_atlas/` - construction records, validators, schemas, and diagnostic
  outputs for the physics tracks.
- `retrodiction_atlas/` - retrodiction cards and ledger.
- `unification_atlas/` - unification cards and domain-tension ledger.
- `scripts/` - small support scripts for release maintenance.

## Scope and Limitations

- The construction artifacts are finite-carrier and toy-level unless the paper
  explicitly says otherwise.
- The 27-round adversarial campaign and 20 repairs/probes are an audit trail,
  not journal peer review or independent replication. The earlier external gate
  never issued final approval. The campaign was run with AI agents under a
  manager/reviewer split; its plan, ledger, and findings are published under
  `review_2026/`, as is the external technical review it answered.
- No forcing prediction is claimed; the three questions are stated as
  construction programs. For P1, each of
  nineteen exact graph fibers has disjoint endpoint forward-reachability sets
  under four directed reductions and bidirectional Delta-Y/Y-Delta, while
  symmetric-closure orbit disjointness remains open. Six exact connected `C2_L1`
  joint-map fibers collapse under the exact diagonal tensor gauge; they are not
  inequivalent tensor-network presentations and imply no bulk-geometry theorem.
  BMV-null is conditional on an assumed perfect-record
  channel, and record-stability is token-definition-sensitive; those two
  construction programs remain open.
- The repository is not uniformly self-verifying: some historical validators
  regenerate artifacts or validate stored summaries, and the preregistration
  freeze is a consistency gate rather than tamper-evident evidence. Run broad
  historical sweeps in scratch copies.
- Rebuilding the corpus-hash rows in QM-GR steps 51--54 requires
  `SIX_BIRDS_PAPERS_ROOT` to point to the external Foundations corpus; ordinary
  validation of the published artifacts does not.
- Citation metadata and paper claims are tracked in `paper/submission/`, but
  the LaTeX source remains the build authority.
