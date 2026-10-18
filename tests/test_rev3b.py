import ast
import hashlib
import io
import json
import shutil
import sys
import tokenize
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from ddiood import rev3b_jobs as rj
import rev3_common as rc
import rev3_d6 as d6
import rev3b_make_notebooks as mk

FILES = ["ddiood/rev3b_jobs.py", "scripts/rev3b_make_notebooks.py", "scripts/rev3b_build_bundle.sh", "scripts/rev3b_smoke.py", "scripts/rev3_d6.py",
         "tests/test_rev3b.py", "colab/experiments/R3b_marker_sentence.ipynb"]


class FakeInputs:
    def __init__(self):
        sent = "Alpha raises beta levels. Alpha and beta are cleared. gamma is unrelated."
        self.test = [{"pair_id": "p1", "sentence_id": "s1", "sentence": sent, "drug_a": "alpha", "drug_b": "beta", "label_id": 1, "spans": ((0, 5), (13, 17))},
                     {"pair_id": "p2", "sentence_id": "s1", "sentence": sent, "drug_a": "alpha", "drug_b": "gamma", "label_id": 0, "spans": None},
                     {"pair_id": "p3", "sentence_id": "s2", "sentence": "nothing here", "drug_a": "alpha", "drug_b": "beta", "label_id": 0, "spans": None}]
        self.swaps = {k: [{**r, "drug_a": "zeta", "drug_b": "eta", "sentence": r["sentence"].replace("Alpha", "zeta").replace("beta", "eta"), "spans": None}
                          for r in self.test] for k in rj.SWAP_KINDS}


def test_registry_names_seeds_and_notebook_coverage():
    reg = rj.registry()
    assert [c["name"] for c in reg] == [f"r3b-marker-sentence-s{s}" for s in (42, 1, 2, 3, 4)]
    assert {c["weights_name"] for c in reg} == {f"r2-marker-biomedbert-s{s}" for s in (42, 1, 2, 3, 4)}
    nb = rj.notebook_jobs()
    assert list(nb) == ["R3b_marker_sentence"] and nb["R3b_marker_sentence"] == [c["name"] for c in reg]


def test_inputs_follow_the_marker_format_and_the_existing_masking():
    inp = FakeInputs()
    texts, fallback = rj.build_inputs(inp)
    assert set(texts) == set(rj.INPUT_KEYS)
    assert texts["sentence"][0] == "<e1>Alpha</e1> raises <e2>beta</e2> levels. Alpha and beta are cleared. gamma is unrelated."
    assert texts["masked"][0] == "<e1>@DRUG$</e1> raises <e2>@DRUG$</e2> levels. @DRUG$ and @DRUG$ are cleared. gamma is unrelated."
    assert texts["names"][0] == "<e1>alpha</e1> and <e2>beta</e2>."
    assert texts["sentence"][2].startswith("<e1>alpha</e1> and <e2>beta</e2>. nothing here")
    assert fallback["sentence"] == 1 and fallback["names"] == 0
    assert all(len(v) == 3 for v in texts.values())
    assert texts["swap_novel"][0].startswith("<e1>zeta</e1>") or "<e1>zeta" in texts["swap_novel"][0]


def test_inputs_hash_changes_with_any_text():
    inp = FakeInputs()
    t, _ = rj.build_inputs(inp)
    h = rj.inputs_sha256(t)
    t2 = {k: list(v) for k, v in t.items()}
    t2["names"][0] += " "
    assert rj.inputs_sha256(t2) != h and rj.inputs_sha256(t) == h


def test_frozen_files_match_and_a_change_is_detected(tmp_path):
    rj.assert_frozen()
    for f in rj.FROZEN_FILE_SHA256:
        shutil.copy(ROOT / "ddiood" / f, tmp_path / f)
    rj.assert_frozen(tmp_path)
    (tmp_path / "inputs.py").write_text((tmp_path / "inputs.py").read_text() + "\nX = 1\n")
    with pytest.raises(RuntimeError, match="inputs.py"):
        rj.assert_frozen(tmp_path)


