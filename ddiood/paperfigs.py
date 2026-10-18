import argparse
import json
import random
import re
import shutil
import subprocess
from pathlib import Path

import numpy as np

from . import baselines, config, inputs, semeval
from . import evaluate2 as ev

INK = "#0b0b0b"
INK2 = "#52514e"
MUTED = "#7F7F7F"
GRID = "#e1e0d9"
BAND = "#efeee9"
SURFACE = "#ffffff"
SHORTCUT = "#6E6E6E"
DRUGBANK = "#AA3377"
BLUE = "#0077BB"
ORANGE = "#E8601C"
SERIES = [BLUE, BLUE, BLUE]
MARKERS = ["o", "s", "^"]
MM = 1 / 25.4
W_SINGLE, W_ONEHALF, W_DOUBLE = 90, 140, 190
BASE, SMALL = 7.5, 6.5
LW, MS = 0.9, 4.6
TOL = 6e-5
AUDIT = {}

SYSTEMS = [("b2sentence", "Sentence-trained"), ("b2mixed", "Mixed-input"), ("b1names", "Names-trained")]
LBL = dict(SYSTEMS)
COLOR = {s: SERIES[i] for i, (s, _) in enumerate(SYSTEMS)}
MARK = {s: MARKERS[i] for i, (s, _) in enumerate(SYSTEMS)}
NAMES_ONLY = {"b2sentence": ("test_empty", "ood_empty", "oodold_empty"),
              "b2mixed": ("test_empty", "ood_empty", "oodold_empty"),
              "b1names": ("test_names", "ood_names", "oodold_names")}
BACKBONE = {"biomedbert": "BiomedBERT", "bertbase": "BERT-base", "biobert": "BioBERT"}
EXAMPLE_PAIR = "Terbinafine decreases the clearance of caffeine by 19%."
FONT_FILES = ("lmroman10-regular.otf", "lmroman10-bold.otf", "lmroman10-italic.otf", "lmmono10-regular.otf")
FONT_FAMILY = "Latin Modern Roman"
FIGURES = ("figS_reference_systems", "figS_disjoint", "figS_masking", "seed_strip", "figS_roc")
BAND_COLORS = ("#efeee9", "#ebebeb")
THICK_LW = 2.2


def font_paths():
    found = []
    for name in FONT_FILES:
        p = config.ROOT / "fonts" / name
        if not p.exists() and shutil.which("kpsewhich"):
            r = subprocess.run(["kpsewhich", name], capture_output=True, text=True)
            if r.stdout.strip():
                p = Path(r.stdout.strip())
        if p.exists():
            found.append(p)
    return found


def style():
    import matplotlib as mpl
    from matplotlib import font_manager
    paths = font_paths()
    for p in paths:
        font_manager.fontManager.addfont(str(p))
    family = FONT_FAMILY if paths else "DejaVu Serif"
    if not paths:
        print("Latin Modern fonts not found; falling back to DejaVu Serif")
    mpl.rcParams.update({
        "font.family": "serif", "font.serif": [family, "DejaVu Serif"], "mathtext.fontset": "cm",
        "font.size": BASE, "axes.labelsize": BASE, "axes.titlesize": BASE, "xtick.labelsize": SMALL,
        "ytick.labelsize": BASE, "legend.fontsize": SMALL, "axes.edgecolor": MUTED, "axes.linewidth": 0.6,
        "axes.labelcolor": INK, "xtick.color": INK2, "ytick.color": INK, "text.color": INK,
        "xtick.major.width": 0.6, "ytick.major.width": 0.6, "xtick.major.size": 2.5, "ytick.major.size": 0,
        "axes.spines.top": False, "axes.spines.right": False, "figure.dpi": 150, "savefig.dpi": 300,
        "pdf.fonttype": 42, "ps.fonttype": 42, "figure.facecolor": SURFACE, "axes.facecolor": SURFACE,
        "legend.frameon": False, "axes.unicode_minus": True, "path.simplify": False,
    })
    return family


def make_fig(w_mm, h_mm, left, right, top, bottom, ncols=1, nrows=1, wspace=0.0, hspace=0.0, **kw):
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(nrows, ncols, figsize=(w_mm * MM, h_mm * MM), squeeze=False, **kw)
    fig.subplots_adjust(left=left / w_mm, right=1 - right / w_mm, top=1 - top / h_mm, bottom=bottom / h_mm,
                        wspace=wspace, hspace=hspace)
    return fig, axes.ravel()


def band_audit(fig, name, bands=0, thick=0):
    from matplotlib.colors import to_hex
    found = sum(1 for ax in fig.axes for p in ax.patches if to_hex(p.get_facecolor()).lower() in BAND_COLORS
                and p.get_facecolor()[3] > 0)
    heavy = sum(1 for ax in fig.axes for ln in ax.lines if abs(ln.get_linewidth() - THICK_LW) < 0.05 and ln.get_visible())
    if found != bands or (thick is not None and heavy != thick):
        raise AssertionError(f"{name}: {found} equivalence bands and {heavy} thick 90% bars drawn; "
                             f"allowed {bands} and {thick}")
    return {"bands": found, "thick_90_bars": heavy}


