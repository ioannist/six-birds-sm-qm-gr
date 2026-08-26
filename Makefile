.PHONY: paper-build paper-clean paper-bib paper-rebuild paper-flatten paper-qeios paper-qeios-clean

# The paper builds out of paper/ using its own latexmkrc, which sets
# out_dir/aux_dir=build and flattens main.tex into build/main_flat.tex
# (latexpand --expand-bbl, so the flattened source carries its bibliography).

paper-build:
	@if command -v latexmk >/dev/null 2>&1; then \
		cd paper && latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex; \
	else \
		cd paper && pdflatex -interaction=nonstopmode -halt-on-error -output-directory=build main.tex && \
		bibtex build/main && \
		pdflatex -interaction=nonstopmode -halt-on-error -output-directory=build main.tex && \
		pdflatex -interaction=nonstopmode -halt-on-error -output-directory=build main.tex; \
	fi
	@$(MAKE) paper-flatten

paper-clean:
	@if command -v latexmk >/dev/null 2>&1; then \
		cd paper && latexmk -C main.tex; \
	else \
		rm -f paper/build/*; \
	fi
	@rm -f paper/build/main_flat.tex

paper-bib:
	cd paper && bibtex build/main

paper-flatten:
	@if ! command -v latexpand >/dev/null 2>&1; then \
		echo "missing LaTeX flattener: install latexpand" >&2; \
		exit 1; \
	fi
	cd paper && latexpand --expand-bbl build/main.bbl main.tex -o build/main_flat.tex

paper-rebuild: paper-clean paper-build

paper-qeios:
	./scripts/build_qeios_assets.sh

paper-qeios-clean:
	rm -rf paper/build/qeios_single
