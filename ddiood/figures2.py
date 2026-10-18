import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import roc_curve

from . import evaluate2 as ev

PRIMARY_MODELS = ("biomedbert", "biomistral")


def _primary(gk):
    if gk[2] != "standard" or gk[1] not in PRIMARY_MODELS:
        return False
    return gk[0] != "krag" or (gk[4] == 5 and gk[5] == 400 and gk[3] in ("hybrid", "contaminated"))


def _save(fig, out, name):
    path = Path(out) / name
    fig.savefig(path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return str(path)


def roc_figure(aggs, out, novelty):
    fig, ax = plt.subplots(figsize=(5, 5))
    col = 0 if novelty == "ood" else 1
    for gk, a in aggs.items():
        key = ev.OOD_KEYS.get(gk[0], (None, None))[col]
        if not _primary(gk) or key is None or key not in a["evals"]:
            continue
        e = a["evals"][key]
        if len(set(e["y"])) < 2:
            continue
        fpr, tpr, _ = roc_curve(e["y"], e["p"])
        ax.plot(fpr, tpr, label=f"{ev.label(gk)} ({ev.auroc(e['y'], e['p']):.2f})")
    ax.plot([0, 1], [0, 1], color="gray", linestyle=":")
    ax.set_xlabel("False positive rate")
    ax.set_ylabel("True positive rate")
    ax.set_title("Novel OOD" if novelty == "ood" else "Older OOD")
    ax.legend(fontsize=6)
    return _save(fig, out, f"roc_{novelty}.png")


def strip_figure(aggs, out):
    fig, ax = plt.subplots(figsize=(7, 4))
    names = []
    for gk, a in aggs.items():
        key = ev.OOD_KEYS.get(gk[0], (None, None))[0]
        if key is None or key not in a["evals"]:
            continue
        e = a["evals"][key]
        vals = [ev.auroc(e["y"], p) for p in e["seed_p"]]
        x = len(names)
        ax.scatter(np.full(len(vals), x) + np.linspace(-0.1, 0.1, len(vals)), vals, s=14)
        ax.hlines(np.nanmean(vals), x - 0.2, x + 0.2, color="black")
        names.append(ev.label(gk))
    ax.axhspan(ev.LO, ev.HI, color="gray", alpha=0.15)
    ax.set_xticks(range(len(names)))
    ax.set_xticklabels(names, rotation=75, ha="right", fontsize=6)
    ax.set_ylabel("Novel OOD AUROC per seed")
    return _save(fig, out, "seed_strip.png")


def swap_figure(tables, out):
    fig, ax = plt.subplots(figsize=(6, 4))
    rows = tables["swap"]
    systems = sorted({(r["system"], r["model"]) for r in rows})
    w = 0.8 / max(len(ev.KINDS), 1)
    for i, kind in enumerate(ev.KINDS):
        vals = [np.mean([r["flip_rate"] for r in rows if (r["system"], r["model"]) == s and r["swap"] == kind]
                        or [np.nan]) for s in systems]
        ax.bar(np.arange(len(systems)) + i * w, vals, w, label=kind)
    ax.set_xticks(np.arange(len(systems)) + w)
    ax.set_xticklabels([f"{s}/{m}" for s, m in systems], rotation=45, ha="right", fontsize=7)
    ax.set_ylabel("Binary prediction flip rate")
    ax.legend()
    return _save(fig, out, "swap_flip.png")


def grid_figure(tables, out, group="b2mixed/biomedbert"):
    rows = [r for r in tables["grid"] if r["group"] == group]
    fig, ax = plt.subplots(figsize=(5, 4))
    fmts = ["sentence", "names only"]
    novs = ["SemEval test", "Novel OOD"]
    for j, nov in enumerate(novs):
        vals, err = [], []
        for f in fmts:
            r = next((x for x in rows if x["format"] == f and x["novelty"] == nov), None)
            vals.append(np.nan if r is None else r["auroc"])
            err.append([0, 0] if r is None or r["lo"] is None else [r["auroc"] - r["lo"], r["hi"] - r["auroc"]])
        ax.bar(np.arange(2) + j * 0.4, vals, 0.4, yerr=np.array(err).T, label=nov, capsize=3)
    ax.set_xticks(np.arange(2) + 0.2)
    ax.set_xticklabels(fmts)
    ax.axhline(0.5, color="gray", linestyle=":")
    ax.set_ylabel("AUROC")
    ax.set_title(group)
    ax.legend()
    return _save(fig, out, "grid_2x2.png")


def make_all(aggs, tables, out):
    Path(out).mkdir(parents=True, exist_ok=True)
    return [roc_figure(aggs, out, "ood"), roc_figure(aggs, out, "oodold"), strip_figure(aggs, out),
            swap_figure(tables, out), grid_figure(tables, out)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--preds", required=True)
    ap.add_argument("--out", default=str(ev.CORRECTED / "revision"))
    a = ap.parse_args()
    aggs = ev.aggregate(ev.load_jobs(a.preds, ev.load_truth()))
    tables = json.loads((Path(a.out) / "tables.json").read_text())
    for p in make_all(aggs, tables, a.out):
        print(p)


if __name__ == "__main__":
    main()
