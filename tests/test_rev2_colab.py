import ast
import io
import json
import re
import sys
import tokenize
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from ddiood import amend7_analysis as aa
from ddiood import rev2_adjudicator as ra
from ddiood import rev2_encoders as re_
from ddiood import rev2_jobs as rj
import rev2_analyze_a as an
import rev2_make_notebooks as mk
import rev2_score_adjudicator as sc

NEW = ["ddiood/rev2_adjudicator.py", "ddiood/rev2_data.py", "ddiood/rev2_encoders.py", "ddiood/rev2_jobs.py",
       "scripts/rev2_analyze_a.py", "scripts/rev2_make_notebooks.py", "scripts/rev2_score_adjudicator.py",
       "scripts/rev2_estimate.py", "scripts/rev2_smoke.py", "scripts/rev2_build_bundle.sh", "tests/test_rev2_colab.py",
       "docs/POSTHOC_REV2_PLAN.md", "colab/experiments/R2a_b2mixed.ipynb", "colab/experiments/R2a_sentence_marker.ipynb",
       "colab/experiments/R2b_adjudicator.ipynb"]


class FakeTok:
    pad_token_id = 0
    eos_token_id = 0

    def __init__(self):
        self.vocab = {"no": 2, "yes": 3, "unsure": 4, "No": 5, "Yes": 6, "Unsure": 7}

    def _ids(self, text):
        return [self.vocab.setdefault(w, len(self.vocab) + 10) for w in text.split()]

    def __call__(self, text, add_special_tokens=False):
        return {"input_ids": self._ids(text)}

    def apply_chat_template(self, messages, tokenize=False, add_generation_prompt=True):
        return messages[0]["content"] + " ASSISTANT"

    def decode(self, ids):
        inv = {v: k for k, v in self.vocab.items()}
        return " ".join(inv[i] for i in ids)


class FakeModel:
    def __init__(self, tok, vocab_size=4096):
        import torch
        self.tok, self.vocab_size = tok, vocab_size
        self.p = torch.nn.Parameter(torch.zeros(1))

    def parameters(self):
        yield self.p

    def __call__(self, input_ids, attention_mask=None, position_ids=None, logits_to_keep=None, use_cache=False):
        import torch
        hit = self.tok.vocab["KEYWORD"]
        n = input_ids.shape[0]
        logits = torch.zeros(n, 1, self.vocab_size)
        has = (input_ids == hit).any(dim=1)
        logits[:, 0, self.tok.vocab["yes"]] = torch.where(has, 5.0, -5.0)
        logits[:, 0, self.tok.vocab["no"]] = torch.where(has, -5.0, 5.0)
        return type("Out", (), {"logits": logits})()


def test_prompt_matches_the_plan_and_has_only_three_fields():
    plan = (ROOT / "docs" / "POSTHOC_REV2_PLAN.md").read_text()
    block = plan.split("<!-- PROMPT-BEGIN -->")[1].split("<!-- PROMPT-END -->")[0]
    body = block.strip().removeprefix("```").removesuffix("```").strip("\n")
    assert body == ra.PROMPT
    assert set(re.findall(r"\{(\w+)\}", ra.PROMPT)) == {"drug", "section", "partner"}
    text = ra.build_prompt("tizanidine", "SECTION TEXT", "propafenone")
    assert "SECTION TEXT" in text and "propafenone" in text and "evidence" not in text.lower()


def test_model_facts_are_pinned():
    assert ra.OLMO == "allenai/OLMo-2-1124-7B-Instruct"
    assert re.fullmatch(r"[0-9a-f]{40}", ra.OLMO_REVISION)
    assert ra.OLMO_LICENSE == "apache-2.0"
    assert "qwen" not in ra.OLMO.lower()


def test_registry_names_and_notebook_coverage():
    reg = rj.registry()
    names = [j["name"] for j in reg]
    assert len(names) == len(set(names)) == 16
    assert all(n.startswith("r2-") for n in names)
    seeds = {j["seed"] for j in reg if j["kind"] == "r2a"}
    assert seeds == {42, 1, 2, 3, 4}
    nb = rj.notebook_jobs()
    assert sorted(x for v in nb.values() for x in v) == sorted(names)
    assert len(nb["R2a_b2mixed"]) == 5 and len(nb["R2a_sentence_marker"]) == 10 and nb["R2b_adjudicator"] == ["r2-olmo-adjudication"]


def test_estimates_stay_under_two_hours_from_stored_seconds():
    est = rj.estimates(r2b_tokens=391062)
    assert all(v["high_h"] <= rj.NOTEBOOK_HOURS_CAP for v in est["notebooks"].values()), est["notebooks"]
    assert est["jobs"]["r2-b2mixed-biomedbert-s1"]["stored_s"] == pytest.approx(460.8)
    assert est["jobs"]["r2-marker-biomedbert-s1"]["stored_s"] == pytest.approx(249.6)
    none = rj.estimates()
    assert none["notebooks"]["R2b_adjudicator"]["high_h"] is None


