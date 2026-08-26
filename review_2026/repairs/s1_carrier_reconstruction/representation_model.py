#!/usr/bin/env python3
"""Conjugation-closed SU(N) representation data for the S1 repair."""

from __future__ import annotations

from typing import Any


DIMENSION_WINDOW = (2, 3, 4)
REPRESENTATION_ALPHABET = (
    "singlet",
    "fund",
    "antifund",
    "sym2",
    "conj_sym2",
    "antisym2",
    "conj_antisym2",
)


def _check_dimension(n: int) -> None:
    if n not in DIMENSION_WINDOW:
        raise ValueError(f"SU(N) dimension outside declared window: {n}")


def _check_rep(rep: str) -> None:
    if rep not in REPRESENTATION_ALPHABET:
        raise ValueError(f"unknown representation: {rep}")


def canonical_rep(rep: str, n: int) -> str:
    """Return the exact dimension-specific isomorphism-class spelling."""
    _check_dimension(n)
    _check_rep(rep)
    if n == 2:
        return {
            "antifund": "fund",
            "antisym2": "singlet",
            "conj_antisym2": "singlet",
            "conj_sym2": "sym2",
        }.get(rep, rep)
    if n == 3:
        return {
            "antisym2": "antifund",
            "conj_antisym2": "fund",
        }.get(rep, rep)
    if n == 4 and rep == "conj_antisym2":
        return "antisym2"
    return rep


def canonical_reps(n: int) -> tuple[str, ...]:
    _check_dimension(n)
    return tuple(dict.fromkeys(canonical_rep(rep, n) for rep in REPRESENTATION_ALPHABET))


def rep_dim(rep: str, n: int) -> int:
    rep = canonical_rep(rep, n)
    if rep == "singlet":
        return 1
    if rep in {"fund", "antifund"}:
        return n
    if rep in {"sym2", "conj_sym2"}:
        return n * (n + 1) // 2
    if rep in {"antisym2", "conj_antisym2"}:
        return n * (n - 1) // 2
    raise AssertionError(rep)


def dynkin_twice(rep: str, n: int) -> int:
    """Return 2T(R), retaining the integer normalization used in the paper code."""
    rep = canonical_rep(rep, n)
    if rep == "singlet":
        return 0
    if rep in {"fund", "antifund"}:
        return 1
    if rep in {"sym2", "conj_sym2"}:
        return n + 2
    if rep in {"antisym2", "conj_antisym2"}:
        return n - 2
    raise AssertionError(rep)


def cubic_anomaly(rep: str, n: int) -> int:
    """Return A(R) with A(fund)=1 and all SU(2) coefficients zero."""
    rep = canonical_rep(rep, n)
    if n == 2 or rep == "singlet":
        return 0
    if rep == "fund":
        return 1
    if rep == "antifund":
        return -1
    if rep == "sym2":
        return n + 4
    if rep == "conj_sym2":
        return -(n + 4)
    if rep == "antisym2":
        return n - 4
    if rep == "conj_antisym2":
        return -(n - 4)
    raise AssertionError(rep)


def conjugate_rep(rep: str, n: int) -> str:
    """Conjugate a representation and return its canonical spelling."""
    rep = canonical_rep(rep, n)
    if rep == "singlet":
        return rep
    if n == 2 and rep in {"fund", "sym2"}:
        return rep
    if rep == "fund":
        return "antifund"
    if rep == "antifund":
        return "fund"
    if rep == "sym2":
        return "conj_sym2"
    if rep == "conj_sym2":
        return "sym2"
    if n == 4 and rep == "antisym2":
        return rep
    if rep == "antisym2":
        return "conj_antisym2"
    if rep == "conj_antisym2":
        return "antisym2"
    raise AssertionError(rep)


def is_self_conjugate(rep: str, n: int) -> bool:
    rep = canonical_rep(rep, n)
    return conjugate_rep(rep, n) == rep


def self_test() -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    canonical_instance_count = 0
    for n in DIMENSION_WINDOW:
        reps = canonical_reps(n)
        for rep in reps:
            canonical_instance_count += 1
            conjugate = conjugate_rep(rep, n)
            checks.append(
                {
                    "check": "conjugate_in_canonical_set",
                    "dimension": n,
                    "rep": rep,
                    "passes": conjugate in reps,
                    "evidence": conjugate,
                }
            )
        for raw_rep in REPRESENTATION_ALPHABET:
            rep = canonical_rep(raw_rep, n)
            conjugate = conjugate_rep(raw_rep, n)
            double_conjugate = conjugate_rep(conjugate, n)
            checks.extend(
                [
                    {
                        "check": "canonicalization_idempotent",
                        "dimension": n,
                        "rep": raw_rep,
                        "passes": canonical_rep(rep, n) == rep,
                        "evidence": f"canonical={rep}",
                    },
                    {
                        "check": "conjugation_involution_on_exact_class",
                        "dimension": n,
                        "rep": raw_rep,
                        "passes": double_conjugate == rep,
                        "evidence": f"bar(bar({raw_rep}))={double_conjugate}; canonical={rep}",
                    },
                    {
                        "check": "conjugate_dimension_equal",
                        "dimension": n,
                        "rep": raw_rep,
                        "passes": rep_dim(conjugate, n) == rep_dim(raw_rep, n),
                        "evidence": f"{rep_dim(raw_rep, n)}={rep_dim(conjugate, n)}",
                    },
                    {
                        "check": "conjugate_dynkin_equal",
                        "dimension": n,
                        "rep": raw_rep,
                        "passes": dynkin_twice(conjugate, n) == dynkin_twice(raw_rep, n),
                        "evidence": f"{dynkin_twice(raw_rep, n)}={dynkin_twice(conjugate, n)}",
                    },
                    {
                        "check": "conjugate_cubic_negated",
                        "dimension": n,
                        "rep": raw_rep,
                        "passes": cubic_anomaly(conjugate, n) == -cubic_anomaly(raw_rep, n),
                        "evidence": f"{cubic_anomaly(raw_rep, n)}->{cubic_anomaly(conjugate, n)}",
                    },
                    {
                        "check": "self_conjugate_cubic_zero",
                        "dimension": n,
                        "rep": raw_rep,
                        "passes": conjugate != rep or cubic_anomaly(raw_rep, n) == 0,
                        "evidence": f"canonical={rep} conjugate={conjugate} A={cubic_anomaly(raw_rep, n)}",
                    },
                ]
            )
    passed = all(bool(row["passes"]) for row in checks)
    return {
        "passes": passed,
        "declared_rep_instances": len(DIMENSION_WINDOW) * len(REPRESENTATION_ALPHABET),
        "canonical_rep_instances": canonical_instance_count,
        "check_count": len(checks),
        "failed_checks": [row for row in checks if not row["passes"]],
        "checks": checks,
    }


def main() -> None:
    result = self_test()
    if not result["passes"]:
        print(f"representation_model.py: FAIL: {result['failed_checks']}")
        raise SystemExit(1)
    print(
        "representation_model.py: PASS: "
        f"declared_rep_instances={result['declared_rep_instances']} "
        f"canonical_rep_instances={result['canonical_rep_instances']} "
        f"checks={result['check_count']}"
    )


if __name__ == "__main__":
    main()
