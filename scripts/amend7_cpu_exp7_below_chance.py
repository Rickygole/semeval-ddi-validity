import argparse
import json
import re

import numpy as np
from scipy.stats import rankdata

from amend7_cpu_common import (BOOT_SEED, OUT, ROOT, ci, cohort_arrays, drugbank_score, ev, f3, fast_within_auroc,
                               logit, paired_draws, read_csv, seed_mean, single, summarize_draws, write)
from ddiood import baselines, config, semeval

STEMS = ("conazole", "prazole", "floxacin", "gliflozin", "gliptin", "barbital", "azepam", "oxetine", "cycline",
         "cillin", "triptan", "setron", "dipine", "profen", "statin", "sartan", "navir", "tinib", "parin", "azole",
         "olol", "pril", "mycin", "caine", "afil", "mab", "vir")
SALTS = {"hydrochloride", "hcl", "sodium", "potassium", "calcium", "magnesium", "sulfate", "bisulfate", "mesylate",
         "maleate", "tartrate", "bitartrate", "acetate", "citrate", "phosphate", "succinate", "fumarate", "besylate",
         "bromide", "hydrobromide", "chloride", "erbumine", "hyclate", "monohydrate", "dihydrate", "disodium",
         "benzoate", "lactate", "gluconate", "nitrate", "oxalate", "malate", "dipropionate", "propionate", "valerate"}
COHORTS = ("older_clean", "novel")
TIERS = ("A", "B")
FEATURES = {"a_semeval_train_frequency": "a", "a2_semeval_train_positive_rate": "a (secondary, no decision)",
            "b_partner_popularity_loo_positives": "b", "iii_partner_prior_loo_rate": "iii",
            "iii2_partner_prior_vocab_di": "iii (label-free; added after the criteria were written, no decision)",
            "c_partner_wordpieces": "c", "c2_partner_words": "c (secondary, no decision)", "e_shared_stem": "e (exploratory)"}
DECIDED = {"a": "a_semeval_train_frequency", "b": "b_partner_popularity_loo_positives", "c": "c_partner_wordpieces",
           "e": "e_shared_stem"}
BELOW = {"a", "b"}


def base(name):
    words = [w for w in re.split(r"\s+", name.lower().strip()) if w and w not in SALTS]
    return " ".join(words) if words else name.lower().strip()


def suffix_len(a, b):
    n = 0
    while n < min(len(a), len(b)) and a[-1 - n] == b[-1 - n]:
        n += 1
    return n


def shared_stem(a, b):
    a, b = base(a), base(b)
    if a == b:
        return 0.0
    ta, tb = a.split()[-1], b.split()[-1]
    stem = next((s for s in STEMS if ta.endswith(s) and tb.endswith(s)), None)
    return float(stem is not None or suffix_len(ta, tb) >= 4)


def semeval_partner_stats():
    semeval.download()
    count, pos = {}, {}
    for r in semeval.load_pairs("train"):
        for d in {r["drug_a"], r["drug_b"]}:
            count[d] = count.get(d, 0) + 1
            pos[d] = pos.get(d, 0) + int(r["label_id"] != 0)
    return count, pos


def loo_partner(y, g, q):
    pos, n = {}, {}
    for yi, gi, qi in zip(y, g, q):
        pos.setdefault(qi, {}).setdefault(gi, 0)
        pos[qi][gi] += int(yi)
        n.setdefault(qi, {}).setdefault(gi, 0)
        n[qi][gi] += 1
    prev = float(np.mean(y))
    cnt, rate = [], []
    for gi, qi in zip(g, q):
        p = sum(pos[qi].values()) - pos[qi][gi]
        m = sum(n[qi].values()) - n[qi][gi]
        cnt.append(float(p))
        rate.append(p / m if m else prev)
    return np.asarray(cnt), np.asarray(rate)