def test_notebooks_are_code_only_parse_and_match_the_generator():
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
        assert "D = '/content/drive/MyDrive/temporal-ood-ddi'" in text
        assert "set -o pipefail" in text and "/content/w" in text and "assert not failed" in text
        assert "rev2_jobs run" in text and "r2-" in text
        for j in jobs:
            assert f'"{j}"' in text


def test_new_files_have_no_dashes_no_comments_no_forbidden_string():
    for f in NEW:
        txt = (ROOT / f).read_text()
        assert chr(0x2013) not in txt and chr(0x2014) not in txt, f
        assert "cla" + "ude" not in txt.lower(), f
        if f.endswith(".py"):
            assert not [t for t in tokenize.generate_tokens(io.StringIO(txt).readline) if t.type == tokenize.COMMENT], f
            tree = ast.parse(txt)
            assert not [n for n in ast.walk(tree) if isinstance(n, (ast.Module, ast.FunctionDef, ast.ClassDef))
                        and ast.get_docstring(n)], f


def rows(prefix, n_drugs, per, pos_every):
    out = []
    for g in range(n_drugs):
        for i in range(per):
            out.append({"drug_a": f"{prefix}{g}", "drug_b": f"p{i}", "y": int(i % pos_every == 0), "group": f"{prefix}{g}"})
    return out


def test_random_items_are_stratified_seeded_and_exclude_older_artifacts():
    novel = rows("n", 30, 40, 3)
    older = rows("o", 40, 60, 3) + rows("artifact", 5, 60, 3)
    a = ra.random_items(novel, older, {"artifact0", "artifact1", "artifact2", "artifact3", "artifact4"})
    b = ra.random_items(novel, older, {"artifact0", "artifact1", "artifact2", "artifact3", "artifact4"})
    assert a == b and len(a) == 250
    assert [x["item_id"] for x in a] == [f"S{i:03d}" for i in range(1, 251)]
    counts = {(c, y): sum(1 for x in a if x["cohort"] == c and x["current_label"] == y) for c in ("older", "novel") for y in (0, 1)}
    assert counts == {("older", 1): 75, ("older", 0): 75, ("novel", 1): 50, ("novel", 0): 50}
    assert not any(x["ood_drug"].startswith("artifact") for x in a)
    assert len({(x["ood_drug"], x["partner"]) for x in a}) == 250
    other = ra.random_items(novel, older, set(), seed=18)
    assert [x["partner"] for x in other] != [x["partner"] for x in a] or [x["ood_drug"] for x in other] != [x["ood_drug"] for x in a]


def test_random_items_fail_when_a_class_is_too_small():
    with pytest.raises(ValueError):
        ra.random_items(rows("n", 2, 5, 3), rows("o", 40, 60, 3), set())


@pytest.mark.skipif(not (ROOT / "artifacts" / "bundle" / "inputs.json.gz").exists(), reason="local artifacts absent")
def test_real_items_have_sections_and_expected_sizes():
    import rev2_estimate as est
    items, sections = est.items_and_sections(ROOT / "artifacts" / "bundle" / "inputs.json.gz")
    assert len(items) == 505
    assert sum(x["set"] == "audit" for x in items) == 255 and sum(x["set"] == "random" for x in items) == 250
    assert all(x["ood_drug"] in sections for x in items)
    older = [x for x in items if x["set"] == "random" and x["cohort"] == "older"]
    primary = json.loads((ROOT / "artifacts" / "amend7" / "primary_sets.json").read_text())
    bad = set(primary["older_artifacts"]) | set(primary["older_missed_vocabulary_drugs"])
    assert len(older) == 150 and not {x["ood_drug"] for x in older} & bad


def test_fit_chunks_keeps_short_sections_whole_and_splits_long_ones_in_order():
    tok = FakeTok()
    short = "One. Two."
    assert ra.fit_chunks(tok, "d", short, "p", limit=500) == [short]
    sentences = [f"Sentence {i} has several words in it." for i in range(60)]
    long = " ".join(sentences)
    chunks = ra.fit_chunks(tok, "d", long, "p", limit=200)
    assert len(chunks) > 1
    assert " ".join(chunks) == long
    for c in chunks:
        assert ra.n_tokens(tok, ra.pr.chat(tok, ra.build_prompt("d", c, "p"))) <= 200


def test_fit_chunks_cuts_a_single_oversized_sentence():
    tok = FakeTok()
    giant = " ".join(f"w{i}" for i in range(900)) + "."
    chunks = ra.fit_chunks(tok, "d", giant, "p", limit=300)
    assert len(chunks) > 2
    for c in chunks:
        assert ra.n_tokens(tok, ra.pr.chat(tok, ra.build_prompt("d", c, "p"))) <= 300


