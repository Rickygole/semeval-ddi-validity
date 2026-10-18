import hashlib
import re

from . import config
from .index import passages_for


def names(a, b):
    return f"{a} [SEP] {b}"


def b1(pairs):
    return [names(p["drug_a"], p["drug_b"]) for p in pairs]


def b2_sentence(pairs):
    return [(p["sentence"], names(p["drug_a"], p["drug_b"])) for p in pairs]


def b2_names(pairs):
    return b1(pairs)


MASK = "@DRUG$"


def mask_names(text, names, token=MASK):
    for n in sorted({n for n in names if n}, key=len, reverse=True):
        text = re.sub(r"(?<![\w-])" + re.escape(n) + r"(?![\w-])", lambda m: token, text, flags=re.IGNORECASE)
    return text


def krag(pairs, cache, chars=config.PASSAGE_CHARS, k=config.TOP_K, mask=False):
    out = []
    for p in pairs:
        ps = passages_for(cache, p["drug_a"], p["drug_b"])[:k]
        if mask:
            ps = [mask_names(x, [p["drug_a"], p["drug_b"]]) for x in ps]
        if not ps:
            out.append(names(p["drug_a"], p["drug_b"]))
        else:
            ev = " [SEP] ".join(x[:chars] for x in ps)
            out.append(f"{p['drug_a']} [SEP] {p['drug_b']} [SEP] {ev}")
    return out


def ood_as_pairs(rows):
    out = []
    for r in rows:
        lab = r["label"]
        y = int(lab) if str(lab).isdigit() else (0 if lab == "no_interaction_silver" else 1)
        out.append({"drug_a": r["ood_drug"], "drug_b": r["semeval_drug"], "y": y,
                    "sentence": r.get("cooccurrence_sentence", ""), "group": r["ood_drug"]})
    return out


def pairs_hash(pairs):
    key = "\n".join(f"{p['drug_a']}|||{p['drug_b']}|||{p['y']}" for p in pairs)
    return hashlib.sha256(key.encode()).hexdigest()


def masked_sentence(p):
    return mask_names(p["sentence"], [p["drug_a"], p["drug_b"]])


def b2_masked(pairs):
    return [(masked_sentence(p), names(MASK, MASK)) for p in pairs]


def b2_empty(pairs):
    return [("", names(p["drug_a"], p["drug_b"])) for p in pairs]


def swapped(p, a, b):
    table = {p["drug_a"].lower(): a, p["drug_b"].lower(): b}
    pat = "|".join(re.escape(k) for k in sorted(table, key=len, reverse=True))
    s = re.sub(r"(?<![\w-])(" + pat + r")(?![\w-])", lambda m: table[m.group(1).lower()], p["sentence"],
               flags=re.IGNORECASE)
    return {**p, "sentence": s, "drug_a": a, "drug_b": b}


def pseudo_word(rng, n=9):
    cons, vow = "bcdfghjklmnprstvz", "aeiou"
    return "".join(rng.choice(cons if i % 2 == 0 else vow) for i in range(n)) + "ib"


def mixed_training(pairs):
    texts, labels = [], []
    for p in pairs:
        for t in (b2_sentence([p])[0], b2_empty([p])[0]):
            texts.append(t)
            labels.append(p["label_id"])
    return texts, labels
