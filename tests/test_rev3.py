import ast
import io
import json
import os
import re
import subprocess
import sys
import tokenize
import zipfile
from pathlib import Path

import numpy as np
import pytest
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from ddiood import evaluate2 as ev
from ddiood import rev2_adjudicator as ra
from ddiood import rev3_jobs as rj
from ddiood import rev3_tac as rt
from ddiood.rev3_pairlabel import NEGATIVE, POSITIVE, UNDECIDED, PairLabeler
import rev3_c1 as c1
import rev3_c2 as c2
import rev3_c3 as c3
import rev3_make_notebooks as mk
import rev3_score_tac as st

NEW = ["ddiood/rev3_pairlabel.py", "ddiood/rev3_tac.py", "ddiood/rev3_jobs.py", "scripts/rev3_common.py", "scripts/rev3_c1.py",
       "scripts/rev3_c2.py", "scripts/rev3_c3.py", "scripts/rev3_score_tac.py", "scripts/rev3_estimate.py",
       "scripts/rev3_make_notebooks.py", "scripts/rev3_build_bundle.sh", "tests/test_rev3.py", "colab/experiments/R2c_tac_calibration.ipynb"]
FROZEN = ["ddiood/bert.py", "ddiood/gpu_jobs.py"] + [f"ddiood/{p.name}" for p in (ROOT / "ddiood").glob("amend7_*.py")] + \
         [f"ddiood/{p.name}" for p in (ROOT / "ddiood").glob("rev2_*.py")] + [f"scripts/{p.name}" for p in (ROOT / "scripts").glob("rev2_*.py")]


def test_frozen_modules_are_unchanged_since_the_plan_commit():
    env = {**os.environ, "DEVELOPER_DIR": "/Library/Developer/CommandLineTools"}
    r = subprocess.run(["git", "diff", "--name-only", "HEAD", "--"] + FROZEN, cwd=ROOT, capture_output=True, text=True, env=env)
    if r.returncode != 0:
        pytest.skip("git unavailable")
    assert r.stdout.strip() == ""


def test_r2b_frozen_constants_are_intact():
    assert ra.prompt_sha256() == ra.EXPECTED_PROMPT_SHA256
    assert ra.EXPECTED_ITEMS_SHA256 == "2f4410cb00e0a8bb3b098493e4a5d15460e2d1f3da2112bac44a6a4f96097cf4"
    assert ra.OLMO_REVISION == rj.PLAN_OLMO_REVISION == "470b1fba1ae01581f270116362ee4aa1b97f4c84"
    rj.assert_frozen_r2b()


def test_new_files_have_no_dashes_no_comments_no_forbidden_string():
    for f in NEW + ["docs/POSTHOC_REV3_PLAN.md"]:
        txt = (ROOT / f).read_text()
        assert chr(0x2013) not in txt and chr(0x2014) not in txt, f
        assert "cla" + "ude" not in txt.lower(), f
        if f.endswith(".py"):
            assert not [t for t in tokenize.generate_tokens(io.StringIO(txt).readline) if t.type == tokenize.COMMENT], f
            tree = ast.parse(txt)
            assert not [n for n in ast.walk(tree) if isinstance(n, (ast.Module, ast.FunctionDef, ast.ClassDef)) and ast.get_docstring(n)], f


def test_notebook_is_code_only_mounts_drive_asserts_gpu_and_matches_the_generator():
    for name, jobs in rj.notebook_jobs().items():
        nb = json.loads((ROOT / "colab" / "experiments" / f"{name}.ipynb").read_text())
        assert nb == mk.build(name, jobs)
        assert all(c["cell_type"] == "code" for c in nb["cells"])
        for c in nb["cells"]:
            src = "".join(c["source"])
            py = "\n".join(l for l in src.split("\n") if not l.startswith(("!", "%")))
            compile(py, name, "exec")
            assert not [t for t in tokenize.generate_tokens(io.StringIO(py).readline) if t.type == tokenize.COMMENT]
        text = "".join("".join(c["source"]) + "\n" for c in nb["cells"])
        assert "drive.mount('/content/drive')" in text and "D = '/content/drive/MyDrive/temporal-ood-ddi'" in text
        assert "torch.cuda.is_available()" in text and "get_device_capability" in text
        assert "assert not failed" in text and "rev3_jobs run" in text and "set -o pipefail" in text
        assert "EXPECTED_TAC_ITEMS_SHA256" in text and "EXPECTED_PROMPT_SHA256" in text
        assert "".join(nb["cells"][-1]["source"]).strip().endswith("drive.flush_and_unmount()")
        for j in jobs:
            assert f'"{j}"' in text