def save(fig, out, name, bands=0, thick=0):
    import matplotlib.pyplot as plt
    AUDIT[name] = band_audit(fig, name, bands, thick)
    out.mkdir(parents=True, exist_ok=True)
    fig.savefig(out / f"{name}.pdf", metadata={"CreationDate": None, "Creator": None, "Producer": None})
    fig.savefig(out / f"{name}.png", dpi=300, metadata={"Software": None})
    plt.close(fig)


def seed_text(seeds):
    s = sorted(seeds)
    return f"seed {s[0]}" if len(s) == 1 else f"{len(s)} seeds ({', '.join(map(str, s))}), scores averaged"


class Data:
    def __init__(self, preds, eval_dir, baselines_json, boot):
        self.boot = boot
        self.truth = ev.load_truth()
        self.jobs = ev.load_jobs(preds, self.truth)
        self.aggs = ev.aggregate(self.jobs)
        self.byname = {j["name"]: j for j in self.jobs}
        test = semeval.load_pairs("test")
        if [int(r["label_id"] != 0) for r in test] != list(self.truth.test_y):
            raise ValueError("SemEval test order differs from the evaluation truth")
        self.sid = np.asarray([r["sentence_id"] for r in test])
        eval_dir = Path(eval_dir)
        self.eval_dir = eval_dir
        self.tables = json.loads((eval_dir / "tables.json").read_text())
        self.decisions = json.loads((eval_dir / "decisions.json").read_text())
        self.drugbank = {r["cohort"]: r for r in json.loads((eval_dir / "drugbank_lookup.json").read_text())["rows"]}
        self.baselines = json.loads(Path(baselines_json).read_text())
        self.seedrows = {(r["group"], r["key"]): r for r in self.tables["seeds"]}
        self.jobrows = {(r["job"], r["key"]): r for r in self.tables["per_job"]}
        self.cohortrows = {(r["group"], r["key"], r["cohort"], r["tier"]): r for r in self.tables["ood_cohorts"]}
        self.disjointrows = {(r["job"], r["key"], r["subset"]): r for r in self.tables["disjoint"]}
        self.checks = {"seed_aggregated": 0, "two_way_ci": 0, "older_clean_pooled": 0, "per_job": 0, "disjoint": 0}

    def gk(self, system, model="biomedbert", split="standard", variant="hybrid", k=5, chars=100):
        key = (system, model, split, variant, k, chars)
        return key if key in self.aggs else None

    def seeds(self, g):
        return self.aggs[g]["seeds"] if g in self.aggs else []

    def draws(self, kind, y, p, g, partner):
        if kind == "test":
            return ev.boot_auroc(y, p, self.sid, None, self.boot), "one-way cluster bootstrap over SemEval sentences"
        if kind == "swapood":
            return ev.boot_auroc(y, p, g, None, self.boot), "one-way cluster bootstrap over novel drugs"
        return ev.boot_auroc(y, p, g, partner, self.boot), "two-way cluster bootstrap over OOD drugs and partners"

    def cell(self, g, key, cohort=None):
        a = self.aggs.get(g)
        e = a["evals"].get(key) if a else None
        if e is None:
            return None
        y, p, gr, pa = e["y"], e["p"], e["g"], e["partner"]
        if cohort == "older_clean":
            m = e["clean"]
            y, p, gr, pa = y[m], p[m], gr[m], pa[m]
        d, how = self.draws(e["kind"], y, p, gr, pa)
        lo, hi = ev.interval(d)
        c = {"auroc": ev.auroc(y, p), "lo": lo, "hi": hi, "n": int(len(y)), "seeds": list(e["seeds"]),
             "group": ev.label(g), "key": key, "cohort": cohort or e["kind"], "ci": how}
        self.verify(c, e["kind"])
        return c

    def verify(self, c, kind):
        if c["cohort"] == "older_clean":
            r = self.cohortrows.get((c["group"], c["key"], "older_clean", "A"))
            if r is not None:
                assert abs(r["auroc_pooled"] - c["auroc"]) < TOL, ("older_clean", c["group"], c["key"])
                self.checks["older_clean_pooled"] += 1
            c["source"] = "computed by ddiood.paperfigs (pooled AUROC check: tables.json ood_cohorts auroc_pooled)"
            return
        r = self.seedrows.get((c["group"], c["key"]))
        assert r is not None, (c["group"], c["key"])
        assert abs(r["auroc"] - c["auroc"]) < TOL, (c["group"], c["key"], r["auroc"], c["auroc"])
        self.checks["seed_aggregated"] += 1
        if kind in ("ood", "oodold"):
            assert abs(r["auroc2_lo"] - c["lo"]) < TOL and abs(r["auroc2_hi"] - c["hi"]) < TOL, (c["group"], c["key"])
            self.checks["two_way_ci"] += 1
            c["source"] = "tables.json seeds (auroc, auroc2_lo, auroc2_hi)"
        else:
            c["source"] = "tables.json seeds (auroc); interval computed by ddiood.paperfigs"

    def job_auroc(self, name, key):
        j = self.byname[name]
        e = j["evals"][key]
        v = ev.auroc(e["y"], e["p"])
        r = self.jobrows[(name, key)]
        assert abs(r["auroc"] - v) < TOL, (name, key)
        self.checks["per_job"] += 1
        return v

    def disjoint_cell(self, name, key, subset):
        j = self.byname[name]
        e = j["evals"][key]
        m = np.zeros(len(e["y"]), bool)
        m[j["unseen"]] = True
        if subset == "seen":
            m = ~m
        y, p = e["y"][m], e["p"][m]
        lo, hi = ev.interval(ev.boot_auroc(y, p, self.sid[m], None, self.boot))
        c = {"auroc": ev.auroc(y, p), "lo": lo, "hi": hi, "n": int(len(y)), "job": name, "key": key,
             "subset": subset, "source": "tables.json disjoint (auroc); interval computed by ddiood.paperfigs"}
        r = self.disjointrows[(name, key, subset)]
        assert abs(r["auroc"] - c["auroc"]) < TOL and r["n"] == c["n"], (name, key, subset)
        self.checks["disjoint"] += 1
        return c

    def baseline(self, setname, name):
        r = self.baselines[setname]["baselines"][name]
        ci = r["auroc_ci95"]
        return {"auroc": r["auroc"], "lo": ci["lower"], "hi": ci["upper"], "n": self.baselines[setname]["n"],
                "source": f"results/corrected/baselines.json {setname}.baselines.{name} (auroc, auroc_ci95)"}

    def drugbank_cell(self, cohort):
        r = self.drugbank[cohort]
        return {"auroc": r["auroc"], "lo": r["auroc2_lo"], "hi": r["auroc2_hi"], "n": r["n"],
                "source": f"drugbank_lookup.json cohort {cohort} (auroc, auroc2_lo, auroc2_hi)"}