def test_label_ids_use_first_tokens_and_reject_collisions():
    tok = FakeTok()
    ids = ra.label_ids(tok)
    assert ids[0] == [2, 5] and ids[1] == [3, 6] and ids[2] == [4, 7]

    class Clash(FakeTok):
        def __call__(self, text, add_special_tokens=False):
            return {"input_ids": [9, 1]}

    with pytest.raises(RuntimeError):
        ra.label_ids(Clash())


def test_adjudicate_takes_the_chunk_with_the_highest_yes_and_deduplicates_prompts():
    tok = FakeTok()
    tok.vocab["KEYWORD"] = 99
    model = FakeModel(tok)
    filler = " ".join(f"Filler sentence number {i} is plain." for i in range(60))
    sections = {"drugA": {"text": filler + " KEYWORD here is the key sentence. " + filler}, "drugB": {"text": "Nothing relevant."}}
    items = [{"item_id": "A001", "set": "audit", "cohort": "older", "ood_drug": "drugA", "partner": "x", "current_label": 1},
             {"item_id": "S001", "set": "random", "cohort": "older", "ood_drug": "drugA", "partner": "x", "current_label": 1},
             {"item_id": "S002", "set": "random", "cohort": "novel", "ood_drug": "drugB", "partner": "y", "current_label": 0}]
    orig = ra.MAX_PROMPT_TOKENS
    ra.fit_chunks.__defaults__ = (400,)
    try:
        out, scores, n_unique = ra.adjudicate(tok, model, items, sections)
    finally:
        ra.fit_chunks.__defaults__ = (orig,)
    assert n_unique == 2
    assert out[0]["decision"] == "yes" and out[1]["decision"] == "yes" and out[2]["decision"] == "no"
    assert out[0]["n_chunks"] > 1 and out[2]["n_chunks"] == 1
    assert out[0]["q_yes"] == out[1]["q_yes"] > 0.9
    assert all(set(o) >= {"q_no", "q_yes", "q_unsure", "decision", "mass", "tokens", "n_chunks", "non_answer"} for o in out)
    assert abs(out[2]["q_no"] + out[2]["q_yes"] + out[2]["q_unsure"] - 1) < 1e-4


def test_adjudicate_rejects_a_missing_section():
    tok = FakeTok()
    tok.vocab["KEYWORD"] = 99
    with pytest.raises(KeyError):
        ra.adjudicate(tok, FakeModel(tok), [{"item_id": "A1", "set": "audit", "cohort": "older", "ood_drug": "zzz", "partner": "x",
                                              "current_label": 1}], {})


def test_run_loop_logs_failures_continues_skips_finished_and_rejects_changed_config(tmp_path):
    class D:
        ood_hash, old_hash = "a", "b"
        manifest = {"train_hash": "c"}

    calls = []

    def runner(cfg, data, state, workdir, weights, te, tl):
        calls.append(cfg["name"])
        if cfg["name"] == "r2-b2mixed-biomedbert-s1":
            raise RuntimeError("boom")
        return {"x": {"p": [0.1], "preds": [0]}}, {}

    only = ["r2-b2mixed-biomedbert-s42", "r2-b2mixed-biomedbert-s1", "r2-b2mixed-biomedbert-s2"]
    failed = rj.run(tmp_path, tmp_path / "runs", tmp_path / "w", only=only, runner=runner, data=D())
    assert failed == ["r2-b2mixed-biomedbert-s1"]
    preds = tmp_path / "runs" / "preds"
    assert (preds / "r2-b2mixed-biomedbert-s1.failed.txt").read_text().strip().endswith("boom")
    assert (preds / "r2-b2mixed-biomedbert-s2.json").exists() and not (preds / "r2-b2mixed-biomedbert-s1.json").exists()
    calls.clear()
    rj.run(tmp_path, tmp_path / "runs", tmp_path / "w", only=only, runner=lambda *a: ({"x": {}}, {}), data=D())
    assert not (preds / "r2-b2mixed-biomedbert-s1.failed.txt").exists()
    assert (preds / "r2-b2mixed-biomedbert-s1.json").exists()
    assert not list(preds.glob("*.tmp"))
    assert rj.run(tmp_path, tmp_path / "runs", tmp_path / "w", only=only, runner=runner, data=D()) == []
    assert calls == []
    f = preds / "r2-b2mixed-biomedbert-s42.json"
    d = json.loads(f.read_text())
    d["config_hash"] = "other"
    f.write_text(json.dumps(d))
    with pytest.raises(RuntimeError):
        rj.run(tmp_path, tmp_path / "runs", tmp_path / "w", only=only, runner=runner, data=D())


