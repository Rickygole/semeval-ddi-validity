import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

from . import config
from .ood import build_pairs, label_identity, label_ingredients, label_text, mention_index, moieties
from .pipeline import _novel_label
from .openfda import LabelStore, section_text
from .textnorm import canonicalize, normalize
from .vocab import surface_forms

MAX_POS_PER_DRUG = 10
SEED = config.PRIMARY_SEED
SUFFIX = re.compile(r"-[a-z]{4}$")


def read_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _tokens(name):
    return normalize(SUFFIX.sub("", normalize(name))).split()


def _contains(big, small):
    n = len(small)
    return n > 0 and any(big[i:i + n] == small for i in range(len(big) - n + 1))


def ood_name_set(ood_rows, old_rows):
    return sorted({r["ood_drug"] for r in ood_rows} | {r["ood_drug"] for r in old_rows})


SALT_WORDS = {
    "hydrochloride", "hcl", "sodium", "disodium", "potassium", "calcium", "magnesium", "acetate", "succinate", "tartrate",
    "phosphate", "mesylate", "fumarate", "maleate", "besylate", "tosylate", "hydrate", "monohydrate", "dihydrate",
    "hemihydrate", "sesquihydrate", "sulfate", "bisulfate", "hydrobromide", "bromide", "chloride", "nitrate", "lactate",
    "oxalate", "citrate", "benzoate", "erbumine", "dimeglumine", "meglumine", "xinafoate", "dipropionate", "valerate",
    "propionate", "butyrate", "pamoate", "stearate", "gluconate", "carbonate", "oxide", "hydroxide", "trihydrate"}
CORE_MIN = 6


def core(name):
    toks = [t for t in _tokens(name) if t not in SALT_WORDS and not t.isdigit()]
    return "".join(toks)


def core_match(a, b):
    ca, cb = core(a), core(b)
    return min(len(ca), len(cb)) >= CORE_MIN and (ca in cb or cb in ca)


def equivalent_ood(strings, ood_names):
    hits = set()
    for n in ood_names:
        nn, cn = normalize(n), canonicalize(n)
        nt = _tokens(n)
        for x in strings:
            xt = _tokens(x)
            if x in (nn, cn) or canonicalize(x) in (nn, cn):
                hits.add(n)
            elif min(len(x), len(n)) >= 5 and xt and (_contains(nt, xt) or _contains(xt, nt)):
                hits.add(n)
            elif core_match(x, n):
                hits.add(n)
    return hits


def excluded_vocab(lookup, ood_names, ingredients=None):
    ingredients = ingredients or {}
    reasons, matches = {}, {}
    ood_norm = {normalize(n) for n in ood_names} | {canonicalize(n) for n in ood_names}
    ood_cui = {lookup[k]["rxcui"] for k in lookup if k in ood_norm or lookup[k]["canonicalized"] in ood_norm}
    for k, v in lookup.items():
        strings = {k, v["normalized"], v["canonicalized"]} | set(ingredients.get(k, ()))
        hit = equivalent_ood(strings, ood_names)
        if hit:
            reasons[k] = "equivalent_to_ood:" + ";".join(sorted(hit))
            matches[k] = sorted(hit)
        elif v["rxcui"] in ood_cui:
            reasons[k] = "same_rxcui"
    return reasons, matches


def ood_ingredients(store, ood_names):
    out = set()
    for n in ood_names:
        out.update(moieties(n))
        out.add(normalize(SUFFIX.sub("", normalize(n))))
        label = _novel_label(store, n)
        if label:
            out |= label_ingredients(label)
    return {x for x in out if x}


def vocab_ingredients(lookup, store, found):
    out = {}
    for k in lookup:
        if found.get(k):
            label = store.get(lookup[k]["normalized"])
            if label:
                out[k] = sorted(label_ingredients(label))
    return out


def unordered(a, b):
    return frozenset((normalize(a), normalize(b)))


def ood_pair_set(ood_rows, old_rows):
    out = set()
    for r in list(ood_rows) + list(old_rows):
        for a in {normalize(r["ood_drug"]), canonicalize(r["ood_drug"])}:
            for b in {normalize(r["semeval_drug"]), canonicalize(r["semeval_drug"])}:
                out.add(frozenset((a, b)))
    return out


def snapshot_dates(store, names):
    dates = Counter()
    missing = 0
    for n in names:
        p = store.path(n)
        if not p.exists():
            missing += 1
            continue
        dates[json.loads(p.read_text()).get("retrieved", "unknown")] += 1
    return {"files": sum(dates.values()), "missing": missing, "earliest": min(dates) if dates else None,
            "latest": max(dates) if dates else None, "by_date": dict(sorted(dates.items()))}