def whisker(ax, pos, c, color, marker, hollow=False, horizontal=True, zorder=3, ms=MS):
    if horizontal:
        ax.plot([c["lo"], c["hi"]], [pos, pos], color=color, lw=LW, solid_capstyle="butt", zorder=zorder)
        mx, my = c["auroc"], pos
    else:
        ax.plot([pos, pos], [c["lo"], c["hi"]], color=color, lw=LW, solid_capstyle="butt", zorder=zorder)
        mx, my = pos, c["auroc"]
    if hollow or marker == "^":
        ax.plot(mx, my, marker, ms=ms, mfc=SURFACE, mec=color, mew=1.0, zorder=zorder + 1)
    else:
        ax.plot(mx, my, marker, ms=ms, mfc=color, mec=SURFACE, mew=0.6, zorder=zorder + 1)


def legend_handle(color, marker, hollow=False):
    from matplotlib.lines import Line2D
    hollow = hollow or marker == "^"
    return Line2D([0], [0], color=color, lw=LW, marker=marker, ms=MS, mfc=SURFACE if hollow else color,
                  mec=color if hollow else SURFACE, mew=1.0 if hollow else 0.6)


def band(ax, vertical=True, chance=0.5):
    if vertical:
        ax.axvline(chance, color=MUTED, lw=0.7, ls=(0, (3, 2)), zorder=1)
    else:
        ax.axhline(chance, color=MUTED, lw=0.7, ls=(0, (3, 2)), zorder=1)


def panel_title(ax, letter, title, dx=9, dy=4):
    ax.annotate(letter, xy=(0, 1), xycoords="axes fraction", xytext=(0, dy), textcoords="offset points",
                fontsize=BASE + 0.5, fontweight="bold", color=INK, ha="left", va="bottom")
    ax.annotate(title, xy=(0, 1), xycoords="axes fraction", xytext=(dx, dy), textcoords="offset points",
                fontsize=BASE, color=INK, ha="left", va="bottom")


def note(ax, text, x=0.995, y=0.02, ha="right", va="bottom"):
    ax.text(x, y, text, transform=ax.transAxes, ha=ha, va=va, fontsize=SMALL, color=INK2)


def bracket(ax, y0, y1, label, xfrac, tick=0.008):
    tr = ax.get_yaxis_transform()
    ax.plot([xfrac - tick, xfrac, xfrac, xfrac - tick], [y0, y0, y1, y1], color=INK2, lw=0.6, transform=tr,
            clip_on=False, solid_capstyle="butt")
    ax.text(xfrac + 0.012, (y0 + y1) / 2, label, transform=tr, ha="left", va="center", fontsize=SMALL,
            color=INK2, linespacing=1.25, clip_on=False)


def value_label(ax, c, y, digits=2, dx=0.012, color=INK2):
    ax.text(c["hi"] + dx, y, f"{c['auroc']:.{digits}f}", ha="left", va="center", fontsize=SMALL, color=color,
            clip_on=False)


def section_labels(fig, ax, items):
    from matplotlib.transforms import blended_transform_factory
    tr = blended_transform_factory(fig.transFigure, ax.transData)
    for y, text in items:
        ax.text(2 / (fig.get_figwidth() / MM), y, text, transform=tr, ha="left", va="center", fontsize=BASE,
                fontweight="bold", color=INK)


