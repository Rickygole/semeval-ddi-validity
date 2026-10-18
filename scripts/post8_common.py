import csv
import json
import re
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from ddiood import amend7_analysis as aa
from ddiood import evaluate2 as ev
from ddiood.amend7_evidence import clean_ws, partner_forms
from ddiood.textnorm import mentions

OUT = ROOT / "results" / "revision" / "post8"
CRITERIA = OUT / "criteria.json"
CORRECTED = ROOT / "results" / "corrected"
AMEND7 = ROOT / "artifacts" / "amend7"
PREDS = ROOT / "runs" / "preds"
CPU = AMEND7 / "preds_cpu"
STATUS = "post hoc and exploratory; criteria in criteria.json were written before computing; changes no preregistered decision"
COHORT_FILES = {"novel": "ood_pairs.csv", "older": "ood_old_pairs.csv"}
TAGS = {"novel": "ood", "older": "oodold"}


def require_criteria():
    if not CRITERIA.exists():
        raise SystemExit("results/revision/post8/criteria.json must be written before this analysis runs")
    return json.loads(CRITERIA.read_text())


def read_csv(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def load_rows(corrected=CORRECTED):
    return {c: read_csv(Path(corrected) / f) for c, f in COHORT_FILES.items()}


class Rule:
    def __init__(self, crit, lookup, sections):
        r = crit["rule"]
        comp = lambda pats: [(i, re.compile(p, re.IGNORECASE)) for i, p in pats]
        self.n, self.l, self.h = comp(r["noninteraction_patterns"]), comp(r["labtest_patterns"]), comp(r["heading_patterns"])
        self.s = comp(r["secondary_absence_family"]["patterns"])
        self.split = re.compile(r["clause_regex"], re.IGNORECASE)
        self.conc = re.compile(r["concessive_regex"], re.IGNORECASE)
        self.sub = re.compile(r["subsection_regex"])
        self.lookup = lookup
        self.sections = sections
        self._forms = {}

    def forms(self, partner):
        if partner not in self._forms:
            self._forms[partner] = partner_forms(partner, self.lookup)
        return self._forms[partner]

    def clauses(self, text):
        out = []
        for part in self.split.split(clean_ws(text)):
            part = part.strip(" ,")
            if not part:
                continue
            if self.conc.match(part) and "," in part:
                a, b = part.split(",", 1)
                out += [a.strip(), b.strip(" ,")]
            else:
                out.append(part)
        return [c for c in out if c]

    def names(self, clause, partner):
        low = clause.lower()
        return any(f in low and mentions(f, low) for f in self.forms(partner))

    @staticmethod
    def hits(pats, text):
        return [i for i, p in pats if p.search(text)]

    def heading(self, drug, evidence):
        text = clean_ws((self.sections.get(drug) or {}).get("text", ""))
        ev_ = clean_ws(evidence)
        pos = text.find(ev_) if ev_ else -1
        if pos < 0 and ev_:
            pos = text.find(ev_[:80])
        if pos < 0:
            return "", False
        before = text[:pos]
        starts = [m.start() for m in self.sub.finditer(before)]
        if not starts:
            return "", True
        head = before[starts[-1]:][:300]
        return head, True

    def screen(self, drug, partner, evidence):
        clauses = self.clauses(evidence)
        named = [c for c in clauses if self.names(c, partner)]
        scope = "clause"
        if not named:
            named, scope = [clean_ws(evidence)], "sentence"
        per = [(self.hits(self.n, c), self.hits(self.l, c), self.hits(self.s, c)) for c in named]
        all_nl = all(n or l for n, l, _ in per)
        all_s = all(n or l or s for n, l, s in per)
        head, located = self.heading(drug, evidence)
        h = sorted(set(self.hits(self.h, clean_ws(evidence)) + (self.hits(self.h, head) if head else [])))
        fam = []
        if h:
            fam.append("H")
        if all_nl and any(n for n, _, _ in per):
            fam.append("N")
        if all_nl and any(l for _, l, _ in per):
            fam.append("L")
        flag = int(bool(h) or all_nl)
        absence = int(not flag and all_s and any(s for _, _, s in per))
        matched = sorted({x for n, l, s in per for x in n + l + s} | set(h))
        return {"flag": flag, "families": "".join(fam), "absence": absence, "scope": scope, "patterns": matched,
                "n_clauses": len(clauses), "n_partner_clauses": len(named) if scope == "clause" else 0,
                "heading": head, "evidence_located": located}

    def screen_nl(self, partner, text):
        if not clean_ws(text):
            return 0
        named = [c for c in self.clauses(text) if self.names(c, partner)]
        if not named:
            return 0
        return int(all(self.hits(self.n, c) or self.hits(self.l, c) for c in named))


def drug_named(drug, text):
    low = clean_ws(text).lower()
    first = re.split(r"[\s\-]", drug.lower())[0]
    keys = {drug.lower()} | ({first} if len(first) >= 4 else set())
    return any(k in low and mentions(k, low) for k in keys)


def load_rule(crit):
    lookup = json.loads((AMEND7 / "lookup.json").read_text())
    sections = json.loads((AMEND7 / "di_sections.json").read_text())
    return Rule(crit, lookup, sections)


def screen_all(rule, rows):
    out = {}
    for c, rs in rows.items():
        res = []
        for r in rs:
            if str(r["label"]) != "1":
                res.append(None)
                continue
            s = rule.screen(r["ood_drug"], r["semeval_drug"], r["evidence"])
            s["ood_drug_not_named"] = int(not drug_named(r["ood_drug"], r["evidence"]))
            s["cooccurrence_also_flags"] = rule.screen_nl(r["semeval_drug"], r.get("cooccurrence_sentence", ""))
            res.append(s)
        out[c] = res
    return out


def flag_vectors(screens):
    v = {}
    for c, res in screens.items():
        v[c] = {"flag": np.array([0 if s is None else s["flag"] for s in res], int),
                "absence": np.array([0 if s is None else s["absence"] for s in res], int)}
    return v


def keep_masks(screens, broad=False):
    out = {}
    for c, f in flag_vectors(screens).items():
        drop = f["flag"].astype(bool)
        if broad:
            drop |= f["absence"].astype(bool)
        out[TAGS[c]] = ~drop
    return out


def oracle_scores(rows, preds=PREDS):
    r = json.loads((Path(preds) / "a7-qwen-oracle.json").read_text())
    out = {}
    for c, tag, field in (("novel", "ood", "ood_hash"), ("older", "oodold", "ood_old_hash")):
        pairs = ev.inputs.ood_as_pairs(rows[c])
        if r[field] != ev.inputs.pairs_hash(pairs):
            raise ValueError(f"oracle {field} does not match the frozen {c} pair set")
        y = np.array([p["y"] for p in pairs])
        p = np.asarray(r["eval"][tag]["p"], float)
        if len(p) != len(y):
            raise ValueError("oracle length mismatch")
        pic = np.asarray(r["context"][tag]["partner_in_context"])
        if (pic[y == 0] != 0).any() or pic[y == 1].mean() < 0.99:
            raise ValueError("oracle partner_in_context does not follow the label order")
        out[c] = p
    return out


class TruthC(aa.Truth):
    def __init__(self, base, keep):
        self.sets, self.test_y, self.sensitivity = base.sets, base.test_y, base.sensitivity
        self.keep = keep

    def cohort(self, name, tier="A", drop=()):
        c = super().cohort(name, tier, drop)
        k = self.keep[c["tag"]]
        m = c["mask"] & k
        s = self.sets[c["tag"]]
        return {"tag": c["tag"], "mask": m, "y": s["y"][m], "g": s["g"][m], "q": s["q"][m], "name": name}


def a7_truth():
    rows = load_rows()
    db_ood = read_csv(ROOT / "artifacts" / "ood" / "drugbank_validation.csv")
    db_old = read_csv(ROOT / "artifacts" / "ood" / "drugbank_validation_old.csv")
    sets = json.loads((AMEND7 / "primary_sets.json").read_text())
    sens = sets["sensitivity_shingle"]
    return aa.Truth(rows["novel"], rows["older"], db_ood, db_old,
                    {"novel": sens["novel"], "older_primary": sens["older_primary"]}), sens, (db_ood, db_old)


def screens_for_run():
    crit = require_criteria()
    rows = load_rows()
    rule = load_rule(crit)
    return crit, rows, rule, screen_all(rule, rows)


def write(name, obj, md):
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{name}.json").write_text(json.dumps(ev.clean(aa.clean(obj)), indent=1) + "\n")
    if md is not None:
        (OUT / f"{name}.md").write_text(md)


def f3(v):
    if v is None or (isinstance(v, float) and v != v):
        return "NA"
    return f"{v:.3f}"


def ci(lo, hi=None):
    if hi is None:
        if not lo:
            return "NA"
        lo, hi = lo
    return "NA" if lo is None or hi is None else f"[{f3(lo)}, {f3(hi)}]"
