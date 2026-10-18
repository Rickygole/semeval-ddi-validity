import gzip
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ddiood import amend7_evidence as ev
from ddiood import amend7_inputs as ai
from ddiood import amend7_pairs as ap
from ddiood import amend7_prompts as pr
from ddiood import config, inputs, stats
from ddiood.openfda import LabelStore
from ddiood.pipeline import _novel_label
from ddiood.textnorm import normalize

OUT = ROOT / "artifacts" / "amend7"
CPU = OUT / "preds_cpu"
OLDER_ARTIFACTS = ("almotriptan malate", "atazanavir sulfate", "atorvastatin calcium", "citalopram hydrobromide",
                   "darifenacin hydrobromide", "rosuvastatin calcium", "benzoate")
OLDER_MISSED = ("clopidogrel bisulfate", "perindopril erbumine", "peginterferon alfa-2a", "calcitonin", "esmolol",
                "toremifene citrate", "trospium chloride")
SHINGLE = 8
SHINGLE_SHARE = 0.3
R_FLOOR = 0.95


def shingles(text, n=SHINGLE):
    w = normalize(text).split()
    return {" ".join(w[i:i + n]) for i in range(max(len(w) - n + 1, 0))}


def auc_within(y, s, g):
    return float(stats.stratified_auroc(np.asarray(y), np.asarray(s, float), np.asarray(g)))


def write_pred(name, system, variant, ood_hash, old_hash, evals, extra=None):
    cfg = {"kind": "cpu", "system": system, "model": "rule", "seed": 0, "priority": 0, "split": "standard",
           "epochs": 0, "variant": variant, "k": 5, "chars": 0, "name": name}
    res = {"config": cfg, "config_hash": hashlib.sha256(json.dumps(cfg, sort_keys=True).encode()).hexdigest(),
           "smoke": False, "ood_hash": ood_hash, "ood_old_hash": old_hash, "eval": evals, "seconds": 0.0}
    if extra:
        res.update(extra)
    CPU.mkdir(parents=True, exist_ok=True)
    (CPU / f"{name}.json").write_text(json.dumps(res))


