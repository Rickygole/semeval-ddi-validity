import argparse

import numpy as np
from scipy.stats import spearmanr

import rev3_common as rc
import rev2_analyze_a as an
import rev3_d3 as d3
from amend7_cpu_common import fast_within_auroc, logit, paired_draws
from amend7_cpu_exp7_below_chance import partial

SEED = 42
MIN_PAIRS = 5


def norm(x):
    return str(x).lower().strip()


def partner_priors(sem_rows, partners):
    tot, pos = {}, {}
    n_pos = n_all = 0
    for r in sem_rows:
        names = {norm(r["drug_a"]), norm(r["drug_b"])}
        y = int(r["label_id"] != 0)
        n_all += 1
        n_pos += y
        for nm in names:
            tot[nm] = tot.get(nm, 0) + 1
            pos[nm] = pos.get(nm, 0) + y
    overall = n_pos / n_all
    primary = np.array([pos[norm(p)] / tot[norm(p)] if norm(p) in tot else overall for p in partners])
    alt = np.array([pos[norm(p)] / n_pos if norm(p) in tot else 0.0 for p in partners])
    has = np.array([norm(p) in tot for p in partners])
    return primary, alt, has, {"overall_positive_share": overall, "n_train_instances": n_all, "n_positive_instances": n_pos,
                               "n_partners_without_train_instance": len({norm(p) for p, h in zip(partners, has) if not h}),
                               "n_pairs_with_partner_without_train_instance": int((~has).sum())}


def seed_mean_logit(family):
    p, have, _ = an.seed_p(d3.PREDS, family, an.COHORT_KEY["seen"])
    return logit(p), have


def sub(c, mask, name="seen"):
    m = np.asarray(mask, bool)
    full_mask = np.zeros(len(c["mask"]), bool)
    full_mask[np.where(c["mask"])[0][m]] = True
    return {"y": c["y"][m], "g": c["g"][m], "q": c["q"][m], "mask": full_mask, "name": name}


def cluster_spearman(x, y, g, n, seed):
    anchors = sorted(set(g))
    index = {a: np.where(g == a)[0] for a in anchors}
    rng = np.random.RandomState(seed)
    out = []
    for _ in range(n):
        pick = rng.randint(0, len(anchors), len(anchors))
        idx = np.concatenate([index[anchors[i]] for i in pick])
        if np.ptp(x[idx]) == 0 or np.ptp(y[idx]) == 0:
            continue
        out.append(spearmanr(x[idx], y[idx]).statistic)
    return out


def within_spearman(x, y, g):
    vals = []
    for d in sorted(set(g)):
        m = g == d
        if m.sum() >= MIN_PAIRS and np.ptp(x[m]) > 0 and np.ptp(y[m]) > 0:
            vals.append(spearmanr(x[m], y[m]).statistic)
    return {"mean_within_drug_spearman": float(np.mean(vals)) if vals else None, "n_anchors": len(vals)}


def summ(est, d):
    return {"value": float(est), "ci95": rc.pct(d), "ci90": rc.pct(d, 5, 95), "n_draws": int(np.sum(~np.isnan(np.asarray(d, float))))}


def adjust(c, score, prior, n):
    s = np.asarray(score, float)[c["mask"]]
    pr = np.asarray(prior, float)[c["mask"]]
    y, g, q = c["y"], c["g"], c["q"]
    adj, beta = partial(s, [pr], g)
    D = paired_draws(y, [s, adj], g, q, n, SEED)
    w, a = fast_within_auroc(y, s, g), fast_within_auroc(y, adj, g)
    return {"raw_within": summ(w, D[0]), "partner_adjusted_within": summ(a, D[1]), "adjusted_minus_raw": summ(a - w, D[1] - D[0]), "slope_on_prior": float(beta[0]),
            "paired_two_way_draws": int(D.shape[1])}