def xml_label(drug, setid, di, other, mentions, interactions, codes=None):
    ms = "".join(f'<Mention id="M{i}" type="Precipitant" span="0 1" str="{s}" code="{c}"/>' for i, (s, c) in enumerate(mentions))
    its = "".join(f'<Interaction id="I{i}" type="Pharmacokinetic interaction" trigger="M0" precipitant="M{i}"/>' for i in interactions)
    return (f'<?xml version="1.0" encoding="utf-8"?><Label drug="{drug}" setid="{setid}"><Text>'
            f'<Section name="DRUG INTERACTIONS SECTION" id="34073-7">{di}</Section>'
            f'<Section name="WARNINGS SECTION" id="43685-7">{other}</Section></Text><Sentences>'
            f'<Sentence id="1" LabelDrug="{drug}" section="34073-7"><SentenceText>{di}</SentenceText>{ms}{its}</Sentence>'
            f'</Sentences><LabelInteractions/></Label>')


def synthetic_set(tmp_path):
    d = tmp_path / "setx"
    d.mkdir()
    specs = [("Alpha", "a1", "Alpha with ketoconazole raises levels. Avoid warfarin.", "general text", [("ketoconazole", "R5Z9X1Q2LP"), ("warfarin", "B1C2D3E4F5"), ("strong cyp inhibitors", "N0000175")], [0, 1, 2]),
             ("Beta", "b1", "Beta interacts with digoxin.", "mentions ketoconazole elsewhere", [("digoxin", "Z9Y8X7W6V5")], [0]),
             ("Gamma", "g1", "Gamma with lithium.", "nothing", [("lithium", "L1L1L1L1L1")], [0]),
             ("Delta", "d1", "Delta with phenytoin.", "nothing", [("phenytoin", "P2P2P2P2P2")], [0]),
             ("Eps", "e1", "Eps with rifampin.", "nothing", [("rifampin", "R3R3R3R3R3")], [0])]
    for drug, sid, di, other, ms, its in specs:
        (d / f"{drug}.xml").write_text(xml_label(drug, sid, di, other, ms, its))
    return d


def test_tac_items_follow_the_rules_and_are_deterministic(tmp_path):
    d = synthetic_set(tmp_path)
    labels = rt.load_set(d)
    items, sections = rt.build_set_items("setx", labels)
    again, _ = rt.build_set_items("setx", rt.load_set(d))
    assert items == again
    assert rt.items_sha256(items) == rt.items_sha256(again)
    pos = [i for i in items if i["gold"]]
    assert {(i["ood_drug"], i["partner"]) for i in pos} >= {("Alpha", "ketoconazole"), ("Alpha", "warfarin"), ("Beta", "digoxin")}
    types = {i["partner"]: i["partner_type"] for i in pos}
    assert types["ketoconazole"] == "substance" and types["strong cyp inhibitors"] == "class"
    neg = [i for i in items if not i["gold"]]
    texts = {x["drug"]: x["all_text"] for x in labels}
    for n in neg:
        assert n["partner"] not in texts[n["ood_drug"]]
        assert (n["ood_drug"], n["partner"]) not in {(p["ood_drug"], p["partner"]) for p in pos}
    assert ("Beta", "ketoconazole") not in {(n["ood_drug"], n["partner"]) for n in neg}
    per_partner = {}
    for n in neg:
        per_partner.setdefault(n["partner"], []).append(n["ood_drug"])
    assert all(len(v) == len(set(v)) for v in per_partner.values())
    assert sections["Alpha"]["text"].startswith("Alpha with ketoconazole")
    assert [i["item_id"] for i in items] == [f"setx-{n:05d}" for n in range(1, len(items) + 1)]


