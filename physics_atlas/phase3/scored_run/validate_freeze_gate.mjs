#!/usr/bin/env node
// validate_freeze_gate.mjs  (R7 — the executable freeze-gate validator)
//
// Physics Layer Atlas — machine freeze-gate validator.
//
// Reads CONTRACT.json (the single source of truth), theory_manifest.jsonl,
// edge_manifest.jsonl, and closure_card_manifest.jsonl, and enforces the
// freeze-gate predicate of CONTRACT.freeze_gate_predicate by comparing
// machine-checkable fields against CONTRACT.json (never against prose).
//
// Usage:
//   node validate_freeze_gate.mjs --mode freeze [--dir <prereg>]
//   node validate_freeze_gate.mjs --mode scored [--dir <prereg>]
//
//   --mode freeze : evaluate the provisional typing (provisional_tier_guess /
//                   provisional_modality_guess). This is the pre-scoring gate.
//   --mode scored : evaluate the scored typing (scored_tier / scored_modality,
//                   falling back to the modality guess if no scored modality is
//                   present). Adds the calibration-equality blocker (check 4b)
//                   and the anti-control-tier blocker.
//
// Every check COLLECTS all failures, prints them, and the process exits 1 if
// ANY failure was collected, 0 if the bundle is clean. No check is weakened:
// a missing artifact, a missing field, or an unresolved endpoint is a FAILURE,
// not a skip. Node built-ins only (fs, JSON.parse, line-split for jsonl).
//
// Where prose and CONTRACT.json disagree, this validator reads CONTRACT.json.
//
// Enforced checks (each ENFORCES a predicate the contract/rubric claim; the
// reviewer mutation-tested the prior validator and found scoring-time seams):
//   C1  — every edge endpoint resolves to a frozen card / registered node.
//   C2  — every edge modality is a CONTRACT.canonical_modalities member.
//   C3  — every (modality, tier) pair is emittable (modality_tier_compat).
//   C4  — calibration rows match the contract rule; [scored] must_seal_* blocker.
//   C5  — anti-controls carry must_not_seal_E1_or_E2 / E3; [scored] may not seal
//         E1/E2; HARDENED (R5): an anti-control sealing E0 must carry a non-empty
//         pre-frozen run_target_stub AND ALL FOUR E.7 interlock booleans true.
//   C6  — value_split fields conform to the schema; no E1-with-E1 collapse;
//         per-row frozen values match.
//   C7  — full §A closure card for every theory id AND every registered
//         candidate_substructure node (HARDENED per O1: all 9, not only sources).
//   C8  — node may_source_E1: no E1 sourced by a not-established node.
//   C9  (R4) — [scored] a near_intra_layer_check edge may not seal E1 unless
//              near_intra_layer_result == "passed".
//   C10 (R3) — value_split reported_tier == split-type rule's choice, and the
//              edge's headline tier may not silently report a NON-reported leg.
//   C11 (R2) — every recognition-landing edge is in affected_edges, carries
//              exactly one non-empty non-menu named_import.
//   C12 (R6) — any frozen registered-null tally equals the actual headline-tier
//              counts; and no frozen prose file carries an obsolete edge-count.
//   C13 (R-P2) — secondary recognition-conditional import-hygiene: every edge
//              carrying a SECONDARY "recognition-conditional" flag (in
//              secondary_modalities or conditionality_flags) at tier E2 — whose
//              PRIMARY modality stays structural — MUST carry exactly one
//              non-empty, non-menu named_import (the C11 hygiene applied to the
//              secondary flag). Disjoint from C11 (primary recognition-landing).

import { readFileSync } from 'node:fs';
import { join } from 'node:path';

// ---------------------------------------------------------------------------
// CLI parsing (deterministic, no external deps)
// ---------------------------------------------------------------------------
function parseArgs(argv) {
  const args = { mode: null, dir: null };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--mode') args.mode = argv[++i];
    else if (a === '--dir') args.dir = argv[++i];
    else if (a.startsWith('--mode=')) args.mode = a.slice('--mode='.length);
    else if (a.startsWith('--dir=')) args.dir = a.slice('--dir='.length);
  }
  return args;
}

const cli = parseArgs(process.argv.slice(2));
const MODE = cli.mode || 'freeze';
if (MODE !== 'freeze' && MODE !== 'scored') {
  console.error(`FATAL: --mode must be "freeze" or "scored" (got "${MODE}")`);
  process.exit(2);
}
// Default dir = the directory this script lives in (the prereg bundle).
const DIR = cli.dir || new URL('.', import.meta.url).pathname;

// ---------------------------------------------------------------------------
// Failure collector. Never throws past a check; every check appends here.
// ---------------------------------------------------------------------------
const failures = [];
function fail(code, msg) {
  failures.push({ code, msg });
}

// ---------------------------------------------------------------------------
// Loaders. A missing/unparseable required artifact is a FATAL load error that
// is itself recorded as a failure (the bundle cannot freeze without it).
// ---------------------------------------------------------------------------
function loadJSON(name, required = true) {
  const path = join(DIR, name);
  try {
    return JSON.parse(readFileSync(path, 'utf8'));
  } catch (e) {
    fail('LOAD', `cannot read/parse ${name} at ${path}: ${e.message}`);
    return required ? null : {};
  }
}

function loadJSONL(name, required = true) {
  const path = join(DIR, name);
  let text;
  try {
    text = readFileSync(path, 'utf8');
  } catch (e) {
    fail('LOAD', `cannot read ${name} at ${path}: ${e.message}`);
    return null;
  }
  const out = [];
  const lines = text.split('\n');
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    if (line.trim() === '') continue;
    try {
      out.push(JSON.parse(line));
    } catch (e) {
      fail('LOAD', `${name}:${i + 1} is not valid JSON: ${e.message}`);
    }
  }
  if (required && out.length === 0) {
    fail('LOAD', `${name} produced zero records (missing or empty)`);
  }
  return out;
}

const CONTRACT = loadJSON('CONTRACT.json', true);
const theories = loadJSONL('theory_manifest.jsonl', true) || [];
const edges = loadJSONL('edge_manifest.jsonl', true) || [];
const cards = loadJSONL('closure_card_manifest.jsonl', true) || [];

