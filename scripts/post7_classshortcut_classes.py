import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ddiood.drugbank import strip_salt

OUT = ROOT / "results" / "revision" / "post7" / "classshortcut"

MAB_INFIX = (("tu", "mab:tumor"), ("li", "mab:immunomodulator"), ("ki", "mab:interleukin"), ("ci", "mab:cardiovascular"),
             ("ba", "mab:bacterial"), ("vi", "mab:viral"), ("so", "mab:bone"), ("ne", "mab:neural"), ("gr", "mab:growth"))

STEMS = ("ximab", "cept", "tinib", "ciclib", "parib", "rafenib", "lisib", "zomib", "degib", "prazole", "sartan", "pril",
         "prilat", "olol", "alol", "dipine", "vastatin", "statin", "gliptin", "gliflozin", "glitazone", "glinide", "triptan",
         "setron", "tidine", "floxacin", "oxacin", "cillin", "conazole", "navir", "previr", "asvir", "buvir", "citabine",
         "ciclovir", "vudine", "virine", "gravir", "azepam", "azolam", "barbital", "caine", "profen", "coxib", "dronate",
         "dronic acid", "parin", "xaban", "gatran", "thiazide", "afil", "lukast", "terol", "sonide", "olone", "asone",
         "isolone", "oxetine", "triptyline", "ipramine", "peridol", "peridone", "apine", "pine", "mycin", "micin", "cycline",
         "nidazole", "platin", "taxel", "rubicin", "mustine", "trexate", "trexed", "fungin", "relix", "relin", "adol",
         "orphan", "orphanol", "fentanil", "curium", "curonium", "vaptan", "lutamide", "trozole", "oxifene", "ifene",
         "limus", "imod", "tecan", "poetin", "grastim", "gramostim", "kinra", "steride", "osin", "azosin", "onide",
         "isone", "semide", "etanide", "lamide", "flunomide", "pressin", "tocin", "reotide", "tide", "glutide", "enatide",
         "lintide", "dopa", "giline", "mantadine", "azoline", "zoline", "dazole", "bendazole", "quine", "quinine",
         "sulfa", "amide", "zodone", "faxine", "pramine", "plon", "clone", "pidem", "melteon", "racetam", "tirom",
         "nacept", "tadine", "astine", "fenadine", "lizumab", "dronic", "anib", "gepant", "dustat", "copan", "fetamine", "sudil", "vir", "ine")

GENERIC_FALLBACK = ("ine", "vir", "amide", "pine", "tide")
MERGE = {"dronic": "dronate", "dronic acid": "dronate", "prilat": "pril", "micin": "mycin", "orphanol": "orphan"}


def stem_of(name):
    n = strip_salt(name).split("-")[0].replace(" acid", "").split(" ")[0]
    n = re.sub(r"[^a-z]", "", n.lower())
    if not n:
        return None
    if n.endswith("mab"):
        core = n[:-3]
        core = re.sub(r"(xi|zu|u|o|a|e|i|axo|xizu)$", "", core)
        for inf, lab in MAB_INFIX:
            if core.endswith(inf) or core.endswith(inf + "m") or core.endswith(inf + "s") or core.endswith(inf + "n"):
                return lab
        return "mab"
    best = None
    for s in STEMS:
        if s in GENERIC_FALLBACK:
            continue
        if n.endswith(s.replace(" ", "")) and len(n) > len(s) + 1 and (best is None or len(s) > len(best)):
            best = s
    return MERGE.get(best, best)


def load_atc():
    return json.loads((OUT / "atc_codes.json").read_text())["drugs"]


def classes(name, atc, definition):
    if definition == "stem":
        s = stem_of(name)
        return {s} if s else set()
    codes = (atc.get(name) or {}).get("atc", [])
    k = 5 if definition == "atc4" else 4
    return {c[:k] for c in codes if len(c) >= k}
