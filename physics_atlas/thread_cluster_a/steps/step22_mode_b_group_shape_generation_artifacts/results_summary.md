# Step 22 Results Summary

SUPERSEDED. The Step 22/23 "generated SM gauge shape" framing is superseded by the v3 external review and the Step 28 confirmation: Steps 22-26 carried a total_slots=5 + exterior-algebra (GUT) prior -> corrected grade = FINITE GUT/EXTERIOR RECOGNITION RECOVERY, NOT neutral generation. The honest, un-smuggled result is the separate neutral hunt in Steps 28-39 (conditional shadow-uniqueness via the introduced clean-separation condition). See SUPERSEDED.md, manager_log, TODO.md.

## Generated-vs-input breakdown

Inputs:
- Bounded enumeration grammar: non-abelian factor count `0..3`, each factor rank `1..4`, plus one abelian charge role.
- Closure tests: nontrivial chirality, anomaly cancellation, charge-grid closure, Witten parity for pseudoreal doublets, and minimality by total rank, then total slots, then factor count.
- Minimality principle: choose the smallest closing sector structure under that ordering.

Generated outputs:
- Enumeration size: `35` candidate sector structures.
- Closing structures: `1`.
- Minimal generated structure: ranks `1|2`, dimensions `2|3`, total rank `3`, total slots `5`.
- Recognition: the generated dimensions `2|3` recognition-land on the SM gauge-sector shape `SU(2) x SU(3) x U(1)` up to factor order, hence the usual `SU(3) x SU(2) x U(1)` naming.

This is the deflationary truth: the bounded range, chirality requirement, anomaly/charge tests, and minimality ordering are inputs. The sector counts and ranks are outputs of the enumeration, not primitives of the build script.

## Closure audit

The minimal closer `r1|2` has:
- ranks `1|2`
- dimensions `2|3`
- primitive neutral weights `-3|2`
- cubic coefficients `0|0`
- mixed coefficients `0|0`
- abelian gravity sum `0`
- abelian cubic sum `0`
- charge quantization `True`
- Witten parity `True`

## Controls and gates

Negative controls pass:
- `abelian_only` does not close.
- `real_rep_only` does not close.
- `single_complex_factor` does not close.

Stage II checks pass:
- No structure without a complex representation closes.
- Single-factor structures do not close because the neutral charge grid is trivial or underdetermined in this grammar.

All six no-smuggling gates pass: primitive exclusion, dependency trace, ablation, negative controls, Stage II earning, and no-single-axiom-equivalence.

## Verdict

`GENERATED`: within the declared finite grammar, the minimal chiral/anomaly-free/charge-quantized closure generates the sector dimensions `2|3`, recognition-landing on the SM gauge-sector shape after the audit. This does not settle E019, does not provide a physical gauge-sector theorem, and does not change the real-world status. The next cascade step should stress the result against richer grammars and additional discriminators rather than treating this finite closure as final.
