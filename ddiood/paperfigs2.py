import argparse
import json
import re
import shutil
import subprocess
import textwrap
import tempfile
from pathlib import Path

import numpy as np

from . import amend7_analysis as aa
from . import config, semeval, stats
from . import evaluate2 as ev
from . import paperfigs as pf
from .baselines import drugbank_scores
from .metrics import binary_f1

SEMEVAL = "#0077BB"
SEMEVAL_TINT = "#99C9E4"
EXTERNAL = "#E8601C"
REF = "#1A1A1A"
DRUGBANK = "#AA3377"
SHORTCUT = "#6E6E6E"
RULE = "#595959"
BAND = "#EBEBEB"
NEUTRAL = "#D9D9D9"
TEXT = "#1A1A1A"
TEXT2 = "#595959"
GRID = "#E6E6E6"
SPINE = "#8C8C8C"
SURFACE = "#FFFFFF"
ROLES = {"SEMEVAL": SEMEVAL, "SEMEVAL_TINT": SEMEVAL_TINT, "EXTERNAL": EXTERNAL, "REF": REF, "SHORTCUT": SHORTCUT,
         "RULE": RULE, "BAND": BAND}
ROLE_LABEL = {"SEMEVAL": "trained on SemEval labels", "EXTERNAL": "not trained on SemEval labels",
              "REF": "external reference", "SHORTCUT": "shortcut baseline"}
BAND_HYPOTHESES = ("H1", "H1-pooled", "H1-novel", "H4", "H6")
BAND_LABEL = "equivalence margin"
H1_CELL = ("b2mixed", "biomedbert", "older_clean", "names")
C8 = ("OOD labels are unvalidated label mentions (the E8 oracle check failed); OOD AUROC measures agreement with that "
      "target, not interaction knowledge.")

MARKER = {"b2sentence": ("o", False), "b2mixed": ("s", False), "b1names": ("^", True), "b2masked": ("D", True),
          "krag": ("p", False), "hub": ("o", True), "inhouse": ("o", False), "drugbank": ("D", False),
          "qwen": ("v", False), "biomistral": ("v", True), "e7": ("s", False), "e8": ("v", False),
          "lsm": ("D", True), "shortcut": ("o", True), "h5": ("p", True)}

MM = 1 / 25.4
W_SINGLE, W_ONEHALF, W_DOUBLE = pf.W_SINGLE, pf.W_ONEHALF, pf.W_DOUBLE
BASE, SMALL, LETTER = 8, 7, 9
PT = 1.0
LW_BOLD, LW_THIN, LW_GHOST, LW_95, LW_90 = 1.4, 0.9, 0.6, 0.8, 2.2
MS_BOLD, MS = 5, 4
TOL4 = 6e-5
TOL = 1e-9
MARGIN = stats.TOST_MARGIN
AMEND7_NOTE = "Amendment 7 results are post hoc and exploratory and change no planned decision."
FORBIDDEN = (chr(0x2013), chr(0x2014), "cla" + "ude")
REGIMES = (("b2sentence", "Sentence-trained"), ("b2mixed", "Mixed-input"), ("b1names", "Names-trained"))
BACKBONES = (("biomedbert", "BiomedBERT"), ("bertbase", "BERT-base"), ("biobert", "BioBERT"))
NAMES_KEYS = pf.NAMES_ONLY
FIGURES = ("fig1_panel_d", "fig2_dissociation", "fig3_encoders", "fig4_sentence_signal", "fig5_positive_controls",
           "fig6_model_panel", "graphical_abstract", "figS_amend7_detail")
OOD_COHORTS = {"fig1_study_design": ("novel", "older"), "fig2_dissociation": ("novel", "older_clean"),
               "fig3_encoders": ("novel", "older_clean"), "fig4_sentence_signal": (),
               "fig5_positive_controls": ("novel", "older_primary"), "fig6_model_panel": ("older_primary", "novel"),
               "figS_amend7_detail": ("novel", "older_primary"), "graphical_abstract": ("novel", "older_clean")}
DODGE = 0.12
EXAMPLE = ("abrocitinib", "aspirin")


class PendingError(RuntimeError):
    pass


class Ledger:
    def __init__(self):
        self.counts = {}
        self.items = []

    def _bump(self, kind):
        self.counts[kind] = self.counts.get(kind, 0) + 1

    def check(self, kind, got, want, where, tol=TOL4):
        if got is None or want is None:
            raise AssertionError(f"{kind} {where}: missing value (computed {got}, stored {want})")
        got, want = float(got), float(want)
        if not (np.isfinite(got) and np.isfinite(want)) or abs(got - want) > tol:
            raise AssertionError(f"{kind} {where}: computed {got} differs from stored {want} (tolerance {tol})")
        self._bump(kind)
        self.items.append({"kind": kind, "where": where, "computed": got, "stored": want})
        return got

    def check_cell(self, kind, got, want, where, keys=("value", "lo95", "hi95", "lo90", "hi90"), tol=TOL4):
        for k in keys:
            if k in want and want[k] is not None:
                self.check(f"{kind}:{k}", got[k], want[k], where, tol)
        return got

    def read(self, where, value):
        self._bump("read")
        self.items.append({"kind": "read", "where": where, "value": value})
        return value


def summ(value, lo95=None, hi95=None, lo90=None, hi90=None, source=""):
    return {"value": float(value), "lo95": lo95, "hi95": hi95, "lo90": lo90, "hi90": hi90, "source": source}


def from_stat(d, source):
    return summ(d["value"], d.get("lo95"), d.get("hi95"), d.get("lo90"), d.get("hi90"), source)


def from_within(r, source):
    return summ(r["auroc_within"], r.get("lo95"), r.get("hi95"), r.get("lo90"), r.get("hi90"), source)


def from_ci(value, ci95, ci90=None, source=""):
    return summ(value, ci95[0], ci95[1], None if ci90 is None else ci90[0], None if ci90 is None else ci90[1], source)


def wilson(k, n, z=1.959963984540054):
    if n == 0:
        return float("nan"), float("nan")
    p = k / n
    den = 1 + z * z / n
    mid = (p + z * z / (2 * n)) / den
    half = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return float(mid - half), float(mid + half)


def two_sig_percent(x):
    v = 100 * x
    if v == 0:
        return "0%"
    digits = max(0, 1 - int(np.floor(np.log10(abs(v)))))
    return f"{round(v, digits):.{digits}f}%"


def f2(x):
    return f"{x:.2f}"


def f3(x):
    return f"{x:.3f}"


def ci_text(c, digits=3, level="95"):
    lo, hi = c.get(f"lo{level}"), c.get(f"hi{level}")
    return f"[{lo:.{digits}f}, {hi:.{digits}f}]"


def lint_text(text, where=""):
    low = text.lower()
    for bad in FORBIDDEN:
        if bad in low:
            raise AssertionError(f"forbidden text {bad!r} in {where}: {text!r}")
    return text


def lint(fig, name, min_pt=None):
    floor = SMALL if min_pt is None else min_pt
    for t in fig.findobj(lambda a: hasattr(a, "get_text") and hasattr(a, "get_fontsize")):
        s = t.get_text()
        if not s or not s.strip() or not t.get_visible():
            continue
        lint_text(s, name)
        if t.get_fontsize() < floor - 1e-6:
            raise AssertionError(f"{name}: text below {floor} pt: {s!r} at {t.get_fontsize()}")


def style():
    import matplotlib as mpl
    family = pf.style()
    mpl.rcParams.update({
        "font.size": BASE, "axes.labelsize": BASE, "axes.titlesize": BASE, "xtick.labelsize": SMALL,
        "ytick.labelsize": BASE, "legend.fontsize": SMALL, "axes.edgecolor": SPINE, "axes.linewidth": 0.6,
        "axes.labelcolor": TEXT, "xtick.color": TEXT, "ytick.color": TEXT, "text.color": TEXT,
        "xtick.major.width": 0.6, "ytick.major.width": 0.6, "xtick.major.size": 2.5, "ytick.major.size": 2.5,
        "xtick.minor.size": 1.5, "xtick.minor.width": 0.5, "xtick.direction": "out", "ytick.direction": "out",
        "lines.solid_capstyle": "butt", "lines.dash_capstyle": "butt",
    })
    return family


def figure(w, h):
    import matplotlib.pyplot as plt
    return plt.figure(figsize=(w * MM, h * MM))


def axes_mm(fig, x, y, w, h):
    W, H = fig.get_figwidth() / MM, fig.get_figheight() / MM
    ax = fig.add_axes([x / W, 1 - (y + h) / H, w / W, h / H])
    ax.patch.set_alpha(0)
    return ax


def canvas(fig):
    W, H = fig.get_figwidth() / MM, fig.get_figheight() / MM
    bg = fig.add_axes([0, 0, 1, 1], zorder=-10)
    bg.set_xlim(0, W)
    bg.set_ylim(H, 0)
    bg.axis("off")
    return bg


def spines(ax, left=True, bottom=True):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(left)
    ax.spines["bottom"].set_visible(bottom)
    for s in ("left", "bottom"):
        ax.spines[s].set_position(("outward", 4))
        ax.spines[s].set_color(SPINE)
        ax.spines[s].set_linewidth(0.6)


def auroc_x(ax, lo=0.3, hi=1.0, labels=True, label="AUROC"):
    ax.set_xlim(lo, hi)
    major = [v for v in np.round(np.arange(0.3, 1.01, 0.2), 1) if lo - 1e-9 <= v <= hi + 1e-9]
    ax.set_xticks(major)
    ax.set_xticks([v for v in np.round(np.arange(0.3, 1.01, 0.1), 1) if lo - 1e-9 <= v <= hi + 1e-9 and v not in major],
                  minor=True)
    ax.grid(axis="x", which="both", color=GRID, lw=0.4, zorder=0)
    if labels:
        ax.set_xticklabels([f"{v:.1f}" for v in major])
        if label:
            ax.set_xlabel(label)
    else:
        ax.set_xticklabels([])


def h1_cell(system, model, cohort, inp="names"):
    return (system, model, cohort, inp) == H1_CELL


def draw_band(ax, hypothesis, vertical=True, lo=None, hi=None, label=None, label_at=None, va="top", ha="center"):
    if hypothesis not in BAND_HYPOTHESES:
        raise AssertionError(f"equivalence band requested for {hypothesis!r}; allowed only for {BAND_HYPOTHESES}")
    from matplotlib.patches import Rectangle
    m0, m1 = MARGIN
    if vertical:
        if lo is None:
            ax.axvspan(m0, m1, color=BAND, lw=0, zorder=0)
        else:
            ax.add_patch(Rectangle((m0, lo), m1 - m0, hi - lo, color=BAND, lw=0, zorder=0))
    else:
        if lo is None:
            ax.axhspan(m0, m1, color=BAND, lw=0, zorder=0)
        else:
            ax.add_patch(Rectangle((lo, m0), hi - lo, m1 - m0, color=BAND, lw=0, zorder=0))
    if label:
        x, y = label_at
        ax.text(x, y, label, ha=ha, va=va, fontsize=SMALL, color=TEXT2, zorder=2)


def chance(ax, vertical=True, label_at=None, ha="left", va="bottom", span=None):
    kw = dict(color=RULE, lw=0.5, ls=(0, (3, 2)), zorder=2)
    if vertical:
        ax.axvline(0.5, **kw) if span is None else ax.plot([0.5, 0.5], span, **kw)
    else:
        ax.axhline(0.5, **kw) if span is None else ax.plot(span, [0.5, 0.5], **kw)
    if label_at is not None:
        ax.text(label_at[0], label_at[1], "chance", ha=ha, va=va, fontsize=SMALL, color=TEXT2, zorder=2)


def mark(ax, pos, c, color, marker, hollow=False, ms=MS, horizontal=True, ci90=False, zorder=3, lw95=LW_95, alpha=1.0,
         offset95=0.0):
    p95 = pos + offset95
    if c.get("lo95") is not None:
        a, b = (c["lo95"], c["hi95"])
        if horizontal:
            ax.plot([a, b], [p95, p95], color=color, lw=lw95, zorder=zorder, solid_capstyle="butt", alpha=alpha)
        else:
            ax.plot([p95, p95], [a, b], color=color, lw=lw95, zorder=zorder, solid_capstyle="butt", alpha=alpha)
    if ci90 and c.get("lo90") is not None:
        a, b = (c["lo90"], c["hi90"])
        if horizontal:
            ax.plot([a, b], [p95, p95], color=color, lw=LW_90, zorder=zorder, solid_capstyle="butt", alpha=alpha)
        else:
            ax.plot([p95, p95], [a, b], color=color, lw=LW_90, zorder=zorder, solid_capstyle="butt", alpha=alpha)
    x, y = (c["value"], pos) if horizontal else (pos, c["value"])
    if hollow:
        ax.plot(x, y, marker, ms=ms, mfc=SURFACE, mec=color, mew=0.8, zorder=zorder + 1, alpha=alpha)
    else:
        ax.plot(x, y, marker, ms=ms, mfc=color, mec=SURFACE, mew=0.6, zorder=zorder + 1, alpha=alpha)


def panel_label(ax, letter, title, dy=4):
    ax.annotate(letter, xy=(0, 1), xycoords="axes fraction", xytext=(-4 * PT, dy), textcoords="offset points",
                fontsize=LETTER, fontweight="bold", ha="left", va="bottom")
    ax.annotate(title, xy=(0, 1), xycoords="axes fraction", xytext=(7, dy), textcoords="offset points",
                fontsize=BASE, ha="left", va="bottom")


def pending_frame(ax, what, final):
    if final:
        raise PendingError(f"pending series in final mode: {what}")
    ax.text(0.5, 0.5, "pending", transform=ax.transAxes, ha="center", va="center", fontsize=SMALL, color=TEXT2)


def spread(values, gap):
    order = np.argsort(values)
    out = np.asarray(values, float).copy()
    for i in range(1, len(order)):
        a, b = order[i - 1], order[i]
        if out[b] - out[a] < gap:
            out[b] = out[a] + gap
    shift = (np.asarray(values, float) - out).mean()
    return out + shift


def save(fig, out, name, bands=0, thick=0, min_pt=None):
    lint(fig, name, min_pt)
    pf.save(fig, Path(out), name, bands, thick)


