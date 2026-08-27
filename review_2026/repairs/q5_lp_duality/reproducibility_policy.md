# Q5 reproducibility policy

Q5 separates exact discrete evidence from platform-sensitive floating numerical evidence. This
changes only the replay contract; it does not change any computation, artifact, tolerance used by
the scientific predicates, or verdict.

## Artifact contracts

| artifact | class | validator contract |
|---|---|---|
| `q5_carrier_edges.csv` | EXACT | byte-identical |
| `q5_region_duality.csv` | EXACT | byte-identical |
| `q5_edge_shadow_prices.csv` | EXACT | byte-identical |
| `q5_lp_matrices.json` | EXACT | byte-identical |
| `q5_schema.json` | EXACT | byte-identical |
| `DESIGN.md` | EXACT | byte-identical |
| `q5_linear_response.csv` | FLOAT | exact header, row order, rational/integer/text fields; declared float fields compared numerically |
| `q5_composition_probe.csv` | FLOAT | exact header, row order, rational/integer/text fields; declared float fields compared numerically |
| `q5_results.json` | FLOAT | exact key order, shape, strings, booleans, integers, verdicts, and unlisted numbers; declared float paths compared numerically |
| `RESULTS.md` | FLOAT | exact non-numeric text and numeric-token placement; integers exact and floating tokens compared numerically |

## Declared numerical tolerances

| artifact / fields | absolute tolerance | relative tolerance |
|---|---:|---:|
| `q5_linear_response.csv`: `recontracted_state_delta_S`, `response_error`, `can_fail_control_delta_S` | `5e-10` | `1e-10` |
| `q5_composition_probe.csv`: `glued_born_direct`, `born_min_plus_components` | `5e-10` | `1e-10` |
| `q5_results.json`: `/linear_response/max_absolute_error` | `5e-10` | `1e-10` |
| `q5_results.json`: `/composition/born_i3`, `/composition/area_i3` | `5e-12` | `1e-10` |
| `RESULTS.md`: floating numeric tokens | `5e-10` | `1e-10` |

The response allowance is below one part in 10^9 at unit scale and covers the independently
observed cross-platform drift of approximately `1.78e-10`; it is also 100,000 times below the
`5e-5` response decision threshold. The tighter MMI allowance covers the observed `born_i3` drift
of approximately `4.44e-16` and is 200 times below the `1e-9` MMI classification boundary in
`q5_lp_duality.py:473`, so the MMI classification is preserved under the allowance. These
differences arise from SVD/BLAS and floating contraction order across numerical environments; the
exact graph enumeration and rational LP path do not use these tolerances.

The validator includes force controls matching both reported drift shapes: a synthetic `1.78e-10`
linear-response CSV variation and a `4.44e-16` `born_i3` JSON variation must pass. A `1e-6`
variation in the verdict-adjacent maximum-response-error field must fail. The controls alter only
in-memory comparison payloads and never rewrite the retained artifacts.
