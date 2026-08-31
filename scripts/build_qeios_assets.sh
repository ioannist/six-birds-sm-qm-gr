#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PAPER_DIR="$ROOT_DIR/paper"
BUILD_DIR="$PAPER_DIR/build"
QEIOS_BUILD_DIR="$BUILD_DIR/qeios_single"
FLAT_TEX="$BUILD_DIR/main_flat.tex"
BBL_FILE="$BUILD_DIR/main.bbl"
QEIOS_TEX="$QEIOS_BUILD_DIR/qeios_single.tex"
QEIOS_PDF="$QEIOS_BUILD_DIR/qeios_single.pdf"
QEIOS_ZIP="$QEIOS_BUILD_DIR/qeios_source_bundle.zip"
QEIOS_NOTES_SRC="$ROOT_DIR/scripts/templates/qeios_submission_notes.md"
QEIOS_README_SRC="$ROOT_DIR/scripts/templates/qeios_readme_build.txt"
QEIOS_NOTES="$QEIOS_BUILD_DIR/Qeios_Submission_Notes.md"
QEIOS_README="$QEIOS_BUILD_DIR/README_BUILD.txt"

cd "$ROOT_DIR"
make paper-build

mkdir -p "$QEIOS_BUILD_DIR"

python3 - <<'PY'
from pathlib import Path

flat_tex = Path("paper/build/main_flat.tex").read_text()
bbl = Path("paper/build/main.bbl").read_text()

# orcidlink may be missing on some TeX installs; provide an inline fallback.
orcid_fallback = r"""% orcidlink: use package if available, else provide a fallback
\IfFileExists{orcidlink.sty}{\usepackage{orcidlink}}{%
  \newcommand{\orcidlink}[1]{\textsuperscript{\href{https://orcid.org/#1}{ORCID}}}%
}"""
flat_tex = flat_tex.replace(r"\usepackage{orcidlink}", orcid_fallback)

# Drop the self-assigned preprint (Zenodo) DOI from the first-page footer;
# Qeios mints its own DOI on acceptance. This targets only the footer string
# (the Zenodo DOIs inside the bibliography are different numbers and are kept).
flat_tex = flat_tex.replace(r" \quad \doi{10.5281/zenodo.22210962}", "")

# If the flattened source still references the external .bib (i.e. it was NOT
# produced with `latexpand --expand-bbl`), embed the .bbl so the single file is
# self-contained. With the repo's latexmkrc the bibliography is already inlined,
# so this replacement is a no-op in the normal path.
flat_tex = flat_tex.replace(
    "\\bibliographystyle{unsrtnat}\n\\bibliography{references}",
    "% Bibliography embedded from BibTeX .bbl output (no external .bib needed)\n" + bbl.rstrip(),
)

Path("paper/build/qeios_single/qeios_single.tex").write_text(flat_tex)
PY

# The figures are raster PNGs (not inlinable TeX), so the single-file build
# still needs them next to qeios_single.tex.
mkdir -p "$QEIOS_BUILD_DIR/figures"
cp "$PAPER_DIR"/figures/*.png "$QEIOS_BUILD_DIR/figures/"

cp "$QEIOS_NOTES_SRC" "$QEIOS_NOTES"
cp "$QEIOS_README_SRC" "$QEIOS_README"

(
  cd "$QEIOS_BUILD_DIR"
  pdflatex -interaction=nonstopmode -halt-on-error qeios_single.tex >/dev/null
  pdflatex -interaction=nonstopmode -halt-on-error qeios_single.tex >/dev/null
)

rm -f "$QEIOS_ZIP"
(
  cd "$PAPER_DIR"
  # Single-file deliverables flat at the archive root.
  zip -jq "$QEIOS_ZIP" \
    build/qeios_single/qeios_single.tex \
    build/qeios_single/qeios_single.pdf \
    build/qeios_single/Qeios_Submission_Notes.md \
    build/qeios_single/README_BUILD.txt
  # Modular sources with their paths preserved (so both the single-file build and
  # `latexmk main.tex` resolve figures/, includes/, and the bibliography).
  zip -qr "$QEIOS_ZIP" \
    main.tex \
    latexmkrc \
    includes \
    build/main.bbl \
    references.bib \
    sections \
    appendices \
    figures \
    -x 'figures/generated/*' '*/.gitkeep' '.gitkeep'
)

echo "Qeios assets ready:"
echo "  $QEIOS_TEX"
echo "  $QEIOS_PDF"
echo "  $QEIOS_ZIP"
