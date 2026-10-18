import csv
import json
import re
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import post8_common as pc
import post8_criteria as cr
import post8_e9 as e9
import post8_screen as sc
from ddiood import amend7_analysis as aa

OUT = ROOT / "results" / "revision" / "post8"
LOOKUP = {"colchicine": {"normalized": "colchicine", "canonicalized": "colchicine", "rxcui": "1"},
          "warfarin": {"normalized": "warfarin", "canonicalized": "warfarin", "rxcui": "2"},
          "amphetamine": {"normalized": "amphetamine", "canonicalized": "amphetamine", "rxcui": "3"},
          "ketoconazole": {"normalized": "ketoconazole", "canonicalized": "ketoconazole", "rxcui": "4"},
          "methadone": {"normalized": "methadone", "canonicalized": "methadone", "rxcui": "5"},
          "tamsulosin": {"normalized": "tamsulosin", "canonicalized": "tamsulosin", "rxcui": "6"},
          "rifampin": {"normalized": "rifampin", "canonicalized": "rifampin", "rxcui": "7"}}


@pytest.fixture
def rule():
    sections = {"drugx": {"text": "7 DRUG INTERACTIONS 7.1 Strong Inhibitors Avoid ketoconazole. 7.2 Drugs without Clinically "
                                  "Significant Interactions with Drugx In studies, methadone exposure was similar."}}
    return pc.Rule(cr.CRITERIA_DOC, LOOKUP, sections)


def test_requested_phrases_are_covered():
    pats = [re.compile(p, re.IGNORECASE) for _, p in cr.NONINTERACTION]
    for phrase in ("no clinically significant", "not clinically significant", "does not alter", "does not affect",
                   "did not affect", "no effect", "lack of effect", "were not observed", "no dose adjustment",
                   "without clinically significant", "no meaningful", "not expected to"):
        assert any(p.search(phrase) for p in pats), phrase
    heads = [re.compile(p, re.IGNORECASE) for _, p in cr.HEADING]
    assert any(p.search("Drugs without Clinically Significant Interactions") for p in heads)
    labs = [re.compile(p, re.IGNORECASE) for _, p in cr.LABTEST]
    assert any(p.search("False-positive urine immunoassay screening tests") for p in labs)


def test_interaction_phrases_are_not_flagged(rule):
    for s in ("Coadministration with warfarin is not recommended.", "Do not exceed 10 mg when used with warfarin.",
              "Avoid concomitant use with ketoconazole.", "Warfarin should not be used with Drugx."):
        r = rule.screen("drugy", s.split()[0].lower() if s.startswith("Warfarin") else ("warfarin" if "warfarin" in s else "ketoconazole"), s)
        assert r["flag"] == 0, s


def test_noninteraction_flag(rule):
    s = "Based on drug interaction studies, febuxostat does not have clinically significant interactions with colchicine or warfarin."
    r = rule.screen("febuxostat", "colchicine", s)
    assert r["flag"] == 1 and "N" in r["families"] and r["scope"] == "clause"


def test_veto_by_interaction_clause(rule):
    s = ("Although the administration of clopidogrel did not modify the pharmacokinetics of warfarin, coadministration of "
         "clopidogrel with warfarin increases the risk of bleeding.")
    assert rule.screen("clopidogrel", "warfarin", s)["flag"] == 0


def test_clause_scope_other_partner(rule):
    s = "Ketoconazole increased exposure 3-fold; rifampin had no effect on exposure."
    assert rule.screen("drugy", "ketoconazole", s)["flag"] == 0
    assert rule.screen("drugy", "rifampin", s)["flag"] == 1


def test_labtest_and_heading(rule):
    s = "7.4 Drug-Laboratory Test Interactions False-positive urine immunoassay screening tests for amphetamine have been reported."
    r = rule.screen("drugy", "amphetamine", s)
    assert r["flag"] == 1 and "L" in r["families"]
    r = rule.screen("drugx", "methadone", "In studies, methadone exposure was similar.")
    assert r["flag"] == 1 and r["families"].startswith("H")


def test_absence_family_not_flagged(rule):
    r = rule.screen("drugy", "tamsulosin", "The effect of tamsulosin on drugy pharmacokinetics has not been evaluated.")
    assert r["flag"] == 0 and r["absence"] == 1


def test_partner_not_located_uses_sentence(rule):
    r = rule.screen("drugy", "colchicine", "No clinically significant interaction was seen.")
    assert r["scope"] == "sentence" and r["flag"] == 1


def test_truthc_masks_rows():
    rows = [{"ood_drug": d, "semeval_drug": p, "label": str(y)} for d, p, y in
            (("a", "x", 1), ("a", "y", 0), ("a", "z", 1), ("b", "x", 0), ("b", "y", 1))]
    base = aa.Truth(rows, rows)
    keep = {"ood": np.array([True, True, False, True, True]), "oodold": np.ones(5, bool)}
    t = pc.TruthC(base, keep)
    c = t.cohort("novel")
    assert c["y"].tolist() == [1, 0, 0, 1] and c["g"].tolist() == ["a", "a", "b", "b"]
    assert len(base.cohort("novel")["y"]) == 5


