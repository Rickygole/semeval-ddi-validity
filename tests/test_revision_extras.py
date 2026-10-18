import sys
from pathlib import Path

import numpy as np
import pytest
from sklearn.metrics import average_precision_score, f1_score, matthews_corrcoef

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ddiood import audit, prevalence


def toy(n=300, seed=0):
    rng = np.random.RandomState(seed)
    y = (rng.rand(n) < 0.25).astype(int)
    p = np.clip(0.4 * y + rng.rand(n) * 0.6, 0, 1)
    return y, p, (p > 0.5).astype(int), rng.randint(0, 20, n)


def test_all_positive_f1_matches_definition():
    assert prevalence.all_positive_f1(1 / 3) == pytest.approx(0.5)
    y = np.array([1] * 371 + [0] * 2439)
    assert prevalence.all_positive_f1(y.mean()) == pytest.approx(f1_score(y, np.ones_like(y)))


def test_reference_row_matches_sklearn():
    y, p, pb, g = toy()
    r = prevalence.reference_row(y, p, pb, g, boot=200)
    assert r["f1"] == pytest.approx(f1_score(y, pb))
    assert r["mcc"] == pytest.approx(matthews_corrcoef(y, pb))
    assert r["auprc"] == pytest.approx(average_precision_score(y, p))
    assert r["auprc_minus_prevalence"] == pytest.approx(r["auprc"] - y.mean())
    assert r["tp"] + r["fp"] + r["fn"] + r["tn"] == len(y)
    assert r["mcc_lo"] <= r["mcc"] <= r["mcc_hi"]
    again = prevalence.reference_row(y, p, pb, g, boot=200)
    assert again["mcc_lo"] == r["mcc_lo"] and again["f1_hi"] == r["f1_hi"]


def test_constant_prediction_has_zero_mcc_and_half_balanced_accuracy():
    y, p, _, g = toy()
    r = prevalence.reference_row(y, p, np.zeros_like(y), g, boot=50)
    assert r["mcc"] == 0.0 and r["balanced_accuracy"] == 0.5 and r["f1"] == 0.0


def test_multiclass_confusion_counts_every_pair():
    m = prevalence.multiclass_confusion([0, 1, 2, 2, 4], [0, 2, 2, 0, 4])
    assert np.asarray(m).sum() == 5 and m[2][2] == 1 and m[1][2] == 1 and m[2][0] == 1


def test_matched_counts_and_indices_hit_target():
    assert prevalence.matched_counts(371, 2439, 148 / 438) == (371, 727)
    assert prevalence.matched_counts(148, 290, 371 / 2810) == (44, 290)
    y = np.array([1] * 371 + [0] * 2439)
    idx = prevalence.matched_indices(y, 148 / 438, np.random.RandomState(1))
    assert y[idx].sum() == 371 and len(idx) == 371 + 727 and len(set(idx)) == len(idx)


def test_prevalence_matched_is_deterministic_and_on_target():
    y, p, pb, _ = toy(400)
    a = prevalence.prevalence_matched(y, p, pb, 0.5, n=50, seed=3)
    b = prevalence.prevalence_matched(y, p, pb, 0.5, n=50, seed=3)
    assert a == b
    assert a["frozen"]["prevalence"] == pytest.approx(0.5)
    assert a["resampled"]["f1_all_positive"]["mean"] == pytest.approx(prevalence.all_positive_f1(0.5))


def ood_rows(n_drugs=12, n_pos=4, n_neg=8):
    rows = []
    for d in range(n_drugs):
        rows += [{"ood_drug": f"d{d}", "semeval_drug": f"p{d}_{i}", "label": "1"} for i in range(n_pos)]
        rows += [{"ood_drug": f"d{d}", "semeval_drug": f"q{d}_{i}", "label": "0"} for i in range(n_neg)]
    return rows


def test_audit_sample_is_balanced_blind_and_deterministic():
    rows = ood_rows()
    items = audit.sample(rows, 30, 30, seed=42)
    assert sum(it["label"] == "1" for it in items) == 30 and len(items) == 60
    assert items == audit.sample(rows, 30, 30, seed=42)
    for lab in ("1", "0"):
        per = {}
        for it in items:
            if it["label"] == lab:
                per[it["ood_drug"]] = per.get(it["ood_drug"], 0) + 1
        assert len(per) == 12 and max(per.values()) - min(per.values()) <= 1
    sheet = audit.sheet_rows(items, {f"d{d}": "section text" for d in range(12)})
    assert all("label" not in r and "fda_label" not in r and "evidence" not in r for r in sheet)
    assert {r["drug_interactions_section"] for r in sheet} == {"section text"}
    assert len({r["item_id"] for r in sheet}) == 60


def test_audit_sample_refuses_too_few_rows():
    with pytest.raises(ValueError):
        audit.sample(ood_rows(2, 1, 1), 5, 1)


def filled(key, answers, basis="named"):
    return [{"item_id": k["item_id"], "annotator": "x", "interacts": a, "basis": basis, "notes": ""}
            for k, a in zip(key, answers)]


def test_kappa_report_hand_example():
    key = [{"item_id": f"Q{i}", "fda_label": lab} for i, lab in enumerate([1, 1, 0, 0])]
    rep, tier_c = audit.report(filled(key, ["yes", "yes", "no", "no"]), filled(key, ["yes", "no", "no", "no"]), key, 100)
    assert rep["kappa_yes_no"] == pytest.approx(0.5)
    assert rep["percent_agreement_yes_no"] == pytest.approx(0.75)
    assert rep["tier_c_size"] == 3 and rep["n_disagreements_excluded"] == 1
    assert rep["agreement_with_fda_label"]["annotator_1"]["agreement"] == 1.0
    assert {t["item_id"] for t in tier_c} == {"Q0", "Q2", "Q3"}


def test_kappa_report_drops_unsure_and_validates():
    key = [{"item_id": f"Q{i}", "fda_label": i % 2} for i in range(6)]
    a = filled(key, ["yes", "no", "unsure", "no", "yes", "no"])
    b = filled(key, ["yes", "no", "yes", "no", "yes", "unsure"])
    rep, _ = audit.report(a, b, key, 100)
    assert rep["n_unsure_either"] == 2 and rep["n_both_decided"] == 4 and rep["kappa_yes_no"] == pytest.approx(1.0)
    bad = filled(key, ["yes", "no", "maybe", "no", "yes", "no"])
    with pytest.raises(ValueError):
        audit.report(bad, b, key, 10)
    with pytest.raises(ValueError):
        audit.report(a[:5], b, key, 10)