def test_tac_partner_types():
    assert rt.partner_type("R5Z9X1Q2LP") == "substance"
    assert rt.partner_type("N0000175553") == "class"
    for c in ("NONE", "NO MAP", "NOT_DRUG", "", "n0000185503"):
        assert rt.partner_type(c) == "class"


def test_tac_fetch_rejects_a_changed_archive_and_skips_appledouble(tmp_path, monkeypatch):
    d = synthetic_set(tmp_path)
    zpath = tmp_path / "dl" / "test1Files2018.zip"
    zpath.parent.mkdir()
    with zipfile.ZipFile(zpath, "w") as z:
        z.write(d / "Alpha.xml", "x/Alpha.xml")
        z.write(d / "Beta.xml", "__MACOSX/x/._Beta.xml")
    monkeypatch.setattr(rt, "SOURCES", {"test1": {"file": "test1Files2018.zip", "bytes": zpath.stat().st_size + 1, "sha256": "0" * 64}})
    with pytest.raises(RuntimeError):
        rt.fetch(zpath.parent)
    monkeypatch.setattr(rt, "SOURCES", {"test1": {"file": "test1Files2018.zip", "bytes": zpath.stat().st_size, "sha256": rt.sha256_file(zpath)}})
    out = rt.fetch(zpath.parent)
    assert [p.name for p in out["test1"].glob("*.xml")] == ["Alpha.xml"]


def test_job_registry_estimates_and_run_loop(tmp_path, monkeypatch):
    assert [c["name"] for c in rj.registry()] == [rj.JOB] and rj.notebook_jobs() == {"R2c_tac_calibration": [rj.JOB]}
    est = rj.estimates(10540557)
    assert est["high_h"] <= rj.NOTEBOOK_HOURS_CAP and est["low_s"] == round(600 + 10540557 / 13000.0)
    d = synthetic_set(tmp_path)
    items, sections = rt.build_all({"test1": d})
    monkeypatch.setattr(rt, "fetch", lambda *_a, **_k: {"test1": d})
    monkeypatch.setattr(rj, "EXPECTED_TAC_ITEMS_SHA256", rt.items_sha256(items))
    calls = []

    def runner(its, secs, state, tiny, smoke):
        calls.append(len(its))
        return {"items": []}, {"tac_items_sha256": rt.items_sha256(its)}

    out = tmp_path / "out"
    assert rj.run(tmp_path, out, runner=runner) == []
    saved = json.loads((out / "preds" / f"{rj.JOB}.json").read_text())
    assert saved["tac_items_sha256"] == rt.items_sha256(items) and saved["config"]["revision"] == ra.OLMO_REVISION
    assert rj.run(tmp_path, out, runner=runner) == [] and len(calls) == 1

    def boom(*a):
        raise RuntimeError("boom")

    out2 = tmp_path / "out2"
    assert rj.run(tmp_path, out2, runner=boom) == [rj.JOB]
    assert "boom" in (out2 / "preds" / f"{rj.JOB}.failed.txt").read_text()
    monkeypatch.setattr(rj, "EXPECTED_TAC_ITEMS_SHA256", "0" * 64)
    with pytest.raises(RuntimeError):
        rj.run(tmp_path, tmp_path / "out3", runner=runner)


