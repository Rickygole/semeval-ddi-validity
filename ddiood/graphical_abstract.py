import textwrap

from . import paperfigs as pf

W, H = 130, 52
MONO = ["Latin Modern Mono", "DejaVu Sans Mono"]
CARD = "#f5f4f1"
HEADLINE = "DDI classifiers trained on SemEval classify sentences, not drug pairs"


def novel_example(truth):
    for p in truth.sets["ood"]["pairs"]:
        if p["y"] == 1:
            return f"{p['drug_a']} ; {p['drug_b']}"
    raise ValueError("no positive novel pair")


def wrap(text, width=33):
    return "\n".join(textwrap.wrap(text, width))


def render(data, out):
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyBboxPatch
    ex = pf.examples()
    third = novel_example(data.truth)
    fig = plt.figure(figsize=(W * pf.MM, H * pf.MM))
    bg = fig.add_axes([0, 0, 1, 1])
    bg.set_xlim(0, W)
    bg.set_ylim(H, 0)
    bg.axis("off")
    bg.text(W / 2, 4.6, HEADLINE, ha="center", va="center", fontsize=9.5, fontweight="bold", color=pf.INK)

    cards = [("sentence", wrap(ex["sentence"])), ("names to pseudo-words", wrap(ex["pseudo"])),
             ("unseen drug, names only", third)]
    x0, cw, ch, gap, y0 = 1.5, 50.0, 10.6, 1.4, 11.0
    for i, (tag, body) in enumerate(cards):
        y = y0 + i * (ch + gap)
        bg.add_patch(FancyBboxPatch((x0, y), cw, ch, boxstyle="round,pad=0,rounding_size=1.2", fc=CARD,
                                    ec=pf.INK2, lw=0.5))
        bg.text(x0 + 1.8, y + 2.1, tag, ha="left", va="center", fontsize=pf.SMALL, color=pf.INK2)
        bg.text(x0 + 1.8, y + 4.0, body, ha="left", va="top", fontsize=pf.SMALL, family=MONO, color=pf.INK,
                linespacing=1.2)

    ay = y0 + 1.5 * ch + gap
    bg.annotate("", xy=(66.0, ay + 1.5), xytext=(53.0, ay + 1.5),
                arrowprops=dict(arrowstyle="-|>,head_length=0.35,head_width=0.14", color=pf.INK2, lw=0.6,
                                shrinkA=0, shrinkB=0))
    bg.text(58.8, ay - 0.6, "SemEval-\ntrained\nBiomedBERT", ha="center", va="bottom", fontsize=pf.SMALL,
            color=pf.INK2, linespacing=1.2)

    ax_l, ax_r, ax_t, ax_b = 84.0, 116.0, 17.0, 36.5
    ax = fig.add_axes([ax_l / W, 1 - ax_b / H, (ax_r - ax_l) / W, (ax_b - ax_t) / H])
    pf.band(ax)
    rows = [("Annotated\nsentence", "test_sentence"), ("Pseudo-word\nswap", "swap_pseudo_sentence"),
            ("Novel drugs,\nnames only", "ood_empty")]
    table = {}
    g = data.gk("b2mixed")
    for i, (label, key) in enumerate(rows):
        c = data.cell(g, key)
        table[label.replace("\n", " ")] = c
        pf.whisker(ax, i, c, pf.COLOR["b2mixed"], pf.MARK["b2mixed"])
        pf.value_label(ax, c, i, dx=0.035)
        bg.text(ax_l - 2.0, ax_t + (ax_b - ax_t) * (i + 0.62) / 3.05, label, ha="right", va="center",
                fontsize=pf.SMALL, color=pf.INK)
    ax.set_ylim(2.55, -0.62)
    ax.set_xlim(0.3, 1.1)
    ax.set_xticks([0.4, 0.6, 0.8, 1.0])
    ax.tick_params(axis="x", labelsize=pf.SMALL, length=2)
    ax.set_xlabel("AUROC", fontsize=pf.SMALL, labelpad=1)
    ax.spines["left"].set_visible(False)
    ax.set_yticks([])
    ax.grid(axis="x", color=pf.GRID, lw=0.5, zorder=0)
    ax.text(0.5, -0.66, "no-signal margin", ha="center", va="bottom", fontsize=pf.SMALL, color=pf.INK2)
    ax.set_xlim(0.3, 1.12)
    note = f"{len(data.seeds(g))} seeds averaged"
    bg.text(ax_r, ax_b + 7.2, note, ha="right", va="top", fontsize=pf.SMALL, color=pf.INK2)
    pf.bracket(ax, -0.4, 1.4, "reads the\nsentence,\nnot the\ndrugs", 1.04, tick=0.012)

    rnd = data.baseline("novel_random_negatives", "partner_frequency_prior")["auroc"]
    mat = data.baseline("novel", "partner_frequency_prior")["auroc"]
    strip = f"Partner-frequency prior, Novel cohort: AUROC {rnd:.2f} (random negatives) vs {mat:.2f} (partner-matched)"
    bg.plot([2, W - 2], [46.6, 46.6], color=pf.GRID, lw=0.6)
    bg.text(W / 2, 49.4, strip, ha="center", va="center", fontsize=pf.SMALL, color=pf.INK2)
    pf.save(fig, out, "graphical_abstract")
    return {"rows": table, "partner_prior_random": rnd, "partner_prior_matched": mat, "third_card": third,
            "seed_note": note}