def forest_axis(ax, xlim, ticks, ylim, xlabel="AUROC"):
    ax.set_xlim(*xlim)
    ax.set_xticks(ticks)
    ax.set_ylim(*ylim)
    ax.set_xlabel(xlabel)
    ax.grid(axis="x", color=GRID, lw=0.5, zorder=0)
    ax.spines["left"].set_visible(False)


def examples(seed=0):
    rows = [r for r in semeval.load_pairs("test") if r["label_id"] > 0 and r["sentence"].strip() == EXAMPLE_PAIR]
    p = rows[0]
    rng = random.Random(seed)
    a, b = inputs.pseudo_word(rng), inputs.pseudo_word(rng)
    sw = inputs.swapped(p, a, b)["sentence"].strip()
    return {"sentence": p["sentence"].strip(), "pseudo": sw[0].upper() + sw[1:],
            "names": f"{p['drug_a']} ; {p['drug_b']}", "drug_a": p["drug_a"], "drug_b": p["drug_b"]}


def fig_reference(data, out):
    gq, gb = data.gk("names", "qwen"), data.gk("names", "biomistral")
    rq, rb = data.gk("rag", "qwen"), data.gk("rag", "biomistral")
    mix = data.gk("b2mixed")
    krag = data.gk("krag", variant="hybrid", chars=400)
    pos = data.gk("krag", variant="contaminated", chars=400)
    lsm = shortcut_scores(data)
    DB, SH, SF, QW, BM, FT, KR, PC = ((DRUGBANK, "D", False), (SHORTCUT, "o", True), (SHORTCUT, "o", False), (ORANGE, "v", False),
                                     (ORANGE, "v", True), (BLUE, "s", False), (BLUE, "p", False), (BLUE, "p", True))
    rows = [
        ("DrugBank lookup", DB, {"novel": lambda: data.drugbank_cell("novel"),
                                  "older": lambda: data.drugbank_cell("older_full"),
                                  "older_clean": lambda: data.drugbank_cell("older_clean")}),
        ("Label string match", SH, {"novel": lambda: data.baseline("novel", "non_di_label_string_match"),
                                     "older": lambda: data.baseline("older", "non_di_label_string_match"),
                                     "older_clean": lambda: lsm["older_clean"]["non_di_label_string_match"]}),
        ("Novel-drug prior (shortcut)", SF, {"novel": lambda: data.baseline("novel", "novel_drug_prior"),
                                              "older": lambda: data.baseline("older", "novel_drug_prior"),
                                              "older_clean": lambda: lsm["older_clean"]["novel_drug_prior"]}),
        None,
        ("Qwen2.5-7B, names only", QW, {"novel": lambda: data.cell(gq, "ood"), "older": lambda: data.cell(gq, "oodold"),
                                         "older_clean": lambda: data.cell(gq, "oodold", "older_clean")}),
        ("BioMistral-7B, names only", BM, {"novel": lambda: data.cell(gb, "ood"),
                                            "older": lambda: data.cell(gb, "oodold"),
                                            "older_clean": lambda: data.cell(gb, "oodold", "older_clean")}),
        ("Qwen2.5-7B, with passages", QW, {"novel": lambda: data.cell(rq, "ood")}),
        ("BioMistral-7B, with passages", BM, {"novel": lambda: data.cell(rb, "ood")}),
        None,
        ("Mixed-input, names only", FT, {"novel": lambda: data.cell(mix, "ood_empty"),
                                         "older": lambda: data.cell(mix, "oodold_empty"),
                                         "older_clean": lambda: data.cell(mix, "oodold_empty", "older_clean")}),
        ("Retrieval-augmented (H6)", KR, {"novel": lambda: data.cell(krag, "ood")}),
        ("Positive control (H5)", PC, {"novel": lambda: data.cell(pos, "ood")}),
    ]
    ys, seps, y = [], [], 0.0
    for r in rows:
        if r is None:
            seps.append(y - 0.225)
            y += 0.55
            ys.append(None)
        else:
            ys.append(y)
            y += 1.0
    ymax = y - 1.0
    H, L = 92, 46
    fig, axes = make_fig(W_DOUBLE, H, L, 9, 13, 11, ncols=3, wspace=0.16)
    panels = (("novel", "A", "Novel (438 pairs)"), ("older", "B", "Older (1,944 pairs)"),
              ("older_clean", "C", "Older-clean (1,832 pairs)"))
    table = {}
    for ax, (cohort, letter, title) in zip(axes, panels):
        band(ax)
        for r, yv in zip(rows, ys):
            if r is None:
                continue
            label, (color, marker, hollow), fns = r
            if cohort not in fns:
                ax.text(0.312, yv, "not run", ha="left", va="center", fontsize=SMALL, color=INK2)
                continue
            c = fns[cohort]()
            whisker(ax, yv, c, color, marker, hollow=hollow)
            value_label(ax, c, yv, digits=3)
            table[f"{cohort} | {label}"] = c
        for yv in seps:
            ax.axhline(yv, color=GRID, lw=0.6, zorder=1)
        panel_title(ax, letter, title)
        forest_axis(ax, (0.3, 1.0), np.arange(0.3, 1.01, 0.1), (ymax + 0.6, -0.6), xlabel="")
        assert sum(1 for ln in ax.lines if list(ln.get_xdata()) == [0.5, 0.5]) == 1, f"chance line missing in panel {letter}"
        ax.set_yticks([])
    axes[0].set_yticks([yv for yv in ys if yv is not None], [r[0] for r in rows if r is not None])
    fig.text((L + (W_DOUBLE - L - 9) / 2) / W_DOUBLE, 2 / H, "AUROC", ha="center", va="bottom", fontsize=BASE)
    handles = [legend_handle(*DB[:2]), legend_handle(*SH[:2], hollow=SH[2]), legend_handle(*SF[:2], hollow=SF[2]),
               legend_handle(ORANGE, "v"), legend_handle(ORANGE, "v", hollow=True), legend_handle(BLUE, "s"),
               legend_handle(BLUE, "p"), legend_handle(BLUE, "p", hollow=True)]
    fig.legend(handles, ["DrugBank", "Rule baseline", "Shortcut", "Qwen2.5-7B", "BioMistral-7B", "Mixed-input", "H6", "H5"],
               loc="upper right", bbox_to_anchor=(1 - 2 / W_DOUBLE, 1 - 0.8 / H), ncol=8, handlelength=1.2,
               handletextpad=0.25, columnspacing=0.6, borderpad=0, borderaxespad=0)
    save(fig, out, "figS_reference_systems")
    return table