def build_training_pairs(lookup, vocab_label_found, ood_rows, old_rows, store=None):
    store = store or LabelStore(offline=True)
    names = ood_name_set(ood_rows, old_rows)
    ood_ings = ood_ingredients(store, names)
    vocab_ings = vocab_ingredients(lookup, store, vocab_label_found)
    ing_names = sorted(ood_ings | set(names))
    excl, matches = excluded_vocab(lookup, ing_names, vocab_ings)
    affected = sorted({n for hit in matches.values() for n in hit if n in names})
    ood_pairs = ood_pair_set(ood_rows, old_rows)

    class Store:
        def get(self, name, fields=None):
            return store.get(lookup[name]["normalized"])

    anchors, anchor_gate = [], Counter()
    for k in sorted(lookup):
        if vocab_label_found.get(k):
            label = store.get(lookup[k]["normalized"])
            if not section_text(label, config.HOLDOUT_SECTION):
                anchor_gate["no_di_section"] += 1
            elif k in excl:
                anchor_gate["excluded_ood_equivalent_or_ingredient_overlap"] += 1
            elif label_identity(label, k):
                anchor_gate["label_identity:" + label_identity(label, k)] += 1
            else:
                anchors.append({"drug": k, "first_approval_year": 0})
    raw, report = build_pairs(anchors, Store(), lookup, vocab_label_found, max_pos_per_drug=MAX_POS_PER_DRUG,
                              negatives="partner")
    counts = {"anchors_after_gates": len(anchors), "anchor_gate_rejections": dict(anchor_gate),
              "equivalent_vocab_drugs": len(excl), "built_pairs": len(raw),
              "built_positives": sum(p["label"] == 1 for p in raw),
              "built_negatives": sum(p["label"] == 0 for p in raw), "dropped": Counter()}
    forms = surface_forms(lookup)
    mention_cache = {}

    def mentions_of(x):
        if x not in mention_cache:
            lab = store.get(lookup[x]["normalized"])
            mention_cache[x] = set(mention_index(label_text(lab), forms)) if lab else set()
        return mention_cache[x]

    kept, seen = [], set()
    for p in raw:
        a, b, y = p["ood_drug"], p["semeval_drug"], int(p["label"])
        if a in excl or b in excl:
            counts["dropped"]["ood_drug_as_anchor_or_partner"] += 1
            if a in excl:
                counts["dropped"]["ood_drug_as_anchor"] += 1
            if b in excl:
                counts["dropped"]["ood_drug_as_partner"] += 1
            continue
        keys = {frozenset((x, z)) for x in {normalize(a), canonicalize(a), lookup[a]["normalized"]}
                for z in {normalize(b), canonicalize(b), lookup[b]["normalized"]}}
        if keys & ood_pairs:
            counts["dropped"]["unordered_pair_in_ood_set"] += 1
            continue
        if y == 0 and a in mentions_of(b):
            counts["dropped"]["negative_reverse_mention"] += 1
            continue
        u = (unordered(a, b), y)
        if u in seen:
            counts["dropped"]["duplicate_unordered_pair"] += 1
            continue
        seen.add(u)
        kept.append(p)
    pos = {unordered(p["ood_drug"], p["semeval_drug"]) for p in kept if int(p["label"]) == 1}
    final = []
    for p in kept:
        if int(p["label"]) == 0 and unordered(p["ood_drug"], p["semeval_drug"]) in pos:
            counts["dropped"]["negative_conflicts_with_positive"] += 1
            continue
        final.append(p)
    rows = [{"drug_a": p["ood_drug"], "drug_b": p["semeval_drug"], "y": int(p["label"]), "label_id": int(p["label"]),
             "anchor": p["anchor"], "evidence": p["evidence"], "cooccurrence_sentence": p["cooccurrence_sentence"],
             "sentence": p["cooccurrence_sentence"], "group": p["ood_drug"]} for p in final]
    counts["dropped"] = dict(counts["dropped"])
    counts.update({"final_pairs": len(rows), "final_positives": sum(r["y"] for r in rows),
                   "final_negatives": sum(1 - r["y"] for r in rows), "anchor_drugs": len({r["group"] for r in rows}),
                   "partner_drugs": len({r["drug_b"] for r in rows}), "excluded_vocab_drugs": len(excl)})
    audit = {"excluded_vocab": excl, "ood_drugs": len(names), "ood_drugs_with_equivalent_vocab_drug": affected,
             "equivalence_matches": matches}
    label_names = sorted({lookup[r["drug_a"]]["normalized"] for r in rows} | {lookup[r["drug_b"]]["normalized"] for r in rows})
    audit["snapshot_training_labels"] = snapshot_dates(store, label_names)
    audit["snapshot_ood_labels"] = snapshot_dates(store, names)
    return rows, counts, audit


def assert_no_leak(rows, lookup, ood_rows, old_rows, excl):
    ood_pairs = ood_pair_set(ood_rows, old_rows)
    for r in rows:
        if r["drug_a"] in excl or r["drug_b"] in excl:
            raise RuntimeError(f"OOD drug in training pair {r['drug_a']}|{r['drug_b']}")
        if frozenset((normalize(r["drug_a"]), normalize(r["drug_b"]))) in ood_pairs:
            raise RuntimeError(f"OOD pair in training set {r['drug_a']}|{r['drug_b']}")
    return True


def rows_hash(rows):
    key = "\n".join(f"{r['drug_a']}|||{r['drug_b']}|||{r['y']}" for r in rows)
    return hashlib.sha256(key.encode()).hexdigest()


FIELDS = ["drug_a", "drug_b", "y", "anchor", "evidence", "cooccurrence_sentence"]


def write_rows(rows, path):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def read_rows(path):
    out = []
    for r in read_csv(path):
        y = int(r["y"])
        out.append({"drug_a": r["drug_a"], "drug_b": r["drug_b"], "y": y, "label_id": y, "anchor": r["anchor"],
                    "evidence": r["evidence"], "cooccurrence_sentence": r["cooccurrence_sentence"],
                    "sentence": r["cooccurrence_sentence"], "group": r["drug_a"]})
    return out
