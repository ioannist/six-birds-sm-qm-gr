#!/usr/bin/env python3
from __future__ import annotations
import csv
from collections import Counter
from pathlib import Path
P=Path('/home/repos/six-birds-sm-qm-gr/open_programs/prog3_cut_fingerprints/step2_orbit_saturation/endpoint_saturation_step2.csv')
rows=list(csv.DictReader(P.open(newline='',encoding='utf-8')))
acc=Counter(); novel=Counter()
for row in rows:
    for token in row['accepted_move_census'].split('|'):
        k,v=token.split(':'); acc[k]+=int(v)
    for token in row['novel_state_census'].split('|'):
        k,v=token.split(':'); novel[k]+=int(v)
print('endpoint_count='+str(len(rows)))
print('accepted='+','.join(f'{k}:{acc[k]}' for k in acc))
print('novel='+','.join(f'{k}:{novel[k]}' for k in novel))
print('state_range='+str((min(int(r['canonical_state_count']) for r in rows),max(int(r['canonical_state_count']) for r in rows))))
print('all_saturated='+str(all(r['saturated']=='True' for r in rows)))
