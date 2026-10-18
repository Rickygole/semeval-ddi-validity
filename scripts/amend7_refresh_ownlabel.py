import gzip
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ddiood import amend7_pairs as ap
from ddiood import amend7_retrieval as ar
from ddiood import config
from ddiood.index import Encoder
from ddiood.inputs import ood_as_pairs
from ddiood.openfda import LabelStore

OUT = ROOT / "artifacts" / "amend7"


def main():
    chunks, emb = ar.load_base()
    n_base = len(chunks)
    store = LabelStore(offline=True)
    lookup = json.loads((config.ARTIFACTS / "vocab" / "drug_lookup.json").read_text())
    train = ap.read_rows(OUT / "train_pairs.csv")
    ood = ap.read_csv(ROOT / "results" / "corrected" / "ood_pairs.csv")
    old = ap.read_csv(ROOT / "results" / "corrected" / "ood_old_pairs.csv")
    old_names = sorted({r["ood_drug"] for r in old})
    extra = ar.older_chunks(old_names, store, n_base)
    chunks_all = chunks + extra
    emb_all = np.vstack([emb, np.load(OUT / "ext_embeddings.npy")])
    names = ap.ood_name_set(ood, old)
    excl = json.loads((OUT / "train_pairs_report.json").read_text())["audit"]["excluded_vocab"]
    u_train = ar.universe_mask(chunks_all, set(names) | set(excl))
    u_base = ar.universe_mask(chunks_all, only_below=n_base)
    u_all = ar.universe_mask(chunks_all)
    qv = ar.QueryVectors(Encoder())
    pairs = lambda rows: [{"drug_a": r["drug_a"], "drug_b": r["drug_b"]} for r in rows]
    jobs = {"train": (pairs(train), u_train), "novel": (pairs(ood_as_pairs(ood)), u_base),
            "older": (pairs(ood_as_pairs(old)), u_all)}
    payload = json.loads((OUT / "retrieval.json").read_text())
    full = json.load(gzip.open(OUT / "retrieval_full.json.gz", "rt"))
    have = set(payload["chunk_text"]) | set(json.load(gzip.open(ROOT / "artifacts" / "bundle" / "inputs.json.gz", "rt"))["chunk_text"])
    for g, (ps, uni) in jobs.items():
        cache = ar.retrieve_arm(chunks_all, emb_all, qv, ps, uni, "ownlabel", lookup=lookup)
        miss = [k for k, v in cache.items() if not v]
        if miss:
            raise SystemExit(f"{g}: {len(miss)} queries without passages")
        payload["retrieval"][g]["ownlabel"] = cache
        full["retrieval"][g]["ownlabel"] = cache
        for ids in cache.values():
            for i in ids:
                payload["chunk_meta"][str(i)] = [chunks_all[i]["drug"], chunks_all[i]["section"]]
                if str(i) not in have:
                    payload["chunk_text"][str(i)] = chunks_all[i]["text"]
                    have.add(str(i))
                full["chunk_text"][str(i)] = chunks_all[i]["text"]
        payload["coverage"][f"{g}/ownlabel"] = {"queries": len(cache), "with_passages": len(cache)}
        print(g, len(cache), flush=True)
    (OUT / "retrieval.json").write_text(json.dumps(payload))
    with gzip.open(OUT / "retrieval_full.json.gz", "wt") as f:
        json.dump(full, f)


if __name__ == "__main__":
    main()
