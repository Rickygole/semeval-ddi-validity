import argparse
import hashlib
import json
import os
import sys
import time
from pathlib import Path

import numpy as np

from . import amend7_data as ad
from . import amend7_inputs as ai
from . import amend7_panel as pn
from . import amend7_prompts as pr
from . import bert, config
from .metrics import binary_f1

E7_SEEDS = [42, 1, 2, 3, 4]
E7_EPOCHS = 10
E7_ARMS = {"a": ("h5", "contaminated", "h5contam", ai.H5_CHARS), "b": ("fixed", "ownlabel", "fixedownlabel", ai.WINDOW_CHARS),
           "c": ("names", None, "names", 0), "d": ("fixed", "other", "fixedother", ai.WINDOW_CHARS),
           "e": ("fixed", "clean", "fixedclean", ai.WINDOW_CHARS)}
QWEN = "Qwen/Qwen2.5-7B-Instruct"
E8_JOBS = [("names", "a7-qwen-names"), ("stem_preserved", "a7-qwen-stem-preserved"),
           ("stem_scrambled", "a7-qwen-stem-scrambled")] + [
    (c, f"a7-qwen-{n}") for c, n in (("oracle", "oracle"), ("masked", "maskedoracle"), ("wrong", "wrongoracle"),
                                      ("redacted", "redactedoracle"), ("contam", "contam"), ("other", "other"),
                                      ("clean", "clean"))]


def job(kind, system, model, seed, name, group, priority=1, **kw):
    cfg = {"kind": kind, "system": system, "model": model, "seed": seed, "priority": priority, "split": "standard",
           "epochs": 0, "variant": "none", "k": ai.K, "chars": 0, "name": name, "group": group}
    cfg.update(kw)
    return cfg


def registry():
    J = []
    for seed in E7_SEEDS:
        for arm, (kind, cache, slug, chars) in E7_ARMS.items():
            J.append(job("e7", f"a7_e7{arm}", "biomedbert", seed, f"a7-e7{arm}-{slug}-s{seed}", "E7",
                         priority=1 if seed == 42 else 2, epochs=E7_EPOCHS, variant=cache or "names", chars=chars,
                         input=kind))
    for kind, name in E8_JOBS:
        J.append(job("e8", f"a7_e8_{kind}", "qwen", 42, name, "E8", variant=kind))
    for bid, repo, fmt in pn.registry_rows():
        J.append(job("panel", "a7_panel", bid, pn.SEED, f"a7-panel-{bid}-{fmt}", "E9", variant=fmt, epochs=pn.EPOCHS,
                     repo=repo))
    for x in pn.EXTERNAL:
        slug = x["repo"].split("/")[-1].lower()
        J.append(job("ext", "a7_external", slug, pn.SEED, f"a7-ext-{slug}", "E9", priority=3, variant="external", repo=x["repo"]))
    return sorted(J, key=lambda j: j["priority"])


NOTEBOOKS = {
    "E7_positive_control_part1": lambda j: j["kind"] == "e7" and j["system"][-1] in "abc",
    "E7_positive_control_part2": lambda j: j["kind"] == "e7" and j["system"][-1] in "de",
    "E8_evidence_reader": lambda j: j["kind"] == "e8",
    "E9_model_panel_part1": lambda j: j["kind"] == "panel" and j["variant"] == "pair",
    "E9_model_panel_part2": lambda j: (j["kind"] == "panel" and j["variant"] in ("marker", "masked")) or j["kind"] == "ext",
}


def notebook_jobs():
    reg = registry()
    out = {n: [j["name"] for j in reg if f(j)] for n, f in NOTEBOOKS.items()}
    flat = [x for v in out.values() for x in v]
    if sorted(flat) != sorted(j["name"] for j in reg):
        raise RuntimeError("the notebooks do not cover every job exactly once")
    return out


def code_version():
    h = hashlib.sha256()
    for p in sorted(Path(__file__).parent.glob("amend7_*.py")):
        h.update(p.name.encode())
        h.update(p.read_bytes())
    return h.hexdigest()


def config_hash(cfg, smoke):
    return hashlib.sha256(json.dumps({**cfg, "smoke": smoke, "code": code_version()}, sort_keys=True).encode()).hexdigest()


def _pred(model, tok, texts):
    p, s = bert.predict(model, tok, texts, return_probs=True)
    return {"preds": p, "p": [round(x, 6) for x in s]}


