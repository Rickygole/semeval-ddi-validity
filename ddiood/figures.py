import argparse
import json
from pathlib import Path

from . import config

COLORS = {"B1 name-only": "#7f7f7f", "B2 sentence-context": "#d62728", "B3 zero-shot LLM": "#9467bd",
          "B4 retrieval+LR": "#8c564b", "B5 LLM+retrieval": "#e377c2", "KnowledgeRAG-DDI": "#1f77b4"}


def slopegraph(res, path):
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(6, 5))
    for name, r in res["table1"].items():
        if r == "missing":
            continue
        ax.plot([0, 1], [r["id_f1"], r["ood_f1"]], marker="o", color=COLORS.get(name), label=name)
    ax.axhline(res["all_positive_reference"]["ood"], ls=":", color="k", lw=1, label="All-positive (OOD)")
    ax.set_xticks([0, 1], ["In-distribution", "Temporal OOD"])
    ax.set_ylabel("Binary F1")
    ax.set_ylim(0, 1)
    ax.legend(fontsize=8, frameon=False)
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)


def multiseed(res, path):
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(5, 4))
    for i, (name, s) in enumerate(res.get("multiseed", {}).items()):
        vals = list(s["ood_by_seed"].values())
        ax.scatter([i] * len(vals), vals, color=COLORS.get(name), s=40)
        ax.hlines(s["ood_mean"], i - 0.2, i + 0.2, color=COLORS.get(name))
    names = list(res.get("multiseed", {}))
    ax.set_xticks(range(len(names)), names)
    ax.set_ylabel("OOD binary F1")
    ax.set_ylim(0, 1)
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)


def fairness(res, path):
    import matplotlib.pyplot as plt
    f = res.get("fairness_2x2")
    if not f:
        return
    keys = [("id_sentence", "ID, sentence"), ("id_names", "ID, names"),
            ("ood_sentence", "OOD, FDA sentence"), ("ood_names", "OOD, names")]
    keys = [(k, l) for k, l in keys if k in f]
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar([l for _, l in keys], [f[k] for k, _ in keys], color=["#d62728", "#ff9896", "#1f77b4", "#aec7e8"][:len(keys)])
    ax.set_ylabel("B2 binary F1")
    ax.set_ylim(0, 1)
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)


def sections(res, path):
    import matplotlib.pyplot as plt
    rows = [(k, v) for k, v in res["table3"].items() if k.startswith("Excl.") and v != "missing"]
    if not rows:
        return
    base = res["table1"].get("KnowledgeRAG-DDI")
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.barh([k for k, _ in rows], [v["id_f1"] for _, v in rows], color="#1f77b4")
    if base and base != "missing":
        ax.axvline(base["id_f1"], ls="--", color="k", lw=1, label="All sections")
        ax.legend(frameon=False)
    ax.set_xlabel("In-distribution binary F1")
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--tables", default=str(config.RESULTS / "corrected" / "tables.json"))
    ap.add_argument("--out", default=str(config.RESULTS / "corrected" / "figures"))
    a = ap.parse_args()
    res = json.loads(Path(a.tables).read_text())
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    slopegraph(res, out / "figure1_slopegraph.png")
    multiseed(res, out / "figure2_multiseed.png")
    fairness(res, out / "figure3_fairness.png")
    sections(res, out / "figure4_sections.png")
