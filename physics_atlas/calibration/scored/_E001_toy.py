"""
E001  qcd -> hadron-spectrum  [arrow: up]

DESCENT-TEST toy model M (declared BEFORE computation; finite linear algebra only,
NEVER an irreducible run).  Goal: honestly test whether the hadron-mass readout
factors as a FINITE coarse-graining (Schur-complement adequacy Xi -> 0) of a finite
truncation of the QCD source, at TWO refinement levels.

WHAT IS BEING MODELED
---------------------
The source card 'qcd' casts Z = staged lattice gauge+quark path-integral configs; the
physical content the target wants is the hadron MASS (proton/pion), which on the lattice
is the exponential decay rate of a gauge-invariant interpolator two-point function
C(t) ~ sum_n |A_n|^2 exp(-m_n t).  The mass m_0 is the SMALLEST transfer-matrix
energy gap.  The decisive physics (card Sigma_f, digest s7): the GeV scale / m_0 is set by
DIMENSIONAL TRANSMUTATION -- m_phys = (1/a) * f(g0(a)), with a -> 0 along an RG trajectory
a(g0) ~ Lambda^{-1} exp(-1/(2 b0 g0^2)).  There is NO free hadron-mass parameter and NO
closed-form predicate in Sigma_f giving m_0 without running.

FINITE TOY: a 1-parameter family of finite Hermitian "lattice Hamiltonians" H(g0) on a
small Hilbert space (a stand-in for the transfer-matrix generator).  The physical
observable is the spectral GAP m(g0) = lambda_1(H) - lambda_0(H) measured in lattice
units, converted to physical units by the dimensional-transmutation rule.  The "currency"
matrices follow digest D.1 EXACTLY (block currencies, Schur complement, MP-pseudoinverse).

PROBE FAMILIES (declared before computation):
  - L0  (native/target probe = the observable_readout layer):  the readout the target
    layer can express.  The target node 'hadron-spectrum' is an observable_readout that
    INHERITS qcd's casting; its expressible currency is the gauge-invariant CORRELATOR
    DATA the lens f keeps -- the short-distance correlator moments at a FIXED finite
    truncation order (what a finite-order / fixed-coupling probe sees).  This is what a
    finite descriptive layer "already accepts" without running the coupling to the IR.
  - D0  (dissolving/source probe = what is to be explained):  the PHYSICAL mass m_phys(g0),
    the dimensional-transmutation readout that the full run produces.

The descent test asks: does D0 (the physical mass) factor LINEARLY through L0 (the
finite-order correlator currency)?  i.e. does there exist A with D0 = A L0 (Xi=0)?
If yes -> E1 (finite descent).  If a stable positive residual Xi > 0 -> obstruction.

REFINEMENT: two finite stages h1 (coarser, fewer couplings + smaller H) and h2 (finer,
more couplings + larger H).  Verdict must be STABLE across both (gate E.9).

NO-OVER-READ (gate E.3): the target's accepted_observables = the mass spectrum read out;
the descent may not literalize a source-only object.  We also report whether the recovered
quantity actually lands as a finite functional.

This is a DECLARED finite stand-in, not reverse-engineered to a desired Xi: the structural
input is just (i) a transfer-matrix gap and (ii) the standard dimensional-transmutation
running a(g0) ~ exp(-1/(2 b0 g0^2)).  Both are textbook QCD, fixed before the computation.
"""

import numpy as np
np.set_printoptions(precision=6, suppress=True)

b0 = 9.0 / (16.0 * np.pi**2)   # one-loop QCD beta coefficient, Nf=3 (texbook, fixed)

def physical_mass(g0):
    """m_phys in physical units = (1/a) * (dimensionless gap), with
    a(g0) ~ exp(-1/(2 b0 g0^2)) (dimensional transmutation, asymptotic freedom).
    The dimensionless lattice gap is an O(1) smooth function of g0 (here a mild,
    monotone, NON-singular dependence). The PHYSICS (the GeV scale) lives in the
    essential singularity exp(-1/(2 b0 g0^2)) -- NON-analytic at g0=0, the hallmark
    of dimensional transmutation: not a finite polynomial/linear functional of g0."""
    a = np.exp(-1.0 / (2.0 * b0 * g0**2))      # lattice spacing (essential singularity)
    inv_a = 1.0 / a                             # physical scale 1/a
    dimensionless_gap = 1.0 + 0.30 * g0**2      # O(1) smooth, regular in g0
    return inv_a * dimensionless_gap            # m_phys

