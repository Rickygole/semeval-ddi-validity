import argparse
import gzip
import json

import numpy as np

from sens_common import ROOT, ci, ev, f3, write
import amend7_cpu_exp6_control_reach as e6
from amend7_cpu_common import BOOT_SEED, paired_draws, stats, summarize_draws
from ddiood import config
from ddiood.metrics import extended

SEP = " [SEP] "


def visible_segments(a, b, cs, tok):
    texts = [c["text"] for c in cs]
    full, evidence = e6.model_input(a, b, texts)
    seen = e6.visible_evidence(tok, full, evidence)
    out, pos = [], 0
    for c in cs:
        t = c["text"][:e6.CHARS]
        out.append((c, seen[pos:pos + len(t)]))
        pos += len(t) + len(SEP)
    return seen, out


def reader_rows(pairs, ids_for, chunks, tok):
    rows = []
    for p in pairs:
        a, b = p["ood_drug"], p["semeval_drug"]
        ids = (ids_for.get(f"{a}|||{b}") or ids_for.get(f"{b}|||{a}") or [])[:e6.K]
        cs = [chunks[i] for i in ids]
        seen, segs = visible_segments(a, b, cs, tok)
        rows.append({"y": int(p["label"]), "g": a, "q": b,
                     "partner_visible": e6.named(b, seen) if seen else False,
                     "partner_visible_own_label": any(e6.named(b, s) for c, s in segs if s and c["drug"] == a)})
    return rows