class Sources:
    def __init__(self, a):
        self.boot = a.boot
        self.final = a.final
        self.L = Ledger()
        self.d = pf.Data(a.preds, a.eval, a.baselines, a.boot)
        ev_dir = Path(a.eval)
        self.exp5 = json.loads((Path(a.amend7) / "cpu" / "exp5_dissociation.json").read_text())
        self.kappa = {r["id"]: r for r in json.loads((Path(a.amend7) / "cpu" / "kappa_weighting.json").read_text())["rows"]}
        self.e7 = self.optional(Path(a.amend7) / "e7.json")
        self.e8 = self.optional(Path(a.amend7) / "e8.json")
        self.e9 = self.optional(Path(a.amend7) / "e9.json")
        self.cs = json.loads((Path(a.post7) / "classshortcut" / "classshortcut.json").read_text())
        p8 = Path(a.post8)
        self.p8_sens = self.optional(p8 / "sensitivity.json")
        self.p8_screen = self.optional(p8 / "screen.json")
        self.p8_e9 = self.optional(p8 / "e9.json")
        self.p8_red = self.optional(p8 / "redacted_confound.json")
        self.ideal = json.loads((Path(a.sensitivity) / "control_ideal_reader.json").read_text())
        self.selfpairs = json.loads((Path(a.sensitivity) / "semeval_selfpairs.json").read_text())
        self.rev2 = json.loads((Path(a.rev2) / "r2a.json").read_text())
        self.rev3 = json.loads((Path(a.rev3) / "c2_seen_reference.json").read_text())
        self.m3b = json.loads((Path(a.rev2_base) / "m3b_drugbank.json").read_text())
        self.d9 = json.loads((Path(a.rev3) / "d9_listing_conventions.json").read_text())
        self.db_lookup = {r["cohort"]: r for r in json.loads((ev_dir / "drugbank_lookup.json").read_text())["rows"]}
        self.a7preds = Path(a.a7preds)
        self.corrected = Path(a.corrected)
        self.boot_ok = a.boot == 1000
        self._db = None
        self._a7truth = None

    @staticmethod
    def optional(p):
        return json.loads(p.read_text()) if p.exists() else None

    def a7truth(self):
        if self._a7truth is None:
            from .amend7_pairs import read_csv
            self._a7truth = aa.Truth(read_csv(self.corrected / "ood_pairs.csv"), read_csv(self.corrected / "ood_old_pairs.csv"))
        return self._a7truth

    def evals(self, system, model, key):
        g = self.d.gk(system, model)
        if g is None:
            return None, None
        return g, self.d.aggs[g]["evals"].get(key)

    def stored_cohort(self, g, key, cohort):
        return self.d.cohortrows.get((ev.label(g), key, cohort, "A"))

    def cohort_within(self, g, key, cohort):
        e = self.d.aggs[g]["evals"][key]
        v = ev.view(e, cohort)
        r = ev.within_stat(v, self.boot, 42 if cohort.startswith("older") else 1042)
        c = from_within(r, f"recomputed with evaluate2.within_stat; checked against tables.json ood_cohorts {ev.label(g)} {key} {cohort} A")
        row = self.stored_cohort(g, key, cohort)
        if row is None:
            raise AssertionError(f"no stored ood_cohorts row for {ev.label(g)} {key} {cohort}")
        self.L.check("ood_cohorts:auroc_within", c["value"], row["auroc_within"], f"{ev.label(g)} {key} {cohort}")
        if self.boot_ok:
            for k in ("lo90", "hi90", "lo95", "hi95"):
                self.L.check(f"ood_cohorts:{k}", c[k], row[k], f"{ev.label(g)} {key} {cohort}")
        c["n"], c["n_drugs"] = r["n"], r["n_drugs"]
        return c

    def pooled_view(self, e_nov, e_old):
        vn, vo = ev.view(e_nov, "novel"), ev.view(e_old, "older_clean")
        return {"y": np.concatenate([vn["y"], vo["y"]]), "p": np.concatenate([vn["p"], vo["p"]]),
                "pb": np.concatenate([vn["pb"], vo["pb"]]),
                "g": np.concatenate([np.char.add("novel:", vn["g"].astype(str)), np.char.add("older:", vo["g"].astype(str))]),
                "partner": np.concatenate([vn["partner"], vo["partner"]]), "dbstate": None}

    def pooled_within(self, e_nov, e_old, where):
        r = ev.within_stat(self.pooled_view(e_nov, e_old), self.boot)
        c = from_within(r, f"recomputed with evaluate2.within_stat on Novel + Older-clean (the H1-pooled estimator): {where}")
        c["n"], c["n_drugs"] = r["n"], r["n_drugs"]
        return c

    def group_pooled(self, system, model):
        kn, ko = (NAMES_KEYS[system][1], NAMES_KEYS[system][2]) if system in NAMES_KEYS else ("ood", "oodold")
        g = self.d.gk(system, model)
        if g is None:
            return None
        a = self.d.aggs[g]["evals"]
        if kn not in a or ko not in a:
            return None
        for key, cohort in ((kn, "novel"), (ko, "older_clean")):
            v = ev.view(a[key], cohort)
            row = self.stored_cohort(g, key, cohort)
            self.L.check("ood_cohorts:auroc_within", stats.stratified_auroc(v["y"], v["p"], v["g"]), row["auroc_within"],
                         f"{ev.label(g)} {key} {cohort} (component of pooled)")
        c = self.pooled_within(a[kn], a[ko], ev.label(g))
        if system == "b2mixed" and model == "biomedbert":
            d = self.d.decisions["H1-pooled"]
            self.L.check("decisions:H1-pooled:value", c["value"], d["value"], "H1-pooled")
            if self.boot_ok:
                self.L.check("decisions:H1-pooled:lo95", c["lo95"], d["interval"][0], "H1-pooled")
                self.L.check("decisions:H1-pooled:hi95", c["hi95"], d["interval"][1], "H1-pooled")
                self.L.check("decisions:H1-pooled:lo90", c["lo90"], d["interval90"][0], "H1-pooled")
                self.L.check("decisions:H1-pooled:hi90", c["hi90"], d["interval90"][1], "H1-pooled")
        c["seeds"] = self.d.seeds(g)
        return c

    def drugbank_evals(self):
        if self._db is None:
            found = ev.load_drugbank(self.corrected)
            out = {}
            for tag, fname in (("ood", "ood_pairs.csv"), ("oodold", "ood_old_pairs.csv")):
                rows = ev._read_csv(self.corrected / fname)
                s = self.d.truth.sets[tag]
                sc = drugbank_scores(rows, found[tag])
                out[tag] = {"y": np.asarray(s["y"]), "p": sc, "pb": sc.astype(int), "g": np.asarray(s["g"]),
                            "partner": np.asarray(s["partner"]), "clean": s["clean"], "sens": s["sens"],
                            "dbstate": s["dbstate"]}
            self._db = out
        return self._db

    def drugbank_pooled(self):
        db = self.drugbank_evals()
        for tag, cohort in (("ood", "novel"), ("oodold", "older_clean")):
            v = ev.view(db[tag], cohort)
            self.L.check("drugbank_lookup:auroc_within", stats.stratified_auroc(v["y"], v["p"], v["g"]),
                         self.db_lookup[cohort]["auroc_within"], cohort)
            self.L.check("drugbank_lookup:auroc", ev.auroc(v["y"], v["p"]), self.db_lookup[cohort]["auroc"], cohort)
        c = self.pooled_within(db["ood"], db["oodold"], "DrugBank lookup")
        self.L.check("kappa_weighting:drugbank_within", c["value"], self.kappa["H1-pooled"]["drugbank_within"],
                     "H1-pooled DrugBank")
        return c


def seen_cells(src):
    r2, c2 = src.rev2, src.rev3
    ov = r2["seen_overlap_with_semeval_train"]
    meta = c2["cohorts"]["seen"]["meta"]
    n_pairs = ov["n_pairs"]
    src.L.check("r2a_seen:n_pairs overlap", n_pairs, c2["overlap"]["n_pairs"], "r2a vs c2 overlap", tol=0)
    src.L.check("r2a_seen:n_pairs meta", n_pairs, meta["n_pairs"], "r2a vs c2 seen meta", tol=0)
    c2rows = {(r["family"], r["cohort"], r["input"]): r for r in c2["r2a_rows"]["dissociation"]}
    out = {"n_pairs": n_pairs, "n_positive": meta["n_positive"], "n_anchor_drugs": meta["n_anchor_drugs"]}
    for family in ("b2mixed", "b2sentence"):
        rows = [r for r in r2["dissociation"] if r["family"] == family and r["cohort"] == "seen" and r["input"] == "names_only"]
        if len(rows) != 1:
            raise AssertionError(f"r2a.json: expected one seen names_only {family} row, found {len(rows)}")
        r = rows[0]
        if not r["complete"] or r["key"] != "train_empty":
            raise AssertionError(f"r2a.json seen {family} row is incomplete or has key {r['key']}")
        m = r["seed_mean"]
        where = f"r2a seen names_only {family}"
        src.L.check("r2a_seen:n_pairs row", r["n_pairs"], n_pairs, where, tol=0)
        src.L.check("r2a_seen:n_positive", r["n_positive"], meta["n_positive"], where, tol=0)
        src.L.check("r2a_seen:n_anchor_drugs", r["n_anchor_drugs"], meta["n_anchor_drugs"], where, tol=0)
        src.L.check("r2a_seen:n_seeds", len(r["seeds"]), 5, where, tol=0)
        src.L.check("r2a_seen:n_draws", m["n_draws"], src.boot, where, tol=0)
        src.L.check("r2a_seen:seed-mean AUROC within 0.02 of mean per-seed AUROC", float(np.mean(r["per_seed"])), m["value"], where,
                    tol=0.02)
        if not (m["lo95"] <= m["value"] <= m["hi95"] and m["lo90"] <= m["value"] <= m["hi90"]):
            raise AssertionError(f"{where}: value outside its interval")
        ref = c2rows[(family, "seen", "names_only")]["seed_mean"]
        for k in ("value", "lo95", "hi95", "lo90", "hi90"):
            src.L.check(f"r2a_seen:c2 copy {k}", m[k], ref[k], where, tol=1.1e-6)
        out[family] = summ(m["value"], m["lo95"], m["hi95"], m["lo90"], m["hi90"],
                           source="rev2_colab/r2a.json dissociation, cohort seen, input names_only, seed mean, two-way 95%")
        out[family]["seeds"] = r["seeds"]
    d = c2["cohorts"]["seen"]["rows"]["drugbank_lookup"]
    src.L.check("c2_seen:drugbank n_draws", d["n_draws_two_way"], src.boot, "DrugBank seen reference", tol=0)
    lo, hi = d["within_ci95_two_way"]
    if not (lo <= d["within_drug_auroc"] <= hi):
        raise AssertionError("DrugBank seen reference: value outside its interval")
    out["drugbank"] = summ(d["within_drug_auroc"], lo, hi,
                           source="rev3/c2_seen_reference.json cohorts.seen.rows.drugbank_lookup.within_drug_auroc, two-way 95%")
    return out


def seed_count(src, system, model="biomedbert"):
    return len(src.d.seeds(src.d.gk(system, model)))


def qwen_unseen(src):
    if src.e8 is None:
        raise AssertionError("e8.json is missing: the Qwen unseen-drug range cannot be drawn")
    from .amend7_prompts import PRIMARY
    c = src.e8["e8_names"]["cohorts"]["older_primary"]
    vals = [v["value"] for v in c["per_prompt"].values()]
    src.L.check("e8:names older_primary primary", c["per_prompt"][PRIMARY]["value"], c["primary"], "hero Qwen", tol=TOL)
    src.L.check("e8:names older_primary min", min(vals), c["min"], "hero Qwen", tol=TOL)
    src.L.check("e8:names older_primary max", max(vals), c["max"], "hero Qwen", tol=TOL)
    src.L.check("e8:names older_primary n_prompts", len(vals), 5, "hero Qwen", tol=0)
    src.L.check("e8:names older_primary stated range low", round(c["min"], 3), 0.519, "hero Qwen stated range", tol=1e-12)
    src.L.check("e8:names older_primary stated range high", round(c["max"], 3), 0.607, "hero Qwen stated range", tol=1e-12)
    if c["robust"]:
        raise AssertionError("e8 names-only Older-primary is no longer reported as not robust")
    out = summ(c["primary"], source="e8.json e8_names cohorts older_primary primary prompt (planned names-only range, Older-primary)")
    out["range"] = (c["min"], c["max"])
    out["n_prompts"] = len(vals)
    out["cohort"] = "Older-primary"
    out["n_drugs"] = src.cs["cells"]["older_primary:A"]["n_drugs"]
    src.L.check("hero:Qwen range cohort drugs", out["n_drugs"], 121, "Older-primary cohort drug count", tol=0)
    return out


def hero_series(src):
    out = {"ghost": [], "bold": []}
    seen = seen_cells(src)
    out["seen"] = seen
    for model, mlabel in BACKBONES:
        for system, slabel in REGIMES:
            g = src.d.gk(system, model)
            if g is None:
                continue
            left = src.d.cell(g, NAMES_KEYS[system][0])
            left = summ(left["auroc"], left["lo"], left["hi"], source=left["source"])
            right = src.group_pooled(system, model)
            item = {"name": f"{slabel} {mlabel}", "system": system, "model": model, "left": left, "right": right,
                    "role": ROLE_LABEL["SEMEVAL"], "seeds": src.d.seeds(g)}
            if model == "biomedbert" and system in seen:
                item["seen"] = seen[system]
            if system == "b2mixed" and model == "biomedbert":
                item.update({"label": "Mixed-input BiomedBERT", "color": SEMEVAL, "marker": "b2mixed", "lw": LW_BOLD,
                             "text_color": SEMEVAL})
                out["bold"].insert(0, item)
            else:
                out["ghost"].append(item)
    a = src.exp5["auroc"][0]
    src.L.read("exp5_dissociation.json auroc[0] (all pairs, unresolvable counted as not listed)", a["auroc"])
    grid = {r["system"]: r for r in src.exp5["grid_2x2"] if r["labels"].startswith("SemEval")}
    src.L.check("exp5:grid DrugBank", a["auroc"], grid["DrugBank lookup"]["value"], "SemEval DrugBank", tol=TOL)
    out["bold"].append({"name": "DrugBank lookup", "label": "DrugBank lookup", "role": ROLE_LABEL["EXTERNAL"],
                        "left": from_ci(a["auroc"], a["ci95"], source="exp5_dissociation.json auroc (sentence-cluster bootstrap)"),
                        "left_excl": selfpair_excluded(src, a),
                        "right": src.drugbank_pooled(), "seen": seen["drugbank"], "color": DRUGBANK, "marker": "drugbank",
                        "lw": LW_BOLD, "text_color": TEXT})
    for model, label, mk, lw in (("qwen", "Qwen2.5-7B", "qwen", LW_BOLD), ("biomistral", "BioMistral-7B", "biomistral", LW_THIN)):
        g = src.d.gk("names", model)
        left = src.d.cell(g, "test")
        left = summ(left["auroc"], left["lo"], left["hi"], source=left["source"])
        key = f"llm-{model}-names (names only)"
        if key in grid:
            src.L.check("exp5:grid value", left["value"], grid[key]["value"], key)
            if src.boot_ok:
                src.L.check("exp5:grid lo95", left["lo95"], grid[key]["ci95"][0], key)
                src.L.check("exp5:grid hi95", left["hi95"], grid[key]["ci95"][1], key)
        right = qwen_unseen(src) if model == "qwen" else src.group_pooled("names", model)
        out["bold"].append({"name": label, "label": label, "role": ROLE_LABEL["EXTERNAL"], "left": left, "right": right,
                            "color": EXTERNAL, "marker": mk, "lw": lw, "text_color": TEXT, "seeds": src.d.seeds(g)})
    pooled = out["bold"][0]["right"]
    src.L.check("hero:unseen pairs", pooled["n"], src.db_lookup["novel"]["n"] + src.db_lookup["older_clean"]["n"],
                "Novel plus Older-clean pairs", tol=0)
    src.L.check("hero:unseen drugs", pooled["n_drugs"], src.db_lookup["novel"]["n_drugs"] + src.db_lookup["older_clean"]["n_drugs"],
                "Novel plus Older-clean drugs", tol=0)
    out["unseen_pairs"], out["unseen_drugs"] = pooled["n"], pooled["n_drugs"]
    return out