def test_save_weights_replaces_atomically(tmp_path):
    src = tmp_path / "src"
    src.mkdir()
    (src / "model.safetensors").write_bytes(b"one")
    dest = tmp_path / "weights" / "job"
    re_.save_weights(src, dest)
    (src / "model.safetensors").write_bytes(b"two")
    re_.save_weights(src, dest)
    assert (dest / "model.safetensors").read_bytes() == b"two"
    assert [p.name for p in (tmp_path / "weights").iterdir()] == ["job"]
    assert re_.file_sha256(dest / "model.safetensors") == __import__("hashlib").sha256(b"two").hexdigest()


def test_training_inputs_match_the_original_recipes():
    from ddiood import inputs
    tr = [{"drug_a": "a", "drug_b": "b", "sentence": "a with b.", "label_id": 2, "spans": ((0, 1), (7, 8))},
          {"drug_a": "c", "drug_b": "d", "sentence": "c and d.", "label_id": 0}]
    va = [{"drug_a": "e", "drug_b": "f", "sentence": "e plus f.", "label_id": 1}]
    f, y, fv, yv = re_.train_texts("b2mixed", tr, va)
    assert (f, y) == inputs.mixed_training(tr) and len(f) == 4 and fv == inputs.b2_sentence(va) and yv == [1]
    f, y, fv, yv = re_.train_texts("b2sentence", tr, va)
    assert f == inputs.b2_sentence(tr) and y == [2, 0]
    f, y, fv, yv = re_.train_texts("marker", tr, va)
    assert f[0] == "<e1>a</e1> with <e2>b</e2>." and fv == ["<e1>e</e1> plus <e2>f</e2>."] and y == [2, 0]
    with pytest.raises(ValueError):
        re_.train_texts("other", tr, va)


def synthetic_truth(seed=0):
    rng = np.random.RandomState(seed)

    def pairs(prefix, n, per):
        return [{"ood_drug": f"{prefix}{g}", "semeval_drug": f"p{i}", "label": str(int(i % 3 == 0)), "cooccurrence_sentence": "",
                 "evidence": ""} for g in range(n) for i in range(per)]
    return aa.Truth(pairs("nov", 12, 9), pairs("old", 16, 9)), rng


def write_job(dir_, name, ev, seconds=1.0):
    Path(dir_).mkdir(parents=True, exist_ok=True)
    (Path(dir_) / f"{name}.json").write_text(json.dumps({"eval": ev, "seconds": seconds}))


def ev_block(p):
    return {"p": [float(x) for x in p], "preds": [int(x >= 0.5) for x in p]}


def test_analysis_perfect_and_chance_scores_and_exact_reproduction(tmp_path):
    truth, rng = synthetic_truth()
    train = [{"drug_a": f"s{g}", "drug_b": f"p{i}", "y": int(i % 3 == 0)} for g in range(14) for i in range(9)]
    y_train = np.array([r["y"] for r in train], float)
    n_nov, n_old = len(truth.sets["ood"]["y"]), len(truth.sets["oodold"]["y"])
    y_nov, y_old = truth.sets["ood"]["y"].astype(float), truth.sets["oodold"]["y"].astype(float)
    test_y = rng.randint(0, 2, 40)
    for family in re_.FAMILIES:
        for seed in re_.SEEDS:
            ev = {"train_empty": ev_block(0.1 + 0.8 * y_train), "ood_empty": ev_block(rng.rand(n_nov)),
                  "oodold_empty": ev_block(rng.rand(n_old)), "test_sentence": ev_block(0.1 + 0.8 * test_y),
                  "test_empty": ev_block(rng.rand(40))}
            if family != "marker":
                ev["train_names"] = ev_block(0.1 + 0.8 * y_train)
                ev["ood_names"] = ev_block(rng.rand(n_nov))
            write_job(tmp_path / "new", f"r2-{family}-biomedbert-s{seed}", ev)
            if family != "marker":
                stored = {k: v for k, v in ev.items() if not k.startswith("train")}
                write_job(tmp_path / "old", f"{family}-biomedbert-s{seed}", stored)
            elif seed == 42:
                write_job(tmp_path / "a7", an.A7_MARKER, {k: v for k, v in ev.items() if not k.startswith("train")})
    semeval_train = [{"drug_a": "S0", "drug_b": "p0 ", "label_id": 2}, {"drug_a": "p3", "drug_b": "s1", "label_id": 0},
                     {"drug_a": "zzz", "drug_b": "yyy", "label_id": 1}]
    res = an.analyze(tmp_path / "new", tmp_path / "old", truth, train, test_y, n=50, semeval_train=semeval_train,
                     a7_dir=tmp_path / "a7")
    ov = res["seen_overlap_with_semeval_train"]
    assert ov["n_in_semeval_train"] == 2 and ov["n_not_in_semeval_train"] == len(train) - 2
    assert ov["n_in_semeval_train_with_a_positive_instance"] == 1 and ov["n_positive_and_semeval_positive"] == 1
    assert ov["n_drugs_both_anchor_and_partner"] == 0 and ov["n_anchor_drugs"] == 14
    outside = [r for r in res["dissociation"] if r["cohort"] == "seen_not_in_semeval_train" and r["input"] == "names_only"]
    assert len(outside) == 3 and all(r["n_pairs"] == len(train) - 2 for r in outside)
    marker = [r for r in res["reproducibility"] if r["family"] == "marker"]
    assert len(marker) == 1 and marker[0]["stored_name"] == an.A7_MARKER and marker[0]["status"] == "compared"
    assert all(v["spearman"] == pytest.approx(1.0) for v in marker[0]["keys"].values())
    assert set(marker[0]["within_drug_auroc"]) == {"ood_empty/novel", "oodold_empty/older_primary"}
    seen = [r for r in res["dissociation"] if r["cohort"] == "seen" and r["input"].startswith("names_only")]
    assert len(seen) == 3 and all(r["seed_mean"]["value"] == pytest.approx(1.0) and r["complete"] for r in seen)
    nov = [r for r in res["dissociation"] if r["cohort"] == "novel" and r["family"] == "b2mixed" and r["input"].startswith("names_only")][0]
    assert 0.2 < nov["seed_mean"]["value"] < 0.8 and nov["n_positive"] == int(y_nov.sum())
    assert all(r["status"] == "compared" for r in res["reproducibility"])
    for r in res["reproducibility"]:
        assert all(v["spearman"] == pytest.approx(1.0) and v["max_abs_diff"] == 0 for v in r["keys"].values())
        assert all(v["difference"] == 0 for v in r["within_drug_auroc"].values())
        assert r["stored_missing_keys"] == [] and r["retrained_missing_keys"] == [] or "train_empty" in r["stored_missing_keys"]
    assert {r["key"] for r in res["semeval_test"]} == {"test_sentence", "test_empty"}
    md = an.markdown(an.clean(res))
    assert "within-drug AUROC" in md and "Spearman" in md