def fig_disjoint(data, out):
    rows = [("Sentence-trained", "b2sentence-biomedbert-disjoint-s42", "test_sentence", "sentence"),
            ("Mixed-input", "b2mixed-biomedbert-disjoint-s42", "test_sentence", "sentence"),
            ("Sentence-trained", "b2sentence-biomedbert-disjoint-s42", "test_empty", "names only"),
            ("Mixed-input", "b2mixed-biomedbert-disjoint-s42", "test_empty", "names only"),
            ("Names-trained", "b1names-biomedbert-disjoint-s42", "test_names", "names only")]
    rows = [r for r in rows if r[1] in data.byname]
    H, L = 62, 44
    fig, (ax,) = make_fig(W_ONEHALF, H, L, 12, 9, 11)
    band(ax)
    table = {}
    ypos = [0, 1, 2.45, 3.45, 4.45]
    for (sysname, job, key, fmt), y in zip(rows, ypos):
        for subset, dy, color, marker, hollow in (("seen", -0.14, BLUE, "o", True), ("unseen", 0.14, BLUE, "o", False)):
            c = data.disjoint_cell(job, key, subset)
            whisker(ax, y + dy, c, color, marker, hollow=hollow)
            value_label(ax, c, y + dy)
            table[f"{sysname} | {fmt} | {subset}"] = c
    forest_axis(ax, (0.3, 1.0), np.arange(0.3, 1.01, 0.1), (ypos[len(rows) - 1] + 0.6, -0.95))
    ax.set_yticks(ypos[:len(rows)], [r[0] for r in rows])
    ax.axhline(1.72, color=GRID, lw=0.6, zorder=1)
    section_labels(fig, ax, [(-0.62, "Sentence input"), (1.95, "Names only")])
    fig.text(2 / W_ONEHALF, 1.5 / H, "BiomedBERT, drug-disjoint training, seed 42", ha="left", va="bottom",
             fontsize=SMALL, color=INK2)
    handles = [legend_handle(BLUE, "o", hollow=True), legend_handle(BLUE, "o")]
    fig.legend(handles, ["Test instances, both drugs seen in training", "Test instances with a held-out drug"],
               loc="upper center", bbox_to_anchor=(0.5, 1 - 0.8 / H), ncol=2, handlelength=2.0,
               handletextpad=0.4, columnspacing=1.2, borderpad=0, borderaxespad=0)
    save(fig, out, "figS_disjoint")
    return table