def test_run_adjudicates_each_set_with_the_frozen_pipeline(tmp_path, monkeypatch):
    d = synthetic_set(tmp_path)
    items, sections = rt.build_all({"test1": d})
    seen = []

    def fake(tok, model, its, secs, log=None):
        seen.append((len(its), sorted(secs)))
        out = [{**x, "q_no": 0.2, "q_yes": 0.7, "q_unsure": 0.1, "decision": "yes", "mass": 0.9, "tokens": 10, "n_chunks": 1, "non_answer": False} for x in its]
        return out, [{"q": [0.2, 0.7, 0.1], "mass": 0.9, "tokens": 10}] * len(its), len(its)

    monkeypatch.setattr(ra, "adjudicate", fake)
    ev_, extra = rj.calibration_job(items, sections, {"llm": (None, None)}, None, False)
    assert seen[0][0] == len(items) and len(ev_["items"]) == len(items)
    assert extra["r2b_frozen"]["prompt_sha256"] == ra.EXPECTED_PROMPT_SHA256 and extra["answer"]["non_answers"] == 0


def test_holm_and_substitution_arithmetic():
    adj = ev.holm({"H1": 0.045954, "H4": 0.338661, "H6": 0.101898})
    assert adj["H1"] == pytest.approx(0.137862) and adj["H6"] == pytest.approx(0.203796) and adj["H4"] == pytest.approx(0.338661)
    a = c3.part_a()
    assert a["family_substituted"]["holm"]["H1_original_endpoint"] == pytest.approx(0.137862, abs=1e-6)
    assert a["h1_supported_by_holm"] is False and a["h1_unadjusted_p_below_alpha"] is True


def test_fast_spearman_rows_match_scipy_and_power_has_nominal_size():
    rng = np.random.RandomState(0)
    z = rng.rand(12)
    A = rng.rand(30, 12)
    got = c3.fast_spearman_rows(c3.rankdata(z), A)
    want = [spearmanr(z, a).statistic for a in A]
    assert np.allclose(got, want)
    curve = c3.power_curve(z, 0.5, np.eye(12) * 0.001, 0.0, 4000, 1)
    assert 0.03 < curve[0]["power"] < 0.08
    assert curve[-1]["power"] > 0.95 and all(curve[i]["power"] <= curve[i + 1]["power"] + 0.03 for i in range(len(curve) - 1))
    s = c3.power_summary(curve, 0.5)
    assert s["reached_on_grid"] and s["smallest_beta_power_at_least_0.80"] is not None


def test_one_way_draws_hold_partners_fixed_and_two_way_vary_them():
    y = np.array([1, 0, 1, 0, 1, 0, 1, 0])
    g = np.array(["a", "a", "b", "b", "c", "c", "d", "d"])
    q = np.array(["p", "q", "r", "s", "p", "q", "r", "s"])
    from ddiood import amend7_panel as pn
    st_ = pn.pair_structure(y, g, q)
    W = np.stack([pn.win_values(np.random.RandomState(i).rand(8), st_) for i in range(3)])
    one = c3.draws_matrix(W, st_, 200, 5, True)
    two = c3.draws_matrix(W, st_, 200, 5, False)
    assert one.shape == two.shape == (200, 3)
    assert np.var(one, axis=0).sum() != np.var(two, axis=0).sum()
    assert ((one >= 0) & (one <= 1)).all()


def test_c1_pair_stats_hand_values_and_units():
    x = np.array([1, 1, 0, 0, 1, 0, 0, 0], bool)
    y = np.array([1, 0, 0, 0, 1, 1, 0, 0], bool)
    r = c1.pair_stats(x, y, np.ones((1, 8)))
    assert r["agreement"][0] == pytest.approx(3 / 4)
    pe = (3 * 3 + 5 * 5) / 64
    assert r["kappa"][0] == pytest.approx((3 / 4 - pe) / (1 - pe))
    assert r["auroc_first_for_second"][0] == pytest.approx(0.5 * (1 + 2 / 3 - 1 / 5))
    assert r["auroc_second_for_first"][0] == pytest.approx(0.5 * (1 + 2 / 3 - 1 / 5))
    w = c1.bootstrap_weights(range(4), np.array([0, 0, 1, 2, 3, 3]), 5, 1)
    assert w.shape == (5, 6) and (w[:, 0] == w[:, 1]).all() and (w[:, 4] == w[:, 5]).all()
    sel = [({"a": "x", "b": "y", "pos": p, "source": "s", "sentence_id": f"s{i}"},
            {"fda_s1": "positive", "fda_s2": "positive", "fda": "positive", "db": 1, "db_state": "positive", "db_resolved_both": True,
             "self": False, "same_rxcui": False}) for i, p in enumerate([1, 0, 0, 1])]
    u = c1.units(sel, "primary")[0]
    assert (u["n"], u["npos"], u["any"], u["maj"], u["half"]) == (4, 2, 1, 0, 1)