def selfpair_excluded(src, a):
    sp = src.selfpairs
    rows = {r["subset"]: r for r in sp["rows"]}
    exp5 = {r["subset"]: r for r in src.exp5["auroc"]}
    full, excl = rows["all pairs, unresolvable counted as not listed"], rows["excluding self pairs"]
    src.L.check("semeval_selfpairs:all auroc", full["auroc"], a["auroc"], "all pairs vs exp5 auroc[0]", tol=TOL)
    for k in ("auroc",):
        src.L.check("semeval_selfpairs:excl auroc", excl[k], exp5["excluding self pairs"][k], "excluding self pairs", tol=TOL)
    for i in (0, 1):
        src.L.check("semeval_selfpairs:excl ci95", excl["ci95"][i], exp5["excluding self pairs"]["ci95"][i],
                    "excluding self pairs", tol=TOL)
    src.L.check("semeval_selfpairs:n", excl["n"], exp5["excluding self pairs"]["n"], "excluding self pairs", tol=0)
    src.L.check("semeval_selfpairs:n_self", sp["n_self_pairs"], full["n"] - excl["n"], "self pairs removed", tol=0)
    src.L.check("semeval_selfpairs:self positives", sp["self_pairs_positive"], 0, "self pairs positive", tol=0)
    if not all(sp["agrees_with_exp5"].values()):
        raise AssertionError("semeval_selfpairs.json does not agree with exp5")
    c = from_ci(excl["auroc"], excl["ci95"], source="sensitivity/semeval_selfpairs.json rows 'excluding self pairs'")
    c["n"], c["n_self_pairs"] = excl["n"], sp["n_self_pairs"]
    m3 = {r["subset"]: r for r in src.m3b["by_source"]}
    src.L.check("m3b:all sources auroc", m3["all sources, all pairs"]["auroc"], a["auroc"], "m3b vs exp5 all pairs", tol=TOL4)
    src.L.check("m3b:no self pairs auroc", m3["all sources, no self pairs"]["auroc"], excl["auroc"], "m3b vs self-pair file",
                tol=TOL4)
    return c


def hero_bars(src):
    lr = src.m3b["listing_rates"]
    sp = src.selfpairs
    out = []
    src.L.check("d9:self pairs removed", src.d9["n_self_pairs"], sp["n_self_pairs"], "d9 vs semeval_selfpairs", tol=0)
    for key, name, med in (("SemEval test negatives, no self pairs", "SemEval negatives", "SemEval test negatives, DDI-MedLine"),
                           ("SemEval test positives, no self pairs", "SemEval positives", "SemEval test positives, DDI-MedLine")):
        r = lr[key]
        n, listed = r["resolvable"], r["listed"]
        src.L.check("m3b:listed share of resolvable", listed / n, r["listed_share_of_resolvable"], name, tol=TOL4)
        lo, hi = wilson(listed, n)
        src.L.check("m3b:wilson lo", lo, r["ci95_resolvable"][0], name, tol=TOL4)
        src.L.check("m3b:wilson hi", hi, r["ci95_resolvable"][1], name, tol=TOL4)
        cls = "negatives" if "negatives" in key else "positives"
        m = [i for i in src.d9["instances"] if i["convention"] == "self_pairs_excluded" and i["class"] == cls
             and i["scope"] == "DDI-MedLine"]
        src.L.check("d9:one MedLine self-pair-excluded instance", len(m), 1, name + " MedLine", tol=0)
        m = m[0]
        src.L.check("d9:medline listed share of resolvable", m["listed"] / m["resolvable"], m["listed_share_of_resolvable"],
                    name + " MedLine", tol=TOL4)
        src.L.check("d9:medline share stated", round(m["listed_share_of_resolvable"], 3), 0.515 if cls == "negatives" else 0.577,
                    name + " MedLine stated", tol=1e-12)
        out.append({"name": name, "n_resolvable": n, "n": r["n"], "listed": listed, "not_listed": n - listed,
                    "share_of_resolvable": listed / n, "wilson95_resolvable": [lo, hi],
                    "medline_share_of_resolvable": m["listed_share_of_resolvable"],
                    "medline_n_resolvable": m["resolvable"],
                    "source": "rev2/m3b_drugbank.json listing_rates, rows without self pairs; MedLine rates from "
                              "rev3/d9_listing_conventions.json self_pairs_excluded"})
    src.L.check("m3b:negatives n without self pairs", lr["SemEval test negatives"]["n"] - lr[
        "SemEval test negatives, no self pairs"]["n"], sp["n_self_pairs"], "self pairs removed from negatives", tol=0)
    src.L.check("m3b:negatives n self pairs stored", src.m3b["n_self_pairs"], sp["n_self_pairs"], "self pairs", tol=0)
    src.L.check("m3b:positives unchanged", lr["SemEval test positives"]["n"], lr["SemEval test positives, no self pairs"]["n"],
                "self pairs are all negatives", tol=0)
    m3 = {r["subset"]: r for r in src.m3b["by_source"]}["all sources, no self pairs"]
    src.L.check("m3b:negatives listed share equals FPR", out[0]["listed"] / lr["SemEval test negatives, no self pairs"]["n"],
                m3["fpr_listed_share_of_negatives"], "negatives without self pairs", tol=TOL4)
    src.L.check("m3b:positives listed share equals TPR", out[1]["listed"] / lr["SemEval test positives, no self pairs"]["n"],
                m3["tpr_listed_share_of_positives"], "positives", tol=TOL4)
    rnd = lr["random vocabulary pairs (names)"]
    src.L.check("m3b:random listed share", rnd["listed"] / rnd["resolvable"], rnd["listed_share_of_resolvable"],
                "random vocabulary pairs", tol=TOL4)
    src.L.check("m3b:random n", rnd["n"], 10000, "random vocabulary pairs", tol=0)
    return {"bars": out, "random": {"share": rnd["listed_share_of_resolvable"], "ci95": rnd["ci95_resolvable"],
                                    "n_resolvable": rnd["resolvable"],
                                    "source": "rev2/m3b_drugbank.json listing_rates, random vocabulary pairs (names)"}}


def seen_label(name):
    return {"Mixed-input BiomedBERT": "Mixed-input", "DrugBank lookup": "DrugBank"}.get(name, name)


def draw_slope(ax, series):
    xs = {"left": 0.075, "right": 0.335, "rule": 0.745, "seen": 0.82}
    ax.set_xlim(0, 1)
    ax.set_ylim(0.3, 0.8)
    chance(ax, vertical=False, span=(0.0, 0.715))
    chance(ax, vertical=False, span=(0.775, 1.0))
    ax.plot([xs["rule"]] * 2, [0.3, 0.8], color=SPINE, lw=0.5, zorder=1)
    for s in series["ghost"]:
        if s["right"] is None:
            continue
        ax.plot((xs["left"], xs["right"]), [s["left"]["value"], s["right"]["value"]], color=SEMEVAL_TINT, lw=LW_GHOST,
                zorder=1)
    w_mm = ax.get_position().width * ax.figure.get_figwidth() / MM
    step = 2.4 / w_mm
    bold = series["bold"]
    offs = (np.arange(len(bold)) - (len(bold) - 1) / 2) * step
    for s, o in zip(bold, offs):
        m, hollow = MARKER[s["marker"]]
        y0 = s["left_excl"]["value"] if "left_excl" in s else s["left"]["value"]
        if "range" not in s["right"]:
            ax.plot([xs["left"] + o, xs["right"] + o], [y0, s["right"]["value"]], color=s["color"], lw=s["lw"], zorder=3)
        ms = MS_BOLD if s["lw"] == LW_BOLD else MS
        c0 = s["left_excl"] if "left_excl" in s else s["left"]
        mark(ax, xs["left"] + o, c0, s["color"], m, hollow, ms, horizontal=False, zorder=4)
        if "range" in s["right"]:
            lo, hi = s["right"]["range"]
            ax.plot([xs["right"] + o] * 2, [lo, hi], color=s["color"], lw=1.6, zorder=3, solid_capstyle="butt")
            ax.plot(xs["right"] + o, s["right"]["value"], m, ms=ms, mfc=s["color"], mec=SURFACE, mew=0.6, zorder=5)
        else:
            mark(ax, xs["right"] + o, s["right"], s["color"], m, hollow, ms, horizontal=False, zorder=4)
        if "left_excl" in s:
            ax.plot(xs["left"] + o + step * 0.9, s["left"]["value"], "D", ms=MS - 0.8, mfc=SURFACE, mec=SHORTCUT, mew=0.7,
                    zorder=4)
    h_mm = ax.get_position().height * ax.figure.get_figheight() / MM
    gap = 3.4 / h_mm * 0.5
    ys = spread([s["right"]["value"] for s in bold], gap)
    xr = xs["right"] + offs.max() + 0.04
    drawn_labels = []
    for s, y in zip(bold, ys):
        r = s["right"]
        txt = f"{s['label']} {f2(r['range'][0])} to {f2(r['range'][1])}" if "range" in r else f"{s['label']} {f2(r['value'])}"
        if "range" in r:
            txt += f"\n({r['cohort']}, {r['n_drugs']} drugs)"
        glyph = s["label"] in ("Qwen2.5-7B", "BioMistral-7B")
        if glyph:
            m_, h_ = MARKER[s["marker"]]
            ax.plot(xr + 0.008, y, m_, ms=MS, mfc=SURFACE if h_ else s["color"], mec=s["color"] if h_ else SURFACE, mew=0.6,
                    zorder=6, clip_on=False)
        ax.text(xr + (0.03 if glyph else 0.0), y, txt, ha="left", va="center", fontsize=SMALL, color=s["text_color"],
                clip_on=False, zorder=6, linespacing=1.15)
        drawn_labels.append(txt)
    enc = bold[0]
    ax.text(xs["left"] + offs[0], enc["left"]["value"] + 0.045, f2(enc["left"]["value"]), ha="center", va="bottom",
            fontsize=SMALL, color=TEXT2)
    db_i = [i for i, s in enumerate(bold) if "left_excl" in s][0]
    db = bold[db_i]
    note_db = f"DrugBank {f3(db['left_excl']['value'])} without\nself pairs; {f3(db['left']['value'])} with\nthem (gray, open)"
    if f3(db["left"]["value"]) != "0.525":
        raise AssertionError("the DrugBank with-self-pairs note is no longer 0.525")
    ax.text(xs["left"] + offs[db_i] - step * 0.2, 0.385, note_db, ha="left", va="top", fontsize=SMALL, color=TEXT2,
            linespacing=1.15)
    sm = series["seen"]
    marks = [("Mixed-input", sm["b2mixed"], SEMEVAL, "s", False), ("Sentence-trained", sm["b2sentence"], SEMEVAL, "o", False),
             ("DrugBank", sm["drugbank"], DRUGBANK, "D", False)]
    sy = spread([m[1]["value"] for m in marks], 3.2 / h_mm * 0.5)
    for (lab, c, color, mk, hollow), y in zip(marks, sy):
        mark(ax, xs["seen"], c, color, mk, hollow, MS_BOLD, horizontal=False, zorder=4)
        ax.text(xs["seen"] + 0.035, y, f"{lab} {f2(c['value'])}", ha="left", va="center", fontsize=SMALL, color=color if color != DRUGBANK else TEXT,
                clip_on=False, zorder=6)
    qlab = [t for t in drawn_labels if t.startswith("Qwen2.5-7B")]
    qr = [s_ for s_ in bold if s_["label"] == "Qwen2.5-7B"][0]["right"]
    if len(qlab) != 1 or f"({qr['cohort']}, {qr['n_drugs']} drugs)" not in qlab[0] or "Older-primary, 121 drugs" not in qlab[0]:
        raise AssertionError(f"the Qwen label does not name its cohort: {qlab}")
    return xs


def fig_hero(src, out):
    series = hero_series(src)
    bars = hero_bars(src)
    W, H = W_DOUBLE, 92
    fig = figure(W, H)
    bg = canvas(fig)
    ax = axes_mm(fig, 14, 12, 106, 58)
    spines(ax, bottom=False)
    xs = draw_slope(ax, series)
    ax.set_yticks(np.round(np.arange(0.3, 0.81, 0.1), 1))
    ax.set_ylabel("AUROC, names only")
    seen = series["seen"]
    ax.set_xticks([xs["left"], xs["right"]], ["SemEval test\ninstances\n(2,810)",
                                            f"Unseen-drug pairs\n({series['unseen_pairs']:,} pairs,\n{series['unseen_drugs']} drugs)"])
    ax.tick_params(axis="x", length=0, labelsize=SMALL, pad=3)
    ax.text(xs["left"], -0.215, "scored against\nSemEval labels", transform=ax.get_xaxis_transform(), ha="center", va="top",
            fontsize=SMALL, color=TEXT2, linespacing=1.15)
    ax.text(xs["right"], -0.215, "against FDA label\nmentions", transform=ax.get_xaxis_transform(),
            ha="center", va="top", fontsize=SMALL, color=TEXT2, linespacing=1.15)
    ax.text((xs["rule"] + 1.0) / 2 + 0.03, 1.02, f"Seen-drug pairs, retrained\nmodels (R2a), {seen['n_pairs']:,} pairs",
            transform=ax.transAxes, ha="center", va="bottom", fontsize=SMALL, color=TEXT, linespacing=1.15)
    ax.text(0.40, 0.345, f"{len(series['ghost'])} other encoder configurations\n(light lines, stored models)", ha="left", va="center",
            fontsize=SMALL, color=TEXT2, linespacing=1.2)
    ax.text(0.995, 0.503, "chance", ha="right", va="bottom", fontsize=SMALL, color=TEXT2)
    qrange = [s_ for s_ in series["bold"] if s_["label"] == "Qwen2.5-7B"][0]["right"]
    ax.text(0.0, -0.40, f"Qwen2.5-7B unseen-drug value: planned names-only range over {qrange['n_prompts']} prompts, "
            "Older-primary cohort.", transform=ax.get_xaxis_transform(), ha="left", va="top", fontsize=SMALL, color=TEXT2)
    panel_label(ax, "A", "Same name-only input, two kinds of label")
    bx = axes_mm(fig, 139, 22, 43, 30)
    draw_bars(bx, bars, bg)
    texts = {t.get_text() for t in fig.findobj(lambda o: hasattr(o, "get_text"))}
    for b_ in bars["bars"]:
        src.L.check("hero:panel B label says instances", float(f"{b_['name']} ({b_['n_resolvable']:,} instances)" in texts),
                    1.0, b_["name"], tol=0)
        src.L.check("hero:panel B share drawn at the bar end", float(two_sig_percent(b_["share_of_resolvable"]) in texts), 1.0,
                    b_["name"], tol=0)
    src.L.check("hero:panel B has no pair wording", float(not [t for t in texts if "resolvable pairs" in t or "a SemEval test pair" in t
                                                             or "pairs listed" in t]), 1.0, "panel B text", tol=0)
    src.L.check("hero:Qwen cohort label drawn", float(any("Older-primary, 121 drugs" in t for t in texts)), 1.0, "panel A", tol=0)
    table = {"series": {s["name"]: {k: s[k] for k in ("left", "right", "role", "left_excl") if k in s}
                        for s in series["bold"] + series["ghost"]},
             "panel_b": bars["bars"], "panel_b_random": bars["random"],
             "unseen_pairs": series["unseen_pairs"], "unseen_drugs": series["unseen_drugs"], "seen": series["seen"],
             "seen_marks": {s["name"]: s["seen"] for s in series["bold"] + series["ghost"] if "seen" in s},
             "decision_band_drawn": False, "ci90_drawn": False}
    save(fig, out, "fig2_dissociation")
    return table, series, bars


