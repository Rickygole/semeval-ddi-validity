import argparse
import gzip
import json
import random
import re
import hashlib
import os
import time
from pathlib import Path

from . import bert, config, inputs, semeval
from .inputs import ood_as_pairs
from .metrics import binary_f1, macro_f1

MODELS = {"biomedbert": config.ENCODER, "bertbase": "bert-base-uncased",
          "biobert": "dmis-lab/biobert-base-cased-v1.2"}
LLMS = {"biomistral": config.LLM, "qwen": "Qwen/Qwen2.5-7B-Instruct"}
KRAG_ABLATIONS = ["bm25", "dense", "excl_mechanism_of_action", "excl_pharmacokinetics",
                  "excl_warnings_and_cautions", "excl_clinical_pharmacology", "masked"]
OTHER_SEEDS = [1, 2, 3, 4]


def job(kind, system, model="biomedbert", seed=42, priority=1, **kw):
    cfg = {"kind": kind, "system": system, "model": model, "seed": seed, "priority": priority,
           "split": "standard", "epochs": config.MAX_EPOCHS, "variant": "hybrid", "k": 5, "chars": 100}
    cfg.update(kw)
    if kind == "llm":
        cfg["name"] = f"llm-{model}-{system}"
    elif system == "krag":
        cfg["name"] = f"krag-{cfg['variant']}-k{cfg['k']}-c{cfg['chars']}-{model}-s{seed}"
    else:
        cfg["name"] = f"{system}-{model}" + ("-disjoint" if cfg["split"] == "disjoint" else "") + f"-s{seed}"
    return cfg


def registry():
    J = []
    for m in ("biomedbert", "bertbase"):
        J += [job("bert", "b2sentence", m), job("bert", "b2mixed", m), job("bert", "b1names", m)]
    J += [job("bert", "b2masked")]
    J += [job("bert", "b2sentence", split="disjoint"), job("bert", "b2mixed", split="disjoint")]
    J += [job("bert", "krag", chars=400, epochs=10)]
    J += [job("bert", "krag", variant="contaminated", chars=400, epochs=10)]
    J += [job("llm", "names", "biomistral"), job("llm", "names", "qwen")]
    for s in OTHER_SEEDS:
        for m in ("biomedbert", "bertbase"):
            J += [job("bert", "b2sentence", m, s, 2), job("bert", "b2mixed", m, s, 2)]
        J += [job("bert", "b1names", "biomedbert", s, 2), job("bert", "b2masked", "biomedbert", s, 2)]
        J += [job("bert", "krag", "biomedbert", s, 2, chars=400, epochs=10)]
        J += [job("bert", "krag", "biomedbert", s, 2, variant="contaminated", chars=400, epochs=10)]
    for v in KRAG_ABLATIONS:
        J += [job("bert", "krag", priority=3, variant=v, chars=400, epochs=10)]
    for k in (1, 3):
        J += [job("bert", "krag", priority=3, k=k, chars=400, epochs=10)]
    J += [job("bert", "krag", priority=3, chars=100)]
    J += [job("bert", "b2sentence", "biobert", priority=3), job("bert", "b2mixed", "biobert", priority=3), job("bert", "b1names", "biobert", priority=3)]
    J += [job("bert", "b1names", priority=3, split="disjoint")]
    J += [job("llm", "rag", "biomistral", priority=3), job("llm", "rag", "qwen", priority=3)]
    return sorted(J, key=lambda j: j["priority"])