// If the contract itself failed to load we cannot run any contract-driven
// check; print what we have and bail out non-zero.
if (!CONTRACT) {
  for (const f of failures) console.error(`[${f.code}] ${f.msg}`);
  console.error(`\nFREEZE-GATE: FAIL (${failures.length} failure(s)) — CONTRACT.json unreadable`);
  process.exit(1);
}

// ---------------------------------------------------------------------------
// Helpers / indexes
// ---------------------------------------------------------------------------
function nonEmpty(v) {
  if (v === null || v === undefined) return false;
  if (typeof v === 'string') return v.trim().length > 0;
  if (Array.isArray(v)) return v.length > 0;
  if (typeof v === 'object') return Object.keys(v).length > 0;
  return true; // numbers, booleans
}

const theoryIds = new Set(theories.map((t) => t.id).filter(Boolean));
const cardIds = new Set(cards.map((c) => c.id).filter(Boolean));

// The frozen registered-node registry. Authoritative node ids come from the
// edge manifest's declared (id, node_kind) for every non-theory_card endpoint,
// and from CONTRACT.node_established_rule.frozen_statuses (the established
// candidate_substructure nodes). A node "resolves" iff it is declared with a
// node_kind in this set somewhere in the manifests.
const VALID_NODE_KINDS = new Set([
  'observable_readout',
  'open_question',
  'candidate_substructure',
]);

// Build the set of registered node ids = every endpoint id whose declared
// *_kind is a node_kind (not theory_card), keyed with its declared kinds.
const registeredNodes = new Map(); // id -> Set(node_kind)
for (const e of edges) {
  const pairs = [
    [e.source_theory_id, e.source_kind],
    [e.target_theory_id, e.target_kind],
  ];
  for (const [id, kind] of pairs) {
    if (kind && kind !== 'theory_card' && VALID_NODE_KINDS.has(kind)) {
      if (!registeredNodes.has(id)) registeredNodes.set(id, new Set());
      registeredNodes.get(id).add(kind);
    }
  }
}

// Frozen established_status map (candidate_substructure nodes).
const frozenStatuses =
  (CONTRACT.node_established_rule && CONTRACT.node_established_rule.frozen_statuses) || {};

const CANON_MODALITIES = new Set(CONTRACT.canonical_modalities || []);
const TIER_COMPAT = CONTRACT.modality_tier_compat || {};
const VALUE_SPLIT_SCHEMA = CONTRACT.value_split_schema || {};

// Tier of an edge under the active mode.
function tierOf(e) {
  return MODE === 'scored' ? e.scored_tier : e.provisional_tier_guess;
}
// Modality of an edge under the active mode (scored falls back to the guess).
function modalityOf(e) {
  if (MODE === 'scored' && nonEmpty(e.scored_modality)) return e.scored_modality;
  return e.provisional_modality_guess;
}

// Resolve a single endpoint id against frozen cards / theory ids / registered
// nodes. Returns true if it resolves.
function endpointResolves(id, kind) {
  if (kind === 'theory_card') {
    // A theory_card endpoint must resolve to a frozen closure-card id OR a
    // registered theory id (the manifest stub). Per the full-card freeze rule
    // a card is the authoritative frozen object; the theory id is its stub.
    return cardIds.has(id) || theoryIds.has(id);
  }
  // Node endpoint: must be declared with a valid node_kind, and that declared
  // kind must match what this edge claims.
  if (!VALID_NODE_KINDS.has(kind)) return false;
  return registeredNodes.has(id) && registeredNodes.get(id).has(kind);
}

// ===========================================================================
// CHECK 1 — every edge source/target id resolves to a frozen closure-card id
//           OR a registered node id (with a declared node_kind).
// ===========================================================================
for (const e of edges) {
  if (!nonEmpty(e.id)) {
    fail('C1', `edge with missing id: ${JSON.stringify(e).slice(0, 120)}`);
    continue;
  }
  if (!endpointResolves(e.source_theory_id, e.source_kind)) {
    fail(
      'C1',
      `${e.id}: source endpoint "${e.source_theory_id}" (kind=${e.source_kind}) ` +
        `does not resolve to a frozen card id or a registered node id`
    );
  }
  if (!endpointResolves(e.target_theory_id, e.target_kind)) {
    fail(
      'C1',
      `${e.id}: target endpoint "${e.target_theory_id}" (kind=${e.target_kind}) ` +
        `does not resolve to a frozen card id or a registered node id`
    );
  }
}

// ===========================================================================
// CHECK 2 — every edge modality is in CONTRACT.canonical_modalities.
// (Checked for the active-mode modality string.)
// ===========================================================================
for (const e of edges) {
  const m = modalityOf(e);
  if (!nonEmpty(m)) {
    fail('C2', `${e.id}: modality is empty (mode=${MODE})`);
  } else if (!CANON_MODALITIES.has(m)) {
    fail('C2', `${e.id}: modality "${m}" is not a canonical modality`);
  }
}

// ===========================================================================
// CHECK 3 — (modality, tier) is allowed by CONTRACT.modality_tier_compat.
// Uses provisional_tier_guess in --mode freeze, scored_tier in --mode scored.
// ===========================================================================
for (const e of edges) {
  const m = modalityOf(e);
  const t = tierOf(e);
  if (!nonEmpty(m) || !CANON_MODALITIES.has(m)) continue; // already failed C2
  if (!nonEmpty(t)) {
    fail('C3', `${e.id}: tier is empty (mode=${MODE}) — cannot check (modality,tier)`);
    continue;
  }
  const allowed = TIER_COMPAT[m];
  if (!Array.isArray(allowed)) {
    fail('C3', `${e.id}: no modality_tier_compat entry for modality "${m}"`);
  } else if (!allowed.includes(t)) {
    fail(
      'C3',
      `${e.id}: (modality=${m}, tier=${t}) is NOT emittable; ` +
        `allowed tiers for ${m} are [${allowed.join(', ')}]`
    );
  }
}

// ===========================================================================
// CHECK 4 — every is_calibration edge has a valid calibration_known_tier per
//           CONTRACT.calibration_rules; in --mode scored, scored_tier MUST
//           equal calibration_known_tier (the calibration blocker).
// ===========================================================================
const calibRules = new Map();
for (const r of CONTRACT.calibration_rules || []) calibRules.set(r.id, r);
const tierEnum = new Set(CONTRACT.value_split_schema?.form_tier_enum || ['E1', 'E2', 'E0', 'E3']);

