import csv
import re

import numpy as np

from . import config
from .openfda import LabelStore, section_text
from .ood import NON_DI_SECTIONS, label_text
from .textnorm import mentions
from .vocab import surface_forms

CYP3A_PERPETRATORS = [
    "ketoconazole", "itraconazole", "clarithromycin", "ritonavir", "voriconazole", "posaconazole",
    "rifampin", "carbamazepine", "phenytoin", "apalutamide", "enzalutamide", "mitotane", "st johns wort",
]
CYP3A_ALIASES = {"st johns wort": ["st johns wort", "st. john's wort", "st john's wort", "hypericum"],
                 "rifampin": ["rifampin", "rifampicin"]}


def _novel_label(store, name):
    label = store.get(name, fields=("openfda.generic_name", "openfda.substance_name"))
    if label is None:
        base = re.sub(r"-[a-z]{4}$", "", name)
        if base != name:
            label = store.get(base, fields=("openfda.generic_name", "openfda.substance_name"))
    return label


def non_di_text(label):
    parts = []
    for k, v in (label or {}).items():
        if k.startswith("drug_interactions") or k in ("openfda", "id", "set_id", "version", "effective_time"):
            continue
        if isinstance(v, list):
            parts.extend(x for x in v if isinstance(x, str))
        elif isinstance(v, str):
            parts.append(v)
    return " ".join(parts).lower()


def read_pairs(path):
    with open(path) as f:
        return list(csv.DictReader(f))


class Context:
    def __init__(self, lookup, store=None):
        self.lookup = lookup
        self.store = store or LabelStore(offline=True)
        forms = surface_forms(lookup)
        self.partner_forms = {}
        for f, k in forms.items():
            self.partner_forms.setdefault(k, []).append(f)
        seen, self.vocab_di, self.vocab_n = set(), {}, 0
        for k in sorted(lookup):
            cui = lookup[k]["rxcui"]
            if cui in seen:
                continue
            label = self.store.get(lookup[k]["normalized"])
            if not label:
                continue
            seen.add(cui)
            di = section_text(label, config.HOLDOUT_SECTION).lower()
            if di:
                self.vocab_di[k] = (cui, di)
        self.vocab_n = len(self.vocab_di)
        self._partner_cache = {}
        self._novel_cache = {}

    def named(self, key, text):
        return any(f in text and mentions(f, text) for f in self.partner_forms.get(key, [key]))

    def partner_prior(self, key):
        if key not in self._partner_cache:
            cui = self.lookup[key]["rxcui"]
            hits = tot = 0
            for _, (c, di) in self.vocab_di.items():
                if c == cui:
                    continue
                tot += 1
                hits += self.named(key, di)
            self._partner_cache[key] = hits / tot if tot else 0.0
        return self._partner_cache[key]

    def novel(self, drug):
        if drug not in self._novel_cache:
            text = non_di_text(_novel_label(self.store, drug))
            n = sum(self.named(k, text) for k in self.vocab_di) if text else 0
            self._novel_cache[drug] = (text, n / max(1, self.vocab_n))
        return self._novel_cache[drug]


def cyp_partner(partner):
    for p in CYP3A_PERPETRATORS:
        names = CYP3A_ALIASES.get(p, [p])
        if partner in names:
            return True
    return False


def drugbank_scores(pairs, db_rows):
    idx = {(r["ood_drug"], r["semeval_drug"]): r["drugbank_label"] for r in db_rows}
    return np.array([1.0 if idx.get((p["ood_drug"], p["semeval_drug"])) == "positive" else 0.0 for p in pairs])


def score_all(pairs, ctx, db_rows=None):
    out = {}
    n = len(pairs)
    out["all_positive"] = np.ones(n)
    out["partner_frequency_prior"] = np.array([ctx.partner_prior(p["semeval_drug"]) for p in pairs])
    out["novel_drug_prior"] = np.array([ctx.novel(p["ood_drug"])[1] for p in pairs])
    out["non_di_label_string_match"] = np.array(
        [float(ctx.named(p["semeval_drug"], ctx.novel(p["ood_drug"])[0])) for p in pairs])
    out["cyp3a_keyword_rule"] = np.array(
        [float("cyp3a" in ctx.novel(p["ood_drug"])[0] and cyp_partner(p["semeval_drug"])) for p in pairs])
    if db_rows is not None:
        out["drugbank_lookup_reference"] = drugbank_scores(pairs, db_rows)
    return out


def binarize(name, score):
    if name in ("all_positive", "non_di_label_string_match", "cyp3a_keyword_rule", "drugbank_lookup_reference"):
        return (score >= 0.5).astype(int)
    return (score > np.mean(score)).astype(int)