def draw_bars(bx, bars, bg):
    from matplotlib.patches import Rectangle
    spines(bx, left=False)
    rows = bars["bars"]
    ref = bars["random"]["share"]
    for i, b in enumerate(rows):
        y = i * 2.2
        share = b["share_of_resolvable"]
        bx.barh(y, share, left=0, height=0.9, color=DRUGBANK, edgecolor=SURFACE, lw=0.8, zorder=2)
        bx.barh(y, 1 - share, left=share, height=0.9, color=NEUTRAL, edgecolor=SURFACE, lw=0.8, zorder=2)
        bx.text(share - 0.02, y, two_sig_percent(share), ha="right", va="center", fontsize=SMALL, color=SURFACE,
                zorder=3)
        lo, hi = b["wilson95_resolvable"]
        bx.plot([lo, hi], [y + 0.75, y + 0.75], color=TEXT, lw=0.8, zorder=3)
        for e in (lo, hi):
            bx.plot([e, e], [y + 0.62, y + 0.88], color=TEXT, lw=0.8, zorder=3)
        bx.text(0, y - 0.62, f"{b['name']} ({b['n_resolvable']:,} instances)", ha="left", va="bottom", fontsize=SMALL,
                color=TEXT, zorder=5, bbox=dict(fc=SURFACE, ec="none", pad=0.6))
    bx.plot([ref, ref], [-1.45, 3.2], color=SHORTCUT, lw=0.9, ls=(0, (3, 2)), zorder=4)
    ref_text = f"random vocabulary pairs: {100 * ref:.1f}%"
    if ref_text != "random vocabulary pairs: 35.5%":
        raise AssertionError(f"reference label {ref_text!r} differs from the stated 35.5%")
    bx.text(ref + 0.02, -1.5, ref_text.replace("vocabulary pairs", "vocabulary\npairs"), ha="left", va="bottom", fontsize=SMALL,
            color=TEXT2, zorder=4, linespacing=1.15)
    bx.set_ylim(3.3, -3.2)
    bx.set_yticks([])
    bx.set_xlim(0, 1)
    bx.set_xticks([0, 0.5, 1.0], ["0%", "50%", "100%"])
    bx.set_xlabel("Share of resolvable instances listed", fontsize=SMALL)
    ytitle = 12 - 4 * PT * 25.4 / 72
    bg.text(131, ytitle, "B", ha="left", va="bottom", fontsize=LETTER, fontweight="bold")
    bg.text(135.5, ytitle, "How often DrugBank lists", ha="left", va="bottom", fontsize=BASE)
    bg.text(135.5, ytitle + 3.8, "a SemEval test instance", ha="left", va="bottom", fontsize=BASE)
    neg, pos = rows
    bg.text(139, 64, "DDI-MedLine abstracts only:\n"
            f"{two_sig_percent(neg['medline_share_of_resolvable'])} of negatives, "
            f"{two_sig_percent(pos['medline_share_of_resolvable'])} of positives.\nSelf pairs removed.", ha="left", va="top",
            fontsize=SMALL, color=TEXT2, linespacing=1.2)


def signal_rows(src, model):
    rows = []
    for label, keys in (("Sentence", {"b2sentence": "test_sentence", "b2mixed": "test_sentence"}),
                        ("Sentence, both names\nreplaced by pseudo-words",
                         {"b2sentence": "swap_pseudo_sentence", "b2mixed": "swap_pseudo_sentence"}),
                        ("Names only", {s: NAMES_KEYS[s][0] for s, _ in REGIMES})):
        cells = {}
        for s, _ in REGIMES:
            if s not in keys:
                continue
            g = src.d.gk(s, model)
            c = src.d.cell(g, keys[s]) if g is not None else None
            if c is not None:
                cells[s] = summ(c["auroc"], c["lo"], c["hi"], source=c["source"])
        rows.append(("semeval", label, cells))
    n_nov = src.db_lookup["novel"]["n_drugs"]
    n_old = src.db_lookup["older_clean"]["n_drugs"]
    yrs = cohort_years(src)
    for cohort, label, ki in (("novel", f"Novel {yrs['novel'][0]} to {yrs['novel'][1]}\n({n_nov} drugs; no H1 decision)", 1),
                              ("older_clean", f"Older-clean {yrs['older'][0]} to {yrs['older'][1]}\n({n_old} drugs)", 2)):
        cells = {}
        for s, _ in REGIMES:
            g = src.d.gk(s, model)
            if g is None or NAMES_KEYS[s][ki] not in src.d.aggs[g]["evals"]:
                continue
            cells[s] = src.cohort_within(g, NAMES_KEYS[s][ki], cohort)
        rows.append(("ood", label, cells))
    return rows


def cohort_years(src):
    s = json.loads((src.corrected / "ood_summary.json").read_text())
    o = json.loads((src.corrected / "ood_old_summary.json").read_text())
    ny = sorted(int(k) for k in s["years"])
    oy = o["first_approval_years"]
    src.L.check("ood_summary:min_year", ny[0], config.OOD_MIN_YEAR, "Novel first year", tol=0)
    src.L.check("ood_summary:n_pairs", s["n_pairs"], src.db_lookup["novel"]["n"], "Novel pairs", tol=0)
    src.L.check("ood_summary:n_drugs", s["n_ood_drugs"], src.db_lookup["novel"]["n_drugs"], "Novel drugs", tol=0)
    src.L.check("ood_old_summary:n_pairs", o["n_pairs"], src.db_lookup["older_full"]["n"], "Older pairs", tol=0)
    src.L.check("ood_old_summary:n_drugs", o["n_ood_drugs"], src.db_lookup["older_full"]["n_drugs"], "Older drugs", tol=0)
    return {"novel": (ny[0], ny[-1]), "older": (oy[0], oy[1]), "novel_pairs": s["n_pairs"], "novel_drugs": s["n_ood_drugs"],
            "older_pairs": o["n_pairs"], "older_drugs": o["n_ood_drugs"]}


def seed_title(src, model):
    counts = {lab: len(src.d.seeds(src.d.gk(s, model))) for s, lab in REGIMES if src.d.gk(s, model) is not None}
    vals = list(counts.values())
    common = max(set(vals), key=vals.count)
    word = lambda k: f"{k} seed" + ("" if k == 1 else "s")
    rest = [f"{lab} {word(k)}" for lab, k in counts.items() if k != common]
    return word(common) + ("" if not rest else "; " + "; ".join(rest))


def fig_encoders(src, out):
    W, H = W_DOUBLE, 92
    fig = figure(W, H)
    bg = canvas(fig)
    LBL, PW, GAP, TOP, PH = 46, 44, 4, 15, 63
    pitch, subs = 5.5, (1.6, 2.2)
    ys, y = [], 0.0
    layout = []
    for gi in range(2):
        layout.append(("header", y))
        y += 4.4
        for _ in range(3 if gi == 0 else 2):
            layout.append(("row", y + pitch / 2))
            y += pitch + 2 * subs[gi]
        y += 2.0
    total = y - 2.0
    table = {}
    drawn_bands, drawn_thick = [], []
    offs = {k: {"b2sentence": -sub, "b2mixed": 0.0, "b1names": sub} for k, sub in (("semeval", subs[0]), ("ood", subs[1]))}
    for p, (model, mlabel) in enumerate(BACKBONES):
        ax = axes_mm(fig, LBL + p * (PW + GAP), TOP, PW, PH)
        spines(ax, left=False)
        ax.set_ylim(total, 0)
        auroc_x(ax, labels=True, label="")
        ax.set_yticks([])
        rows = signal_rows(src, model)
        row_pos = [v for k, v in layout if k == "row"]
        hdr = [v for k, v in layout if k == "header"]
        ym = row_pos[4] + offs["ood"]["b2mixed"]
        if h1_cell("b2mixed", model, "older_clean"):
            half = 1.25
            draw_band(ax, "H1", lo=ym - half, hi=ym + half, label=BAND_LABEL, label_at=(MARGIN[1] + 0.06, ym), va="center",
                      ha="left")
            ax.text(MARGIN[1] + 0.06, ym + 2.5, "H1 decision", ha="left", va="center", fontsize=SMALL, color=TEXT2,
                    zorder=2)
            drawn_bands.append(f"{mlabel} | Mixed-input | Older-clean")
        chance(ax, label_at=(0.505, 0.3) if p == 0 else None, va="top")
        ax.axhline((row_pos[2] + hdr[1]) / 2 + 1.2, color=NEUTRAL, lw=0.4, zorder=1)
        for (kind, label, cells), yr in zip(rows, row_pos):
            for s, _ in REGIMES:
                if s not in cells:
                    continue
                m, hollow = MARKER[s]
                c = cells[s]
                thick = label.startswith("Older-clean") and h1_cell(s, model, "older_clean")
                mark(ax, yr + offs[kind][s], c, SEMEVAL, m, hollow, MS, ci90=thick)
                if thick:
                    drawn_thick.append(f"{mlabel} | {dict(REGIMES)[s]} | Older-clean")
                if kind == "ood":
                    ax.text(c["hi95"] + 0.015, yr + offs[kind][s], f2(c["value"]), ha="left", va="center", fontsize=SMALL,
                            color=TEXT2)
                table[f"{mlabel} | {label} | {dict(REGIMES)[s]}"] = c
        if p == 0:
            for (kind, label, _), yr in zip(rows, row_pos):
                bg.text(2, TOP + yr * PH / total, label, ha="left", va="center", fontsize=BASE, color=TEXT,
                        linespacing=1.1)
            bg.text(2, TOP + hdr[0] * PH / total + 1.6, "SemEval test instances", ha="left", va="center", fontsize=BASE,
                    fontweight="bold")
            bg.text(2, TOP + hdr[1] * PH / total + 1.6, "Unseen drugs, names only", ha="left", va="center", fontsize=BASE,
                    fontweight="bold")
        panel_label(ax, "ABC"[p], mlabel, dy=9)
        ax.annotate(seed_title(src, model), xy=(0, 1), xycoords="axes fraction", xytext=(7, 2), textcoords="offset points",
                    fontsize=SMALL, color=TEXT2, ha="left", va="bottom")
    bg.text(LBL + (3 * PW + 2 * GAP) / 2, H - 4.5, "AUROC", ha="center", va="center", fontsize=BASE)
    want = ["BiomedBERT | Mixed-input | Older-clean"]
    if drawn_bands != want or drawn_thick != want:
        raise AssertionError(f"band rule: bands {drawn_bands}, thick 90% bars {drawn_thick}, expected only {want}")
    src.L.check("band rule:equivalence bands drawn in Fig 3", len(drawn_bands), 1, "only Mixed-input BiomedBERT Older-clean", tol=0)
    src.L.check("band rule:thick 90% bars drawn in Fig 3", len(drawn_thick), 1, "only Mixed-input BiomedBERT Older-clean", tol=0)
    save(fig, out, "fig3_encoders", bands=1, thick=1)
    return table


def fig_sentence(src, out):
    W, H = W_DOUBLE, 73
    fig = figure(W, H)
    bg = canvas(fig)
    TOP, PH = 14, 44
    AW, CW = 44, 42
    ax = axes_mm(fig, 13, TOP, AW, PH)
    bx = axes_mm(fig, 69, TOP, 50, PH)
    CX = 146
    cx = axes_mm(fig, CX, TOP, CW, PH)
    table = {"A": {}, "B": {}, "C": {}}
    conds = [("Original", "orig"), ("Other\nSemEval\ndrugs", "vocab"), ("Novel\ndrugs", "novel"), ("Pseudo-\nwords", "pseudo")]
    spines(ax, bottom=False)
    chance(ax, vertical=False, label_at=(-0.35, 0.503))
    dx = {"b2sentence": -1.2 / AW * 3.9, "b2mixed": 1.2 / AW * 3.9, "b1names": 0.0}
    sent_vals, name_vals = [], []
    for s, lab in REGIMES:
        fmt = "names" if s == "b1names" else "sentence"
        g = src.d.gk(s)
        cells = []
        for _, k in conds:
            c = src.d.cell(g, f"test_{fmt}" if k == "orig" else f"swap_{k}_{fmt}")
            cells.append(summ(c["auroc"], c["lo"], c["hi"], source=c["source"]))
        m, hollow = MARKER[s]
        ls = (0, (4, 2)) if s == "b1names" else "-"
        for j in range(1, len(conds)):
            ax.plot([0 + dx[s], j + dx[s]], [cells[0]["value"], cells[j]["value"]], color=SEMEVAL, lw=0.6 if s != "b1names" else 1.0,
                    ls=ls, zorder=2, alpha=0.9)
        for j, c in enumerate(cells):
            mark(ax, j + dx[s], c, SEMEVAL, m, hollow, MS, horizontal=False, zorder=3)
        table["A"][lab] = {k: c for (_, k), c in zip(conds, cells)}
        (name_vals if s == "b1names" else sent_vals).extend(c["value"] for c in cells[1:])
    ax.set_xlim(-0.4, len(conds) - 0.5)
    ax.set_ylim(0.4, 1.0)
    ax.set_yticks(np.round(np.arange(0.4, 1.01, 0.2), 1))
    ax.set_yticks(np.round(np.arange(0.5, 1.01, 0.2), 1), minor=True)
    ax.grid(axis="y", which="both", color=GRID, lw=0.4, zorder=0)
    ax.set_xticks(range(len(conds)), [c[0] for c in conds])
    ax.tick_params(axis="x", length=0, labelsize=SMALL)
    ax.set_ylabel("AUROC on SemEval test")
    rng = lambda v: f2(min(v)) if f2(min(v)) == f2(max(v)) else f"{f2(min(v))} to {f2(max(v))}"
    ax.text(len(conds) - 0.5, min(sent_vals) - 0.04, f"Sentence readers {rng(sent_vals)}", ha="right", va="top",
            fontsize=SMALL, color=SEMEVAL)
    ax.text(len(conds) - 0.5, 0.645, f"Names-trained {rng(name_vals)}", ha="right", va="bottom",
            fontsize=SMALL, color=SEMEVAL)
    panel_label(ax, "A", "Both drug names replaced", dy=11)
    masks = [r for r in src.d.tables["masking"] if r["model"] == "biomedbert" and r["split"] == "standard"]
    spines(bx, bottom=False)
    bx.grid(axis="y", color=GRID, lw=0.4, zorder=0)
    ann = {}
    texts = {}
    for i, (s, lab, hid) in enumerate((("b2sentence", "Sentence-trained", "H2a"), ("b2masked", "Masked-trained", "H2b"))):
        rs = sorted([r for r in masks if r["system"] == s], key=lambda r: r["seed"])
        m, hollow = MARKER[s]
        o = (i - 0.5) * 0.08
        for r in rs:
            bx.plot([0 + o, 1 + o], [r["f1_sentence"], r["f1_masked"]], color=SEMEVAL, lw=0.6, alpha=0.9, zorder=2)
        for j, field in enumerate(("f1_sentence", "f1_masked")):
            v = [r[field] for r in rs]
            bx.plot([j + o] * len(v), v, m, ms=2.5, mfc=SURFACE, mec=SEMEVAL, mew=0.6, zorder=3)
            bx.plot(j + o, float(np.median(v)), m, ms=MS, mfc=SURFACE if hollow else SEMEVAL, mec=SEMEVAL if hollow else SURFACE,
                    mew=0.8 if hollow else 0.6, zorder=4)
        ratios = sorted(r["ratio"] for r in rs)
        d = src.d.decisions[hid]
        if hid == "H2a":
            src.L.check("decisions:H2a ratio", float(np.mean(ratios)), d["value"]["ratio"], "H2a", tol=6e-4)
            ann[hid] = f"H2a {d['decision']}; seed-mean ratio {d['value']['ratio']:.3f}"
            if ann[hid] != "H2a falsified; seed-mean ratio 0.028":
                raise AssertionError(f"H2a annotation changed: {ann[hid]!r}")
        else:
            med = float(np.median(ratios))
            txt_med = re.search(r"median ratio ([0-9.]+)", d["detail"]).group(1)
            lo, hi = re.search(r"per-seed ratio range ([0-9.]+) to ([0-9.]+)", d["detail"]).groups()
            src.L.check("decisions:H2b median", med, float(txt_med), "H2b", tol=6e-4)
            src.L.check("decisions:H2b min", ratios[0], float(lo), "H2b", tol=6e-4)
            src.L.check("decisions:H2b max", ratios[-1], float(hi), "H2b", tol=6e-4)
            if d["decision"] == "supported" and "mean" not in d["detail"]:
                raise AssertionError("H2b detail no longer names the seed-mean aggregation")
            ann[hid] = f"Masked-trained: H2b {d['decision']} (seed-mean rule); median ratio {txt_med}, seeds {lo} to {hi}"
            if ann[hid] != "Masked-trained: H2b supported (seed-mean rule); median ratio 1.581, seeds 1.364 to 23.939":
                raise AssertionError(f"H2b annotation changed: {ann[hid]!r}")
            texts = {"median_text": txt_med, "range_text": [lo, hi]}
        table["B"][lab] = {"per_seed": {r["seed"]: [r["f1_sentence"], r["f1_masked"]] for r in rs},
                           "median_ratio": float(np.median(ratios)), "ratio_range": [ratios[0], ratios[-1]],
                           "decision": d["decision"], "source": f"tables.json masking; decisions.json {hid}",
                           **(texts if hid == "H2b" else {})}
    sent_masked = float(np.median([r["f1_masked"] for r in masks if r["system"] == "b2sentence"]))
    wrap = lambda t: "\n".join(textwrap.wrap(t, 21))
    bx.text(1.13, sent_masked + 0.01, wrap(ann["H2a"]), ha="left", va="bottom", fontsize=SMALL, color=TEXT2, linespacing=1.15)
    mk_masked = float(np.median([r["f1_masked"] for r in masks if r["system"] == "b2masked"]))
    bx.text(1.13, mk_masked + 0.04, wrap(ann["H2b"]), ha="left", va="top", fontsize=SMALL, color=TEXT2, linespacing=1.15)
    bx.set_xlim(-0.2, 2.5)
    bx.set_ylim(0, 0.8)
    bx.set_xticks([0, 1], ["Names\nvisible", "Names\nmasked"])
    bx.tick_params(axis="x", length=0, labelsize=SMALL)
    bx.set_ylabel("Binary F1 on SemEval test")
    panel_label(bx, "B", "Masking the names", dy=11)
    rows = [("Sentence input,\nSentence-trained", "b2sentence-biomedbert-disjoint-s42", "test_sentence", "b2sentence"),
            ("Sentence input,\nMixed-input", "b2mixed-biomedbert-disjoint-s42", "test_sentence", "b2mixed"),
            ("Names only,\nMixed-input", "b2mixed-biomedbert-disjoint-s42", "test_empty", "b2mixed"),
            ("Names only,\nNames-trained", "b1names-biomedbert-disjoint-s42", "test_names", "b1names")]
    spines(cx, left=False)
    chance(cx)
    ylim = (len(rows) - 0.5, -0.5)
    cx.set_ylim(*ylim)
    arrows = 0
    for i, (lab, job, key, s) in enumerate(rows):
        y = i
        seen = src.d.disjoint_cell(job, key, "seen")
        uns = src.d.disjoint_cell(job, key, "unseen")
        cs_ = {k: summ(v["auroc"], v["lo"], v["hi"], source=v["source"]) for k, v in (("seen", seen), ("unseen", uns))}
        m = MARKER[s][0]
        cx.annotate("", xy=(cs_["unseen"]["value"], y - DODGE), xytext=(cs_["seen"]["value"], y + DODGE),
                    arrowprops=dict(arrowstyle="-|>,head_length=0.3,head_width=0.13", color=TEXT, lw=0.6,
                                    shrinkA=2.4, shrinkB=2.4), zorder=2)
        arrows += 1
        mark(cx, y + DODGE, cs_["seen"], SEMEVAL, m, True, MS)
        mark(cx, y - DODGE, cs_["unseen"], SEMEVAL, m, False, MS + 0.6)
        bg.text(CX - 2.5, TOP + (y - ylim[1]) / (ylim[0] - ylim[1]) * PH, lab, ha="right", va="center", fontsize=BASE,
                color=TEXT, linespacing=1.1)
        table["C"][lab.replace("\n", " ")] = cs_
    src.L.check("fig4 panel C:arrows drawn, one per row", arrows, len(rows), "held-out cost arrows", tol=0)
    cx.set_yticks([])
    auroc_x(cx, 0.4, 1.0)
    bg.text(121, TOP - 11 * 0.3528 - 0.2, "C", ha="left", va="baseline", fontsize=LETTER, fontweight="bold")
    bg.text(125.5, TOP - 11 * 0.3528 - 0.2, "Held-out SemEval drugs (seed 42)", ha="left", va="baseline", fontsize=BASE)
    bg.text(125.5, TOP - 1.0, "open: all drugs seen; filled: a held-out drug", ha="left", va="baseline", fontsize=SMALL,
            color=TEXT2)
    save(fig, out, "fig4_sentence_signal")
    table["seeds"] = {lab: src.d.seeds(src.d.gk(s)) for s, lab in REGIMES}
    table["held_out_cost"] = {k: table["C"][k]["seen"]["value"] - table["C"][k]["unseen"]["value"] for k in table["C"]}
    return table