def test_analysis_reports_a_missing_seed_as_incomplete_and_a_difference(tmp_path):
    truth, rng = synthetic_truth()
    train = [{"drug_a": f"s{g}", "drug_b": f"p{i}", "y": int(i % 3 == 0)} for g in range(14) for i in range(9)]
    n_nov, n_old = len(truth.sets["ood"]["y"]), len(truth.sets["oodold"]["y"])
    base = {"train_empty": ev_block(rng.rand(len(train))), "ood_empty": ev_block(rng.rand(n_nov)), "oodold_empty": ev_block(rng.rand(n_old))}
    write_job(tmp_path / "new", "r2-b2mixed-biomedbert-s42", base)
    shifted = {k: v for k, v in base.items() if k != "train_empty"}
    shifted["ood_empty"] = ev_block(rng.rand(n_nov))
    write_job(tmp_path / "old", "b2mixed-biomedbert-s42", shifted)
    res = an.analyze(tmp_path / "new", tmp_path / "old", truth, train, None, n=20)
    row = [r for r in res["dissociation"] if r["cohort"] == "seen"][0]
    assert row["seeds"] == [42] and row["complete"] is False
    r0 = [r for r in res["reproducibility"] if r["family"] == "b2mixed" and r["seed"] == 42][0]
    assert abs(r0["within_drug_auroc"]["ood_empty/novel"]["difference"]) > 0
    assert r0["keys"]["ood_empty"]["spearman"] < 0.99
    assert [r["status"] for r in res["reproducibility"] if r["seed"] == 1] == ["missing", "missing"]
    assert [r["status"] for r in res["reproducibility"] if r["family"] == "marker"] == ["missing"]
    assert res["seen_overlap_with_semeval_train"] is None
    assert not [r for r in res["dissociation"] if r["cohort"] == "seen_not_in_semeval_train"]
    assert "semeval_test" not in res


def test_clopper_pearson_known_values():
    lo, hi = sc.cp(0, 10)
    assert lo == 0.0 and hi == pytest.approx(1 - 0.025 ** 0.1, abs=1e-6)
    lo, hi = sc.cp(10, 10)
    assert hi == 1.0 and lo == pytest.approx(0.025 ** 0.1, abs=1e-6)
    lo, hi = sc.cp(5, 20)
    assert lo == pytest.approx(0.0866, abs=1e-3) and hi == pytest.approx(0.4910, abs=1e-3)
    assert sc.cp(0, 0) == [None, None]


