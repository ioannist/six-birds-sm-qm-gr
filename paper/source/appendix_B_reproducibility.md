# Appendix B — toy constructions & reproducibility

Every number in the body regenerates deterministically from the artifact repository accompanying this paper
(`physics_atlas/`, tracks `thread_cluster_a/` and `thread_qm_gr/`). Each step directory contains the build script (the
construction), a machine-readable schema (the claimed numbers), and a validator `run_stepNN.py` that **recomputes** the
headline quantities from frozen inputs and fails on mismatch, on anti-smuggling-gate violations, and on overclaim
phrases. Imports between steps are SHA-256-pinned. Python 3 + NumPy suffice; every validator runs offline.

## B.1 The SM track (selection layer) — key artifacts

| result (§) | artifact dir (under `thread_cluster_a/steps/`) | headline numbers the validator re-derives |
|---|---|---|
| neutral carrier + token-blind selection (§4.2) | `step8_structural_token_blind_selection_*` | $8640$-world neutral product; structural pruning $\to 468$; realized analog rank 2 in a 6-way tie (not unique) |
| corrected closure / exclusion (§4.2) | `step28–42` family (corrected chirality, mass-closure) | $11{,}990$ genuinely-chiral structures $\to \{2|3, SU(4)\}$ |
| clean separation = $\Delta_{\mathrm{fact}}$; $X/Y$ coset (§4.3–4.4) | `step41_mode_b_factorization_defect_clean_separation_*` | defect witnesses = $X/Y$ coset; $\Delta_{\mathrm{fact}}(\mathrm{SM},\mathrm{GUT})=15$, reverse $0$ |
| record-stability grounding (§4.5) | `step57/58/59_mode_b_record_stability_*` | $0$ record-stable $\wedge$ breaking out of $11{,}990$; substrate-only $60$; capacity-only $311$ |
| single-factor theorem (§4.3) | `step61_mode_t_single_factor_clean_separation_theorem_*` | symbolic 3-step proof; non-vacuous at $N=4$ |
| $N_{\mathrm{gen}}$-blindness theorem (§4.6) | `step62_mode_t_ngen_blindness_theorem_*` | all-$N$ invariance; verified to $N=1000$; odd-doublet control $N$-sensitive |
| unification cluster (§4.4) | `step63_*` | $\sin^2\theta_W = \operatorname{Tr}T_3^2/\operatorname{Tr}Q^2 = 2/(16/3) = 3/8$; $k_Y=5/3$; product control $3/23$ |
| fork resolution (§4.4) | `step65_mode_b_proton_monopole_fork_resolution_*` | record-stable breaking count $=0$; fork object verified = step-41 coset |
| measurement extension (§7.4) | `step66/67/68_*` | strict-extension witness; $D$-vs-$\Sigma_f$ discriminator |
| **Prediction 3** (§6.3) | `step69_mode_t_record_stability_baryon_no_monopole_falsifiable_prediction_*` | the $2\times2$ table $\{24,0;292,11674\}$; anti-circularity witnesses `carrier_00827`, `carrier_00770`; F27/F48 $=0$ on the clean sample |

## B.2 The QM–GR track (common refinement) — key artifacts

