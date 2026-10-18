import io
import json
import sys
import tokenize
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from ddiood import stats
from ddiood import evaluate2 as ev

import spikein_core as sc
import spikein_run as sr

SOURCES = ["scripts/spikein_core.py", "scripts/spikein_run.py", "scripts/spikein_report.py", "tests/test_spikein.py"]
DECISIONS = ROOT / "results" / "revision" / "eval" / "decisions.json"


def toy(seed=0, n=240):
    rng = np.random.RandomState(seed)
    g = rng.randint(0, 15, n)
    q = rng.randint(0, 12, n)
    y = rng.randint(0, 2, n)
    s = np.round(rng.rand(4, n), 1)
    return y, g, q, s


def test_batched_two_way_equals_stats():
    y, g, q, s = toy()
    ref = np.array([stats.two_way_samples(stats.stratified_auroc, y, si, g, q, n=40, seed=42, strat=g) for si in s])
    got = sc.draws(y, s, g, q, 40, 42)
    assert got.shape == ref.shape
    assert np.allclose(got, ref, atol=1e-12)


def test_batched_one_way_matches_manual_resample():
    y, g, q, s = toy(1)
    got = sc.draws(y, s[:1], g, None, 25, 7)[0]
    c = sc.codes(g)
    rng = np.random.RandomState(7)
    ref = []
    for _ in range(25):
        w = np.bincount(rng.randint(0, c.max() + 1, c.max() + 1), minlength=c.max() + 1)
        ys, ss, st = [], [], []
        for k in range(c.max() + 1):
            for copy in range(w[k]):
                m = c == k
                ys.append(y[m])
                ss.append(s[0][m])
                st.append(np.full(m.sum(), k * 100 + copy))
        ref.append(stats.stratified_auroc(np.concatenate(ys), np.concatenate(ss), np.concatenate(st)))
    assert np.allclose(got, ref, atol=1e-12)


def test_point_within_equals_stratified_auroc():
    y, g, q, s = toy(2)
    assert np.allclose(sc.point_within(y, s, g), [stats.stratified_auroc(y, si, g) for si in s])


def test_decision_rules():
    d = np.vstack([np.linspace(0.45, 0.55, 300), np.linspace(0.62, 0.80, 300), np.linspace(0.35, 0.65, 300)])
    a = sc.auroc_decisions(d)
    assert list(a["decision"]) == ["equivalent", "falsified", "inconclusive"]
    assert a["p_tost"][0] < 0.05 and a["p_tost"][2] > 0.05
    assert list(a["holm"]) == ["equivalent", "falsified", "inconclusive"]
    db = np.full(300, 0.7)
    k = sc.kappa_decisions(np.vstack([np.full(300, 0.52), np.full(300, 0.65), np.linspace(0.45, 0.65, 300)]), db)
    assert list(k["decision"]) == ["equivalent", "falsified", "inconclusive"]


def test_crossings():
    grid = [0, 0.1, 0.2, 0.3]
    assert sc.crossing_up(grid, [0.0, 0.5, 0.9, 1.0], 0.8) == (0.2, pytest.approx(0.175))
    assert sc.crossing_down(grid, [1.0, 0.6, 0.1, 0.0], 0.2) == (0.1, pytest.approx(0.18))
    assert sc.crossing_up(grid, [0, 0, 0, 0.1], 0.8) == (None, None)


def test_criteria_fixed():
    crit = sc.load_criteria()
    assert crit["kappa_grid"] == [0, 0.05, 0.1, 0.15, 0.2, 0.3, 0.4, 0.5, 0.6, 0.8, 1.0]
    assert crit["reps_per_grid_point"] >= 200 and crit["bootstrap"]["draws_per_rep"] >= 300
    assert crit["blend"]["sigma"] == sc.SIGMA
    out = sc.OUT / "spikein.json"
    if out.exists():
        assert json.loads(out.read_text())["criteria"] == crit


def test_sources_are_clean():
    for f in SOURCES:
        txt = (ROOT / f).read_text()
        assert chr(0x2013) not in txt and chr(0x2014) not in txt
        assert "cla" + "ude" not in txt.lower()
        assert not [t for t in tokenize.generate_tokens(io.StringIO(txt).readline) if t.type == tokenize.COMMENT]
    for p in sc.OUT.glob("*"):
        txt = p.read_text()
        assert chr(0x2013) not in txt and chr(0x2014) not in txt and "cla" + "ude" not in txt.lower()


@pytest.fixture(scope="module")
def data():
    try:
        truth = ev.load_truth()
        return sr.cohort_data(truth)
    except Exception as e:
        pytest.skip(f"real data unavailable: {e}")


def test_kappa_zero_recovers_half(data):
    d = data["older_clean"]
    s = sc.make_scores(d["db"], None, "noise", 77, 0, 0.0, 30)
    est = sc.point_within(d["y"], s, d["g"])
    assert abs(est.mean() - 0.5) < 0.01


def test_kappa_one_recovers_drugbank(data):
    for c in ("older_clean", "novel"):
        d = data[c]
        a_db = stats.stratified_auroc(d["y"], d["db"], d["g"])
        for base, scores in (("noise", None), ("b2mixed", d["b2"])):
            s = sc.make_scores(d["db"], scores, base, 78, 0, 1.0, 30)
            assert abs(sc.point_within(d["y"], s, d["g"]).mean() - a_db) < 0.01
    assert abs(stats.stratified_auroc(data["older_clean"]["y"], data["older_clean"]["db"], data["older_clean"]["g"]) - 0.641) < 5e-4
    assert abs(stats.stratified_auroc(data["novel"]["y"], data["novel"]["db"], data["novel"]["g"]) - 0.729) < 5e-4


def test_calibration_hits_targets(data):
    d = data["older_clean"]
    cal = sc.calibrate(d["y"], d["g"], d["db"], d["b2"], "b2mixed", 79, [0.0, 0.3, 1.0], n_cal=20)
    assert cal["curve"][0] < -0.2
    s = sc.make_scores(d["db"], d["b2"], "b2mixed", 79, 5, cal["w"][1], 40)
    k = (sc.point_within(d["y"], s, d["g"]) - 0.5) / (cal["a_db"] - 0.5)
    assert abs(k.mean() - 0.3) < 0.05


def test_real_b2mixed_matches_evaluate2(data):
    dec = json.loads(DECISIONS.read_text())
    o = sr.observed(data["older_clean"], 1000)["A"]
    h1 = dec["H1"]
    assert abs(o["auroc"] - h1["value"]) < 1e-4
    assert np.allclose(o["ci90"], h1["interval90"], atol=1e-4)
    assert np.allclose(o["ci95"], h1["interval"], atol=1e-4)
    assert abs(o["p_tost"] - h1["p_tost"]) < 1e-4
    assert o["decision_holm"] == h1["decision"] == "inconclusive"
    assert o["decision"] == "inconclusive"
    assert abs(o["kappa_ci95"][1] - 0.133) < 5e-4
    n = sr.observed(data["novel"], 1000)["A"]
    assert abs(n["auroc"] - dec["H1-novel"]["value"]) < 1e-4
    assert np.allclose(n["ci95"], dec["H1-novel"]["interval"], atol=1e-4)


def test_middle_cohort_shape(data):
    m = sr.middle(data["older_clean"], 1)
    assert len(set(m["g"])) == 188
    assert len(m["y"]) == len(m["db"]) == len(m["b2"]) == len(m["q"])
    assert m["y"][:1832].tolist() == data["older_clean"]["y"].tolist()
