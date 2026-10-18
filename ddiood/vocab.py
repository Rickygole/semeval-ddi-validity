from collections import Counter, defaultdict

from . import semeval
from .textnorm import GENERIC_TERMS, REJECT_TERMS, canonicalize, normalize


def build_lookup(rx, corpus=None):
    raw, type_counts = semeval.load_entities("train", corpus)
    names = sorted({normalize(n) for n in raw if normalize(n)})
    removed = Counter(n for n in names if n in REJECT_TERMS)
    names = [n for n in names if n not in REJECT_TERMS]
    lookup, audit = {}, []
    if hasattr(rx, "prefetch"):
        rx.prefetch(names + [canonicalize(n) for n in names])
    for name in names:
        canon = canonicalize(name)
        hit, form = rx(name), "normalized"
        if hit["rxcui"] is None and canon and canon != name:
            hit, form = rx(canon), "canonicalized"
        audit.append({"normalized": name, "canonicalized": canon, "rxcui": hit["rxcui"],
                      "tty": hit["tty"], "matched_form": form if hit["rxcui"] else "", "status": hit["status"]})
        if hit["rxcui"] and len(name) >= 2:
            lookup.setdefault(name, {"normalized": name, "canonicalized": canon,
                                     "rxcui": hit["rxcui"], "tty": hit["tty"], "matched_form": form})
    rx.flush()
    by_cui = defaultdict(list)
    for k, v in lookup.items():
        by_cui[v["rxcui"]].append(k)
    conflicts = [[cui, *sorted(ks)] for cui, ks in sorted(by_cui.items()) if len(ks) > 1]
    counts = {
        "raw_entities": len(raw),
        "unique_normalized": len(names) + sum(removed.values()),
        "reject_removed": dict(removed),
        "rxnorm_pass": len(lookup),
        "rxnorm_fail": sum(1 for a in audit if not a["rxcui"]),
        "type_counts": type_counts,
    }
    return lookup, audit, conflicts, counts


def surface_forms(lookup, min_len=4):
    forms = {}
    for key, v in lookup.items():
        cands = {key, v["normalized"]}
        if v.get("matched_form") == "canonicalized":
            cands.add(v["canonicalized"])
        for f in cands:
            if f and len(f) >= min_len and f not in GENERIC_TERMS:
                forms.setdefault(f, key)
    return forms


def harmonize(name, lookup, forms=None):
    forms = forms or surface_forms(lookup, min_len=1)
    n = normalize(name)
    if n in forms:
        return forms[n]
    c = canonicalize(n)
    return forms.get(c)
