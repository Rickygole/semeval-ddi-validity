import json
import re
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import matplotlib

matplotlib.use("Agg")

from ddiood import evaluate2 as ev
from ddiood import paperfigs2 as p2
from ddiood import stats

FIG = ROOT / "results" / "revision" / "figures"


def test_check_passes_within_tolerance_and_counts():
    L = p2.Ledger()
    assert L.check("k", 0.45181, 0.4518, "x") == pytest.approx(0.45181)
    L.check("k", 0.5, 0.5, "y", tol=0)
    assert L.counts["k"] == 2
    assert len(L.items) == 2


@pytest.mark.parametrize("got,want", [(0.4519, 0.4518), (None, 0.5), (0.5, None), (float("nan"), 0.5)])
def test_check_raises_on_mismatch_or_missing(got, want):
    with pytest.raises(AssertionError):
        p2.Ledger().check("k", got, want, "x")


def test_check_cell_compares_only_stored_keys():
    L = p2.Ledger()
    got = {"value": 0.6, "lo95": 0.5, "hi95": 0.7, "lo90": 0.52, "hi90": 0.68}
    L.check_cell("c", got, {"value": 0.6, "lo95": 0.5}, "x", tol=1e-12)
    assert set(L.counts) == {"c:value", "c:lo95"}
    with pytest.raises(AssertionError):
        L.check_cell("c", got, {"value": 0.6, "hi90": 0.69}, "x", tol=1e-12)


def test_read_is_counted_separately():
    L = p2.Ledger()
    L.read("source", 0.3)
    assert L.counts == {"read": 1}


def test_wilson_matches_closed_form():
    lo, hi = p2.wilson(50, 100)
    assert lo == pytest.approx(0.4038, abs=1e-4)
    assert hi == pytest.approx(0.5962, abs=1e-4)
    assert np.isnan(p2.wilson(0, 0)[0])


def test_two_significant_digit_percent():
    assert p2.two_sig_percent(1609 / 2439) == "66%"
    assert p2.two_sig_percent(0.0412) == "4.1%"
    assert p2.two_sig_percent(0.0) == "0%"


def test_spread_keeps_minimum_gap():
    out = p2.spread([0.50, 0.51, 0.70], 0.05)
    s = np.sort(out)
    assert np.all(np.diff(s) >= 0.05 - 1e-12)


def test_lint_rejects_dashes_forbidden_word_and_small_text():
    import matplotlib.pyplot as plt
    for bad in ("a " + chr(0x2013) + " b", "a " + chr(0x2014) + " b", "made by " + "Cla" + "ude"):
        fig = plt.figure()
        fig.text(0.5, 0.5, bad, fontsize=8)
        with pytest.raises(AssertionError):
            p2.lint(fig, "t")
        plt.close(fig)
    fig = plt.figure()
    fig.text(0.5, 0.5, "tiny", fontsize=6)
    with pytest.raises(AssertionError):
        p2.lint(fig, "t")
    plt.close(fig)
    fig = plt.figure()
    fig.text(0.5, 0.5, "AUROC 0.45 to 0.60", fontsize=7)
    p2.lint(fig, "t")
    plt.close(fig)


def test_pending_frame_fails_in_final_mode():
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots()
    with pytest.raises(p2.PendingError):
        p2.pending_frame(ax, "E9", final=True)
    p2.pending_frame(ax, "E9", final=False)
    assert any(t.get_text() == "pending" for t in ax.texts)
    plt.close(fig)


def toy_eval(seed, nd=10, prefix="d"):
    rng = np.random.default_rng(seed)
    y, g, q = [], [], []
    for d in range(nd):
        for k in range(6):
            y.append(int(k < 2))
            g.append(f"{prefix}{d}")
            q.append(f"p{rng.integers(12)}")
    y = np.asarray(y)
    p = rng.normal(size=len(y)) + 0.4 * y
    clean = np.ones(len(y), bool)
    clean[: 6] = False
    return {"y": y, "p": p, "pb": (p > 0).astype(int), "g": np.asarray(g), "partner": np.asarray(q), "clean": clean,
            "sens": np.ones(len(y), bool), "dbstate": None}


def test_pooled_view_keeps_drugs_apart_and_drops_unclean_older_rows():
    nov, old = toy_eval(0, prefix="x"), toy_eval(1, prefix="x")
    v = p2.Sources.pooled_view(None, nov, old)
    assert len(v["y"]) == len(nov["y"]) + int(old["clean"].sum())
    assert len(set(v["g"].tolist())) == 10 + 9
    expect = stats.stratified_auroc(v["y"], v["p"], v["g"])
    assert ev.within_stat(v, 50)["auroc_within"] == pytest.approx(expect)


def test_palette_roles_are_fixed():
    assert p2.SEMEVAL == "#0077BB" and p2.EXTERNAL == "#E8601C"
    assert p2.DRUGBANK == "#AA3377" and p2.SHORTCUT == "#6E6E6E"
    assert set(p2.ROLES) == {"SEMEVAL", "SEMEVAL_TINT", "EXTERNAL", "REF", "SHORTCUT", "RULE", "BAND"}
    assert p2.ROLE_LABEL["EXTERNAL"] == "not trained on SemEval labels"
    assert p2.ROLE_LABEL["REF"] == "external reference"


