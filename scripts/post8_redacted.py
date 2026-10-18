import argparse
import json

import numpy as np

import post8_common as pc
from ddiood import amend7_analysis as aa
from ddiood import amend7_evidence as aev
from ddiood import amend7_prompts as pr
from ddiood import inputs

QWEN = "Qwen/Qwen2.5-7B-Instruct"


def build_lengths(rows, tok):
    sections = json.loads((pc.AMEND7 / "di_sections.json").read_text())
    lookup = json.loads((pc.AMEND7 / "lookup.json").read_text())
    out = {}
    for c, tag in (("novel", "ood"), ("older", "oodold")):
        pairs = inputs.ood_as_pairs(rows[c])
        drugs = sorted({p["drug_a"] for p in pairs})
        di = {d: sections[d]["text"] for d in drugs}
        b = aev.EvidenceBuilder(tok, di, lookup, {}, {}, drugs)
        rec = {k: [] for k in ("tok_red", "tok_full", "chr_red", "chr_full", "prompt_red", "prompt_full", "trunc_red")}
        for p in pairs:
            er, mr = b.evidence("redacted", p["drug_a"], p["drug_b"])
            ef, mf = b.evidence("oracle", p["drug_a"], p["drug_b"])
            rec["tok_red"].append(len(tok(er, add_special_tokens=False)["input_ids"]))
            rec["tok_full"].append(len(tok(ef, add_special_tokens=False)["input_ids"]))
            rec["chr_red"].append(len(er))
            rec["chr_full"].append(len(ef))
            rec["trunc_red"].append(int(mr.get("truncated", False)))
            rec["prompt_red"].append(len(tok(pr.chat(tok, pr.evidence_prompt(er, p["drug_a"], p["drug_b"])), add_special_tokens=False)["input_ids"]))
            rec["prompt_full"].append(len(tok(pr.chat(tok, pr.evidence_prompt(ef, p["drug_a"], p["drug_b"])), add_special_tokens=False)["input_ids"]))
        out[tag] = {k: np.asarray(v) for k, v in rec.items()}
    return out


def check(lengths):
    res = {}
    for job, key in (("a7-qwen-redactedoracle", "prompt_red"), ("a7-qwen-oracle", "prompt_full")):
        r = json.loads((pc.PREDS / f"{job}.json").read_text())
        for tag in ("ood", "oodold"):
            mine = float(lengths[tag][key].mean())
            ref = r["answer"][tag]["tokens_mean"]
            res[f"{job}/{tag}"] = {"reconstructed_tokens_mean": mine, "recorded_tokens_mean": ref,
                                   "reconstructed_tokens_max": int(lengths[tag][key].max()), "recorded_tokens_max": r["answer"][tag]["tokens_max"],
                                   "match": bool(abs(mine - ref) <= 0.01)}
    if not all(v["match"] for v in res.values()):
        raise SystemExit(f"redacted reconstruction does not reproduce the recorded prompt lengths: {res}")
    return res


def by_class(c, L):
    y = c["y"]
    m = c["mask"]
    tr, tf, cr = L["tok_red"][m], L["tok_full"][m], L["chr_red"][m]
    removed = tf - tr
    out = {}
    for lab, name in ((1, "positives"), (0, "negatives")):
        k = y == lab
        out[name] = {"n": int(k.sum()), "tokens_mean": float(tr[k].mean()), "tokens_median": float(np.median(tr[k])),
                     "chars_mean": float(cr[k].mean()), "tokens_removed_mean": float(removed[k].mean()),
                     "tokens_removed_median": float(np.median(removed[k])), "share_with_tokens_removed": float((removed[k] > 0).mean())}
    g = c["g"]
    per = []
    for d in np.unique(g):
        k = g == d
        pos, neg = k & (y == 1), k & (y == 0)
        if pos.any() and neg.any():
            per.append(float(tr[neg].mean() - tr[pos].mean()))
    per = np.asarray(per)
    out["per_drug_neg_minus_pos_tokens"] = {"n_drugs": int(len(per)), "mean": float(per.mean()), "median": float(np.median(per)),
                                            "min": float(per.min()), "max": float(per.max()), "share_positive": float((per > 0).mean()),
                                            "share_zero": float((per == 0).mean())}
    return out