def score_summary(y, g, q, s, boot, draws):
    lo, hi = ev.interval(ev.boot_auroc(y, s, g, q, boot))
    return {"auroc_within": summarize_draws(stats.stratified_auroc(y, s, g), draws),
            "auroc_pooled": ev.auroc(y, s), "auroc_pooled_ci95": [lo, hi],
            "positives_scored_up": int(((s > 0) & (y == 1)).sum()),
            "negatives_scored_up": int(((s > 0) & (y == 0)).sum()),
            "negatives_scored_down": int(((s < 0) & (y == 0)).sum()),
            "mcc_of_score_above_zero": extended(y, (s > 0).astype(int))["mcc"]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--boot", type=int, default=1000)
    a = ap.parse_args()
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(config.ENCODER, local_files_only=True)
    bundle = json.load(gzip.open(ROOT / "artifacts" / "bundle" / "inputs.json.gz", "rt"))
    chunks = json.loads((config.ARTIFACTS / "index" / "all_chunks.json").read_text())
    pairs = bundle["ood_pairs"]
    truth = ev.load_truth()
    if [int(p["label"]) for p in pairs] != list(truth.sets["ood"]["y"]):
        raise ValueError("bundle Novel pairs differ from the evaluation truth")
    exp6 = json.loads((ROOT / "results" / "revision" / "amend7" / "cpu" / "exp6_control_reach.json").read_text())
    out = {"status": "sensitivity analysis, post hoc, exploratory; changes no preregistered decision",
           "source": "H5 input rebuilt with the functions of scripts/amend7_cpu_exp6_control_reach.py "
                     "(contaminated retrieval, k 5, first 400 characters per passage, BiomedBERT tokenizer truncation at 512 tokens)",
           "readers": {
               "partner_visibility_rule": "1 if the partner is named in the visible evidence, else 0 (exp6 partner_in_512_tokens)",
               "ideal_reader": "+1 if the partner is named in the visible evidence and the pair is positive, -1 if it is named and "
                               "the pair is negative, 0 if it is not named. This grants a perfect judge of whether a visible mention "
                               "is an interaction statement: every visible positive mention is taken as one and no visible negative "
                               "mention is. It uses the labels, so it is an upper bound for a reader of this input, not a rule.",
               "source_proxy_reader": "+1 if the partner is named in the visible part of a passage from the OOD drug's own label, -1 if "
                                      "it is named only in other visible passages, 0 if it is not named. Label free; it treats an "
                                      "own-label mention as the interaction statement."},
           "boot": a.boot, "boot_seed_within": BOOT_SEED["novel"], "variants": {}}
    md = ["# Positive control (H5): what an ideal reader of the H5 input reaches", "",
          "Sensitivity analysis, post hoc. Novel cohort, n = 438. Within-drug AUROC with the two-way cluster bootstrap "
          f"({a.boot} draws, seed {BOOT_SEED['novel']}); pooled AUROC with the two-way bootstrap of `ddiood.evaluate2`.", "",
          "The ideal reader uses the labels: it scores a visible partner mention up for positives and down for negatives, "
          "which is what a perfect judge of interaction statements would do if every visible positive mention stated the "
          "interaction. It is an upper bound for this input. The source proxy is the label-free version that treats a "
          "mention in the OOD drug's own label as the interaction statement.", ""]
    for v in ("contaminated", "hybrid"):
        rows = reader_rows(pairs, bundle["retrieval"][v], chunks, tok)
        y = np.array([r["y"] for r in rows])
        g = np.array([r["g"] for r in rows])
        q = np.array([r["q"] for r in rows])
        vis = np.array([r["partner_visible"] for r in rows], float)
        own = np.array([r["partner_visible_own_label"] for r in rows], float)
        scores = {"partner_visibility_rule": vis,
                  "ideal_reader": vis * (2 * y - 1),
                  "source_proxy_reader": np.where(own > 0, 1.0, np.where(vis > 0, -1.0, 0.0))}
        names = list(scores)
        draws = paired_draws(y, [scores[k] for k in names], g, q, a.boot, BOOT_SEED["novel"])
        res = {"n": int(len(y)), "n_pos": int(y.sum()), "n_neg": int((1 - y).sum()),
               "positives_partner_visible": int(vis[y == 1].sum()), "negatives_partner_visible": int(vis[y == 0].sum()),
               "positives_partner_visible_own_label": int(own[y == 1].sum()),
               "negatives_partner_visible_own_label": int(own[y == 0].sum()), "readers": {}}
        for i, k in enumerate(names):
            res["readers"][k] = score_summary(y, g, q, scores[k], a.boot, draws[i])
        ref = exp6["variants"][v]["features"]["partner_in_512_tokens"]
        mine = res["readers"]["partner_visibility_rule"]
        res["matches_exp6_partner_in_512_tokens"] = bool(
            ref["positives"] == res["positives_partner_visible"] and ref["negatives"] == res["negatives_partner_visible"]
            and round(mine["auroc_within"]["value"], 6) == ref["rule_auroc_within"]["value"]
            and round(mine["auroc_pooled"], 6) == ref["rule_auroc_pooled"])
        out["variants"][v] = res
        md += [f"## {v} index", "",
               f"Partner visible after truncation: {res['positives_partner_visible']} of {res['n_pos']} positives, "
               f"{res['negatives_partner_visible']} of {res['n_neg']} negatives; in a visible own-label passage: "
               f"{res['positives_partner_visible_own_label']} positives, {res['negatives_partner_visible_own_label']} negatives. "
               f"Visibility rule equals exp6 `partner_in_512_tokens`: {res['matches_exp6_partner_in_512_tokens']}.", "",
               "| reader | AUROC within | 95% CI | AUROC pooled | 95% CI | MCC (score > 0) |", "| --- | --- | --- | --- | --- | --- |"]
        for k in names:
            r = res["readers"][k]
            md.append(f"| {k} | {f3(r['auroc_within']['value'])} | {ci(r['auroc_within']['ci95'])} | {f3(r['auroc_pooled'])} | "
                      f"{ci(r['auroc_pooled_ci95'])} | {f3(r['mcc_of_score_above_zero'])} |")
        md.append("")
    md += ["The H5 thresholds are Novel pooled AUROC 0.75 and MCC 0.30. The trained control reached 0.621 and 0.167 (`results/revision/eval/decisions.md`).", ""]
    write("control_ideal_reader", out, "\n".join(md))
    print("\n".join(md))


if __name__ == "__main__":
    main()
