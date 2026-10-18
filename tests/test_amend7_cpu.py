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
sys.path.insert(0, str(ROOT / "tests"))

from ddiood import config, inputs, stats
from ddiood import evaluate2 as ev

import amend7_cpu_common as common
import amend7_cpu_exp5_dissociation as exp5
import amend7_cpu_exp6_control_reach as exp6
import amend7_cpu_exp7_below_chance as exp7
import amend7_cpu_kappa_weighting as kw
from test_evaluate2 import ood_rows, write

NEW = ["scripts/amend7_cpu_common.py", "scripts/amend7_cpu_exp5_dissociation.py",
       "scripts/amend7_cpu_exp6_control_reach.py", "scripts/amend7_cpu_exp7_below_chance.py",
       "scripts/amend7_cpu_kappa_weighting.py",
       "tests/test_amend7_cpu.py", "ddiood/evaluate2.py", "ddiood/config.py"]


@pytest.fixture(scope="module")
def truth():
    rng = np.random.RandomState(0)
    labels = [int(v) for v in rng.choice([0, 0, 0, 1, 2, 3, 4], 80)]
    old = ood_rows("old", 12, 8, 2) + [{"ood_drug": "esmolol", "semeval_drug": f"partner{q}", "label": str(q % 2),
                                         "cooccurrence_sentence": ""} for q in range(6)]
    return ev.Truth(labels, ood_rows("nov", 20, 10, 1), old)


def test_config_seeds_match_evaluator():
    assert config.SEEDS == [42, 1, 2, 3, 4]
    assert sorted(config.SEEDS) == sorted(ev.SEEDS)


def test_sensitivity_view_drops_missed_drugs(truth):
    s = truth.sets["oodold"]
    assert int((~s["sens"]).sum()) == 6
    e = {"y": np.asarray(s["y"]), "p": np.linspace(0, 1, len(s["y"])), "pb": np.zeros(len(s["y"]), int),
         "g": np.asarray(s["g"]), "partner": np.asarray(s["partner"]), "clean": s["clean"], "sens": s["sens"],
         "dbstate": None}
    assert len(ev.view(e, "older_clean")["y"]) == len(s["y"])
    assert len(ev.view(e, "older_clean_sensitivity")["y"]) == len(s["y"]) - 6


def test_pooled_ci_rename_keeps_json_keys():
    rows = ev.pooled_ci_rows([{"auroc_lo": 0.1, "auroc_hi": 0.2, "auroc2_lo": 0.05, "auroc2_hi": 0.3, "n": 3}])
    assert rows == [{"auroc_pooled_lo95": 0.1, "auroc_pooled_hi95": 0.2, "auroc_pooled2_lo95": 0.05,
                     "auroc_pooled2_hi95": 0.3, "n": 3}]


def test_h2_spread_reports_median_and_per_seed():
    ms = [{"seed": s, "ratio": r, "f1_masked": fm, "f1_sentence": 0.5} for s, r, fm in
          ((1, 4.0, 2.0), (2, 1.0, 0.5), (3, 2.0, 1.0))]
    sw = [{"seed": s, "swap": k, "flip_rate": 0.2 if s == 3 and k == "novel" else 0.05} for s in (1, 2, 3) for k in ev.KINDS]
    txt = ev.h2_spread(ms, sw)
    assert "median ratio 2.000" in txt
    assert "ratio of mean F1s 2.333" in txt
    assert "s3 ratio 2.000" in txt and "(over 0.10: novel)" in txt
    assert "not preregistered" in txt


def test_evaluation_with_masked_model_and_sensitivity_row(tmp_path, truth):
    d = tmp_path / "preds"
    d.mkdir()
    for s in ev.SEEDS:
        write(d, truth, "b2mixed", seed=s, sig=0.0)
        write(d, truth, "b2sentence", seed=s, sig=0.0)
        write(d, truth, "b2masked", seed=s, sig=0.0)
    t = ev.evaluate(d, tmp_path / "out", truth, boot=100)
    dec = t["decisions"]
    assert list(dec)[:4] == ["H1", "H1-novel", "H1-pooled", "H1-sensitivity"]
    assert dec["H1-sensitivity"]["decision"] == "sensitivity, not preregistered (no decision rule)"
    assert dec["H1-sensitivity"]["p_holm"] is None and "n=96" in dec["H1-sensitivity"]["detail"]
    assert "median ratio" in dec["H2b"]["detail"] and "median ratio" not in dec["H2a"]["detail"]
    assert set(dec["H2b"]["value"]) == {"ratio", *ev.KINDS}
    md = (tmp_path / "out" / "tables.md").read_text()
    assert "auroc_pooled_lo95" in md and "auroc_pooled2_hi95" in md
    row = next(r for r in t["per_job"] if r["key"] == "ood_empty")
    assert "auroc_lo" in row and "auroc_pooled_lo95" not in row