for (const e of edges) {
  if (!e.is_calibration) continue;
  const rule = calibRules.get(e.id);
  if (!rule) {
    fail('C4', `${e.id}: is_calibration=true but no CONTRACT.calibration_rules entry exists`);
    continue;
  }
  // The edge's declared known tier must exist, be a valid tier, and match the
  // contract's frozen known tier for that id.
  if (!nonEmpty(e.calibration_known_tier)) {
    fail('C4', `${e.id}: is_calibration=true but calibration_known_tier is empty`);
  } else if (!tierEnum.has(e.calibration_known_tier)) {
    fail('C4', `${e.id}: calibration_known_tier "${e.calibration_known_tier}" is not a valid tier`);
  } else if (e.calibration_known_tier !== rule.calibration_known_tier) {
    fail(
      'C4',
      `${e.id}: calibration_known_tier "${e.calibration_known_tier}" != contract value ` +
        `"${rule.calibration_known_tier}"`
    );
  }
  // The edge's calibration_rule must match the contract's frozen rule.
  if (e.calibration_rule !== rule.calibration_rule) {
    fail(
      'C4',
      `${e.id}: calibration_rule "${e.calibration_rule}" != contract value "${rule.calibration_rule}"`
    );
  }
  // --mode scored: the calibration EQUALITY blocker for must_seal_* rules.
  if (MODE === 'scored' && typeof rule.calibration_rule === 'string' &&
      rule.calibration_rule.startsWith('must_seal_')) {
    if (!nonEmpty(e.scored_tier)) {
      fail('C4', `${e.id}: [scored] calibration edge has no scored_tier`);
    } else if (e.scored_tier !== rule.calibration_known_tier) {
      fail(
        'C4',
        `${e.id}: [scored] CALIBRATION BLOCKER — scored_tier "${e.scored_tier}" != ` +
          `calibration_known_tier "${rule.calibration_known_tier}"`
      );
    }
  }
}

// ===========================================================================
// CHECK 5 — anti-control edges (E018-E021) have must_not_seal_E1_or_E2=true and
//           calibration_known_tier=E3.
// The anti-control id set is taken from the contract (anti_control_rules).
// ===========================================================================
const antiControlIds = new Set(
  (CONTRACT.anti_control_rules?.must_not_seal_E1_or_E2?.current_anti_controls) || []
);
// The four E.7 double-run interlock booleans an E0-sealed anti-control MUST
// carry (read from the contract's machine schema; fall back to the frozen four
// if the schema is malformed so the fence can never be silently disabled).
const E7_INTERLOCK_BOOLEANS = (() => {
  const mf =
    CONTRACT.anti_control_rules?.e7_interlock_schema?.machine_fields;
  const keys = mf && typeof mf === 'object' ? Object.keys(mf) : [];
  const fallback = [
    'descent_test_logged_negative',
    'recognition_search_logged_negative',
    'non_descending_run_object_exhibited',
    'run_target_stub_frozen_pre_scoring',
  ];
  // run_target_stub_frozen_pre_scoring is a boolean alongside the non-empty
  // run_target_stub string requirement; the union of schema keys + fallback
  // guarantees all four are enforced even if the schema is edited.
  const set = new Set([...keys, ...fallback]);
  return [...set];
})();
const edgeById = new Map(edges.map((e) => [e.id, e]));
for (const id of antiControlIds) {
  const e = edgeById.get(id);
  if (!e) {
    fail('C5', `anti-control ${id} is declared in CONTRACT but absent from edge_manifest`);
    continue;
  }
  if (e.must_not_seal_E1_or_E2 !== true) {
    fail(
      'C5',
      `${id}: anti-control must carry must_not_seal_E1_or_E2=true (got ${JSON.stringify(e.must_not_seal_E1_or_E2)})`
    );
  }
  if (e.calibration_known_tier !== 'E3') {
    fail(
      'C5',
      `${id}: anti-control must carry calibration_known_tier=E3 (got ${JSON.stringify(e.calibration_known_tier)})`
    );
  }
  // In scored mode the anti-control's sealed tier must satisfy must_not_seal:
  // it may not seal E1/E2; allowed are {E3, E0}, and E0 only with a pre-frozen
  // run_target_stub AND the full E.7 double-run interlock (R5, hardened C5).
  if (MODE === 'scored') {
    const t = e.scored_tier;
    if (t === 'E1' || t === 'E2') {
      fail('C5', `${id}: [scored] ANTI-CONTROL BLOCKER — sealed tier ${t} violates must_not_seal_E1_or_E2`);
    } else if (t === 'E0') {
      // O4/R5 fence: a bare E0 label is NOT a doubt-haven. The contract
      // (anti_control_rules.e7_interlock_schema) requires a pre-frozen
      // non-empty run_target_stub AND all four interlock booleans present and
      // true. Any absent/false field demotes the edge to E3 -> freeze blocked.
      if (!nonEmpty(e.run_target_stub)) {
        fail(
          'C5',
          `${id}: [scored] anti-control sealed E0 without a pre-frozen non-empty run_target_stub ` +
            `(O4/R5 fence); must demote to E3`
        );
      }
      for (const b of E7_INTERLOCK_BOOLEANS) {
        if (e[b] !== true) {
          fail(
            'C5',
            `${id}: [scored] anti-control sealed E0 but E.7 interlock field "${b}" is ` +
              `${JSON.stringify(e[b])} (must be present and === true); a bare E0 is a ` +
              `conservative-default FAILURE -> demote to E3 (e7_interlock_schema, R5)`
          );
        }
      }
    } else if (t !== 'E3') {
      fail('C5', `${id}: [scored] anti-control sealed tier "${t}" is not in {E3, E0}`);
    }
  }
}

// ===========================================================================
// CHECK 6 — value_split fields conform to CONTRACT.value_split_schema
//           (valid split_type; no field sums E1 with E2/E0).
// The contract freezes per-row value_split content in
// value_split_schema.rows_carrying_value_split; each present split must match.
// ===========================================================================
const splitTypeEnum = new Set(VALUE_SPLIT_SCHEMA.split_type_enum || []);
const formTierEnum = new Set(VALUE_SPLIT_SCHEMA.form_tier_enum || []);
const valueTierEnum = new Set(VALUE_SPLIT_SCHEMA.value_tier_enum || []);
const frozenRows = VALUE_SPLIT_SCHEMA.rows_carrying_value_split || {};

