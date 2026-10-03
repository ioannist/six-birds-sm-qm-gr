# Qeios Submission Notes

**Title:** To Kill Three Stones with Six Birds: A Common Grammar for the SM, QM, and GR

**Author:** Ioannis Tsiokos (ORCID: 0009-0009-7659-5964)

**Affiliation:** Automorph Inc., Wilmington, DE, USA

**Corresponding email:** ioannis@automorph.io

---

## Recommended domain/field selections

- **Primary:** Physics
- **Secondary:** Mathematics
- **Suggested subfields:** Foundations of Physics; High Energy Physics -- Theory;
  General Relativity & Quantum Cosmology

## Suggested keywords

Six Birds Theory; emergence calculus; finite structural constructions;
Standard Model gauge selection; quantum gravity; holographic entanglement

---

## Abstract

Can one small mathematical vocabulary organize two very different open problems in fundamental physics? We test
this with the Six Birds emergence calculus, whose working core is simple: a coarse description is a quotient of a finer
one, a quantity either passes through the quotient or leaves a checkable obstruction, and two descriptions may
share a common refinement. We apply this vocabulary to two problems: why the Standard Model (SM) has its gauge
structure, and how quantum (QM) and gravitational (GR) descriptions relate. Every result lives on an explicitly declared
finite model (a finite enumeration, a fixed finite graph, or matrices of fixed size), holds only under the stated
caps and conventions, and ships with a public validator.

On the SM side, a census of $1{,}066$ chiral gauge structures shows that, within the declared windows, only the
$SU(2)\times SU(3)$ family admits a “clean” breaking branch, and every clean branch breaks the $SU(2)$ factor.
Selection is therefore a property of a structure-plus-branch pair, not of a bare gauge group. A separate toy theorem
rules out single-factor $SU(N)$ candidates. An exact construction of the regular $SU(5)$ embedding forces the
hypercharge direction and reproduces $\sin^2\theta_W=3/8$ and $k_Y=5/3$. These are standard values. They are
recovered under named conventions and do not single out $SU(5)$.

On the QM–GR side, an exact theorem shows that the declared QM and GR readouts of an abstract carrier are
incomparable: neither is a coarse-graining of the other, although a common refinement carries both. On finite graphs,
an exact max-flow/min-cut certificate realizes $\operatorname{Area}(\text{min cut})=\sum_e c_e y_e$ with per-edge
shadow prices $y_e$, and sampled tensor-network entropies stay below the cut. In a toy holographic carrier, a general
linear-algebra theorem shows that the full raw boundary readout loses only internal gauge data, while an exact witness
shows that a half-boundary readout loses physical information.

Three questions are developed as construction programs. For the first, nineteen exact equal-cut graph pairs cannot be
joined by forward reduction moves, while six state-level pairs turn out to be gauge-equivalent. The other two concern
gravitational record formation and the persistence of records; their finite precursors are, respectively, conditional
on an assumed channel and sensitive to how records are defined. Negative results, such as the exact commutation of
the natural “quantize” and “curve” completions, are reported as results. No claim about nature is made beyond these
finite carriers.


---

## Declarations block (copy/paste for Qeios submission form)

**Funding:**
No external funding was received for this research.

**Potential competing interests:**
The author is affiliated with Automorph Inc.; no financial competing interests to declare.

**Author contributions:**
I. Tsiokos: Conceptualization; Methodology; Formal analysis; Investigation; Software; Data curation; Visualization; Writing -- original draft; Writing -- review & editing. Sole author; CRediT taxonomy summarized accordingly.

**Data availability:**
No external or third-party datasets were used. The materials supporting this work consist of manuscript source files, bibliography records, finite-carrier construction artifacts, validator outputs, and build outputs in the public repository `six-birds-sm-qm-gr`.

**Code availability:**
Source, construction artifacts, and independent re-derivation scripts are available at https://github.com/ioannist/six-birds-sm-qm-gr (see `physics_atlas/INDEPENDENT_REDERIVATIONS.md`).

**Ethics / Human subjects:**
Not applicable; this work involves no human or animal participants and no personal data.

**Generative AI / AI-assisted technologies:**
AI tools were used for coding and build-pipeline assistance, bibliography verification, LaTeX editing, drafting and readability editing, and an AI-based factual-correctness review of the manuscript against the repository evidence. The figures are TikZ drawings whose source was drafted with AI assistance and reviewed by the author. All mathematical claims, theorem statements, scope decisions, and final manuscript text were reviewed, validated, and edited by the author, who takes full responsibility for the published article. [AUTHOR: confirm the figure-provenance sentence matches how each figure was actually produced before submitting.]

---

## Links

- **GitHub repository:** https://github.com/ioannist/six-birds-sm-qm-gr
- **Zenodo archive:** https://doi.org/10.5281/zenodo.23120510 (record: https://zenodo.org/records/23120510)

---

## Upload files

- **Preferred:** Upload `qeios_single.tex` (all figures are TikZ and are inlined
  in the .tex; no image files are needed).
- **Alternative:** Upload `qeios_source_bundle.zip` (full source with modular TeX,
  embedded `.bbl`, and figures).
- **Pre-built PDF:** `qeios_single.pdf`

---

## Article type

This manuscript is best classified as an **Original Research Article** (theoretical / foundational physics).