class StubStore:
    def __init__(self, labels):
        self.labels = labels

    def get(self, name, fields=None):
        return self.labels.get(name)


def stub_lookup(names):
    return {n: {"normalized": n, "canonicalized": n, "rxcui": str(i), "matched_form": "normalized"} for i, n in enumerate(names)}


def label(name, di, other=""):
    return {"openfda": {"substance_name": [name]}, "drug_interactions": [di], "warnings": [other]}


def test_pair_state_positive_negative_and_undecided():
    names = ["warfarin", "ketoconazole", "digoxin", "lithium", "phenytoin"]
    labels = {"warfarin": label("warfarin", "Coadministration with ketoconazole increases AUC of warfarin. Avoid digoxin."),
              "ketoconazole": label("ketoconazole", "Coadministration with warfarin is common."),
              "digoxin": label("digoxin", "Digoxin interacts with many agents. Avoid concomitant use of agents.", "lithium is discussed here"),
              "lithium": label("lithium", "Lithium is renally cleared. Concomitant diuretics may raise levels."),
              "phenytoin": label("phenytoin", "No interacting drugs are listed. Avoid alcohol.")}
    lk = stub_lookup(names)
    L = PairLabeler(lk, {n: True for n in names}, StubStore(labels))
    assert L.pair_state("warfarin", "ketoconazole")[0] == POSITIVE
    assert L.pair_state("ketoconazole", "warfarin")[0] == POSITIVE
    assert L.pair_state("warfarin", "digoxin")[0] == POSITIVE
    assert L.pair_state("warfarin", "phenytoin")[0] == NEGATIVE
    assert L.pair_state("digoxin", "lithium")[0] == UNDECIDED
    assert L.pair_state("phenytoin", "lithium")[0] == UNDECIDED
    assert L.pair_state("warfarin", "phenytoin", require_info=False)[0] == NEGATIVE
    assert L.pair_state("phenytoin", "digoxin", require_info=False)[0] in (NEGATIVE, UNDECIDED)
    L.excluded = {"phenytoin"}
    assert L.pair_state("warfarin", "phenytoin")[0] == UNDECIDED
    assert L.pair_state("warfarin", "ketoconazole", ood_blocked=lambda a, b: True)[0] == UNDECIDED
    assert L.has_di("warfarin")


def test_lodo_partner_rate_removes_the_held_out_drug_in_both_roles():
    rows = [{"drug_a": "A", "drug_b": "p", "y": 1}, {"drug_a": "B", "drug_b": "p", "y": 0}, {"drug_a": "C", "drug_b": "p", "y": 0},
            {"drug_a": "p", "drug_b": "q", "y": 1}, {"drug_a": "A", "drug_b": "q", "y": 1}]
    s = c2.lodo_scores(rows, list(range(5)))
    assert s[0] == pytest.approx(c2.smoothed(0, 2))
    assert s[1] == pytest.approx(c2.smoothed(1, 1))
    assert s[4] == pytest.approx(c2.smoothed(1, 0))
    plain = c2.plain_scores(rows, list(range(5)))
    assert plain[0] == pytest.approx(c2.smoothed(1, 2))


