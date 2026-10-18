import json
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from ddiood import evaluate2 as ev
from ddiood import stats
import post7_calibration as cal
import post7_common as pc
import post7_coverage as cov
import post7_partner as pp


def toy(seed=0, nd=12, nq=15):
    rng = np.random.default_rng(seed)
    y, g, q = [], [], []
    for d in range(nd):
        parts = rng.choice(nq, size=6, replace=False)
        for k, p in enumerate(parts):
            y.append(int(k < 2))
            g.append(f"d{d}")
            q.append(f"p{p}")
    y = np.asarray(y)
    s = rng.normal(size=len(y)) + 0.3 * y
    return y, np.asarray(g), np.asarray(q), s


def test_two_way_matches_evaluate2():
    y, g, q, s = toy()
    D = pc.within_design(y, g, q)
    W1, W2 = pc.scheme_weights("two_way", D["nd"], D["nq"], 200, 5)
    d, ok = pc.draws(D, pc.comparisons(D, s), W1, W2)
    ref = stats.two_way_samples(stats.stratified_auroc, y, s, g, q, n=200, seed=5, strat=g)
    assert np.allclose(d[0][ok], ref)
    assert pc.estimate(D, s) == pytest.approx(stats.stratified_auroc(y, s, g))


def test_one_way_weights_equal_drug_copies_as_strata():
    y, g, q, s = toy(1)
    D = pc.within_design(y, g, q)
    W1, W2 = pc.scheme_weights("one_way_drug", D["nd"], D["nq"], 20, 3)
    d, _ = pc.draws(D, pc.comparisons(D, s), W1, W2)
    gd = pc.codes(g)
    for b in range(20):
        idx, strata = [], []
        for k in range(D["nd"]):
            rows = np.where(gd == k)[0]
            for c in range(int(W1[b, k])):
                idx += rows.tolist()
                strata += [f"{k}:{c}"] * len(rows)
        idx = np.asarray(idx)
        assert d[0][b] == pytest.approx(stats.stratified_auroc(y[idx], s[idx], np.asarray(strata)))
    assert np.all(W2 == 1)


def test_partner_stratified_estimate():
    y, g, q, s = toy(2)
    D = pc.partner_design(y, g, q)
    assert pc.estimate(D, s) == pytest.approx(stats.stratified_auroc(y, s, q))


def test_tetrad_cancels_additive_effects():
    y, g, q, _ = toy(3, nd=20, nq=10)
    D = pc.tetrad_design(y, g, q)
    assert len(D["a"]) > 0
    gd, qd = pc.codes(g), pc.codes(q)
    rng = np.random.default_rng(0)
    base = rng.integers(-5, 5, gd.max() + 1)[gd].astype(float) + rng.integers(-5, 5, qd.max() + 1)[qd]
    assert pc.estimate(D, base) == pytest.approx(0.5)
    assert pc.estimate(D, base + 0.5 * y) == pytest.approx(1.0)
    assert np.all(y[D["a"]] == 1) and np.all(y[D["b"]] == 1) and np.all(y[D["c"]] == 0) and np.all(y[D["e"]] == 0)
    assert np.all(gd[D["a"]] == gd[D["c"]]) and np.all(qd[D["a"]] == qd[D["e"]])
    keys = {frozenset([(int(gd[a]), int(qd[a])), (int(gd[b]), int(qd[b]))]) for a, b in zip(D["a"], D["b"])}
    assert len(keys) == len(D["a"])


def test_tetrad_hand_example():
    y = np.array([1, 0, 1, 0])
    g = np.array(["d1", "d1", "d2", "d2"])
    q = np.array(["p1", "p2", "p2", "p1"])
    D = pc.tetrad_design(y, g, q)
    assert len(D["a"]) == 1
    s = np.array([2.0, 0.0, 1.0, 0.0])
    assert pc.estimate(D, s) == 1.0


def test_tost_matches_evaluate2():
    d = np.random.default_rng(4).normal(0.5, 0.06, 500)
    assert pc.tost_p(d) == pytest.approx(ev.tost_p(d))


def test_true_auroc_formula():
    rng = np.random.default_rng(5)
    sc = {"beta": 0.8, "partner_sd": 1.0, "slope_sd": 0.5}
    n = 400000
    b = sc["beta"] + sc["slope_sd"] * rng.standard_normal(n)
    diff = b + sc["partner_sd"] * (rng.standard_normal(n) - rng.standard_normal(n)) + rng.standard_normal(n) - rng.standard_normal(n)
    assert np.mean(diff > 0) == pytest.approx(cov.true_auroc(0.8, 1.0, 0.5), abs=0.003)
    for s in cov.scenarios():
        assert cov.true_auroc(s["beta"], s["partner_sd"], s["slope_sd"]) == pytest.approx(s["true_auroc"])


def test_coverage_run_shape():
    y, g, q, _ = toy(6, nd=30)
    sc = cov.scenarios()[2]
    r = cov.run_design(y, g, q, sc, 5, 50, np.random.default_rng(0))
    assert set(r["schemes"]) == {"two_way", "one_way_drug", "partner_only"}
    for v in r["schemes"].values():
        assert 0 <= v["coverage90"] <= 1


def test_explained_rule():
    assert pp.explained(0.452, {"value": 0.49, "ci95": [0.42, 0.55]}, True)["explained"]
    assert not pp.explained(0.452, {"value": 0.47, "ci95": [0.42, 0.55]}, True)["explained"]
    assert not pp.explained(0.452, {"value": 0.49, "ci95": [0.42, 0.55]}, False)["explained"]
    assert not pp.explained(0.452, {"value": 0.49, "ci95": [0.42, 0.48]}, True)["explained"]


def test_within_ranks_and_spearman():
    rng = np.random.default_rng(7)
    gc = np.repeat(np.arange(5), 8)
    x = rng.normal(size=40)
    r = pp.within_ranks(x, gc)
    for k in range(5):
        m = gc == k
        assert np.allclose(r[m], np.argsort(np.argsort(x[m])) + 1 - 4.5)
    assert pp.weighted_corr(r, r, np.ones(40)) == pytest.approx(1.0)


def test_bayes_bootstrap_centres_on_estimate():
    y, g, q, s = toy(8, nd=40)
    c = {"y": y, "g": g, "q": q}
    d = cal.bayes_auc(c, s, 4000, np.random.default_rng(0))
    assert d.mean() == pytest.approx(stats.stratified_auroc(y, s, g), abs=0.01)
    d2 = cal.bayes_auc(c, s, 600, np.random.default_rng(0), two_way=True)
    assert d2.std() >= d.std() * 0.8


def test_criteria_written_and_complete():
    crit = json.loads(pc.CRITERIA.read_text())
    for k in ("analysis_0_kappa_framing", "analysis_1a_one_way", "analysis_1b_coverage", "analysis_1c_bayes",
              "analysis_2a_partner_decomposition", "analysis_2b_popularity_simulation", "analysis_2c_decomposition"):
        assert k in crit
    assert "post hoc" in crit["status"]


def test_post7_files_are_clean():
    files = list((ROOT / "scripts").glob("post7_*.py")) + [Path(__file__)] + [p for p in pc.OUT.glob("*") if p.is_file()]
    banned = [chr(8211), chr(8212), "cl" + "aude"]
    for f in files:
        text = f.read_text().lower()
        for b in banned:
            assert b not in text, f"{f.name} contains a banned string"
    for f in (ROOT / "scripts").glob("post7_*.py"):
        assert not any(line.lstrip().startswith("#") for line in f.read_text().splitlines())