def e7_point_check(src, arm, cohort, stored_value, key_i):
    if not src.a7preds.exists():
        return
    avg = aa.seed_average(src.a7preds, arm, aa.KEYS[arm][key_i])
    if avg is None:
        return
    c = src.a7truth().cohort(cohort)
    mode = "pooled" if arm == "a" else "within"
    src.L.check(f"e7:{arm}:{cohort}:point", aa.point(c["y"], avg["p"][c["mask"]], c["g"], mode), stored_value,
                f"E7{arm} {cohort} recomputed from a7 predictions", tol=1e-9)


def e8_point_check(src, job, key_suffix, cohort, stored_value):
    if not src.a7preds.exists():
        return
    r = aa.read_job(src.a7preds, f"a7-qwen-{job}")
    if r is None:
        return
    c = src.a7truth().cohort(cohort)
    key = ("ood" if cohort == "novel" else "oodold") + key_suffix
    v = aa.point(c["y"], np.asarray(r["eval"][key]["p"], float)[c["mask"]], c["g"])
    src.L.check(f"e8:{job}:{cohort}:point", v, stored_value, f"E8 {job} {cohort} recomputed from a7 predictions", tol=1e-9)


def row(label, color, mk, cells, group="main", thr=None, ticks=None, ranges=None, style="normal", notes=None,
        ideals=None, bars_behind=()):
    return {"kind": "row", "label": label, "color": color, "mk": mk, "cells": cells, "group": group, "thr": thr or {},
            "ticks": ticks or {}, "ranges": ranges or {}, "style": style, "notes": notes or {}, "ideals": ideals or {},
            "bars_behind": tuple(bars_behind)}


def header(text, group="main"):
    return {"kind": "header", "label": text, "group": group}


def flat(label):
    return label.replace("\n", " ")


def fig5_rows(src):
    cs = src.cs["cells"]
    rows = []
    rows.append(header("SemEval labels"))
    b2 = {c: from_stat(cs[f"{c}:A"]["systems"]["b2mixed"], f"classshortcut.json cells {c}:A systems b2mixed") for c in ("novel", "older_primary")}
    tr = src.a7truth()
    for cname, key in (("novel", "ood_empty"), ("older_primary", "oodold_empty")):
        e = src.d.aggs[src.d.gk("b2mixed")]["evals"][key]
        c = tr.cohort(cname)
        est = aa.estimate(c, e["p"][c["mask"]], src.boot)
        src.L.check_cell("classshortcut:b2mixed", est, b2[cname], cname, tol=TOL if src.boot_ok else 1.0,
                         keys=("value", "lo95", "hi95", "lo90", "hi90") if src.boot_ok else ("value",))
    src.L.check("decisions:H1-novel", b2["novel"]["value"], src.d.decisions["H1-novel"]["value"], "b2mixed Novel")
    rows.append(row("Mixed-input BiomedBERT, names only", SEMEVAL, "b2mixed", b2))
    h5 = src.d.decisions["H5"]
    h5c = summ(h5["value"][0], h5["interval"][0], h5["interval"][1], source="decisions.json H5 (pooled AUROC)")
    rows.append(row(f"H5 control, SemEval labels (pooled): {h5['decision']}", SEMEVAL, "h5", {"novel": h5c},
                    thr={"novel": [(aa.H5_AUROC, "threshold")]}))
    if src.e7 is None:
        rows.append(header("Label-mention targets (E7) pending"))
        return rows
    e7 = src.e7
    rows.append(header("Integrity controls (answer supplied)"))
    a = e7["e7a"]
    e7_point_check(src, "a", "novel", a["pooled_auroc"]["value"], 1)
    ideal = src.ideal["variants"]["contaminated"]["readers"]["ideal_reader"]["auroc_pooled"]
    auc_ok = a["pooled_auroc"]["value"] >= a["thresholds"][0]
    mcc_ok = a["mcc_majority_vote"] >= a["thresholds"][1]
    if (auc_ok and mcc_ok) != a["pass"] or a["decision"] != ("pass" if a["pass"] else "fail"):
        raise AssertionError("E7a decision does not follow from its AUROC and MCC thresholds")
    word = lambda ok: "pass" if ok else "fail"
    rows.append(row(f"E7a, H5 input, label-mention targets\n(pooled): {word(auc_ok)} on AUROC, {word(mcc_ok)} on MCC",
                    EXTERNAL, "e7", {"novel": from_stat(a["pooled_auroc"], "e7.json e7a pooled_auroc")},
                    thr={"novel": [(a["thresholds"][0], "threshold")]}, ideals={"novel": [(ideal, "ideal reader")]}))
    b = e7["e7b"]
    for cname, ki in (("novel", 1), ("older_primary", 2)):
        e7_point_check(src, "b", cname, b[cname]["within"]["value"], ki)
    vals = [b[c]["within"]["value"] for c in ("novel", "older_primary")]
    if min(vals) < 1.0 - 5e-4:
        raise AssertionError(f"E7b no longer scores 1.000 in both cohorts: {vals}")
    rows.append(row(f"E7b, answer placed in the input\n({f2(min(vals))} by construction)", EXTERNAL, "e7",
                    {c: from_stat(b[c]["within"], f"e7.json e7b {c} within") for c in ("novel", "older_primary")},
                    thr={c: [(b[c]["threshold"], "threshold")] for c in ("novel", "older_primary")}))
    jobs = {"masked": "maskedoracle", "wrong": "wrongoracle", "redacted": "redactedoracle", "contam": "contam",
            "other": "other", "clean": "clean"}
    if src.e8 is not None:
        o = src.e8["e8_oracle_rule"]
        for c in ("novel", "older_primary"):
            e8_point_check(src, "oracle", "", c, o[c]["within"]["value"])
            src.L.check_cell("e8:oracle==evidence", o[c]["within"], src.e8["e8_evidence"]["oracle"][f"{c}/A"]["within"],
                             c, tol=TOL)
        op = o["older_primary"]
        if op["statistic"] != "lower95" or (op["within"]["lo95"] >= op["bar"]) != op["pass"]:
            raise AssertionError("E8 Older-primary oracle rule is not the lower-bound rule the figure draws")
        rel = "<" if op["within"]["lo95"] < op["bar"] else "\u2265"
        rows.append(row(f"E8 oracle, Qwen reads its own\nsection: {o['decision']}", EXTERNAL, "e8",
                        {c: from_stat(o[c]["within"], f"e8.json e8_oracle_rule {c} within") for c in ("novel", "older_primary")},
                        thr={c: [(o[c]["bar"], "bar")] for c in ("novel", "older_primary")},
                        ticks={c: [(o[c]["grep"], "regex")] for c in ("novel", "older_primary")},
                        notes={"older_primary": f"lower bound {op['within']['lo95']:.3f}\n{rel} bar {op['bar']:.3f}"},
                        bars_behind=("older_primary",)))
        if src.p8_sens is not None:
            ps = src.p8_sens["e8"]
            for c in ("novel", "older_primary"):
                src.L.check_cell("post8:e8 tier A", o[c]["within"], ps["A"][c]["within"], c, tol=TOL4)
            ca = ps["C-auto"]
            drop = {c: src.p8_sens["tiers"]["C-auto"][c]["positives_dropped"] for c in ("novel", "older_primary")}
            src.L.check("post8:C-auto flagged positives dropped, Older-primary", drop["older_primary"], 37, "C-auto row label", tol=0)
            src.L.check("post8:C-auto flagged positives dropped, Novel", drop["novel"], 1, "C-auto row label", tol=0)
            if src.p8_screen is not None:
                sc = src.p8_screen["counts"]
                src.L.check("post8:screen rule flags, Older-primary", sc["older/older_primary"]["rule_flags"], drop["older_primary"],
                            "C-auto row label", tol=0)
                src.L.check("post8:screen rule flags, Novel", sc["novel/all"]["rule_flags"], drop["novel"], "C-auto row label", tol=0)
            r = row(f"Same, tier C-auto (flagged positives dropped:\n{drop['novel']} Novel, {drop['older_primary']} Older-primary; post hoc)",
                    EXTERNAL, "e8s",
                    {c: from_stat(ca[c]["within"], f"post8/sensitivity.json e8 C-auto {c} within")
                     for c in ("novel", "older_primary")}, style="sens")
            r["sens"] = {"decision": ca["decision"], "bar": {c: ca[c]["bar"] for c in ("novel", "older_primary")}}
            rows.append(r)
        rows.append(header("Oracle controls (E8)"))
        names = {"masked": "Name-masked oracle", "wrong": "Wrong drug's section",
                 "redacted": "Partner sentences removed (confounded)"}
        for k, lab in names.items():
            evd = src.e8["e8_evidence"][k]
            ticks = {}
            for c in ("novel", "older_primary"):
                e8_point_check(src, jobs[k], "", c, evd[f"{c}/A"]["within"]["value"])
                if k == "redacted" and src.p8_red is not None:
                    rc = src.p8_red["tiers"]["A"][c]
                    src.L.check("post8:redacted qwen", evd[f"{c}/A"]["within"]["value"], rc["qwen_redacted_within"]["value"], c)
                    ticks[c] = [(rc["length_only_within"]["value"], "length only")]
            rows.append(row(lab, EXTERNAL, "e8h" if k == "redacted" else "e8",
                            {c: from_stat(evd[f"{c}/A"]["within"], f"e8.json e8_evidence {k} {c}/A within")
                             for c in ("novel", "older_primary")}, ticks=ticks))
    else:
        rows.append(header("Evidence reader (E8) pending"))
    rows.append(header("Pair-label arms (E7, exploratory)", "supp"))
    for arm, lab in (("c", "E7c, names only"), ("d", "E7d, other drugs' labels retrieved"), ("e", "E7e, clean retrieval")):
        cells = {}
        for cname, ki in (("novel", 1), ("older_primary", 2)):
            st = e7["knowledge"][arm][f"{cname}/A"]["within"]
            e7_point_check(src, arm, cname, st["value"], ki)
            ref = cs[f"{cname}:A"]["systems"][f"E7{arm}"]
            src.L.check_cell(f"classshortcut:E7{arm}", st, ref, cname, tol=TOL)
            cells[cname] = from_stat(st, f"e7.json knowledge {arm} {cname}/A within")
        rows.append(row(lab, EXTERNAL, "e7", cells, group="supp"))
        if arm == "c":
            adj = {c: from_stat(cs[f"{c}:A"]["partial"]["rank:joint"]["residual_within"],
                                f"classshortcut.json {c}:A partial rank:joint residual_within") for c in ("novel", "older_primary")}
            for c in ("novel", "older_primary"):
                src.L.check_cell("classshortcut:E7c_within", cs[f"{c}:A"]["partial"]["E7c_within"], cs[f"{c}:A"]["systems"]["E7c"],
                                 c, tol=TOL)
            rows.append(row("E7c, adjusted for drug class", EXTERNAL, "e7h", adj, group="supp"))
    if src.e8 is not None:
        rows.append(header("Qwen2.5-7B arms (E8, exploratory)", "supp"))
        nm = src.e8["e8_names"]["cohorts"]
        from .amend7_prompts import PRIMARY
        cells, ranges = {}, {}
        for c in ("novel", "older_primary"):
            st = nm[c]["per_prompt"][PRIMARY]
            for pid, v in nm[c]["per_prompt"].items():
                e8_point_check(src, "names", f"_{pid}", c, v["value"])
            src.L.check("e8:names primary", st["value"], nm[c]["primary"], c, tol=TOL)
            vals = [v["value"] for v in nm[c]["per_prompt"].values()]
            src.L.check("e8:names min", min(vals), nm[c]["min"], c, tol=TOL)
            src.L.check("e8:names max", max(vals), nm[c]["max"], c, tol=TOL)
            cells[c] = from_stat(st, f"e8.json e8_names {c} primary prompt")
            ranges[c] = (nm[c]["min"], nm[c]["max"])
        rob = "robust" if src.e8["e8_names"]["robust"] else "not robust"
        rows.append(row(f"Names only (5 prompts: {rob})", EXTERNAL, "qwen", cells, group="supp", ranges=ranges))
        for k, lab in (("contam", "Contaminated retrieval"), ("other", "Other drugs' labels"), ("clean", "Clean retrieval")):
            evd = src.e8["e8_evidence"][k]
            for c in ("novel", "older_primary"):
                e8_point_check(src, jobs[k], "", c, evd[f"{c}/A"]["within"]["value"])
            rows.append(row(lab, EXTERNAL, "qwen", {c: from_stat(evd[f"{c}/A"]["within"], f"e8.json e8_evidence {k} {c}/A within")
                                                    for c in ("novel", "older_primary")}, group="supp"))
    dbc = {}
    for c in ("novel", "older_primary"):
        dop = cs[f"{c}:A"]["drugbank_operating_point"]["drugbank_auroc_from_placements"]
        dbc[c] = from_stat(dop, f"classshortcut.json {c}:A drugbank_operating_point drugbank_auroc_from_placements")
        src.L.check("e7:drugbank_within", dbc[c]["value"], e7["knowledge"]["c"][f"{c}/A"]["drugbank_within"], c, tol=TOL)
    src.L.check("drugbank_lookup:novel within", dbc["novel"]["value"], src.db_lookup["novel"]["auroc_within"], "novel")
    for g in ("main", "supp"):
        rows.append(header("External reference", g))
        rows.append(row("DrugBank lookup", DRUGBANK, "drugbank", dbc, group=g))
    return rows