def features_for(truth, cohort, tok, sem_count, sem_pos, ctx):
    full = cohort_arrays(truth, cohort, "A")
    cnt, rate = loo_partner(full["y"], full["g"], full["q"])
    q, g = full["q"], full["g"]
    f = {"a_semeval_train_frequency": np.log1p([sem_count.get(x, 0) for x in q]),
         "a2_semeval_train_positive_rate": np.asarray([sem_pos.get(x, 0) / sem_count[x] if sem_count.get(x) else 0.0 for x in q]),
         "b_partner_popularity_loo_positives": cnt, "iii_partner_prior_loo_rate": rate,
         "iii2_partner_prior_vocab_di": np.asarray([ctx.partner_prior(x) for x in q]),
         "c_partner_wordpieces": np.asarray([float(len(tok.tokenize(x))) for x in q]),
         "c2_partner_words": np.asarray([float(len(x.split())) for x in q]),
         "e_shared_stem": np.asarray([shared_stem(a, b) for a, b in zip(g, q)])}
    coverage = {"partners_absent_from_semeval_train": int(len({x for x in q if not sem_count.get(x)})),
                "n_partners": int(len(set(q))), "pairs_with_shared_stem": int(f["e_shared_stem"].sum())}
    return full["mask"], f, coverage


def system_scores(truth):
    tags = {"older_clean": "oodold", "novel": "ood"}
    out = {}
    for cohort, tag in tags.items():
        k = "oodold" if tag == "oodold" else "ood"
        out[cohort] = {"b2mixed-biomedbert": logit(seed_mean("b2mixed-biomedbert", f"{k}_empty")[0]),
                       "b1names-biomedbert": logit(seed_mean("b1names-biomedbert", f"{k}_names")[0]),
                       "llm-qwen-names": logit(single("llm-qwen-names", k)),
                       "DrugBank lookup": drugbank_score(truth, tag)}
    return out


def demean(x, codes):
    m = np.bincount(codes, weights=x) / np.bincount(codes)
    return x - m[codes]


def within_rank_assoc(s, f, g, boot, seed=42):
    codes = np.unique(g, return_inverse=True)[1]
    rs = np.zeros(len(s))
    rf = np.zeros(len(f))
    for k in range(codes.max() + 1):
        m = codes == k
        rs[m] = rankdata(s[m])
        rf[m] = rankdata(f[m])
    xs, xf = demean(rs, codes), demean(rf, codes)
    def corr(w):
        a = (w * xs * xf).sum()
        b = np.sqrt((w * xs ** 2).sum() * (w * xf ** 2).sum())
        return float(a / b) if b > 0 else float("nan")
    est = corr(np.ones(len(s)))
    rng = np.random.RandomState(seed)
    G = codes.max() + 1
    d = []
    for _ in range(boot):
        w = np.bincount(rng.randint(0, G, G), minlength=G)[codes].astype(float)
        v = corr(w)
        if not np.isnan(v):
            d.append(v)
    return summarize_draws(est, d)


def partial(s, F, g):
    codes = np.unique(g, return_inverse=True)[1]
    X = np.column_stack([demean(np.asarray(f, float), codes) for f in F])
    keep = (X ** 2).sum(0) > 0
    if not keep.any():
        return s.copy(), [0.0] * len(F)
    beta = np.zeros(len(F))
    beta[keep] = np.linalg.lstsq(X[:, keep], demean(s, codes), rcond=None)[0]
    return s - np.column_stack([np.asarray(f, float) for f in F]) @ beta, beta.tolist()


def judge(letter, feat, assoc, raw, part):
    lo, hi = feat["ci95"]
    c1 = hi < 0.5 if letter in BELOW else (hi < 0.5 or lo > 0.5)
    alo, ahi = assoc["ci95"]
    sign_ok = np.sign(assoc["value"]) * (feat["value"] - 0.5) < 0
    c2 = bool((alo > 0 or ahi < 0) and sign_ok)
    gap, gap2 = abs(raw - 0.5), abs(part - 0.5)
    c3 = bool(gap - gap2 >= 0.5 * gap)
    verdict = "confirmed" if c1 and c2 and c3 else ("partial" if c1 and c2 else "rejected")
    return {"C1": bool(c1), "C2": c2, "C3": c3, "verdict": verdict}


