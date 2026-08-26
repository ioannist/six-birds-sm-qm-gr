# Six Birds SM, QM, and GR

This repository contains the public support surface for the paper:

> **To Kill Three Stones with Six Birds: A Common Grammar for the SM, QM, and GR**
>
> DOI: [10.5281/zenodo.20713213](https://doi.org/10.5281/zenodo.20713213)
>
> Archived at: https://zenodo.org/records/20713213

The paper applies the Six Birds emergence calculus to two physics tracks:
Standard Model structural selection and the QM-GR interface. It reports two
finite-carrier construction results and three falsifiable predictions, while
keeping the stated scope at toy-level structural evidence rather than
frame-transfer to nature-level derivations.

## What this repository provides

- Modular LaTeX paper sources under `paper/`, with section files,
  appendices, figures, bibliography, and submission audit notes.
- A tracked flattened manuscript source at the repository root:
  `Tsiokos_2026_To_Kill_Three_Stones_with_Six_Birds_A_Common_Grammar_for_the_SM_QM_and_GR.tex`.
- Mirrored Markdown source under `paper/source/` for review and editing.
- Physics-track construction artifacts and validator outputs under
  `physics_atlas/`.
- Re-derivation pointers for the three Section 6 predictions in
  `physics_atlas/INDEPENDENT_REDERIVATIONS.md`.
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

## Re-Derivation Checks

The main prediction checks are documented in
`physics_atlas/INDEPENDENT_REDERIVATIONS.md`. The principal entry points are:

```bash
cd physics_atlas/thread_qm_gr/steps/step55_f51_entanglement_underdetermines_geometry_artifacts
python3 run_step55.py --self

cd ../step56_gravitational_mediation_bmv_prediction_artifacts
python3 run_step56.py --self

cd ../../../thread_cluster_a/steps/step69_mode_t_record_stability_baryon_no_monopole_falsifiable_prediction_artifacts
python3 run_step69.py --self
```

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
- The adversarial review record is part of the audit trail; it is not journal
  peer review or independent replication.
- The three predictions are intended as falsifiable outputs of the stated
  grammar-level program, not as established experimental facts.
- Citation metadata and paper claims are tracked in `paper/submission/`, but
  the LaTeX source remains the build authority.
