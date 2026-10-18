import ast
import hashlib
import io
import json
import re
import subprocess
import sys
import tokenize
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import rev3_c2 as c2
import rev3_d7 as d7
import rev3_d8 as d8
import rev3_d9 as d9

FILES = ["scripts/rev3_d7.py", "scripts/rev3_d8.py", "scripts/rev3_d9.py", "tests/test_rev3_e.py"]
OUTPUTS = ["d6_marker_sentence", "d7_tac_overlap", "d8_partner_marginal", "d9_listing_conventions"]


def test_new_files_have_no_dashes_no_comments_no_forbidden_string():
    for f in FILES:
        txt = (ROOT / f).read_text()
        assert chr(0x2013) not in txt and chr(0x2014) not in txt, f
        assert "cla" + "ude" not in txt.lower(), f
        assert not [t for t in tokenize.generate_tokens(io.StringIO(txt).readline) if t.type == tokenize.COMMENT], f
        tree = ast.parse(txt)
        assert not [n for n in ast.walk(tree) if isinstance(n, (ast.Module, ast.FunctionDef, ast.ClassDef)) and ast.get_docstring(n)], f


def test_clopper_pearson_known_values():
    lo, hi = d7.clopper_pearson(0, 10)
    assert lo == 0.0 and hi == pytest.approx(0.3084971, abs=1e-6)
    lo, hi = d7.clopper_pearson(5, 10)
    assert lo == pytest.approx(0.1870860, abs=1e-6) and hi == pytest.approx(0.8129140, abs=1e-6)
    assert d7.clopper_pearson(10, 10)[1] == 1.0 and d7.clopper_pearson(0, 0) is None


def tac_label(drug, positives):
    return {"drug": drug, "di_text": "text", "positives": {k: {"code": c, "type": "x"} for k, c in positives.items()}}


def cohort(drugs, partner_of):
    rows = []
    for d in drugs:
        for p, y in partner_of[d]:
            rows.append({"drug": d, "partner": p, "y": y})
    return rows, set(drugs)


def test_d7_below_minimum_records_not_possible_and_no_statistics():
    tac = {"test1": [tac_label(f"Drug{i}", {"aa": "R5Z9X1Q2LP"}) for i in range(4)], "test2": []}
    rows, ds = cohort([f"drug{i}" for i in range(4)] + ["other"], {**{f"drug{i}": [("aa", 1)] for i in range(4)}, "other": [("aa", 0)]})
    res = d7.analyse(tac, {"older_clean": (rows, ds)})
    c = res["cohorts"]["older_clean"]
    assert res["check_possible"] is False and c["exact_overlap"] == 4 and c["check_possible"] is False
    assert "pooled" not in c and "note" in res
    text = d7.md(res)
    assert "Check possible: False" in text


def test_d7_agreement_precision_recall_by_hand_and_cluster_bootstrap_threshold():
    drugs = [f"drug{i}" for i in range(5)]
    tac = {"test1": [tac_label(d.capitalize(), {"aa": "R5Z9X1Q2LP", "bb": "B1C2D3E4F5", "cls": "N0000175"}) for d in drugs], "test2": []}
    partner_of = {d: [("aa", 1), ("bb", 0), ("cc", 0)] for d in drugs}
    rows, ds = cohort(drugs, partner_of)
    vocab_rows = rows + [{"drug": "x", "partner": "bb", "y": 0}]
    res = d7.analyse(tac, {"older_clean": (vocab_rows, ds)}, n_boot=20)
    c = res["cohorts"]["older_clean"]
    assert res["check_possible"] is True
    p = c["pooled"]
    assert p["precision_of_our_positives"]["k"] == 5 and p["precision_of_our_positives"]["n"] == 5
    assert p["recall_of_tac_gold_by_our_positives"]["k"] == 5 and p["recall_of_tac_gold_by_our_positives"]["n"] == 10
    assert p["our_negatives_listed_by_tac_gold"]["k"] == 5 and p["our_negatives_listed_by_tac_gold"]["n"] == 10
    assert p["agreement"]["k"] == 10 and p["agreement"]["n"] == 15
    assert "label_cluster_bootstrap_ci95" not in c
    drugs10 = [f"drug{i}" for i in range(10)]
    tac10 = {"test1": [tac_label(d.capitalize(), {"aa": "R5Z9X1Q2LP"}) for d in drugs10], "test2": []}
    rows10, ds10 = cohort(drugs10, {d: [("aa", 1), ("bb", 0)] for d in drugs10})
    r = d7.analyse(tac10, {"novel": (rows10, ds10)}, n_boot=20)
    assert "label_cluster_bootstrap_ci95" in r["cohorts"]["novel"]


