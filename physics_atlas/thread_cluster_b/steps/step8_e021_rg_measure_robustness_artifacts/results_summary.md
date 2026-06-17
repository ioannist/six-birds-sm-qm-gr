# Step 8 Results Summary

## Orientation

Step 8 replaces the hand-built Step 3 selection pair with a structured finite toy: a moduli grid, deterministic toy RG flow, and a measure/relaxation score that selects a realized modulus.

## RG / Measure Toy

The bare UV Sigma is `(cutoff, spectrum_code, g_uv, beta0)`. The RG flow computes `g_IR` by a beta-function recurrence. The measure score selects `selected_phi_star` from the moduli grid `[-2.0, -1.0, 0.0, 1.0, 2.0]`. The realized `Lambda` is a function of the bare UV and the selected modulus.

## Non-Factorization

- `Lambda_from_bare_UV`: obstruction `4`, witnesses `A_left-A_right;A_left-A_far_right;A_right-A_far_right;B_center-B_left`.
- `Lambda_from_UV_selected_phi`: obstruction `0`.
- `phi_star_from_bare_UV`: obstruction `4`, witnesses `A_left-A_right;A_left-A_far_right;A_right-A_far_right;B_center-B_left`.
- `g_IR_from_bare_UV`: obstruction `0`.
- `no_selection_Lambda_from_bare_UV`: obstruction `0`.

## Controls

The RG-derived control passes: `g_IR` descends from the bare UV with obstruction `0`.

The no-selection control passes: a Lambda-like readout with no modulus/measure residue descends from the bare UV with obstruction `0`.

Selection relocation passes: once `selected_phi_star` is included in Sigma, `Lambda` descends with obstruction `0`, while `selected_phi_star` itself remains non-descending from bare UV with obstruction `4`.

## Verdict

`E021_rg_measure_robustness_established`.

On this finite RG/measure toy, `Lambda` stays non-descending from the bare UV. The adversarial Sigma that includes the selected modulus makes `Lambda` descend, but the non-descendingness relocates to the selection. The RG running is genuinely UV-derived, so the test has teeth. The toy supplies no physical value or real selection mechanism.
