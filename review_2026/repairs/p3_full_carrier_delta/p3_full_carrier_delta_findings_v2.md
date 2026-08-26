# P3-REPAIR-1b: factor-labelled product-confinement findings

## Binary stability

All 11,990 historical rows were re-evaluated. The complete-product projection changes the clean/breaking/undefined binary for **0 rows**. Moved carrier IDs: none.

| RS status | clean evaluated | breaking evaluated | Delta undefined | Total |
|---|---:|---:|---:|---:|
| RS_false | 9222 | 918 | 1826 | 11966 |
| RS_true | 24 | 0 | 0 | 24 |

The headline counts therefore remain RS=24, RS and breaking=0, breaking total=918, clean total=9,246, and Delta undefined=1,826.

## Product-confinement calculation

Every residual nonabelian factor is a separate coordinate of `pi_conf_product`. Every massless generator and transition vector carries its source `factor_label`. A massive transition vector pairs only with massless generators whose complete product-sector tuple is equal. This prevents a leak from an active residual SU(2) being attributed to an untouched SU(3).

There are 1203 multi-confinement carrier rows and 2406 residual-factor rows in the detailed table.

| Legacy pairs | Product-faithful pairs | Carrier rows |
|---:|---:|---:|
| 0 | 0 | 553 |
| 12 | 12 | 200 |
| 32 | 12 | 88 |
| 48 | 48 | 222 |
| 60 | 12 | 88 |
| 90 | 48 | 52 |

| Factor label | Original factor | Scalar rep | State | Residual | Rows | Pair total | Witness total |
|---|---|---|---|---|---:|---:|---:|
| factor0 | SU(2) | singlet | untouched | SU(2) | 647 | 0 | 0 |
| factor0 | SU(3) | antifund | active_broken_to_residual | SU(2) | 132 | 1584 | 528 |
| factor0 | SU(3) | singlet | untouched | SU(3) | 264 | 0 | 0 |
| factor0 | SU(4) | antifund | active_broken_to_residual | SU(3) | 20 | 960 | 120 |
| factor0 | SU(4) | antisym2 | active_broken_to_residual | SU(3) | 6 | 288 | 36 |
| factor0 | SU(4) | singlet | untouched | SU(4) | 134 | 0 | 0 |
| factor1 | SU(3) | antifund | active_broken_to_residual | SU(2) | 244 | 2928 | 976 |
| factor1 | SU(3) | singlet | untouched | SU(3) | 249 | 0 | 0 |
| factor1 | SU(4) | antifund | active_broken_to_residual | SU(3) | 180 | 8640 | 1080 |
| factor1 | SU(4) | antisym2 | active_broken_to_residual | SU(3) | 68 | 3264 | 408 |
| factor1 | SU(4) | singlet | untouched | SU(4) | 462 | 0 | 0 |

Per-carrier, per-factor counts are recorded in `p3_full_carrier_delta_multiconfinement_factors_v2.csv`.

## Surviving typed claim

`RS(C) => C in Dom(Delta_fact) AND Delta_fact(C) = empty` survives on all 24 record-stable rows.

**Evidence grade: CONDITIONAL FINITE-TOY PROXY ENUMERATION DIAGNOSTIC.** It is conditional on the proxy higher-layer breaking/scalar choice, inherits the published 11,990-row carrier and its representation/enumeration limitations, and tests the record-grammar shape encoded by the frozen Step-57 machinery rather than a derived continuum record theorem. The factor-labelled repair removes the product-confinement bookkeeping defect but does not remove those caveats or promote the statement beyond this finite diagnostic.

No-confinement rows retain the typed value `delta_undefined_no_confinement`; none is record-stable.

## Validator coverage

The version-2 validator independently rederives all 10164 Delta-defined rows, including all 24 RS rows, all 918 breaking rows, and all 1203 multi-confinement rows. It also checks all 1826 no-confinement rows as negative controls. This replaces the historical 32-row arbitrary sample.
