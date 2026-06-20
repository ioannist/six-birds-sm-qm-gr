#!/usr/bin/env bash
#
# make_handoff_zip.sh — build a versioned handoff bundle of the Six Birds lattice project
# plus the SBT paper corpus, for handing to an external agent/advisor.
#
# Each run writes the NEXT version (..._v1.zip, _v2.zip, ...) to the repo root and DELETES
# all prior handoff zips, so only the latest remains.
#
# Contents (mirrors the bundle prepared 2026-06-19):
#   - the public git tree of this repo (tracked + untracked-not-ignored), incl. SIX_BIRDS_UNDERSTANDING/
#   - the lattice construction context that is gitignored but an advisor needs:
#       EXPERIMENT_PROPOSAL.md, manager_log.md, cascade_*, findings_*, mode_b_*.csv,
#       engine_study/, _superseded_wrong_frame/, recent steps (>= $MIN_STEP), and the
#       Rust engine SOURCE (vendor/six-birds-pica, minus its build target)
#   - all papers from ../six-birds-papers (*.tex + *.md)
# Excludes all build/data bulk: target/, __pycache__, caches, *.npy/*.npz/*.pstats/*.pyc.
#
# Usage:  scripts/make_handoff_zip.sh            # builds the next version
#         MIN_STEP=106 scripts/make_handoff_zip.sh   # include step106+ instead of 103+
#         PAPERS_DIR=/path/to/papers scripts/make_handoff_zip.sh
set -euo pipefail

# --- locate dirs (works regardless of cwd) ---
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
REPO_NAME="$(basename "$REPO_ROOT")"
PARENT_DIR="$(dirname "$REPO_ROOT")"
PAPERS_DIR="${PAPERS_DIR:-$PARENT_DIR/six-birds-papers}"
PAPERS_NAME="$(basename "$PAPERS_DIR")"

# steps numbered >= MIN_STEP are the current construction frame; older steps are superseded bulk.
MIN_STEP="${MIN_STEP:-103}"

BASENAME="six_birds_lattice_handoff"
EXCLUDE_DIRS='/(target|__pycache__|\.pytest_cache|\.ruff_cache|node_modules|\.git)/'
EXCLUDE_EXTS='\.(npy|npz|pstats|pyc)$'

LIST="$(mktemp)"
trap 'rm -f "$LIST" "$LIST.tmp"' EXIT

# --- 1) repo file list (paths relative to PARENT_DIR, i.e. prefixed with the repo dir name) ---
cd "$REPO_ROOT"
{
  # public git tree
  git ls-files
  git ls-files --others --exclude-standard
  # gitignored-but-needed lattice construction context
  for f in lattice_qcd_layer/EXPERIMENT_PROPOSAL.md \
           lattice_qcd_layer/manager_log.md \
           lattice_qcd_layer/cascade_map_lattice.md \
           lattice_qcd_layer/cascade_lattice.canvas \
           lattice_qcd_layer/findings_lattice.md; do
    [ -e "$f" ] && echo "$f"
  done
  ls lattice_qcd_layer/mode_b_*.csv 2>/dev/null || true
  for d in lattice_qcd_layer/engine_study \
           lattice_qcd_layer/_superseded_wrong_frame \
           lattice_qcd_layer/vendor/six-birds-pica; do
    [ -d "$d" ] && find "$d" -type f
  done
  # recent step artifacts (>= MIN_STEP), text/code only (bulk filtered below)
  for d in lattice_qcd_layer/steps/step*/; do
    [ -d "$d" ] || continue
    n="$(basename "$d" | sed -E 's/^step0*([0-9]+).*/\1/')"
    if [[ "$n" =~ ^[0-9]+$ ]] && [ "$n" -ge "$MIN_STEP" ]; then
      find "$d" -type f
    fi
  done
} | grep -vE "$EXCLUDE_DIRS" | grep -vE "$EXCLUDE_EXTS" | sed "s#^#$REPO_NAME/#" > "$LIST"

# --- 2) papers (relative to PARENT_DIR) ---
if [ -d "$PAPERS_DIR" ]; then
  ( cd "$PARENT_DIR" && ls "$PAPERS_NAME"/*.tex "$PAPERS_NAME"/*.md 2>/dev/null ) >> "$LIST" || true
else
  echo "WARN: papers dir not found at $PAPERS_DIR — bundle will omit the corpus." >&2
fi

# --- 2b) the REAL strict-extension engine: the sixbirds_event Python driver SOURCE + vision.md ---
# This is the authority for "run the real engine" (computes the global-packaging obstruction
# verdict; the Rust six-birds-pica it drives is already bundled via vendor/six-birds-pica above).
EVENT_PKG_DIR="${EVENT_PKG_DIR:-$PARENT_DIR/six-birds-event-package}"
EVENT_PKG_NAME="$(basename "$EVENT_PKG_DIR")"
if [ -d "$EVENT_PKG_DIR" ]; then
  {
    [ -e "$EVENT_PKG_DIR/vision.md" ] && echo "$EVENT_PKG_NAME/vision.md"
    [ -d "$EVENT_PKG_DIR/src/sixbirds_event" ] && \
      ( cd "$PARENT_DIR" && find "$EVENT_PKG_NAME/src/sixbirds_event" -type f )
  } | grep -vE "$EXCLUDE_DIRS" | grep -vE "$EXCLUDE_EXTS" >> "$LIST"
else
  echo "WARN: event-package dir not found at $EVENT_PKG_DIR — bundle will omit the real engine source." >&2
fi

# de-dup + never include a handoff zip in itself
sort -u "$LIST" | grep -vE "/$BASENAME[^/]*\.zip$" > "$LIST.tmp"
mv "$LIST.tmp" "$LIST"

# --- 3) compute next version ---
maxv=0
shopt -s nullglob
for z in "$REPO_ROOT/${BASENAME}_v"*.zip; do
  v="$(basename "$z" | sed -E "s/^${BASENAME}_v([0-9]+)\.zip\$/\1/")"
  if [[ "$v" =~ ^[0-9]+$ ]] && [ "$v" -gt "$maxv" ]; then maxv="$v"; fi
done
nextv=$((maxv + 1))
OUT="$REPO_ROOT/${BASENAME}_v${nextv}.zip"

# --- 4) build the zip (paths resolve from PARENT_DIR) ---
cd "$PARENT_DIR"
rm -f "$OUT"
zip -q "$OUT" -@ < "$LIST"

# --- 5) delete all prior handoff zips (keep only the new one) ---
for z in "$REPO_ROOT/${BASENAME}"*.zip; do
  [ "$z" = "$OUT" ] && continue
  echo "  deleted previous: $(basename "$z")"
  rm -f "$z"
done

echo "Created: $OUT"
echo "  size:  $(du -h "$OUT" | cut -f1)"
echo "  files: $(wc -l < "$LIST")"
echo "  steps included: >= $MIN_STEP   papers: $([ -d "$PAPERS_DIR" ] && echo yes || echo MISSING)"