def analyze(coh, sem_rows, n):
    seen = coh["seen"]
    outside = coh["seen_not_in_semeval_train"]
    prim, alt, has, info = partner_priors(sem_rows, d3_partners(seen))
    res = {"prior_info": info, "views": {}}
    full_has = np.asarray(has)
    for vname, c in (("seen_4643", seen), ("seen_not_in_semeval_train_4062", outside)):
        pv = {"n_pairs": int(len(c["y"]))}
        pv["prior_primary"] = d3.intervals(c, prim, n)
        pv["prior_alternative"] = d3.intervals(c, alt, n)
        cc = sub(c, full_has[c["mask"]])
        pv["prior_primary_partners_with_train_instance_only"] = {"n_pairs": int(len(cc["y"])), **d3.intervals(cc, prim, n)}
        fam = {}
        for family in an.FAMILIES:
            score, have = seed_mean_logit(family)
            adj = adjust(c, score, prim, n)
            x, pr = score[c["mask"]], prim[c["mask"]]
            sp = float(spearmanr(x, pr).statistic)
            ds = cluster_spearman(x, pr, c["g"], n, SEED)
            fam[family] = {"seeds": have, **adj, "spearman_pooled": sp, "spearman_pooled_anchor_bootstrap_ci95": rc.pct(ds),
                           "spearman_n_draws": len(ds), **within_spearman(x, pr, c["g"])}
        pv["families"] = fam
        res["views"][vname] = pv
    return res


def d3_partners(c):
    return list(c["q"])


def md(res):
    i = res["prior_info"]
    L = ["# D4: seen-cohort mechanism check", "", f"Status: {rc.STATUS}.", "",
         "Prior (primary): for a partner, the share of positive SemEval train instances among the train instances that contain the partner as either entity. "
         "Alternative: the number of positive train instances that contain the partner divided by all positive train instances. A partner with no train instance gets the overall positive share (primary) or 0 (alternative). "
         "Priors use all train instances, including the instances of the overlap pairs. Scores are the logit of the seed-mean R2a probability (names only). "
         "Bootstrap seed 42, 1,000 draws; the Spearman interval resamples anchor drugs. Raw and adjusted within-drug AUROC use the fast within-drug AUROC of rev2 m4. "
         "These are descriptive associations on anchor drugs of which many also act as partners; no mechanism or cause is identified.", "",
         f"SemEval train: {i['n_train_instances']} instances, {i['n_positive_instances']} positive, overall positive share {i['overall_positive_share']:.6f}; "
         f"{i['n_pairs_with_partner_without_train_instance']} seen pairs ({i['n_partners_without_train_instance']} partners) have a partner with no train instance.", ""]
    for vname, v in res["views"].items():
        L += [f"## View {vname} ({v['n_pairs']} pairs)", "", "(a) Prior as a scorer", ""]
        rows = [[k, rc.f3(v[k]["pooled_auroc"]), rc.f3(v[k]["within_drug_auroc"]), rc.ci(v[k]["within_ci95_two_way"]), rc.ci(v[k]["within_ci95_anchor_only"])]
                for k in ("prior_primary", "prior_alternative")]
        k = v["prior_primary_partners_with_train_instance_only"]
        rows.append([f"prior_primary, only pairs whose partner has a train instance ({k['n_pairs']} pairs)", rc.f3(k["pooled_auroc"]), rc.f3(k["within_drug_auroc"]),
                     rc.ci(k["within_ci95_two_way"]), rc.ci(k["within_ci95_anchor_only"])])
        L += rc.table(["scorer", "pooled AUROC", "within-drug AUROC", "95% two-way", "95% anchor only"], rows) + ["", "(b) Within-drug AUROC after partialling out the prior, and (c) Spearman with the prior", ""]
        rows = [[f, rc.f3(x["raw_within"]["value"]), rc.ci(x["raw_within"]["ci95"]), rc.f3(x["partner_adjusted_within"]["value"]), rc.ci(x["partner_adjusted_within"]["ci95"]),
                 rc.f3(x["adjusted_minus_raw"]["value"]), rc.ci(x["adjusted_minus_raw"]["ci95"]), rc.f3(x["slope_on_prior"]), rc.f3(x["spearman_pooled"]),
                 rc.ci(x["spearman_pooled_anchor_bootstrap_ci95"]), rc.f3(x["mean_within_drug_spearman"]), x["n_anchors"]] for f, x in v["families"].items()]
        L += rc.table(["family", "raw within", "95% paired two-way", "adjusted within", "95% paired two-way", "adjusted minus raw", "95% paired two-way", "slope on prior",
                       "Spearman pooled", "95% anchor bootstrap", "mean within-drug Spearman", "anchors"], rows) + [""]
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--boot", type=int, default=1000)
    a = ap.parse_args()
    rows, sem, overlap, coh = d3.load_context()
    res = analyze(coh, sem, a.boot)
    res["n_boot"], res["seed"], res["overlap"] = a.boot, SEED, overlap
    rc.write("d4_seen_mechanism", res, md(res))
    print(rc.OUT / "d4_seen_mechanism.md")


if __name__ == "__main__":
    main()
