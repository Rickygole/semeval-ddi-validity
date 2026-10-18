import json
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ddiood import amend7_evidence as ev
from ddiood import amend7_inputs as ai
from ddiood import amend7_jobs as aj
from ddiood import amend7_llm as al
from ddiood import amend7_panel as pn
from ddiood import amend7_pairs as ap
from ddiood import amend7_prompts as pr
from ddiood import amend7_train as tr

LOOKUP = {"warfarin": {"normalized": "warfarin", "canonicalized": "warfarin", "rxcui": "1"},
          "coumadin": {"normalized": "coumadin", "canonicalized": "coumadin", "rxcui": "1"},
          "aspirin": {"normalized": "aspirin", "canonicalized": "aspirin", "rxcui": "2"}}


def rows(n_groups=20, per=6, seed=0):
    rng = np.random.RandomState(seed)
    out = []
    for g in range(n_groups):
        for i in range(per):
            out.append({"drug_a": f"d{g}", "drug_b": f"p{i}", "y": int(i < 2 or rng.rand() < 0.2), "group": f"d{g}"})
    return out


def test_grouped_split_has_no_group_overlap_and_both_classes():
    r = rows()
    a, b = tr.grouped_split(r, 3)
    assert not {x["group"] for x in a} & {x["group"] for x in b}
    assert {x["y"] for x in b} == {0, 1}
    assert tr.grouped_split(r, 3)[1] == b
    assert tr.grouped_split(r, 4)[1] != b


def test_val_auroc_is_within_drug():
    y = [1, 0, 1, 0]
    g = ["a", "a", "b", "b"]
    assert tr.val_auroc(y, [0.9, 0.1, 0.2, 0.1], g) == 1.0
    assert tr.val_auroc(y, [0.9, 0.95, 0.2, 0.1], g) == 0.5


def test_partner_forms_use_rxcui_synonyms():
    f = ev.partner_forms("warfarin", LOOKUP)
    assert "coumadin" in f and "warfarin" in f and "aspirin" not in f
    assert ev.grep_hit("Coumadin levels rise.", f) == 1
    assert ev.grep_hit("antiwarfarinic agents", f) == 0


def test_redact_removes_every_partner_sentence():
    text = "Drug X raises warfarin levels. It is a CYP3A inhibitor. Avoid use with Coumadin or aspirin."
    out = ev.redact(text, ev.partner_forms("warfarin", LOOKUP))
    assert "warfarin" not in out.lower() and "coumadin" not in out.lower()
    assert "CYP3A inhibitor" in out


def test_mask_names_keeps_class_statements():
    names = {("warfarin",), ("aspirin",), ("st", "johns", "wort")}
    out = ev.mask_names("Warfarin and aspirin with St Johns Wort; strong CYP3A inhibitors raise exposure.", names)
    assert out.count("[DRUG]") == 3
    assert "strong CYP3A inhibitors" in out


def test_snippet_centres_on_partner_and_orders_hits_first():
    forms = ["warfarin"]
    long = "x " * 300 + "warfarin " + "y " * 300
    s, has = ai.snippet(long, forms, 100)
    assert has and "warfarin" in s and len(s) <= 100
    s2, has2 = ai.snippet("nothing here " * 40, forms, 100)
    assert not has2 and len(s2) == 100
    text = {"1": "alpha beta", "2": long, "3": "gamma"}
    meta = {"1": ["a", "sec"], "2": ["b", "sec"], "3": ["c", "sec"]}
    out = ai.evidence_snippets("a", "warfarin", ["1", "2", "3"], text, meta, forms, 100)
    assert "warfarin" in out[0] and out[0].startswith("b | sec:")


def test_builders_raise_on_missing_passages():
    with pytest.raises(ai.MissingPassages):
        ai.krag_h5([{"drug_a": "a", "drug_b": "b"}], {}, {})
    fb = ai.FixedBuilder(LOOKUP, {}, {})
    with pytest.raises(ai.MissingPassages):
        fb.encoder_inputs([{"drug_a": "a", "drug_b": "b"}], {"a|||b": []})