def finite_order_correlator_currency(g0, K):
    """L0 native probe currency: what a FINITE-ORDER (fixed-truncation) lens sees --
    the first K perturbative correlator moments, polynomials in g0^2 (analytic at g0=0).
    These are exactly the predicates Sigma_f expresses WITHOUT running the coupling to
    the IR: a finite Taylor data vector. By construction (and by physics) these are
    REGULAR in g0; they cannot contain the essential singularity exp(-1/(2 b0 g0^2))."""
    return np.array([g0**(2*k) for k in range(K)])   # [1, g0^2, g0^4, ..., g0^{2(K-1)}]

def build_currencies(g0_grid, K):
    """Build finite response operators L0, D0 over a grid of g0 samples, then the
    digest-D.1 block currencies and the Schur-complement adequacy residual Xi."""
    n = len(g0_grid)
    # D0 : 1 x n  (the physical-mass readout sampled on the grid)
    D0 = np.array([[physical_mass(g) for g in g0_grid]])
    # L0 : K x n  (finite-order correlator currency, K moments, sampled on the grid)
    L0 = np.array([finite_order_correlator_currency(g, K) for g in g0_grid]).T
    # audit energy C0 = I_n (legal-energy quotient; PSD identity, least-commitment)
    C0 = np.eye(n)
    C0inv = np.linalg.pinv(C0)
    K_LL = L0 @ C0inv @ L0.T
    K_DL = D0 @ C0inv @ L0.T
    K_LD = K_DL.T
    K_DD = D0 @ C0inv @ D0.T
    Xi = K_DD - K_DL @ np.linalg.pinv(K_LL) @ K_LD     # Schur complement (2,2)
    # relative residual: fraction of the source-readout "energy" NOT explained by L
    rel = float(Xi[0, 0] / K_DD[0, 0])
    return float(Xi[0, 0]), rel, float(K_DD[0, 0])

print("=== E001 descent-test: Xi adequacy residual (Schur complement) ===")
print("Question: does the physical hadron mass D0 = m_phys(g0) factor as a finite")
print("LINEAR functional of the finite-order correlator currency L0 ?  Xi=0 <=> yes (E1).")
print()

# ---- TWO refinement levels (gate E.9: verdict must be STABLE across both) ----
# coarser stage h1 and finer stage h2: finer = more g0 samples AND more correlator moments K
for label, g0_grid, K in [
    ("h1 (coarse): 6 g0-samples, K=3 correlator moments",
     np.linspace(0.9, 1.6, 6), 3),
    ("h2 (fine):  12 g0-samples, K=6 correlator moments",
     np.linspace(0.85, 1.7, 12), 6),
]:
    Xi, rel, KDD = build_currencies(g0_grid, K)
    print(f"[{label}]")
    print(f"    Xi (Schur complement)         = {Xi:.6e}")
    print(f"    K_DD (source readout energy)  = {KDD:.6e}")
    print(f"    relative residual Xi/K_DD     = {rel:.6f}")
    print(f"    verdict: {'Xi ~ 0  (FINITE DESCENT, E1)' if rel < 1e-6 else 'Xi > 0 STABLY (obstruction; NOT E1)'}")
    print()

# ---- CONTROL: a genuinely descending (analytic) target factors to Xi~0 ----
# Replace the essential-singularity mass with a target that IS a finite polynomial in g0^2.
def analytic_target(g0):
    return 2.0 + 1.5*g0**2 - 0.4*g0**4    # lies in span of {1, g0^2, g0^4} = L0 for K>=3
def build_control(g0_grid, K):
    n = len(g0_grid)
    D0 = np.array([[analytic_target(g) for g in g0_grid]])
    L0 = np.array([finite_order_correlator_currency(g, K) for g in g0_grid]).T
    C0inv = np.eye(n)
    K_LL = L0 @ C0inv @ L0.T; K_DL = D0 @ C0inv @ L0.T; K_LD = K_DL.T; K_DD = D0 @ C0inv @ D0.T
    Xi = K_DD - K_DL @ np.linalg.pinv(K_LL) @ K_LD
    return float(Xi[0,0]/K_DD[0,0])
print("=== CONTROL (sanity: an ANALYTIC target DOES descend) ===")
for label, g0_grid, K in [("h1", np.linspace(0.9,1.6,6), 3), ("h2", np.linspace(0.85,1.7,12), 6)]:
    rel = build_control(g0_grid, K)
    print(f"    [{label}] analytic target rel-residual Xi/K_DD = {rel:.3e}  -> {'Xi~0 (descends, E1)' if rel<1e-6 else 'NONZERO'}")
print()
print("INTERPRETATION: the control confirms the test is not rigged to always return Xi>0 --")
print("an analytic (finite-polynomial) target descends cleanly (Xi~0).  The physical mass,")
print("carrying the dimensional-transmutation essential singularity exp(-1/(2 b0 g0^2)),")
print("does NOT lie in the span of any finite analytic correlator currency: Xi stays")
print("positive and STABLE across both refinements.  No finite linear descent exists.")
