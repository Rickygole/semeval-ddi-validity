import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ddiood import amend7_analysis as aa
from ddiood import amend7_jobs as aj
from ddiood import amend7_prompts as pr

N_BOOT = 120


def rows(prefix, n_drugs, rng, extra=()):
    out = []
    names = [f"{prefix}{i}" for i in range(n_drugs)] + list(extra)
    for d in names:
        partners = rng.choice(12, size=9, replace=False)
        for j, q in enumerate(partners):
            out.append({"ood_drug": d, "semeval_drug": f"vp{q}", "label": int(j < 3), "cooccurrence_sentence": ""})
    return out


def db_rows(rs):
    return [{"ood_drug": r["ood_drug"], "semeval_drug": r["semeval_drug"], "fda_label": r["label"],
             "drugbank_label": "positive" if r["label"] else "negative"} for r in rs]


class World:
    def __init__(self, tmp):
        rng = np.random.RandomState(0)
        self.rng = rng
        self.ood = rows("n", 30, rng)
        self.old = rows("o", 40, rng, extra=("almotriptan malate", "esmolol"))
        self.truth = aa.Truth(self.ood, self.old, db_rows(self.ood), db_rows(self.old))
        self.preds = Path(tmp) / "preds"
        self.cpu = Path(tmp) / "cpu"
        self.preds.mkdir()
        self.cpu.mkdir()
        self.y = {"ood": self.truth.sets["ood"]["y"], "oodold": self.truth.sets["oodold"]["y"]}

    def scores(self, strength, key="ood", seed=0):
        r = np.random.RandomState(seed)
        y = self.y[key]
        z = strength * (y - 0.5) * 2 + r.randn(len(y))
        return 1 / (1 + np.exp(-z))

    def write(self, name, ev, extra=None, cfg=None, cpu=False):
        res = {"config": cfg or {"name": name}, "eval": ev, **(extra or {})}
        (self.cpu if cpu else self.preds).joinpath(f"{name}.json").write_text(json.dumps(res))

    def ev(self, p):
        p = np.asarray(p)
        return {"preds": (p >= 0.5).astype(int).tolist(), "p": p.round(6).tolist()}


def make_e7(w, strengths):
    for arm, strength in strengths.items():
        for seed in aa.SEEDS:
            keys = aa.KEYS[arm]
            ev = {keys[1]: w.ev(w.scores(strength, "ood", seed)), keys[2]: w.ev(w.scores(strength, "oodold", seed + 100)),
                  keys[0]: w.ev(np.full(5, 0.5))}
            w.write(f"a7-e7{arm}-{aa.ARMS[arm]}-s{seed}", ev)


def test_e7a_and_e7b_rules(tmp_path):
    w = World(tmp_path)
    make_e7(w, {"a": 3.0, "b": 4.0})
    v = aa.e7a_verdict(w.preds, w.truth, N_BOOT)
    assert v["decision"] == "pass" and v["pooled_auroc"]["value"] >= 0.75 and v["mcc_majority_vote"] >= 0.30
    b = aa.e7b_verdict(w.preds, w.truth, {"threshold_novel": 0.9, "threshold_older_primary": 0.9}, N_BOOT)
    assert b["decision"] == "pass" and b["novel"]["within"]["lo95"] > 0.70
    hard = aa.e7b_verdict(w.preds, w.truth, {"threshold_novel": 1.01, "threshold_older_primary": 0.9}, N_BOOT)
    assert hard["decision"] == "fail" and not hard["novel"]["pass"] and hard["older_primary"]["pass"]


def test_e7a_fails_for_weak_scores_and_is_pending_without_all_seeds(tmp_path):
    w = World(tmp_path)
    make_e7(w, {"a": 0.2})
    assert aa.e7a_verdict(w.preds, w.truth, N_BOOT)["decision"] == "fail"
    (w.preds / "a7-e7a-h5contam-s4.json").unlink()
    v = aa.e7a_verdict(w.preds, w.truth, N_BOOT)
    assert v["decision"].startswith("pending") and v["complete"] is False


