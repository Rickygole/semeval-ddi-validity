import argparse
import gzip
import json
import re

import numpy as np

from amend7_cpu_common import (BOOT_SEED, PREDS, ROOT, SEEDS, ci, ev, f3, paired_draws, summarize_draws, stats, write)
from ddiood import config
from ddiood.metrics import extended

VARIANTS = ("contaminated", "hybrid")
CHARS, K = 400, 5


def named(name, text):
    return re.search(r"(?<![\w-])" + re.escape(name) + r"(?![\w-])", text, flags=re.IGNORECASE) is not None


def model_input(a, b, texts):
    if not texts:
        return f"{a} [SEP] {b}", ""
    ev_text = " [SEP] ".join(x[:CHARS] for x in texts)
    return f"{a} [SEP] {b} [SEP] {ev_text}", ev_text


def visible_evidence(tok, full, evidence):
    if not evidence:
        return ""
    enc = tok(full, truncation=True, max_length=config.MAX_LENGTH, return_offsets_mapping=True)
    ends = [e for s, e in enc["offset_mapping"] if e > 0]
    cut = max(ends) if ends else 0
    start = len(full) - len(evidence)
    return full[start:cut] if cut > start else ""


def reach_rows(pairs, ids_for, chunks, tok):
    out = []
    for p in pairs:
        a, b = p["ood_drug"], p["semeval_drug"]
        ids = (ids_for.get(f"{a}|||{b}") or ids_for.get(f"{b}|||{a}") or [])[:K]
        cs = [chunks[i] for i in ids]
        texts = [c["text"] for c in cs]
        full, evidence = model_input(a, b, texts)
        seen = visible_evidence(tok, full, evidence)
        di = [c for c in cs if c["section"] == config.HOLDOUT_SECTION and c["drug"] == a]
        own = [c for c in cs if c["drug"] == a]
        out.append({"y": int(p["label"]), "g": a, "q": b, "n_chunks": len(cs),
                    "di_chunk_of_ood_drug": bool(di),
                    "partner_in_full_chunks": any(named(b, t) for t in texts),
                    "partner_in_first400": any(named(b, t[:CHARS]) for t in texts),
                    "partner_in_512_tokens": named(b, seen),
                    "partner_in_di_chunk_first400": any(named(b, c["text"][:CHARS]) for c in di),
                    "own_label_chunk_retrieved": bool(own),
                    "partner_in_own_label_chunk": any(named(b, c["text"]) for c in own),
                    "partner_in_own_label_first400": any(named(b, c["text"][:CHARS]) for c in own),
                    "truncated": len(seen) < len(evidence)})
    return out


FIELDS = ("di_chunk_of_ood_drug", "partner_in_full_chunks", "partner_in_first400", "partner_in_512_tokens",
          "partner_in_di_chunk_first400", "own_label_chunk_retrieved", "partner_in_own_label_chunk",
          "partner_in_own_label_first400")


def summarize(rows, boot):
    y = np.array([r["y"] for r in rows])
    g = np.array([r["g"] for r in rows])
    q = np.array([r["q"] for r in rows])
    res = {"n": int(len(y)), "n_pos": int(y.sum()), "n_neg": int((1 - y).sum()),
           "inputs_truncated_at_512": int(sum(r["truncated"] for r in rows)), "features": {}}
    feats = {f: np.array([float(r[f]) for r in rows]) for f in FIELDS}
    draws = paired_draws(y, [feats[f] for f in FIELDS], g, q, boot, BOOT_SEED["novel"])
    for i, f in enumerate(FIELDS):
        s = feats[f]
        pb = s.astype(int)
        lo, hi = ev.interval(ev.boot_auroc(y, s, g, q, boot))
        res["features"][f] = {"positives": int(s[y == 1].sum()), "negatives": int(s[y == 0].sum()),
                              "share_pos": float(s[y == 1].mean()), "share_neg": float(s[y == 0].mean()),
                              "rule_auroc_pooled": ev.auroc(y, s), "rule_auroc_pooled_ci95": [lo, hi],
                              "rule_auroc_within": summarize_draws(stats.stratified_auroc(y, s, g), draws[i]),
                              "rule_mcc": extended(y, pb)["mcc"]}
    return res