def test_band_only_for_equivalence_hypotheses():
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots()
    for h in ("H1", "H1-pooled", "H1-novel", "H4", "H6"):
        p2.draw_band(ax, h)
    for h in ("H2a", "H5", "E7", "E8", "E9", None):
        with pytest.raises(AssertionError):
            p2.draw_band(ax, h)
    plt.close(fig)


@pytest.mark.skipif(not (FIG / "figure_data_main.json").exists(), reason="figures not built")
def test_commitment8_sentence_and_language():
    md = (FIG / "FIGURES.md").read_text()
    main = md[md.index("## Main text"):md.index("## Supplement")]
    caps = {}
    name = None
    for line in main.splitlines():
        if line.startswith("### "):
            name = line[4:].split(".pdf")[0]
        elif line.startswith("**Caption draft.**"):
            caps[name] = line
    assert set(caps) == set(p2.OOD_COHORTS)
    for name, cap in caps.items():
        assert (p2.C8 in cap) == bool(p2.OOD_COHORTS[name]), name
        low = cap.lower()
        for bad in ("pair knowledge", "pair-knowledge", "ceiling", "no-signal", "knowing", "know drug"):
            assert bad not in low, (name, bad)
    first = caps["fig2_dissociation"].split(": ", 1)[1]
    assert first.index("0.480") < first.index("0.525")
    assert "by construction" in caps["fig5_positive_controls"]


@pytest.mark.skipif(not (FIG / "figure_data_main.json").exists(), reason="figures not built")
def test_caption_numbers_come_from_figure_data():
    data = json.loads((FIG / "figure_data_main.json").read_text())
    vals = set()

    def walk(o):
        if isinstance(o, dict):
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
        elif isinstance(o, (int, float)) and not isinstance(o, bool):
            for d in (2, 3):
                vals.add(f"{o:.{d}f}")
                vals.add(f"{-o:.{d}f}")
        elif isinstance(o, str):
            vals.update(re.findall(r"\d+\.\d+", o))

    walk(data)
    md = (FIG / "FIGURES.md").read_text()
    main = md[md.index("## Main text"):md.index("## Supplement")]
    caps = "\n".join(l for l in main.splitlines() if l.startswith("**Caption draft.**"))
    nums = set(re.findall(r"(?<![\w.])-?\d\.\d{2,3}(?!\d)", caps))
    missing = sorted(n for n in nums if n not in vals and n.lstrip("-") not in vals)
    assert not missing, missing


@pytest.mark.skipif(not (FIG / "figure_data_main.json").exists(), reason="figures not built")
def test_assertion_layer_ran_and_no_mean_ratio():
    data = json.loads((FIG / "figure_data_main.json").read_text())
    assert sum(v for k, v in data["checks"].items() if k != "read") > 200
    md = (FIG / "FIGURES.md").read_text()
    main = md[md.index("## Main text"):md.index("## Supplement")]
    assert "6.008" not in main
    assert "1.581" in main
    for name in p2.FIGURES:
        assert (FIG / f"{name}.pdf").exists() and (FIG / f"{name}.png").exists()


def test_marker_encoding_follows_the_shared_table():
    assert p2.MARKER["b2sentence"] == ("o", False) and p2.MARKER["b2mixed"] == ("s", False)
    assert p2.MARKER["b1names"] == ("^", True) and p2.MARKER["b2masked"] == ("D", True)
    assert p2.MARKER["qwen"] == ("v", False) and p2.MARKER["biomistral"] == ("v", True)
    assert p2.MARKER["drugbank"] == ("D", False) and p2.MARKER["h5"] == ("p", True)
    assert dict(p2.REGIMES)["b1names"] == "Names-trained"


def test_graphical_abstract_geometry_and_legibility():
    from PIL import Image
    im = Image.open(FIG / "graphical_abstract.png")
    assert im.size == p2.GA_PX and im.size[0] / im.size[1] == 2.5
    assert p2.GA_LABEL_PX >= p2.GA_MIN_LABEL_PX and p2.GA_TITLE_PX == 44 and p2.GA_LINE_PX == 8
    assert not hasattr(p2, "GA_FOOT_PX") and "\n" not in p2.GA_TITLE


@pytest.mark.skipif(not (FIG / "figure_data_main.json").exists(), reason="figures not built")
def test_hero_panel_values_and_no_figure_numbers_in_artwork():
    data = json.loads((FIG / "figure_data_main.json").read_text())
    h = data["fig2_dissociation"]
    assert h["unseen_pairs"] == 2270 and h["unseen_drugs"] == 176
    b = {r["name"]: r for r in h["panel_b"]}
    assert b["SemEval negatives"]["n_resolvable"] == 2108 and b["SemEval positives"]["n_resolvable"] == 362
    assert round(b["SemEval negatives"]["share_of_resolvable"], 3) == 0.763
    assert round(b["SemEval positives"]["share_of_resolvable"], 3) == 0.727
    assert round(h["panel_b_random"]["share"], 3) == 0.355
    qw = h["series"]["Qwen2.5-7B"]["right"]["range"]
    assert (round(qw[0], 3), round(qw[1], 3)) == (0.519, 0.607)
    assert round(h["series"]["DrugBank lookup"]["left_excl"]["value"], 3) == 0.480
    tex = (ROOT / "paper" / "figures" / "pipeline.tex").read_text()
    assert not re.search(r"Figure\s*\d", tex)