def test_h5_format_matches_existing_krag_when_passages_exist():
    from ddiood import inputs
    cache = {"a|||b": [1, 2]}
    text = {"1": "p" * 500, "2": "q" * 10}
    pairs = [{"drug_a": "a", "drug_b": "b"}]
    assert ai.krag_h5(pairs, cache, text) == inputs.krag(pairs, {"a|||b": [text["1"], text["2"]]}, chars=400, k=5)


def test_stems_preserved_and_scrambled():
    class Tok:
        def __call__(self, s, add_special_tokens=False):
            return {"input_ids": list(range(max(1, len(s) // 4)))}
    r = ev.stem_names_for("vemurafenib", set(), Tok())
    assert r and r["preserved"].endswith(r["stem"]) and not ev.has_stem(r["scrambled"])
    assert sorted(r["scrambled"][len(r["prefix"]):]) == sorted(r["stem"])
    assert abs(r["tokens_preserved"] - r["tokens_scrambled"]) <= 1
    assert ev.stem_names_for("plainname", set(), Tok()) is None
    assert ev.stem_names_for("insulin glargine", set(), Tok()) is None


def test_prompts_are_frozen_and_primary_is_binary():
    assert len(pr.NAMES_PROMPTS) == 5
    assert pr.NAMES_PROMPTS[0][0] == pr.PRIMARY == "p2_binary"
    assert pr.NAMES_PROMPTS[0][2] == pr.BINARY
    assert pr.MAX_PROMPT_TOKENS == 8192
    assert len(pr.frozen_hash()) == 64


def test_budget_batches_cover_all_and_respect_budget():
    lens = [10, 500, 30, 480, 20, 3000]
    batches = al.batches_by_budget(lens, 1000)
    assert sorted(i for b in batches for i in b) == list(range(len(lens)))
    for b in batches:
        assert max(lens[i] for i in b) * len(b) <= 1000 or len(b) == 1


def test_to_eval_binary_and_five_way():
    sc = [{"q": [0.2, 0.8], "mass": 1.0, "tokens": 5}]
    e = al.to_eval(sc, pr.BINARY)
    assert e["p"] == [0.8] and e["preds"] == [1]
    sc5 = [{"q": [0.1, 0.5, 0.2, 0.1, 0.1], "mass": 1.0, "tokens": 5}]
    e5 = al.to_eval(sc5, pr.CLASSES)
    assert e5["preds"] == [1] and abs(e5["p"][0] - 0.9) < 1e-6


def test_prompt_too_long_raises():
    class Tok:
        def __call__(self, t, add_special_tokens=False):
            return {"input_ids": list(range(len(t)))}
    with pytest.raises(al.PromptTooLong):
        al.tokenize_all(Tok(), ["x" * 20], max_length=10)


def test_marker_function_uses_annotated_offsets_and_sep_tokens():
    s = "Warfarin may increase the effect of aspirin; aspirin is not warfarin."
    m = pn.mark(s, "warfarin", "aspirin")
    assert m == "<e1>Warfarin</e1> may increase the effect of <e2>aspirin</e2>; aspirin is not warfarin."
    ann = ((s.index("; aspirin") + 2, s.index("; aspirin") + 9), (s.rindex("warfarin"), s.rindex("warfarin") + 8))
    m2 = pn.mark(s, "aspirin", "warfarin", annotated=ann)
    assert m2.endswith("<e2>warfarin</e2>.") and "; <e1>aspirin</e1> is not" in m2
    bad = pn.mark(s, "aspirin", "warfarin", annotated=((0, 4), (5, 9)))
    assert bad is not None
    assert pn.mark(s, "warfarin", "ibuprofen") is None
    assert pn.marker_names([{"drug_a": "d", "drug_b": "p"}]) == ["<e1>d</e1> and <e2>p</e2>."]
    assert pn.marker_names([{"drug_a": "d", "drug_b": "p"}], pn.BRACKET) == ["[E1]d[/E1] and [E2]p[/E2]."]
    out, ok = pn.marker_sentence([{"drug_a": "x", "drug_b": "y", "sentence": ""}])
    assert ok == [False]
    row = {"drug_a": "a", "drug_b": "b", "sentence": "s"}
    assert pn.formats("pair", "</s>")["sentence"]([row])[0] == [("s", "a </s> b")]
    assert pn.formats("masked", "</s>")["names"]([row]) == [("", "@DRUG$ </s> @DRUG$")]


def test_panel_stats_two_way_shared_draws_recovers_signal_and_ties():
    rng = np.random.RandomState(0)
    drugs = np.repeat([f"d{i}" for i in range(40)], 6)
    partners = np.array([f"p{i % 9}" for i in range(240)])
    y = np.tile([1, 1, 0, 0, 0, 0], 40)
    models = []
    for i in range(8):
        p = rng.rand(len(y)) + 0.1 * i * y
        models.append({"name": f"m{i}", "y": y, "p": p, "groups": drugs, "partners": partners, "semeval": 0.5 + 0.05 * i})
    res = pn.panel_stats(models, n_boot=200, seed=42)
    assert res["rho"] > 0.8 and res["n_models"] == 8 and "two-way" in res["bootstrap"]
    again = pn.panel_stats(models, n_boot=200, seed=42)
    assert again["rho_lo95"] == res["rho_lo95"] and again["lo95"] == res["lo95"]
    tied = [{"name": "t", "y": y, "p": np.zeros(len(y)), "groups": drugs, "partners": partners, "semeval": 0.9},
            {"name": "u", "y": y, "p": np.zeros(len(y)), "groups": drugs, "partners": partners, "semeval": 0.8}]
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        r2 = pn.panel_stats(tied, n_boot=50)
    assert r2["auroc"] == [0.5, 0.5] and r2["rho"] != r2["rho"]
    from ddiood import stats
    st = pn.pair_structure(y, drugs, partners)
    assert abs(pn.win_values(models[0]["p"], st).mean() - stats.stratified_auroc(y, models[0]["p"], drugs)) < 1e-9


def test_registry_shape():
    reg = aj.registry()
    names = [j["name"] for j in reg]
    assert len(names) == len(set(names))
    assert all(n.startswith("a7-") for n in names)
    e7 = [j for j in reg if j["group"] == "E7"]
    assert len(e7) == 25 and {j["seed"] for j in e7} == {42, 1, 2, 3, 4}
    assert len([j for j in reg if j["group"] == "E8"]) == 10
    panel = [j for j in reg if j["group"] == "E9"]
    assert len([j for j in panel if j["variant"] != "masked"]) >= 15
    assert all(j["epochs"] == aj.E7_EPOCHS for j in e7)


def test_excluded_vocab_catches_salts_prodrugs_and_metabolites():
    def entry(n, cui):
        return {"normalized": n, "canonicalized": n, "rxcui": cui}
    lk = {k: entry(k, str(i)) for i, k in enumerate(
        ["atorvastatin", "warfarin", "aprepitant", "naltrexone", "somatropin", "venlafaxine", "sirolimus", "esmolol hcl"])}
    ood = ["atorvastatin calcium", "aducanumab-avwa", "fosaprepitant dimeglumine", "methylnaltrexone bromide",
           "lonapegsomatropin-tcgd", "desvenlafaxine", "temsirolimus", "esmolol"]
    excl, matches = ap.excluded_vocab(lk, ood)
    assert set(excl) == {"atorvastatin", "aprepitant", "naltrexone", "somatropin", "venlafaxine", "sirolimus", "esmolol hcl"}
    assert "fosaprepitant dimeglumine" in matches["aprepitant"] and "desvenlafaxine" in matches["venlafaxine"]
    assert "warfarin" not in excl
    assert ap.core("fosaprepitant dimeglumine") == "fosaprepitant"
    assert not ap.core_match("amlodipine", "lovastatin")
    ex2, _ = ap.excluded_vocab(lk, ["x"], {"warfarin": ["methylwarfarinxyz"]})
    assert "warfarin" not in ex2
    ex3, m3 = ap.excluded_vocab(lk, ["methylnaltrexone"], {"warfarin": ["naltrexone"]})
    assert "warfarin" in ex3


def test_dense_rows_never_returns_masked_chunks():
    from ddiood import amend7_retrieval as ar
    rng = np.random.RandomState(0)
    x = rng.randn(6, 4).astype("float32")
    q = rng.randn(1, 4).astype("float32")
    out = ar._dense_rows(q, x, (x ** 2).sum(1), [np.array([0, 1, 2])], 10)
    assert set(out[0][out[0] >= 0].tolist()) == {3, 4, 5}
    assert (out[0] == -1).sum() == len(out[0]) - 3


def test_notebooks_cover_every_job_once_parse_and_follow_conventions():
    import json
    root = Path(__file__).resolve().parents[1]
    nbs = aj.notebook_jobs()
    assert sorted(x for v in nbs.values() for x in v) == sorted(j["name"] for j in aj.registry())
    est_path = root / "artifacts" / "amend7" / "time_estimates.json"
    if est_path.exists():
        assert all(v["high_h"] <= 2.5 for v in json.loads(est_path.read_text())["notebooks"].values())
    for name, jobs in nbs.items():
        nb = json.loads((root / "colab" / "experiments" / f"{name}.ipynb").read_text())
        assert all(c["cell_type"] == "code" for c in nb["cells"])
        for i, c in enumerate(nb["cells"]):
            assert all(l.endswith("\n") for l in c["source"][:-1])
            src = "".join(c["source"])
            python = [l for l in src.split("\n") if not l.startswith(("!", "%"))]
            compile("\n".join(python), f"{name} cell {i}", "exec")
        src = "".join("".join(c["source"]) + "\n" for c in nb["cells"])
        assert "import osfrom" not in src and "import os\nfrom google.colab import drive" in src
        assert not any(line.strip().startswith("#") for line in src.split("\n"))
        for bad in ("cla" + "ude", chr(0x2013), chr(0x2014), "/MyDrive/temporal-ood-ddi/work"):
            assert bad not in src.lower()
        assert f"runs/{name}.log" in src and all(f'"{j}"' in src for j in jobs)
        assert "set -o pipefail" in src and "amend7_bundle.tgz -C /content/w" in src and "failed.txt" in src


def _stub_data():
    class D:
        smoke = True
        ood_hash = "h1"
        old_hash = "h2"
        manifest = {"train_hash": "t"}
    return D()


def test_run_writes_atomically_skips_finished_and_records_failures(tmp_path, monkeypatch):
    reg = [aj.job("e7", "a7_e7a", "biomedbert", 42, f"a7-fake-{i}", "E7") for i in range(3)]
    monkeypatch.setattr(aj, "registry", lambda: reg)
    calls = []

    def runner(cfg, data, state, workdir, te, tl):
        calls.append(cfg["name"])
        if cfg["name"].endswith("1"):
            raise ValueError("boom")
        return {"test": {"preds": [0], "p": [0.1]}}, {}

    (tmp_path / "preds").mkdir()
    (tmp_path / "preds" / "a7-fake-0.999.tmp").write_text("{}")
    failed = aj.run(tmp_path, tmp_path, runner=runner, data=_stub_data(), smoke=True)
    assert failed == ["a7-fake-1"] and calls == ["a7-fake-0", "a7-fake-1", "a7-fake-2"]
    assert (tmp_path / "preds" / "a7-fake-0.json").exists() and (tmp_path / "preds" / "a7-fake-2.json").exists()
    assert not (tmp_path / "preds" / "a7-fake-1.json").exists()
    assert "boom" in (tmp_path / "preds" / "a7-fake-1.failed.txt").read_text()
    calls.clear()
    aj.run(tmp_path, tmp_path, runner=lambda c, *a: (calls.append(c["name"]) or ({"test": {"preds": [0], "p": [0.2]}}, {})),
           data=_stub_data(), smoke=True)
    assert calls == ["a7-fake-1"]
    assert not (tmp_path / "preds" / "a7-fake-1.failed.txt").exists()
    saved = json.loads((tmp_path / "preds" / "a7-fake-0.json").read_text())
    assert saved["config"]["name"] == "a7-fake-0" and saved["config_hash"] == aj.config_hash(reg[0], True)


def test_config_hash_changes_with_code_version(monkeypatch):
    cfg = aj.registry()[0]
    h1 = aj.config_hash(cfg, False)
    monkeypatch.setattr(aj, "code_version", lambda: "other")
    assert aj.config_hash(cfg, False) != h1
