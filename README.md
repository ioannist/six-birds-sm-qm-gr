# Six Birds SM, QM, and GR

This repository contains the public support surface for the paper:

> **To Kill Three Stones with Six Birds: A Common Grammar for the SM, QM, and GR**
>
> DOI: [10.5281/zenodo.20713213](https://doi.org/10.5281/zenodo.20713213)
>
> Archived at: https://zenodo.org/records/20713213

Version 3 applies the Six Birds emergence calculus to two finite physics tracks:
Standard Model structural selection and the QM-GR interface. Post-publication
verification (Version 2) retained several conditional constructions and two toy
theorems, materially corrected or retracted stronger claims, and replaced the
former prediction-forcing claims with three sharply typed construction programs.
Version 3 adds the reviewer-certified resolution of the first program within
declared scope: nineteen exact same-graph fibers on the thirteen residual
min-cut carriers have disjoint complete queue-exhaustive orbits under the five
declared move classes, modulo terminal-label-fixed exact weighted isomorphism,
with undeclared transformations open. Six exact finite connected `C2_L1`
state-level underdetermination examples also survive the declared capacity
convention and frozen family relation (see `open_programs/`).
The other two programs remain open, with an approved research proposal at
`PROPOSAL_DYNAMICAL_RECORD_STABILITY.md`. No foundational grade, universality,
or frame-transfer claim is made.

## What this repository provides

- Modular LaTeX paper sources under `paper/`, with section files,
  appendices, figures, bibliography, and submission audit notes.
- A tracked flattened manuscript source at the repository root:
  `Tsiokos_2026_To_Kill_Three_Stones_with_Six_Birds_A_Common_Grammar_for_the_SM_QM_and_GR.tex`.
- Mirrored Markdown source under `paper/source/` for review and editing.
- Physics-track construction artifacts and validator outputs under
  `physics_atlas/`.
- The certified Version-2 claims map and machine-verifiable repairs/probes under
  `review_2026/`, plus the certified Version-3 closure records under
  `open_programs/`.
- Historical re-derivation pointers under
  `physics_atlas/INDEPENDENT_REDERIVATIONS.md`; superseded headline claims there
  do not override `review_2026/CLAIMS_MAP.md`.
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
- `figures/` — the raster figures, which are not inlinable and must accompany
  `qeios_single.tex`.
- `qeios_source_bundle.zip` — upload/archive bundle (single-file deliverables
  plus the full modular source and figures).
- `Qeios_Submission_Notes.md` — copy/paste submission metadata.
- `README_BUILD.txt` — build instructions for the bundle.

The submission-notes and README templates live under `scripts/templates/`.

## Certified Re-Derivation Checks

The Version-2/3 entry points include:

```bash
cd review_2026/repairs/s1_carrier_reconstruction
python3 run_s1_carrier_reconstruction_v3.py --self

cd ../../probes/p1_kernel_quotient
python3 run_active_cut_quotient_v3.py --self

cd ../../repairs/q5_lp_duality
python3 run_q5.py --self

cd ../../../open_programs/prog3_cut_fingerprints/step2_orbit_saturation
python3 run_step2.py --self

cd ../../prog2_state_underdetermination/step5_family_gauge_classification
python3 run_step5.py --self
```

See `review_2026/CLAIMS_MAP.md` for the complete certified disposition and the
artifact directory attached to each repaired statement.

## Repository Layout

- `paper/main.tex` - LaTeX entry point.
- `paper/sections/` and `paper/appendices/` - modular manuscript source.
- `paper/figures/` - figure assets used by the paper build.
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
  never issued final approval.
- The former three forcing predictions are retracted or reduced. For P1,
  nineteen exact graph fibers have disjoint complete five-class orbits modulo
  terminal-label-fixed exact weighted isomorphism, with transformations outside
  those classes open; six exact finite connected `C2_L1` state examples survive
  the declared capacity convention and frozen family relation, without implying
  a bulk-geometry theorem. BMV-null is conditional on an assumed perfect-record
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
