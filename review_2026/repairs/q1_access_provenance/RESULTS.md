# Q1-REPAIR-1 results

## Field-to-mode provenance

Population: **54** states (`26` Step25 samples, `16` Step28 history states, `8` fresh seeded states, and `4` paired controls). The field-derived quotient has 14 `q_QM` fibers and 10 `q_GR` fibers. The maximum residual when rebuilding all 16 stored Step28 potentials is `8.77708367144e-17`.

| check | factors | defect_pair_count | first_witness |
|---|---|---|---|
| born_audit_determines_d1 | True | 0 |  |
| born_audit_determines_d3 | False | 1 | control_potential_base|control_potential_perturbed |
| q_QM_determines_d1 | True | 0 |  |
| q_QM_determines_d3 | False | 5 | step25_004|control_potential_perturbed |
| geometry_readout_determines_d3 | True | 0 |  |
| q_GR_determines_d3 | True | 0 |  |
| q_GR_determines_d1 | False | 32 | step25_004|step25_016 |
| q_QM_determines_q_GR | False | 5 | step25_004|control_potential_perturbed |
| q_GR_determines_q_QM | False | 32 | step25_004|step25_016 |

The access split is **REALIZED ON THE DECLARED FINITE COARSE FUNCTIONALS**: the Step25 Born audit determines `d1` but not `d3`, while the geometry quotient determines `d3` but not `d1`. In particular, the potential-only pair has an identical Born audit and different geometry mode, and the conjugate pair has identical density/back-reaction geometry and opposite current orientation:

| control | same_density_mode | same_geometry_mode | phase_mode_differs | same_q_QM_fiber | same_q_GR_fiber | geometry_mode_differs | witness |
|---|---|---|---|---|---|---|---|
| complex_conjugate_phase_only | True | True | True |  | True |  | control_phase_original|control_phase_conjugate |
| potential_only | True | False | False | True | False | True | control_potential_base|control_potential_perturbed |

This repairs provenance conditionally rather than deriving a unique mode dictionary. The normalization coordinate is constant (`d0=1`) on the normalized population, and the binning choices remain declared finite coarse-grainings.

## Exhausted coordinate-partition lattice

| quantity | computed value |
|---|---:|
| carrier states | 16 |
| coordinate-subset partitions | 16 |
| unordered distinct pairs | 120 |
| incomparable pairs | 55 |
| nested pairs | 65 |
| meet/join closure size | 16 |

`q_QM=P_d0_d1_d2` and `q_GR=P_d0_d2_d3` are one of exactly **55 incomparable unordered pairs** in this declared class. Their two directed obstruction counts are `8` and `8`. All 65 nested pairs are explicit controls in the same exhaustive table; nesting is common, not a specially chosen exception.

## Computed F24-shape competitors

| family | G_stability | G_control_QM | G_control_GR | G_audit | G_nosmuggle | QM_obstruction_pairs | GR_obstruction_pairs | partition_equivalent_to_L | reconciles | computed_status |
|---|---|---|---|---|---|---|---|---|---|---|
| MemoryLayer | True | True | True | True | True | 0 | 0 | True | True | reconciles_but_partition_equivalent_to_L |
| HiddenUpstreamRole | True | True | False | True | True | 0 | 8 | False | False | fails_endpoint_control |
| BridgeMediatedRole | True | True | True | True | True | 0 | 0 | True | True | reconciles_but_partition_equivalent_to_L |
| BudgetedRole | True | True | False | True | True | 0 | 8 | False | False | fails_endpoint_control |
| ScopedRole | True | True | False | True | True | 0 | 4 | False | False | fails_endpoint_control |
| CoarsenedRole | True | False | False | True | True | 8 | 8 | False | False | fails_endpoint_control |
| OutsideRoleScope | True | False | False | True | True | 8 | 8 | False | False | fails_endpoint_control |
| BlockedNonClosure | True | True | False | False | True | 0 | 8 | False | False | blocked_nonclosure |
| FusedDuplicateControl | True | True | True | True | False | 0 | 0 | True | False | fails_no_smuggle |

The mechanically generated class contains all 8 official F24 names plus the fused-duplicate control. `BridgeMediatedRole` and the exposed XOR-coded `MemoryLayer` reconcile, but both induce exactly the `L` partition; therefore **no generated competitor is a distinct reconciling partition**. Hidden, budgeted, scoped, coarsened, outside-scope, and blocked maps fail computed endpoint/audit gates. The fused direct sum determines both endpoints but fails `G_nosmuggle` through duplicate columns `d0` and `d2`. This reproduces the substantive “collapse to L or fail” result without literal defeat booleans, while making the Memory collapse explicit.