def test_clopper_pearson_and_se_sp_counts():
    assert st.cp(0, 10)[0] == 0.0 and st.cp(10, 10)[1] == 1.0
    lo, hi = st.cp(5, 10)
    assert lo == pytest.approx(0.187086, abs=1e-5) and hi == pytest.approx(0.812914, abs=1e-5)
    items = []
    for i in range(40):
        items.append({"set": "test1", "ood_drug": f"L{i % 5}", "gold": 1, "decision": "yes" if i % 4 else "no", "non_answer": False, "partner_type": "substance",
                      "tokens": 100 + i, "n_chunks": 1})
    for i in range(60):
        items.append({"set": "test1", "ood_drug": f"L{i % 5}", "gold": 0, "decision": "no" if i % 5 else ("unsure" if i % 2 else "yes"), "non_answer": False,
                      "partner_type": "substance", "tokens": 100 + i, "n_chunks": 1})
    r, _ = st.se_sp(items, "unsure_not_yes")
    assert (r["tp"], r["fn"]) == (30, 10) and r["sensitivity"] == pytest.approx(0.75)
    assert r["tn"] + r["fp"] == 60 and r["fp"] == 6
    r2, _ = st.se_sp(items, "unsure_excluded")
    assert r2["tn"] + r2["fp"] == 54 and r2["fp"] == 6
    r3, _ = st.se_sp(items, "unsure_as_yes")
    assert r3["fp"] == 12
    assert r["sensitivity_label_cluster95"][0] <= 0.75 <= r["sensitivity_label_cluster95"][1]


def test_rogan_gladen_recovers_a_known_error_rate():
    se, sp, true_err = 0.8, 0.9, 0.2
    q1 = se * (1 - true_err) + (1 - sp) * true_err
    n = 1000
    k = round(q1 * n)
    items = [{"set": "random", "cohort": "older", "current_label": 1, "decision": "yes" if i < k else "no", "non_answer": False} for i in range(n)]
    cal = {"s": {"unsure_not_yes": {"sensitivity": se, "specificity": sp}}}
    draws = {("s", "unsure_not_yes"): (np.full(50, se), np.full(50, sp))}
    out = st.rogan_gladen(items, draws, cal, "unsure_not_yes", "s")
    row = out["rows"][0]
    assert row["corrected_error_rate"] == pytest.approx(true_err, abs=0.01)
    assert row["corrected_error_ci95"][0] <= row["corrected_error_rate"] <= row["corrected_error_ci95"][1]
    q0 = se * 0.1 + (1 - sp) * 0.9
    k0 = round(q0 * n)
    items0 = [{"set": "random", "cohort": "novel", "current_label": 0, "decision": "yes" if i < k0 else "no", "non_answer": False} for i in range(n)]
    row0 = st.rogan_gladen(items0, draws, cal, "unsure_not_yes", "s")["rows"][0]
    assert row0["corrected_error_rate"] == pytest.approx(0.1, abs=0.01)


def test_committed_aggregates_hold_no_drug_names():
    lookup_path = ROOT / "artifacts" / "vocab" / "drug_lookup.json"
    files = sorted((ROOT / "results" / "revision" / "rev3").glob("c[12]_*.json"))
    if not lookup_path.exists() or not files:
        pytest.skip("no artifacts")
    names = {k for k in json.loads(lookup_path.read_text()) if len(k) >= 5}

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
    for f in files:
        strings = set(walk(json.loads(f.read_text())))
        assert not [s for s in strings if s.lower() in names], f


def test_plan_hash_is_recorded_in_outputs():
    import hashlib
    import rev3_common as rc
    plan = "docs/POSTHOC_REV3_PLAN.md"
    commits = subprocess.run(["git", "log", "--format=%H", "--", plan], cwd=ROOT, capture_output=True, text=True).stdout.split()
    data = (ROOT / plan).read_bytes()
    known = {rc.plan_sha256()} | {hashlib.sha256(data[:m.start() + 1]).hexdigest() for m in re.finditer(rb"\n\n## Addendum ", data)}
    for c in commits:
        blob = subprocess.run(["git", "show", f"{c}:{plan}"], cwd=ROOT, capture_output=True, check=True).stdout
        known.add(hashlib.sha256(blob).hexdigest())
    for f in (ROOT / "results" / "revision" / "rev3").glob("*.json"):
        assert json.loads(f.read_text())["plan_sha256"] in known, f
