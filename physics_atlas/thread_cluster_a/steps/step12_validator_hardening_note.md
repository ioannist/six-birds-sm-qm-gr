# Cluster A Step 12 Validator Hardening Note

## Scope

This is an infrastructure-only hardening pass for `physics_atlas/thread_cluster_a`.

No scientific artifact, computed number, claim, grade, theorem statement, carrier, or construction result was changed. The edits are limited to validator entrypoints, validator verification notes in `results_summary.md`, and the new top-level self-check runner.

## Interface

Every `run_stepN.py` validator for Steps 1-11 now exposes the same command-line interface:

- `python3 run_stepN.py` or `python3 run_stepN.py --self`: validate only that step's own artifacts.
- `python3 run_stepN.py --chain`: run prior validators once each in order, each in `--self` mode, then run the current step's self-check.

Default mode is non-recursive and deterministic.

Self mode uses in-process execution for the step-local build script where applicable. It does not shell out to prior validators. Chain mode is the only mode that shells out to other validators, and it invokes each prior step exactly once with `--self`.

## Review Runner

Added:

```text
steps/run_all_selfcheck.py
```

This is the advertised non-recursive review command. It runs Steps 1-11 in self mode and prints a PASS/FAIL table.

Command run from the thread root:

```text
python3 steps/run_all_selfcheck.py
```

Observed output:

```text
Cluster A self-check table
step,status
step1,PASS
step2,PASS
step3,PASS
step4,PASS
step5,PASS
step6,PASS
step7,PASS
step8,PASS
step9,PASS
step10,PASS
step11,PASS
```

## Additional Verification

All individual default validators pass:

```text
python3 steps/stepN_*/run_stepN.py
```

All explicit chain validators pass:

```text
python3 steps/stepN_*/run_stepN.py --chain
```

The previously fragile Step 7 chain was explicitly run and passed:

```text
python3 steps/step7_consolidated_statement_artifacts/run_step7.py --chain
```

Observed output:

```text
run_step7.py: PASS
```

Static self-mode check: every `run_self()` body in Steps 1-11 was inspected and contains no `subprocess.run` call, so recursion is not reachable under self mode.

## Organizational Verdict

Validator hardening complete. The Cluster A validation interface is now uniform, non-recursive by default, and has an explicit deterministic chain mode. This step is organizational-only.