def row_layout(rows, single=5.2, double=7.4, hgap=5.0):
    ys, y = [], 0.0
    for r in rows:
        if r["kind"] == "header":
            y += hgap if ys else 3.2
            ys.append(y - 1.2)
        else:
            h = double if "\n" in r["label"] else single
            y += h
            ys.append(y - h / 2)
    return ys, y + 0.8


def draw_rows(fig, bg, rows, ys, total, TOP, LBL, PW, GAP, cohorts, letter="A", value_col=False):
    table = {}
    for ci, (cname, ctitle) in enumerate(cohorts):
        ax = axes_mm(fig, LBL + ci * (PW + GAP), TOP, PW, total)
        spines(ax, left=False)
        ax.set_ylim(total, 0)
        auroc_x(ax, 0.3, 1.0, label="")
        ax.set_xlim(0.3, 1.025)
        ax.set_yticks([])
        chance(ax, label_at=(0.51, 0.2) if ci == 0 else None, va="top")
        for k, (r, yv) in enumerate(zip(rows, ys)):
            if r["kind"] == "header":
                if ci == 0:
                    bg.text(2, TOP + yv, r["label"], ha="left", va="center", fontsize=SMALL + 0.5, fontweight="bold")
                ax.axhline(yv - 1.6, color=NEUTRAL, lw=0.4, zorder=1)
                continue
            label, color, mk, cells = r["label"], r["color"], r["mk"], r["cells"]
            sens = r["style"] == "sens"
            rh = 7.4 if "\n" in label else 5.2
            if ci == 0:
                bg.text(4, TOP + yv, label, ha="left", va="center", fontsize=SMALL, color=TEXT2 if sens else TEXT,
                        linespacing=1.1)
            if cname in r["ranges"]:
                lo, hi = r["ranges"][cname]
                table[f"{cname} | {flat(label)} | prompt range"] = [lo, hi]
                ax.plot([lo, hi], [yv, yv], color=r["color"], lw=5.0, alpha=0.45, zorder=2, solid_capstyle="butt")
            if cname not in cells:
                ax.text(0.5, yv, "not run", ha="center", va="center", fontsize=SMALL, color=TEXT2, zorder=6,
                        bbox=dict(fc=SURFACE, ec="none", pad=0.8))
                table[f"{cname} | {flat(label)} | not run"] = True
                continue
            c = cells[cname]
            marker, hollow = {"e7h": ("s", True), "e8h": ("v", False), "e8s": ("v", True)}.get(mk, MARKER.get(mk, ("s", False)))
            behind = cname in r["bars_behind"]
            mark(ax, yv, c, color, marker, hollow, MS_BOLD if behind else MS)
            table[f"{cname} | {flat(label)}"] = c
            for xv, lab in r["thr"].get(cname, []):
                draw_thr(ax, xv, yv, rh / 2 if behind else 2.1, 1 if behind else 5)
                table[f"{cname} | {flat(label)} | {lab}"] = xv
            for xv, lab in r["ticks"].get(cname, []):
                draw_ref(ax, xv, yv)
                table[f"{cname} | {flat(label)} | {lab}"] = xv
            for xv, lab in r["ideals"].get(cname, []):
                draw_ideal(ax, xv, yv)
                table[f"{cname} | {flat(label)} | {lab}"] = xv
            tc = TEXT2
            if value_col:
                ax.text(1.025 + 0.012, yv, f2(c["value"]), transform=ax.get_yaxis_transform(), ha="left", va="center",
                        fontsize=SMALL, color=TEXT2 if sens else tc)
                if cname in r["notes"]:
                    ax.text(c["lo95"] - 0.015, yv, r["notes"][cname], ha="right", va="center", fontsize=SMALL, color=TEXT,
                            linespacing=1.1)
                continue
            if cname in r["notes"]:
                ax.text(c["lo95"] - 0.015, yv, r["notes"][cname], ha="right", va="center", fontsize=SMALL, color=TEXT,
                        linespacing=1.1)
            elif c.get("hi95") is not None and c["hi95"] < 0.9 and not r["thr"].get(cname):
                ax.text(c["hi95"] + 0.015, yv, f2(c["value"]), ha="left", va="center", fontsize=SMALL, color=tc)
            else:
                marks = ([t for t, _ in r["thr"].get(cname, [])] + [t for t, _ in r["ideals"].get(cname, [])]
                         + [t for t, _ in r["ticks"].get(cname, [])])
                left = min([c["lo95"] if c.get("lo95") is not None else c["value"]] + marks)
                right = max([c["hi95"] if c.get("hi95") is not None else c["value"]] + marks)
                w = 4.0 / PW * (1.025 - 0.3)
                if left - 0.015 - w < 0.52 and right + 0.015 + w < 1.025:
                    ax.text(right + 0.015, yv, f2(c["value"]), ha="left", va="center", fontsize=SMALL, color=tc)
                else:
                    ax.text(left - 0.015, yv, f2(c["value"]), ha="right", va="center", fontsize=SMALL, color=tc)
        if ci == 0 and letter is not None:
            panel_label(ax, letter, ctitle)
        else:
            ax.annotate(ctitle, xy=(0, 1), xycoords="axes fraction", xytext=(0, 4), textcoords="offset points",
                        fontsize=BASE, ha="left", va="bottom")
    return table


def fig5_cohorts(src):
    n = {c: src.cs["cells"][f"{c}:A"]["n_drugs"] for c in ("novel", "older_primary")}
    return (("novel", f"Novel ({n['novel']} drugs)"), ("older_primary", f"Older-primary ({n['older_primary']} drugs)"))


def draw_thr(ax, x, y, half, zorder=5):
    ax.plot([x, x], [y - half, y + half], color=REF, lw=0.8, zorder=zorder, solid_capstyle="butt")


def draw_ref(ax, x, y):
    ax.plot(x, y, "|", ms=5, mew=0.8, color=TEXT2, zorder=5)


def draw_ideal(ax, x, y):
    ax.plot(x, y, "o", ms=MS, mfc=SURFACE, mec=SHORTCUT, mew=0.8, zorder=6)


def draw_tick_key(bg, x, y, ideal_text):
    draw_thr(bg, x + 1.5, y, 2.1)
    bg.text(x + 5, y, "pass threshold or bar", ha="left", va="center", fontsize=SMALL, color=TEXT)
    draw_ref(bg, x + 1.5, y + 4.7)
    bg.text(x + 5, y + 4.7, "trivial reference score: regex baseline\nor length only, both 1.000", ha="left", va="center",
            fontsize=SMALL, color=TEXT, linespacing=1.15)
    draw_ideal(bg, x + 1.5, y + 10.2)
    bg.text(x + 5, y + 10.2, ideal_text, ha="left", va="center", fontsize=SMALL, color=TEXT)


def fig_controls(src, out):
    allrows = fig5_rows(src)
    rows = [r for r in allrows if r["group"] == "main"]
    ys, total = row_layout(rows)
    W, TOP = W_DOUBLE, 12
    H = TOP + total + 19
    fig = figure(W, H)
    bg = canvas(fig)
    LBL, PW, GAP = 62, 50, 15
    table = draw_rows(fig, bg, rows, ys, total, TOP, LBL, PW, GAP, fig5_cohorts(src), letter=None, value_col=True)
    for r in rows:
        if r.get("sens"):
            table["sensitivity"] = {"label": flat(r["label"]), **r["sens"]}
    if src.e7 is not None:
        a = src.e7["e7a"]
        table["e7a_rule"] = {"auroc": a["pooled_auroc"]["value"], "mcc": a["mcc_majority_vote"],
                             "thresholds": a["thresholds"], "decision": a["decision"]}
    if src.e8 is not None:
        o = src.e8["e8_oracle_rule"]
        table["e8_oracle_rule"] = {"decision": o["decision"],
                                   **{c: {k: o[c][k] for k in ("statistic", "bar", "grep", "pass")} for c in ("novel", "older_primary")}}
    bg.text(LBL + PW + GAP / 2, TOP + total + 9, "AUROC, within-drug (E7a and H5 rows: pooled)", ha="center", va="center",
            fontsize=BASE)
    ideal_value = [c for k, c in table.items() if k.endswith("| ideal reader")]
    ideal_text = "ideal reader (E7a), n/a" if not ideal_value else f"ideal reader (E7a), {f3(ideal_value[0])}"
    if src.e7 is not None:
        src.L.check("fig4:ideal reader pooled AUROC drawn at 0.785", round(ideal_value[0], 3), 0.785, "E7a row, gray open circle",
                    tol=1e-12)
        if ideal_text != "ideal reader (E7a), 0.785":
            raise AssertionError(ideal_text)
        not_run = sorted(k.split(" | ")[1] for k in table if k.startswith("older_primary | ") and k.endswith(" | not run"))
        want = sorted(flat(r["label"]) for r in rows if r["kind"] == "row"
                      and "older_primary" not in r["cells"])
        src.L.check("fig4:rows marked not run in Older-primary", len(not_run), 2, "H5 and E7a", tol=0)
        if not_run != want or not all(k.startswith(("H5", "E7a")) for k in not_run):
            raise AssertionError(f"not-run rows {not_run} differ from the rows without an Older-primary cell {want}")
    draw_tick_key(bg, 2, TOP + total + 5.5, ideal_text)
    save(fig, out, "fig5_positive_controls")
    return table, allrows


def fig_amend7_detail(src, out, allrows):
    rows = [r for r in allrows if r["group"] == "supp"]
    ys, total = row_layout(rows)
    W, TOP = W_DOUBLE, 12
    H = max(TOP + total + 12, TOP + 108)
    fig = figure(W, H)
    bg = canvas(fig)
    LBL, PW, GAP = 50, 34, 4
    table = draw_rows(fig, bg, rows, ys, total, TOP, LBL, PW, GAP, fig5_cohorts(src))
    bg.text(LBL + PW + GAP / 2, TOP + total + 9, "Within-drug AUROC", ha="center", va="center", fontsize=BASE)
    X0 = LBL + 2 * PW + GAP + 24
    bw = W - X0 - 6
    ytitle = TOP - 4 * 0.3528
    if src.e7 is not None:
        bx = axes_mm(fig, X0, TOP + 9, bw, 30)
        table["B"] = draw_fair(bx, src)
        bg.text(X0 - 19.5, ytitle, "B", ha="left", va="bottom", fontsize=LETTER, fontweight="bold")
        bg.text(X0 - 15, ytitle, "E7c and DrugBank at the", ha="left", va="bottom", fontsize=BASE)
        bg.text(X0 - 15, ytitle + 3.8, "same false positive rate", ha="left", va="bottom", fontsize=BASE)
    if src.e8 is not None:
        cx = axes_mm(fig, X0, TOP + 66, bw, 20)
        table["C"] = draw_stem(cx, src)
        n = table["C"]["n_drugs"]
        bg.text(X0 - 19.5, TOP + 56, "C", ha="left", va="bottom", fontsize=LETTER, fontweight="bold")
        bg.text(X0 - 15, TOP + 56, f"E8 stem control, {n} stem-bearing", ha="left", va="bottom", fontsize=BASE)
        bg.text(X0 - 15, TOP + 59.8, "drugs (Novel and Older-primary)", ha="left", va="bottom", fontsize=BASE)
    save(fig, out, "figS_amend7_detail")
    return table


def draw_fair(bx, src):
    spines(bx, left=False)
    out = {}
    yt = []
    for i, c in enumerate(("novel", "older_primary")):
        op = src.cs["cells"][f"{c}:A"]["drugbank_operating_point"]
        db = from_stat(op["drugbank_tpr_within_at_its_fpr"], f"classshortcut.json {c}:A drugbank_tpr_within_at_its_fpr")
        e7c = from_stat(op["e7c_tpr_within_at_drugbank_fpr"], f"classshortcut.json {c}:A e7c_tpr_within_at_drugbank_fpr")
        diff = from_stat(op["e7c_minus_drugbank_tpr_within"], f"classshortcut.json {c}:A e7c_minus_drugbank_tpr_within")
        src.L.check("classshortcut:tpr difference", e7c["value"] - db["value"], diff["value"], c, tol=1e-9)
        y0 = i * 2.7
        mark(bx, y0, db, DRUGBANK, "D", False, MS)
        mark(bx, y0 + 0.7, e7c, EXTERNAL, "s", False, MS)
        bx.text(-0.55, y0 + 1.35, f"difference {diff['value']:.3f} {ci_text(diff)}", ha="left", va="center",
                fontsize=SMALL, color=TEXT2, transform=bx.get_yaxis_transform())
        bx.text(-0.55, y0 - 0.55, "Novel" if c == "novel" else "Older-primary", ha="left", va="center", fontsize=SMALL,
                fontweight="bold", transform=bx.get_yaxis_transform())
        yt += [(y0, "DrugBank"), (y0 + 0.7, "E7c")]
        out[c] = {"drugbank_tpr": db, "e7c_tpr": e7c, "difference": diff,
                  "drugbank_fpr": from_stat(op["drugbank_fpr_pooled"], f"classshortcut.json {c}:A drugbank_fpr_pooled")}
    bx.set_ylim(4.5, -1.0)
    bx.set_yticks([])
    for yv, t in yt:
        bx.text(-0.02, yv, t, ha="right", va="center", fontsize=SMALL, transform=bx.get_yaxis_transform())
    bx.set_xlim(0, 1)
    bx.set_xticks([0, 0.5, 1.0], ["0.0", "0.5", "1.0"])
    bx.grid(axis="x", color=GRID, lw=0.4, zorder=0)
    bx.set_xlabel("True positive rate", fontsize=SMALL)
    return out


