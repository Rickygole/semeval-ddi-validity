import io
import json
import sys
import tokenize
from pathlib import Path

import numpy as np
import pytest
from sklearn.metrics import roc_auc_score

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ddiood import evaluate2 as ev
from ddiood import figures2, inputs


def ood_rows(prefix, n_drugs, n_part, seed):
    rng = np.random.RandomState(seed)
    rows = []
    for d in range(n_drugs):
        for q in range(n_part):
            y = int(rng.rand() < 0.4)
            rows.append({"ood_drug": f"{prefix}{d}", "semeval_drug": f"partner{q}", "label": str(y),
                         "cooccurrence_sentence": f"{prefix}{d} with partner{q}" if y or q % 2 else ""})
    return rows


@pytest.fixture(scope="module")
def truth():
    rng = np.random.RandomState(0)
    labels = [int(v) for v in rng.choice([0, 0, 0, 1, 2, 3, 4], 80)]
    return ev.Truth(labels, ood_rows("nov", 20, 10, 1), ood_rows("old", 12, 8, 2))


def scores(rng, y, signal):
    p = np.clip(0.5 + signal * (np.asarray(y) - 0.5) + rng.normal(0, 0.15, len(y)), 0.01, 0.99)
    return {"p": [round(float(v), 6) for v in p], "preds": [int(v > 0.5) for v in p]}


def write(d, truth, system, model="biomedbert", seed=42, kind="bert", sig=0.0, test_sig=0.8, **kw):
    cfg = {"kind": kind, "system": system, "model": model, "seed": seed, "priority": 1, "split": "standard",
           "epochs": 3, "variant": "hybrid", "k": 5, "chars": 100}
    cfg.update(kw)
    cfg["name"] = f"{system}-{model}-{cfg['variant']}-{cfg['split']}-s{seed}"
    rng = np.random.RandomState(seed + hash(system) % 1000)
    o, old = truth.sets["ood"], truth.sets["oodold"]
    yt = truth.test_y
    ey = {}
    if system == "krag":
        ey = {"test": scores(rng, yt, test_sig), "ood": scores(rng, o["y"], sig)}
    elif system == "b1names":
        ey = {"test_names": scores(rng, yt, test_sig), "ood_names": scores(rng, o["y"], sig),
              "oodold_names": scores(rng, old["y"], sig)}
        for k in ev.KINDS:
            ey[f"swap_{k}_names"] = scores(rng, yt, test_sig)
    elif system in ("names", "rag"):
        ey = {"test": scores(rng, yt, 0.0), "ood": scores(rng, o["y"], sig), "oodold": scores(rng, old["y"], sig)}
    else:
        idx = [i for i, s in enumerate(inputs.ood_as_pairs(_rows(truth, "ood"))) if s["sentence"]]
        oidx = [i for i, s in enumerate(inputs.ood_as_pairs(_rows(truth, "oodold"))) if s["sentence"]]
        ey = {"test_sentence": scores(rng, yt, test_sig), "test_masked": scores(rng, yt, test_sig),
              "test_empty": scores(rng, yt, 0.2), "test_names": scores(rng, yt, 0.2),
              "ood_empty": scores(rng, o["y"], sig), "ood_names": scores(rng, o["y"], sig),
              "ood_sentence": {**scores(rng, [o["y"][i] for i in idx], 0.3), "index": idx},
              "oodold_empty": scores(rng, old["y"], sig),
              "oodold_sentence": {**scores(rng, [old["y"][i] for i in oidx], 0.3), "index": oidx}}
        sy = [int(i % 2 == 0) for i in range(len(truth.swap_groups))]
        ey["ood_swap_sentence"] = {**scores(rng, sy, sig), "y": sy}
        for k in ev.KINDS:
            ey[f"swap_{k}_sentence"] = scores(rng, yt, test_sig)
        if cfg["split"] == "disjoint":
            ey["test_unseen_index"] = list(range(0, len(yt), 3))
    res = {"config": cfg, "config_hash": "h", "ood_hash": o["hash"], "ood_old_hash": old["hash"], "eval": ey,
           "history": [], "seconds": 1.0}
    (Path(d) / f"{cfg['name']}.json").write_text(json.dumps(res))
    return cfg["name"]


def _rows(truth, tag):
    return [{"ood_drug": p["drug_a"], "semeval_drug": p["drug_b"], "label": str(p["y"]),
             "cooccurrence_sentence": p["sentence"]} for p in truth.sets[tag]["pairs"]]


def test_fast_auroc_matches_sklearn():
    rng = np.random.RandomState(3)
    y = rng.randint(0, 2, 300)
    p = np.round(rng.rand(300), 1)
    assert ev.auroc(y, p) == pytest.approx(roc_auc_score(y, p))
    assert np.isnan(ev.auroc(np.ones(5), rng.rand(5)))


