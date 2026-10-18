import csv
import hashlib
import random
import re
from pathlib import Path
from collections import Counter, defaultdict

from . import config
from .openfda import section_text
from .textnorm import (ANCHOR_TOKENS, canonicalize, guardrail_excluded, has_risk_signal, mentions,
                       normalize, split_sentences)
from .vocab import surface_forms

NON_DI_SECTIONS = config.INDEX_SECTIONS + ["indications_and_usage", "boxed_warning", "warnings",
                                           "precautions", "contraindications", "adverse_reactions"]


def moieties(field):
    parts = re.split(r";|,|/|\band\b", re.sub(r"\([^)]*\)", " ", field.lower()))
    return [canonicalize(p) for p in parts if canonicalize(p)]


def novel_drugs(nme_csv, excluded_names, min_year=config.OOD_MIN_YEAR, prior_csv=None):
    first = {}
    if prior_csv and Path(prior_csv).exists():
        with open(prior_csv) as f:
            for row in csv.DictReader(f):
                first[row["moiety"]] = (int(row["first_us_approval_year"]), row["product"], "")
    with open(nme_csv, encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            year = int(re.sub(r"\D", "", row.get("Approval Year", "")) or 0)
            if not year:
                continue
            for m in moieties(row.get("Active Ingredient/Moiety", "")):
                if m not in first or year < first[m][0]:
                    first[m] = (year, row.get("Proprietary  Name", "").strip(), row.get("FDA Approval Date", ""))
    drugs, rejected = [], Counter()
    for name, (year, brand, date) in sorted(first.items()):
        if year < min_year:
            continue
        if name in excluded_names or normalize(name) in excluded_names:
            rejected["in_semeval_vocabulary"] += 1
            continue
        drugs.append({"drug": name, "first_approval_year": year, "brand": brand, "approval_date": date})
    return drugs, dict(rejected)


def _window(sentences, i):
    return " ".join(sentences[max(0, i - 1):i + 2]).lower()


def _first_anchor(text_lower):
    for a in ANCHOR_TOKENS:
        if a in text_lower:
            return a
    return None


def mention_index(text, forms):
    lower = text.lower()
    found = {}
    for form, key in forms.items():
        if form in lower and mentions(form, lower):
            found.setdefault(key, form)
    return found


NULL_EFFECT = re.compile(
    r"no clinically (significant|relevant|meaningful)|not clinically (significant|relevant)|not impacted|"
    r"no (significant |meaningful |relevant )?effect|no dose adjustment|no dosage adjustment|did not (affect|alter|change)|"
    r"no (significant |clinically significant )?(change|difference)|\u2194", re.IGNORECASE)


def label_text(label):
    parts = []
    for v in (label or {}).values():
        if isinstance(v, list):
            parts.extend(x for x in v if isinstance(x, str))
        elif isinstance(v, str):
            parts.append(v)
    return " ".join(parts)


def label_ingredients(label):
    o = (label or {}).get("openfda") or {}
    names = o.get("substance_name") or o.get("generic_name") or []
    out = set()
    for n in names:
        out.update(m for m in moieties(n))
    return out


def label_identity(label, drug):
    ings = label_ingredients(label)
    base = re.sub(r"-[a-z]{4}$", "", drug)
    matches = any(base in i or i in base for i in ings) if ings else False
    if not ings:
        return "no_openfda_ingredients"
    if not matches:
        return "label_is_for_another_moiety"
    if len(ings) > 1:
        return "combination_product_label"
    return None


def build_pairs(novel, store, lookup, label_available, seed=config.PRIMARY_SEED,
                ratio=config.NEGATIVE_RATIO, max_pos_per_drug=10, negatives="partner"):
    forms = surface_forms(lookup)
    cui = {k: v["rxcui"] for k, v in lookup.items()}
    pairs, report, info = [], {}, {}
    eligible = {k for k in lookup if label_available.get(k) and len(k) >= 4 and k in set(forms.values())}
    pool = sorted(eligible)
    for d in novel:
        drug = d["drug"]
        label = store.get(drug, fields=("openfda.generic_name", "openfda.substance_name"))
        rec = {"drug": drug, "first_approval_year": d["first_approval_year"], "label_found": bool(label)}
        report[drug] = rec
        if not label:
            continue
        bad = label_identity(label, drug)
        rec["label_ingredients"] = sorted(label_ingredients(label))
        if bad:
            rec["excluded"] = bad
            continue
        di = section_text(label, config.HOLDOUT_SECTION)
        rec["di_section"] = bool(di)
        if not di:
            continue
        di_lower = di.lower()
        sentences = split_sentences(di)
        mentioned = mention_index(label_text(label), forms)
        mentioned_cuis = {cui[k] for k in mentioned}
        candidates = {k: f for k, f in mention_index(di, forms).items()
                      if f not in drug and drug not in f and k in eligible}
        rec["candidates"] = len(candidates)
        if not candidates and has_risk_signal(di_lower):
            rec["excluded"] = "risk_signal_without_semeval_match"
            continue
        seen_cui, positives, nulls = set(), [], 0
        for key, form in sorted(candidates.items()):
            if cui[key] in seen_cui:
                continue
            hit = None
            for i, s in enumerate(sentences):
                if mentions(form, s.lower()):
                    if NULL_EFFECT.search(s):
                        nulls += 1
                        continue
                    anchor = _first_anchor(_window(sentences, i))
                    if anchor:
                        hit = (anchor, s)
                        break
            if hit:
                seen_cui.add(cui[key])
                positives.append((key, hit))
        rec["null_effect_sentences_skipped"] = nulls
        rec["after_anchor"] = len(positives)
        rng = random.Random(f"{seed}:{drug}")
        if max_pos_per_drug and len(positives) > max_pos_per_drug:
            positives = sorted(rng.sample(positives, max_pos_per_drug))
        rec["positives"] = len(positives)
        if not positives:
            continue
        cooc = _cooccurrence(label, drug, forms)
        info[drug] = {"mentioned": set(mentioned), "cuis": mentioned_cuis, "di": di_lower, "cooc": cooc,
                      "year": d["first_approval_year"]}
        for key, (anchor, sent) in positives:
            pairs.append({"ood_drug": drug, "semeval_drug": key, "label": 1, "anchor": anchor,
                          "evidence": sent, "cooccurrence_sentence": cooc.get(key, ""),
                          "first_approval_year": d["first_approval_year"]})
        if negatives == "partner":
            continue
        neg_pool = [k for k in pool if k not in mentioned and cui[k] not in mentioned_cuis
                    and not guardrail_excluded(k, di_lower)]
        used, negs = set(), []
        for k in rng.sample(neg_pool, len(neg_pool)):
            if cui[k] in used:
                continue
            used.add(cui[k])
            negs.append(k)
            if len(negs) == ratio * len(positives):
                break
        rec["negatives"] = len(negs)
        rec["guardrail_excluded"] = sum(1 for k in pool if guardrail_excluded(k, di_lower))
        for key in negs:
            pairs.append({"ood_drug": drug, "semeval_drug": key, "label": 0, "anchor": "", "evidence": "",
                          "cooccurrence_sentence": cooc.get(key, ""),
                          "first_approval_year": d["first_approval_year"]})
    if negatives == "partner":
        pairs += partner_matched_negatives(pairs, info, cui, seed, ratio, report)
    return pairs, report


def partner_matched_negatives(positives, info, cui, seed, ratio, report):
    drugs = sorted(info)
    taken, out = set(), []
    for p in positives:
        x = p["semeval_drug"]
        ok = [d for d in drugs if d != p["ood_drug"] and x not in info[d]["mentioned"]
              and cui[x] not in info[d]["cuis"] and not guardrail_excluded(x, info[d]["di"])
              and (d, x) not in taken]
        rng = random.Random(f"{seed}:{p['ood_drug']}:{x}")
        for d in rng.sample(ok, min(ratio, len(ok))):
            taken.add((d, x))
            out.append({"ood_drug": d, "semeval_drug": x, "label": 0, "anchor": "", "evidence": "",
                        "cooccurrence_sentence": info[d]["cooc"].get(x, ""), "first_approval_year": info[d]["year"]})
            report[d]["negatives"] = report[d].get("negatives", 0) + 1
    return out


def _cooccurrence(label, drug, forms):
    out = {}
    for section in NON_DI_SECTIONS:
        for s in split_sentences(section_text(label, section)):
            low = s.lower()
            if drug not in low:
                continue
            for key in mention_index(s, forms):
                out.setdefault(key, s)
    return out


def summarize(pairs):
    by = defaultdict(Counter)
    for p in pairs:
        by[p["ood_drug"]][p["label"]] += 1
    return {
        "n_pairs": len(pairs),
        "n_pos": sum(p["label"] == 1 for p in pairs),
        "n_neg": sum(p["label"] == 0 for p in pairs),
        "n_ood_drugs": len(by),
        "max_pairs_per_drug": max((sum(c.values()) for c in by.values()), default=0),
        "years": dict(Counter(p["first_approval_year"] for p in pairs if p["label"] == 1)),
        "b2_applicable": sum(bool(p["cooccurrence_sentence"]) for p in pairs),
    }


DASHES = "[" + "".join(map(chr, (0x2012, 0x2013, 0x2014, 0x2015))) + "]"


def _clean(v):
    return re.sub(DASHES, "-", v) if isinstance(v, str) else v


def write_csv(pairs, path):
    pairs = [{k: _clean(v) for k, v in p.items()} for p in pairs]
    fields = ["ood_drug", "semeval_drug", "label", "anchor", "evidence", "cooccurrence_sentence", "first_approval_year"]
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(pairs)
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def rebuild_submitted_600(ood_pairs_rows, strict_common):
    keep = {(p["ood_drug"], p["semeval_drug"]) for p in strict_common}
    pos = [p for p in ood_pairs_rows if p["label"] == "interaction"
           and (p["ood_drug"], p["semeval_drug"]) in keep
           and p["ood_drug"] != p["semeval_drug"] and p["semeval_drug"].strip() != ""]
    neg_pool = [p for p in ood_pairs_rows if p["label"] == "no_interaction_silver"]
    random.seed(42)
    neg = random.sample(neg_pool, min(len(pos) * 2, len(neg_pool)))
    return pos + neg
