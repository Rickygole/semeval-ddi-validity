import ast
import io
import json
import sys
import tokenize
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import rev3_c3 as c3
import rev3_d1 as d1
import rev3_d2 as d2
import rev3_d3 as d3
import rev3_d4 as d4

FILES = ["scripts/rev3_d1.py", "scripts/rev3_d2.py", "scripts/rev3_d3.py", "scripts/rev3_d4.py", "tests/test_rev3_d.py"]
OUTPUTS = ["d1_transport", "d2_power_oneway", "d3_r2a_overlap", "d4_seen_mechanism"]


def test_new_files_have_no_dashes_no_comments_no_forbidden_string():
    for f in FILES:
        txt = (ROOT / f).read_text()
        assert chr(0x2013) not in txt and chr(0x2014) not in txt, f
        assert "cla" + "ude" not in txt.lower(), f
        assert not [t for t in tokenize.generate_tokens(io.StringIO(txt).readline) if t.type == tokenize.COMMENT], f
        tree = ast.parse(txt)
        assert not [n for n in ast.walk(tree) if isinstance(n, (ast.Module, ast.FunctionDef, ast.ClassDef)) and ast.get_docstring(n)], f


def test_tercile_assignment_uses_less_or_equal_edges():
    edges = [882, 1485]
    assert [d1.tercile_of(t, edges) for t in (1, 882, 883, 1485, 1486)] == [0, 0, 1, 1, 2]


def test_length_matched_calibration_and_rogan_gladen_by_hand():
    se, sp = d1.length_matched([0.5, 0.3, 0.1], [1.0, 0.9, 0.8], [0.5, 0.25, 0.25])
    assert abs(se - 0.35) < 1e-12 and abs(sp - 0.925) < 1e-12
    assert abs(d1.rg_value(0.4, 0.5, 0.9) - 0.75) < 1e-12
    assert d1.rg_value(0.4, 0.1, 0.8) is None
    assert d1.err_of(0.75, 1) == 0.25 and d1.err_of(0.75, 0) == 0.75 and d1.err_of(None, 1) is None


def fake_items(n_per, tokens, label, cohort, yes):
    return [{"set": "random", "cohort": cohort, "current_label": label, "decision": "yes" if k < yes else "no", "non_answer": False, "tokens": tokens}
            for k in range(n_per)]


def test_length_matched_rows_reduce_to_plain_rogan_gladen_when_one_tercile_holds_all():
    cal = {s: {"unsure_not_yes": {"sensitivity": se, "specificity": sp, "n_items": 100, "tp": 50, "fn": 50, "tn": 50, "fp": 0}}
           for s, se, sp in zip(d1.TERCILE_STRATA, (0.6, 0.4, 0.2), (0.9, 0.9, 0.9))}
    rng = np.random.RandomState(0)
    draws = {(s, "unsure_not_yes"): (np.clip(cal[s]["unsure_not_yes"]["sensitivity"] + rng.normal(0, 0.02, 500), 0, 1), np.full(500, 0.9)) for s in d1.TERCILE_STRATA}
    items = fake_items(40, 500, 1, "older", 12)
    rows, extra = d1.cell_rows(items, "unsure_not_yes", cal, draws, [882, 1485])
    r = [x for x in rows if x["cohort"] == "older" and x["label_class"] == 1][0]
    assert r["tercile_counts"] == [40, 0, 0]
    assert abs(r["calibration_sensitivity"] - 0.6) < 1e-12
    assert abs(r["corrected_true_share_unclipped"] - d1.rg_value(0.3, 0.6, 0.9)) < 1e-12
    assert abs(r["corrected_error_rate_unclipped"] - (1 - d1.rg_value(0.3, 0.6, 0.9))) < 1e-12
    mixed = fake_items(20, 500, 1, "older", 6) + fake_items(20, 2000, 1, "older", 4)
    rows, _ = d1.cell_rows(mixed, "unsure_not_yes", cal, draws, [882, 1485])
    m = [x for x in rows if x["cohort"] == "older" and x["label_class"] == 1][0]
    assert abs(m["calibration_sensitivity"] - 0.4) < 1e-12 and m["tercile_shares"] == [0.5, 0.0, 0.5]


