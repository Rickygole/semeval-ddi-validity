import argparse
import json
from pathlib import Path

import numpy as np

import rev3_common as rc
import rev2_m10 as m10
from ddiood import amend7_analysis as aa
from ddiood import rev3b_jobs as rj
from ddiood import semeval
from ddiood.evaluate2 import auroc

INPUTS = rj.INPUT_KEYS
SWAPS = ("swap_vocab", "swap_novel", "swap_pseudo")
BOOT_SEED = 42
PREDS = rc.ROOT / "runs" / "preds"
STORED = "r2-marker-biomedbert-s{seed}"


def binary_f1(y, pred):
    y, pred = np.asarray(y) > 0, np.asarray(pred) > 0
    tp = float((y & pred).sum())
    den = float(y.sum() + pred.sum())
    return 2 * tp / den if den else 0.0


def seed_metrics(y, ev):
    out = {}
    for k in INPUTS:
        p = np.asarray(ev[k]["p"], float)
        out[k] = {"auroc": float(auroc(y, p)), "binary_f1": binary_f1(y, ev[k]["preds"])}
    base = np.asarray(ev["sentence"]["preds"]) > 0
    basep = np.asarray(ev["sentence"]["p"], float)
    for k in SWAPS:
        out[k]["flip_rate"] = float(((np.asarray(ev[k]["preds"]) > 0) != base).mean())
        out[k]["mean_abs_dp"] = float(np.abs(np.asarray(ev[k]["p"], float) - basep).mean())
    return out


def stat_vector(y, evs, idx=None):
    sel = slice(None) if idx is None else idx
    ys = np.asarray(y)[sel]
    row = {}
    for k in INPUTS:
        ps = [np.asarray(e[k]["p"], float)[sel] for e in evs]
        prs = [np.asarray(e[k]["preds"])[sel] for e in evs]
        row[f"{k}.auroc"] = float(np.mean([aa.point(ys, p, None, "pooled") for p in ps]))
        row[f"{k}.binary_f1"] = float(np.mean([binary_f1(ys, q) for q in prs]))
        row[f"{k}.auroc_of_mean_p"] = float(aa.point(ys, np.mean(ps, axis=0), None, "pooled"))
    for k in INPUTS[1:]:
        for m in ("auroc", "binary_f1"):
            row[f"{k}.{m}_minus_sentence"] = row[f"{k}.{m}"] - row[f"sentence.{m}"]
    return row


def bootstrap(y, sid, evs, n, seed=BOOT_SEED):
    codes = np.unique(sid, return_inverse=True)[1].ravel()
    order = np.argsort(codes, kind="stable")
    bounds = np.searchsorted(codes[order], np.arange(codes.max() + 2))
    rows = [order[bounds[g]:bounds[g + 1]] for g in range(codes.max() + 1)]
    rng = np.random.RandomState(seed)
    draws = []
    for _ in range(n):
        idx = np.concatenate([rows[g] for g in rng.randint(0, len(rows), len(rows))])
        draws.append(stat_vector(y, evs, idx))
    return {k: np.array([d[k] for d in draws]) for k in draws[0]}


def micro_rows(gold, sid, evs, seeds, extra_fn, n):
    out = []
    for s, e in zip(seeds, evs):
        pred = np.asarray(e["sentence"]["preds"], int)
        out.append({"seed": s, **m10.evaluate(gold, pred, sid, n, extra_fn)})
    return out


def summarize(y, gold, sid, extra_fn, files, n):
    seeds = [f["config"]["seed"] for f in files]
    evs = [f["eval"] for f in files]
    per_seed = {str(s): seed_metrics(y, e) for s, e in zip(seeds, evs)}
    point = stat_vector(y, evs)
    draws = bootstrap(y, sid, evs, n)
    agg = {k: {"value": point[k], "ci95": rc.pct(draws[k]), "n_draws": int(len(draws[k]))} for k in point}
    swap_agg = {}
    for k in SWAPS:
        for m in ("flip_rate", "mean_abs_dp"):
            swap_agg[f"{k}.{m}"] = float(np.mean([per_seed[str(s)][k][m] for s in seeds]))
    return {"seeds": seeds, "complete": sorted(seeds) == sorted(rj.SEEDS), "per_seed": per_seed, "seed_mean": agg,
            "swap_seed_mean": swap_agg, "micro_f1_sentence": micro_rows(gold, sid, evs, seeds, extra_fn, n)}


def reproduction(files, stored_files):
    out = []
    for f, st in zip(files, stored_files):
        if st is None:
            out.append({"seed": f["config"]["seed"], "stored": False})
            continue
        a = np.asarray(f["eval"]["sentence"]["p"], float)
        b = np.asarray(st["eval"]["test_sentence"]["p"], float)
        same_pred = f["eval"]["sentence"]["preds"] == st["eval"]["test_sentence"]["preds"]
        out.append({"seed": f["config"]["seed"], "stored": True, "max_abs_gap_sentence": float(np.abs(a - b).max()), "preds_identical": bool(same_pred),
                    "job_checks": f.get("reproduction")})
    return out


