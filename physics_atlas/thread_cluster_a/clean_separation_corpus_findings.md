# What SBT says on the clean-separation question — corpus search findings

> Record of a wide search across the SBT corpus (3 independent reader sweeps) for what the framework says
> about the **clean-separation** condition — the load-bearing condition of the Step-38 structure-uniqueness:
> *the mass-breaking produces no vector bosons charged under the confining sector* (the EW-breaking sector and
> the color/confining sector are separate, non-interfering; W/Z colorless vs SU(4)→SU(3)'s 6 colored coset
> vectors). The open question: is clean-separation **fundamental** (forced by deeper SBT principles) or
> **introduced**? Companion computation: Step 41 (Δ_fact instantiation).

> **[STATUS UPDATE — Steps 57–59.]** This doc's verdict ("introduced recognition source") remains correct *for the
> gauge layer* — clean-separation is not toy-derivable there (Step 39). But it has since been **GROUNDED one layer
> up**: requiring a **memory-stability** layer (stable substrate + capacity for ≥2 records + distinguishability)
> **forces** clean-separation, non-circularly and enumeration-robustly across the 11,990-structure carrier
> (Steps 57–59; **LANDED · GROUND** — see `MAIN_RESULTS.md` J1 / `LANDED_vs_NOT.md`). So it is introduced *at the
> gauge layer* AND grounded *from the layer above* — a relocation up the tower, not derivation-from-nothing (the
> all-structures theorem L60→L64 is the open upgrade; the physical fundamentality of memory-stability is the
> standing external question).

## Convergent verdict (3 independent reads agree): INTRODUCED — a *recognition source*

SBT has real, named machinery that clean-separation maps onto, but **none of it forces clean-separation**;
every relevant law is a *neutral equivalence* or a *conditional with a supplied source obligation*. The
corpus's own structure therefore answers the open question: clean-separation is **introduced** — and SBT has a
*named category* for exactly this: a **recognition source** (a structural condition supplied/named at the
formed layer and audited downstream, not derived from primitives). This independently confirms Step 39 (which
found the only internal derivation route circular) — now from the papers, not just the toy.

## The three genuine connections (ranked)

1. **Non-factorization (Foundations III, Thm 12/13) — the precise formal home.**
   `π₁ ⊀ π₀ ⟺ Δ_fact(π₀,π₁) ≠ ∅`, with the factorization defect collecting witness pairs `(s,s')` one
   quotient identifies but the other splits. **Clean-separation = `Δ_fact = ∅`** between the confining-sector
   quotient and the mass-sector quotient; the contaminating confining-charged broken vectors ARE the witnesses.
   Faithful translation (recurs as "no-interference = factorization", and Foundations IV files
   noninterference-security as factor-through-a-projection). **But the calculus is a neutral equivalence** — it
   supplies the defect that *decides* separation; it never asserts it empty. → instantiated in **Step 41**.

2. **Self-Dual Trace Confinement (SDTC) / F14 "Duality Fixity" — the richest resonance (and the "duality" hit).**
   An involution `J` splits a structure into invariant (fixed-locus) + anti-invariant parts; the anti-invariant
   content is confined/vanishes ("visible mass confined to `Fix(J)`"). Evocative for clean-separation
   (clean = self-dual/fixed-locus; colored debris = anti-invariant content). **But:** (i) its "mass"/"confinement"
   are measure-theoretic homonyms (μ-mass; localization), not particle-mass/QCD-confinement; (ii) its
   gauge-invariance instance is an explicit "structural prediction, not a theorem," and targets a *different*
   proposition (project onto gauge-invariant observables); (iii) SDTC is itself "named as a recognition source …
   not derived from framework primitives," and its "separation" is a *defined hypothesis*. So grounding
   clean-separation in SDTC **relocates** the assumption (posit the involution + separating readout + domination
   budget = clean-separation restated), it does not discharge it.

3. **F28 Composability (cross-residual descent) + Foundations II no-collapse — positive coexistence + hygiene.**
   F28: components compose with "no cross-term smuggled in; the residual descends independently" (CRD) — clean-
   separation as a CRD instance. Foundations II boundary-distinctions: "distinct functions keep their bookkeeping
   on distinct channels; composition is not identification" — the corpus's cleanest "separate channels, no
   smuggled debris." **But** F28 is a conditional, and Foundations II is explicitly *audit hygiene* (not a global
   independence theorem; you may not *conflate* the channels, it does not say they physically can't interfere).

## Corrections to earlier loose glosses (honesty)
- **Currency–constraint duality / shadow prices** (To Spend a Stone) is **vertical** (lower-layer currency →
  higher-layer constraint → shadow price), NOT a horizontal "spend vs conserve on separate ledgers" across
  co-existing sub-sectors. My earlier "currency/audit-ledger separation" reading was loose — retracted.
- **F37 Complementarity / non-joint access** is the **dual polarity** (two readouts that *cannot* be jointly
  realized), not clean-separation (two sectors that *can* coexist without interfering). The right-polarity
  cousin is F51 (common refinement), not F37.

## The resolution (and why "introduced" is not a defect)
In SBT's own vocabulary, "is clean-separation fundamental?" resolves to: **it is a recognition-source closure
condition** — the *same kind of object as SDTC itself*. SBT's discipline is to *name* such conditions and audit
downstream, not to derive them. So the honest grade is not "we smuggled an arbitrary condition" but
"clean-separation is a declared **`Δ_fact = ∅`** closure condition / recognition source," which is a more
principled, framework-native statement than the bare "no confining-charged vectors." Whether that recognition
source corresponds to real physics is the standing **frame-transfer** question (external judgment).

## Key sources
- Foundations III: non-factorization Thm 12/13 (Δ_fact); status-family separation; StructDown vs TopDownChannel.
- Foundations IV: F14 Duality Fixity/SDTC; F28 Composability (COD/CRD); F37 Complementarity; F51 Unification; F27 Conservation.
- `Self_Dual_Trace_Confinement…`, `Riemann_Hypothesis_via_Self_Dual_Trace_Confinement…` (the SDTC law + its one worked instantiation; gauge = disclaimed prediction).
- `To_Spend_a_Stone…` (currency-constraint duality — vertical), `Emergence_IS_the_Needle_Killer` (the two-ledger involutive split), `Six_Birds_Foundations_II` (no-collapse/no-smuggling hygiene).
- In-repo: Step 9 / Step 18 found facet-selection comes out **coupled-but-distinct** (SBT factorization is neutral; physics comes out coupled when tested). Step 41 = the Δ_fact instantiation of clean-separation.