def cause_d(raw_a, raw_b):
    gap_a, gap_b = abs(raw_a["value"] - 0.5), abs(raw_b["value"] - 0.5)
    lo, hi = raw_b["ci95"]
    if gap_b >= gap_a:
        v = "rejected"
    elif gap_a - gap_b >= 0.5 * gap_a and lo <= 0.5 <= hi:
        v = "confirmed"
    else:
        v = "partial"
    return {"tier_A_gap": gap_a, "tier_B_gap": gap_b, "tier_B_ci95_contains_0.5": bool(lo <= 0.5 <= hi), "verdict": v}


def analyse_cohort(truth, cohort, feats, mask_a, scores, boot):
    res = {}
    for tier in TIERS:
        c = cohort_arrays(truth, cohort, tier)
        sel = c["mask"][mask_a]
        y, g, q = c["y"], c["g"], c["q"]
        F = {k: v[sel] for k, v in feats.items()}
        S = {k: v[c["mask"]] for k, v in scores.items()}
        names = list(F)
        cols, labels = [], []
        for k in names:
            cols.append(F[k])
            labels.append(("feature", k, None))
        partials = {}
        for sys_name, s in S.items():
            cols.append(s)
            labels.append(("raw", sys_name, None))
            for k in names:
                ps, beta = partial(s, [F[k]], g)
                partials[(sys_name, k)] = beta
                cols.append(ps)
                labels.append(("partial", sys_name, k))
            joint = [F[DECIDED[x]] for x in ("a", "b", "c", "e")]
            ps, beta = partial(s, joint, g)
            partials[(sys_name, "joint a+b+c+e")] = beta
            cols.append(ps)
            labels.append(("partial", sys_name, "joint a+b+c+e"))
        d = paired_draws(y, cols, g, q, boot, BOOT_SEED[cohort])
        summ = {lab: summarize_draws(fast_within_auroc(y, col, g), d[i]) for i, (lab, col) in enumerate(zip(labels, cols))}
        out = {"n": int(len(y)), "n_pos": int(y.sum()), "n_drugs": int(len(set(g))), "features": {}, "systems": {}}
        for k in names:
            out["features"][k] = {"cause": FEATURES[k], "within_auroc": summ[("feature", k, None)],
                                  "mean_pos": float(F[k][y == 1].mean()), "mean_neg": float(F[k][y == 0].mean())}
        for sys_name, s in S.items():
            raw = summ[("raw", sys_name, None)]
            row = {"raw_within_auroc": raw, "by_feature": {}}
            for k in names + ["joint a+b+c+e"]:
                part = summ[("partial", sys_name, k)]
                item = {"partialled_within_auroc": part, "slope": partials[(sys_name, k)]}
                if k != "joint a+b+c+e":
                    item["within_drug_spearman"] = within_rank_assoc(s, F[k], g, boot)
                    letter = next((x for x, v in DECIDED.items() if v == k), None)
                    if letter:
                        item["criteria"] = judge(letter, out["features"][k]["within_auroc"], item["within_drug_spearman"],
                                                 raw["value"], part["value"])
                row["by_feature"][k] = item
            if c["dbstate"] is not None and tier == "A" and sys_name != "DrugBank lookup":
                neg = y == 0
                st = c["dbstate"][neg]
                yy = (st == 2).astype(int)
                sub = (st == 1) | (st == 2)
                row["contradicted_vs_confirmed_negatives"] = {
                    "n_contradicted": int((st == 2).sum()), "n_confirmed": int((st == 1).sum()),
                    "within_auroc": fast_within_auroc(yy[sub], s[neg][sub], g[neg][sub]),
                    "meaning": "above 0.5: the model scores DrugBank-listed FDA negatives higher than DrugBank-unlisted ones, within drug"}
            out["systems"][sys_name] = row
        res[tier] = out
    for sys_name in scores:
        res["A"]["systems"][sys_name]["cause_d_label_noise"] = cause_d(res["A"]["systems"][sys_name]["raw_within_auroc"],
                                                                      res["B"]["systems"][sys_name]["raw_within_auroc"])
    return res