for (const e of edges) {
  const vs = e.value_split;
  if (vs === null || vs === undefined) {
    // If the contract says this edge MUST carry a value_split, absence is a fail.
    if (Object.prototype.hasOwnProperty.call(frozenRows, e.id)) {
      fail('C6', `${e.id}: contract requires a value_split but the edge carries none`);
    }
    continue;
  }
  if (typeof vs !== 'object' || Array.isArray(vs)) {
    fail('C6', `${e.id}: value_split must be an object`);
    continue;
  }
  // form_tier / value_tier present and valid.
  if (!nonEmpty(vs.form_tier) || !formTierEnum.has(vs.form_tier)) {
    fail('C6', `${e.id}: value_split.form_tier "${vs.form_tier}" not in form_tier_enum`);
  }
  if (!nonEmpty(vs.value_tier) || !valueTierEnum.has(vs.value_tier)) {
    fail('C6', `${e.id}: value_split.value_tier "${vs.value_tier}" not in value_tier_enum`);
  }
  // split_type: must be present and a valid enum member.
  if (!nonEmpty(vs.split_type)) {
    fail('C6', `${e.id}: value_split is missing required split_type`);
  } else if (!splitTypeEnum.has(vs.split_type)) {
    fail('C6', `${e.id}: value_split.split_type "${vs.split_type}" is not a valid split_type`);
  }
  // value_node must be present (non-empty).
  if (!nonEmpty(vs.value_node)) {
    fail('C6', `${e.id}: value_split is missing required value_node`);
  }
  // NO-SUMMING WITHIN EDGE: form_tier and value_tier are on separate ledgers.
  // The forbidden situation is a value_split that *collapses* the two tiers
  // into one summed ledger. We enforce the structural invariant the contract
  // states: when form_tier==E1, the value_tier MUST be carried separately (be
  // a different ledger, i.e. E2/E0/E3, never silently E1-and-summed). An E1
  // form_tier paired with an E1 value_tier would be a single un-split ledger
  // masquerading as a split — reject it (it would let E0/E2 content be summed
  // into the E1 count via the form leg).
  if (vs.form_tier === 'E1' && vs.value_tier === 'E1') {
    fail(
      'C6',
      `${e.id}: value_split sums E1 with E1 (form_tier=E1, value_tier=E1) — a split must carry ` +
        `the value on a SEPARATE ledger, never summed into the E1 form leg`
    );
  }
  // Cross-check against the frozen per-row contract values, when present.
  const frozen = frozenRows[e.id];
  if (frozen) {
    for (const k of ['form_tier', 'value_tier', 'split_type', 'value_node']) {
      if (vs[k] !== frozen[k]) {
        fail(
          'C6',
          `${e.id}: value_split.${k} "${vs[k]}" != frozen contract value "${frozen[k]}"`
        );
      }
    }
  }
}

// ===========================================================================
// CHECK 7 — full-card freeze: every theory id AND every casting-bearing node
//           id has a full §A closure card with all required fields non-empty.
// Required §A fields are taken from CONTRACT.full_card_freeze_rule.rule prose,
// frozen here as the §A schema. Casting-bearing nodes = candidate_substructure
// nodes that act as an edge SOURCE (they contribute a Z/f/Σ_f to the descent).
// ===========================================================================
const REQUIRED_CARD_FIELDS = [
  'id',
  'Z',
  'f',
  'Sigma_f',
  'E',
  'D',
  'accepted_observables',
  'lawful_layer_note',
  'casting_justification',
  'casting_alternatives',
  'status',
];

// Index cards by id (first wins; duplicates are a fail).
const cardById = new Map();
for (const c of cards) {
  if (!nonEmpty(c.id)) {
    fail('C7', `closure_card_manifest.jsonl: card with missing id: ${JSON.stringify(c).slice(0, 120)}`);
    continue;
  }
  if (cardById.has(c.id)) {
    fail('C7', `closure_card_manifest.jsonl: duplicate card id "${c.id}"`);
  } else {
    cardById.set(c.id, c);
  }
}

// The ids that MUST have a full frozen card (HARDENED per O1):
//   (a) every theory id;
//   (b) EVERY registered candidate_substructure node — whether it is an edge
//       SOURCE or only a TARGET. The reviewer asked (O1) that a target-only
//       card cannot be silently deleted; the registry is the union of every
//       candidate_substructure endpoint declared in the edge manifest AND every
//       node frozen in CONTRACT.node_established_rule.frozen_statuses.
const mustHaveCard = new Set(theoryIds);
for (const e of edges) {
  if (e.source_kind === 'candidate_substructure') mustHaveCard.add(e.source_theory_id);
  if (e.target_kind === 'candidate_substructure') mustHaveCard.add(e.target_theory_id);
}
for (const id of Object.keys(frozenStatuses)) mustHaveCard.add(id);

for (const id of mustHaveCard) {
  const c = cardById.get(id);
  if (!c) {
    fail('C7', `no full §A closure card frozen for "${id}" (required by full_card_freeze_rule)`);
    continue;
  }
  for (const field of REQUIRED_CARD_FIELDS) {
    if (!nonEmpty(c[field])) {
      fail('C7', `closure card "${id}": required §A field "${field}" is empty/missing`);
    }
  }
  // A card whose status is not "frozen" is not freeze-eligible.
  if (nonEmpty(c.status) && c.status !== 'frozen') {
    fail('C7', `closure card "${id}": status "${c.status}" != "frozen" (not freeze-eligible)`);
  }
}

// ===========================================================================
// CHECK 8 — node may_source_E1 rule: no E1 edge is sourced by a node with
//           established_status != experimentally_established.
// Applies to candidate_substructure sources (theory cards are trivially
// experimentally_established). The established_status is read from
// CONTRACT.node_established_rule.frozen_statuses.
// ===========================================================================
for (const e of edges) {
  const t = tierOf(e);
  if (t !== 'E1') continue;
  if (e.source_kind !== 'candidate_substructure') continue; // cards are established
  const status = frozenStatuses[e.source_theory_id];
  if (!status) {
    fail(
      'C8',
      `${e.id}: E1 sourced by candidate_substructure "${e.source_theory_id}" with no frozen ` +
        `established_status in CONTRACT.node_established_rule.frozen_statuses`
    );
  } else if (status.established_status !== 'experimentally_established') {
    fail(
      'C8',
      `${e.id}: E1 may NOT be sourced by "${e.source_theory_id}" ` +
        `(established_status="${status.established_status}"); re-type to E2/E0/E3 or promote the node`
    );
  }
}