def fake_adjudication(tmp_path):
    items = []
    spec = [("audit", "older", 1, "no", "positive_oracle_below_0.5", 6), ("audit", "older", 1, "yes", "positive_oracle_below_0.5", 3),
            ("audit", "novel", 0, "yes", "negative_oracle_above_0.5", 2), ("audit", "novel", 0, "no", "negative_oracle_above_0.5", 2),
            ("audit", "older", 1, "unsure", "positive_rule_flag", 1),
            ("random", "older", 1, "yes", "x", 8), ("random", "older", 1, "no", "x", 2), ("random", "novel", 0, "no", "x", 9),
            ("random", "novel", 0, "yes", "x", 1)]
    key, earlier, i = [], [], 0
    for s, cohort, lab, dec, why, n in spec:
        for _ in range(n):
            i += 1
            iid = f"{'A' if s == 'audit' else 'S'}{i:03d}"
            items.append({"item_id": iid, "set": s, "cohort": cohort, "ood_drug": f"d{i}", "partner": "p", "current_label": lab,
                          "q_no": 0.1, "q_yes": 0.8, "q_unsure": 0.1, "decision": dec, "mass": 0.9, "tokens": 10, "n_chunks": 1,
                          "non_answer": False})
            if s == "audit":
                key.append({"item_id": iid, "selected_because": why})
                earlier.append({"item_id": iid, "adjudication": "no" if lab == 1 else "yes"})
    p = tmp_path / "preds.json"
    p.write_text(json.dumps({"eval": {"items": items}, "model": {"repo": ra.OLMO}, "prompt_sha256": "h", "smoke": False}))
    for name, rows_ in (("key.csv", key), ("earlier.csv", earlier)):
        with open(tmp_path / name, "w", newline="") as f:
            import csv
            w = csv.DictWriter(f, fieldnames=list(rows_[0]))
            w.writeheader()
            w.writerows(rows_)
    return p, tmp_path / "earlier.csv", tmp_path / "key.csv"


def test_scorer_counts_rates_and_agreement(tmp_path):
    p, earlier, key = fake_adjudication(tmp_path)
    res = sc.score(p, earlier, key)
    pos = res["audit"]["errors"]["positives_judged_no"]
    assert pos["n"] == 10 and pos["n_wrong"] == 6 and pos["n_unsure"] == 1
    assert pos["primary_decided_only"]["k"] == 6 and pos["primary_decided_only"]["n"] == 9
    assert pos["unsure_as_error"]["k"] == 7 and pos["unsure_as_correct"]["n"] == 10
    neg = res["audit"]["errors"]["negatives_judged_yes"]
    assert neg["n"] == 4 and neg["n_wrong"] == 2
    cur = res["audit"]["agreement_with_current_label"]
    assert cur["decided_only"]["k"] == 3 + 2 and cur["decided_only"]["n"] == 13
    assert res["audit"]["positives_by_selection"]["positive_rule_flag"]["positives_judged_no"]["n_unsure"] == 1
    rnd = res["random"]["errors_by_cohort"]
    assert rnd["older"]["positives_judged_no"]["primary_decided_only"]["k"] == 2
    assert rnd["novel"]["negatives_judged_yes"]["primary_decided_only"]["n"] == 10
    assert res["random"]["errors_unweighted_pool_by_class"]["positives_judged_no"]["n"] == 10
    ag = res["audit"]["agreement_with_earlier_model_adjudication"]["all"]
    assert ag["n"] == 14 and ag["agreement_three_way"]["k"] == 6 + 2 and ag["table_rows_new_cols_earlier"]["no"]["no"] == 6
    assert ag["kappa_both_decided"] is not None
    md = sc.markdown(res)
    assert "Full run." in md and "Agreement with the earlier model adjudication" in md


def test_scorer_rejects_an_invalid_decision(tmp_path):
    p, earlier, key = fake_adjudication(tmp_path)
    d = json.loads(p.read_text())
    d["eval"]["items"][0]["decision"] = "maybe"
    p.write_text(json.dumps(d))
    with pytest.raises(ValueError):
        sc.score(p, earlier, key)


def test_scorer_requires_an_earlier_adjudication_for_every_audit_item(tmp_path):
    p, earlier, key = fake_adjudication(tmp_path)
    lines = earlier.read_text().splitlines()
    earlier.write_text("\n".join(lines[:-1]) + "\n")
    with pytest.raises(ValueError):
        sc.score(p, earlier, key)


TINY_HUB = "hf-internal-testing/tiny-random-bert"


def tiny_available():
    try:
        from transformers import AutoModel, AutoTokenizer
        AutoTokenizer.from_pretrained(TINY_HUB)
        AutoModel.from_pretrained(TINY_HUB)
    except Exception:
        return False
    return (ROOT / "data" / "DDICorpus" / "DDICorpus").exists() and (ROOT / "artifacts" / "bundle" / "inputs.json.gz").exists()


