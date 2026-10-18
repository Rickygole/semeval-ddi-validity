import argparse
import gzip
import json
import sys
from pathlib import Path

import numpy as np
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ddiood import amend7_analysis as aa
from ddiood import amend7_data as ad
from ddiood import rev2_encoders as re_

FAMILIES = re_.FAMILIES
SEEDS = re_.SEEDS
STORED = {"b2mixed": "b2mixed-biomedbert-s{seed}", "b2sentence": "b2sentence-biomedbert-s{seed}"}
COHORT_KEY = {"seen": "train_empty", "seen_not_in_semeval_train": "train_empty", "novel": "ood_empty",
              "older_primary": "oodold_empty"}
NAMES_FORM_KEY = {"seen": "train_names", "seen_not_in_semeval_train": "train_names", "novel": "ood_names"}
BOOT = {"seen": 42, "seen_not_in_semeval_train": 42, "novel": 1042, "older_primary": 42}
A7_MARKER = "a7-panel-biomedbert_full-marker"
MARKER_AUROC_KEYS = (("ood_empty", "novel"), ("oodold_empty", "older_primary"))
REPRO_AUROC_KEYS = (("ood_empty", "novel"), ("oodold_empty", "older_primary"), ("ood_names", "novel"))
REPRO_FAMILIES = ("b2mixed", "b2sentence")


def read(dir_, name):
    f = Path(dir_) / f"{name}.json"
    return json.loads(f.read_text()) if f.exists() else None


def new_job(dir_, family, seed):
    return read(dir_, f"r2-{family}-biomedbert-s{seed}")


def stored_job(dir_, family, seed):
    return read(dir_, STORED[family].format(seed=seed))


def pair_key(a, b):
    return frozenset((str(a).lower().strip(), str(b).lower().strip()))


def semeval_pair_index(semeval_rows):
    index = {}
    for r in semeval_rows:
        index.setdefault(pair_key(r["drug_a"], r["drug_b"]), []).append(int(r["label_id"] != 0))
    return index


def overlap_summary(train_rows, index):
    inside = np.array([pair_key(r["drug_a"], r["drug_b"]) in index for r in train_rows])
    y = np.array([r["y"] for r in train_rows])
    sem_pos = np.array([pair_key(r["drug_a"], r["drug_b"]) in index and any(index[pair_key(r["drug_a"], r["drug_b"])])
                        for r in train_rows])
    anchors = {r["drug_a"] for r in train_rows}
    partners = {r["drug_b"] for r in train_rows}
    return {"match_rule": "unordered pair, each name lowercased and stripped, against every SemEval 2013 train pair",
            "n_pairs": int(len(train_rows)), "n_in_semeval_train": int(inside.sum()),
            "n_in_semeval_train_with_a_positive_instance": int(sem_pos.sum()),
            "n_positive_and_semeval_positive": int((sem_pos & (y == 1)).sum()),
            "n_not_in_semeval_train": int((~inside).sum()), "n_positive_not_in_semeval_train": int(((~inside) & (y == 1)).sum()),
            "n_drugs_both_anchor_and_partner": int(len(anchors & partners)), "n_anchor_drugs": int(len(anchors)),
            "n_partner_drugs": int(len(partners))}, ~inside


def cohorts(truth, train_rows, outside=None):
    out = {"seen": {"y": np.array([r["y"] for r in train_rows]), "g": np.array([r["drug_a"] for r in train_rows]),
                    "q": np.array([r["drug_b"] for r in train_rows]), "mask": np.ones(len(train_rows), bool), "name": "seen"}}
    if outside is not None:
        m = np.asarray(outside, bool)
        full = out["seen"]
        out["seen_not_in_semeval_train"] = {"y": full["y"][m], "g": full["g"][m], "q": full["q"][m], "mask": m,
                                            "name": "seen_not_in_semeval_train"}
    for name in ("novel", "older_primary"):
        out[name] = truth.cohort(name)
    return out


def view(c, p):
    p = np.asarray(p, float)
    return p[c["mask"]]


def within(c, p, n):
    s = view(c, p)
    d = aa.draws(c["y"], [s], c["g"], c["q"], n, BOOT[c["name"]], "within")[0]
    return aa.summ(aa.point(c["y"], s, c["g"], "within"), d)


def seed_p(dir_, family, key, seeds=SEEDS):
    ps, have = [], []
    for s in seeds:
        r = new_job(dir_, family, s)
        if r is not None and key in r["eval"]:
            ps.append(np.asarray(r["eval"][key]["p"], float))
            have.append(s)
    return (np.mean(ps, axis=0) if ps else None), have, ps