def e7_job(data, cfg, out, tiny=None):
    from . import amend7_train as tr
    arm = cfg["system"][-1]
    kind, cache, _, _ = E7_ARMS[arm]
    fn = data.text_fn(kind, cache)
    train_rows, val_rows = tr.grouped_split(data.train, cfg["seed"])
    f_tr, f_va = fn(train_rows, "train"), fn(val_rows, "train")
    model, tok = tr.train_binary(f_tr, [r["y"] for r in train_rows], f_va, [r["y"] for r in val_rows],
                                 [r["group"] for r in val_rows], out / "work", cfg["seed"], tiny or config.ENCODER,
                                 revision=None if tiny else data.manifest["panel_revisions"][config.ENCODER],
                                 epochs=1 if data.smoke else cfg["epochs"])
    suffix = "_names" if kind == "names" else ""
    ev = {f"test{suffix}": _pred(model, tok, fn(data.test, "test")),
          f"ood{suffix}": _pred(model, tok, fn(data.ood, "novel")),
          f"oodold{suffix}": _pred(model, tok, fn(data.ood_old, "older"))}
    del model
    return ev


def load_qwen(revision):
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
    q = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4", bnb_4bit_compute_dtype=torch.bfloat16,
                           bnb_4bit_use_double_quant=True)
    tok = AutoTokenizer.from_pretrained(QWEN, revision=revision)
    model = AutoModelForCausalLM.from_pretrained(QWEN, revision=revision, quantization_config=q, device_map="auto").eval()
    return tok, model


def get_llm(state, data, tiny=None):
    if "llm" not in state:
        if tiny:
            from transformers import AutoModelForCausalLM, AutoTokenizer
            tok = AutoTokenizer.from_pretrained(tiny)
            state["llm"] = (tok, AutoModelForCausalLM.from_pretrained(tiny).eval())
        else:
            state["llm"] = load_qwen(data.manifest["qwen_revision"])
    return state["llm"]


def _score_eval(tok, model, texts, words, label, log):
    from . import amend7_llm as al
    sc = al.score(tok, model, texts, words, log=log)
    return al.to_eval(sc, words), al.answer_stats(sc, pr.NON_ANSWER_MASS)


def e8_job(data, cfg, state, tiny=None):
    from . import amend7_evidence as ev
    tok, model = get_llm(state, data, tiny)
    log = lambda m: print(f"{cfg['name']} {m}", flush=True) if m.endswith("0") else None
    kind = cfg["variant"]
    out, stats = {}, {}
    cohorts = (("ood", "novel", data.ood), ("oodold", "older", data.ood_old))
    if kind == "names":
        for pid, template, words in pr.NAMES_PROMPTS:
            for key, _, rows in cohorts:
                texts = [pr.chat(tok, pr.names_prompt(template, r["drug_a"], r["drug_b"])) for r in rows]
                out[f"{key}_{pid}"], stats[f"{key}_{pid}"] = _score_eval(tok, model, texts, words, pid, log)
        for key, _, _ in cohorts:
            out[key] = out[f"{key}_{pr.PRIMARY}"]
        return out, {"answer": stats}
    if kind in ("stem_preserved", "stem_scrambled"):
        stems = json.loads((data.a7 / "stem_names.json").read_text())["stems"]
        field = "preserved" if kind == "stem_preserved" else "scrambled"
        excluded = set(data.sets["older_artifacts"]) | set(data.sets["older_missed_vocabulary_drugs"])
        for key, _, rows in cohorts:
            idx = [i for i, r in enumerate(rows) if r["drug_a"] in stems and r["drug_a"] not in excluded]
            sub = [{**rows[i], "drug_a": stems[rows[i]["drug_a"]][field]} for i in idx]
            texts = [pr.chat(tok, pr.names_prompt(pr.P2, r["drug_a"], r["drug_b"])) for r in sub]
            e, s = _score_eval(tok, model, texts, pr.BINARY, kind, log)
            out[key] = {**e, "index": idx}
            stats[key] = s
        return out, {"answer": stats}
    context = {}
    for key, coh, rows in cohorts:
        full_rows = data.ood_full if coh == "novel" else data.old_full
        drugs = sorted({r["drug_a"] for r in full_rows})
        sections = json.loads((data.a7 / "di_sections.json").read_text())
        pick = "masked" if kind == "masked" else "text"
        di = {d: sections[d][pick] for d in drugs if d in sections}
        caches = {"contaminated": data.cache(coh, "contaminated"), "hybrid": data.cache(coh, "clean")}
        ctx = ev.EvidenceBuilder(tok, di, data.lookup, caches, data.chunk_text, drugs)
        arm_caches = {a: data.cache(coh, a) for a in ("contaminated", "other", "clean")}
        texts, hits, cut = [], [], 0
        for r in rows:
            e, m = ai.qwen_evidence(kind, r, ctx, data.fixed, arm_caches)
            cut += int(m.get("truncated", False))
            texts.append(pr.chat(tok, pr.evidence_prompt(e, r["drug_a"], r["drug_b"])))
            hits.append(ev.grep_hit(e, data.fixed.forms(r["drug_b"])))
        out[key], stats[key] = _score_eval(tok, model, texts, pr.BINARY, kind, log)
        y = np.array([r["y"] for r in rows])
        h = np.array(hits)
        context[key] = {"evidence_truncated": cut, "positives_with_partner_in_context": float(h[y == 1].mean()),
                        "negatives_with_partner_in_context": float(h[y == 0].mean()), "partner_in_context": hits}
    return out, {"answer": stats, "context": context}


