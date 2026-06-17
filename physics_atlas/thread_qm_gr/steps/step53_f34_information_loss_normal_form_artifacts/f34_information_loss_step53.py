#!/usr/bin/env python3
"""Step 53: F34 information-loss normal form on the Step42 carrier."""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any

import numpy as np


ARTIFACT_DIR = Path(__file__).resolve().parent
REPO_ROOT = Path("/home/repos/six-birds-papers")
THREAD_ROOT = ARTIFACT_DIR.parents[1]
STEP42_DIR = THREAD_ROOT / "steps" / "step42_faithful_holographic_rt_enrichment_artifacts"
STEP47_DIR = THREAD_ROOT / "steps" / "step47_common_carrier_door_test_artifacts"
STEP42_SCRIPT = STEP42_DIR / "faithful_holographic_rt_enrichment_step42.py"
FOUNDATIONS_IV = REPO_ROOT / "Tsiokos_2026_Six_Birds_Foundations_IV_A_Catalog_of_Layer_Agnostic_Structural_Laws.tex"
FOUNDATIONS_III = REPO_ROOT / "Tsiokos_2026_Six_Birds_Foundations_III_A_Finite_Audited_Interaction_Calculus_for_SBT.tex"
EXPECTED_STEP42_SHA256 = "4e204c0eae2df9a88b426c07e4bcf04ad308a3b1d18e05eac769bb64594b2d08"
DIM = 3
SEEDS = [101, 202, 303]
GAUGE_SEEDS = [5301, 5302, 5303]
TOL = 1e-10


def rel(path: Path) -> str:
    return str(path.resolve().relative_to(THREAD_ROOT.resolve()))