def md(o):
    L = ["# D6: sentence dependence of the entity-marker models", "", f"Status: {rc.STATUS}.", "",
         f"Seeds present: {o['seeds']} (complete: {o['complete']}). SemEval 2013 test, {o['n_pairs']} pairs, {o['n_positive']} positive. Pooled AUROC is the "
         "positive-class probability against the binary label; binary F1 is `preds != 0` against the binary label. Seed mean = mean of the per-seed value; "
         f"the AUROC of the seed-mean probability is listed separately. Intervals: sentence-cluster bootstrap, {o['n_boot']} draws, seed {BOOT_SEED}, "
         "one resample for all seeds and inputs, 95% percentile on the seed mean.", ""]
    rows = []
    for k in INPUTS:
        m, f, am = o["seed_mean"][f"{k}.auroc"], o["seed_mean"][f"{k}.binary_f1"], o["seed_mean"][f"{k}.auroc_of_mean_p"]
        rows.append([k, rc.f3(m["value"]), rc.ci(m["ci95"]), rc.f3(f["value"]), rc.ci(f["ci95"]), rc.f3(am["value"]), rc.ci(am["ci95"]),
                     o["fallback"].get(k)])
    L += rc.table(["input", "AUROC seed mean", "95% CI", "binary F1 seed mean", "95% CI", "AUROC of seed-mean p", "95% CI", "marker fallback rows"], rows)
    L += ["", "## Difference from the original marked sentence (seed mean, paired draws)", ""]
    rows = []
    for k in INPUTS[1:]:
        a, f = o["seed_mean"][f"{k}.auroc_minus_sentence"], o["seed_mean"][f"{k}.binary_f1_minus_sentence"]
        rows.append([k, rc.f3(a["value"]), rc.ci(a["ci95"]), rc.f3(f["value"]), rc.ci(f["ci95"])])
    L += rc.table(["input", "AUROC difference", "95% CI", "binary F1 difference", "95% CI"], rows)
    L += ["", "## Swap inputs against the original sentence (seed mean)", ""]
    rows = [[k, rc.f3(o["swap_seed_mean"][f"{k}.flip_rate"]), rc.f3(o["swap_seed_mean"][f"{k}.mean_abs_dp"])] for k in SWAPS]
    L += rc.table(["input", "flip rate of the binary prediction", "mean absolute change in probability"], rows)
    L += ["", "## Per seed", ""]
    rows = []
    for s in o["seeds"]:
        r = o["per_seed"][str(s)]
        for k in INPUTS:
            rows.append([s, k, rc.f3(r[k]["auroc"]), rc.f3(r[k]["binary_f1"]), rc.f3(r[k].get("flip_rate")), rc.f3(r[k].get("mean_abs_dp"))])
    L += rc.table(["seed", "input", "AUROC", "binary F1", "flip rate", "mean abs dp"], rows)
    L += ["", "## Five-class micro F1 on the original sentence (as `m10_semeval_standard`)", ""]
    rows = [[r["seed"], rc.f3(r["micro_f1_4class"]), rc.ci(r["ci95"]), rc.f3(r["micro_f1_official_set_bound"]), rc.f3(r["precision"]),
             rc.f3(r["recall"]), rc.f3(r["binary_f1"])] for r in o["micro_f1_sentence"]]
    L += rc.table(["seed", "micro F1 (2810 pairs)", "95% CI", "official-set bound", "precision", "recall", "binary F1"], rows)
    L += ["", "## Reproduction against the stored R2a files", ""]
    rows = [[r["seed"], r["stored"], r.get("max_abs_gap_sentence"), r.get("preds_identical")] for r in o["reproduction"]]
    L += rc.table(["seed", "stored file found", "max abs gap, sentence", "argmax identical"], rows)
    L += ["", "Rows for which the entity markers could not be placed fall back to the template followed by the sentence; their counts are in the first table. "
          "Swapped rows keep the gold label of the original pair.", ""]
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--preds", default=str(PREDS))
    ap.add_argument("--boot", type=int, default=1000)
    a = ap.parse_args()
    semeval.download()
    test = semeval.load_pairs("test")
    full = semeval.load_pairs("test", entity_types={"drug", "drug_n", "brand", "group"})
    y = np.asarray([int(r["label_id"] != 0) for r in test])
    gold = np.asarray([r["label_id"] for r in test])
    sid = np.asarray([r["sentence_id"] for r in test])
    extra_fn = int(sum(r["label_id"] > 0 for r in full) - (gold > 0).sum())
    files = []
    for s in rj.SEEDS:
        f = Path(a.preds) / f"{rj.job_name(s)}.json"
        if f.exists():
            files.append(json.loads(f.read_text()))
    if not files:
        raise SystemExit("no r3b prediction files under " + a.preds)
    labels_hash = rj.labels_sha256(test)
    for f in files:
        if f["test_labels_sha256"] != labels_hash or f["n_rows"] != len(test) or f["smoke"]:
            raise SystemExit("a prediction file was not made on the full SemEval test set or is a smoke file")
    files.sort(key=lambda f: rj.SEEDS.index(f["config"]["seed"]))
    stored = []
    for f in files:
        sf = Path(a.preds) / f"{STORED.format(seed=f['config']['seed'])}.json"
        stored.append(json.loads(sf.read_text()) if sf.exists() else None)
    o = summarize(y, gold, sid, extra_fn, files, a.boot)
    o.update({"n_pairs": int(len(y)), "n_positive": int(y.sum()), "n_boot": a.boot, "fallback": files[0]["marker_fallback"],
              "reproduction": reproduction(files, stored), "inputs_sha256": files[0]["inputs_sha256"],
              "weights_sha256": {str(f["config"]["seed"]): f["weights"].get("weight_sha256") for f in files}})
    rc.write("d6_marker_sentence", o, md(o))
    print(md(o))


if __name__ == "__main__":
    main()