class Inputs:
    def __init__(self, bundle, smoke=False):
        with gzip.open(bundle, "rt") as f:
            d = json.load(f)
        self.text = d["chunk_text"]
        self.retrieval = d["retrieval"]
        semeval.download()
        self.train = semeval.load_pairs("train")
        self.test = semeval.load_pairs("test")
        self.ood = ood_as_pairs(d["ood_pairs"])
        self.ood_old = ood_as_pairs(d.get("ood_old_pairs", []))
        if not self.ood_old and not smoke:
            raise RuntimeError("bundle has no older-drug pairs; rebuild it")
        if smoke:
            self.train, self.test = self.train[::60], self.test[::40]
            self.ood, self.ood_old = self.ood[::10], self.ood_old[::10]
        self.novel_names = sorted({p["drug_a"] for p in self.ood})
        self.vocab_names = sorted({n for r in self.train for n in (r["drug_a"], r["drug_b"])})
        self._swaps()
        self._disjoint()
        self._ood_swap()

    def _swaps(self):
        rng = random.Random(0)
        self.swaps = {}
        for kind in ("vocab", "novel", "pseudo"):
            rows = []
            for p in self.test:
                if kind == "pseudo":
                    a, b = inputs.pseudo_word(rng), inputs.pseudo_word(rng)
                else:
                    pool = self.vocab_names if kind == "vocab" else self.novel_names
                    a, b = rng.sample([n for n in pool if n not in (p["drug_a"], p["drug_b"])], 2)
                rows.append(inputs.swapped(p, a, b))
            self.swaps[kind] = rows

    def _ood_swap(self):
        rng = random.Random(0)
        negs = {}
        for p in self.ood:
            if p["y"] == 0:
                negs.setdefault(p["drug_a"], []).append(p["drug_b"])
        rows = []
        for p in self.ood:
            if p["y"] == 1 and p["sentence"] and negs.get(p["drug_a"]):
                rows.append(p)
                n = rng.choice(negs[p["drug_a"]])
                s = re.sub(r"(?<![\w-])" + re.escape(p["drug_b"]) + r"(?![\w-])", lambda m: n, p["sentence"],
                           flags=re.IGNORECASE)
                rows.append({**p, "drug_b": n, "sentence": s, "y": 0})
        self.ood_swap = rows

    def _disjoint(self, frac=0.3):
        drugs = sorted({n for r in self.test for n in (r["drug_a"], r["drug_b"])})
        rng = random.Random(0)
        self.heldout = set(rng.sample(drugs, int(len(drugs) * frac)))
        self.train_disjoint = [r for r in self.train if r["drug_a"] not in self.heldout and r["drug_b"] not in self.heldout]
        self.test_unseen_index = [i for i, r in enumerate(self.test)
                                  if r["drug_a"] in self.heldout or r["drug_b"] in self.heldout]

    def cache(self, variant, k):
        ids = self.retrieval["hybrid" if variant == "masked" else variant]
        return {key: [self.text[str(i)] for i in v[:k]] for key, v in ids.items()}


def _pred(model, tok, texts):
    p, s = bert.predict(model, tok, texts, return_probs=True)
    return {"preds": p, "p": [round(x, 6) for x in s]}


def _sub(rows, idx):
    return [rows[i] for i in idx]


def bert_job(inp, cfg, out):
    seed, system = cfg["seed"], cfg["system"]
    train_rows = inp.train_disjoint if cfg["split"] == "disjoint" else inp.train
    tr, va = bert.split_train_val(train_rows, seed)
    if system == "b2sentence":
        f_tr, y_tr = inputs.b2_sentence(tr), [r["label_id"] for r in tr]
        f_va = inputs.b2_sentence(va)
    elif system == "b2mixed":
        f_tr, y_tr = inputs.mixed_training(tr)
        f_va = inputs.b2_sentence(va)
    elif system == "b2masked":
        f_tr, y_tr = inputs.b2_masked(tr), [r["label_id"] for r in tr]
        f_va = inputs.b2_masked(va)
    elif system == "b1names":
        f_tr, y_tr = inputs.b1(tr), [r["label_id"] for r in tr]
        f_va = inputs.b1(va)
    elif system == "krag":
        cache = inp.cache(cfg["variant"], cfg["k"])
        chars = cfg["chars"]
        fk = lambda rows: inputs.krag(rows, cache, chars=chars, k=cfg["k"], mask=cfg["variant"] == "masked")
        f_tr, y_tr, f_va = fk(tr), [r["label_id"] for r in tr], fk(va)
    model, tok = bert.train(f_tr, y_tr, f_va, [r["label_id"] for r in va], out / "work", seed,
                            model_name=MODELS[cfg["model"]], epochs=cfg["epochs"])
    ev = {}
    sent_idx = [i for i, p in enumerate(inp.ood) if p["sentence"]]
    old_idx = [i for i, p in enumerate(inp.ood_old) if p["sentence"]]
    if system == "krag":
        ev["test"] = _pred(model, tok, fk(inp.test))
        ev["ood"] = _pred(model, tok, fk(inp.ood))
    elif system == "b1names":
        ev["test_names"] = _pred(model, tok, inputs.b1(inp.test))
        ev["ood_names"] = _pred(model, tok, inputs.b1(inp.ood))
        ev["oodold_names"] = _pred(model, tok, inputs.b1(inp.ood_old))
        for k, rows in inp.swaps.items():
            ev[f"swap_{k}_names"] = _pred(model, tok, inputs.b1(rows))
    else:
        ev["test_sentence"] = _pred(model, tok, inputs.b2_sentence(inp.test))
        ev["test_masked"] = _pred(model, tok, inputs.b2_masked(inp.test))
        ev["test_empty"] = _pred(model, tok, inputs.b2_empty(inp.test))
        ev["test_names"] = _pred(model, tok, inputs.b1(inp.test))
        ev["ood_empty"] = _pred(model, tok, inputs.b2_empty(inp.ood))
        ev["ood_names"] = _pred(model, tok, inputs.b1(inp.ood))
        ev["ood_sentence"] = {**_pred(model, tok, inputs.b2_sentence(_sub(inp.ood, sent_idx))), "index": sent_idx}
        ev["ood_swap_sentence"] = {**_pred(model, tok, inputs.b2_sentence(inp.ood_swap)),
                                   "y": [p["y"] for p in inp.ood_swap]}
        ev["oodold_empty"] = _pred(model, tok, inputs.b2_empty(inp.ood_old))
        ev["oodold_sentence"] = {**_pred(model, tok, inputs.b2_sentence(_sub(inp.ood_old, old_idx))), "index": old_idx}
        for k, rows in inp.swaps.items():
            ev[f"swap_{k}_sentence"] = _pred(model, tok, inputs.b2_sentence(rows))
    if cfg["split"] == "disjoint":
        ev["test_unseen_index"] = inp.test_unseen_index
    del model
    return ev