def paired_differences(truth, scores, boot):
    rows = []
    for cohort in COHORTS:
        for tier in TIERS:
            c = cohort_arrays(truth, cohort, tier)
            names = ["b2mixed-biomedbert", "llm-qwen-names", "DrugBank lookup"]
            S = [scores[cohort][n][c["mask"]] for n in names]
            d = paired_draws(c["y"], S, c["g"], c["q"], boot, BOOT_SEED[cohort])
            est = [fast_within_auroc(c["y"], s, c["g"]) for s in S]
            for j, other in ((1, "llm-qwen-names"), (2, "DrugBank lookup")):
                diff = d[0] - d[j]
                rows.append({"cohort": cohort, "tier": tier, "comparison": f"b2mixed-biomedbert minus {other}",
                             "n": int(len(c["y"])), "n_drugs": int(len(set(c["g"]))), "b2mixed": est[0], "other": est[j],
                             **summarize_draws(est[0] - est[j], diff), "share_draws_above_0": float((diff > 0).mean()),
                             "note": "DrugBank is circular on tier B (1.0 by construction)" if tier == "B" and j == 2 else ""})
    return rows


def ceiling(truth, boot):
    rows = []
    for cohort in COHORTS:
        c = cohort_arrays(truth, cohort, "A")
        tag = c["tag"]
        s = drugbank_score(truth, tag)[c["mask"]]
        y = c["y"]
        cpos, rneg = float(s[y == 1].mean()), float(s[y == 0].mean())
        w = summarize_draws(fast_within_auroc(y, s, c["g"]), paired_draws(y, [s], c["g"], c["q"], boot, BOOT_SEED[cohort])[0])
        rows.append({"cohort": cohort, "tier": "A", "n": int(len(y)), "n_drugs": int(len(set(c["g"]))),
                     "c_share_fda_positives_listed": cpos, "r_share_fda_negatives_listed": rneg,
                     "analytic_pooled_ceiling": 0.5 * (1 + cpos - rneg), "within_auroc_perfect_drugbank_scorer": w})
    return rows


def ece(y, p, bins=10):
    edges = np.linspace(0, 1, bins + 1)
    idx = np.clip(np.digitize(p, edges[1:-1]), 0, bins - 1)
    tot = 0.0
    for b in range(bins):
        m = idx == b
        if m.any():
            tot += m.mean() * abs(p[m].mean() - y[m].mean())
    return float(tot)


def confidently_wrong(truth):
    cells = {"b2mixed-biomedbert": (("test_sentence", "SemEval test, sentence"), ("test_empty", "SemEval test, names only"),
                                    ("ood_empty", "novel"), ("oodold_empty", "older_clean")),
             "b2sentence-biomedbert": (("test_sentence", "SemEval test, sentence"), ("test_empty", "SemEval test, names only"),
                                       ("ood_empty", "novel"), ("oodold_empty", "older_clean")),
             "b1names-biomedbert": (("test_names", "SemEval test, names only"), ("ood_names", "novel"), ("oodold_names", "older_clean")),
             "llm-qwen-names": (("test", "SemEval test, names only"), ("ood", "novel"), ("oodold", "older_clean"))}
    rows = []
    for system, keys in cells.items():
        for key, where in keys:
            p = single(system, key) if system.startswith("llm") else seed_mean(system, key)[0]
            if where.startswith("SemEval"):
                y = np.asarray(truth.test_y)
            else:
                c = cohort_arrays(truth, where, "A")
                y, p = c["y"], p[c["mask"]]
            neg = p[y == 0]
            rows.append({"system": system, "set": where, "key": key, "n": int(len(y)), "n_neg": int(len(neg)),
                         "neg_above_0.5": int((neg > 0.5).sum()), "share_neg_above_0.5": float((neg > 0.5).mean()),
                         "neg_above_0.9": int((neg > 0.9).sum()), "share_neg_above_0.9": float((neg > 0.9).mean()),
                         "ece_10_bins": ece(y, p), "n_seeds": 1 if system.startswith("llm") else 5})
    return rows