def test_keep_masks_drop_only_flagged_positives():
    screens = {"novel": [None, {"flag": 1, "absence": 0}, {"flag": 0, "absence": 1}],
               "older": [{"flag": 0, "absence": 0}, None]}
    k = pc.keep_masks(screens)
    assert k["ood"].tolist() == [True, False, True] and k["oodold"].tolist() == [True, True]
    kb = pc.keep_masks(screens, broad=True)
    assert kb["ood"].tolist() == [True, False, False]


def test_paired_reference_identity():
    rng = np.random.default_rng(3)
    y, g, q = [], [], []
    for d in range(10):
        for k, p in enumerate(rng.choice(12, 5, replace=False)):
            y.append(int(k < 2))
            g.append(f"d{d}")
            q.append(f"p{p}")
    c = {"y": np.array(y), "g": np.array(g), "q": np.array(q)}
    scores = [rng.normal(size=len(y)) + 0.2 * np.array(y) for _ in range(4)]
    point, D, _ = e9.panel_draws(c, scores, 200, 5)
    from itertools import combinations
    pv = np.mean([np.var(D[:, i] - D[:, j], ddof=1) for i, j in combinations(range(4), 2)]) / 2
    cov = np.cov(D.T, ddof=1)
    mean_cov = (cov.sum() - np.trace(cov)) / (4 * 3)
    assert abs(pv - (np.trace(cov) / 4 - mean_cov)) < 1e-12


def test_audit_items_shuffled_and_blind():
    rows = {"novel": [{"ood_drug": "a", "semeval_drug": "x", "label": "1", "evidence": "e1", "cooccurrence_sentence": ""},
                      {"ood_drug": "a", "semeval_drug": "y", "label": "0", "evidence": "", "cooccurrence_sentence": ""}],
            "older": [{"ood_drug": "b", "semeval_drug": "x", "label": "1", "evidence": "e2", "cooccurrence_sentence": ""}]}
    s = {"flag": 0, "families": "", "absence": 0, "patterns": [], "scope": "clause", "ood_drug_not_named": 0, "cooccurrence_also_flags": 0}
    screens = {"novel": [s, None], "older": [dict(s, flag=1)]}
    oracle = {"novel": np.array([0.2, 0.9]), "older": np.array([0.8])}
    items = sc.audit_items(rows, screens, oracle)
    assert len(items) == 3 and all(it["author_label"] == "" and it["notes"] == "" for it in items)
    assert sorted(it["item_id"] for it in items) == ["A001", "A002", "A003"]
    assert not any("oracle" in c or "score" in c for c in sc.SHEET_COLUMNS)


@pytest.mark.skipif(not (OUT / "label_audit_sheet.csv").exists(), reason="post8 outputs not built")
def test_audit_sheet_outputs():
    sheet = list(csv.DictReader(open(OUT / "label_audit_sheet.csv", newline="")))
    key = list(csv.DictReader(open(OUT / "label_audit_key.csv", newline="")))
    assert [r["item_id"] for r in sheet] == [r["item_id"] for r in key]
    assert list(sheet[0].keys()) == sc.SHEET_COLUMNS
    assert all(r["author_label"] == "" and r["notes"] == "" for r in sheet)
    for r in key:
        p, y = float(r["oracle_p_yes"]), int(r["current_label"])
        assert (y == 1 and (p < 0.5 or r["rule_flag"] == "1")) or (y == 0 and p > 0.5)


@pytest.mark.skipif(not (OUT / "summary.json").exists(), reason="post8 outputs not built")
def test_summary_checks_and_reviewer_numbers():
    s = json.loads((OUT / "summary.json").read_text())
    assert all(s["checks"].values())
    assert s["reviewer_comparison"]["older_positives_oracle_below_0.5"]["here"] == "142 of 648"
    assert s["reviewer_comparison"]["negatives_oracle_above_0.5"]["older"] == 52
    crit = json.loads((OUT / "criteria.json").read_text())
    assert crit["rule"]["noninteraction_patterns"] == cr.NONINTERACTION


def test_post8_files_are_clean():
    files = sorted((ROOT / "scripts").glob("post8_*.py")) + [Path(__file__)] + sorted(OUT.glob("*"))
    for f in files:
        text = f.read_text(encoding="utf-8")
        assert chr(0x2013) not in text and chr(0x2014) not in text, f
        assert "cla" + "ude" not in text.lower(), f
        if f.suffix == ".py":
            assert not any(line.strip().startswith("#") for line in text.splitlines()), f
