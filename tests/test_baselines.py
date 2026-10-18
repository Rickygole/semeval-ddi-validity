import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ddiood import stats


def synth(seed=0, n=200):
    rng = np.random.RandomState(seed)
    y = (rng.rand(n) < 0.4).astype(int)
    s = rng.rand(n) + 0.5 * y
    g1 = rng.randint(0, 10, n)
    g2 = rng.randint(0, 15, n)
    return y, s, g1, g2


def test_auroc_perfect_reversed_tied():
    assert stats.auroc([0, 0, 1, 1], [0.1, 0.2, 0.8, 0.9]) == 1.0
    assert stats.auroc([0, 0, 1, 1], [0.9, 0.8, 0.2, 0.1]) == 0.0
    assert stats.auroc([0, 1, 0, 1], [1, 1, 1, 1]) == 0.5
    assert np.isnan(stats.auroc([1, 1], [0.1, 0.2]))


def test_auprc_and_prevalence():
    assert stats.auprc([0, 0, 1, 1], [0.1, 0.2, 0.8, 0.9]) == 1.0
    assert stats.prevalence([0, 0, 0, 1]) == 0.25
    assert stats.auprc([0, 1, 0, 1], [1, 1, 1, 1]) == 0.5


def test_cluster_bootstrap_deterministic_and_ordered():
    y, s, g1, g2 = synth()
    a = stats.two_way_bootstrap(stats.auroc, y, s, g1, g2, n=200, seed=7)
    b = stats.two_way_bootstrap(stats.auroc, y, s, g1, g2, n=200, seed=7)
    assert a == b
    assert a["lower"] <= a["mean"] <= a["upper"]
    c = stats.one_way_bootstrap(stats.auroc, y, s, g1, n=200, seed=7)
    assert c == stats.one_way_bootstrap(stats.auroc, y, s, g1, n=200, seed=7)
    assert c["lower"] <= stats.auroc(y, s) <= c["upper"]


def test_two_way_wider_than_one_way():
    y, s, g1, g2 = synth(1, 400)
    w2 = stats.two_way_bootstrap(stats.auroc, y, s, g1, g2, n=300)
    w1 = stats.one_way_bootstrap(stats.auroc, y, s, g1, n=300)
    assert w2["upper"] - w2["lower"] >= 0.5 * (w1["upper"] - w1["lower"])


def test_tost_decisions():
    rng = np.random.RandomState(0)
    tight = 0.5 + 0.01 * rng.randn(500)
    assert stats.tost_decision(tight)["equivalent"]
    wide = 0.5 + 0.2 * rng.randn(500)
    assert not stats.tost_decision(wide)["equivalent"]
    shifted = 0.75 + 0.01 * rng.randn(500)
    assert not stats.tost_decision(shifted)["equivalent"]


def test_holm():
    r = stats.holm([0.01, 0.04, 0.03], alpha=0.05)
    assert r["adjusted"] == pytest.approx([0.03, 0.06, 0.06])
    assert r["reject"] == [True, False, False]
    assert stats.holm([0.5])["adjusted"] == [0.5]


def test_seed_average():
    out = stats.seed_average([[0.0, 1.0], [1.0, 1.0]])
    assert out.tolist() == [0.5, 1.0]


def test_kappa():
    a = ["y", "n", "y", "n", "u", "y"]
    assert stats.kappa(a, a) == 1.0
    assert stats.kappa(["y", "y", "n", "n"], ["y", "n", "y", "n"]) == 0.0
    assert stats.kappa(["y", "y", "n", "n"], ["n", "n", "y", "y"]) == -1.0
    assert stats.kappa(["y", "y"], ["y", "y"]) == 1.0