def wls(x, y, w):
    X = np.column_stack([np.ones(len(x)), x])
    W = np.sqrt(w)
    b = np.linalg.lstsq(X * W[:, None], y * W, rcond=None)[0]
    return b


def year_gradient(truth, scores, boot):
    years = {"novel": [int(r["first_approval_year"]) for r in read_csv(ROOT / "results" / "corrected" / "ood_pairs.csv")],
             "older_clean": [int(r["first_approval_year"]) for r in read_csv(ROOT / "results" / "corrected" / "ood_old_pairs.csv")]}
    out = {}
    for sys_name in ("b2mixed-biomedbert", "llm-qwen-names", "b1names-biomedbert", "DrugBank lookup"):
        per = []
        for cohort in COHORTS:
            c = cohort_arrays(truth, cohort, "A")
            yr = np.asarray(years[cohort])[c["mask"]]
            s = scores[cohort][sys_name][c["mask"]]
            for d in sorted(set(c["g"])):
                m = c["g"] == d
                if len(set(c["y"][m])) < 2:
                    continue
                per.append({"cohort": cohort, "drug": d, "year": int(yr[m][0]), "n_pairs": int(m.sum()),
                            "auroc": fast_within_auroc(c["y"][m], s[m], np.zeros(m.sum(), int))})
        x = np.asarray([r["year"] for r in per], float)
        a = np.asarray([r["auroc"] for r in per])
        w = np.asarray([r["n_pairs"] for r in per], float)
        b = wls(x, a, w)
        rng = np.random.RandomState(42)
        draws = []
        for _ in range(boot):
            i = rng.randint(0, len(per), len(per))
            if len(set(x[i])) > 1:
                draws.append(wls(x[i], a[i], w[i])[1] * 10)
        side = {}
        for cohort in COHORTS:
            m = np.asarray([r["cohort"] == cohort for r in per])
            side[cohort] = {"n_drugs": int(m.sum()), "years": [int(x[m].min()), int(x[m].max())],
                            "weighted_mean_per_drug_auroc": float(np.average(a[m], weights=w[m]))}
        out[sys_name] = {"slope_per_decade": summarize_draws(float(b[1] * 10), draws), "n_drugs": len(per),
                         "cohorts": side, "per_drug": per if sys_name == "b2mixed-biomedbert" else None}
    return out