def test_d8_loo_matches_c2_and_marginal_by_hand():
    g = np.array(["a", "a", "b", "b", "c", "c", "d"])
    q = np.array(["x", "y", "x", "y", "x", "z", "z"])
    y = np.array([1, 0, 0, 1, 1, 0, 1])
    s = np.array([0.9, 0.1, 0.4, 0.8, 0.6, 0.2, 0.3])
    rate, marginal, n_other = d8.loo_stats(g, q, y, s)
    rows = [{"drug_a": a, "drug_b": b, "y": int(v)} for a, b, v in zip(g, q, y)]
    assert np.allclose(rate, c2.lodo_scores(rows, list(range(len(rows)))))
    assert marginal[0] == pytest.approx((0.4 + 0.6) / 2) and n_other[0] == 2
    assert marginal[1] == pytest.approx(0.8) and marginal[5] == pytest.approx(0.3)
    assert rate[0] == pytest.approx((1 + 1) / (2 + 2))


def test_d8_pairs_without_other_anchor_are_dropped():
    c = {"name": "novel", "y": np.array([1, 0, 1, 0, 1, 0]), "g": np.array(["a", "a", "b", "b", "c", "c"]), "q": np.array(["x", "y", "x", "y", "z", "z"])}
    s = np.array([0.9, 0.2, 0.8, 0.3, 0.5, 0.5])
    b = d8.system_block(c, s, 30)
    assert b["n_with_other_anchor_pairs"] == 4 and b["n_dropped_no_other_pair"] == 2
    assert d8.spearman([1, 2, 3], [3, 2, 1]) == pytest.approx(-1.0) and d8.spearman([1, 1, 1], [1, 2, 3]) is None


def test_d8_partner_bootstrap_is_reproducible():
    q = np.array(list("aabbccdd"))
    v = np.arange(8, dtype=float)
    f = lambda idx: d8.spearman(v[idx], v[idx] ** 2)
    assert d8.partner_bootstrap(q, f, 25) == d8.partner_bootstrap(q, f, 25)


def test_d9_counts_conventions_and_reproduction_flags():
    state = np.array(["positive", "negative", "unresolvable", "positive", "negative", "positive"])
    sides = np.array([2, 2, 0, 1, 2, 2])
    y = np.array([0, 0, 0, 0, 1, 1])
    source = np.array(["DrugBank", "DrugBank", "MedLine", "MedLine", "DrugBank", "MedLine"])
    selfpair = np.array([False, True, False, False, False, False])
    rows = d9.instance_rows(y, source, selfpair, state, sides)
    ex = rows[("self_pairs_excluded", "negatives", "pooled")]
    inc = rows[("self_pairs_included", "negatives", "pooled")]
    assert (ex["n"], ex["resolvable"], ex["listed"], ex["n_self_pairs_removed"]) == (3, 2, 2, 1)
    assert (inc["n"], inc["resolvable"], inc["listed"]) == (4, 3, 2)
    assert ex["listed_share_of_resolvable"] == 1.0 and ex["listed_share_of_all"] == pytest.approx(2 / 3)
    keys = [("a", "b"), ("a", "b"), ("c", "d"), ("c", "d"), ("a", "b"), ("e", "f")]
    uniq, both = d9.pair_rows(None, y, source, selfpair, state, sides, keys)
    assert both == 1
    assert uniq[("self_pairs_included", "negatives", "pooled")]["n"] == 2
    bad = d9.reproduce({k: {"listed": 0, "resolvable": 0, "n": 0, "listed_share_of_resolvable": None, "listed_share_of_all": None,
                            "ci95_resolvable": None, "ci95_all": None} for k in rows})
    assert not any(r["match"] for r in bad)


def test_d9_cache_loader_accepts_matching_wrapper_and_rejects_stale(tmp_path, monkeypatch):
    import pickle
    z = tmp_path / "db.zip"
    z.write_bytes(b"xx")
    st = z.stat()
    key = f"{st.st_size}:{int(st.st_mtime)}"
    cache = tmp_path / "t.pkl"
    cache.write_bytes(pickle.dumps({"source_key": key, "table": {"a": {"b"}}}))
    table, how = d9.load_cached_table(z, cache)
    assert table == {"a": {"b"}} and "matching" in how
    cache.write_bytes(pickle.dumps({"source_key": "0:0", "table": {"a": {"b"}}}))
    monkeypatch.setattr(d9.drugbank, "load_interactions", lambda p: {"fresh": set()})
    table, how = d9.load_cached_table(z, cache)
    assert table == {"fresh": set()} and "nothing written" in how


def test_outputs_hold_no_drug_names_and_carry_a_known_plan_hash():
    rel = "docs/POSTHOC_REV3_PLAN.md"
    data = (ROOT / rel).read_bytes()
    known = {hashlib.sha256(data[:m.start() + 1]).hexdigest() for m in re.finditer(rb"\n\n## Addendum ", data)} | {hashlib.sha256(data).hexdigest()}
    for c in subprocess.run(["git", "log", "--format=%H", "--", rel], cwd=ROOT, capture_output=True, text=True).stdout.split():
        known.add(hashlib.sha256(subprocess.run(["git", "show", f"{c}:{rel}"], cwd=ROOT, capture_output=True, check=True).stdout).hexdigest())
    names = set()
    for f in (ROOT / "artifacts" / "vocab" / "drug_lookup.json", ROOT / "artifacts" / "amend7" / "di_sections.json"):
        if f.exists():
            names |= {k.lower().strip() for k in json.loads(f.read_text())}

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
