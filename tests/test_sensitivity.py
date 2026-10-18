import csv
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ddiood import drugbank
from ddiood import evaluate2 as ev


def write_csv(path, rows):
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def test_missing_drugbank_raises(tmp_path, monkeypatch):
    monkeypatch.setattr(ev, "ARTIFACTS", tmp_path / "none")
    with pytest.raises(ev.MissingDrugBankError, match="--allow-missing-drugbank"):
        ev.load_drugbank(tmp_path)


def test_missing_drugbank_allowed_with_flag(tmp_path, monkeypatch):
    monkeypatch.setattr(ev, "ARTIFACTS", tmp_path / "none")
    found = ev.load_drugbank(tmp_path, allow_missing_drugbank=True)
    assert found == {"ood": None, "oodold": None}


def test_partial_drugbank_still_raises(tmp_path, monkeypatch):
    monkeypatch.setattr(ev, "ARTIFACTS", tmp_path / "none")
    write_csv(tmp_path / "drugbank_validation.csv",
              [{"pair_id": 0, "ood_drug": "a", "semeval_drug": "b", "fda_label": 1, "drugbank_label": "positive"}])
    with pytest.raises(ev.MissingDrugBankError, match="oodold"):
        ev.load_drugbank(tmp_path)
    assert ev.load_drugbank(tmp_path, allow_missing_drugbank=True)["ood"][0]["drugbank_label"] == "positive"


def test_load_truth_checks_drugbank_before_anything_else(tmp_path, monkeypatch):
    monkeypatch.setattr(ev, "ARTIFACTS", tmp_path / "none")
    monkeypatch.setattr(ev.semeval, "download", lambda: pytest.fail("download reached before the DrugBank check"))
    with pytest.raises(ev.MissingDrugBankError):
        ev.load_truth(tmp_path)


def test_cli_flag_is_parsed(monkeypatch, tmp_path):
    seen = {}
    monkeypatch.setattr(ev, "load_truth", lambda **kw: seen.update(kw) or (_ for _ in ()).throw(SystemExit(0)))
    with pytest.raises(SystemExit):
        ev.main(["--preds", str(tmp_path), "--allow-missing-drugbank"])
    assert seen == {"allow_missing_drugbank": True}
    seen.clear()
    with pytest.raises(SystemExit):
        ev.main(["--preds", str(tmp_path)])
    assert seen == {"allow_missing_drugbank": False}


TABLE = {"clopidogrel": {"omeprazole"}, "omeprazole": {"clopidogrel"}, "warfarin": {"aspirin"}, "aspirin": {"warfarin"}}
PAIRS = [{"ood_drug": "clopidogrel bisulfate", "semeval_drug": "omeprazole", "label": "1"},
         {"ood_drug": "clopidogrel bisulfate", "semeval_drug": "warfarin", "label": "0"},
         {"ood_drug": "unknownumab", "semeval_drug": "aspirin", "label": "0"},
         {"ood_drug": "unknownumab", "semeval_drug": "nothing", "label": "0"}]


def test_salt_stripping_is_off_by_default():
    rows, _ = drugbank.validate(PAIRS, TABLE, {})
    assert [r["drugbank_label"] for r in rows] == ["negative", "negative", "negative", "unresolvable"]
    assert set(rows[0]) == {"pair_id", "ood_drug", "semeval_drug", "fda_label", "drugbank_label"}


def test_salt_stripping_resolves_salt_forms():
    rows, _ = drugbank.validate(PAIRS, TABLE, {}, strip_salts=True, detail=True)
    assert rows[0]["ood_resolved"] and rows[0]["drugbank_label"] == "positive"
    assert rows[1]["drugbank_label"] == "negative"
    assert drugbank.strip_salt("Eletriptan  Hydrobromide") == "eletriptan"
    assert drugbank.strip_salt("sodium") == "sodium"


def test_one_sided_pairs_can_be_unresolvable():
    rows, s = drugbank.validate(PAIRS, TABLE, {}, strip_salts=True, one_sided="unresolvable")
    assert [r["drugbank_label"] for r in rows] == ["positive", "negative", "unresolvable", "unresolvable"]
    assert s["resolvable"] == 2
    rows, _ = drugbank.validate(PAIRS, TABLE, {}, one_sided="unresolvable")
    assert [r["drugbank_label"] for r in rows] == ["unresolvable"] * 4
    with pytest.raises(ValueError):
        drugbank.validate(PAIRS, TABLE, {}, one_sided="other")