def test_bootstrap_interval_covers_estimate_and_two_way_wider():
    rng = np.random.RandomState(1)
    g = np.repeat(np.arange(20), 10)
    q = np.tile(np.arange(10), 20)
    y = rng.randint(0, 2, 200)
    p = y * 0.5 + rng.rand(200)
    lo, hi = ev.interval(ev.boot_auroc(y, p, g, None, 300))
    lo2, hi2 = ev.interval(ev.boot_auroc(y, p, g, q, 300))
    assert lo <= ev.auroc(y, p) <= hi
    assert hi2 - lo2 > 0


def test_holm_and_tost():
    adj = ev.holm({"a": 0.01, "b": 0.04, "c": None})
    assert adj["a"] == pytest.approx(0.03)
    assert adj["b"] == pytest.approx(0.08)
    assert adj["c"] == 1.0
    assert ev.tost_p(np.full(100, 0.5)) < 0.05
    assert ev.tost_p(np.full(100, 0.7)) > 0.5


def test_clean_keeps_digits_for_three_decimal_display():
    assert ev.md_table(ev.clean([{"v": 0.660535}]), ["v"]).endswith("| 0.661 |\n")


def test_hash_mismatch_refused(tmp_path, truth):
    write(tmp_path, truth, "krag")
    f = next(tmp_path.glob("*.json"))
    res = json.loads(f.read_text())
    res["ood_hash"] = "bad"
    f.write_text(json.dumps(res))
    with pytest.raises(ValueError, match="ood_hash"):
        ev.load_jobs(tmp_path, truth)


def test_length_mismatch_refused(tmp_path, truth):
    write(tmp_path, truth, "krag")
    f = next(tmp_path.glob("*.json"))
    res = json.loads(f.read_text())
    res["eval"]["ood"]["p"] = res["eval"]["ood"]["p"][:-1]
    f.write_text(json.dumps(res))
    with pytest.raises(ValueError, match="length"):
        ev.load_jobs(tmp_path, truth)


def test_full_evaluation(tmp_path, truth):
    d = tmp_path / "preds"
    d.mkdir()
    for s in ev.SEEDS:
        write(d, truth, "b2mixed", seed=s, sig=0.0)
        write(d, truth, "b2sentence", seed=s, sig=0.0)
    write(d, truth, "b2sentence", split="disjoint")
    write(d, truth, "b1names")
    for s in ev.SEEDS:
        write(d, truth, "krag", seed=s, variant="contaminated", chars=400, sig=2.0)
    write(d, truth, "names", model="biomistral", kind="llm")
    out = tmp_path / "out"
    bl = {"novel": {"n": 200, "baselines": {"partner_frequency_prior": {
        "auroc": 0.55, "auroc_ci95": {"lower": 0.5, "upper": 0.6}, "prevalence": 0.4, "binary_f1": 0.4, "mcc": 0.1,
        "balanced_accuracy": 0.5, "confusion": {"tp": 1, "fp": 2, "fn": 3, "tn": 4}}}},
          "older": {"n": 96, "baselines": {"partner_frequency_prior": {"auroc": 0.6}}}}
    t = ev.evaluate(d, out, truth, boot=200, baselines=bl)
    assert {r["set"] for r in t["baselines"]} == {"Novel OOD", "Older OOD"}
    assert "partner_frequency_prior" in (out / "tables.md").read_text()
    pr = next(r for r in t["seeds"] if r["group"] == "krag/biomedbert/contaminated-k5-c400" and r["key"] == "ood")
    assert pr["partner_prior_auroc"] == 0.55 and pr["beats_partner_prior"] is True
    for name in ("tables.json", "tables.md", "decisions.md"):
        assert (out / name).exists()
    assert json.loads((out / "tables.json").read_text())["decisions"]["H1"]["decision"] == t["decisions"]["H1"]["decision"]
    dec = t["decisions"]
    assert dec["H5"]["decision"] == "supported"
    assert dec["H6"]["decision"].startswith("pending")
    assert dec["H1"]["decision"] in ("supported", "inconclusive")
    assert dec["H1"]["cohort"] == "Older-clean" and dec["H1"]["interval90"] and dec["H1"]["interval"]
    assert dec["H2b"]["decision"].startswith("pending")
    assert dec["H3"]["decision"] == "descriptive only" and dec["H3"]["p_holm"] is None
    assert dec["H2a"]["decision"] in ("supported", "inconclusive", "falsified")
    row = next(r for r in t["per_job"] if r["key"] == "ood_empty" and r["seed"] == 42 and r["system"] == "b2mixed")
    assert row["n"] == 200 and row["auroc_lo"] <= row["auroc"] <= row["auroc_hi"]
    assert row["tp"] + row["fp"] + row["fn"] + row["tn"] == 200
    sent = next(r for r in t["per_job"] if r["key"] == "ood_sentence" and r["system"] == "b2mixed")
    assert sent["n"] < 200
    seeds = next(r for r in t["seeds"] if r["group"] == "b2mixed/biomedbert" and r["key"] == "ood_empty")
    assert seeds["n_seeds"] == 5 and seeds["seed_auroc_sd"] is not None
    assert {r["swap"] for r in t["swap"]} == set(ev.KINDS)
    assert all(0 <= r["flip_rate"] <= 1 for r in t["swap"])
    assert all(r["ratio"] is not None for r in t["masking"])
    assert {r["subset"] for r in t["disjoint"]} == {"unseen", "seen"}
    assert sum(r["n"] for r in t["disjoint"] if r["key"] == "test_sentence" and r["subset"] in ("seen", "unseen")) == 80
    assert any(r["format"] == "names only" and r["novelty"] == "Novel OOD" for r in t["grid"])
    assert "pending (0 of 5 seeds)" in (out / "decisions.md").read_text()
    for s in (out / "tables.md", out / "decisions.md"):
        txt = s.read_text()
        assert chr(0x2013) not in txt and chr(0x2014) not in txt