def fig_masking(data, out):
    import matplotlib.pyplot as plt
    masks = [r for r in data.tables["masking"] if r["model"] == "biomedbert" and r["split"] == "standard"]
    swaps = [r for r in data.tables["swap"] if r["model"] == "biomedbert" and r["split"] == "standard"]
    systems = [("b2sentence", "Sentence-trained", COLOR["b2sentence"], "o", "H2a"),
               ("b2masked", "Masked-trained", BLUE, "D", "H2b")]
    H, L = 74, 40
    fig = plt.figure(figsize=(W_DOUBLE * MM, H * MM))
    gs = fig.add_gridspec(1, 2, left=L / W_DOUBLE, right=1 - 6 / W_DOUBLE, top=1 - 12 / H, bottom=12 / H,
                          wspace=0.62)
    ax, bx = fig.add_subplot(gs[0]), fig.add_subplot(gs[1])
    table = {}
    ylab = []
    for i, (s, name, color, marker, hid) in enumerate(systems):
        rs = [r for r in masks if r["system"] == s]
        for j, (field, inp) in enumerate((("f1_sentence", "annotated sentence"), ("f1_masked", "both drugs masked"))):
            y = i * 2.4 + j
            vals = [r[field] for r in rs]
            ax.plot(vals, [y] * len(vals), marker, ms=3.0, mfc=SURFACE, mec=color, mew=0.8, zorder=3)
            m = float(np.mean(vals))
            ax.plot([m, m], [y - 0.3, y + 0.3], color=color, lw=1.6, solid_capstyle="butt", zorder=4)
            ylab.append((y, f"{name},\n{inp}"))
            table[f"{name} | {field}"] = {"seeds": {r["seed"]: r[field] for r in rs}, "mean": m,
                                          "source": "tables.json masking"}
        d = data.decisions[hid]
        ratios = sorted(r["ratio"] for r in rs)
        if hid == "H2b":
            med = re.search(r"median ratio ([0-9.]+)", d["detail"]).group(1)
            lo, hi = re.search(r"per-seed ratio range ([0-9.]+) to ([0-9.]+)", d["detail"]).groups()
            for txt, v in ((med, float(np.median(ratios))), (lo, ratios[0]), (hi, ratios[-1])):
                assert abs(float(txt) - v) < 1e-3, (hid, txt, v)
            label = f"{hid}: median ratio {med},\nseeds {lo} to {hi}, {d['decision']}*"
        else:
            label = f"{hid}: mean ratio {d['value']['ratio']:.3f}, {d['decision']}"
        ax.text(0.03 if i == 0 else 0.03, i * 2.4 + 0.5, label,
                ha="left", va="center", fontsize=SMALL, color=INK, linespacing=1.15)
        table[f"{hid} decision"] = {"value": d["value"], "decision": d["decision"], "source": f"decisions.json {hid}",
                                    "median_ratio": float(np.median(ratios)), "ratio_range": [ratios[0], ratios[-1]],
                                    "ratio_source": "tables.json masking"}
    ax.set_xlim(0, 0.8)
    ax.set_xticks(np.arange(0, 0.81, 0.2))
    ax.set_ylim(3.9, -0.6)
    ax.set_yticks([y for y, _ in ylab], [t for _, t in ylab], linespacing=1.15, fontsize=SMALL)
    ax.set_xlabel("Binary F1 on SemEval test")
    ax.grid(axis="x", color=GRID, lw=0.5, zorder=0)
    ax.spines["left"].set_visible(False)
    panel_title(ax, "A", "Masked over unmasked F1")
    kinds = [("vocab", "Other SemEval drugs"), ("novel", "Novel drugs"), ("pseudo", "Pseudo-words")]
    bx.axvline(0.10, color=MUTED, lw=0.7, ls=(0, (3, 2)), zorder=1)
    bx.axvline(0.25, color=MUTED, lw=0.7, ls=(0, (1, 1.5)), zorder=1)
    for k, (kind, klab) in enumerate(kinds):
        for i, (s, name, color, marker, hid) in enumerate(systems):
            y = k + (i - 0.5) * 0.34
            vals = [r["flip_rate"] for r in swaps if r["system"] == s and r["swap"] == kind]
            assert abs(float(np.mean(vals)) - data.decisions[hid]["value"][kind]) < TOL, (hid, kind)
            bx.plot(vals, [y] * len(vals), marker, ms=3.0, mfc=SURFACE, mec=color, mew=0.8, zorder=3)
            m = float(np.mean(vals))
            bx.plot([m, m], [y - 0.14, y + 0.14], color=color, lw=1.6, solid_capstyle="butt", zorder=4)
            table[f"{name} | flip {kind}"] = {"seeds": vals, "mean": m,
                                             "source": f"tables.json swap (flip_rate); mean equals decisions.json {hid}"}
    bx.set_xlim(0, 0.3)
    bx.set_xticks(np.arange(0, 0.31, 0.05))
    bx.set_ylim(len(kinds) - 0.4, -0.75)
    bx.set_yticks(range(len(kinds)), [k[1] for k in kinds])
    bx.set_xlabel("Share of binary predictions that flip")
    bx.grid(axis="x", color=GRID, lw=0.5, zorder=0)
    bx.spines["left"].set_visible(False)
    bx.text(0.05, -0.62, "support\n(< 0.10)", ha="center", va="center", fontsize=SMALL, color=INK2, linespacing=1.1)
    bx.text(0.255, -0.62, "falsify\n(> 0.25)", ha="left", va="center", fontsize=SMALL, color=INK2, linespacing=1.1)
    panel_title(bx, "B", "Name swaps, sentence input")
    from matplotlib.lines import Line2D
    handles = [Line2D([0], [0], color=c, lw=1.6, marker=m, ms=3.0, mfc=SURFACE, mec=c, mew=0.8)
               for _, _, c, m, _ in systems]
    fig.legend(handles, ["Sentence-trained", "Masked-trained"], loc="upper right", bbox_to_anchor=(1 - 2 / W_DOUBLE, 1 - 0.8 / H),
               ncol=2, handlelength=2.0, handletextpad=0.4, columnspacing=1.2, borderpad=0, borderaxespad=0)
    fig.text(2 / W_DOUBLE, 1 - 1.2 / H, "BiomedBERT, open marks are seeds 1, 2, 3, 4, 42; bars are seed means",
             ha="left", va="top", fontsize=SMALL, color=INK2)
    fig.text(2 / W_DOUBLE, 0.8 / H, f"* Planned H2b statistic: seed-mean ratio {data.decisions['H2b']['value']['ratio']:.3f}, "
             "inflated by seed 1; the decision is the same.", ha="left", va="bottom", fontsize=SMALL, color=INK2)
    save(fig, out, "figS_masking")
    return table