def test_reproduction_check_passes_and_fails():
    ev = {"sentence": {"p": [0.1, 0.9]}, "names": {"p": [0.2, 0.3]}}
    stored = {"eval": {"test_sentence": {"p": [0.1, 0.9005]}, "test_empty": {"p": [0.2, 0.3]}}}
    out = rj.reproduction_checks(ev, stored, 2)
    assert out["sentence_vs_test_sentence_max_abs_gap"] == pytest.approx(0.0005)
    stored["eval"]["test_empty"]["p"] = [0.2, 0.4]
    with pytest.raises(RuntimeError, match="names"):
        rj.reproduction_checks(ev, stored, 2)
    with pytest.raises(RuntimeError, match="missing"):
        rj.reproduction_checks(ev, None, 2)


def fake_runner(inp, cfg, state, weights_dir, stored_dir, smoke, tiny):
    if cfg["seed"] == 3:
        raise ValueError("boom")
    return {"sentence": {"preds": [0], "p": [0.5]}}, {"n_rows": 1}


def test_run_writes_atomically_skips_finished_and_records_failures(tmp_path):
    out = tmp_path / "runs"
    failed = rj.run(tmp_path, out, tmp_path / "w", smoke=True, runner=fake_runner, inp=FakeInputs())
    assert failed == ["r3b-marker-sentence-s3"]
    preds = out / "preds"
    assert (preds / "r3b-marker-sentence-s3.failed.txt").read_text().strip().endswith("ValueError: boom")
    good = json.loads((preds / "r3b-marker-sentence-s42.json").read_text())
    assert good["smoke"] is True and good["code_version"] == rj.code_version() and good["config"]["family"] == "marker"
    assert not list(preds.glob("*.tmp"))
    before = (preds / "r3b-marker-sentence-s42.json").read_text()
    rj.run(tmp_path, out, tmp_path / "w", smoke=True, runner=fake_runner, inp=FakeInputs())
    assert (preds / "r3b-marker-sentence-s42.json").read_text() == before
    d = json.loads(before)
    d["config_hash"] = "x"
    (preds / "r3b-marker-sentence-s42.json").write_text(json.dumps(d))
    with pytest.raises(RuntimeError, match="different config"):
        rj.run(tmp_path, out, tmp_path / "w", only=["r3b-marker-sentence-s42"], smoke=True, runner=fake_runner, inp=FakeInputs())


def test_preflight_requires_weights_and_a_gpu(tmp_path):
    with pytest.raises(RuntimeError):
        rj.preflight(rj.registry(), tmp_path / "w", smoke=False)
    with pytest.raises(RuntimeError, match="free"):
        rj.preflight(rj.registry(), tmp_path / "w2", smoke=True, min_free=10 ** 18)


def test_estimates_cover_every_job():
    e = rj.estimates()
    assert set(e["jobs"]) == {c["name"] for c in rj.registry()}
    nb = e["notebooks"]["R3b_marker_sentence"]
    assert nb["jobs"] == 5 and 0 < nb["low_h"] < nb["high_h"] < rj.NOTEBOOK_HOURS_CAP


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
        assert "torch.cuda.is_available()" in text
        assert text.index("torch.cuda.is_available()") < text.index("drive.mount")
        assert "assert_frozen()" in text and "EXPECTED_INPUTS_SHA256" in text and "weight_sha256" in text
        assert "assert not failed" in text and "rev3b_jobs run" in text and "set -o pipefail" in text
        assert "".join(nb["cells"][-1]["source"]).strip().endswith("drive.flush_and_unmount()")
        assert text.count("flush_and_unmount") == 1
        for j in jobs:
            assert f'"{j}"' in text


def synthetic_files(n=80, seeds=(42, 1, 2), noise=0.3):
    rng = np.random.RandomState(0)
    gold5 = rng.choice([0, 1, 2, 3, 4], n, p=[0.6, 0.1, 0.1, 0.1, 0.1])
    y = (gold5 > 0).astype(int)
    sid = np.array([f"s{i // 2}" for i in range(n)])
    files = []
    for s in seeds:
        r = np.random.RandomState(s)
        ev = {}
        for k in rj.INPUT_KEYS:
            p = np.clip(y * 0.6 + 0.2 + r.normal(0, noise, n), 0.001, 0.999)
            preds = np.where(p > 0.5, gold5.clip(1, 4), 0)
            ev[k] = {"preds": preds.tolist(), "p": p.round(6).tolist()}
        files.append({"config": {"seed": s}, "eval": ev, "reproduction": {}})
    return y, gold5, sid, files


