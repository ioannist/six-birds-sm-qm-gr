# Submission Checklist

- From the repo root, build with `(cd paper && latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex)`.
- Confirm `paper/build/main.pdf` and `paper/build/main_flat.tex` exist.
- Run stale-text searches for old title variants, obsolete prediction-count language, wrong-section references for
  proton/monopole material, placeholder-figure language, and inactive-bibliography language.
- Scan the final LaTeX log for citation warnings, label warnings, figure-file problems, and natbib warnings before printing.
- Confirm Figures F0-F4 have corresponding files under `paper/figures/`.