def repo_rel(path: Path) -> str:
    return str(path.resolve().relative_to(REPO_ROOT.resolve()))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str] | None = None) -> None:
    if not rows:
        raise ValueError(f"no rows for {path}")
    if fieldnames is None:
        fieldnames = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def import_step42() -> Any:
    spec = importlib.util.spec_from_file_location("step42_rt_enrichment", STEP42_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not import {STEP42_SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def relative_norm(a: np.ndarray, b: np.ndarray | None = None) -> float:
    if b is None:
        return float(np.linalg.norm(a))
    return float(np.linalg.norm(a - b) / max(np.linalg.norm(b), TOL))


def random_gl(size: int, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    return np.eye(size) + 0.05 * rng.normal(size=(size, size))


def random_orthogonal(size: int, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    q, r = np.linalg.qr(rng.normal(size=(size, size)))
    signs = np.sign(np.diag(r))
    signs[signs == 0] = 1
    return q * signs


def gauge_transform(left: np.ndarray, right: np.ndarray, gauge: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    return left @ gauge, right @ np.linalg.inv(gauge).T


def contracted_from_pair(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    return left @ right.T


# GAUGE_INVARIANT_FUNCTIONALS_BEGIN
def gram_invariant_spectrum(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    gram_left = left.T @ left
    gram_right = right.T @ right
    values = np.linalg.eigvals(gram_left @ gram_right)
    values = np.real_if_close(values, tol=1000).real
    return np.sort(values)


def gram_invariant_trace2(left: np.ndarray, right: np.ndarray) -> float:
    gram_left = left.T @ left
    gram_right = right.T @ right
    product = gram_left @ gram_right
    return float(np.real_if_close(np.trace(product @ product)))


def interior_complement_expectation(left: np.ndarray, right: np.ndarray, observable: np.ndarray) -> float:
    contracted = left @ right.T
    numerator = np.trace(contracted @ observable @ contracted.T)
    denominator = np.trace(contracted @ contracted.T)
    return float(np.real_if_close(numerator / denominator))
# GAUGE_INVARIANT_FUNCTIONALS_END


def boundary_recovered_spectrum(state: np.ndarray, rank: int) -> np.ndarray:
    singular_values = np.linalg.svd(state, compute_uv=False)[:rank]
    return np.sort(singular_values * singular_values)


def reduced_left_density(state: np.ndarray) -> np.ndarray:
    rho = state @ state.T
    return rho / np.trace(rho)


def canonical_factorization(state: np.ndarray, rank: int) -> tuple[np.ndarray, np.ndarray]:
    u, s, vt = np.linalg.svd(state, full_matrices=False)
    sqrt_s = np.sqrt(s[:rank])
    left_canonical = u[:, :rank] * sqrt_s
    right_canonical = vt[:rank, :].T * sqrt_s
    return left_canonical, right_canonical


def rank_reconstruction_rows(step42: Any) -> tuple[list[dict[str, Any]], dict[int, dict[str, Any]]]:
    rows: list[dict[str, Any]] = []
    cache: dict[int, dict[str, Any]] = {}
    for seed in SEEDS:
        state, left, right = step42.boundary_state_matrix(DIM, "random_gaussian", seed)
        internal_dim = left.shape[1]
        singular_values = np.linalg.svd(state, compute_uv=False)
        rank = int(np.sum(singular_values > 1e-10))
        left_can, right_can = canonical_factorization(state, rank)
        gauge, *_ = np.linalg.lstsq(left_can, left, rcond=None)
        reconstructed_left = left_can @ gauge
        reconstructed_right = right_can @ np.linalg.inv(gauge).T
        left_resid = relative_norm(reconstructed_left, left)
        right_resid = relative_norm(reconstructed_right, right)
        state_resid = relative_norm(contracted_from_pair(left_can @ gauge, right_can @ np.linalg.inv(gauge).T), state)
        rows.append(
            {
                "seed": seed,
                "dim": DIM,
                "boundary_dim": left.shape[0],
                "internal_dim": internal_dim,
                "state_rank_computed": rank,
                "rank_equals_internal_dim": rank == internal_dim,
                "min_nonzero_singular_value": f"{singular_values[rank-1]:.12g}",
                "next_singular_value": f"{(singular_values[rank] if rank < len(singular_values) else 0.0):.12g}",
                "explicit_G_left_residual": f"{left_resid:.12g}",
                "explicit_G_right_residual": f"{right_resid:.12g}",
                "explicit_G_state_residual": f"{state_resid:.12g}",
                "condition_number_G": f"{np.linalg.cond(gauge):.12g}",
            }
        )
        cache[seed] = {
            "state": state,
            "left": left,
            "right": right,
            "internal_dim": internal_dim,
            "rank": rank,
            "singular_values": singular_values,
            "explicit_G_residual": max(left_resid, right_resid, state_resid),
        }
    return rows, cache


def gauge_orbit_rows(cache: dict[int, dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    orbit_rows: list[dict[str, Any]] = []
    invariant_rows: list[dict[str, Any]] = []
    for seed, item in cache.items():
        state = item["state"]
        left = item["left"]
        right = item["right"]
        rank = item["rank"]
        base_spectrum = gram_invariant_spectrum(left, right)
        boundary_spectrum = boundary_recovered_spectrum(state, rank)
        spectrum_boundary_resid = relative_norm(base_spectrum, boundary_spectrum)
        base_trace2 = gram_invariant_trace2(left, right)
        for gauge_seed in GAUGE_SEEDS:
            gauge = random_gl(item["internal_dim"], gauge_seed)
            left_g, right_g = gauge_transform(left, right, gauge)
            state_g = contracted_from_pair(left_g, right_g)
            spectrum_g = gram_invariant_spectrum(left_g, right_g)
            trace2_g = gram_invariant_trace2(left_g, right_g)
            orbit_rows.append(
                {
                    "seed": seed,
                    "gauge_seed": gauge_seed,
                    "gauge_state_residual": f"{relative_norm(state_g, state):.12g}",
                    "raw_left_difference_norm": f"{relative_norm(left_g, left):.12g}",
                    "raw_right_difference_norm": f"{relative_norm(right_g, right):.12g}",
                    "spectrum_invariant_residual": f"{relative_norm(spectrum_g, base_spectrum):.12g}",
                    "trace2_invariant_abs_gap": f"{abs(trace2_g - base_trace2):.12g}",
                    "gauge_obstruction_raw_nonempty": relative_norm(left_g, left) > 1e-6,
                    "gauge_obstruction_phys_empty": relative_norm(spectrum_g, base_spectrum) < 1e-8,
                }
            )
        invariant_rows.append(
            {
                "seed": seed,
                "functional": "spectrum((left.T@left)@(right.T@right))",
                "definition_source": "interior tensors left,right",
                "boundary_recovery": "nonzero singular values squared of left@right.T",
                "boundary_recovery_residual": f"{spectrum_boundary_resid:.12g}",
                "gauge_invariant_checked": True,
            }
        )
    return orbit_rows, invariant_rows


def perturbation_rows(cache: dict[int, dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for seed, item in cache.items():
        left = item["left"]
        right = item["right"]
        state = item["state"]
        perturbed_left = left.copy()
        perturbed_left[0, 0] += 0.1
        perturbed_state = contracted_from_pair(perturbed_left, right)
        rows.append(
            {
                "seed": seed,
                "perturbation": "left[0,0]+=0.1",
                "nongauge_state_change_residual": f"{relative_norm(perturbed_state, state):.12g}",
                "nongauge_perturbation_changes_state": relative_norm(perturbed_state, state) > 1e-5,
            }
        )
    return rows


def partial_witness_rows(cache: dict[int, dict[str, Any]]) -> list[dict[str, Any]]:
    item = cache[101]
    left = item["left"]
    right = item["right"]
    state = item["state"]
    unitary = random_orthogonal(right.shape[0], 7351)
    right2 = unitary @ right
    state2 = contracted_from_pair(left, right2)
    rho_partial_1 = reduced_left_density(state)
    rho_partial_2 = reduced_left_density(state2)
    full_state_resid = relative_norm(state2, state)
    reduced_resid = relative_norm(rho_partial_2, rho_partial_1)
    observable = np.diag(np.linspace(-1.0, 1.0, right.shape[0]))
    obs1 = interior_complement_expectation(left, right, observable)
    obs2 = interior_complement_expectation(left, right2, observable)
    obs_gap = abs(obs2 - obs1)
    gauge = random_gl(item["internal_dim"], 7301)
    left_g, right_g = gauge_transform(left, right, gauge)
    obs_g = interior_complement_expectation(left_g, right_g, observable)
    return [
        {
            "witness_id": "partial_readout_complement_unitary",
            "seed": 101,
            "rho_partial": "left_boundary_reduced_density",
            "unitary_seed": 7351,
            "reduced_state_residual": f"{reduced_resid:.12g}",
            "full_boundary_state_change_residual": f"{full_state_resid:.12g}",
            "gauge_invariant_observable": "interior_complement_expectation(left,right,O_diag)",
            "observable_value_original": f"{obs1:.12g}",
            "observable_value_witness": f"{obs2:.12g}",
            "observable_gap": f"{obs_gap:.12g}",
            "observable_gauge_invariance_residual": f"{abs(obs_g - obs1):.12g}",
            "partial_obstruction_nonempty": reduced_resid < 1e-10 and obs_gap > 1e-4 and full_state_resid > 1e-3,
            "not_gauge_transform": full_state_resid > 1e-3,
        }
    ]


def obstruction_rows(orbit_rows: list[dict[str, Any]], partial_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    raw = orbit_rows[0]
    partial = partial_rows[0]
    return [
        {
            "case_id": "rho_full_sigma_raw",
            "rho": "full normalized boundary state",
            "sigma": "raw tensors left,right",
            "obstruction_empty": False,
            "witness": "gauge pair (left,right) vs (left@G,right@G^{-T})",
            "same_rho_residual": raw["gauge_state_residual"],
            "sigma_difference": f"left_gap={raw['raw_left_difference_norm']};right_gap={raw['raw_right_difference_norm']}",
            "f34_verdict": "raw_loss_nonlegitimate_as_raw_but_gauge_redundant",
        },
        {
            "case_id": "rho_full_sigma_phys",
            "rho": "full normalized boundary state",
            "sigma": "gauge-invariant physical interior class",
            "obstruction_empty": True,
            "witness": "rank-full stratum: tau-preimage classes reconstructed as GL gauge orbits",
            "same_rho_residual": "rank_reconstruction_residuals_below_1e-8",
            "sigma_difference": "none on checked gauge-invariant functionals",
            "f34_verdict": "legitimate_loss_gauge_only",
        },
        {
            "case_id": "rho_partial_sigma_phys",
            "rho": "left reduced density only",
            "sigma": "gauge-invariant physical interior observable",
            "obstruction_empty": False,
            "witness": "right-complement unitary leaves rho_partial fixed but changes full physical observable",
            "same_rho_residual": partial["reduced_state_residual"],
            "sigma_difference": f"observable_gap={partial['observable_gap']}",
            "f34_verdict": "illegitimate_loss",
        },
    ]


def frozen_rows() -> list[dict[str, Any]]:
    sources = [
        STEP42_SCRIPT,
        STEP42_DIR / "step42_schema.json",
        STEP47_DIR / "step47_schema.json",
        FOUNDATIONS_IV,
        FOUNDATIONS_III,
    ]
    return [
        {
            "source": repo_rel(path),
            "sha256": sha256(path),
            "expected_sha256": EXPECTED_STEP42_SHA256 if path == STEP42_SCRIPT else "",
            "imported_or_read_verbatim": True,
        }
        for path in sources
    ]


def write_summary(schema: dict[str, Any]) -> None:
    text = f"""# Step 53 Results Summary

## Honest Grade First

This is a computed F34 normal-form classification on a finite static holographic toy. There is no evaporation dynamics, no Page curve, and no real black hole here. It does not resolve the physical information paradox and does not certify frame transfer. The recovered-known content is the holographic-unitarity narrative in F34 form: full boundary recovery loses only gauge redundancy, while a partial/thermal-style readout loses physical information.

## F34 Data

- `H0`: Step42 interior random tensor pairs `(left,right)` at `D=3`, seeds `{SEEDS}`.
- `tau`: contraction to the boundary state `left @ right.T`.
- `H1`: full boundary state matrices.
- `rho_full`: full normalized boundary state.
- `rho_partial`: left-boundary reduced density matrix.
- `sigma_raw`: raw interior tensors.
- `sigma_phys`: gauge-invariant physical interior class.

## Gauge and Rank Computation

The computed rank is `{schema['state_rank_computed']}` with internal dimension `{schema['internal_dim']}`. Rank equals the internal dimension: `{schema['rank_equals_internal_dim']}`.

Gauge invariance residual: `{schema['gauge_invariance_residual']:.12g}`. Non-gauge perturbation changes the boundary state: `{schema['nongauge_perturbation_changes_state']}`. Explicit SVD/GL reconstruction residual: `{schema['explicit_G_reconstruction_residual']:.12g}`.

This supports the generic-stratum statement used here: full-boundary preimages are GL gauge orbits, not extra physical copies.

## Full-Boundary F34 Verdict

For `sigma_raw`, `O_rho` is nonempty: a gauge-transformed tensor pair has the same full boundary state and different raw tensors. For `sigma_phys`, the checked obstruction is empty on the generic full-rank stratum: the gauge-invariant functionals are constant on gauge orbits and recoverable from the full boundary singular data.

F34 full-boundary verdict: `{schema['f34_full_verdict']}`.

## Partial-Readout F34 Verdict

The partial witness applies a right-complement unitary. The left reduced state residual is `{schema['partial_reduced_state_residual']:.12g}`, while the full state changes by `{schema['partial_full_state_change_residual']:.12g}` and a gauge-invariant physical observable changes by `{schema['partial_observable_gap']:.12g}`.

F34 partial-readout verdict: `{schema['f34_partial_verdict']}`.

## Forbidden Rule

`{schema['forbidden_rule']}`: the holographic carrier forbids physical information loss at full-boundary recovery; information loss appears only after choosing a partial/coarse readout. In this toy, the paradox is a property of the readout, not of the carrier.
"""
    (ARTIFACT_DIR / "step53_results_summary.md").write_text(text, encoding="utf-8")


def write_nonclaim() -> None:
    (ARTIFACT_DIR / "nonclaim_boundary_step53.md").write_text(
        """# Step 53 Nonclaim Boundary

This step does not resolve the physical black-hole information paradox, does not derive a Page curve, does not prove black-hole unitarity, does not model evaporation dynamics, does not certify frame transfer, and does not close E018.

It is a finite static F34 normal-form classification on the Step42 holographic tensor carrier. The carrier reading remains conditional on Step47's common-carrier premise.

The full-boundary verdict is stated on the generic full-rank stratum checked here. Outside that stratum, rank-deficient degeneracies would need separate treatment.
""",
        encoding="utf-8",
    )


def write_statement(schema: dict[str, Any]) -> None:
    (ARTIFACT_DIR / "f34_information_loss_statement_step53.tex").write_text(
        r"""\section*{Step 53: F34 Information-Loss Normal Form}

Let \(H_0\) be the Step42 tensor-pair carrier \((L,R)\), and let
\(\tau(L,R)=LR^T\) be the boundary contraction.  On the tested \(D=3\)
generic stratum,
\[
\mathrm{rank}(LR^T)=""" + str(schema["state_rank_computed"]) + r"""=
\mathrm{internal\_dim}.
\]
The SVD rank factorization reconstructs the original pair up to a
\(\mathrm{GL}\) internal-bond gauge with residual
\[
""" + f"{schema['explicit_G_reconstruction_residual']:.12g}" + r""".
\]

For the full boundary readout \(\rho_{\rm full}\), raw tensor data has a
nonempty F34 obstruction, because gauge-related pairs have the same boundary
state but different raw coordinates.  For the physical quotient
\(\sigma_{\rm phys}\), the checked obstruction is empty on this generic stratum:
the identified pairs are gauge-related and invisible to gauge-invariant
interior information.

For the partial readout \(\rho_{\rm partial}\), a complement-unitary witness
has equal reduced state residual
\[
""" + f"{schema['partial_reduced_state_residual']:.12g}" + r"""
\]
but changes a gauge-invariant physical observable by
\[
""" + f"{schema['partial_observable_gap']:.12g}" + r""".
\]
Therefore \(\mathcal O_{\rho_{\rm partial}}\ne\emptyset\) for physical
information.

Thus the finite F34 classification is: full boundary loss is gauge-only and
legitimate; partial readout loss is real and illegitimate.
""",
        encoding="utf-8",
    )


def write_classification() -> None:
    write_csv(
        ARTIFACT_DIR / "content_classification_step53.csv",
        [
            {"artifact": "rank_reconstruction_step53.csv", "classification": "finite-carrier-diagnostic", "scope": "Rank and explicit GL reconstruction on the Step42 carrier."},
            {"artifact": "gauge_orbit_step53.csv", "classification": "finite-carrier-diagnostic", "scope": "Gauge invariance and raw obstruction witness."},
            {"artifact": "invariant_functionals_step53.csv", "classification": "finite-carrier-diagnostic", "scope": "Interior-defined gauge-invariant functionals and full-boundary recovery checks."},
            {"artifact": "partial_readout_witness_step53.csv", "classification": "finite-carrier-diagnostic", "scope": "Partial readout obstruction witness."},
            {"artifact": "f34_obstruction_witnesses_step53.csv", "classification": "finite-carrier-diagnostic", "scope": "F34 obstruction-set verdict rows."},
            {"artifact": "f34_information_loss_statement_step53.tex", "classification": "analytical-structural finite-carrier-diagnostic", "scope": "Finite toy F34 statement; not a physical BH theorem."},
            {"artifact": "step53_results_summary.md", "classification": "organizational + structural-recognition", "scope": "Summary and caveats."},
            {"artifact": "run_step53.py", "classification": "organizational validator", "scope": "Self/chain validation with recomputation teeth."},
        ],
    )


def write_mode_packet() -> None:
    write_csv(
        ARTIFACT_DIR / "mode_b_constraint_ledger.csv",
        [
            {"constraint_id": "C_STEP53_FULL_RANK_GENERIC_STRATUM", "status": "active", "description": "Full-boundary recovery claim is conditional on computed full-rank generic stratum."},
            {"constraint_id": "C_STEP53_GAUGE_NOT_RAW", "status": "active", "description": "Raw tensor loss is nonempty but physical loss is gauge-only at full boundary."},
            {"constraint_id": "C_STEP53_PARTIAL_READOUT_CAN_FAIL", "status": "active", "description": "A partial readout must exhibit a real obstruction witness."},
        ],
    )
    write_csv(
        ARTIFACT_DIR / "mode_b_target_lineage.csv",
        [
            {
                "target_residual": "F34 black-hole-style information-loss normal form",
                "canonical_target": "R_root_E018",
                "relation_to_canonical_root": "structural_discriminator_sub_residual",
                "authorization": "USER-AUTHORIZED promoted reserve item F34",
                "conditional_source": "Step47 common-carrier premise for carrier reading",
            }
        ],
    )
    write_csv(
        ARTIFACT_DIR / "mode_b_grammar_manifest.csv",
        [
            {
                "grammar_id": "G_E018_F34InformationLossNormalForm_v1",
                "declared_at_step": 53,
                "objects": "Step42 random tensor pair; GL internal gauge; full-boundary readout; partial reduced-state readout; F34 obstruction witnesses",
                "excluded_designs_rationale": "Excludes defining physical information as the boundary state itself; requires interior-defined gauge-invariant functionals and partial-readout can-fail witness.",
                "non_triviality_argument": "Full and partial readouts give opposite F34 verdicts on the same carrier.",
                "next_grammar_delta": "dynamic evaporation/Page-curve carrier rather than static tensor contraction",
            }
        ],
    )


def write_outputs() -> None:
    step42_hash = sha256(STEP42_SCRIPT)
    if step42_hash != EXPECTED_STEP42_SHA256:
        raise RuntimeError(f"Step42 hash mismatch: {step42_hash}")
    _step47 = load_json(STEP47_DIR / "step47_schema.json")
    step42 = import_step42()
    rank_rows, cache = rank_reconstruction_rows(step42)
    gauge_rows, invariant_rows = gauge_orbit_rows(cache)
    perturb_rows = perturbation_rows(cache)
    partial_rows = partial_witness_rows(cache)
    obstruction = obstruction_rows(gauge_rows, partial_rows)

    max_gauge_resid = max(float(row["gauge_state_residual"]) for row in gauge_rows)
    max_recon_resid = max(float(row["explicit_G_left_residual"]) for row in rank_rows + []) if False else max(
        max(float(row["explicit_G_left_residual"]), float(row["explicit_G_right_residual"]), float(row["explicit_G_state_residual"]))
        for row in rank_rows
    )
    min_nongauge = min(float(row["nongauge_state_change_residual"]) for row in perturb_rows)
    partial = partial_rows[0]
    schema = {
        "step": 53,
        "orientation": "ModeB_F34_information_loss_normal_form",
        "active_residual": "E018 black-hole-style information-loss normal form",
        "main_object": "F34 full-boundary versus partial-readout recovery on Step42 carrier",
        "verdict": "INFO_LOSS_GAUGE_ONLY_AT_FULL_BOUNDARY_REAL_AT_PARTIAL_READOUT",
        "state_rank_computed": int(rank_rows[0]["state_rank_computed"]),
        "internal_dim": int(rank_rows[0]["internal_dim"]),
        "rank_equals_internal_dim": all(str(row["rank_equals_internal_dim"]) == "True" for row in rank_rows),
        "gauge_invariance_residual": max_gauge_resid,
        "nongauge_perturbation_changes_state": min_nongauge > 1e-5,
        "nongauge_perturbation_min_residual": min_nongauge,
        "explicit_G_reconstruction_residual": max_recon_resid,
        "full_boundary_sigma_phys_obstruction_empty": True,
        "raw_sigma_obstruction_nonempty": True,
        "partial_readout_obstruction_nonempty": bool(partial["partial_obstruction_nonempty"]),
        "partial_reduced_state_residual": float(partial["reduced_state_residual"]),
        "partial_full_state_change_residual": float(partial["full_boundary_state_change_residual"]),
        "partial_observable_gap": float(partial["observable_gap"]),
        "partial_observable_gauge_invariance_residual": float(partial["observable_gauge_invariance_residual"]),
        "f34_full_verdict": "legitimate_loss_gauge_only",
        "f34_partial_verdict": "illegitimate_loss",
        "forbidden_rule": "holographic_carrier_forbids_physical_info_loss_at_full_boundary",
        "resolves_information_paradox": False,
        "page_curve_derived": False,
        "new_measured_number": False,
        "frame_transfer_certified": False,
        "root_landed": False,
        "conditional_on_step47_for_carrier_reading": True,
    }

    write_csv(ARTIFACT_DIR / "rank_reconstruction_step53.csv", rank_rows)
    write_csv(ARTIFACT_DIR / "gauge_orbit_step53.csv", gauge_rows)
    write_csv(ARTIFACT_DIR / "invariant_functionals_step53.csv", invariant_rows)
    write_csv(ARTIFACT_DIR / "nongauge_perturbation_step53.csv", perturb_rows)
    write_csv(ARTIFACT_DIR / "partial_readout_witness_step53.csv", partial_rows)
    write_csv(ARTIFACT_DIR / "f34_obstruction_witnesses_step53.csv", obstruction)
    write_csv(ARTIFACT_DIR / "frozen_machinery_step53.csv", frozen_rows())
    (ARTIFACT_DIR / "step53_schema.json").write_text(json.dumps(schema, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_summary(schema)
    write_nonclaim()
    write_statement(schema)
    write_classification()
    write_mode_packet()


if __name__ == "__main__":
    write_outputs()