@pytest.fixture(scope="module")
def tiny(tmp_path_factory):
    if not tiny_available():
        pytest.skip("tiny encoder, SemEval corpus or bundle unavailable")
    from transformers import AutoModel, AutoTokenizer
    path = tmp_path_factory.mktemp("tiny")
    AutoModel.from_pretrained(TINY_HUB).save_pretrained(path)
    AutoTokenizer.from_pretrained(TINY_HUB).save_pretrained(path)
    return str(path)


@pytest.fixture(scope="module")
def smoke_inputs(tiny):
    from ddiood import gpu_jobs
    return gpu_jobs.Inputs(ROOT / "artifacts" / "bundle" / "inputs.json.gz", smoke=True)


def test_b2_jobs_reproduce_the_original_bert_job_exactly_on_cpu(smoke_inputs, tiny, tmp_path, monkeypatch):
    from ddiood import gpu_jobs

    class Data:
        smoke = True
        inp = smoke_inputs
        train = [{"drug_a": "a", "drug_b": "b", "y": 0}, {"drug_a": "c", "drug_b": "d", "y": 1}]
        manifest = {"train_hash": "h"}

    monkeypatch.setitem(gpu_jobs.MODELS, "biomedbert", tiny)
    for family in ("b2mixed", "b2sentence"):
        old = gpu_jobs.bert_job(smoke_inputs, {**gpu_jobs.job("bert", family, "biomedbert", 42), "epochs": 1}, tmp_path / f"old-{family}")
        cfg = {"family": family, "seed": 42, "name": f"r2-{family}-biomedbert-s42"}
        new, extra = re_.encoder_job(Data, cfg, tmp_path / f"new-{family}", tmp_path / "weights", tiny=tiny)
        assert set(old) <= set(new)
        for k in old:
            assert np.allclose(new[k]["p"], old[k]["p"], atol=1e-4) and new[k]["preds"] == old[k]["preds"], (family, k)
            if "index" in old[k]:
                assert new[k]["index"] == old[k]["index"]
        assert len(new["train_empty"]["p"]) == 2 and extra["weights"]["reload_max_abs_gap"] <= 1e-4
        assert (tmp_path / "weights" / cfg["name"] / "model.safetensors").exists()


def test_marker_job_reproduces_the_e9_panel_job_exactly_on_cpu(smoke_inputs, tiny, tmp_path):
    from ddiood import amend7_jobs as aj
    from ddiood import amend7_panel as pn

    class Data:
        smoke = True
        inp = smoke_inputs
        train = [{"drug_a": "a", "drug_b": "b", "y": 0}]
        manifest = {"train_hash": "h", "panel_lowercase": {}}
        train_semeval = pn.attach_offsets(smoke_inputs.train, pn.load_offsets("train"))
        test = pn.attach_offsets(smoke_inputs.test, pn.load_offsets("test"))
        ood, ood_old = smoke_inputs.ood, smoke_inputs.ood_old

    old, _ = aj.panel_job(Data, {"tiny": tiny, "variant": "marker", "seed": 42, "epochs": 1, "repo": "x"}, tmp_path / "old")
    cfg = {"family": "marker", "seed": 42, "name": "r2-marker-biomedbert-s42"}
    new, extra = re_.encoder_job(Data, cfg, tmp_path / "new", tmp_path / "weights", tiny=tiny)
    assert set(old) <= set(new)
    for k in old:
        assert np.allclose(new[k]["p"], old[k]["p"], atol=1e-4) and new[k]["preds"] == old[k]["preds"], k


def test_pair_key_is_unordered_lowercase_and_stripped():
    assert an.pair_key("Warfarin ", "ASPIRIN") == an.pair_key("aspirin", " warfarin")
    assert an.pair_key("a", "b") != an.pair_key("a", "c")


@pytest.mark.skipif(not (ROOT / "data" / "DDICorpus" / "DDICorpus").exists()
                    or not (ROOT / "artifacts" / "amend7" / "train_pairs.csv").exists(), reason="local data absent")
def test_real_seen_overlap_counts():
    from ddiood import amend7_data as ad
    from ddiood import semeval
    rows = [ad.Data._train_row(x) for x in ad.read_rows_csv(ROOT / "artifacts" / "amend7" / "train_pairs.csv")]
    ov, outside = an.overlap_summary(rows, an.semeval_pair_index(semeval.load_pairs("train")))
    assert ov["n_pairs"] == 4643 and ov["n_in_semeval_train"] == 581 and ov["n_not_in_semeval_train"] == 4062
    assert ov["n_positive_and_semeval_positive"] == 206 and ov["n_drugs_both_anchor_and_partner"] == 175
    assert int(outside.sum()) == 4062