def test_majority_vote_and_seed_average(tmp_path):
    w = World(tmp_path)
    n = len(w.y["ood"])
    for seed, val in zip(aa.SEEDS, [0.9, 0.9, 0.9, 0.1, 0.1]):
        w.write(f"a7-e7a-h5contam-s{seed}", {"ood": w.ev(np.full(n, val))})
    avg = aa.seed_average(w.preds, "a", "ood")
    assert abs(avg["p"][0] - 0.58) < 1e-9 and avg["pb"].min() == 1 and avg["complete"]


def test_knowledge_arms_labels_kappa_and_differences(tmp_path):
    w = World(tmp_path)
    make_e7(w, {"c": 2.0, "d": 0.0, "e": 0.0})
    prior = {"ood": w.ev(np.full(len(w.y["ood"]), 0.4)), "oodold": w.ev(np.full(len(w.y["oodold"]), 0.4))}
    w.write("a7-prior-partner-train", prior, cpu=True)
    k = aa.knowledge_arms(w.preds, w.truth, w.cpu, n=N_BOOT)
    assert k["c"]["novel/A"]["label"] == "signal" and k["c"]["older_primary/A"]["label"] == "signal"
    assert k["d"]["older_primary/A"]["label"] in ("no signal", "neither")
    assert k["c"]["older_primary/A"]["paired_vs_partner_prior"]["lo95"] > 0
    db = {"ood": aa.drugbank_scores(w.ood, db_rows(w.ood)), "oodold": aa.drugbank_scores(w.old, db_rows(w.old))}
    k = aa.add_kappas(k, w.truth, db, N_BOOT)
    e = k["c"]["novel/A"]
    assert abs(e["kappa"] - (e["within"]["value"] - 0.5) / (e["drugbank_within"] - 0.5)) < 1e-12
    diffs = aa.arm_differences(w.preds, w.truth, N_BOOT)
    assert diffs["novel/c-d"]["value"] > 0 and diffs["novel/c-d"]["lo95"] > 0
    sel = w.truth.cohort("older_primary")
    assert "almotriptan malate" not in set(sel["g"]) and "esmolol" not in set(sel["g"])
    assert "esmolol" in set(w.truth.cohort("older_clean")["g"])


def test_additive_residual_removes_partner_effect():
    rng = np.random.RandomState(1)
    g = np.repeat(np.arange(20), 8)
    q = rng.randint(0, 6, len(g))
    noise = rng.randn(len(g)) * 0.3
    s = rng.randn(20)[g] + 3 * rng.randn(6)[q] + noise
    res = aa.additive_residual(s, g, q)
    assert np.corrcoef(res, noise)[0, 1] > 0.8
    assert abs(res.mean()) < 1e-6


