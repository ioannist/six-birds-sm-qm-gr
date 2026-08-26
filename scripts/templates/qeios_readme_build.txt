README_BUILD.txt
================
To Kill Three Stones with Six Birds: A Common Grammar for the SM, QM, and GR
Ioannis Tsiokos <ioannis@automorph.io>

Build instructions for the Qeios source bundle
-----------------------------------------------

OPTION A: Single-file build (recommended, no BibTeX needed)

    pdflatex qeios_single.tex
    pdflatex qeios_single.tex

  Two passes are needed for cross-references. No .bib file is required;
  the bibliography is embedded in the .tex file.

  NOTE: the five figures are raster images and are NOT inlined in the .tex.
  Keep the accompanying `figures/` directory next to `qeios_single.tex`
  (it ships in this bundle) so the `\includegraphics` calls resolve.

OPTION B: Full modular build

    make paper-build

  This writes the canonical manuscript outputs to:

    paper/build/main.pdf
    paper/build/main_flat.tex

  The modular build requires:
  - `paper/references.bib`
  - `paper/includes/paper_macros.tex`
  - all files under `paper/sections/` and `paper/appendices/`
  - all images under `paper/figures/`
  - `paper/latexmkrc` (sets the build dir and produces main_flat.tex)

OPTION C: Generate all Qeios-ready assets

    make paper-qeios

  This produces:

    paper/build/qeios_single/qeios_single.tex
    paper/build/qeios_single/qeios_single.pdf
    paper/build/qeios_single/qeios_source_bundle.zip
    paper/build/qeios_single/Qeios_Submission_Notes.md
    paper/build/qeios_single/README_BUILD.txt
    paper/build/qeios_single/figures/*.png

Files in this bundle
--------------------
  qeios_single.tex                         Self-contained single-file TeX (needs figures/)
  qeios_single.pdf                         Pre-built PDF from qeios_single.tex
  qeios_source_bundle.zip                  Source bundle for upload / archive
  Qeios_Submission_Notes.md                Copy/paste submission metadata
  README_BUILD.txt                         This file
  main.tex                                 Modular main TeX
  latexmkrc                                latexmk configuration (build dir + flatten)
  includes/paper_macros.tex                Shared macro definitions
  build/main.bbl                           Pre-built BibTeX output
  references.bib                           BibTeX database
  sections/*.tex                           Section files
  appendices/*.tex                         Appendix files
  figures/*.png                            Figure image assets (required by both builds)

Requirements
------------
  - pdflatex (TeX Live 2022 or later recommended)
  - latexmk recommended for the modular build
  - latexpand for the flattened export (uses --expand-bbl)
  - zip for the source-bundle archive
  - Standard packages used by `paper/main.tex`
  - Optional: orcidlink (fallback provided in `qeios_single.tex`)