def test_mount_is_unconditional_and_the_run_is_gated():
    for name, jobs in rj.notebook_jobs().items():
        nb = json.loads((ROOT / "colab" / "experiments" / f"{name}.ipynb").read_text())
        srcs = ["".join(c["source"]) for c in nb["cells"]]
        mount = [x for x in srcs if "drive.mount" in x]
        assert len(mount) == 1
        assert "if " not in mount[0] and "D = '/content'" not in mount[0] and "else" not in mount[0]
        assert "D = '/content/drive/MyDrive/temporal-ood-ddi'" in mount[0]
        assert not [x for x in srcs if "os.path.exists('/content/rev2_bundle.tgz')" in x]
        gpu = [x for x in srcs if "torch.cuda.is_available()" in x]
        assert len(gpu) == 1 and ("get_device_capability(0)[0] >= 8" in gpu[0]) == name.startswith("R2b")
        assert "cp {D}/rev2_bundle.tgz /content/rev2_bundle.tgz" in "\n".join(srcs)
        assert "drive.flush_and_unmount()" in srcs[-1] and "assert not failed" in srcs[-2]
        assert srcs.index(mount[0]) < srcs.index(gpu[0]) + 2


def test_frozen_hashes_match_the_real_items_and_the_prompt():
    assert ra.prompt_sha256() == ra.EXPECTED_PROMPT_SHA256
    if (ROOT / "artifacts" / "bundle" / "inputs.json.gz").exists():
        import rev2_estimate as est
        items, _ = est.items_and_sections(ROOT / "artifacts" / "bundle" / "inputs.json.gz")
        assert ra.items_sha256(items) == ra.EXPECTED_ITEMS_SHA256
        ra.assert_frozen(items)
        with pytest.raises(RuntimeError):
            ra.assert_frozen(items[:-1])
        tampered = [dict(x) for x in items]
        tampered[0]["partner"] = "other"
        with pytest.raises(RuntimeError):
            ra.assert_frozen(tampered)


def test_adjudicator_job_checks_the_frozen_items_before_loading_the_model(tmp_path):
    import csv
    wd = tmp_path / "rev2"
    wd.mkdir()
    sheet = [{"item_id": f"A{i:03d}", "cohort": "older", "ood_drug": "d", "partner": "p", "current_label": "1"} for i in range(255)]
    with open(wd / "label_audit_sheet.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(sheet[0]))
        w.writeheader()
        w.writerows(sheet)
    old = [{"drug_a": f"o{g}", "drug_b": f"p{i}", "y": int(i % 2 == 0)} for g in range(10) for i in range(30)]
    nov = [{"drug_a": f"n{g}", "drug_b": f"p{i}", "y": int(i % 2 == 0)} for g in range(10) for i in range(30)]

    class D:
        workdir = tmp_path
        ood_full, old_full, excluded_older, sections, smoke = nov, old, set(), {}, False

    loaded = []
    orig = ra.load_olmo
    ra.load_olmo = lambda *a, **k: loaded.append(1)
    try:
        with pytest.raises(RuntimeError, match="item list sha256"):
            rj.adjudicator_job(D, {"name": "x"}, {}, None)
    finally:
        ra.load_olmo = orig
    assert loaded == []


def test_preflight_checks_space_gpu_and_cleans_stale_tmp(tmp_path):
    r2a = [{"kind": "r2a"}]
    w = tmp_path / "weights"
    (w / "job.123.tmp").mkdir(parents=True)
    (w / "job.123.tmp" / "x").write_text("x")
    rj.preflight(r2a, w, smoke=True)
    assert not list(w.glob("*.tmp"))
    with pytest.raises(RuntimeError, match="free"):
        rj.preflight(r2a, w, smoke=True, min_free=10 ** 18)
    rj.preflight([{"kind": "r2b"}], w, smoke=True, min_free=10 ** 18)
    import torch
    if not torch.cuda.is_available():
        with pytest.raises(RuntimeError, match="no GPU"):
            rj.preflight(r2a, w, smoke=False, min_free=1)


def test_save_weights_removes_its_tmp_folder_after_a_failed_copy(tmp_path, monkeypatch):
    src = tmp_path / "src"
    src.mkdir()
    (src / "model.safetensors").write_bytes(b"one")
    import shutil

    def broken(s, d, *a, **k):
        Path(d).mkdir()
        (Path(d) / "half").write_text("x")
        raise OSError("disk full")

    monkeypatch.setattr(shutil, "copytree", broken)
    with pytest.raises(OSError):
        re_.save_weights(src, tmp_path / "weights" / "job")
    assert list((tmp_path / "weights").iterdir()) == []


def test_environment_info_records_versions_and_gpu():
    env = rj.env_info()
    assert set(env) == {"torch", "transformers", "bitsandbytes", "accelerate", "gpu", "gpu_capability"}
    assert env["torch"] and env["transformers"]
