# My reductionist failure modes — the bias log (read this EVERY session)

I (the assistant) have a strong, repeated reductionist bias that produces confident, articulate, **wrong**
conclusions about Six Birds. This file catalogs the exact failures I committed (2026-06-18) and the grounded
litmus that catches each. The user's words: I claimed to understand strict extension 4 times and was wrong 4
times. **Do not trust an assertion of understanding — only grounded, cited reasoning.** Companion antidote:
`/home/repos/six-birds-papers/SIX_BIRDS_ANTI_REDUCTIONISM_PRIMER.md` (read it first).

The single root cause (primer §0): my default move is to **reduce** — derive/factor/shortcut. That instrument
is correct *inside a fixed theory* and is **the wrong instrument between layers**, which is the only place SBT
has content. Every failure below is an instance.

---

## The failures I actually committed this session (specific, so I recognize the pattern)

1. **Inject-and-recover toy (steps 99–102) = the cardinal sin.** I injected a *known* transfer operator, coarse-
   grained it, and "recovered" its mass gap. That gap **factored through the operator I injected** (`gap = h̃∘f`)
   ⇒ *definable* ⇒ a **trivial, non-strict** extension by the exact definition (`02` §1.2–1.3). And I "validated"
   it by matching a gap I had **injected** ⇒ **in-sample / circular** (forbidden, `02` §1.6). In SAU terms it is a
   **counterfeit certificate**: `δ_nosmuggle ≠ ∅` and `δ_fact = ∅` (`02` §3.3).
   - **Litmus:** *Does the value/distinction provably NOT factor through the base lens, and is it checked
     out-of-sample with nothing injected?* If it factors or is checked in-sample → it is not strict extension. STOP.

2. **Chased RECOVERY / lumpability — the literal negation of the certificate.** I treated "the macro gap matches
   the known gap" as success. But strict extension requires **macro-admissibility OBSTRUCTION** (the base is too
   coarse to express the packaged future = non-lumpable = non-factorization). Recovery = admissibility =
   factorization = the **opposite** of the certificate (`02` §2.4).
   - **Litmus:** the success signal is the base **failing** to reconstruct the packaged object, not succeeding.

3. **Called calibration / compression a "milestone / success."** Deflationary inflation: plumbing dressed as
   progress. Even a genuine `k≪dim` compression is, per the corpus, at most proof-of-mechanism — never strict
   extension (`02` §1, primer §9.2–9.3).
   - **Litmus:** never label a step a success unless it produced a *non-factoring, out-of-sample-validated* result.

4. **Deferred strict extension to "a later phase / R1."** It is the **point of every step**, not phase 2. Reading
   a value before the certificate chain is exactly backwards (the value is read LAST, `02` §3.2).
   - **Litmus:** if a step doesn't advance non-factorization, don't run it.

5. **Trusted my OWN synthesized documents over the running code — repeatedly.** I treated my
   `TRUE_STRICT_EXTENSION_SPEC.md` (a relic I authored, built on `closurelab/numeric.py`, a 321-line python toy)
   as governing, instead of reading the actual papers + pica code. The relic even **inverted** the
   macro-admissibility obstruction (the *certificate*) into a "bust to overcome" (`02` §2.4).
   - **Litmus:** a synthesis/summary/spec (mine most of all) is NEVER authority. The papers and the running code
     are. When unsure, read them — do not trust a write-up.

6. **Conflated "the computation library changed" with "the strict-extension mechanism is obsolete."** At the
   engine pivot I bucketed the whole strict-extension apparatus as "baggage" because its example code was the
   discarded python library. The mechanism is substrate-independent; only the HOW changes.
   - **Litmus:** when the substrate changes, keep the WHAT (non-factorization, the certificate chain), swap only the HOW.

7. **Claimed understanding without grounding (×4).** Each "I understand it now" was an assertion, not a cited
   argument, and each was wrong.
   - **Litmus:** never write "I understand"; write the cited claim and let it stand or fall on the citation.

---

## The general traps (primer §9) — the non-reductive correction for each

- **"Unify A and B by deriving both from shared math."** ✗ asks for the factorization strict extension *proves
  does not exist*. → ask what common third they both project from (common refinement); audit the relation.
- **"Derive the emergent constant / find its formula."** ✗ a derivable constant is not emergent. → identify the
  **run** that generates it + the **out-of-sample** test. (Proton mass = the canonical run-only constant.)
- **"Summarize/shortcut the run with a closed form."** ✗ if you could, it wasn't emergent. → the run is irreducible.
- **"SBT is just <textbook lemma> relabeled."** ✗ you evaluated it *within* a layer (where SBT is silent by design).
  → re-pose **between** layers.
- **"The higher layer reduces to the lower."** ✗ reduction runs DOWN (shadow), never UP. → keep the asymmetry.
- **Over-deflation ("emergence is a definitional trick") OR over-inflation ("emergence is mystical").** ✗ both. →
  it is **fully mechanical** (the run obeys math-as-mechanism) AND **genuinely irreducible** (escapes
  math-as-reduction). Hold both.
- **"Score SBT by how much it derives/predicts within a layer."** ✗ it looks thin there. → score it on inter-layer
  structure (foreclosure, descent legality, recognition).
- **"A negative result means the theory failed."** ✗ SBT *predicts* its own foreclosure. A foreclosure verdict is
  the theory working.

---

## The 4-line pre-step ritual (run before ANY construction step)

1. **NON-FACTORIZATION:** what distinction/value am I producing that provably does NOT factor through the base lens?
2. **CERTIFICATE not recovery:** am I looking for the base to FAIL to reconstruct it (obstruction), not succeed?
3. **NO SMUGGLING:** is the value absent from my inputs/construction, i.e. not injected?
4. **OUT-OF-SAMPLE:** can I validate it by predicting something I did not fit?
If any answer is "no / I'm matching a known value / I injected it / I'll check in-sample" → it is NOT strict
extension. Stop and re-pose.
