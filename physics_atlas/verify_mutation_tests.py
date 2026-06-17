#!/usr/bin/env python3
"""Independent re-run of the external reviewer's mutation tests against the hardened
freeze-gate validator. For each mutation we build a scored copy of the prereg bundle,
perturb ONE thing, run the validator in --mode scored, and require it to EXIT NONZERO.
A 'valid scored baseline' must pass first, so each failure is attributable to the mutation."""
import json, os, shutil, subprocess, sys, tempfile

OUT = os.environ.get("PREREG_DIR") or os.path.join(os.path.dirname(os.path.abspath(__file__)), "prereg")
COPY = ["CONTRACT.json", "theory_manifest.jsonl", "edge_manifest.jsonl",
        "closure_card_manifest.jsonl", "validate_freeze_gate.mjs",
        # C12's stale-prose guard reads these frozen prose files:
        "FREEZE_NOTES.md", "SCIENCE_DIGEST.md", "TYPING_RUBRIC.md", "edge_manifest_notes.md"]

def load_edges():
    with open(os.path.join(OUT, "edge_manifest.jsonl")) as f:
        return [json.loads(l) for l in f if l.strip()]

def run(edges, mode="scored"):
    d = tempfile.mkdtemp(prefix="mut_")
    for fn in COPY:
        shutil.copy(os.path.join(OUT, fn), os.path.join(d, fn))
    with open(os.path.join(d, "edge_manifest.jsonl"), "w") as f:
        for e in edges:
            f.write(json.dumps(e) + "\n")
    p = subprocess.run(["node", os.path.join(d, "validate_freeze_gate.mjs"),
                        "--mode", mode, "--dir", d],
                       capture_output=True, text=True)
    shutil.rmtree(d, ignore_errors=True)
    return p.returncode, (p.stdout + p.stderr)

def scored_baseline():
    """All scored_*=provisional; near-intra rows marked passed; calibration scored=known."""
    edges = load_edges()
    for e in edges:
        e["scored_tier"] = e.get("provisional_tier_guess")
        e["scored_modality"] = e.get("provisional_modality_guess")
        if e.get("is_calibration") and e.get("calibration_known_tier"):
            e["scored_tier"] = e["calibration_known_tier"]
        if e.get("near_intra_layer_check"):
            e["near_intra_layer_result"] = "passed"
    return edges

def find(edges, eid):
    for e in edges:
        if e.get("id") == eid:
            return e
    raise KeyError(eid)

def fired(out):
    return ",".join(sorted({tok for tok in ("C5","C9","C10","C11") if tok in out})) or "(none)"

results = []
# baseline must PASS
rc, out = run(scored_baseline())
results.append(("BASELINE valid scored", rc, rc == 0, fired(out)))

# (a) revert near-intra rows to pending -> C9
e = scored_baseline()
for i in ("E016","E017","E039"):
    find(e, i)["near_intra_layer_result"] = "pending"
rc, out = run(e); results.append(("(a) near-intra E1 pending  -> want FAIL/C9", rc, rc != 0, fired(out)))

# (b) anti-control E018 seals E0 with no E.7 interlock -> C5
e = scored_baseline()
x = find(e, "E018")
x["scored_tier"] = "E0"; x["scored_modality"] = "emergence-up"; x["run_target_stub"] = "dummy-stub"
for b in ("descent_test_logged_negative","recognition_search_logged_negative",
          "non_descending_run_object_exhibited","run_target_stub_frozen_pre_scoring"):
    x.pop(b, None)
rc, out = run(e); results.append(("(b) anti-control E0 no E.7  -> want FAIL/C5", rc, rc != 0, fired(out)))

# (c) recognition row import blanked, and menu-ified -> C11
for variant, val in (("blank", ""), ("menu", "Gleason or envariance or decision-theoretic")):
    e = scored_baseline(); find(e, "E025")["named_import"] = val
    rc, out = run(e); results.append((f"(c-{variant}) recognition import -> want FAIL/C11", rc, rc != 0, fired(out)))

# (d) value_split row reports a non-reported leg -> C10
e = scored_baseline(); find(e, "E041")["scored_tier"] = "E0"
rc, out = run(e); results.append(("(d) value_split tier mismatch -> want FAIL/C10", rc, rc != 0, fired(out)))

print(f"{'test':42} {'exit':>4} {'ok?':>4}  fired")
allok = True
for name, rc, ok, f in results:
    allok = allok and ok
    print(f"{name:42} {rc:>4} {('YES' if ok else 'NO'):>4}  {f}")
print("\nALL MUTATION CHECKS BEHAVE AS REQUIRED:", allok)
sys.exit(0 if allok else 1)
