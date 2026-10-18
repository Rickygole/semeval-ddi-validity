import json
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from ddiood import amend7_analysis as aa
import post7_classshortcut as cs
import post7_classshortcut_classes as cl

OUT = ROOT / "results" / "revision" / "post7" / "classshortcut"


def toy(seed=0, nd=12, nq=15, ties=False):
    rng = np.random.default_rng(seed)
    y, g, q = [], [], []
    for d in range(nd):
        parts = rng.choice(nq, size=6, replace=False)
        for k, p in enumerate(parts):
            y.append(int(k < 2))
            g.append(f"d{d}")
            q.append(f"p{p}")
    y = np.asarray(y)
    s = rng.normal(size=len(y)) + 0.5 * y
    if ties:
        s = np.round(s)
    return y, np.asarray(g), np.asarray(q), s


@pytest.mark.parametrize("ties", [False, True])
def test_placement_area_equals_within_auroc(ties):
    y, g, q, s = toy(1, ties=ties)
    lo, hi, w = cs.placements(y, s, g)
    assert cs.pauc_at(lo, hi, w, 1.0) == pytest.approx(aa.fast_within(y, s, cs.codes(g)))


def test_tpr_and_pauc_shape():
    y, g, q, s = toy(2)
    lo, hi, w = cs.placements(y, s, g)
    ts = np.linspace(0, 1, 21)
    tpr = [cs.tpr_at(lo, hi, w, t) for t in ts]
    assert all(b >= a - 1e-12 for a, b in zip(tpr, tpr[1:]))
    assert tpr[-1] == pytest.approx(1.0)
    pa = [cs.pauc_at(lo, hi, w, t) for t in ts]
    assert pa[0] == 0.0
    assert all(b >= a - 1e-12 for a, b in zip(pa, pa[1:]))
    lo, hi, w = cs.placements(y, y.astype(float), g)
    assert cs.tpr_at(lo, hi, w, 0.0) == pytest.approx(1.0)


def test_binary_tie_ramp():
    y = np.array([1, 0, 0])
    s = np.array([1.0, 1.0, 0.0])
    lo, hi, w = cs.placements(y, s, np.zeros(3, int))
    assert lo[0] == 0.0 and hi[0] == 0.5
    assert cs.tpr_at(lo, hi, w, 0.25) == pytest.approx(0.5)
    assert cs.pauc_at(lo, hi, w, 1.0) == pytest.approx(0.75)


def test_resamples_match_amend7_draws():
    y, g, q, s = toy(3)
    ref = aa.draws(y, [s], g, q, n=30, seed=7)[0]
    got = [aa.fast_within(y[i], s[i], st) for i, st in cs.resamples(g, q, 30, 7)]
    assert np.allclose(ref, got)


def test_rank_residual_orthogonal():
    y, g, q, s = toy(4)
    rng = np.random.default_rng(4)
    x = s + rng.normal(size=len(s))
    r, beta = cs.residualize(s, [x], g, "rank")
    assert abs(np.dot(r, cs.within_center_rank(x, g))) < 1e-6
    assert beta[0] > 0
    r0, b0 = cs.residualize(s, [np.zeros(len(s))], g, "rank")
    assert b0 == [0.0]
    assert np.allclose(r0, cs.within_center_rank(s, g))


def test_class_scores_toy():
    rows = [{"drug_a": "a1", "drug_b": "x", "y": "1"}, {"drug_a": "a2", "drug_b": "x", "y": "0"},
            {"drug_a": "a2", "drug_b": "z", "y": "1"}, {"drug_a": "b1", "drug_b": "x", "y": "1"}]
    graph = cs.Graph(rows)
    atc = {"a1": {"atc": ["L04AB01"]}, "a2": {"atc": ["L04AB02"]}, "b1": {"atc": ["B01AF01"]},
           "t": {"atc": ["L04AB05"]}, "u": {"atc": []}}
    share, cond, nm = cs.class_scores(np.array(["t", "t", "u"]), np.array(["x", "z", "x"]), graph, atc, "atc4", graph.anchors)
    assert list(nm) == [2, 2, 0]
    assert share.tolist() == [0.5, 0.5, 0.0]
    assert cond.tolist() == [0.5, 1.0, 0.0]
    _, _, nm3 = cs.class_scores(np.array(["t"]), np.array(["x"]), graph, atc, "atc3", graph.anchors)
    assert nm3[0] == 2


def test_stems():
    assert cl.stem_of("adalimumab") == cl.stem_of("golimumab") == "mab:immunomodulator"
    assert cl.stem_of("rituximab") == "mab:tumor"
    assert cl.stem_of("trandolapril") == cl.stem_of("perindopril erbumine") == "pril"
    assert cl.stem_of("zoledronic acid") == cl.stem_of("risedronate") == "dronate"
    assert cl.stem_of("axitinib") == "tinib"
    assert cl.stem_of("benzoate") is None


def test_pk_rule():
    assert cs.PK_RE.search("increased the C max and AUC of digoxin")
    assert cs.PK_RE.search("a strong CYP3A4 inhibitor")
    assert not cs.PK_RE.search("increased risk of bleeding")
    assert not cs.PK_RE.search("in Caucasian subjects")


def test_class_share():
    assert cs.class_share(0.7, 0.6) == pytest.approx(0.5)
    assert cs.class_share(0.7, 0.75) == 0.0
    assert cs.class_share(0.7, 0.4) == 1.0
    assert cs.class_share(0.5, 0.6) is None


def test_criteria_written_and_outputs_consistent():
    crit = json.loads((OUT / "criteria.json").read_text())
    assert "verdict_rule" in crit
    f = OUT / "classshortcut.json"
    if not f.exists():
        pytest.skip("analysis not run")
    res = json.loads(f.read_text())
    e7 = json.loads((ROOT / "results" / "revision" / "amend7" / "e7.json").read_text())["knowledge"]
    for arm, name in (("c", "E7c"), ("d", "E7d"), ("e", "E7e")):
        for cell, key in (("older_primary:A", "older_primary/A"), ("novel:A", "novel/A")):
            a, b = res["cells"][cell]["systems"][name], e7[arm][key]["within"]
            assert a["value"] == pytest.approx(b["value"])
            assert a["lo95"] == pytest.approx(b["lo95"])
            assert a["hi95"] == pytest.approx(b["hi95"])
    op = res["cells"]["older_primary:A"]["drugbank_operating_point"]
    assert op["e7c_auroc_from_placements"]["value"] == pytest.approx(res["cells"]["older_primary:A"]["systems"]["E7c"]["value"])
    assert res["verdict"]["verdict"] in ("a", "b", "c")


def test_no_forbidden_text():
    files = [ROOT / "scripts" / n for n in ("post7_classshortcut.py", "post7_classshortcut_atc.py", "post7_classshortcut_classes.py",
                                             "post7_classshortcut_embed.py")]
    files += [Path(__file__)] + sorted(OUT.glob("*.json")) + sorted(OUT.glob("*.md"))
    bad = "cl" + "aude"
    for f in files:
        t = f.read_text().lower()
        assert bad not in t, f
        assert chr(0x2013) not in t and chr(0x2014) not in t, f
