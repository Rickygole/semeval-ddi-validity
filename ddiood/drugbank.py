import re
import zipfile
import xml.etree.ElementTree as ET

NS = "{http://www.drugbank.ca}"


def _text(el, tag):
    t = el.find(NS + tag)
    return t.text.strip() if t is not None and t.text else ""


def _open(path):
    path = str(path)
    if path.endswith(".zip"):
        z = zipfile.ZipFile(path)
        return z.open([n for n in z.namelist() if n.endswith(".xml")][0])
    return open(path, "rb")


def load_interactions(path):
    table = {}
    with _open(path) as f:
        for _, el in ET.iterparse(f, events=("end",)):
            if el.tag != NS + "drug":
                continue
            if el.get("type") not in ("small molecule", "biotech"):
                el.clear()
                continue
            names = {_text(el, "name").lower()} - {""}
            syn = el.find(NS + "synonyms")
            if syn is not None:
                names |= {s.text.strip().lower() for s in syn.findall(NS + "synonym") if s.text}
            partners = set()
            di = el.find(NS + "drug-interactions")
            if di is not None:
                partners = {_text(x, "name").lower() for x in di.findall(NS + "drug-interaction")}
            for n in names:
                table.setdefault(n, set()).update(partners)
            el.clear()
    return table


def _norm(s):
    return re.sub(r"\s+", " ", s.lower().strip())


SALT_WORDS = ("hydrochloride", "dihydrochloride", "hcl", "hydrobromide", "bromide", "chloride", "bisulfate", "sulfate",
              "sulphate", "hydrogen sulfate", "mesylate", "mesilate", "dimesylate", "besylate", "besilate", "tosylate",
              "maleate", "malate", "tartrate", "bitartrate", "citrate", "acetate", "fumarate", "hemifumarate", "succinate",
              "phosphate", "diphosphate", "benzoate", "lactate", "gluconate", "oxalate", "nitrate", "mononitrate",
              "erbumine", "tromethamine", "meglumine", "dimeglumine", "xinafoate", "proxetil", "sodium", "disodium", "potassium", "calcium", "magnesium",
              "hyclate", "propionate", "dipropionate", "valerate", "monohydrate", "dihydrate", "trihydrate",
              "sesquihydrate", "hemihydrate", "hydrate", "anhydrous")
_SALT_RE = re.compile(r"\b(" + "|".join(sorted((re.escape(w) for w in SALT_WORDS), key=len, reverse=True)) + r")\b")


def strip_salt(name):
    out = _norm(_SALT_RE.sub(" ", _norm(name)))
    return out or _norm(name)


def resolve(name, table, lookup, strip_salts=False):
    forms = [_norm(name)]
    if name in lookup:
        forms += [_norm(lookup[name]["normalized"]), _norm(lookup[name]["canonicalized"])]
    for n in sorted(set(forms), key=forms.index):
        if n in table:
            return table[n]
    if strip_salts:
        for n in sorted({strip_salt(f) for f in forms} - set(forms)):
            if n in table:
                return table[n]
    return None


def _forms(name, lookup, strip_salts):
    out = {_norm(name)}
    if name in lookup:
        out |= {_norm(lookup[name]["normalized"]), _norm(lookup[name]["canonicalized"])}
    if strip_salts:
        out |= {strip_salt(n) for n in out}
    return out


def validate(pairs, table, lookup, strip_salts=False, one_sided="negative", detail=False):
    if one_sided not in ("negative", "unresolvable"):
        raise ValueError("one_sided must be 'negative' or 'unresolvable'")
    def forms(d):
        out = {_norm(d)}
        if d in lookup:
            out |= {_norm(lookup[d]["normalized"]), _norm(lookup[d]["canonicalized"])}
        return out
    rows = []
    for i, p in enumerate(pairs):
        if strip_salts:
            fa, fb = _forms(p["ood_drug"], lookup, True), _forms(p["semeval_drug"], lookup, True)
            ea, eb = resolve(p["ood_drug"], table, lookup, True), resolve(p["semeval_drug"], table, lookup, True)
        else:
            fa, fb = forms(p["ood_drug"]), forms(p["semeval_drug"])
            ea = next((table[n] for n in fa if n in table), None)
            eb = next((table[n] for n in fb if n in table), None)
        if ea is None and eb is None:
            db = "unresolvable"
        elif (ea and fb & ea) or (eb and fa & eb):
            db = "positive"
        elif one_sided == "unresolvable" and (ea is None or eb is None):
            db = "unresolvable"
        else:
            db = "negative"
        row = {"pair_id": i, "ood_drug": p["ood_drug"], "semeval_drug": p["semeval_drug"],
               "fda_label": int(p["label"]), "drugbank_label": db}
        if detail:
            row.update({"ood_resolved": ea is not None, "partner_resolved": eb is not None})
        rows.append(row)
    res = [r for r in rows if r["drugbank_label"] != "unresolvable"]
    pos = [r for r in res if r["fda_label"] == 1]
    neg = [r for r in res if r["fda_label"] == 0]
    summary = {
        "total": len(rows), "resolvable": len(res), "unresolvable": len(rows) - len(res),
        "pos_resolvable": len(pos), "pos_confirmed": sum(r["drugbank_label"] == "positive" for r in pos),
        "neg_resolvable": len(neg), "neg_contradicted": sum(r["drugbank_label"] == "positive" for r in neg),
    }
    summary["positive_precision"] = round(summary["pos_confirmed"] / len(pos), 4) if pos else None
    summary["negative_contradiction_rate"] = round(summary["neg_contradicted"] / len(neg), 4) if neg else None
    return rows, summary
