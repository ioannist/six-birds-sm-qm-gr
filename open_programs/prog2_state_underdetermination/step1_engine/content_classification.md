# Content classification

| object | classification | role |
|---|---|---|
| `state_entropy.py` | GENERATED NUMERICAL ENGINE | state-only complex128/SVD reduced-density-matrix entropy path with truncation accountability |
| `tensor_engine.py` | GENERATED ENGINE | explicit dense tensor construction and contraction |
| `gauge_library.py` | GENERATED ENGINE | certified state-preserving/local-unitary presentation moves |
| P1-v3 survivor topology and weights | IMPORTED, HASH-PINNED | topology selection and source provenance only |
| Step41/42/44 scripts | READ-ONLY, HASH-PINNED REFERENCES | sound contraction/entropy/MMI patterns inspected; not executed by the engine |
| integer bond dimensions D=2,3,4 | DECLARED STEP-1 PARAMETERS | tractability census; not inferred from generic cut capacities |
| heterogeneous edge dimensions 2 and 3 | DECLARED STEP-1 CHECK | verifies that bond dimensions need not be uniform |
| control tensor seeds 7101/7102/7201 | DECLARED DETERMINISTIC PARAMETERS | small controls only |
| survivor tensor namespace `prog2_step2_tensor_seed_v1` | DECLARED INDEPENDENT PARAMETER | hash payload excludes P1 capacity seed |
| `legacy_seed_history_step1.csv` | FROZEN, HASH-PINNED HISTORY | before-fix digests only; never feeds tensor construction |
| entropy vectors and residuals | COMPUTED | derived exclusively from contracted boundary states |
| min-cut values | NOT USED / NOT PRODUCED | deliberately absent from the entropy path |