def draw_stem(cx, src):
    spines(cx, left=False)
    s = src.e8["e8_stem_control"]
    rows = [("Real names", "real"), ("Stem kept", "preserved"), ("Stem scrambled", "scrambled")]
    out = {}
    chance(cx)
    for i, (lab, k) in enumerate(rows):
        c = from_stat(s[k], f"e8.json e8_stem_control {k}")
        mark(cx, i, c, EXTERNAL, "v", k != "real", MS)
        cx.text(-0.02, i, lab, ha="right", va="center", fontsize=SMALL, transform=cx.get_yaxis_transform())
        out[k] = c
    d = from_stat(s["preserved_minus_scrambled"], "e8.json e8_stem_control preserved_minus_scrambled")
    src.L.check("e8:stem difference", s["preserved"]["value"] - s["scrambled"]["value"], d["value"], "stem", tol=1e-9)
    verdict = s["decision"]
    cx.text(-0.55, 4.6, f"kept minus scrambled {d['value']:.3f} {ci_text(d)}:\n{verdict}", ha="left", va="top",
            fontsize=SMALL, color=TEXT2, transform=cx.get_yaxis_transform(), linespacing=1.15)
    cx.set_ylim(2.6, -0.6)
    cx.set_yticks([])
    auroc_x(cx, 0.3, 1.0, label="")
    cx.set_xlabel("Within-drug AUROC", fontsize=SMALL)
    out["difference"] = d
    out["verdict"] = verdict
    out["n_drugs"] = s["n_drugs"]
    out["expected_drop"] = aa.STEM_DROP
    return out


def panel_f1(src, names):
    ytest = np.asarray(src.d.truth.test_y)
    out = {}
    for n in names:
        r = json.loads((src.a7preds / f"{n}.json").read_text())
        out[n] = binary_f1(ytest, r["eval"]["test_sentence"]["preds"])
    return out


def fig_panel(src, out):
    W, H = W_SINGLE, 82
    fig = figure(W, H)
    bg = canvas(fig)
    ax = axes_mm(fig, 15, 8, 70, 58)
    spines(ax)
    table = {}
    if src.e9 is None or not src.a7preds.exists():
        pending_frame(ax, "E9", src.final)
        save(fig, out, "fig6_model_panel")
        return {"pending": True}
    e9 = src.e9["e9"]
    p = e9["panel"]["older_primary"]
    f1 = panel_f1(src, p["names"])
    if src.p8_e9 is not None:
        for cname in ("older_primary", "novel"):
            for r in src.p8_e9["tiers"]["A"][cname]["per_checkpoint"]:
                src.L.check("post8:e9 f1", f1[r["name"]], r["semeval_binary_f1"], r["name"], tol=TOL4)
        t8 = src.p8_e9["tiers"]["A"]["older_primary"]
        src.L.check("post8:e9 ratio_old", p["variance_ratio"], t8["ratio_old"], "older_primary", tol=TOL4)
        src.L.check("post8:e9 n_upper", sum(p["upper_at_most_bound"]), t8["n_upper_at_most_0.60"], "older_primary", tol=0)
    x = [f1[n] for n in p["names"]]
    from .amend7_panel import spearman
    src.L.check("e9:rho", spearman(x, p["auroc"]), p["rho"], "older_primary rho", tol=1e-9)
    if "novel" in e9["panel"]:
        q = e9["panel"]["novel"]
        src.L.check("e9:rho novel", spearman([f1[n] for n in q["names"]], q["auroc"]), q["rho"], "novel rho", tol=1e-9)
    src.L.check("e9:upper_at_most_bound", sum(h <= p["bound"] for h in p["hi95"]), sum(p["upper_at_most_bound"]),
                "older_primary count", tol=0)
    chance(ax, vertical=False, label_at=(0.45, 0.503), ha="center")
    db = src.cs["cells"]["older_primary:A"]["drugbank_operating_point"]["drugbank_auroc_from_placements"]["value"]
    src.L.check("e7:drugbank_within", db, src.e7["knowledge"]["c"]["older_primary/A"]["drugbank_within"], "fig6", tol=1e-9)
    ax.axhline(db, color=DRUGBANK, lw=0.8, zorder=2)
    ax.axhline(p["bound"], color=REF, lw=0.5, ls=(0, (1, 1.5)), zorder=2)
    for n, xv, a, lo, hi in zip(p["names"], x, p["auroc"], p["lo95"], p["hi95"]):
        mark(ax, xv, summ(a, lo, hi), SEMEVAL, "o", False, MS, horizontal=False, zorder=3, lw95=LW_95)
        table[n] = {"semeval_binary_f1": xv, "auroc_within": a, "lo95": lo, "hi95": hi,
                    "source": "e9.json panel older_primary; F1 recomputed with metrics.binary_f1 from test_sentence preds"}
    extra = {}
    for kind in ("external", "masked"):
        for n, v in e9.get(kind, {}).get("older_primary", {}).items():
            f = panel_f1(src, [n])[n]
            src.L.check(f"e9:{kind} f1", f, v["semeval_binary_f1"], n, tol=1e-9)
            extra[n] = {"kind": kind, "semeval_binary_f1": f, "auroc_within": v["auroc_within"]}
    msk = [v for v in extra.values() if v["kind"] == "masked"]
    ext = [v for v in extra.values() if v["kind"] == "external"]
    for v in ext:
        ax.plot(v["semeval_binary_f1"], v["auroc_within"], "o", ms=MS, mfc=SURFACE, mec=SEMEVAL, mew=0.8, zorder=4)
    for v in msk:
        m, hollow = MARKER["b2masked"]
        ax.plot(v["semeval_binary_f1"], v["auroc_within"], m, ms=MS + 1.5, mfc=SURFACE, mec=SEMEVAL, mew=1.0, zorder=10)
    allx = x + [v["semeval_binary_f1"] for v in extra.values()]
    lo_x = np.floor(min(allx) * 20) / 20 - 0.02
    hi_x = np.ceil(max(allx) * 20) / 20 + 0.01
    ax.set_xlim(lo_x, hi_x)
    ax.set_ylim(0.3, 0.75)
    ticks = np.round(np.arange(0.3, 0.751, 0.05), 2)
    ax.set_yticks(ticks)
    ax.set_yticklabels([f"{v:.2f}" for v in ticks])
    ax.tick_params(axis="y", labelsize=SMALL)
    ax.grid(axis="y", color=GRID, lw=0.4, zorder=0)
    ax.set_xlabel("SemEval test binary F1, with sentence", fontsize=SMALL)
    ax.set_ylabel("Older-primary within-drug AUROC,\nnames only", fontsize=SMALL, linespacing=1.15)
    ax.text(hi_x, db + 0.006, f"DrugBank lookup {f2(db)}", ha="right", va="bottom", fontsize=SMALL, color=TEXT)
    ax.text(hi_x, p["bound"] + 0.006, f"E9 rule: 95% upper bound at most {p['bound']:.2f}", ha="right", va="bottom",
            fontsize=SMALL, color=TEXT2)
    k = sum(p["upper_at_most_bound"])
    ax.text(lo_x + 0.005, 0.745, f"Spearman $\\rho$ = {p['rho']:.2f} [{p['rho_lo95']:.2f}, {p['rho_hi95']:.2f}], n = {p['n_models']}\n"
            f"{k} of {p['n_models']} upper bounds at most {p['bound']:.2f}", ha="left", va="top", fontsize=SMALL,
            color=TEXT, linespacing=1.2)
    if ext:
        e = ext[0]
        ax.text(e["semeval_binary_f1"], e["auroc_within"] - 0.025, "public\ncheckpoint", ha="center", va="top",
                fontsize=SMALL, color=TEXT2, linespacing=1.1)
    if msk:
        ax.text(0.46, 0.565, f"masked-trained\n({len(msk)} models)", ha="center", va="center", fontsize=SMALL, color=TEXT2)
        for v in msk:
            ax.annotate("", xy=(v["semeval_binary_f1"], v["auroc_within"] + 0.012), xytext=(0.52, 0.555), textcoords="data",
                        arrowprops=dict(arrowstyle="-", color=SHORTCUT, lw=0.5, shrinkA=0.0, shrinkB=3.2), zorder=11)
        src.L.check("fig5 panel:leaders drawn to masked diamonds", len(msk), 2, "masked-trained leaders", tol=0)
    save(fig, out, "fig6_model_panel")
    return {"models": table, "extra": extra, "rho": p["rho"], "rho_ci95": [p["rho_lo95"], p["rho_hi95"]],
            "n_models": p["n_models"], "k_upper_at_most_bound": k, "bound": p["bound"], "drugbank_within": db,
            "variance_ratio": p["variance_ratio"],
            "variance_ratio_paired": None if src.p8_e9 is None else src.p8_e9["tiers"]["A"]["older_primary"]["ratio_paired"],
            "novel": {kk: e9["panel"]["novel"][kk] for kk in ("rho", "rho_lo95", "rho_hi95", "n_models")}
            if "novel" in e9["panel"] else None}


def example_pair(src):
    for p in src.d.truth.sets["ood"]["pairs"]:
        if (p["drug_a"], p["drug_b"]) == EXAMPLE:
            return f"{p['drug_a']} + {p['drug_b']}", p["y"]
    raise AssertionError(f"example pair {EXAMPLE} is not in the Novel set")


GA_FONTS = ("Arial", "Helvetica")
GA_FALLBACK = ("Liberation Sans", "Nimbus Sans", "Arimo")
GA_MONO = ["Courier New", "Courier", "DejaVu Sans Mono"]


def ga_font():
    from matplotlib import font_manager as fm
    have = {f.name for f in fm.fontManager.ttflist}
    for name in GA_FONTS + GA_FALLBACK:
        if name in have:
            return name
    raise AssertionError(f"none of {GA_FONTS + GA_FALLBACK} is installed for the graphical abstract")


def fig_ga(src, out, series):
    import matplotlib as mpl
    font = ga_font()
    src.L.check("ga:font is Arial, Helvetica or a metric-compatible clone", float(font in GA_FONTS + GA_FALLBACK), 1.0,
                f"graphical abstract font {font}", tol=0)
    with mpl.rc_context({"font.family": [font], "font.sans-serif": [font], "pdf.fonttype": 42, "ps.fonttype": 42}):
        return draw_ga(src, out, series, font)


GA_PX = (2000, 800)
PX_PT = 72 / 300
GA_TITLE_PX, GA_LABEL_PX, GA_LINE_PX, GA_MIN_LABEL_PX = 44, 40, 8, 36
GA_TITLE = "Names-only AUROC against two label sources"
GA_NOTE = "Different drugs and statistics; FDA-label targets failed their oracle check"
GA_CONV = "DrugBank SemEval value excludes self pairs ({} with them). Bars: 95% intervals."
GA_COLS = ("SemEval labels\n(pooled)", "FDA label mentions\n(within-drug)")
GA_CI_PT = 2.4
GA_FOOT = "DrugBank draws partly on FDA labels; label mentions are not validated interactions."
GA_PRIOR_TITLE = "SemEval scores do not carry over to FDA-label targets"
GA_OLD_TITLE = ("Change the label source and the ranking flips; earlier still: Same two drug names, opposite rankings: SemEval labels favour the SemEval-trained encoder; "
                "FDA label mentions favour DrugBank")
GA_BAR_PT = 3.6


def gpt(px):
    return px * PX_PT


