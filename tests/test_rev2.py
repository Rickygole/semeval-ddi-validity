import json
import sys
import zipfile
from pathlib import Path

import numpy as np
import pytest
from sklearn.metrics import f1_score

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import rev2_common as rc
import rev2_m3b as m3b
import rev2_m4 as m4
import rev2_m10 as m10

OUT = ROOT / "results" / "revision" / "rev2"
SCRIPTS = sorted((ROOT / "scripts").glob("rev2_*.py")) + [Path(__file__)]


def test_criteria_written():
    c = json.loads((OUT / "criteria.json").read_text())
    for k in ("m3b", "m4", "m7", "m8", "m9", "m10", "already_known_when_written"):
        assert k in c


def test_wilson_bounds():
    lo, hi = rc.wilson(50, 100)
    assert lo < 0.5 < hi
    assert rc.wilson(0, 0) is None
    lo, hi = rc.wilson(0, 10)
    assert lo == pytest.approx(0.0, abs=1e-12) and hi > 0


def test_micro_f1_matches_sklearn():
    rng = np.random.RandomState(0)
    gold = rng.randint(0, 5, 400)
    pred = rng.randint(0, 5, 400)
    tp, p, g = m10.micro(gold, pred)
    want = f1_score(gold, pred, labels=[1, 2, 3, 4], average="micro", zero_division=0)
    assert m10.f1_from(tp, p, g) == pytest.approx(want)
    assert m10.f1_from(tp, p, g, 50) < m10.f1_from(tp, p, g)


def test_binary_auroc_decomposition():
    rng = np.random.RandomState(1)
    y = rng.randint(0, 2, 500)
    s = rng.randint(0, 2, 500).astype(float)
    com = rng.rand(500) < 0.4
    d = m3b.decomposition(y, s, com, np.ones(500, bool), "toy")
    assert d["pooled"]["auroc"] == pytest.approx(d["pooled"]["auroc_direct"])
    for k in ("co-mentioned", "not co-mentioned"):
        assert 0 <= d[k]["tpr"] <= 1


def test_rho_boot_and_perm():
    x = np.arange(10, dtype=float)
    d, dropped = m4.rho_boot(x, -x, 200, 0)
    assert np.all(d <= -0.99)
    assert m4.perm_p(x, -x, 500, 0) < 0.01


def test_header_parse(tmp_path):
    xml = '<?xml version="1.0"?>\n<drugbank xmlns="http://www.drugbank.ca" version="5.1" exported-on="2026-03-05">\n</drugbank>'
    z = tmp_path / "db.xml.zip"
    with zipfile.ZipFile(z, "w") as f:
        f.writestr("full database.xml", xml)
    h = m3b.header(z)
    assert h["version"] == "5.1" and h["exported_on"] == "2026-03-05"


def load(name):
    p = OUT / f"{name}.json"
    if not p.exists():
        pytest.skip(f"{name}.json not generated")
    return json.loads(p.read_text())


def test_m4_reproduces_exp7_and_post7():
    o = load("m4_partner")
    assert o["checks"] and all(c["match"] for c in o["checks"])
    r = {(x["tier"], x["cohort"], x["format"]): x for x in o["rho"]}
    assert r[("A", "older_primary", "marker")]["rho"] == pytest.approx(-0.4788, abs=1e-3)
    assert r[("A", "older_primary", "all")]["rho"] == pytest.approx(-0.1609, abs=1e-3)
    assert len([k for k in o["adjust"]["novel"]["systems"] if k.startswith("panel ")]) == 20


def test_m3b_records_release_and_reproduces_exp5():
    o = load("m3b_drugbank")
    assert o["drugbank_release"]["version"] and o["drugbank_release"]["exported_on"]
    assert all(o["check_exp5"].values())
    assert o["listing_rates"]["random vocabulary pairs (names)"]["n"] == 10000


def test_m7_reproduces():
    assert load("m7_prereg_endpoint")["endpoint"]["reproduces_tables_md"]


def test_m9_reproduces_h2():
    o = load("m9_confusion")
    assert o["h2_ratio"]["reproduces"]
    assert len(o["panel"]) == 60


def test_m10_counts():
    o = load("m10_semeval_standard")
    assert o["test"]["n_scored"] == 2810 and o["test"]["n_official"] == 5716
    assert o["published"]["rows"]["PubMedBERT (uncased)"] == 82.36


def test_style_rules():
    files = SCRIPTS + sorted(OUT.glob("*"))
    banned = ("cl" + "aude", chr(0x2013), chr(0x2014))
    for f in files:
        text = f.read_text(encoding="utf-8").lower()
        for b in banned:
            assert b not in text, f"{b!r} in {f.name}"
    for f in SCRIPTS:
        for line in f.read_text().splitlines():
            assert not line.lstrip().startswith("#"), f"comment in {f.name}"