def test_one_way_draws_ignore_partner_resampling_and_are_reproducible():
    st = {"k1": 4, "k2": 3, "drug": np.array([0, 0, 1, 1, 2, 3]), "qpos": np.array([0, 1, 2, 0, 1, 2]), "qneg": np.array([1, 2, 0, 1, 2, 0])}
    W = np.random.RandomState(1).rand(3, 6)
    a = c3.draws_matrix(W, st, 50, 7, True)
    b = c3.draws_matrix(W, st, 50, 7, True)
    st2 = dict(st, k2=9)
    c = c3.draws_matrix(W, st2, 50, 7, True)
    t = c3.draws_matrix(W, st, 50, 7, False)
    assert np.array_equal(a, b) and np.array_equal(a, c) and not np.allclose(a, t)


def test_overlap_cohort_is_the_complement_of_the_not_in_train_mask():
    n = 8
    mask = np.array([1, 1, 0, 1, 0, 1, 1, 1], bool)
    full = {"y": np.array([1, 0, 1, 0, 1, 0, 1, 0]), "g": np.array(list("aabbccdd")), "q": np.array(list("pqrstuvw")), "mask": np.ones(n, bool), "name": "seen"}
    c = d4.sub(full, ~mask)
    assert list(c["g"]) == ["b", "c"] and list(c["y"]) == [1, 1] and np.array_equal(c["mask"], ~mask) and c["name"] == "seen"
    assert d3.contributing_anchors(full) == 4


def test_partner_prior_definitions_and_default():
    sem = [{"drug_a": "Alpha", "drug_b": "beta", "label_id": 1}, {"drug_a": "alpha ", "drug_b": "gamma", "label_id": 0},
           {"drug_a": "beta", "drug_b": "gamma", "label_id": 2}, {"drug_a": "delta", "drug_b": "delta", "label_id": 0}]
    prim, alt, has, info = d4.partner_priors(sem, ["alpha", "BETA", "gamma", "zeta"])
    assert np.allclose(prim, [0.5, 1.0, 0.5, 0.5])
    assert np.allclose(alt, [0.5, 1.0, 0.5, 0.0])
    assert list(has) == [True, True, True, False]
    assert info["n_train_instances"] == 4 and info["n_positive_instances"] == 2 and info["n_partners_without_train_instance"] == 1


def test_partialling_out_the_prior_removes_the_within_drug_linear_component():
    rng = np.random.RandomState(3)
    g = np.repeat(np.arange(20), 10)
    prior = rng.rand(200)
    s = 3 * prior + rng.normal(0, 0.1, 200)
    y = (rng.rand(200) > 0.5).astype(int)
    c = {"y": y, "g": g, "q": np.arange(200), "mask": np.ones(200, bool), "name": "seen"}
    res = d4.adjust(c, s, prior, 20)
    assert abs(res["slope_on_prior"] - 3) < 0.3
    assert res["paired_two_way_draws"] > 0


def test_spearman_helpers():
    x = np.arange(18, dtype=float)
    g = np.repeat(np.arange(3), 6)
    out = d4.within_spearman(x, x, g)
    assert out["n_anchors"] == 3 and abs(out["mean_within_drug_spearman"] - 1) < 1e-12
    ds = d4.cluster_spearman(x, x, g, 10, 42)
    assert len(ds) == 10 and all(abs(v - 1) < 1e-9 for v in ds)


def test_committed_outputs_hold_no_drug_names_and_carry_the_plan_hash():
    import hashlib
    names = set()
    for f in (ROOT / "artifacts" / "vocab" / "drug_lookup.json", ROOT / "artifacts" / "amend7" / "di_sections.json"):
        if f.exists():
            names |= {k.lower().strip() for k in json.loads(f.read_text())}
    import re
    import subprocess
    rel = "docs/POSTHOC_REV3_PLAN.md"
    data = (ROOT / rel).read_bytes()
    known = {hashlib.sha256(data[:m.start() + 1]).hexdigest() for m in re.finditer(rb"\n\n## Addendum ", data)} | {hashlib.sha256(data).hexdigest()}
    commits = subprocess.run(["git", "log", "--format=%H", "--", rel], cwd=ROOT, capture_output=True, text=True).stdout.split()
    for c in commits:
        blob = subprocess.run(["git", "show", f"{c}:{rel}"], cwd=ROOT, capture_output=True, check=True).stdout
        known.add(hashlib.sha256(blob).hexdigest())

    def walk(x):
        if isinstance(x, dict):
            for k, v in x.items():
                yield str(k)
                yield from walk(v)
        elif isinstance(x, list):
            for v in x:
                yield from walk(v)
        elif isinstance(x, str):
            yield x
    for name in OUTPUTS:
        f = ROOT / "results" / "revision" / "rev3" / f"{name}.json"
        if not f.exists():
            continue
        obj = json.loads(f.read_text())
        assert obj["plan_sha256"] in known
        assert not [s for s in walk(obj) if s.lower().strip() in names]