// ===========================================================================
// CHECK 9 (R4) — near-intra-layer gate E.4/E.11.
// In --mode scored, an edge with near_intra_layer_check == true and
// scored_tier == "E1" FAILS unless near_intra_layer_result == "passed".
// (The reviewer's mutation test 1: a scored copy that sets every
// scored_tier=provisional but leaves E016/E017/E039 unresolved E1 must FAIL.)
//
// near_intra_layer_check is read as a strict boolean true. The frozen manifest
// currently carries a legacy free-text "PENDING_E4: ..." STRING on these rows
// (a human note); per CONTRACT.near_intra_layer_schema the validator reads the
// MACHINE fields near_intra_layer_check (boolean) + near_intra_layer_result
// (enum). A non-empty near_intra_layer marker (boolean true OR a non-empty
// PENDING_E4 string) flags the row as subject to the gate; the only way an
// E1-sealed flagged row passes is an explicit near_intra_layer_result=="passed".
// ===========================================================================
const NEAR_INTRA_RESULT_ENUM = new Set(
  (CONTRACT.near_intra_layer_schema?.machine_fields?.near_intra_layer_result?.enum) ||
    ['pending', 'passed', 'failed']
);
function isNearIntraFlagged(e) {
  const v = e.near_intra_layer_check;
  if (v === true) return true;
  // Legacy free-text marker still present on the frozen rows: a non-empty
  // string flag also subjects the row to the gate (never a silent skip).
  if (typeof v === 'string' && v.trim().length > 0) return true;
  return false;
}
for (const e of edges) {
  if (!isNearIntraFlagged(e)) continue;
  // The result enum must be present and valid when the row is flagged.
  const res = e.near_intra_layer_result;
  if (nonEmpty(res) && !NEAR_INTRA_RESULT_ENUM.has(res)) {
    fail(
      'C9',
      `${e.id}: near_intra_layer_result "${res}" is not a valid enum ` +
        `(${[...NEAR_INTRA_RESULT_ENUM].join(', ')})`
    );
  }
  if (MODE !== 'scored') continue; // the seal-time blocker is a scored-mode gate
  const t = e.scored_tier;
  if (t === 'E1' && res !== 'passed') {
    fail(
      'C9',
      `${e.id}: [scored] near-intra-layer row sealed E1 but near_intra_layer_result=` +
        `${JSON.stringify(res)} (must be "passed"); a pending/failed gate-E.4 row may NOT ` +
        `count as a sealed E1 (R4 / near_intra_layer_schema)`
    );
  }
}

// ===========================================================================
// CHECK 10 (R3) — value_split reported_tier consistency.
// For every edge carrying a value_split:
//   (a) the contract's split-type rule choice (value_tier for
//       form_value/form_value_imported, form_tier for theorem_run) is computed
//       and the per-row frozen reported_tier (when present) MUST equal it;
//   (b) the edge's HEADLINE tier (provisional_tier_guess in freeze, scored_tier
//       in scored) MUST NOT silently report a NON-reported value_split leg as
//       the edge's closure: for form_value/form_value_imported the headline may
//       not be the form_tier leg; for theorem_run the headline MUST equal the
//       form_tier (the reported leg). Where the contract freezes a per-row
//       edge_scored_tier, the headline must equal it.
// This is the narrow invariant CONTRACT.value_split_schema.headline_tier_invariant
// states (an audited edge tier such as E029->E2 is NOT a value_split leg and is
// allowed; only reporting the WRONG leg is rejected). (Reviewer mutation test 4:
// row tier == the non-reported value_split leg must FAIL here.)
// ===========================================================================
const REPORTED_BY_SPLIT =
  CONTRACT.value_split_schema?.reported_tier_rule?.reported_tier_by_split_type || {};
