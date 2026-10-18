import argparse
import csv
import json
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ddiood import config, logreg, semeval
from ddiood.inputs import ood_as_pairs, pairs_hash

A = ROOT / "artifacts"
SAVED = ROOT / "results" / "corrected" / "preds" / "b4_s42.json"
OUT = ROOT / "results" / "revision" / "cpu" / "b4-lr-s42.json"


def features(pairs, cache, emb):
    rows = []
    for a, b in pairs:
        ids = cache.get(f"{a}|||{b}") or cache.get(f"{b}|||{a}") or []
        rows.append(emb[ids].mean(axis=0) if ids else np.zeros(emb.shape[1]))
    return np.array(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(OUT))
    a = ap.parse_args()
    t0 = time.time()
    emb = np.load(A / "index" / "embeddings.npy")
    cache = json.loads((A / "retrieval" / "hybrid.json").read_text())
    semeval.download()
    tr, te = semeval.load_pairs("train"), semeval.load_pairs("test")
    ood = list(csv.DictReader(open(ROOT / "results" / "corrected" / "ood_pairs.csv")))
    Xtr = features([(p["drug_a"], p["drug_b"]) for p in tr], cache, emb)
    Xte = features([(p["drug_a"], p["drug_b"]) for p in te], cache, emb)
    Xood = features([(r["ood_drug"], r["semeval_drug"]) for r in ood], cache, emb)
    scaler, clf = logreg.fit(Xtr, [p["label_id"] for p in tr], config.PRIMARY_SEED)
    false_col = list(clf.classes_).index(0)
    ev = {}
    for key, X in (("test", Xte), ("ood", Xood)):
        Z = scaler.transform(X)
        ev[key] = {"preds": [int(v) for v in clf.predict(Z)],
                   "p": [round(float(1 - v), 6) for v in clf.predict_proba(Z)[:, false_col]]}
    saved = json.loads(SAVED.read_text())
    match = {"test": ev["test"]["preds"] == saved["test_preds"], "ood": ev["ood"]["preds"] == saved["ood_preds"]}
    ood_hash = pairs_hash(ood_as_pairs(ood))
    if ood_hash != saved["ood_hash"]:
        raise SystemExit("OOD pair hash differs from the saved B4 file")
    res = {"config": {"kind": "cpu", "system": "b4", "model": "pubmedbert-embeddings-logreg", "seed": config.PRIMARY_SEED,
                      "split": "standard", "name": "b4-lr-s42"},
           "ood_hash": ood_hash, "reproduces_saved_hard_predictions": match, "eval": ev,
           "seconds": round(time.time() - t0, 1)}
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(res))
    print(json.dumps({"out": str(out.relative_to(ROOT)), "ood_hash": ood_hash, "reproduces": match,
                      "seconds": res["seconds"]}))


if __name__ == "__main__":
    main()