def fig_seed_strip(data, out):
    rows = [("b2sentence", "biomedbert", "ood_empty", "Sentence-trained, BiomedBERT", COLOR["b2sentence"], "o"),
            ("b2mixed", "biomedbert", "ood_empty", "Mixed-input, BiomedBERT", COLOR["b2mixed"], "s"),
            ("b1names", "biomedbert", "ood_names", "Names-trained, BiomedBERT", COLOR["b1names"], "^"),
            ("b2sentence", "bertbase", "ood_empty", "Sentence-trained, BERT-base", COLOR["b2sentence"], "o"),
            ("b2mixed", "bertbase", "ood_empty", "Mixed-input, BERT-base", COLOR["b2mixed"], "s"),
            ("b2masked", "biomedbert", "ood_empty", "Masked-trained, BiomedBERT", BLUE, "D"),
            ("krag", "biomedbert", "ood", "Retrieval-augmented (H6)", BLUE, "p"),
            ("krag-contaminated", "biomedbert", "ood", "Positive control (H5)", BLUE, "p")]
    H, L = 70, 50
    fig, (ax,) = make_fig(W_ONEHALF, H, L, 4, 8, 11)
    band(ax)
    table = {}
    used = []
    for i, (s, model, key, label, color, marker) in enumerate(rows):
        if s == "krag":
            g = data.gk("krag", variant="hybrid", chars=400)
        elif s == "krag-contaminated":
            g = data.gk("krag", variant="contaminated", chars=400)
        else:
            g = data.gk(s, model)
        if g is None or len(data.seeds(g)) < 2:
            continue
        a = data.aggs[g]
        vals = {}
        for j in a["jobs"]:
            if key in j["evals"]:
                vals[j["cfg"]["seed"]] = data.job_auroc(j["name"], key)
        r = data.seedrows[(ev.label(g), key)]
        mean = r["seed_auroc_mean"]
        assert abs(mean - float(np.mean(list(vals.values())))) < TOL, label
        y = len(used)
        if s == "krag":
            ax.plot(list(vals.values()), [y] * len(vals), "p", ms=2.6, mfc=color, mec=color, mew=0.3, zorder=3)
        else:
            ax.plot(list(vals.values()), [y] * len(vals), marker, ms=3.4, mfc=SURFACE, mec=color, mew=0.8, zorder=3)
        ax.plot([mean, mean], [y - 0.3, y + 0.3], color=color, lw=1.6, solid_capstyle="butt", zorder=4)
        used.append(label)
        table[label] = {"per_seed": vals, "seed_auroc_mean": mean, "seed_auroc_sd": r["seed_auroc_sd"],
                        "source": "tables.json per_job (auroc) and seeds (seed_auroc_mean)"}
    forest_axis(ax, (0.3, 0.8), np.arange(0.3, 0.81, 0.1), (len(used) - 0.4, -0.9), xlabel="Pooled AUROC on Novel, one point per seed")
    ax.set_yticks(range(len(used)), used, fontsize=SMALL)
    fig.text(1 - 4 / W_ONEHALF, 1 - 1.2 / H, "one mark per seed (1, 2, 3, 4, 42; H6 filled); bar: mean of the per-seed AUROCs",
             ha="right", va="top", fontsize=SMALL, color=INK2)
    save(fig, out, "seed_strip")
    return table


def baseline_score_cache():
    return config.RESULTS / "corrected" / "baseline_scores.json"


def shortcut_scores(data):
    path = baseline_score_cache()
    if path.exists():
        raw = json.loads(path.read_text())
    else:
        lk = json.loads((config.ARTIFACTS / "vocab" / "drug_lookup.json").read_text())
        ctx = baselines.Context(lk)
        raw = {}
        for set_name, fname in (("novel", "ood_pairs.csv"), ("older", "ood_old_pairs.csv")):
            pairs = baselines.read_pairs(config.RESULTS / "corrected" / fname)
            sc = baselines.score_all(pairs, ctx, None)
            raw[set_name] = {k: [float(v) for v in sc[k]] for k in ("novel_drug_prior", "non_di_label_string_match")}
        path.write_text(json.dumps(raw))
    out = {}
    for set_name, tag in (("novel", "ood"), ("older", "oodold"), ("older_clean", "oodold")):
        s = data.truth.sets[tag]
        m = np.ones(len(s["y"]), bool) if set_name != "older_clean" else s["clean"]
        y, g, q = np.asarray(s["y"])[m], np.asarray(s["g"])[m], np.asarray(s["partner"])[m]
        out[set_name] = {}
        for name, v in raw["older" if set_name == "older_clean" else set_name].items():
            sc = np.asarray(v)[m]
            point = ev.auroc(y, sc)
            if set_name != "older_clean":
                ref = data.baselines[set_name]["baselines"][name]["auroc"]
                assert abs(ref - point) < 1e-9, (set_name, name, ref, point)
            lo, hi = ev.interval(ev.boot_auroc(y, sc, g, q, data.boot))
            out[set_name][name] = {"auroc": point, "lo": lo, "hi": hi, "n": int(len(y)), "scores": sc, "y": y,
                                   "source": "computed by ddiood.paperfigs from results/corrected/baseline_scores.json, "
                                             "two-way cluster bootstrap"}
    return out


