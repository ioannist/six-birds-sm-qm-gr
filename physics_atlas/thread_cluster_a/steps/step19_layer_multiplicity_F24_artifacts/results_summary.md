# Step 19 Results Summary: F24/F47 Layer Multiplicity

## Exact Quotient and Role

- Access quotient `q`: content-selection equivalence class over `gauge_code, rep_code, n_gen, texture_code, uv_code, vacuum_code, anomaly_free, gauge_rep_consistent, generation_chirality_ok, texture_ok, uv_consistent`.
- Role readout `s`: F47 scale/naturalness readout from the scale ratio and radiative sensitivity.

## Role Obstruction

- `|O_s|` unordered q-fiber pairs: `5760`.
- Descends through q: `False`.
- RoleSplit: `True`.

The role split is computed directly: there are q-equal worlds with different scale/naturalness readouts.

## F24 Resolution

Selected resolution: `BudgetedRole`.

MemoryLayer is not selected: the scale-only readout does not form an independent closed access quotient because the role uses the content-dependent radiative score. The role is instead priced as a finite naturalness budget on the same closure.

The other F24 families are ruled out in `f24_resolution_step19.csv`.

## F47 Small Selector Region

- `mu_total`: `8640`.
- `mu(Sigma)`: `342`.
- `mu(Sigma)/mu_total`: `0.039583333333`.
- `theta`: `0.05`.
- `Small(Sigma)`: `True`.
- `Realized`: `True`.

## Controls

- Known descending control obstruction: `0`.
- Known splitting control obstruction: `8640`.

The controls distinguish descending from splitting roles.

## Structural Dependency Note

The Step-18 mutual information is a structural dependency statistic. It is not a TDGate-certified cause relation: no intervention/control/effect-threshold gate was run.

## Verdict

`RoleSplit -> BudgetedRole`, with F47 small-selector-region fine-tuning. This is one closure with a budgeted scale role, not an independently closed scale layer.