def draw_ga(src, out, series, font):
    W, H = GA_PX[0] / 300 / MM, GA_PX[1] / 300 / MM
    fig = figure(W, H)
    bg = canvas(fig)
    by = {s_["label"]: s_ for s_ in series["bold"]}
    enc, db = (by[k] for k in ("Mixed-input BiomedBERT", "DrugBank lookup"))
    ex = db["left_excl"]
    conv = GA_CONV.format(f3(db["left"]["value"]))
    src.L.check("ga:with-self-pairs value is 0.525", float(f3(db["left"]["value"]) == "0.525"), 1.0, conv, tol=0)
    cross = bool(enc["left"]["value"] > ex["value"] and db["right"]["value"] > enc["right"]["value"])
    src.L.check("ga:encoder leads on SemEval labels", float(cross), 1.0, "title claim: encoder above DrugBank on SemEval, "
                "below it on label mentions", tol=0)
    bg.text(3.5, 3.0, GA_TITLE, ha="left", va="top", fontsize=gpt(GA_TITLE_PX), fontweight="bold")
    ax = axes_mm(fig, 24, 17, 140, 27)
    spines(ax, bottom=False)
    ax.set_xlim(0, 140)
    ax.set_ylim(0.35, 0.75)
    ax.set_yticks([0.5, 0.7])
    ax.tick_params(axis="y", labelsize=gpt(GA_LABEL_PX), length=3)
    ax.set_ylabel("AUROC", fontsize=gpt(GA_LABEL_PX))
    xl, xr = 12.0, 62.0
    chance(ax, vertical=False, span=(0, 70))
    items = (("SemEval-trained encoder", enc, 0), ("DrugBank", db, 1))
    step = 3.2
    offs = (np.arange(2) - 0.5) * step
    ends = []
    ci_drawn = []
    for (name, s_, i), o in zip(items, offs):
        m, hollow = MARKER[s_["marker"]]
        c0 = s_["left_excl"] if "left_excl" in s_ else s_["left"]
        c1 = s_["right"]
        y0, y1 = c0["value"], c1["value"]
        for x_, c_, tag in ((xl + o, c0, "left"), (xr + o, c1, "right")):
            if c_.get("lo95") is None or c_.get("hi95") is None:
                raise AssertionError(f"graphical abstract {name} {tag} has no 95% interval")
            ax.plot([x_, x_], [c_["lo95"], c_["hi95"]], color=s_["color"], lw=GA_CI_PT, zorder=4, solid_capstyle="butt")
            ci_drawn.append((name, tag, c_))
        ax.plot([xl + o, xr + o], [y0, y1], color=s_["color"], lw=gpt(GA_LINE_PX), zorder=3)
        if "range" in s_["right"]:
            lo, hi = s_["right"]["range"]
            ax.plot([xr + o] * 2, [lo, hi], color=s_["color"], lw=GA_BAR_PT, zorder=3, solid_capstyle="butt")
        for x_, y_, h_ in ((xl + o, y0, hollow), (xr + o, y1, hollow and "range" not in s_["right"])):
            if h_:
                ax.plot(x_, y_, m, ms=8.5, mfc=SURFACE, mec=s_["color"], mew=1.6, zorder=5)
            else:
                ax.plot(x_, y_, m, ms=8.5, mfc=s_["color"], mec=SURFACE, mew=0.8, zorder=5)
        ends.append(y1)
    h_mm = ax.get_position().height * ax.figure.get_figheight() / MM
    ys = spread(ends, 5.2 / h_mm * 0.35)
    label_text = {}
    end_labels = []
    for (name, s_, i), y in zip(items, ys):
        txt = f"{name} {f2(s_['right']['value'])}"
        label_text[name] = txt
        end_labels.append(ax.text(xr + offs.max() + 5, y, txt, ha="left", va="center", fontsize=gpt(GA_LABEL_PX),
                                  color=s_["text_color"] if s_["color"] != EXTERNAL else TEXT, clip_on=False, zorder=6))
    src.L.check("ga:drawn series are the encoder and DrugBank only", len(items), 2, "graphical abstract", tol=0)
    src.L.check("ga:encoder label text", float(label_text["SemEval-trained encoder"] == f"SemEval-trained encoder {f2(enc['right']['value'])}"), 1.0,
                "encoder end label", tol=0)
    src.L.check("ga:drugbank label text", float(label_text["DrugBank"] == f"DrugBank {f2(db['right']['value'])}"), 1.0,
                "DrugBank end label", tol=0)
    src.L.check("ga:all intervals inside the axis", float(min(c_["lo95"] for _, _, c_ in ci_drawn) >= ax.get_ylim()[0]
                and max(c_["hi95"] for _, _, c_ in ci_drawn) <= ax.get_ylim()[1]), 1.0, "no interval is clipped", tol=0)
    src.L.check("ga:intervals drawn for every plotted point", len(ci_drawn), 4, "2 series x 2 columns", tol=0)
    segs = [tuple(np.round(ln.get_ydata(), 12)) for ln in ax.lines if ln.get_lw() == GA_CI_PT]
    src.L.check("ga:interval segments in the artwork", len(segs), 4, "drawn vertical interval lines", tol=0)
    for name, tag, c_ in ci_drawn:
        src.L.check(f"ga:{name} {tag} drawn lo95", float(tuple(np.round([c_["lo95"], c_["hi95"]], 12)) in segs), 1.0,
                    f"{name} {tag} interval [{c_['lo95']:.3f}, {c_['hi95']:.3f}] drawn", tol=0)
        src.L.check(f"ga:{name} {tag} interval brackets the point", float(c_["lo95"] < c_["value"] < c_["hi95"]), 1.0,
                    f"{name} {tag}", tol=0)
    src.L.check("ga:no range bars drawn", float(not any("range" in s_["right"] for _, s_, _ in items)), 1.0,
                "graphical abstract", tol=0)
    ax.set_xticks([xl, xr], list(GA_COLS))
    ax.tick_params(axis="x", length=0, labelsize=gpt(GA_LABEL_PX), pad=3)
    bg.text(3.5, 56.5, GA_NOTE, ha="left", va="top", fontsize=gpt(GA_LABEL_PX), fontweight="bold", color=TEXT)
    bg.text(3.5, 62.0, conv, ha="left", va="top", fontsize=gpt(GA_MIN_LABEL_PX), color=TEXT2)
    label_px = min(t.get_fontsize() for t in end_labels) / PX_PT
    src.L.check("ga:end labels at least 36 px", float(label_px >= GA_MIN_LABEL_PX), 1.0, f"end label size {label_px:.1f} px", tol=0)
    src.L.check("ga:title size px", GA_TITLE_PX, 44, "title", tol=0)
    src.L.check("ga:line width px", round(gpt(GA_LINE_PX) / PX_PT), 8, "series lines", tol=0)
    title_artist = [t for t in fig.findobj(lambda a: hasattr(a, "get_text")) if t.get_text() == GA_TITLE]
    if len(title_artist) != 1 or "\n" in GA_TITLE:
        raise AssertionError("the title must be exactly one line")
    fig.canvas.draw()
    tw = title_artist[0].get_window_extent().width
    src.L.check("ga:title fits one line within the canvas", float(tw < 0.95 * GA_PX[0]), 1.0, f"title width {tw:.0f} px", tol=0)
    src.L.check("ga:caveat is not drawn in the image", float(not [t for t in fig.findobj(lambda a: hasattr(a, "get_text"))
                                                              if "validated" in t.get_text()]), 1.0, "footer removed", tol=0)
    w_px, h_px = round(fig.get_figwidth() * 300), round(fig.get_figheight() * 300)
    src.L.check("ga:width px", w_px, GA_PX[0], "graphical abstract pixel width", tol=0)
    src.L.check("ga:height px", h_px, GA_PX[1], "graphical abstract pixel height", tol=0)
    src.L.check("ga:aspect ratio 2.50", w_px / h_px, 2.5, "graphical abstract", tol=1e-9)
    fig.canvas.draw()
    for t in fig.findobj(lambda a: hasattr(a, "get_text")):
        if t.get_text() in (GA_NOTE, conv):
            bb = t.get_window_extent()
            src.L.check(f"ga:text inside canvas {t.get_text()[:20]}", float(bb.x1 < 0.98 * GA_PX[0] and bb.y0 > 0), 1.0,
                        f"width {bb.width:.0f} px", tol=0)
    drawn = {t.get_text() for t in fig.findobj(lambda a: hasattr(a, "get_text"))}
    src.L.check("ga:oracle line drawn in the artwork", float(GA_NOTE in drawn), 1.0, GA_NOTE, tol=0)
    src.L.check("ga:self-pair convention drawn in the artwork", float(conv in drawn), 1.0, GA_CONV, tol=0)
    src.L.check("ga:column subtitles say pooled and within-drug", float(all(c in drawn for c in GA_COLS)
                and "pooled" in GA_COLS[0] and "within-drug" in GA_COLS[1]), 1.0, "column subtitles", tol=0)
    save(fig, out, "graphical_abstract", thick=None, min_pt=gpt(GA_MIN_LABEL_PX))
    return {"title": GA_TITLE, "note": GA_NOTE, "convention": conv, "columns": list(GA_COLS),
            "intervals": {f"{n} {t}": [c_["lo95"], c_["value"], c_["hi95"]] for n, t, c_ in ci_drawn},
            "prior_title": GA_PRIOR_TITLE, "footer": GA_FOOT, "old_title": GA_OLD_TITLE,
            "encoder_above_drugbank_on_semeval_labels": cross, "font": font,
            "font_is_arial_or_helvetica": font in GA_FONTS, "size_px": list(GA_PX),
            "size_px_by_role": {"title": GA_TITLE_PX, "end_labels": GA_LABEL_PX, "lines": GA_LINE_PX},
            "labels": label_text, "n_bold": len(items), "seeds": len(enc["seeds"]),
            "lines": {s_["label"]: {"left": (s_["left_excl"] if "left_excl" in s_ else s_["left"])["value"],
                                    "right": s_["right"]["value"]} for s_ in (enc, db)},
            "drugbank_semeval_excl": ex}


def enc_seeds(series):
    return series["bold"][0]["seeds"]


def fig1_panel(src, out):
    W, H = 58, 36
    fig = figure(W, H)
    bg = canvas(fig)
    ax = axes_mm(fig, 31, 6, 25, 20)
    spines(ax, left=False)
    rows = [("partner_frequency_prior", "Partner-frequency prior"), ("novel_drug_prior", "Novel-drug prior")]
    bl = {(r["set"], r["baseline"]): r for r in src.d.tables["baselines"]}
    table = {}
    yv = 0.0
    ys = []
    for cohort, setname, ctitle in (("novel", "Novel OOD", "Novel"), ("older", "Older OOD", "Older")):
        ys.append(("header", yv, ctitle))
        yv += 1
        for key, lab in rows:
            r = src.d.baseline(f"{cohort}_random_negatives", key)
            m = src.d.baseline(cohort, key)
            src.L.check("tables:baselines auroc", m["auroc"], bl[(setname, key)]["auroc"], f"{cohort} {key}")
            if (cohort, key) == ("older", "partner_frequency_prior"):
                src.L.check("fig1:Older partner-frequency prior under partner matching is 0.500", m["auroc"], 0.5,
                            "baselines.json older", tol=0)
            ax.annotate("", xy=(m["auroc"], yv), xytext=(r["auroc"], yv),
                        arrowprops=dict(arrowstyle="-|>,head_length=0.3,head_width=0.13", color=EXTERNAL, lw=0.6,
                                        shrinkA=2.6, shrinkB=2.6), zorder=2)
            ax.plot(r["auroc"], yv, "o", ms=MS, mfc=SURFACE, mec=SHORTCUT, mew=0.8, zorder=3)
            ax.plot(m["auroc"], yv, "o", ms=MS, mfc=EXTERNAL, mec=SURFACE, mew=0.6, zorder=3)
            table[f"{cohort} | {lab}"] = {"random": r["auroc"], "partner_matched": m["auroc"],
                                          "source": f"baselines.json {cohort}_random_negatives and {cohort}; partner matched checked against tables.json baselines"}
            ys.append(("row", yv, lab))
            yv += 1
    chance(ax, label_at=(0.51, -0.6), va="top")
    ax.set_ylim(yv - 0.4, -0.6)
    ax.set_yticks([])
    ax.set_xlim(0.4, 0.9)
    ax.set_xticks([0.4, 0.5, 0.6, 0.7, 0.8, 0.9], ["0.4", "", "0.6", "", "0.8", ""])
    ax.tick_params(axis="x", labelsize=SMALL)
    ax.grid(axis="x", color=GRID, lw=0.4, zorder=0)
    ax.set_xlabel("Pooled AUROC", fontsize=SMALL, labelpad=1)
    for kind, y, lab in ys:
        bg.text(2 if kind == "header" else 4, 6 + (y + 0.6) / (yv - 0.4 + 0.6) * 20, lab, ha="left", va="center",
                fontsize=SMALL, fontweight="bold" if kind == "header" else "normal", color=TEXT)
    bg.plot(3, 2.6, "o", ms=MS, mfc=SURFACE, mec=SHORTCUT, mew=0.8)
    bg.text(5, 2.6, "random negatives", ha="left", va="center", fontsize=SMALL, color=TEXT)
    bg.plot(28, 2.6, "o", ms=MS, mfc=EXTERNAL, mec=SURFACE, mew=0.6)
    bg.text(30, 2.6, "partner-matched", ha="left", va="center", fontsize=SMALL, color=TEXT)
    save(fig, out, "fig1_panel_d")
    return table


def tex_values(src, path):
    yrs = cohort_years(src)
    train = len(semeval.load_pairs("train"))
    chip, _ = example_pair(src)
    vals = {"TrainPairs": f"{train:,}", "NovelDrugs": str(yrs["novel_drugs"]), "NovelPairs": f"{yrs['novel_pairs']:,}",
            "OlderDrugs": str(yrs["older_drugs"]), "OlderPairs": f"{yrs['older_pairs']:,}",
            "NovelFrom": str(yrs["novel"][0]), "NovelTo": str(yrs["novel"][1]), "OlderFrom": str(yrs["older"][0]),
            "OlderTo": str(yrs["older"][1]), "ExampleChip": chip.replace(" + ", " $+$ "),
            "Seeds": str(seed_count(src, "b2mixed")),
            "OlderCleanDrugs": str(src.db_lookup["older_clean"]["n_drugs"]),
            "OlderPrimaryDrugs": str(src.cs["cells"]["older_primary:A"]["n_drugs"])}
    if src.e9 is not None:
        pnl = src.e9["e9"]["panel"]["older_primary"]
        backbones = {n.split("-")[2] for n in pnl["names"]}
        src.L.check("e9:n_models", len(pnl["names"]), pnl["n_models"], "panel size", tol=0)
        vals.update({"PanelModels": str(pnl["n_models"]), "PanelBackbones": str(len(backbones))})
    lines = [f"\\newcommand{{\\val{k}}}{{{v.replace(',', '{,}')}}}" for k, v in vals.items()]
    for line in lines:
        lint_text(line, "pipeline values")
    Path(path).write_text("\n".join(lines) + "\n")
    return vals


def compile_pipeline(tex_dir, out):
    tex_dir = Path(tex_dir)
    exe = shutil.which("pdflatex")
    if exe is None:
        print("pdflatex not found; fig1_study_design not compiled")
        return None
    with tempfile.TemporaryDirectory() as tmp:
        for f in ("pipeline.tex", "pipeline_values.tex", "fig1_panel_d.pdf"):
            shutil.copy(tex_dir / f, Path(tmp) / f)
        env = {"SOURCE_DATE_EPOCH": "0", "FORCE_SOURCE_DATE": "1", "PATH": str(Path(exe).parent) + ":/usr/bin:/bin"}
        r = subprocess.run([exe, "-interaction=nonstopmode", "-halt-on-error", "pipeline.tex"], cwd=tmp, env=env,
                           capture_output=True, text=True)
        if r.returncode != 0:
            raise RuntimeError("pipeline.tex failed to compile:\n" + r.stdout[-3000:])
        pdf = Path(tmp) / "pipeline.pdf"
        shutil.copy(pdf, tex_dir / "pipeline.pdf")
        shutil.copy(pdf, Path(out) / "fig1_study_design.pdf")
        ppm = shutil.which("pdftoppm")
        if ppm:
            subprocess.run([ppm, "-r", "300", "-png", "-singlefile", str(pdf), str(Path(tmp) / "pipeline")], check=True)
            shutil.copy(Path(tmp) / "pipeline.png", tex_dir / "pipeline.png")
            shutil.copy(Path(tmp) / "pipeline.png", Path(out) / "fig1_study_design.png")
    return Path(out) / "fig1_study_design.pdf"


def jsonable(o):
    return pf.jsonable(o)


def run(a):
    family = style()
    src = Sources(a)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    data = {"font": family, "boot": a.boot, "status": AMEND7_NOTE, "margin": list(MARGIN)}
    data["fig1_panel_d"] = fig1_panel(src, out)
    tex_dir = Path(a.tex_dir)
    tex_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy(out / "fig1_panel_d.pdf", tex_dir / "fig1_panel_d.pdf")
    data["fig1_values"] = tex_values(src, tex_dir / "pipeline_values.tex")
    shutil.copy(tex_dir / "pipeline_values.tex", out / "pipeline_values.tex")
    hero, series, bars = fig_hero(src, out)
    data["fig2_dissociation"] = hero
    data["fig3_encoders"] = fig_encoders(src, out)
    data["fig4_sentence_signal"] = fig_sentence(src, out)
    data["fig5_positive_controls"], rows5 = fig_controls(src, out)
    data["figS_amend7_detail"] = fig_amend7_detail(src, out, rows5)
    data["fig6_model_panel"] = fig_panel(src, out)
    data["graphical_abstract"] = fig_ga(src, out, series)
    data["ood_cohorts"] = {k: list(v) for k, v in OOD_COHORTS.items()}
    data["band_audit"] = dict(pf.AUDIT)
    data["commitment8"] = C8
    data["roles"] = ROLE_LABEL
    if a.compile:
        compile_pipeline(tex_dir, out)
    data["checks"] = src.L.counts
    data["checks_paperfigs_cells"] = src.d.checks
    data["ledger"] = src.L.items
    (out / "figure_data_main.json").write_text(json.dumps(jsonable(data), indent=1))
    caps = captions(data)
    if a.figures_md:
        write_md(Path(a.figures_md), caps)
    missing = [f for f in FIGURES for ext in ("pdf", "png") if not (out / f"{f}.{ext}").exists()]
    if missing:
        raise SystemExit(f"missing figures: {missing}")
    print(json.dumps({"font": family, "figures": len(FIGURES), "checks": sum(v for k, v in src.L.counts.items() if k != "read"),
                      "read": src.L.counts.get("read", 0)}))
    return data


def captions(D):
    from .captions import build
    return build(D)


def write_md(path, caps):
    text = path.read_text() if path.exists() else ""
    marker = "\n## Supplement"
    tail = text[text.index(marker):] if marker in text else ""
    body = caps.rstrip() + "\n" + tail
    lint_text(body, str(path))
    path.write_text(body)


def main(argv=None):
    ap = argparse.ArgumentParser()
    R = config.RESULTS / "revision"
    ap.add_argument("--preds", default=str(R / "preds"))
    ap.add_argument("--a7preds", default=str(config.ROOT / "runs" / "preds"))
    ap.add_argument("--eval", default=str(R / "eval"))
    ap.add_argument("--amend7", default=str(R / "amend7"))
    ap.add_argument("--post7", default=str(R / "post7"))
    ap.add_argument("--sensitivity", default=str(R / "sensitivity"))
    ap.add_argument("--post8", default=str(R / "post8"))
    ap.add_argument("--baselines", default=str(config.RESULTS / "corrected" / "baselines.json"))
    ap.add_argument("--corrected", default=str(config.RESULTS / "corrected"))
    ap.add_argument("--rev2", default=str(R / "rev2_colab"))
    ap.add_argument("--rev2-base", default=str(R / "rev2"))
    ap.add_argument("--rev3", default=str(R / "rev3"))
    ap.add_argument("--out", default=str(R / "figures"))
    ap.add_argument("--tex-dir", default=str(config.ROOT / "paper" / "figures"))
    ap.add_argument("--figures-md", default=str(R / "figures" / "FIGURES.md"))
    ap.add_argument("--boot", type=int, default=1000)
    ap.add_argument("--final", action="store_true")
    ap.add_argument("--compile", action="store_true")
    return run(ap.parse_args(argv))


if __name__ == "__main__":
    main()
