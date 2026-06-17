# Step 6 Results Summary

## Orientation

Step 6 applies the P6 decaying-degeneracy audit to the E043 horns. The degeneracy is the number of scale-ratio values still effectively in play under each horn's refinement.

## Degeneracy Sequences

- Derivation attractor: `6->5->4->2->1->1`.
- Broad anthropic measure: `6->6->6->6->6->6`.
- Sharp selecting measure control: `3->2->2->1->1`.

## Adjudication

The P6 criterion certifies horns whose degeneracy collapses to a single point. On this toy:

- Certified: `derivation_attractor;sharp_selecting_measure`.
- Failed as broad landscape: `broad_anthropic_measure`.

This adjudicates by collapse, not by horn label: the sharp measure also passes because it collapses, while the broad measure fails because it remains a distribution.

## Controls

- Broad measure fails to collapse: `True`.
- Derivation collapses: `True`.
- Sharp measure also collapses: `True`.
- Carrier guard: scale-ratio grid plus degeneracy audit.

## Verdict

`e043_horn_adjudication_constructed`.

The framework criterion certifies selection-to-a-point and fails broad landscape behavior on the finite toy.