| result (§) | artifact dir (under `thread_qm_gr/steps/`) | headline numbers the validator re-derives |
|---|---|---|
| co-sourcing carrier + dynamics (§5.3) | `step25/26_*` | one $\psi$: Born + $T[\psi]$ residuals $0$; $V=V_0+\kappa T_{00}$ fixed point, residual $3.49\times10^{-16}$ ($\kappa=0.3$); runaway at $\kappa=30$ |
| program theorems (§5.2) | `step30–38` family | $T_{\mathrm{QG\text{-}NoGo}}$; $T_{\mathrm{QGR\text{-}Unique}}$; carrier-independence; nested control flips |
| RT bound + enrichment (§5.4) | `step41/42_*` (QM–GR numbering) | $S(A)\le\mathrm{mincut}$; saturation $0.729/0.904/0.941$ at $D{=}2,3,4$ (seeds 101–505) |
| entropy cone / MMI (§5.4) | `step44_holographic_mmi_entropy_cone_*` | holographic $I_3\le0$; min-cut $I_3=0$; GHZ $I_3=\log 2$ |
| discrete Einstein condition (§5.4) | `step45_discrete_einstein_consistency_*` | $38$ regions / $14$ edges; rank $10$, cokernel $28$; residuals $9\times10^{-17}$ vs $0.042$ |
| premise door-test + grounding (§5.3) | `step47_common_carrier_door_test_*` | per-law form-not-existence; commutator $0.7071$; non-co-sourcing $0.3806$ |
| ladder vs fork (§5.2) | `step48_ladder_vs_fork_resolution_*` | ladder defect $8$ (incl. $A_{\mathrm{RT}}=d_0+2d_2$ variant); fork $0/0$; nested $0$; route mismatch $0.5$ |
| one fiber-volume ledger (§5.4) | `step50_born_area_one_fiber_volume_ledger_*` | $\mathrm{area}=\log 3$ seed-invariant; $S_{\mathrm{Born}}$ varies; ratios $0.9986/0.9973/0.9995 < 1$ strictly |
| monogamy forcing (§5.4) | `step51_f51_joint_prediction_*` | geometric-dual compatibility (I3-independent); with-compat $\max I_3=-0.033$; GHZ rel-gap $0.79$; broken-compat un-forces |
| Bell / F49 (§7.1) | `step52_f49_bell_nonlocal_residual_*` | CHSH $2\sqrt2$ computed; bound $2$ enumerated (16 strategies); control LHV table error $1.8\times10^{-15}$ |
| BH information / F34 (§7.2) | `step53_f34_information_loss_normal_form_*` | rank $27=$ internal dim; explicit-$G$ residual $3\times10^{-15}$; partial witness $5.3\times10^{-16}$ / gap $0.0097$ |
| $\Lambda$ / F50 (§7.3) | `step54_f50_background_moduli_demarcation_*` | background sweep $15/18$ pass; $\kappa$ boundary ($\le10$ pass, $\ge15$ fail) |
| **Prediction 1** (§6.1) | `step55_f51_entanglement_underdetermines_geometry_*` | fingerprint $11{,}049$ features; central-diff rank/nullity $9/5$ (seeds 101/202/303); clean shadows $2$/seed; tree control nullity $0$ |
| **Prediction 2** (§6.2) | `step56_gravitational_mediation_bmv_prediction_*` | initial entanglement $6.2\times10^{-18}$; fork channel $\mathcal N=0$, CHSH $0$, damping $1.0$; coherent control $\mathcal N=0.3536$, CHSH $\sqrt6=2.4495$; restriction derived from `step48_access_tuple`+`T_QG_NoGo`; `mean_field_channel_used=false` |

## B.3 Re-run recipe

```bash
cd physics_atlas/thread_<track>/steps/<step_dir>
python3 run_stepNN.py --self     # validator: recomputes + audits this step
python3 run_stepNN.py --chain    # additionally re-validates frozen upstream steps
python3 <build_script>.py        # regenerates every artifact deterministically
```

All validators exit non-zero on any mismatch. The two review packets discussed in Appendix D additionally ship
`SHA256SUMS` manifests verified from clean extracts.

## B.4 Independent re-derivation

Beyond validator passes, every headline number in §6 was reproduced by code written independently of the build scripts
(direct SVD of centrally-differenced Jacobians for Prediction 1; direct BMV channel calculation for Prediction 2; direct recount of the $2\times2$ partition and the
single-conjunct witness sets for Prediction 3), with exact agreement. The public reproducibility record for these
checks is the diagnostic-artifact manifest `physics_atlas/INDEPENDENT_REDERIVATIONS.md`; process logs are not part of
the public artifact surface.
