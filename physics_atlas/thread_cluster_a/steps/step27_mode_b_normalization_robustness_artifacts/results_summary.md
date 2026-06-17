# Step 27 Results Summary

Deflationary truth first: Step 26's `3/8` is a toy sector-trace result, not a physical chiral-fermion-multiplet trace. Step 27 adversarially varies the trace/readout conventions on the same Step-23 generated structure and finds convention-dependence. The generated structure and Step-21 comparison relation are read from prior artifacts; they are not Step-27 primitives.

## Convention Sweep

Generated structure under stress:

- structure: `r1|2`
- ranks: `1|2`
- dimensions: `2|3`
- selected charge vector: `3|-2`

Convention results:

| Convention | Charge rule | T3 readout | `sin^2(theta_W)` | Matches Step-21 target? |
|---|---|---|---:|---|
| `product_charge__rank_one_t3` | product of dimensions | unique rank-one factor | `3/8` | true |
| `lattice_lcm_charge__rank_one_t3` | lcm of dimensions | unique rank-one factor | `3/8` | true |
| `total_slots_charge__rank_one_t3` | total slot count | unique rank-one factor | `5/17` | false |
| `integer_weight_charge__rank_one_t3` | integer weights | unique rank-one factor | `1/61` | false |
| `product_charge__alternate_t3` | product of dimensions | first non-rank-one factor | `9/19` | false |
| `product_charge__all_factor_t3` | product of dimensions | all factors | `3/5` | false |

There is a real can-fail: four of six conventions flip the value, including one equally simple natural charge-unit convention (`total_slots_charge__rank_one_t3`). The baseline value is not invariant across the declared toy-trace convention family.

## Residual-Smuggle Hunt

- Charge-unit denominator: load-bearing. Product/lcm preserve `3/8` on the generated row; total-slot normalization flips it to `5/17`.
- T3 readout selection: load-bearing. Selecting a non-rank-one readout flips to `9/19`; using all factors flips to `3/5`.
- Hidden all-structure forcing: not found. Non-generated controls never reproduce the Step-21 target across the convention family.

## Consequence Consistency

The F51 parent-shadow consequences remain on the same generated structure:

- Step-25 `SU(5)` exact parent-shadow row: charged/full obstruction `0/0`, same child dimensions.
- Step-25 `SO(10)` scoped parent row: charged/full obstruction `0/1`, same child dimensions.

So the F51 hierarchy and neutral-residual consequence remain consistent with the structure being stress-tested. The normalization fragility is a trace-convention issue, not a mismatch between Step 26 and Step 25.

## Gates

- Primitive exclusion: pass. Target relation and generated structure are read from prior artifacts, not used as carrier literals.
- Convention can-fail: pass. The convention family contains both matching and flipping rows.
- Negative controls: pass. Non-generated structures never reproduce the target under the convention family.
- Consequence consistency: pass. Step-25 rows use the same generated child dimensions.
- Stage II: pass. Charge quantization persists on the generated row.
- No single-axiom equivalence: pass. Convention variation shows the toy trace convention is load-bearing.

## Verdict

`FRAGILE_CONVENTION_DEPENDENT`: the Step-26 integrated normalization is not robust across the declared toy-trace convention family. The next grammar delta is to replace the toy sector trace with a physical chiral-multiplet trace, or to add a principled rule selecting the trace convention.

This is a hardening result, not a wall. It preserves the generated shape and the F51 hierarchy while sharply bounding the normalization claim.
