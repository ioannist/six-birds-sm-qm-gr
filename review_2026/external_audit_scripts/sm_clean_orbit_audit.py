#!/usr/bin/env python3
from __future__ import annotations
import csv
from pathlib import Path
ROOT=Path('/mnt/data/sixbirds_review/six-birds-sm-qm-gr/review_2026/repairs/s1_carrier_reconstruction')
for fn in ['s1_v3_singleton_scalar_branches.csv','s1_v3_two_scalar_pair_branches.csv']:
    rows=list(csv.DictReader((ROOT/fn).open(newline='',encoding='utf-8')))
    clean=[r for r in rows if r['clean_or_breaking']=='clean']
    branch_key='singleton_branch_orbit_id' if 'singleton' in fn else 'two_scalar_pair_orbit_id'
    print(','.join([
        fn,
        f'all={len(rows)}',f'clean={len(clean)}',
        f'clean_labelled_structures={len({r["structure_id"] for r in clean})}',
        f'clean_carrier_orbits={len({r["carrier_orbit_id"] for r in clean})}',
        f'clean_branch_orbits={len({r[branch_key] for r in clean})}',
    ]))
    print('structures='+' || '.join(sorted({r['structure_id'] for r in clean})))
    print('carrier_orbits='+' || '.join(sorted({r['carrier_orbit_id'] for r in clean})))