const FROZEN_VS_ROWS = CONTRACT.value_split_schema?.rows_carrying_value_split || {};
for (const e of edges) {
  const vs = e.value_split;
  if (vs === null || vs === undefined || typeof vs !== 'object' || Array.isArray(vs)) continue;
  const st = vs.split_type;
  if (!nonEmpty(st)) continue; // C6 already flags missing split_type
  const ruleChoice = REPORTED_BY_SPLIT[st]; // "value_tier" | "form_tier"
  if (ruleChoice !== 'value_tier' && ruleChoice !== 'form_tier') {
    fail(
      'C10',
      `${e.id}: split_type "${st}" has no reported_tier_by_split_type rule in CONTRACT ` +
        `(cannot determine the reported leg)`
    );
    continue;
  }
  const reportedLegTier = vs[ruleChoice]; // the actual tier value of the reported leg

  // (a) reported_tier consistency. The reported_tier the contract/edge carry for
  // this row MUST equal the split-type rule's choice (value_tier for
  // form_value/form_value_imported, form_tier for theorem_run). This catches a
  // reported_tier that silently disagrees with its own split-type rule (R3,
  // reviewer mutation test 4). Both the EDGE's value_split.reported_tier (when
  // present) and the CONTRACT's frozen reported_tier are checked.
  const frozen = FROZEN_VS_ROWS[e.id];
  if (Object.prototype.hasOwnProperty.call(vs, 'reported_tier')) {
    if (vs.reported_tier !== reportedLegTier) {
      fail(
        'C10',
        `${e.id}: edge value_split.reported_tier "${vs.reported_tier}" != the split-type rule's ` +
          `choice (${ruleChoice}="${reportedLegTier}") for split_type "${st}" (R3)`
      );
    }
  }
  if (frozen && Object.prototype.hasOwnProperty.call(frozen, 'reported_tier')) {
    // The contract row's frozen reported_tier must agree with the contract row's
    // OWN split_type rule choice (uses the contract row's split_type/legs).
    const fSt = frozen.split_type;
    const fChoice = REPORTED_BY_SPLIT[fSt];
    const fLegTier = (fChoice === 'value_tier' || fChoice === 'form_tier') ? frozen[fChoice] : undefined;
    if (fLegTier !== undefined && frozen.reported_tier !== fLegTier) {
      fail(
        'C10',
        `${e.id}: contract reported_tier "${frozen.reported_tier}" != the split-type rule's ` +
          `choice (${fChoice}="${fLegTier}") for contract split_type "${fSt}" (R3)`
      );
    }
  }

  // (b) The edge's HEADLINE tier (provisional_tier_guess in freeze, scored_tier
  // in scored) must equal the contract's authoritative frozen edge_scored_tier
  // for the row, when the contract freezes one. This is the contract's
  // headline_tier_invariant operationalized: the headline may be the reported
  // leg (E041 theorem_run -> form E3), the form leg for a descent row whose
  // closure IS the descent (E004/E008/E035a/E038 -> E1), or an audited
  // edge-modality tier that is neither leg (E029 -> E2). The single rejected
  // case is a headline that disagrees with the frozen per-row headline (a row
  // silently reporting the WRONG leg as its closure). (Reviewer mutation test 4.)
  const headline = tierOf(e);
  if (!nonEmpty(headline)) continue; // tier-empty already flagged by C3/C4
  if (frozen && Object.prototype.hasOwnProperty.call(frozen, 'edge_scored_tier')) {
    if (headline !== frozen.edge_scored_tier) {
      fail(
        'C10',
        `${e.id}: [${MODE}] headline tier "${headline}" != contract frozen edge_scored_tier ` +
          `"${frozen.edge_scored_tier}" (value_split row; the headline may not silently report a ` +
          `NON-reported leg as the edge's closure — R3 / headline_tier_invariant)`
      );
    }
  } else if (st === 'theorem_run') {
    // No frozen per-row headline: for theorem_run the reported (headline) leg is
    // the form_tier; the run-exhibited value leg is never the headline.
    if (headline !== reportedLegTier) {
      fail(
        'C10',
        `${e.id}: [${MODE}] theorem_run headline tier "${headline}" != reported leg ` +
          `(form_tier="${reportedLegTier}"); the run-exhibited value leg is never the headline ` +
          `(R3 / headline_tier_invariant)`
      );
    }
  }
}

// ===========================================================================
// CHECK 11 (R2) — recognition-landing named_import.
// Every edge whose ACTIVE-MODE modality == "recognition-landing":
//   (i)   is listed in CONTRACT.recognition_resolution.affected_edges
//         (the rule-driven set; the validator also asserts every id in
//          affected_edges is a recognition-landing row in the manifest);
//   (ii)  carries EXACTLY ONE non-empty named_import (a single string, or a
//         single-element array — an array of >1 is a menu);
//   (iii) that named_import is NOT a menu: no "or"-alternation, no
//         "to be frozen"/"choose one" placeholder, no 3+-way "/"-separated
//         enumeration (the old E007 "Gleason / envariance / decision-theoretic"
//         signature). A 2-way "/" "aka" compound (e.g. "einselection /
//         predictability-sieve criterion") is a SINGLE frozen principle and is
//         NOT a menu. The contract's frozen import for the row is also checked
//         for the same menu signatures.
// (Reviewer mutation test 3: a recognition row with no/menu named_import fails.)
// ===========================================================================
const recogResolution = CONTRACT.recognition_resolution || {};
const affectedEdges = new Set(recogResolution.affected_edges || []);
const frozenNamedImports = recogResolution.affected_edges_named_imports || {};

// Menu signature detector. `s` is a single string.
function isMenuString(s) {
  if (typeof s !== 'string') return true; // anything non-string in import position is suspect
  const lower = s.toLowerCase();
  // (1) explicit alternation word "or" as a separator (word-bounded).
  if (/\bor\b/.test(lower)) return true;
  // (2) placeholder / "to be frozen" / "choose one" / "tbd" markers.
  if (/\bto be frozen\b|\bone to be frozen\b|\bchoose one\b|\btbd\b|\beither\b/.test(lower)) {
    return true;
  }
  // (3) a 3+-way "/"-separated enumeration (the old menu signature). A 2-way
  // slash "aka" compound is allowed (a single principle with two names).
  if (s.split(/\s\/\s/).length >= 3) return true;
  return false;
}
// Extract the single named_import of an edge, or null if zero/multiple.
function singleNamedImport(e) {
  const ni = e.named_import;
  if (Array.isArray(ni)) {
    const items = ni.filter((x) => nonEmpty(x));
    if (items.length !== 1) return { ok: false, reason: `array of ${items.length} imports (menu)` };
    return { ok: true, value: items[0] };
  }
  if (typeof ni === 'string') {
    if (!nonEmpty(ni)) return { ok: false, reason: 'empty named_import' };
    return { ok: true, value: ni };
  }
  if (ni === null || ni === undefined) return { ok: false, reason: 'missing named_import' };
  return { ok: false, reason: `named_import is not a string/array (${typeof ni})` };
}

const recognitionRowIds = new Set();
for (const e of edges) {
  const m = modalityOf(e);
  if (m !== 'recognition-landing') continue;
  recognitionRowIds.add(e.id);
  // (i) membership in affected_edges.
  if (!affectedEdges.has(e.id)) {
    fail(
      'C11',
      `${e.id}: recognition-landing row is NOT listed in ` +
        `recognition_resolution.affected_edges (R2: a stale list is rejected)`
    );
  }
  // (ii) exactly one non-empty named_import.
  const si = singleNamedImport(e);
  if (!si.ok) {
    fail('C11', `${e.id}: recognition-landing row must carry exactly one named_import — ${si.reason}`);
  } else if (isMenuString(si.value)) {
    // (iii) the edge's import is a menu.
    fail(
      'C11',
      `${e.id}: recognition-landing named_import is a MENU (alternation/placeholder/3+-way "/"), ` +
        `not a single frozen principle: "${si.value.slice(0, 80)}..."`
    );
  }
  // (iii') the CONTRACT's frozen import for the row must also be a single
  // non-menu principle (catches a menu re-introduced on the contract side).
  if (Object.prototype.hasOwnProperty.call(frozenNamedImports, e.id)) {
    const fi = frozenNamedImports[e.id];
    if (!nonEmpty(fi)) {
      fail('C11', `${e.id}: contract affected_edges_named_imports entry is empty`);
    } else if (isMenuString(fi)) {
      fail(
        'C11',
        `${e.id}: contract frozen named_import is a MENU (alternation/placeholder/3+-way "/"): ` +
          `"${String(fi).slice(0, 80)}..."`
      );
    }
  } else {
    fail(
      'C11',
      `${e.id}: recognition-landing row has no frozen import in ` +
        `recognition_resolution.affected_edges_named_imports`
    );
  }
}
// Conversely: every id declared in affected_edges MUST be a recognition-landing
// row in the manifest (a stale enumeration is rejected).
for (const id of affectedEdges) {
  if (!recognitionRowIds.has(id)) {
    const e = edgeById.get(id);
    const got = e ? modalityOf(e) : '(absent from manifest)';
    fail(
      'C11',
      `affected_edges lists "${id}" but its manifest modality is "${got}" (not recognition-landing); ` +
        `affected_edges is rule-driven and must equal the recognition-landing set (R2)`
    );
  }
}