def panel_job(data, cfg, out):
    from transformers import AutoTokenizer
    if cfg.get("tiny"):
        model_path = cfg["tiny"]
    else:
        model_path = pn.prepare_model(cfg["repo"], data.manifest["panel_revisions"][cfg["repo"]], out / "model",
                                      data.manifest["panel_lowercase"].get(cfg["repo"]))
    sep = AutoTokenizer.from_pretrained(model_path).sep_token or "[SEP]"
    spec = pn.formats(cfg["variant"], sep)
    tr, va = bert.split_train_val(data.train_semeval, cfg["seed"])
    f_tr, ok_tr = spec["sentence"](tr)
    f_va, _ = spec["sentence"](va)
    model, tok = bert.train(f_tr, [r["label_id"] for r in tr], f_va, [r["label_id"] for r in va], out / "work",
                            cfg["seed"], model_name=model_path, epochs=1 if data.smoke else cfg["epochs"])
    ev = {}
    t_sent, t_ok = spec["sentence"](data.test)
    ev["test_sentence"] = _pred(model, tok, t_sent)
    ev["test_empty"] = _pred(model, tok, spec["names"](data.test))
    ev["ood_empty"] = _pred(model, tok, spec["names"](data.ood))
    ev["oodold_empty"] = _pred(model, tok, spec["names"](data.ood_old))
    info = {"marker_fallback_train": int(len(ok_tr) - sum(ok_tr)), "marker_fallback_test": int(len(t_ok) - sum(t_ok)),
            "sep_token": sep, "do_lower_case": data.manifest["panel_lowercase"].get(cfg["repo"]),
            "tokenizer_lowercases": bool(getattr(tok, "do_lower_case", False))}
    for key, rows in (("ood_sentence", data.ood), ("oodold_sentence", data.ood_old)):
        s, ok = spec["sentence"](rows)
        idx = [i for i, p in enumerate(rows) if p["sentence"] and ok[i]]
        ev[key] = {**_pred(model, tok, [s[i] for i in idx]), "index": idx}
    del model
    return ev, info


def _probs(model, tok, texts, batch_size=64):
    import torch
    from transformers import DataCollatorWithPadding
    dev = next(model.parameters()).device
    coll = DataCollatorWithPadding(tok)
    enc = bert._encode(tok, texts, config.MAX_LENGTH)
    out = []
    model.eval()
    for feats, _ in bert._batches(enc, None, batch_size, False, None):
        b = {k: v.to(dev) for k, v in coll(feats).items()}
        with torch.no_grad():
            out.extend(torch.softmax(model(**b).logits.float(), -1).cpu().tolist())
    return np.array(out)


def ext_job(data, cfg, out, tiny=None):
    from transformers import AutoModelForSequenceClassification, AutoTokenizer
    from .index import device
    spec = next(x for x in pn.EXTERNAL if x["repo"] == cfg["repo"])
    tags = spec["tags"]
    facts = data.manifest["external_facts"][cfg["repo"]]
    checks = pn.static_checks(facts)
    if not all(checks.values()):
        raise RuntimeError(f"{cfg['repo']} fails the static checks: {checks}")
    path = tiny or str(pn.snapshot(cfg["repo"], data.manifest["external_revisions"][cfg["repo"]]))
    tok = AutoTokenizer.from_pretrained(path)
    model = AutoModelForSequenceClassification.from_pretrained(path).to(device()).eval()
    sample = data.train_semeval[:pn.EXTERNAL_TRAIN_SAMPLE]
    s_texts, _ = pn.marker_sentence(sample, tags)
    train_probs = _probs(model, tok, s_texts)
    neg = pn.majority_class(train_probs.argmax(1).tolist())
    names = getattr(model.config, "id2label", {})
    info = {"negative_class_index": int(neg), "negative_class_label": names.get(neg, str(neg)),
            "train_sample": len(sample), "train_share_predicted_negative": float((train_probs.argmax(1) == neg).mean()),
            "static_checks": checks, "facts": facts}

    def pred(texts):
        pr_ = _probs(model, tok, texts)
        p = 1 - pr_[:, neg]
        return {"preds": [int(x != neg) for x in pr_.argmax(1)], "p": [round(float(x), 6) for x in p]}

    ev = {}
    t_sent, t_ok = pn.marker_sentence(data.test, tags)
    ev["test_sentence"] = pred(t_sent)
    ev["test_empty"] = pred(pn.marker_names(data.test, tags))
    ev["ood_empty"] = pred(pn.marker_names(data.ood, tags))
    ev["oodold_empty"] = pred(pn.marker_names(data.ood_old, tags))
    for key, rows in (("ood_sentence", data.ood), ("oodold_sentence", data.ood_old)):
        s_, ok = pn.marker_sentence(rows, tags)
        idx = [i for i, p in enumerate(rows) if p["sentence"] and ok[i]]
        ev[key] = {**pred([s_[i] for i in idx]), "index": idx}
    y = [int(r["label_id"] != 0) for r in data.test]
    info["semeval_test_binary_f1"] = binary_f1(y, ev["test_sentence"]["preds"])
    return ev, info


