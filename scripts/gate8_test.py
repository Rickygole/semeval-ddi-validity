import io
import json
import sys
import tokenize
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import gate8_power as gp
from ddiood import evaluate2 as ev

SOURCES = [Path(gp.__file__), Path(__file__)]


@pytest.fixture(scope="module")
def data():
    return gp.cohort_data(ev.load_truth(), json.loads(gp.SCREEN.read_text()))


def test_criteria_fixed():
    c = gp.load_criteria()
    assert c["K_values"] == [0.25, 0.33, 0.50]
    assert c["simulation"]["reps_per_point"] >= 200 and c["simulation"]["bootstrap_draws_per_rep"] >= 300
    assert set(c["designs"]) >= set(gp.DESIGNS) and set(c["label_variants"]) == set(gp.VARIANTS)


def test_variant_masks(data):
    for c, n_flag in (("novel", 1), ("older_clean", 38)):
        d = data[c]
        assert int(d["flag"].sum()) == n_flag and (d["y"][d["flag"]] == 1).all()
        r = gp.variant_mask(d, "validated_rule")
        assert int((~r).sum()) == n_flag
        o = gp.variant_mask(d, "validated_rule_plus_db")
        dropped = ~o & r
        assert ((d["y"][dropped] == 0) & (d["db"][dropped] == 1)).all()
        assert not ((d["y"][o] == 0) & (d["db"][o] == 1)).any()


def test_design_sizes(data):
    assert len(gp.pick_drugs(data["novel"], "novel48", 0)) == 48
    p = gp.pick_drugs(data["novel"], "novel60", 1)
    assert len(p) == 60 and len(set(p)) == 48
    q = gp.pick_drugs(data["older_clean"], "older_clean60", 1)
    assert len(q) == 60 and len(set(q)) == 60
    a = gp.assemble(data["novel"], p)
    assert len(set(a["g"])) == 60 and len(a["y"]) == len(a["db"]) == len(a["q"]) == len(a["flag"])


def test_kappa_bounds_one_sided():
    two = np.tile(np.linspace(0.4, 0.8, 201), (1, 1))
    b = gp.kappa_bounds(two, np.full(201, 0.9))
    k = (np.linspace(0.4, 0.8, 201) - 0.5) / 0.4
    assert b["up95_one_sided"][0] == pytest.approx(np.percentile(k, 95))
    assert b["lo95_two_sided"][0] == pytest.approx(np.percentile(k, 2.5))


def test_small_job_runs(data):
    d = gp.assemble(data["novel"], gp.pick_drugs(data["novel"], "novel48", 0))
    r = gp.run_job({"design": "novel48", "cohort": "novel", "realisation": 0, "variant": "as_is", "cohort_id": 9999,
                    "picked": [], "data": d, "reps": 4, "boot": 20, "n_cal": 10, "K": [0.25, 0.33, 0.5]})
    assert r["drugbank_within"] == pytest.approx(0.729, abs=1e-3)
    assert set(r["null"]["power_by_K"]) == {"0.25", "0.33", "0.5"} and r["control"] is not None


def test_sources_and_outputs_clean():
    for f in SOURCES:
        txt = f.read_text()
        assert chr(0x2013) not in txt and chr(0x2014) not in txt and "cla" + "ude" not in txt.lower()
        assert not [t for t in tokenize.generate_tokens(io.StringIO(txt).readline) if t.type == tokenize.COMMENT]
    for p in gp.OUT.glob("*"):
        txt = p.read_text()
        assert chr(0x2013) not in txt and chr(0x2014) not in txt and "cla" + "ude" not in txt.lower()


def test_verdict_follows_rule():
    p = gp.OUT / "gate8.json"
    if not p.exists():
        pytest.skip("gate8.json not written yet")
    r = json.loads(p.read_text())
    for K, v in r["verdict"].items():
        t = r["power"]
        gov = [dz for dz in gp.DESIGNS if t[dz][gp.GOVERNING]["null_power_by_K"][K] >= 0.8
               and (t[dz][gp.GOVERNING]["control_power"] or 0) >= 0.8]
        assert (v["verdict"] == "GO") == bool(gov)