def test_informative_names_model_is_falsified(tmp_path, truth):
    d = tmp_path / "preds"
    d.mkdir()
    for s in ev.SEEDS:
        write(d, truth, "b2mixed", seed=s, sig=2.5)
    t = ev.evaluate(d, tmp_path / "o", truth, boot=200)
    assert t["decisions"]["H1"]["decision"] == "falsified"
    assert t["decisions"]["H4"]["decision"] == "inconclusive"


def test_missing_seeds_not_run(tmp_path, truth):
    d = tmp_path / "preds"
    d.mkdir()
    write(d, truth, "b2mixed", seed=42)
    t = ev.evaluate(d, tmp_path / "o", truth, boot=100)
    assert t["decisions"]["H1"]["decision"] == "pending (1 of 5 seeds)"


def test_figures(tmp_path, truth):
    d = tmp_path / "preds"
    d.mkdir()
    for s in (1, 42):
        write(d, truth, "b2mixed", seed=s, sig=1.0)
        write(d, truth, "b2sentence", seed=s, sig=1.0)
    write(d, truth, "b1names")
    write(d, truth, "krag", variant="contaminated", chars=400, sig=1.0)
    write(d, truth, "names", model="biomistral", kind="llm")
    t = ev.evaluate(d, tmp_path / "o", truth, boot=100)
    aggs = ev.aggregate(ev.load_jobs(d, truth))
    paths = figures2.make_all(aggs, t, tmp_path / "fig")
    assert len(paths) == 5
    for p in paths:
        assert Path(p).stat().st_size > 1000


def test_no_forbidden_characters_in_sources():
    for f in ("evaluate2.py", "figures2.py"):
        txt = (ROOT / "ddiood" / f).read_text()
        assert chr(0x2013) not in txt and chr(0x2014) not in txt
        assert "cla" + "ude" not in txt.lower()
        assert not [t for t in tokenize.generate_tokens(io.StringIO(txt).readline) if t.type == tokenize.COMMENT]


def test_older_clean_filter_and_tiers():
    rows = ood_rows("old", 3, 4, 5) + [{"ood_drug": "benzoate", "semeval_drug": "partner0", "label": "1",
                                       "cooccurrence_sentence": ""},
                                      {"ood_drug": "rizatriptan benzoate", "semeval_drug": "partner0", "label": "0",
                                       "cooccurrence_sentence": ""}]
    db = [{"ood_drug": r["ood_drug"], "semeval_drug": r["semeval_drug"], "fda_label": r["label"],
           "drugbank_label": "positive" if r["label"] == "1" else "negative"} for r in rows]
    t = ev.Truth([0, 1], ood_rows("nov", 2, 2, 1), rows, {"oodold": db})
    assert int((~t.sets["oodold"]["clean"]).sum()) == 1
    assert (t.sets["oodold"]["dbstate"] == 1).all()
    assert t.sets["ood"]["dbstate"] is None
    e = {"y": np.array([1, 0]), "p": np.array([0.2, 0.1]), "pb": np.array([0, 0]), "g": None, "partner": None,
         "clean": np.array([True, False]), "dbstate": None}
    assert len(ev.view(e, "older_clean")["y"]) == 1
    assert ev.view(e, "older_clean", "B") is None


def test_five_seed_gate_and_within_drug(tmp_path, truth):
    d = tmp_path / "preds"
    d.mkdir()
    for s in (1, 2, 3, 4):
        write(d, truth, "b2mixed", seed=s, sig=0.0)
    t = ev.evaluate(d, tmp_path / "o", truth, boot=100)
    assert t["decisions"]["H1"]["decision"] == "pending (4 of 5 seeds)"
    write(d, truth, "b2mixed", seed=42, sig=0.0)
    t = ev.evaluate(d, tmp_path / "o", truth, boot=200)
    assert not t["decisions"]["H1"]["decision"].startswith("pending")
    assert (tmp_path / "o" / "decisions.json").exists()
    rows = [r for r in t["ood_cohorts"] if r["tier"] == "B"]
    assert rows and all(r["status"] == "not available" for r in rows)