def test_fast_within_auroc_and_paired_draws_match_stats():
    rng = np.random.RandomState(4)
    n = 240
    g, q = rng.randint(0, 25, n), rng.randint(0, 12, n)
    y = rng.randint(0, 2, n)
    s1, s2 = np.round(rng.rand(n), 1), rng.rand(n) + 0.3 * y
    assert common.fast_within_auroc(y, s1, g) == pytest.approx(stats.stratified_auroc(y, s1, g))
    d = common.paired_draws(y, [s1, s2], g, q, 150, 9)
    ref = stats.two_way_samples(stats.stratified_auroc, y, s2, g, q, 150, 9, strat=g)
    assert d.shape[1] == len(ref)
    assert np.allclose(d[1], ref)


def test_drugbank_resolution_on_semeval_pairs():
    table = {"warfarin": {"aspirin"}, "aspirin": {"warfarin"}, "digoxin": set()}
    assert exp5.resolve("warfarin", "aspirin", table, {}) == ("positive", 2)
    assert exp5.resolve("digoxin", "aspirin", table, {}) == ("negative", 2)
    assert exp5.resolve("digoxin", "unknownium", table, {}) == ("negative", 1)
    assert exp5.resolve("foo", "bar", table, {}) == ("unresolvable", 0)
    lookup = {"coumadin": {"normalized": "warfarin", "canonicalized": "warfarin"}}
    assert exp5.resolve("coumadin", "aspirin", table, lookup)[0] == "positive"


def test_partner_named_and_model_input():
    assert exp6.named("aspirin", "Low-dose ASPIRIN increases")
    assert not exp6.named("aspirin", "acetylaspirinate")
    assert not exp6.named("ace", "ace-inhibitor")
    texts = ["x" * 500, "partner text"]
    full, evidence = exp6.model_input("a", "b", texts)
    assert full == inputs.krag([{"drug_a": "a", "drug_b": "b"}], {"a|||b": texts}, chars=400, k=5)[0]
    assert full.endswith(evidence) and len(evidence) == 400 + len(" [SEP] ") + len("partner text")
    assert exp6.model_input("a", "b", []) == ("a [SEP] b", "")


class Tok:
    def __call__(self, text, truncation, max_length, return_offsets_mapping):
        spans = [(i, i + 1) for i in range(len(text))][:max_length - 2]
        return {"offset_mapping": [(0, 0)] + spans + [(0, 0)]}


def test_visible_evidence_truncates_at_token_limit():
    full, evidence = exp6.model_input("a", "b", ["y" * 400, "z" * 400])
    seen = exp6.visible_evidence(Tok(), full, evidence)
    assert len(seen) == config.MAX_LENGTH - 2 - (len(full) - len(evidence))
    assert evidence.startswith(seen)


def test_leave_one_drug_out_partner_features():
    y = np.array([1, 0, 0, 1, 0])
    g = np.array(["d1", "d1", "d2", "d2", "d3"])
    q = np.array(["p", "r", "p", "r", "p"])
    cnt, rate = exp7.loo_partner(y, g, q)
    assert cnt.tolist() == [0.0, 1.0, 1.0, 0.0, 1.0]
    assert rate.tolist() == [0.0, 1.0, 0.5, 0.0, 0.5]


def test_shared_stem():
    assert exp7.shared_stem("atorvastatin", "simvastatin") == 1.0
    assert exp7.shared_stem("metoprolol tartrate", "propranolol") == 1.0
    assert exp7.shared_stem("warfarin", "aspirin") == 0.0
    assert exp7.shared_stem("esmolol", "esmolol hydrochloride") == 0.0


def test_partial_removes_a_linear_feature_within_drug():
    rng = np.random.RandomState(2)
    g = np.repeat(np.arange(30), 8)
    f = rng.rand(len(g))
    s = 3.0 * f + rng.normal(0, 1, 30)[g]
    res, beta = exp7.partial(s, [f], g)
    assert beta[0] == pytest.approx(3.0)
    assert np.allclose(exp7.demean(res, g), 0, atol=1e-9)


def test_within_rank_assoc_sign():
    rng = np.random.RandomState(5)
    g = np.repeat(np.arange(20), 6)
    f = rng.rand(len(g))
    up = exp7.within_rank_assoc(f + 0.01 * rng.rand(len(g)), f, g, 50)
    down = exp7.within_rank_assoc(-f, f, g, 50)
    assert up["value"] > 0.9 and down["value"] == pytest.approx(-1.0)


