# Step 39 - Clean-Separation Derivation Test

Deflationary truth first: the proposed standard confining-sector requirement implies clean separation, but on this finite carrier it is extensionally equivalent to clean separation. Therefore Step 39 does not establish a more basic independent basis for the rule. Clean separation remains a qualified introduced standardness condition.

## Carrier

The Step-35 higher-layer survivors were rederived:

- Reproduced survivors: `12`.
- Structure split: `2|3:8;4:4`.

## Standardness Requirement Tested

The tested requirement is:

> A surviving confining sector is standard when its confining-charged matter content is fermionic only; confining-charged massive vector content is non-standard.

The computation records, per survivor:

- confining subgroup(s);
- confining-charged fermion type count;
- confining-charged massive vector count;
- whether mass closure is complete;
- whether clean separation holds;
- whether standardness holds.

## Computed Outcomes

| structure | carrier | standard | relaxed | vector count | target passes |
|---|---:|---:|---:|---|---|
| `2|3` | 8 | 8 | 8 | `0` | yes |
| `4` | 4 | 0 | 4 | `6` | no |

Relaxing the standardness condition by allowing confining-charged massive vectors brings the single-factor family back:

- relaxed survivors: `12` (`2|3:8;4:4`);
- standard survivors: `8` (`2|3:8;4:0`);
- condition is load-bearing: yes.

## Implication And Circularity

Computed implication tests:

- `standardness => clean separation`: true.
- `clean separation => standardness`: true.
- extensional equivalence on this carrier: true.
- independent-basis status: not established.

The circularity detector flags this: the only non-standard charged matter channel in the finite carrier is the same confining-charged massive-vector obstruction used by clean separation.

## Verdict

`INDEPENDENT_INTRODUCED_CIRCULAR`.

Clean separation remains a defensible, load-bearing standardness condition, but it is not derived from a strictly more fundamental independent requirement in this step. The Step-38 grade remains qualified.

Next grammar delta: continue to the content cascade, or build a richer confining-layer grammar with more charged-matter channels before trying to re-derive standardness.
