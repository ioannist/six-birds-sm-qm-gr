#!/usr/bin/env bash
# Stage-1 reproduction baseline: run every live step validator (--self) with a bounded pool.
set -u
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
OUT="$ROOT/review_2026/stage1_repro"
LOGS="$OUT/logs"
export TMPDIR=/mnt/8tb/six-birds-sm-qm-gr/scratch 2>/dev/null || true
mkdir -p "$TMPDIR" 2>/dev/null || export TMPDIR=/tmp
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
find "$ROOT/physics_atlas" -name "run_*.py" -not -path "*/review_packets/*" | sort | \
xargs -P 16 -I{} bash -c '
  r="{}"
  rel="${r#'"$ROOT"'/physics_atlas/}"
  tag=$(echo "$rel" | tr "/" "__" | sed "s/\.py$//")
  start=$(date +%s)
  timeout 2400 python3 "$r" --self >"'"$LOGS"'/$tag.log" 2>&1
  rc=$?
  end=$(date +%s)
  echo "$rc $((end-start))s $rel" >> "'"$OUT"'/results_raw.txt"
'
sort -k3 "$OUT/results_raw.txt" > "$OUT/results.txt"
awk '{if($1=="0")p++;else f++}END{printf "PASS %d FAIL %d TOTAL %d\n",p,f,p+f}' "$OUT/results.txt" > "$OUT/SUMMARY.txt"
awk '$1!="0"' "$OUT/results.txt" >> "$OUT/SUMMARY.txt"
cat "$OUT/SUMMARY.txt"
