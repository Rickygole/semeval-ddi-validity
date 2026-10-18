import gzip
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ddiood import amend7_pairs as ap
from ddiood import amend7_retrieval as ar
from ddiood import config, semeval
from ddiood.index import Encoder
from ddiood.inputs import ood_as_pairs
from ddiood.ood import label_identity
from ddiood.openfda import LabelStore
from ddiood.pipeline import _novel_label

OUT = ROOT / "artifacts" / "amend7"


def pairs_of(rows):
    return [{"drug_a": r["drug_a"], "drug_b": r["drug_b"]} for r in rows]


def main():
    chunks, emb = ar.load_base()
    n_base = len(chunks)
    enc = Encoder()
    qv = ar.QueryVectors(enc)
    store = LabelStore(offline=True)
    lookup = json.loads((config.ARTIFACTS / "vocab" / "drug_lookup.json").read_text())
    train = ap.read_rows(OUT / "train_pairs.csv")
    ood = ap.read_csv(ROOT / "results" / "corrected" / "ood_pairs.csv")
    old = ap.read_csv(ROOT / "results" / "corrected" / "ood_old_pairs.csv")
    novel_pairs, old_pairs = ood_as_pairs(ood), ood_as_pairs(old)
    semeval.download()
    test_pairs = semeval.load_pairs("test")

    old_names = sorted({r["ood_drug"] for r in old})
    gated = [n for n in old_names if _novel_label(store, n) and not label_identity(_novel_label(store, n), n)]
    if gated != old_names:
        raise SystemExit(f"Older labels failing the identity gate: {sorted(set(old_names) - set(gated))}")
    extra = ar.older_chunks(old_names, store, n_base)
    covered = {c["drug"] for c in extra}
    if covered != set(old_names):
        raise SystemExit(f"Older drugs without chunks: {sorted(set(old_names) - covered)}")
    path = OUT / "ext_embeddings.npy"
    if path.exists() and np.load(path, mmap_mode="r").shape[0] == len(extra):
        ext_emb = np.load(path)
    else:
        ext_emb = enc([c["text"] for c in extra]).astype("float32")
        np.save(path, ext_emb)
    chunks_all = chunks + extra
    emb_all = np.vstack([emb, ext_emb])
    print(f"base chunks {n_base}, older chunks {len(extra)} for {len(covered)} drugs", flush=True)

    names = ap.ood_name_set(ood, old)
    excl = json.loads((OUT / "train_pairs_report.json").read_text())["audit"]["excluded_vocab"]
    u_train = ar.universe_mask(chunks_all, set(names) | set(excl))
    u_base = ar.universe_mask(chunks_all, only_below=n_base)
    u_all = ar.universe_mask(chunks_all)

    groups = {"train": (pairs_of(train), u_train, ("contaminated", "clean", "other", "ownlabel")),
              "novel": (pairs_of(novel_pairs), u_base, ("other", "ownlabel")),
              "test": (pairs_of(test_pairs), u_base, ("other",)),
              "older": (pairs_of(old_pairs), u_all, ("contaminated", "clean", "other", "ownlabel"))}
    retrieval = {}
    for g, (pairs, uni, arms) in groups.items():
        retrieval[g] = {}
        for arm in arms:
            retrieval[g][arm] = ar.retrieve_arm(chunks_all, emb_all, qv, pairs, uni, arm, lookup=lookup)
            print(g, arm, len(retrieval[g][arm]), flush=True)

    ref = {a: json.loads((config.ARTIFACTS / "retrieval" / f).read_text())
           for a, f in (("clean", "hybrid.json"), ("contaminated", "contaminated.json"))}
    check = {}
    for arm in ("contaminated", "clean"):
        got = ar.retrieve_arm(chunks_all, emb_all, qv, pairs_of(novel_pairs), u_base, arm)
        check[arm] = {"queries": len(got), "mismatches": sum(got[k] != ref[arm].get(k) for k in got)}
        retrieval.setdefault("novel", {})[arm] = got
        sample = pairs_of(test_pairs)[::14]
        got_t = ar.retrieve_arm(chunks_all, emb_all, qv, sample, u_base, arm)
        check[arm + "_test_sample"] = {"queries": len(got_t), "mismatches": sum(got_t[k] != ref[arm].get(k) for k in got_t)}
        retrieval.setdefault("test", {})[arm + "_sample"] = got_t
    print("reproduction of the existing caches:", check, flush=True)
    if any(c["mismatches"] for c in check.values()):
        raise SystemExit("new retrieval code does not reproduce the existing caches")
    for arm in ("contaminated", "clean"):
        full = {k: ref[arm][k] for k in {f"{p['drug_a']}|||{p['drug_b']}" for p in pairs_of(test_pairs)}}
        retrieval["test"][arm] = full
        del retrieval["test"][arm + "_sample"]

    coverage = {}
    for g, (pairs, _, _) in groups.items():
        keys = {f"{p['drug_a']}|||{p['drug_b']}" for p in pairs}
        for arm, cache in retrieval[g].items():
            miss = [k for k in keys if not cache.get(k)]
            coverage[f"{g}/{arm}"] = {"queries": len(keys), "with_passages": len(keys) - len(miss)}
            if miss:
                raise SystemExit(f"{g}/{arm}: {len(miss)} queries without passages, e.g. {miss[:3]}")
    print("coverage", json.dumps(coverage), flush=True)

    existing = json.load(gzip.open(ROOT / "artifacts" / "bundle" / "inputs.json.gz", "rt"))
    have = set(existing["chunk_text"])
    used = set()
    for g in retrieval:
        for arm, cache in retrieval[g].items():
            if g in ("novel", "test") and arm in ("contaminated", "clean"):
                continue
            for ids in cache.values():
                used.update(ids)
    new_text = {str(i): chunks_all[i]["text"] for i in sorted(used) if str(i) not in have}
    meta = {}
    for g in retrieval:
        for cache in retrieval[g].values():
            for ids in cache.values():
                for i in ids:
                    meta[str(i)] = [chunks_all[i]["drug"], chunks_all[i]["section"]]
    ship = {g: {arm: cache for arm, cache in retrieval[g].items()
                if not (g in ("novel", "test") and arm in ("contaminated", "clean"))} for g in retrieval}
    payload = {"retrieval": ship, "chunk_text": new_text, "chunk_meta": meta, "base_chunks": n_base,
               "older_chunks": len(extra), "reproduction_check": check, "coverage": coverage}
    (OUT / "retrieval.json").write_text(json.dumps(payload))
    full_payload = {"retrieval": retrieval, "chunk_text": {str(i): chunks_all[i]["text"] for i in sorted(set(
        i for g in retrieval for c in retrieval[g].values() for ids in c.values() for i in ids))}}
    with gzip.open(OUT / "retrieval_full.json.gz", "wt") as f:
        json.dump(full_payload, f)
    print(json.dumps({"shipped_chunk_texts": len(new_text), "meta": len(meta)}))


if __name__ == "__main__":
    main()