// ===========================================================================
// CHECK 12 (R6) — registered-null tally consistency + stale-prose guard.
// (a) If the contract freezes a registered-null tally (any of a small set of
//     plausible keys, each a {tier: count} map), it MUST equal the actual
//     headline-tier counts of the edge manifest (provisional_tier_guess in
//     freeze, scored_tier in scored). A frozen tally that disagrees fails.
// (b) Stale-count guard: every FROZEN prose file (edge_manifest_notes.md,
//     SCIENCE_DIGEST.md, TYPING_RUBRIC.md, FREEZE_NOTES.md) is scanned for an
//     obsolete edge-count string ("44 edge"/"44 edges"); any occurrence fails
//     (the registered null + no-summing ledger are part of the freeze, so a
//     stale edge count is a firewall drift, not cosmetic).
// ===========================================================================
// (a) Actual headline-tier counts.
// CHARGEABLE-COUNT EXCLUSION (R1, minimal non-weakening edit): rows flagged
// excluded_from_foreclosure_count===true are "within-a-layer, no SBT content"
// sentinels (gate-E.4 failed; carried as scored_tier:"E3" only as a schema
// label) and are NOT ordinary E3 foreclosure gaps. They are SKIPPED from the
// chargeable foreclosure tally so the scored-null tally is the inter-layer
// chargeable distribution (E1=17,E2=13,E0=4,E3=10). No other check changes.
const actualTierCounts = {};
for (const e of edges) {
  if (e.excluded_from_foreclosure_count === true) continue;
  const t = tierOf(e);
  if (!nonEmpty(t)) continue; // tier-empty rows already flagged by C3/C4
  actualTierCounts[t] = (actualTierCounts[t] || 0) + 1;
}
// A frozen tally may live under any of these keys (the Prose agent may add it).
//
// SCORED-NULL DRIFT HANDLING (minimal, non-weakening — Phase-3 scored run):
// The FROZEN CONTRACT.registered_null is the PRE-AUDIT PREDICTION; scored tiers
// are allowed to DRIFT from it. So the tally key checked here is MODE-DEPENDENT:
//   - --mode freeze : check the registered_null prediction against
//                     provisional_tier_guess (the pre-scoring gate, UNCHANGED).
//   - --mode scored : check CONTRACT.scored_registered_null (the recorded scored
//                     null) against scored_tier. Drift from the prediction is
//                     allowed, but the RECORDED scored null must still equal the
//                     manifest's scored headline-tier counts (no weakening: a
//                     scored null that disagrees with the manifest still FAILS).
// This is the only behavioural change vs. the freeze validator; every other
// check is byte-identical. In scored mode the registered_null PREDICTION is NOT
// enforced against the (drifted) scored counts — that is the intended drift.
const TALLY_CANDIDATE_KEYS = MODE === 'scored'
  ? [
      'scored_registered_null',
      'scored_registered_null_counts',
      'scored_registered_null_tally',
      'scored_registered_null_tallies',
    ]
  : [
      'registered_null',
      'registered_null_counts',
      'registered_null_tally',
      'registered_null_tallies',
    ];
function asTierCountMap(obj) {
  // Accepts {E1: n, E2: n, ...} possibly nested under a "counts"/"tally" field.
  if (!obj || typeof obj !== 'object' || Array.isArray(obj)) return null;
  const TIERS = CONTRACT.tier_order || ['E1', 'E2', 'E0', 'E3'];
  const direct = {};
  let any = false;
  for (const tier of TIERS) {
    if (typeof obj[tier] === 'number') {
      direct[tier] = obj[tier];
      any = true;
    }
  }
  if (any) return direct;
  for (const sub of ['counts', 'tally', 'tier_counts', 'by_tier']) {
    if (obj[sub] && typeof obj[sub] === 'object') {
      const m = asTierCountMap(obj[sub]);
      if (m) return m;
    }
  }
  return null;
}
for (const key of TALLY_CANDIDATE_KEYS) {
  if (!Object.prototype.hasOwnProperty.call(CONTRACT, key)) continue;
  const tally = asTierCountMap(CONTRACT[key]);
  if (!tally) continue; // present but not a tier-count map (e.g. the caveat prose object) — skip
  const TIERS = CONTRACT.tier_order || ['E1', 'E2', 'E0', 'E3'];
  for (const tier of TIERS) {
    const claimed = tally[tier];
    if (typeof claimed !== 'number') continue;
    const actual = actualTierCounts[tier] || 0;
    if (claimed !== actual) {
      fail(
        'C12',
        `CONTRACT.${key} tier ${tier} count ${claimed} != actual edge_manifest ${MODE} ` +
          `headline-tier count ${actual} (R6)`
      );
    }
  }
}
// (b) Stale-count guard over the frozen prose files.
const FROZEN_PROSE_FILES = [
  'edge_manifest_notes.md',
  'SCIENCE_DIGEST.md',
  'TYPING_RUBRIC.md',
  'FREEZE_NOTES.md',
];
const STALE_EDGE_COUNT_RE = /\b44\s+edges?\b/gi;
for (const fname of FROZEN_PROSE_FILES) {
  let text;
  try {
    text = readFileSync(join(DIR, fname), 'utf8');
  } catch (err) {
    fail('C12', `cannot read frozen prose file ${fname} for the stale-count guard: ${err.message}`);
    continue;
  }
  const lines = text.split('\n');
  for (let i = 0; i < lines.length; i++) {
    if (STALE_EDGE_COUNT_RE.test(lines[i])) {
      fail(
        'C12',
        `${fname}:${i + 1} contains an obsolete edge-count string "${lines[i].trim().slice(0, 90)}" ` +
          `(prose count drifted from the ${edges.length}-edge manifest; R6)`
      );
    }
    STALE_EDGE_COUNT_RE.lastIndex = 0; // reset the /g regex between lines
  }
}