def test_scorer_values_by_hand():
    y = np.array([1, 0, 1, 0])
    assert d6.binary_f1(y, [1, 0, 0, 0]) == pytest.approx(2 / 3)
    assert d6.binary_f1([0, 0], [0, 0]) == 0.0
    ev = {k: {"preds": [4, 0, 4, 0], "p": [0.9, 0.1, 0.8, 0.2]} for k in rj.INPUT_KEYS}
    ev["swap_vocab"] = {"preds": [4, 4, 0, 0], "p": [0.9, 0.9, 0.1, 0.2]}
    m = d6.seed_metrics(y, ev)
    assert m["sentence"]["auroc"] == 1.0 and m["sentence"]["binary_f1"] == 1.0
    assert m["swap_vocab"]["flip_rate"] == 0.5 and m["swap_vocab"]["mean_abs_dp"] == pytest.approx((0 + 0.8 + 0.7 + 0) / 4)
    assert m["swap_novel"]["flip_rate"] == 0.0


def test_scorer_summarize_is_deterministic_and_paired():
    y, gold5, sid, files = synthetic_files()
    a = d6.summarize(y, gold5, sid, 3, files, 50)
    b = d6.summarize(y, gold5, sid, 3, files, 50)
    assert a == b
    assert a["complete"] is False and a["seeds"] == [42, 1, 2]
    v = a["seed_mean"]
    for k in rj.INPUT_KEYS:
        per = [a["per_seed"][str(s)][k]["auroc"] for s in a["seeds"]]
        assert v[f"{k}.auroc"]["value"] == pytest.approx(np.mean(per))
        lo, hi = v[f"{k}.auroc"]["ci95"]
        assert lo <= hi and v[f"{k}.auroc"]["n_draws"] == 50
    diff = v["names.auroc_minus_sentence"]["value"]
    assert diff == pytest.approx(v["names.auroc"]["value"] - v["sentence.auroc"]["value"])
    assert len(a["micro_f1_sentence"]) == 3 and a["micro_f1_sentence"][0]["seed"] == 42


def test_scorer_markdown_and_writer(tmp_path, monkeypatch):
    y, gold5, sid, files = synthetic_files(seeds=tuple(rj.SEEDS))
    o = d6.summarize(y, gold5, sid, 3, files, 20)
    o.update({"n_pairs": len(y), "n_positive": int(y.sum()), "n_boot": 20, "fallback": {k: 0 for k in rj.INPUT_KEYS}, "reproduction": [],
              "inputs_sha256": "x", "weights_sha256": {}})
    text = d6.md(o)
    assert "D6" in text and "swap_pseudo" in text and "Five-class micro F1" in text
    monkeypatch.setattr(rc, "OUT", tmp_path)
    rc.write("d6_marker_sentence", o, text)
    obj = json.loads((tmp_path / "d6_marker_sentence.json").read_text())
    assert obj["plan_sha256"] == hashlib.sha256((ROOT / "docs" / "POSTHOC_REV3_PLAN.md").read_bytes()).hexdigest()
    assert obj["status"] == rc.STATUS


def test_reproduction_report_flags_missing_and_gaps():
    f = {"config": {"seed": 42}, "eval": {"sentence": {"p": [0.1, 0.2], "preds": [0, 0]}}, "reproduction": {"x": 1}}
    st = {"eval": {"test_sentence": {"p": [0.1, 0.2002], "preds": [0, 0]}}}
    out = d6.reproduction([f, f], [st, None])
    assert out[0]["max_abs_gap_sentence"] == pytest.approx(0.0002) and out[0]["preds_identical"] is True
    assert out[1] == {"seed": 42, "stored": False}


def test_new_files_have_no_dashes_no_comments_no_forbidden_string():
    for f in FILES:
        txt = (ROOT / f).read_text()
        assert chr(0x2013) not in txt and chr(0x2014) not in txt, f
        assert "cla" + "ude" not in txt.lower(), f
        if f.endswith(".py"):
            assert not [t for t in tokenize.generate_tokens(io.StringIO(txt).readline) if t.type == tokenize.COMMENT], f
            tree = ast.parse(txt)
            assert not [n for n in ast.walk(tree) if isinstance(n, (ast.Module, ast.FunctionDef, ast.ClassDef)) and ast.get_docstring(n)], f