def md_report(res):
    L = ["# Experiment 7: the below-chance Older-clean result", "",
         "Exploratory and post hoc. Criteria were written to `exp7_criteria.json` before any statistic below was computed. "
         "Primary system b2mixed-biomedbert (seed-averaged, names only); tiers A and B are co-primary. Verdicts answer the "
         "below-chance question for the primary system on Older-clean; rows for other systems and for Novel are for information.", "",
         "## Verdicts for the primary system on Older-clean", "", "| cause | tier A | tier B |", "| --- | --- | --- |"]
    oc = res["causes"]["older_clean"]
    for letter, k in DECIDED.items():
        va = oc["A"]["systems"]["b2mixed-biomedbert"]["by_feature"][k]["criteria"]["verdict"]
        vb = oc["B"]["systems"]["b2mixed-biomedbert"]["by_feature"][k]["criteria"]["verdict"]
        L.append(f"| {letter} ({k}) | {va} | {vb} |")
    dd = oc["A"]["systems"]["b2mixed-biomedbert"]["cause_d_label_noise"]["verdict"]
    L.append(f"| d (label-noise asymmetry, tier B versus tier A) | {dd} | {dd} |")
    L.append("")
    for k, what in (("iii_partner_prior_loo_rate", "test-label partner prior (leave-one-drug-out positive rate in the cohort)"),
                    ("iii2_partner_prior_vocab_di", "label-free partner prior (share of vocabulary Drug Interactions sections naming the partner)")):
        pa = oc["A"]["features"][k]["within_auroc"]
        pb = oc["B"]["features"][k]["within_auroc"]
        sa = oc["A"]["systems"]["b2mixed-biomedbert"]["by_feature"][k]
        L.append(f"(iii) {what}, Older-clean within drug: tier A {f3(pa['value'])} {ci(pa['ci95'])}, tier B {f3(pb['value'])} "
                 f"{ci(pb['ci95'])}; b2mixed within-drug Spearman with it {f3(sa['within_drug_spearman']['value'])} "
                 f"{ci(sa['within_drug_spearman']['ci95'])}; b2mixed partialled {f3(sa['partialled_within_auroc']['value'])} (tier A).")
    L.append("")
    for cohort in COHORTS:
        for tier in TIERS:
            r = res["causes"][cohort][tier]
            L += [f"## {cohort}, tier {tier} (n = {r['n']}, {r['n_pos']} positive, {r['n_drugs']} drugs)", "",
                  "| feature | cause | within-drug AUROC | 95% CI | mean pos | mean neg |", "| --- | --- | --- | --- | --- | --- |"]
            for k, f in r["features"].items():
                L.append(f"| {k} | {f['cause']} | {f3(f['within_auroc']['value'])} | {ci(f['within_auroc']['ci95'])} | "
                         f"{f3(f['mean_pos'])} | {f3(f['mean_neg'])} |")
            L += ["", "| system | raw within AUROC | 95% CI | feature | Spearman within | 95% CI | partialled AUROC | 95% CI | C1 | C2 | C3 | verdict |",
                  "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
            for sname, srow in r["systems"].items():
                raw = srow["raw_within_auroc"]
                for k, it in srow["by_feature"].items():
                    sp = it.get("within_drug_spearman") or {}
                    cr = it.get("criteria") or {}
                    L.append(f"| {sname} | {f3(raw['value'])} | {ci(raw['ci95'])} | {k} | {f3(sp.get('value'))} | {ci(sp.get('ci95'))} | "
                             f"{f3(it['partialled_within_auroc']['value'])} | {ci(it['partialled_within_auroc']['ci95'])} | "
                             f"{cr.get('C1', '')} | {cr.get('C2', '')} | {cr.get('C3', '')} | {cr.get('verdict', '')} |")
            L.append("")
        L += [f"### Cause d (label-noise asymmetry), {cohort}", "", "| system | tier A gap | tier B gap | tier B CI contains 0.5 | contradicted vs confirmed negatives AUROC | verdict |",
              "| --- | --- | --- | --- | --- | --- |"]
        for sname, srow in res["causes"][cohort]["A"]["systems"].items():
            dd = srow["cause_d_label_noise"]
            cv = srow.get("contradicted_vs_confirmed_negatives", {})
            L.append(f"| {sname} | {f3(dd['tier_A_gap'])} | {f3(dd['tier_B_gap'])} | {dd['tier_B_ci95_contains_0.5']} | "
                     f"{f3(cv.get('within_auroc'))} (n {cv.get('n_contradicted', '')}/{cv.get('n_confirmed', '')}) | {dd['verdict']} |")
        L.append("")
    L += ["## (i) Paired within-drug differences (shared two-way draws)", "",
          "| cohort | tier | comparison | n | drugs | b2mixed | other | difference | 95% CI | share of draws above 0 | note |",
          "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    L += [f"| {r['cohort']} | {r['tier']} | {r['comparison']} | {r['n']} | {r['n_drugs']} | {f3(r['b2mixed'])} | {f3(r['other'])} | "
          f"{f3(r['value'])} | {ci(r['ci95'])} | {f3(r['share_draws_above_0'])} | {r['note']} |" for r in res["paired_differences"]]
    L += ["", "## (ii) Knowledge ceiling on tier A (a scorer that knows DrugBank exactly)", "",
          "| cohort | n | drugs | c (positives listed) | r (negatives listed) | analytic pooled 0.5(1+c-r) | within-drug AUROC | 95% CI |",
          "| --- | --- | --- | --- | --- | --- | --- | --- |"]
    L += [f"| {r['cohort']} | {r['n']} | {r['n_drugs']} | {f3(r['c_share_fda_positives_listed'])} | {f3(r['r_share_fda_negatives_listed'])} | "
          f"{f3(r['analytic_pooled_ceiling'])} | {f3(r['within_auroc_perfect_drugbank_scorer']['value'])} | "
          f"{ci(r['within_auroc_perfect_drugbank_scorer']['ci95'])} |" for r in res["ceiling"]]
    L += ["", "## (iv) Confidently wrong", "", "| system | set | n | negatives | share neg > 0.5 | share neg > 0.9 | ECE (10 bins) |",
          "| --- | --- | --- | --- | --- | --- | --- |"]
    L += [f"| {r['system']} | {r['set']} | {r['n']} | {r['n_neg']} | {f3(r['share_neg_above_0.5'])} ({r['neg_above_0.5']}) | "
          f"{f3(r['share_neg_above_0.9'])} ({r['neg_above_0.9']}) | {f3(r['ece_10_bins'])} |" for r in res["confidently_wrong"]]
    L += ["", "## Approval-year gradient (descriptive only, exploratory)", "",
          "Per-drug within-drug AUROC on continuous first approval year, weighted by pairs, Novel and Older-clean drugs together, "
          "drug bootstrap. The 2013 to 2019 gap and the label-format difference between cohorts make this weak.", "",
          "| system | drugs | slope per decade | 95% CI | Older-clean weighted mean (drugs, years) | Novel weighted mean (drugs, years) |",
          "| --- | --- | --- | --- | --- | --- |"]
    for sname, r in res["year_gradient"].items():
        o, n = r["cohorts"]["older_clean"], r["cohorts"]["novel"]
        L.append(f"| {sname} | {r['n_drugs']} | {f3(r['slope_per_decade']['value'])} | {ci(r['slope_per_decade']['ci95'])} | "
                 f"{f3(o['weighted_mean_per_drug_auroc'])} ({o['n_drugs']}, {o['years'][0]} to {o['years'][1]}) | "
                 f"{f3(n['weighted_mean_per_drug_auroc'])} ({n['n_drugs']}, {n['years'][0]} to {n['years'][1]}) |")
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--boot", type=int, default=1000)
    a = ap.parse_args()
    if not (OUT / "exp7_criteria.json").exists():
        raise SystemExit("exp7_criteria.json must be written before this analysis runs")
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(config.ENCODER, local_files_only=True)
    truth = ev.load_truth()
    sem_count, sem_pos = semeval_partner_stats()
    ctx = baselines.Context(json.loads((config.ARTIFACTS / "vocab" / "drug_lookup.json").read_text()))
    scores = system_scores(truth)
    res = {"status": "Amendment 7 experiment 7, exploratory, post hoc; criteria in exp7_criteria.json written before computing",
           "criteria": json.loads((OUT / "exp7_criteria.json").read_text()), "causes": {}, "coverage": {}}
    for cohort in COHORTS:
        mask_a, feats, cov = features_for(truth, cohort, tok, sem_count, sem_pos, ctx)
        res["coverage"][cohort] = cov
        res["causes"][cohort] = analyse_cohort(truth, cohort, feats, mask_a, scores[cohort], a.boot)
    res["paired_differences"] = paired_differences(truth, scores, a.boot)
    res["ceiling"] = ceiling(truth, a.boot)
    res["confidently_wrong"] = confidently_wrong(truth)
    res["year_gradient"] = year_gradient(truth, scores, a.boot)
    md = md_report(res)
    write("exp7_below_chance", res, md)
    print(md)


if __name__ == "__main__":
    main()