def training_table(test_y):
    rows = []
    for s in SEEDS:
        for job in (f"krag-contaminated-k5-c400-biomedbert-s{s}", f"krag-hybrid-k5-c400-biomedbert-s{s}",
                    f"b1names-biomedbert-s{s}"):
            f = PREDS / f"{job}.json"
            if not f.exists():
                continue
            r = json.loads(f.read_text())
            key = "test" if "test" in r["eval"] else "test_names"
            h = r.get("history") or {}
            rows.append({"job": job, "seed": s, "semeval_test_auroc": ev.auroc(np.asarray(test_y), r["eval"][key]["p"]),
                         "best_epoch": h.get("best_epoch"), "max_epochs": r["config"]["epochs"],
                         "best_val_macro_f1": h.get("best_val_macro_f1")})
    return rows



def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--boot", type=int, default=1000)
    a = ap.parse_args()
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(config.ENCODER, local_files_only=True)
    bundle = json.load(gzip.open(ROOT / "artifacts" / "bundle" / "inputs.json.gz", "rt"))
    chunks = json.loads((config.ARTIFACTS / "index" / "all_chunks.json").read_text())
    for cid, txt in bundle["chunk_text"].items():
        if chunks[int(cid)]["text"] != txt:
            raise ValueError(f"chunk {cid} text differs between the bundle and all_chunks.json")
    truth = ev.load_truth()
    indexed = {c["drug"] for c in chunks}
    older = sorted({r["ood_drug"] for r in bundle["ood_old_pairs"]})
    older_indexed = [d for d in older if d in indexed]
    pairs = bundle["ood_pairs"]
    if [int(p["label"]) for p in pairs] != list(truth.sets["ood"]["y"]):
        raise ValueError("bundle Novel pairs differ from the evaluation truth")
    out = {"status": "Amendment 7 experiment 6, exploratory, post hoc",
           "method": "top 5 chunk ids from artifacts/bundle/inputs.json.gz; model input rebuilt as ddiood.inputs.krag "
                     "(names, then the first 400 characters of each chunk) and truncated with the BiomedBERT tokenizer at 512 "
                     "tokens; partner matched case-insensitively at word boundaries as in ddiood.inputs.mask_names, only in the "
                     "evidence part (not the leading drug names); rule AUROC within drug with a two-way cluster bootstrap "
                     "(1,000 draws, seed 1042), pooled AUROC with the same two-way bootstrap, MCC of the binary rule",
           "variants": {},
           "older": {"status": "not available" if not older_indexed else "partly indexed",
                     "n_older_drugs": len(older), "n_older_drugs_in_index": len(older_indexed),
                     "note": "Older drugs have no chunks in the retrieval index, so no retrieval-based statistic is computed for Older; nothing falls back to names only"}}
    md = ["# Experiment 6: what the failed positive control could see (Novel, n = 438)", "",
          f"Older cohort: {out['older']['status']} ({out['older']['n_older_drugs_in_index']} of {out['older']['n_older_drugs']} "
          "Older drugs have chunks in the retrieval index).", "",
          "`partner_in_own_label_*` is a construction leak: a retrieved passage from the OOD drug's own label names the partner. "
          "Negatives are built from partners the drug's label never names, so this rule cannot fire on a negative and any "
          "positive it reaches is answered by construction.", ""]
    for v in VARIANTS:
        rows = reach_rows(pairs, bundle["retrieval"][v], chunks, tok)
        s = summarize(rows, a.boot)
        out["variants"][v] = s
        md += [f"## {v} index", "", f"n = {s['n']} ({s['n_pos']} positive, {s['n_neg']} negative); "
               f"{s['inputs_truncated_at_512']} inputs truncated at 512 tokens.", "",
               "| feature | positives | negatives | share pos | share neg | rule AUROC within | 95% CI | rule AUROC pooled | 95% CI | MCC |",
               "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
        for f, r in s["features"].items():
            w = r["rule_auroc_within"]
            md.append(f"| {f} | {r['positives']} | {r['negatives']} | {f3(r['share_pos'])} | {f3(r['share_neg'])} | "
                      f"{f3(w['value'])} | {ci(w['ci95'])} | {f3(r['rule_auroc_pooled'])} | {ci(r['rule_auroc_pooled_ci95'])} | {f3(r['rule_mcc'])} |")
        md.append("")
    t = training_table(truth.test_y)
    out["training"] = t
    md += ["## SemEval test AUROC and best epoch per seed", "", "| job | seed | SemEval test AUROC | best epoch | max epochs | best val macro F1 |",
           "| --- | --- | --- | --- | --- | --- |"]
    md += [f"| {r['job']} | {r['seed']} | {f3(r['semeval_test_auroc'])} | {r['best_epoch']} | {r['max_epochs']} | {f3(r['best_val_macro_f1'])} |" for r in t]
    write("exp6_control_reach", out, "\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