def test_names_prompts_oracle_rule_and_stem_control(tmp_path):
    w = World(tmp_path)
    n1, n2 = len(w.y["ood"]), len(w.y["oodold"])
    ev = {}
    for i, (pid, _, _) in enumerate(pr.NAMES_PROMPTS):
        ev[f"ood_{pid}"] = w.ev(w.scores(1.0 + (2.0 if i == 4 else 0), "ood", i))
        ev[f"oodold_{pid}"] = w.ev(w.scores(1.0 + (2.0 if i == 4 else 0), "oodold", i + 9))
    ev["ood"], ev["oodold"] = ev[f"ood_{pr.PRIMARY}"], ev[f"oodold_{pr.PRIMARY}"]
    w.write("a7-qwen-names", ev, {"answer": {"ood": {"non_answers": 0}}})
    r = aa.names_prompts(w.preds, w.truth, N_BOOT)
    assert r["robust"] is False and r["cohorts"]["novel"]["max"] > r["cohorts"]["novel"]["primary"] + 0.05
    w.write("a7-qwen-oracle", {"ood": w.ev(w.scores(6.0, "ood", 1)), "oodold": w.ev(w.scores(6.0, "oodold", 2))})
    grep = {"ood": w.ev(w.y["ood"].astype(float)), "oodold": w.ev(w.y["oodold"].astype(float))}
    w.write("a7-grep-qwen-oracle", grep, cpu=True)
    o = aa.oracle_rule(w.preds, w.truth, w.cpu, N_BOOT)
    assert o["novel"]["bar"] == 0.95 and o["older_primary"]["statistic"] == "lower95"
    assert o["decision"] == "pass"
    w.write("a7-qwen-oracle", {"ood": w.ev(w.scores(1.0, "ood", 1)), "oodold": w.ev(w.scores(1.0, "oodold", 2))})
    assert aa.oracle_rule(w.preds, w.truth, w.cpu, N_BOOT)["decision"] == "fail"
    idx_n = list(range(0, n1, 2))
    idx_o = [i for i in range(0, n2, 2) if w.truth.sets["oodold"]["g"][i] not in aa.OLDER_ARTIFACTS + aa.OLDER_MISSED]
    for name, strength in (("preserved", 3.0), ("scrambled", 0.5)):
        sub = {"ood": {**w.ev(w.scores(strength, "ood", 5)[idx_n]), "index": idx_n},
               "oodold": {**w.ev(w.scores(strength, "oodold", 6)[idx_o]), "index": idx_o}}
        w.write(f"a7-qwen-stem-{name}", sub)
    s = aa.stem_control(w.preds, w.truth, N_BOOT)
    assert s["expected_drop_observed"] is True and s["preserved_minus_scrambled"]["value"] > 0.05
    assert s["n_rows"] == len(idx_n) + len(idx_o)


def test_evidence_arms_report_tiers_and_context(tmp_path):
    w = World(tmp_path)
    w.write("a7-qwen-names", {"ood": w.ev(w.scores(0.5, "ood", 1)), "oodold": w.ev(w.scores(0.5, "oodold", 2))})
    w.write("a7-qwen-clean", {"ood": w.ev(w.scores(1.0, "ood", 3)), "oodold": w.ev(w.scores(1.0, "oodold", 4))},
            {"context": {"ood": {"positives_with_partner_in_context": 0.4, "partner_in_context": [0]}}, "answer": {}})
    a = aa.evidence_arms(w.preds, w.truth, N_BOOT)
    assert set(a["clean"]) >= {"novel/A", "novel/B", "older_primary/A", "context"}
    assert a["clean"]["novel/A"]["minus_names_only"]["value"] > 0
    assert '"partner_in_context"' not in json.dumps(a["clean"]["context"])


def test_panel_outputs_and_masked_reported_separately(tmp_path):
    w = World(tmp_path)
    rng = np.random.RandomState(3)
    ytest = rng.randint(0, 2, 60)
    def job(name, variant, strength, f1_noise):
        pt = (ytest ^ (rng.rand(60) < f1_noise)).astype(int)
        ev = {"test_sentence": {"preds": pt.tolist(), "p": pt.astype(float).tolist()},
              "ood_empty": w.ev(w.scores(strength, "ood", len(name))), "oodold_empty": w.ev(w.scores(strength, "oodold", len(name) + 1))}
        w.write(name, ev, cfg={"name": name, "variant": variant})
    for i in range(5):
        job(f"a7-panel-m{i}-pair", "pair", 0.3 * i, 0.4 - 0.07 * i)
    job("a7-panel-x-masked", "masked", 0.0, 0.1)
    out = aa.panel(w.preds, w.truth, ytest, N_BOOT)
    assert out["panel"]["novel"]["n_models"] == 5 and "a7-panel-x-masked" in out["masked"]["novel"]
    assert out["panel"]["older_primary"]["n_models"] == 5
    assert len(out["panel"]["novel"]["upper_at_most_bound"]) == 5


def test_clean_serializes_numpy_and_nan():
    out = aa.clean({"a": np.float64("nan"), "b": np.array([1, 2]), "c": np.bool_(True), "d": np.int64(3)})
    assert out == {"a": None, "b": [1, 2], "c": True, "d": 3}
    json.dumps(out)
    assert aj.registry()