def atomic_write(dest, text):
    tmp = dest.with_name(f"{dest.stem}.{os.getpid()}.tmp")
    tmp.write_text(text)
    os.replace(tmp, dest)


def finished(dest, chash, name):
    if not dest.exists():
        return False
    try:
        old = json.loads(dest.read_text())
    except ValueError:
        old = {}
    if old.get("config_hash") != chash:
        raise RuntimeError(f"{name}: existing result was made with a different config")
    return True


def run_job(cfg, data, state, workdir, tiny_encoder, tiny_llm):
    local = Path(workdir) / "work_local" / cfg["name"]
    extra = {}
    if cfg["kind"] == "e7":
        ev = e7_job(data, cfg, local, tiny_encoder)
    elif cfg["kind"] == "e8":
        ev, extra = e8_job(data, cfg, state, tiny_llm)
    elif cfg["kind"] == "ext":
        ev, extra = ext_job(data, cfg, local, tiny_encoder)
    else:
        ev, extra = panel_job(data, {**cfg, "tiny": tiny_encoder}, local)
    hist = local / "work" / "history.json"
    if hist.exists():
        extra["history"] = json.loads(hist.read_text())
    return ev, extra


def run(workdir, out_dir, only=None, smoke=False, tiny_encoder=None, tiny_llm=None, groups=None, runner=None, data=None):
    out_dir = Path(out_dir)
    (out_dir / "preds").mkdir(parents=True, exist_ok=True)
    selected = [c for c in registry() if not ((only and c["name"] not in only) or (groups and c["group"] not in groups))]
    if data is None:
        data = ad.Data(workdir, smoke, need_semeval=any(c["kind"] in ("e7", "panel", "ext") for c in selected))
    runner = runner or run_job
    state, failed = {}, []
    for cfg in selected:
        name = cfg["name"]
        dest = out_dir / "preds" / f"{name}.json"
        chash = config_hash(cfg, smoke)
        if finished(dest, chash, name):
            print(f"skip {name}", flush=True)
            continue
        t0 = time.time()
        print(f"start {name}", flush=True)
        try:
            ev, extra = runner(cfg, data, state, workdir, tiny_encoder, tiny_llm)
            res = {"config": cfg, "config_hash": chash, "smoke": smoke, "ood_hash": data.ood_hash,
                   "ood_old_hash": data.old_hash, "train_hash": data.manifest["train_hash"],
                   "prompts_sha256": pr.frozen_hash(), "code_version": code_version(), "eval": ev,
                   "seconds": round(time.time() - t0, 1), **extra}
            atomic_write(dest, json.dumps(res))
            (out_dir / "preds" / f"{name}.failed.txt").unlink(missing_ok=True)
            print(f"done {name} in {res['seconds']}s", flush=True)
        except Exception:
            import traceback
            failed.append(name)
            atomic_write(out_dir / "preds" / f"{name}.failed.txt", traceback.format_exc())
            print(f"FAILED {name}", flush=True)
        try:
            import torch
            torch.cuda.empty_cache()
        except Exception:
            pass
    if failed:
        print(f"{len(failed)} jobs failed: {failed}", flush=True)
    return failed


def main(argv=None):
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="cmd")
    m = sp.add_parser("merge")
    m.add_argument("--inputs", required=True)
    m.add_argument("--delta", required=True)
    r = sp.add_parser("run")
    r.add_argument("--workdir", required=True)
    r.add_argument("--out", required=True)
    r.add_argument("--only", nargs="*")
    r.add_argument("--group", nargs="*")
    r.add_argument("--smoke", action="store_true")
    r.add_argument("--tiny-encoder")
    r.add_argument("--tiny-llm")
    sp.add_parser("list")
    a = ap.parse_args(argv)
    if a.cmd == "merge":
        print("corrected bundle ready", ad.merge_corrected(a.inputs, a.delta))
    elif a.cmd == "list":
        for c in registry():
            print(c["priority"], c["group"], c["name"])
    else:
        failed = run(a.workdir, a.out, a.only, a.smoke, a.tiny_encoder, a.tiny_llm, a.group)
        if failed:
            sys.exit(1)


if __name__ == "__main__":
    main()
