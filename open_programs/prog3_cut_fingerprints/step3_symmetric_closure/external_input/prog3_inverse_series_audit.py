#!/usr/bin/env python3
from __future__ import annotations
import sys
from pathlib import Path
ROOT=Path('/home/repos/six-birds-sm-qm-gr')
STEP2=ROOT/'open_programs/prog3_cut_fingerprints/step2_orbit_saturation'
STEP1=ROOT/'open_programs/prog3_cut_fingerprints/step1_finite_range'
for p in (STEP2,STEP1): sys.path.insert(0,str(p))
from saturation_engine import saturate_orbit
from exact_engine import enumerate_terminal_cuts, terminal_fixed_weighted_canonical_key, v2, five_move_closure_exact
from step1_core import carrier_map

name='wheel_W4__b8__leaf_offset0'; seed=47
raw=v2.seeded_weights(carrier_map()[name],seed)
g,a0,_=five_move_closure_exact(raw)
u,v,c=g.weighted_edges[0]
new='INV_SERIES_NODE'
rows=list(g.weighted_edges[1:])+[(u,new,c),(new,v,2*c)]
expanded=v2.make_graph(g.name+'_inverse_series',g.family,g.boundaries,rows,g.boundary_map)
a1=enumerate_terminal_cuts(expanded)
reduced=v2.transform_series(expanded,new)
key0=terminal_fixed_weighted_canonical_key(g); keyr=terminal_fixed_weighted_canonical_key(reduced)
forward=saturate_orbit(g); keye=terminal_fixed_weighted_canonical_key(expanded)
print(f'carrier={name} seed={seed}')
print(f'base_edges={len(g.edges)} expanded_edges={len(expanded.edges)}')
print(f'fingerprint_equal={a0.values==a1.values}')
print(f'expanded_unique={a1.unique}')
print(f'series_reduces_back_exactly={key0==keyr}')
print(f'expanded_in_forward_saturation={keye in forward.states_by_key}')
print(f'forward_state_count={len(forward.states_by_key)} saturated={forward.saturated}')
print('PASS' if a0.values==a1.values and a1.unique and key0==keyr and keye not in forward.states_by_key else 'FAIL')