// ===========================================================================
// CHECK 13 (R-P2) — secondary recognition-conditional named_import hygiene.
// The import-hygiene PARALLEL of C11 for the SECONDARY recognition-conditional
// case (CONTRACT.secondary_modality_schema.import_hygiene_parallel_check).
//
// Per the Pause-2 modality_precedence_rule (option b), a STRUCTURAL E2 edge may
// keep its structural PRIMARY modality (the existing 'modality' field) yet still
// require a named external import to close; it records 'recognition-conditional'
// as a SECONDARY flag (in secondary_modalities and/or conditionality_flags).
// Such an edge is NOT a primary recognition-landing (so it is NOT covered by
// C11 — the two sets are disjoint per modality_precedence_rule.discriminator),
// but the SAME named-import hygiene must hold: the row MUST carry exactly ONE
// non-empty named_import, a SINGLE frozen principle, NOT a menu (no
// "or"-alternation, no "to be frozen"/"choose one" placeholder, no 3+-way
// "/"-separated enumeration), not substitutable at typing time (gate E.0).
//
// Scope (per the contract): every edge at tier E2 whose secondary_modalities OR
// conditionality_flags contains 'recognition-conditional'. The PRIMARY modality
// is read via modalityOf (the existing 'modality' field) ONLY to assert the two
// sets are disjoint (a primary recognition-landing row is C11's, not C13's); the
// secondary flag itself — never the primary field — is what triggers this check.
// (Currently applies to E005; fences any future structural-E2 edge that declares
// a named import dependency via the secondary recognition-conditional flag.)
// ===========================================================================
const SECONDARY_FLAG_VALUE = 'recognition-conditional';
function carriesRecognitionConditional(e) {
  const sm = e.secondary_modalities;
  const cf = e.conditionality_flags;
  const inArr = (a) => Array.isArray(a) && a.includes(SECONDARY_FLAG_VALUE);
  return inArr(sm) || inArr(cf);
}
for (const e of edges) {
  if (!carriesRecognitionConditional(e)) continue;
  // The flag is meaningful only at tier E2 (the structural-E2 conditional case).
  // Read the active-mode tier; a non-E2 tier carrying the flag is itself a
  // contract violation (the secondary flag is defined for structural E2 rows).
  const t = tierOf(e);
  if (t !== 'E2') {
    fail(
      'C13',
      `${e.id}: carries a SECONDARY 'recognition-conditional' flag but its ` +
        `${MODE} tier is "${t}" (not E2); the recognition-conditional flag is defined ` +
        `only for structural-E2 edges (secondary_modality_schema.import_hygiene_parallel_check)`
    );
    continue;
  }
  // Disjointness from C11: a SECONDARY recognition-conditional flag may NOT sit on
  // a row whose PRIMARY modality is itself recognition-landing (that row is a C11
  // primary recognition-landing, never a structural-primary carrying the flag —
  // see modality_precedence_rule.discriminator). The primary modality is the
  // existing 'modality' field (read via modalityOf), unaffected by the secondary.
  const primaryModality = modalityOf(e);
  if (primaryModality === 'recognition-landing') {
    fail(
      'C13',
      `${e.id}: PRIMARY modality is recognition-landing yet the row also carries a ` +
        `SECONDARY 'recognition-conditional' flag; the two are mutually exclusive ` +
        `(a primary recognition-landing is C11's, not a structural-primary C13 row — ` +
        `modality_precedence_rule.discriminator)`
    );
  }
  // The C11 hygiene, applied to the secondary flag: exactly one non-empty,
  // non-menu named_import frozen on the row.
  const si = singleNamedImport(e);
  if (!si.ok) {
    fail(
      'C13',
      `${e.id}: secondary recognition-conditional E2 row must carry exactly one ` +
        `named_import — ${si.reason} (import-hygiene parallel of C11; ` +
        `secondary_modality_schema.import_hygiene_parallel_check)`
    );
  } else if (isMenuString(si.value)) {
    fail(
      'C13',
      `${e.id}: secondary recognition-conditional named_import is a MENU ` +
        `(alternation/placeholder/3+-way "/"), not a single frozen principle: ` +
        `"${si.value.slice(0, 80)}..." (C13, import-hygiene parallel of C11)`
    );
  }
}

// ---------------------------------------------------------------------------
// Report and exit.
// ---------------------------------------------------------------------------
const CODE_ORDER = ['LOAD', 'C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'C9', 'C10', 'C11', 'C12', 'C13'];
failures.sort((a, b) => {
  const ai = CODE_ORDER.indexOf(a.code);
  const bi = CODE_ORDER.indexOf(b.code);
  if (ai !== bi) return ai - bi;
  return a.msg < b.msg ? -1 : a.msg > b.msg ? 1 : 0;
});

console.log(`Physics Layer Atlas — freeze-gate validator`);
console.log(`mode=${MODE}  dir=${DIR}`);
console.log(
  `loaded: ${theories.length} theory stub(s), ${edges.length} edge(s), ${cards.length} closure card(s)`
);
console.log('');

if (failures.length === 0) {
  console.log(`FREEZE-GATE: PASS — all checks clean (mode=${MODE})`);
  process.exit(0);
}

const byCode = {};
for (const f of failures) {
  console.log(`[${f.code}] ${f.msg}`);
  byCode[f.code] = (byCode[f.code] || 0) + 1;
}
console.log('');
console.log(
  `FREEZE-GATE: FAIL — ${failures.length} failure(s): ` +
    CODE_ORDER.filter((c) => byCode[c]).map((c) => `${c}=${byCode[c]}`).join(' ')
);
process.exit(1);
