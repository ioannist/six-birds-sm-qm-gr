# S6-ABLATION design: dimension-generic record grammar

## Scope and pinned carrier

This ablation reads no `physics_atlas/` artifact at runtime. It imports the accepted S1-v2
carrier implementation from `../s1_carrier_reconstruction/` after checking fixed SHA-256
constants for `representation_model.py`, `carrier_chain.py`, and `carrier_chain_v2.py`.
The imported computation supplies all 52 chirality-faithful structures and all 12 admissible
singleton `(C,phi)` branches. The 44 structures with no singleton branch contribute one typed
`undefined_no_singleton_branch` row each, with the record substrate set false. Thus the finite
evaluation table has 56 rows and never silently calls a no-branch structure clean or breaking.

The published comparison is
`physics_atlas/thread_cluster_a/steps/step57_mode_b_record_stability_descent_artifacts/record_stability_descent_step57.py`:

- lines 17-18 fix `MIN_RECORD_TOKENS=2` and `WEAK_SHIFT_UNIT=3`;
- lines 71-75 split a weak fundamental by the literal shifts `q+3,q-3`;
- lines 92-110 treat `antisym2` as a dual only at dimension three;
- lines 118-148 form mesons and exactly three-member baryons.

Those files remain read-only. This directory implements the ablation independently.

## Generic grammar

The record substrate is the final factor in the carrier dimension tuple, matching Step 57's
substrate-factor convention. Its original carrier dimension is the epsilon rank `N`; hence an
SU(4) carrier is explicitly tested with four-fold fundamental/antifundamental epsilon tokens.
This is distinct from the later scalar-shadow residual label and is the interpretation requested
by the SU(4) ablation.

1. **Actual duality.** Every representation is canonicalized by the pinned S1-v2 representation
   model. Its dual is `conjugate_rep(r,N)`. No `dimension==3` alias rule is present.
2. **Component weights.** For each spectator factor, the code constructs representation weights
   under the standard integral Cartan projection `diag(N-1,N-3,...,-N+1)`. Component charge is
   the declared U(1) charge plus the sum of these derived weights. In particular, an SU(2)
   fundamental splits by `+1,-1`, not by a fixed `+3,-3`.
3. **Mesonic tokens.** A neutral pair `r + conjugate(r)` is one mesonic token basis element.
4. **Baryonic tokens.** Exactly `N` fundamentals or exactly `N` antifundamentals saturating one
   epsilon tensor form baryonic basis elements when their component charges sum to zero.
5. **Mixed tokens.** Exterior-power representations may jointly saturate one epsilon tensor when
   their covariant ranks sum to `N` (or their dual ranks do). Pure baryons and two-body mesons are
   removed from this class, so the three reported bases are disjoint.

Token identity retains field occurrence, spectator weight, exact substrate representation, and
component charge. Distinguishability uses exact canonical representation spellings; it fails only
if distinct spellings survive as aliases of one canonical representation. No such alias occurs
on the repaired carrier.

## Record predicate and thresholds

The three conjuncts remain persistence/substrate, capacity, and distinguishability. The reference
threshold remains the published minimal value two. Thresholds one through four are computed as
an explicit sensitivity table. No threshold is selected from a desired clean result.

The clean cross-table uses the S1-v2 branch verdict exactly: `clean_evaluated`,
`breaking_evaluated`, or `undefined_no_singleton_branch`. Three logical readings are reported:

- **branch pointwise:** every selected `(C,phi)` satisfying RS must itself be clean;
- **structure universal:** `(all phi RS(C,phi)) => (all phi Clean(C,phi))`;
- **structure existential:** `(exists phi RS(C,phi)) => (exists phi Clean(C,phi))`.

The 44 empty branch domains are typed undefined and excluded from both structure quantifiers;
they are not counted as vacuous successes.
