import argparse
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ddiood.drugbank import NS, _norm, _open, _text, strip_salt

OUT = ROOT / "results" / "revision" / "post7" / "classshortcut"
DEFAULT_XML = Path.home() / "Downloads" / "drugbank_all_full_database.xml.zip"


def parse(path):
    table = {}
    with _open(path) as f:
        for _, el in ET.iterparse(f, events=("end",)):
            if el.tag != NS + "drug" or el.get("type") is None:
                continue
            codes = set()
            atc = el.find(NS + "atc-codes")
            if atc is not None:
                codes = {c.get("code") for c in atc.findall(NS + "atc-code") if c.get("code")}
            if codes:
                names = {_norm(_text(el, "name"))} - {""}
                syn = el.find(NS + "synonyms")
                if syn is not None:
                    names |= {_norm(s.text) for s in syn.findall(NS + "synonym") if s.text}
                for n in names:
                    table.setdefault(n, set()).update(codes)
            el.clear()
    return table


def lookup_codes(name, table):
    for form in (_norm(name), strip_salt(name)):
        if form in table:
            return sorted(table[form]), form
    first = _norm(name).split("-")[0]
    if first in table:
        return sorted(table[first]), first
    return [], None


def needed_names():
    from ddiood.amend7_pairs import read_csv
    names = set()
    for r in read_csv(ROOT / "artifacts" / "amend7" / "train_pairs.csv"):
        names |= {r["drug_a"], r["drug_b"]}
    for f in ("ood_pairs.csv", "ood_old_pairs.csv"):
        for r in read_csv(ROOT / "results" / "corrected" / f):
            names |= {r["ood_drug"], r["semeval_drug"]}
    return sorted(names)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--xml", default=str(DEFAULT_XML))
    a = ap.parse_args()
    table = parse(a.xml)
    out = {}
    for n in needed_names():
        codes, form = lookup_codes(n, table)
        out[n] = {"atc": codes, "matched_form": form}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "atc_codes.json").write_text(json.dumps({"source": str(a.xml), "drugs": out}, indent=1) + "\n")
    print(sum(1 for v in out.values() if v["atc"]), "of", len(out), "names have ATC codes")


if __name__ == "__main__":
    main()
