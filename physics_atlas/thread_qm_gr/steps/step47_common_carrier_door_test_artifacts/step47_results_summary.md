# Step 47 Results Summary

## Honest Grade / Verdict First

Verdict: the common-carrier premise is LANDED * GROUND (conditional) -- grounded as the down-shadow of the semiclassical co-sourcing layer. This is a recognition-mode landing, not an unconditional derivation, and not "merely relocation": the premise is not derivable within the QM-GR layer, so the valid landing is relocation up the tower to a named source-warrant.

The door-test does not find an SBT-internal law that forces QM and GR to share a carrier. The formal verdict remains `COMMON_CARRIER_IS_RECOGNITION_SOURCE_WARRANTED`: F37, F51, FoEC, and SAU give the form, criterion, or license for a common carrier once one is warranted, but they do not derive the existence of the shared carrier for this physical pair. The common-carrier premise is therefore a named recognition source, warranted by semiclassical co-sourcing: one field `psi` has both the Born readout `|psi|^2` and the stress-energy readout `T[psi]`.

GROUND caveats: (i) source-warrant: the source is semiclassical co-sourcing, extended by Step26's back-reaction loop; (ii) theorem-strength: this is a recognition-source landing, not a proof from SBT alone.

This is not arbitrary modeling, but it is also not an SBT-only theorem. The warrant is known semiclassical co-sourcing, checked in Step25 independently of the Step47 door-test and extended in Step26 to matter-sourced geometry via `V[psi] = background + kappa*T00[psi]`.

The per-law forces-vs-form classification (F37 / F51 / FoEC / SAU) is a structural reading of the framework sources, not a line-by-line computation from the texts; the computed teeth are the two can-fail controls: the complementary pair gives no manufactured carrier, and the non-co-sourcing control removes the warrant. This is a structural audit plus recognition-source GROUND landing, not a decisive proof.

## Toy

The main access pair mirrors Step18:

- `q_QM = (d0,d1,d2)`.
- `q_GR = (d0,d2,d3)`.
- `L_joint = (d0,d1,d2,d3)`.

Computed joint residuals:

- QM residual: `0`.
- GR residual: `0`.
- admissible joint: `True`.

## Forces-vs-Form Test

| Law | Gives form/criterion | Forces existence | Computed evidence | Door-test result |
|---|---:|---:|---|---|
| `F37_complementarity_non_joint_access` | `True` | `False` | co-sourcing pair admissible_joint=True; complementary_control_commutator_residual=0.707106781187; complementary_control_admissible_joint=False | `FORM_NOT_EXISTENCE` |
| `F51_unification_common_refinement` | `True` | `False` | L refinement residuals qm=0, gr=0; complementary_control_has_joint=False | `FORM_NOT_EXISTENCE` |
| `FoEC_universal_quotient_calculus` | `True` | `False` | individual_carrier_QM=True; individual_carrier_GR=True; shared_carrier_requires_extra_warrant=True | `FORM_NOT_EXISTENCE` |
| `SAU_non_descending_object_discipline` | `True` | `False` | L_single_psi_sources_both=True; non_cosourced_control_pass=False; control_max_stress_residual=0.380602660378 | `LICENSE_NOT_DERIVATION` |

## Can-Fail Controls

| Control | Result | Evidence |
|---|---|---|
| Complementary noncommuting pair | no manufactured shared carrier | commutator residual `0.707106781187`; admissible joint `False` |
| Non-co-sourcing independent field | no common-carrier warrant | Step25 control max stress residual `0.380602660378`; non-co-sourced control pass `False` |

## Recognition Warrant

The recognition source is semiclassical co-sourcing, not the existence of the Step18 finite `L` itself. Step25 computes:

- `L_single_psi_sources_both = True`.
- `L_max_born_residual = 0`.
- `L_max_stress_residual = 0`.
- `non_co_sourced_control_pass = False`.

Step26 extends the warrant past stress-energy toward matter-sourced geometry:

- source: `steps/step26_semiclassical_dynamics_artifacts/step26_schema.json`.
- `potential_sourced_from_T00 = True`.
- `consistent_coupling_converged = True`.
- `consistent_fixed_point_residual = 3.4936318023e-16`.

Removing co-sourcing removes the warrant, which is why the premise is not arbitrary and not forced by the abstract laws alone.

## Frame-Transfer Residual

The residual is narrowed: the warrant reaches QM's Born readout, stress-energy, and matter-sourced geometry in the finite semiclassical back-reaction toy. What remains open is the free gravitational degrees of freedom, the full quantum-gravity sector, and trans-semiclassical survival of the common carrier. It is not accurate to say that curvature in general is wholly outside the warrant.