def fig_roc(data, out):
    from sklearn.metrics import roc_curve
    sc = shortcut_scores(data)
    styles = {"b2sentence": "-", "b2mixed": (0, (4, 2)), "b1names": (0, (1, 1.5))}
    H, L, R, T, B = 104, 13, 4, 11, 14
    side = 80
    fig, axes = make_fig(W_DOUBLE, H, L, R, T, B, ncols=2, wspace=(W_DOUBLE - L - R - 2 * side) / side)
    table = {}
    for ax, (which, kind, letter, title) in zip(axes, (("novel", 1, "A", "Novel, names only"),
                                                       ("older", 2, "B", "Older, names only"))):
        y = np.asarray(data.truth.sets["ood" if which == "novel" else "oodold"]["y"])
        panel_title(ax, letter, f"{title} (n = {len(y):,})", dx=10)
        ax.plot([0, 1], [0, 1], color=MUTED, lw=0.7, ls=(0, (3, 2)), zorder=1)
        for s, mlabel in SYSTEMS:
            g = data.gk(s)
            key = NAMES_ONLY[s][kind]
            e = data.aggs[g]["evals"][key]
            c = data.cell(g, key)
            f, t, _ = roc_curve(e["y"], e["p"])
            ax.plot(f, t, color=COLOR[s], lw=1.1, ls=styles[s], label=f"{mlabel} ({c['auroc']:.3f})")
            table[f"{which} | {mlabel}"] = c
        ref = sc[which]["non_di_label_string_match"]
        f, t, _ = roc_curve(ref["y"], ref["scores"])
        ax.plot(f, t, color=SHORTCUT, lw=1.1, label=f"Label string match, reference ({ref['auroc']:.3f})", zorder=2)
        table[f"{which} | label string match"] = {k: v for k, v in ref.items() if k not in ("scores", "y")}
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_box_aspect(1)
        ax.set_xticks(np.arange(0, 1.01, 0.2))
        ax.set_yticks(np.arange(0, 1.01, 0.2))
        ax.set_xlabel("False positive rate")
        ax.grid(color=GRID, lw=0.5)
        ax.legend(loc="lower right", bbox_to_anchor=(0.99, 0.08), fontsize=SMALL, handlelength=3.0, borderpad=0.2)
        note(ax, "BiomedBERT, " + seed_text(data.seeds(data.gk("b2mixed"))), x=0.985, y=0.015)
    axes[0].set_ylabel("True positive rate")
    save(fig, out, "figS_roc")
    return table


def jsonable(o):
    if isinstance(o, dict):
        return {str(k): jsonable(v) for k, v in o.items() if k not in ("scores", "y")}
    if isinstance(o, (list, tuple)):
        return [jsonable(v) for v in o]
    if isinstance(o, np.generic):
        return o.item()
    if isinstance(o, np.ndarray):
        return o.tolist()
    return o


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--preds", default=str(config.RESULTS / "revision" / "preds"))
    ap.add_argument("--eval", default=str(config.RESULTS / "revision" / "eval"))
    ap.add_argument("--baselines", default=str(config.RESULTS / "corrected" / "baselines.json"))
    ap.add_argument("--out", default=str(config.RESULTS / "revision" / "figures"))
    ap.add_argument("--boot", type=int, default=1000)
    a = ap.parse_args(argv)
    family = style()
    out = Path(a.out)
    data = Data(a.preds, a.eval, a.baselines, a.boot)
    tables = {"font": family, "boot": a.boot,
              "seeds": {ev.label(g): v["seeds"] for g, v in data.aggs.items()},
              "figS_reference_systems": fig_reference(data, out),
              "figS_disjoint": fig_disjoint(data, out),
              "figS_masking": fig_masking(data, out),
              "seed_strip": fig_seed_strip(data, out),
              "figS_roc": fig_roc(data, out)}
    tables["band_audit"] = dict(AUDIT)
    tables["checks_against_eval"] = data.checks
    (out / "figure_data.json").write_text(json.dumps(jsonable(tables), indent=1))
    missing = [f for f in FIGURES for ext in ("pdf", "png") if not (out / f"{f}.{ext}").exists()]
    if missing:
        raise SystemExit(f"missing figures: {missing}")
    print(json.dumps({"font": family, "figures": len(FIGURES), "checks_against_eval": data.checks}))


if __name__ == "__main__":
    main()