def cohort_rows(truth, L, qwen, n):
    out = {}
    for cname in ("novel", "older_primary"):
        c = truth.cohort(cname)
        tag = c["tag"]
        length_score = -L[tag]["tok_red"][c["mask"]].astype(float)
        q = qwen[tag][c["mask"]]
        out[cname] = {"by_class": by_class(c, L[tag]), "length_only_within": aa.estimate(c, length_score, n),
                      "qwen_redacted_within": aa.estimate(c, q, n), "qwen_minus_length": aa.paired(c, q, length_score, n),
                      "n": int(len(c["y"])), "n_pos": int(c["y"].sum())}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--boot", type=int, default=1000)
    a = ap.parse_args()
    from transformers import AutoTokenizer
    crit, rows, rule, screens = pc.screens_for_run()
    tok = AutoTokenizer.from_pretrained(QWEN, local_files_only=True)
    L = build_lengths(rows, tok)
    checks = check(L)
    base, _, _ = pc.a7_truth()
    r = json.loads((pc.PREDS / "a7-qwen-redactedoracle.json").read_text())
    for tag, field in (("ood", "ood_hash"), ("oodold", "ood_old_hash")):
        if r[field] != base.sets[tag]["hash"]:
            raise ValueError("redacted oracle row order does not match the frozen sets")
    qwen = {tag: np.asarray(r["eval"][tag]["p"], float) for tag in ("ood", "oodold")}
    tiers = {"A": base, "C-auto": pc.TruthC(base, pc.keep_masks(screens))}
    out = {"status": pc.STATUS, "reconstruction_check": checks, "boot": a.boot,
           "truncated_redacted": {tag: int(L[tag]["trunc_red"].sum()) for tag in L},
           "tiers": {t: cohort_rows(tr, L, qwen, a.boot) for t, tr in tiers.items()}}
    Lm = ["# Redacted-oracle context-length confound (post hoc, exploratory)", "", f"Status: {pc.STATUS}.", "",
          "The redacted evidence of every row was rebuilt with ddiood.amend7_evidence.EvidenceBuilder from artifacts/amend7/di_sections.json and the Qwen tokenizer; "
          "the mean prompt token counts reproduce the recorded answer.tokens_mean of a7-qwen-redactedoracle.json and a7-qwen-oracle.json:", ""]
    for k, v in checks.items():
        Lm.append(f"- {k}: reconstructed {v['reconstructed_tokens_mean']:.4f}, recorded {v['recorded_tokens_mean']:.4f}, max {v['reconstructed_tokens_max']} vs {v['recorded_tokens_max']}")
    for t, coh in out["tiers"].items():
        Lm += ["", f"## Tier {t}", "", "| cohort | class | n | evidence tokens mean | median | tokens removed mean | median | share with tokens removed |", "| --- | --- | --- | --- | --- | --- | --- | --- |"]
        for cname, v in coh.items():
            for cls in ("positives", "negatives"):
                b = v["by_class"][cls]
                Lm.append(f"| {cname} | {cls} | {b['n']} | {b['tokens_mean']:.1f} | {b['tokens_median']:.1f} | {b['tokens_removed_mean']:.1f} | {b['tokens_removed_median']:.1f} | {b['share_with_tokens_removed']:.3f} |")
        Lm += ["", "| cohort | per-drug mean neg minus pos tokens: mean | median | share of drugs > 0 | length-only within-drug AUROC | 95% CI | Qwen redacted within-drug AUROC | 95% CI | Qwen minus length | 95% CI |",
               "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
        for cname, v in coh.items():
            p = v["by_class"]["per_drug_neg_minus_pos_tokens"]
            l, q, d = v["length_only_within"], v["qwen_redacted_within"], v["qwen_minus_length"]
            Lm.append(f"| {cname} | {p['mean']:.1f} | {p['median']:.1f} | {p['share_positive']:.3f} | {pc.f3(l['value'])} | {pc.ci(l['lo95'], l['hi95'])} | "
                      f"{pc.f3(q['value'])} | {pc.ci(q['lo95'], q['hi95'])} | {pc.f3(d['value'])} | {pc.ci(d['lo95'], d['hi95'])} |")
    Lm += ["", "Length-only score: minus the Qwen token count of the redacted evidence, so a shorter context ranks higher. Two-way bootstrap, Novel seed 1042, Older-primary seed 42."]
    pc.write("redacted_confound", out, "\n".join(Lm) + "\n")
    print("\n".join(Lm[-12:]))


if __name__ == "__main__":
    main()
