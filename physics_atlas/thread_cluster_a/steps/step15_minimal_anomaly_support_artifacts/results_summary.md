# Step 15 Results Summary: Minimal Anomaly-Support Test

## Declared Minimality Measure

Primary measure: irreducible chiral multiplet count after quotienting vector-like pairs, overall hypercharge normalization, and trivial neutral singlets.

Tie-breaker: total Weyl component count. A final lexicographic ordering is used only to make CSV output deterministic.

## Enumeration Counts

- Multiplet types: `66`.
- Raw bounded supports: `9705619`.
- Raw anomaly-free supports: `1161`.
- Distinct irreducible chiral supports after quotient: `28`.
- Non-SM irreducible anomaly-free supports: `27`.

The can-fail control passes: the enumeration contains non-SM irreducible anomaly-free supports.

## SM Location

- SM support label, in canonical hypercharge sign convention: `(1,1)_-1 + (1,2)_3/6 + (3,2)_-1/6 + (3bar,1)_-2/6 + (3bar,1)_4/6`.
- SM score: `5` irreducible multiplets, `15` Weyl components.
- Minimal score in the enumeration: `4` irreducible multiplets, `12` Weyl components.
- SM rank: `28` of `28`.
- Competitors at or below the SM score: `27`.

## Verdict

`honest_no_go_minimality_insufficient`.

Anomaly-freedom plus the declared minimality measure does not single out the SM one-generation chiral content in this bounded enumeration. Several non-SM irreducible anomaly-free supports beat the SM score. This is an honest no-go for minimality-alone as the selection law.

The next door is explicit: minimality must be supplemented by an electroweak quark-lepton participation or observed-charge sector condition.

## Competitor Supports

See `competitors_at_or_below_sm_step15.csv`. The first minimal competitors have score `4` multiplets / `12` Weyl components.

## Candidate-Law Obligation Status

- Faithful enrichment: continued.
- Independently checkable consequence: advanced as a typed no-go.
- Closed-form relation: inherited from Step 14; no new closed-form selection law lands here.
- Limit recovery: continued, because the SM support is present and anomaly-free.