def spearman(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    if np.ptp(a) == 0 or np.ptp(b) == 0:
        return None
    return float(spearmanr(a, b).statistic)


def dissociation(dir_, coh, n):
    rows = []
    for family in FAMILIES:
        for cname, c in coh.items():
            for form, keymap in (("names_only", COHORT_KEY), ("names_text_b1", NAMES_FORM_KEY)):
                if cname not in keymap:
                    continue
                key = keymap[cname]
                if form == "names_text_b1" and family == "marker":
                    continue
                p, have, per = seed_p(dir_, family, key)
                if p is None:
                    continue
                per_seed = [aa.point(c["y"], view(c, x), c["g"], "within") for x in per]
                rows.append({"family": family, "cohort": cname, "input": form, "key": key, "n_pairs": int(len(c["y"])),
                             "n_positive": int(c["y"].sum()), "n_anchor_drugs": int(len(set(c["g"]))),
                             "seeds": have, "complete": sorted(have) == sorted(SEEDS),
                             "seed_mean": within(c, p, n), "per_seed": [float(x) for x in per_seed]})
    return rows


def semeval_rows(dir_, test_y):
    rows = []
    y = np.asarray(test_y)
    for family in FAMILIES:
        for key in ("test_sentence", "test_empty"):
            p, have, per = seed_p(dir_, family, key)
            if p is None:
                continue
            if len(p) != len(y):
                raise ValueError(f"{family}/{key}: {len(p)} scores for {len(y)} test pairs")
            rows.append({"family": family, "key": key, "seeds": have, "pooled_auroc_seed_mean": aa.point(y, p, None, "pooled"),
                         "per_seed": [aa.point(y, x, None, "pooled") for x in per]})
    return rows


def compare(a, b, coh, auroc_keys):
    keys = {}
    for key in sorted(set(b["eval"]) & set(a["eval"])):
        pa, pb = np.asarray(a["eval"][key]["p"], float), np.asarray(b["eval"][key]["p"], float)
        if pa.shape != pb.shape:
            keys[key] = {"status": "shape mismatch", "new": int(len(pa)), "stored": int(len(pb))}
            continue
        keys[key] = {"n": int(len(pa)), "spearman": spearman(pa, pb), "max_abs_diff": float(np.abs(pa - pb).max()),
                     "same_class": float(np.mean(np.asarray(a["eval"][key]["preds"]) == np.asarray(b["eval"][key]["preds"])))}
    diffs = {}
    for key, cname in auroc_keys:
        if key in a["eval"] and key in b["eval"]:
            c = coh[cname]
            na = aa.point(c["y"], view(c, a["eval"][key]["p"]), c["g"], "within")
            sb = aa.point(c["y"], view(c, b["eval"][key]["p"]), c["g"], "within")
            diffs[f"{key}/{cname}"] = {"retrained": na, "stored": sb, "difference": na - sb}
    return {"status": "compared", "keys": keys, "within_drug_auroc": diffs,
            "stored_missing_keys": sorted(set(a["eval"]) - set(b["eval"])),
            "retrained_missing_keys": sorted(set(b["eval"]) - set(a["eval"]))}


def repro(new_dir, stored_dir, coh, a7_dir=None):
    rows = []
    for family in REPRO_FAMILIES:
        for seed in SEEDS:
            a, b = new_job(new_dir, family, seed), stored_job(stored_dir, family, seed)
            if a is None or b is None:
                rows.append({"family": family, "seed": seed, "status": "missing", "new": a is not None, "stored": b is not None})
                continue
            rows.append({"family": family, "seed": seed, **compare(a, b, coh, REPRO_AUROC_KEYS)})
    a, b = new_job(new_dir, "marker", 42), read(a7_dir, A7_MARKER) if a7_dir else None
    if a is None or b is None:
        rows.append({"family": "marker", "seed": 42, "status": "missing", "new": a is not None, "stored": b is not None,
                     "stored_name": A7_MARKER})
    else:
        rows.append({"family": "marker", "seed": 42, "stored_name": A7_MARKER, **compare(a, b, coh, MARKER_AUROC_KEYS)})
    return rows


def analyze(new_dir, stored_dir, truth, train_rows, test_y=None, n=1000, semeval_train=None, a7_dir=None):
    outside, overlap = None, None
    if semeval_train is not None:
        overlap, outside = overlap_summary(train_rows, semeval_pair_index(semeval_train))
    coh = cohorts(truth, train_rows, outside)
    out = {"status": "post hoc, descriptive; no decision rule", "bootstrap": "two-way over anchor drugs and partners, percentile 95%",
           "bootstrap_seeds": BOOT, "n_draws": n, "seen_overlap_with_semeval_train": overlap,
           "dissociation": dissociation(new_dir, coh, n), "reproducibility": repro(new_dir, stored_dir, coh, a7_dir)}
    if test_y is not None:
        out["semeval_test"] = semeval_rows(new_dir, test_y)
    return out


def f3(v):
    return "NA" if v is None or (isinstance(v, float) and np.isnan(v)) else f"{v:.3f}"


def markdown(res):
    ov = res.get("seen_overlap_with_semeval_train")
    md = ["# R2a: SemEval-trained encoders on seen-drug and unseen-drug pair labels", "", res["status"], "",
          f"Seen pairs also in SemEval train: {ov['n_in_semeval_train']} of {ov['n_pairs']} ({ov['n_in_semeval_train_with_a_positive_instance']} with a "
          f"SemEval positive instance); {ov['n_drugs_both_anchor_and_partner']} drugs act as both anchor and partner." if ov else "", "",
          "## Within-drug AUROC, names only, seed-mean score, two-way bootstrap 95% interval", "",
          "| family | cohort | input | pairs | positives | anchor drugs | seeds | within-drug AUROC | 95% interval | per seed |",
          "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for r in res["dissociation"]:
        s = r["seed_mean"]
        lo = f3(s["lo95"]) if s["lo95"] is not None else "NA"
        hi = f3(s["hi95"]) if s["hi95"] is not None else "NA"
        md.append(f"| {r['family']} | {r['cohort']} | {r['input']} | {r['n_pairs']} | {r['n_positive']} | {r['n_anchor_drugs']} | "
                  f"{len(r['seeds'])}{'' if r['complete'] else ' (incomplete)'} | {f3(s['value'])} | [{lo}, {hi}] | "
                  f"{', '.join(f3(x) for x in r['per_seed'])} |")
    if res.get("semeval_test"):
        md += ["", "## SemEval 2013 test, pooled AUROC", "", "| family | key | seeds | seed-mean AUROC | per seed |", "| --- | --- | --- | --- | --- |"]
        for r in res["semeval_test"]:
            md.append(f"| {r['family']} | {r['key']} | {len(r['seeds'])} | {f3(r['pooled_auroc_seed_mean'])} | "
                      f"{', '.join(f3(x) for x in r['per_seed'])} |")
    md += ["", "## Reproducibility of the retrained b2mixed and b2sentence models against the stored predictions", "",
           "| family | seed | key | n | Spearman | max abs diff | same class |", "| --- | --- | --- | --- | --- | --- | --- |"]
    for r in res["reproducibility"]:
        if r["status"] != "compared":
            md.append(f"| {r['family']} | {r['seed']} | not compared (new {r['new']}, stored {r['stored']}) | | | | |")
            continue
        for key, v in r["keys"].items():
            if "spearman" not in v:
                md.append(f"| {r['family']} | {r['seed']} | {key} | {v['status']} | | | |")
                continue
            md.append(f"| {r['family']} | {r['seed']} | {key} | {v['n']} | {f3(v['spearman'])} | {v['max_abs_diff']:.4f} | {v['same_class']:.4f} |")
    md += ["", "| family | seed | key / cohort | retrained within-drug AUROC | stored | difference |", "| --- | --- | --- | --- | --- | --- |"]
    for r in res["reproducibility"]:
        if r["status"] == "compared":
            for k, v in r["within_drug_auroc"].items():
                md.append(f"| {r['family']} | {r['seed']} | {k} | {f3(v['retrained'])} | {f3(v['stored'])} | {v['difference']:+.4f} |")
    return "\n".join(md) + "\n"


def clean(x):
    if isinstance(x, dict):
        return {k: clean(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [clean(v) for v in x]
    if isinstance(x, (np.floating, float)):
        return None if np.isnan(x) else float(x)
    if isinstance(x, np.integer):
        return int(x)
    return x


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--preds", required=True)
    ap.add_argument("--stored", default=str(ROOT / "results" / "revision" / "preds"))
    ap.add_argument("--a7", default=str(ROOT / "runs" / "preds"))
    ap.add_argument("--inputs", default=str(ROOT / "artifacts" / "bundle" / "inputs.json.gz"))
    ap.add_argument("--train", default=str(ROOT / "artifacts" / "amend7" / "train_pairs.csv"))
    ap.add_argument("--out", default=str(ROOT / "results" / "revision" / "rev2_colab"))
    ap.add_argument("--boot", type=int, default=1000)
    a = ap.parse_args()
    base = json.load(gzip.open(a.inputs, "rt"))
    truth = aa.Truth(base["ood_pairs"], base["ood_old_pairs"])
    train_rows = [ad.Data._train_row(x) for x in ad.read_rows_csv(a.train)]
    from ddiood import semeval
    semeval.download()
    test_y = [int(r["label_id"] != 0) for r in semeval.load_pairs("test")]
    res = clean(analyze(a.preds, a.stored, truth, train_rows, test_y, a.boot, semeval.load_pairs("train"), a.a7))
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "r2a.json").write_text(json.dumps(res, indent=1))
    (out / "r2a.md").write_text(markdown(res))
    print(out / "r2a.md")


if __name__ == "__main__":
    main()