def test_judge_and_cause_d_rules():
    feat = {"value": 0.40, "ci95": [0.30, 0.48]}
    assoc = {"value": 0.3, "ci95": [0.1, 0.5]}
    assert exp7.judge("a", feat, assoc, 0.40, 0.48)["verdict"] == "confirmed"
    assert exp7.judge("a", feat, assoc, 0.40, 0.42)["verdict"] == "partial"
    assert exp7.judge("a", feat, {"value": -0.3, "ci95": [-0.5, -0.1]}, 0.40, 0.48)["verdict"] == "rejected"
    assert exp7.judge("a", {"value": 0.6, "ci95": [0.52, 0.7]}, assoc, 0.40, 0.48)["verdict"] == "rejected"
    assert exp7.judge("c", {"value": 0.6, "ci95": [0.52, 0.7]}, {"value": -0.3, "ci95": [-0.5, -0.1]}, 0.40, 0.48)["verdict"] == "confirmed"
    assert exp7.cause_d({"value": 0.45}, {"value": 0.40, "ci95": [0.3, 0.5]})["verdict"] == "rejected"
    assert exp7.cause_d({"value": 0.40}, {"value": 0.48, "ci95": [0.4, 0.56]})["verdict"] == "confirmed"
    assert exp7.cause_d({"value": 0.40}, {"value": 0.47, "ci95": [0.41, 0.49]})["verdict"] == "partial"


def test_ece():
    y = np.array([0, 0, 1, 1])
    assert exp7.ece(y, np.array([0.0, 0.0, 1.0, 1.0])) == pytest.approx(0.0)
    assert exp7.ece(y, np.array([0.5, 0.5, 0.5, 0.5])) == pytest.approx(0.0)
    assert exp7.ece(y, np.array([1.0, 1.0, 0.0, 0.0])) == pytest.approx(1.0)


def test_criteria_file_precedes_results():
    out = ROOT / "results" / "revision" / "amend7" / "cpu"
    crit = json.loads((out / "exp7_criteria.json").read_text())
    assert set(crit["causes"]) == {"a", "b", "c", "d", "e"}
    res = out / "exp7_below_chance.json"
    if res.exists():
        assert json.loads(res.read_text())["criteria"] == crit


def test_new_sources_are_clean():
    for f in NEW:
        txt = (ROOT / f).read_text()
        assert chr(0x2013) not in txt and chr(0x2014) not in txt
        assert "cla" + "ude" not in txt.lower()
        if f.endswith(".py"):
            assert not [t for t in tokenize.generate_tokens(io.StringIO(txt).readline) if t.type == tokenize.COMMENT]
    for p in (ROOT / "results" / "revision" / "amend7" / "cpu").glob("*"):
        txt = p.read_text()
        assert chr(0x2013) not in txt and chr(0x2014) not in txt and "cla" + "ude" not in txt.lower()


def test_drug_weighted_auroc_and_kappa():
    y = np.array([1, 0, 1, 0, 0, 0, 1])
    s = np.array([0.9, 0.1, 0.2, 0.8, 0.7, 0.6, 0.5])
    g = np.array([0, 0, 1, 1, 1, 1, 2])
    assert kw.drug_weighted_auroc(y, s, g) == pytest.approx(0.5)
    assert stats.stratified_auroc(y, s, g) == pytest.approx(0.25)
    assert kw.kappa(0.60, 0.641) == pytest.approx(0.709, abs=1e-3)
    rng = np.random.RandomState(1)
    gg, qq = rng.randint(0, 15, 200), rng.randint(0, 9, 200)
    yy, ss = rng.randint(0, 2, 200), rng.rand(200)
    a = kw.draws_with(common.fast_within_auroc, yy, [ss], gg, qq, 80, 3)[0]
    b = common.paired_draws(yy, [ss], gg, qq, 80, 3)[0]
    assert np.allclose(a, b)


def test_own_label_leak_rule():
    chunks = {1: {"drug": "nov", "section": "warnings_and_cautions", "text": "avoid warfarin"},
              2: {"drug": "other", "section": "drug_interactions", "text": "digoxin"}}

    class T:
        def __call__(self, text, truncation, max_length, return_offsets_mapping):
            return {"offset_mapping": [(0, 0), (0, len(text)), (0, 0)]}
    pairs = [{"ood_drug": "nov", "semeval_drug": "warfarin", "label": "1"},
             {"ood_drug": "nov", "semeval_drug": "digoxin", "label": "0"}]
    rows = exp6.reach_rows(pairs, {"nov|||warfarin": [1, 2], "nov|||digoxin": [1, 2]}, chunks, T())
    assert rows[0]["partner_in_own_label_chunk"] and not rows[1]["partner_in_own_label_chunk"]
    assert rows[1]["partner_in_full_chunks"] and not rows[1]["di_chunk_of_ood_drug"]