def llm_job(inp, cfg, state):
    from . import llm
    if state.get("llm_name") != cfg["model"]:
        state.pop("llm", None)
        import gc
        gc.collect()
        try:
            import torch
            torch.cuda.empty_cache()
        except Exception:
            pass
        state["llm"] = llm.load_any(LLMS[cfg["model"]])
        state["llm_name"] = cfg["model"]
    tok, model = state["llm"]
    ids = llm.label_token_ids(tok)
    cache = inp.cache("hybrid", 5)
    ev = {}
    sets = {"test": inp.test, "ood": inp.ood}
    if cfg["system"] == "names":
        sets["oodold"] = inp.ood_old
    for split, rows in sets.items():
        prompts = [llm.prompt_b3(r["drug_a"], r["drug_b"]) if cfg["system"] == "names"
                   else llm.prompt_b5(r["drug_a"], r["drug_b"], cache) for r in rows]
        probs = llm.score(tok, model, prompts, ids)
        ev[split] = {"preds": [max(range(5), key=lambda c: q[c]) for q in probs],
                     "p": [round(1 - q[0], 6) for q in probs]}
        print(f"{cfg['name']} {split} done", flush=True)
    return ev


def headline(ev):
    for key in ("test_sentence", "test", "test_names"):
        if key in ev:
            return key, ev[key]["preds"]
    return None, None


def run(bundle, out_dir, only=None, max_priority=3, smoke=False):
    out_dir = Path(out_dir)
    (out_dir / "preds").mkdir(parents=True, exist_ok=True)
    inp = Inputs(bundle, smoke)
    y_te = [r["label_id"] for r in inp.test]
    y_ood = [p["y"] for p in inp.ood]
    state = {}
    for cfg in registry():
        name = cfg["name"]
        if (only and name not in only) or cfg["priority"] > max_priority:
            continue
        dest = out_dir / "preds" / f"{name}.json"
        chash = hashlib.sha256(json.dumps({**cfg, "smoke": smoke}, sort_keys=True).encode()).hexdigest()
        if dest.exists():
            try:
                old = json.loads(dest.read_text())
            except ValueError:
                old = {}
            if old.get("config_hash") != chash:
                raise RuntimeError(f"{name}: existing result was made with a different config")
            print(f"skip {name}", flush=True)
            continue
        t0 = time.time()
        print(f"start {name}", flush=True)
        run_cfg = {**cfg, "epochs": 1} if smoke else cfg
        ev = llm_job(inp, run_cfg, state) if cfg["kind"] == "llm" else bert_job(inp, run_cfg, out_dir / name)
        res = {"config": cfg, "config_hash": chash, "smoke": smoke, "ood_hash": inputs.pairs_hash(inp.ood),
               "ood_old_hash": inputs.pairs_hash(inp.ood_old), "eval": ev, "seconds": round(time.time() - t0, 1)}
        hist = out_dir / name / "work" / "history.json"
        if hist.exists():
            res["history"] = json.loads(hist.read_text())
        tmp = dest.with_suffix(".tmp")
        tmp.write_text(json.dumps(res))
        os.replace(tmp, dest)
        k, p = headline(ev)
        ood_key = "ood" if "ood" in ev else ("ood_names" if "ood_names" in ev else None)
        msg = f"done {name} in {res['seconds']}s"
        if p:
            msg += f" {k} binF1={binary_f1(y_te, p):.4f} macroF1={macro_f1(y_te, p):.4f}"
        if ood_key:
            msg += f" {ood_key} binF1={binary_f1(y_ood, ev[ood_key]['preds']):.4f}"
        print(msg, flush=True)
        try:
            import torch
            torch.cuda.empty_cache()
        except Exception:
            pass


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--bundle", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--only", nargs="*")
    ap.add_argument("--max-priority", type=int, default=3)
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args()
    if a.list:
        for c in registry():
            print(c["priority"], c["name"])
    else:
        run(a.bundle, a.out, a.only, a.max_priority, a.smoke)
