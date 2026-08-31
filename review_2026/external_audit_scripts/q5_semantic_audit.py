#!/usr/bin/env python3
from __future__ import annotations
import csv,json,math
from pathlib import Path
STORED=Path('/mnt/data/sixbirds_review/six-birds-sm-qm-gr/review_2026/repairs/q5_lp_duality')
FRESH=Path('/mnt/data/sixbirds_review_logs/q5_rebuilt')
files=sorted(p.name for p in FRESH.iterdir() if p.is_file())
for name in files:
    same=(STORED/name).read_bytes()==(FRESH/name).read_bytes()
    print(f'{name},byte_equal={same}')
# Numeric drift for linear response.
a=list(csv.DictReader((STORED/'q5_linear_response.csv').open()))
b=list(csv.DictReader((FRESH/'q5_linear_response.csv').open()))
maxdiff=0.0; field=''; region=''
for ra,rb in zip(a,b):
    for k in ra:
        try: d=abs(float(ra[k])-float(rb[k]))
        except Exception: continue
        if d>maxdiff: maxdiff=d; field=k; region=ra['region']
print(f'linear_response_max_abs_numeric_drift={maxdiff:.17g},field={field},region={region}')
ja=json.loads((STORED/'q5_results.json').read_text()); jb=json.loads((FRESH/'q5_results.json').read_text())
keys=['all_min_cuts_unique','primal_feasible_all_regions','dual_feasible_all_regions','strong_duality_all_regions','complementary_slackness_all_regions','sensitivity_equals_shadow_price_all_region_edges']
print('exact_semantic_flags_equal='+str(all(ja[k]==jb[k] for k in keys)))
print('linear_response_verdict_equal='+str(ja['linear_response']['verdict']==jb['linear_response']['verdict']))
print('composition_verdict_equal='+str(ja['composition']['verdict']==jb['composition']['verdict']))
print('born_i3_abs_drift='+format(abs(ja['composition']['born_i3']-jb['composition']['born_i3']),'.17g'))