def main():
    from transformers import AutoTokenizer
    if CPU.exists():
        for old_file in CPU.glob("a7-*.json"):
            old_file.unlink()
    lookup = json.loads((config.ARTIFACTS / "vocab" / "drug_lookup.json").read_text())
    ood = ap.read_csv(ROOT / "results" / "corrected" / "ood_pairs.csv")
    old = ap.read_csv(ROOT / "results" / "corrected" / "ood_old_pairs.csv")
    novel_pairs, old_pairs = inputs.ood_as_pairs(ood), inputs.ood_as_pairs(old)
    ood_hash, old_hash = inputs.pairs_hash(novel_pairs), inputs.pairs_hash(old_pairs)
    train = ap.read_rows(OUT / "train_pairs.csv")
    store = LabelStore(offline=True)
    full = json.load(gzip.open(OUT / "retrieval_full.json.gz", "rt"))
    caches, text = full["retrieval"], full["chunk_text"]
    meta = json.loads((OUT / "retrieval.json").read_text())["chunk_meta"]
    bert_tok = AutoTokenizer.from_pretrained(config.ENCODER)
    qwen_tok = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-7B-Instruct")

    excluded_older = set(OLDER_ARTIFACTS) | set(OLDER_MISSED)
    novel_drugs = sorted({p["drug_a"] for p in novel_pairs})
    older_drugs = sorted({p["drug_a"] for p in old_pairs})
    older_primary_drugs = [d for d in older_drugs if d not in excluded_older]
    old_primary_mask = np.array([p["drug_a"] not in excluded_older for p in old_pairs])
    old_clean_mask = np.array([p["drug_a"] not in OLDER_ARTIFACTS for p in old_pairs])
    cohorts = {"novel": (novel_pairs, np.ones(len(novel_pairs), bool)),
               "older_primary": (old_pairs, old_primary_mask), "older_clean": (old_pairs, old_clean_mask)}

    di, vocab_di = {}, {}
    for d in novel_drugs + older_drugs:
        label = _novel_label(store, d)
        di[d] = ev.di_section(label)
    for k, v in lookup.items():
        label = store.get(v["normalized"])
        if label:
            t = ev.di_section(label)
            if t:
                vocab_di[k] = t
    pool = set()
    for t in vocab_di.values():
        pool |= shingles(t)
    share = {}
    for d in novel_drugs + older_drugs:
        sh = shingles(di[d])
        share[d] = len(sh & pool) / len(sh) if sh else 0.0
    shingle_flagged = sorted(d for d, s in share.items() if s > SHINGLE_SHARE)
    affected = json.loads((OUT / "train_pairs_report.json").read_text())["audit"]["ood_drugs_with_equivalent_vocab_drug"]
    flagged = sorted(set(shingle_flagged) | set(affected))
    sens = {"shingle_only": shingle_flagged, "equivalent_vocab_drug": affected, "rule": f"share of the drug's {SHINGLE}-word Drug Interactions shingles found in any vocabulary drug's section exceeds {SHINGLE_SHARE}",
            "novel": [d for d in flagged if d in novel_drugs],
            "older_clean": [d for d in flagged if d in older_drugs and d not in OLDER_ARTIFACTS],
            "older_primary": [d for d in flagged if d in older_drugs and d not in excluded_older],
            "older_primary_equivalent_only": [d for d in affected if d in older_drugs and d not in excluded_older and d not in shingle_flagged],
            "share": {d: round(share[d], 4) for d in flagged}, "vocab_sections": len(vocab_di)}

    names = ev.build_name_set(config.FDA_LABEL_DIR, extra=list(lookup) + novel_drugs + older_drugs +
                              [v["normalized"] for v in lookup.values()])
    sections = {d: {"text": di[d], "masked": ev.mask_names(di[d], names)} for d in di}
    (OUT / "di_sections.json").write_text(json.dumps(sections))
    (OUT / "drug_names.json").write_text(json.dumps(sorted(" ".join(t) for t in names)))
    (OUT / "lookup.json").write_text(json.dumps({k: {x: v[x] for x in ("normalized", "canonicalized", "rxcui")}
                                                 for k, v in lookup.items()}))
    lk = json.loads((OUT / "lookup.json").read_text())

    taken = set(lk) | {v["normalized"] for v in lk.values()} | {" ".join(t) for t in names} | set(di)
    stems = {}
    for d in novel_drugs + older_primary_drugs:
        r = ev.stem_names_for(d, taken, qwen_tok)
        if r:
            stems[d] = r
            taken |= {r["preserved"], r["scrambled"]}
    stem_report = {"stems": stems, "stem_list_sha256": hashlib.sha256(json.dumps(ev.STEMS).encode()).hexdigest(),
                   "stem_list_size": len(ev.STEMS),
                   "drugs_with_stem": {"novel": sum(d in stems for d in novel_drugs),
                                       "older_primary": sum(d in stems for d in older_primary_drugs)},
                   "drugs_total": {"novel": len(novel_drugs), "older_primary": len(older_primary_drugs)}}
    (OUT / "stem_names.json").write_text(json.dumps(stem_report, indent=1))

    sets = {"older_artifacts": list(OLDER_ARTIFACTS), "older_missed_vocabulary_drugs": list(OLDER_MISSED),
            "rows": {"older_total": len(old_pairs), "older_clean": int(old_clean_mask.sum()),
                     "older_primary": int(old_primary_mask.sum())},
            "novel_rows": len(novel_pairs), "sensitivity_shingle": sens}
    (OUT / "primary_sets.json").write_text(json.dumps(sets, indent=1))

    fixed = ai.FixedBuilder(lk, text, meta)
    cohort_rows = {"novel": novel_pairs, "older": old_pairs}

    def arm_cache(group, arm):
        return caches[group][arm]

    def own_label_rule(arm):
        res, evals_own = {}, {}
        for coh, rows in (("novel", novel_pairs), ("older", old_pairs)):
            cache = arm_cache(coh, arm)
            hit = []
            for p in rows:
                forms = fixed.forms(p["drug_b"])
                ids = cache[f"{p['drug_a']}|||{p['drug_b']}"][:5]
                hit.append(int(any(meta[str(i)][0] == p["drug_a"] and ev.grep_hit(text[str(i)], forms) for i in ids)))
            hit = np.array(hit)
            y = np.array([p["y"] for p in rows])
            g = np.array([p["drug_a"] for p in rows])
            mask = old_primary_mask if coh == "older" else np.ones(len(rows), bool)
            res[coh] = {"positives_hit": int(hit[mask & (y == 1)].sum()), "positives": int((mask & (y == 1)).sum()),
                        "negatives_hit": int(hit[mask & (y == 0)].sum()), "negatives": int((mask & (y == 0)).sum()),
                        "grep_auroc_within": auc_within(y[mask], hit[mask], g[mask])}
            evals_own["ood" if coh == "novel" else "oodold"] = {"preds": hit.tolist(), "p": hit.astype(float).tolist()}
        write_pred(f"a7-grep-ownlabel-answer-{arm}", "a7_grep_ownlabel", arm, ood_hash, old_hash, evals_own)
        return res

    arms_enc = {"e7a_h5_contaminated": ("contaminated", "h5"), "e7b_fixed_ownlabel": ("ownlabel", "fixed"),
                "e7b_alt_fixed_global_contaminated": ("contaminated", "fixed"),
                "e7d_fixed_other": ("other", "fixed"), "e7e_fixed_clean": ("clean", "fixed")}
    audit = {"prompts_frozen_sha256": pr.frozen_hash(), "window_chars": ai.WINDOW_CHARS, "h5_chars": ai.H5_CHARS,
             "labels_snapshot": json.loads((OUT / "train_pairs_report.json").read_text())["audit"]["snapshot_ood_labels"],
             "encoder_arms": {}, "own_label_names_partner": {}}
    grep_evals = {}
    for arm, (cname, fmt) in arms_enc.items():
        audit["encoder_arms"][arm] = {}
        evals = {}
        for coh, key in (("novel", "ood"), ("older", "oodold")):
            rows = cohort_rows[coh]
            cache = arm_cache(coh, cname)
            texts = (ai.krag_h5(rows, cache, text) if fmt == "h5" else fixed.encoder_inputs(rows, cache))
            hits, trunc = ai.reachability(bert_tok, texts, rows, fixed)
            hits = np.array(hits)
            y = np.array([p["y"] for p in rows])
            g = [p["drug_a"] for p in rows]
            res = {"truncated_inputs": trunc, "n": len(rows)}
            for cname2, (_c, mask) in cohorts.items():
                if (cname2 == "novel") != (coh == "novel"):
                    continue
                m = mask
                res[cname2] = {"R_positives_with_partner_in_seen_text": float(hits[m & (y == 1)].mean()),
                               "negatives_with_partner_in_seen_text": float(hits[m & (y == 0)].mean()),
                               "grep_auroc_within": auc_within(y[m], hits[m], np.array(g)[m]),
                               "grep_auroc_pooled": float(stats.auroc(y[m], hits[m]))}
            audit["encoder_arms"][arm][coh] = res
            evals[key] = {"preds": hits.tolist(), "p": hits.astype(float).tolist()}
        grep_evals[arm] = evals
        write_pred(f"a7-grep-{arm}", "a7_grep", arm, ood_hash, old_hash, evals)
        if cname not in audit["own_label_names_partner"]:
            audit["own_label_names_partner"][cname] = own_label_rule(cname)

    r_nov = audit["encoder_arms"]["e7b_fixed_ownlabel"]["novel"]["novel"]["R_positives_with_partner_in_seen_text"]
    r_old = audit["encoder_arms"]["e7b_fixed_ownlabel"]["older"]["older_primary"]["R_positives_with_partner_in_seen_text"]
    train_hits, train_trunc = ai.reachability(
        bert_tok, fixed.encoder_inputs(train, caches["train"]["ownlabel"]), train, fixed)
    ty = np.array([p["y"] for p in train])
    audit["e7b_train_reachability"] = {"R_positives": float(np.array(train_hits)[ty == 1].mean()),
                                       "negatives_with_partner": float(np.array(train_hits)[ty == 0].mean()),
                                       "truncated_inputs": train_trunc, "n": len(train)}
    thr = lambda r: max(0.75, 0.5 + 0.8 * (r - 0.5))
    audit["e7b_rule"] = {"R_novel": r_nov, "R_older_primary": r_old, "threshold_novel": thr(r_nov),
                         "threshold_older_primary": thr(r_old), "R_floor": R_FLOOR,
                         "assertion_R_at_least_floor": bool(r_nov >= R_FLOOR and r_old >= R_FLOOR),
                         "lower_bound_floor": 0.70}

    audit["qwen_arms"] = {}
    for cond in ("oracle", "masked", "wrong", "redacted", "contam", "other", "clean"):
        audit["qwen_arms"][cond] = {}
        evals = {}
        for coh, key in (("novel", "ood"), ("older", "oodold")):
            rows = cohort_rows[coh]
            drugs = novel_drugs if coh == "novel" else older_drugs
            di_text = {d: (sections[d]["masked"] if cond == "masked" else sections[d]["text"]) for d in drugs}
            ctx = ev.EvidenceBuilder(qwen_tok, di_text, lk, {"contaminated": caches[coh]["contaminated"],
                                                             "hybrid": caches[coh]["clean"]}, text, drugs, excluded_older)
            hits, toks, cut = [], [], 0
            for p in rows:
                e, m = ai.qwen_evidence(cond, p, ctx, fixed, caches[coh])
                cut += int(m.get("truncated", False))
                prompt = pr.chat(qwen_tok, pr.evidence_prompt(e, p["drug_a"], p["drug_b"]))
                toks.append(len(qwen_tok(prompt, add_special_tokens=False)["input_ids"]))
                hits.append(ev.grep_hit(e, fixed.forms(p["drug_b"])))
            hits = np.array(hits)
            y = np.array([p["y"] for p in rows])
            g = np.array([p["drug_a"] for p in rows])
            entry = {"truncated_evidence": cut, "tokens_mean": float(np.mean(toks)), "tokens_max": int(max(toks)),
                     "prompts_over_limit": int(sum(t > pr.MAX_PROMPT_TOKENS for t in toks)), "n": len(rows)}
            for cname2, (_c, mask) in cohorts.items():
                if (cname2 == "novel") != (coh == "novel"):
                    continue
                entry[cname2] = {"positives_with_partner_in_context": float(hits[mask & (y == 1)].mean()),
                                 "negatives_with_partner_in_context": float(hits[mask & (y == 0)].mean()),
                                 "grep_auroc_within": auc_within(y[mask], hits[mask], g[mask]),
                                 "grep_auroc_pooled": float(stats.auroc(y[mask], hits[mask]))}
            audit["qwen_arms"][cond][coh] = entry
            evals[key] = {"preds": hits.tolist(), "p": hits.astype(float).tolist()}
        write_pred(f"a7-grep-qwen-{cond}", "a7_grep_qwen", cond, ood_hash, old_hash, evals)

    pos_n = Counter()
    neg_n = Counter()
    for r in train:
        (pos_n if r["y"] else neg_n)[r["drug_b"]] += 1
    prior = lambda b: (pos_n[b] + 1) / (pos_n[b] + neg_n[b] + 2)
    evals = {}
    for key, rows in (("ood", novel_pairs), ("oodold", old_pairs)):
        p = [prior(r["drug_b"]) for r in rows]
        evals[key] = {"preds": [int(x > 1 / 3) for x in p], "p": [round(x, 6) for x in p]}
    write_pred("a7-prior-partner-train", "a7_prior", "partner_train", ood_hash, old_hash, evals)

    db = {}
    for coh, rows, f in (("novel", novel_pairs, "drugbank_validation.csv"), ("older", old_pairs, "drugbank_validation_old.csv")):
        r = ap.read_csv(config.ARTIFACTS / "ood" / f)
        idx = {(x["ood_drug"], x["semeval_drug"]): x["drugbank_label"] for x in r}
        s = np.array([1.0 if idx.get((p["drug_a"], p["drug_b"])) == "positive" else 0.0 for p in rows])
        y = np.array([p["y"] for p in rows])
        g = np.array([p["drug_a"] for p in rows])
        out = {}
        for cname2, (_c, mask) in cohorts.items():
            if (cname2 == "novel") != (coh == "novel"):
                continue
            out[cname2] = auc_within(y[mask], s[mask], g[mask])
        db[coh] = out
    audit["drugbank_lookup_within_auroc"] = db
    audit["training"] = json.loads((OUT / "train_pairs_report.json").read_text())["counts"]
    audit["shingle_sensitivity"] = {k: (v if k != "share" else None) for k, v in sens.items()}
    audit["stems"] = {k: v for k, v in stem_report.items() if k != "stems"}
    audit["primary_sets"] = sets["rows"]
    (OUT / "input_audit.json").write_text(json.dumps(audit, indent=1))
    print(json.dumps({"e7b_rule": audit["e7b_rule"], "drugbank": db, "stems": audit["stems"],
                      "sens_counts": {k: len(v) for k, v in sens.items() if isinstance(v, list)}}, indent=1))
    if not audit["e7b_rule"]["assertion_R_at_least_floor"]:
        raise SystemExit("reachability assertion failed: R below 0.95 on E7b inputs")


if __name__ == "__main__":
    main()
