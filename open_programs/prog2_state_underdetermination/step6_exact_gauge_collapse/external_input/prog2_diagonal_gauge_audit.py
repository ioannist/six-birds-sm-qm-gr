#!/usr/bin/env python3
from __future__ import annotations
import sys
from pathlib import Path
import numpy as np

ROOT=Path('/home/repos/six-birds-sm-qm-gr')
STEP5=ROOT/'open_programs/prog2_state_underdetermination/step5_family_gauge_classification'
STEP3=ROOT/'open_programs/prog2_state_underdetermination/step3_kernel_test'
STEP1=ROOT/'open_programs/prog2_state_underdetermination/step1_engine'
for p in (STEP5, STEP3, STEP1):
    sys.path.insert(0,str(p))
from step5_core import construct_pairs, product
from survivor_loader import as_tensor_carrier
from tensor_engine import build_network
from conventions_step3 import convention_by_id
from step3_core import dress_network, _raw_contract
from gauge_library import apply_internal_gauge

conv=convention_by_id('C2_L1')

def fval(x):
    # exact algebraic element exposes decimal(); Fraction works with float
    return float(x.decimal(50)) if hasattr(x,'decimal') else float(x)

def solve_log_h(graph, c, cp):
    nodes=list(graph.nodes); idx={v:i for i,v in enumerate(nodes)}
    E=len(graph.edges); V=len(nodes)
    B=np.zeros((V,E)); b=np.zeros(V)
    for j,((u,v),a,ap) in enumerate(zip(graph.edges,c,cp)):
        B[idx[u],j]=1.0; B[idx[v],j]=-1.0
        b[idx[u]] += 0.5*np.log(ap/a)
    # discard one dependent row; minimum norm solution
    x,*_=np.linalg.lstsq(B[:-1,:],b[:-1],rcond=None)
    return x, np.max(np.abs(B@x-b)), b.sum()

def proportional_residual(left,right):
    lv=left.ravel(); rv=right.ravel()
    denom=np.vdot(rv,rv)
    lam=np.vdot(rv,lv)/denom
    return float(np.linalg.norm(lv-lam*rv)/max(np.linalg.norm(lv),1e-300)), lam

rows=[]
for pair in construct_pairs():
    c=np.array([fval(x) for x in pair.base.weights])
    cp=np.array([fval(x) for x in pair.displaced.weights])
    carrier=as_tensor_carrier(pair.case.graph,2)
    independent=build_network(carrier,'structured_copy')
    base=dress_network(independent,tuple(c),conv)
    target=dress_network(independent,tuple(cp),conv)
    x,eq_res,sum_b=solve_log_h(pair.case.graph,c,cp)
    gauged=base
    for edge,xe in zip(gauged.carrier.edges,x):
        G=np.diag([np.exp(xe),1.0]).astype(np.complex128)
        gauged=apply_internal_gauge(gauged,edge.edge_id,G)
    vertex=[]; lambdas=[]
    for v in gauged.carrier.vertices:
        r,lam=proportional_residual(gauged.tensors[v],target.tensors[v])
        vertex.append(r); lambdas.append(lam)
    raw_g=_raw_contract(gauged); raw_t=_raw_contract(target)
    raw_res,raw_lam=proportional_residual(raw_g,raw_t)
    # normalized state residual
    ng=raw_g/np.linalg.norm(raw_g.ravel()); nt=raw_t/np.linalg.norm(raw_t.ravel())
    phase=np.vdot(nt.ravel(),ng.ravel()); phase=phase/abs(phase)
    state_res=float(np.linalg.norm(ng-phase*nt))
    rows.append((pair.candidate_id,eq_res,sum_b,max(vertex),raw_res,state_res,abs(np.prod(lambdas)-raw_lam)))

print('candidate,vertex_balance_residual,sum_balance,max_local_proportional_residual,raw_state_proportional_residual,normalized_state_residual,scalar_consistency_residual')
for row in rows:
    print(','.join([row[0]]+[f'{x:.3e}' for x in row[1:]]))
print('PASS' if all(max(r[1:])<1e-10 for r in rows) else 'FAIL')
