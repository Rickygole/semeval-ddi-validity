import argparse
import csv
import gzip
import hashlib
import json
import re
import shutil
from collections import Counter
from pathlib import Path

import numpy as np

from . import config, semeval
from .index import HybridIndex, chunk_words, leaks
from .openfda import LabelStore, section_text
from .textnorm import normalize

A = config.ARTIFACTS

VARIANTS = {
    "hybrid": {"mode": "hybrid", "index": "clean"},
    "bm25": {"mode": "bm25", "index": "clean"},
    "dense": {"mode": "dense", "index": "clean"},
    "excl_mechanism_of_action": {"mode": "hybrid", "index": "excl_mechanism_of_action"},
    "excl_pharmacokinetics": {"mode": "hybrid", "index": "excl_pharmacokinetics"},
    "excl_warnings_and_cautions": {"mode": "hybrid", "index": "excl_warnings_and_cautions"},
    "excl_clinical_pharmacology": {"mode": "hybrid", "index": "excl_clinical_pharmacology"},
    "contaminated": {"mode": "hybrid", "index": "contaminated"},
}


def dump(obj, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=1))
    return path


def load(path):
    return json.loads(Path(path).read_text())


def step_data(_):
    corpus = semeval.download()
    tr, te = semeval.load_pairs("train"), semeval.load_pairs("test")
    stats = {"corpus": str(corpus), "commit": config.DDI_COMMIT,
             "train": {"n": len(tr), **Counter(r["label"] for r in tr)},
             "test": {"n": len(te), **Counter(r["label"] for r in te)}}
    dump(stats, A / "semeval_stats.json")
    print(json.dumps(stats, indent=1))


def step_vocab(_):
    from .rxnorm import CachedRxNorm
    from .vocab import build_lookup
    rx = CachedRxNorm(A / "vocab" / "rxnorm_cache.json")
    lookup, audit, conflicts, counts = build_lookup(rx)
    dump(lookup, A / "vocab" / "drug_lookup.json")
    dump(conflicts, A / "vocab" / "rxcui_conflicts.json")
    dump(counts, A / "vocab" / "vocab_counts.json")
    with open(A / "vocab" / "rxnorm_audit.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(audit[0]))
        w.writeheader()
        w.writerows(audit)
    print(json.dumps(counts, indent=1))


def _novel_label(store, name):
    label = store.get(name, fields=("openfda.generic_name", "openfda.substance_name"))
    if label is None:
        base = re.sub(r"-[a-z]{4}$", "", name)
        if base != name:
            label = store.get(base, fields=("openfda.generic_name", "openfda.substance_name"))
    return label


def _excluded_names(lookup):
    names = set()
    for split in ("train", "test"):
        raw, _ = semeval.load_entities(split, entity_types={"drug", "drug_n", "brand", "group"})
        names |= {normalize(n) for n in raw}
    names |= set(lookup) | {v["canonicalized"] for v in lookup.values()}
    return names


def step_labels(args):
    from .ood import novel_drugs
    store = LabelStore(offline=args.offline)
    lookup = load(A / "vocab" / "drug_lookup.json")
    if not args.offline:
        store.prefetch([lookup[k]["normalized"] for k in lookup])
    avail = {}
    for i, key in enumerate(sorted(lookup)):
        avail[key] = store.get(lookup[key]["normalized"]) is not None
        if i % 100 == 0:
            print(f"vocabulary labels {i}/{len(lookup)}", flush=True)
    novel, rejected = novel_drugs(config.NME_CSV, _excluded_names(lookup), prior_csv=config.PRIOR_APPROVALS_CSV)
    if not args.offline:
        store.prefetch([d["drug"] for d in novel], fields=("openfda.generic_name", "openfda.substance_name"))
    nl = {}
    for d in novel:
        nl[d["drug"]] = _novel_label(store, d["drug"]) is not None
    dump({"vocab_label_found": avail, "novel_label_found": nl, "novel_drugs": novel,
          "novel_rejected": rejected}, A / "labels" / "coverage.json")
    print(f"vocabulary drugs with a label: {sum(avail.values())}/{len(avail)}")
    print(f"novel drugs with a label: {sum(nl.values())}/{len(nl)}; rejected: {rejected}")


def step_ood(args):
    from .ood import build_pairs, summarize, write_csv
    store = LabelStore(offline=True)
    lookup = load(A / "vocab" / "drug_lookup.json")
    cov = load(A / "labels" / "coverage.json")
    novel = [d for d in cov["novel_drugs"] if cov["novel_label_found"].get(d["drug"])]
    sha_src = hashlib.sha256(json.dumps(novel, sort_keys=True).encode()).hexdigest()
    dump({"sha256": sha_src, "drugs": novel}, A / "ood" / "ood_drugs_source.json")

    class Store:
        def get(self, name, fields=None):
            return _novel_label(store, name)

    pairs, report = build_pairs(novel, Store(), lookup, cov["vocab_label_found"],
                                max_pos_per_drug=args.max_pos_per_drug, negatives="partner")
    rand, _ = build_pairs(novel, Store(), lookup, cov["vocab_label_found"],
                          max_pos_per_drug=args.max_pos_per_drug, negatives="random")
    write_csv(rand, A / "ood" / "ood_pairs_random_negatives.csv")
    sha = write_csv(pairs, A / "ood" / "ood_pairs.csv")
    summary = {**summarize(pairs), "sha256": sha, "source_sha256": sha_src,
               "max_pos_per_drug": args.max_pos_per_drug, "novel_drugs_with_label": len(novel)}
    dump(report, A / "ood" / "ood_construction_report.json")
    dump(summary, A / "ood" / "ood_summary.json")
    print(json.dumps(summary, indent=1))


def _all_chunks():
    store = LabelStore(offline=True)
    lookup = load(A / "vocab" / "drug_lookup.json")
    cov = load(A / "labels" / "coverage.json")
    labels = {k: store.get(lookup[k]["normalized"]) for k, ok in cov["vocab_label_found"].items() if ok}
    for d in cov["novel_drugs"]:
        if cov["novel_label_found"].get(d["drug"]):
            labels[d["drug"]] = _novel_label(store, d["drug"])
    out = []
    for drug in sorted(labels):
        for section in config.INDEX_SECTIONS + [config.HOLDOUT_SECTION]:
            for text in chunk_words(section_text(labels[drug], section)):
                out.append({"chunk_id": len(out), "drug": drug, "section": section, "text": text,
                            "leaks": leaks(text)})
    return out


def _variant_ids(chunks, name):
    clean = [c for c in chunks if c["section"] in config.INDEX_SECTIONS and not c["leaks"]]
    if name == "clean":
        sel = clean
    elif name == "contaminated":
        sel = chunks
    elif name.startswith("excl_"):
        sec = name[5:]
        sel = [c for c in clean if c["section"] != sec]
    else:
        raise ValueError(name)
    for c in sel:
        if name != "contaminated" and (c["leaks"] or c["section"] == config.HOLDOUT_SECTION):
            raise RuntimeError("leakage assertion failed")
    return [c["chunk_id"] for c in sel]


def step_index(_):
    from .index import Encoder
    chunks = _all_chunks()
    dump(chunks, A / "index" / "all_chunks.json")
    emb_path = A / "index" / "embeddings.npy"
    if emb_path.exists() and np.load(emb_path, mmap_mode="r").shape[0] == len(chunks):
        emb = np.load(emb_path)
    else:
        emb = Encoder()([c["text"] for c in chunks]).astype("float32")
        np.save(emb_path, emb)
    sizes = {}
    for name in ["clean", "contaminated"] + [f"excl_{s}" for s in config.INDEX_SECTIONS]:
        ids = _variant_ids(chunks, name)
        sizes[name] = len(ids)
    sizes["leaked_chunks_skipped"] = sum(1 for c in chunks if c["leaks"] and c["section"] in config.INDEX_SECTIONS)
    sizes["di_chunks"] = sum(1 for c in chunks if c["section"] == config.HOLDOUT_SECTION)
    dump(sizes, A / "index" / "index_sizes.json")
    print(json.dumps(sizes, indent=1))


def _build_variant(chunks, emb, name, encoder):
    from rank_bm25 import BM25Okapi
    from .textnorm import drug_tokenize
    ids = _variant_ids(chunks, name)
    sub = [dict(chunks[i], local=j) for j, i in enumerate(ids)]
    bm25 = BM25Okapi([drug_tokenize(c["text"]) for c in sub])
    return HybridIndex(sub, bm25, None, encoder)


def _dense_topk(q, x, k, batch=512):
    out = []
    for i in range(0, len(q), batch):
        d = (x ** 2).sum(1)[None, :] - 2 * q[i:i + batch] @ x.T
        part = np.argpartition(d, k, axis=1)[:, :k]
        order = np.take_along_axis(d, part, 1).argsort(1, kind="stable")
        out.append(np.take_along_axis(part, order, 1))
    return np.vstack(out)


def _pair_lists():
    tr, te = semeval.load_pairs("train"), semeval.load_pairs("test")
    ood = list(csv.DictReader(open(A / "ood" / "ood_pairs.csv")))
    oq = [{"drug_a": r["ood_drug"], "drug_b": r["semeval_drug"]} for r in ood]
    return tr, te, oq


def step_retrieve(_):
    from .index import Encoder, query
    chunks = load(A / "index" / "all_chunks.json")
    emb = np.load(A / "index" / "embeddings.npy")
    enc = Encoder()
    tr, te, oq = _pair_lists()
    todo = sorted({(p["drug_a"], p["drug_b"]) for p in tr + te + oq})
    qvec = enc([query(a, b) for a, b in todo]).astype("float32")
    built = {}
    for vname, spec in VARIANTS.items():
        if spec["index"] not in built:
            built[spec["index"]] = _build_variant(chunks, emb, spec["index"], None)
        ix = built[spec["index"]]
        dense = _dense_topk(qvec, emb[[c["chunk_id"] for c in ix.chunks]], config.CANDIDATES_PER_RETRIEVER)
        from .index import rrf
        from .textnorm import drug_tokenize
        cache = {}
        for qi, (a, b) in enumerate(todo):
            lists = []
            if spec["mode"] in ("hybrid", "bm25"):
                s = ix.bm25.get_scores(drug_tokenize(query(a, b)))
                lists.append([int(i) for i in np.argsort(-s)[:config.CANDIDATES_PER_RETRIEVER] if s[i] > 0])
            if spec["mode"] in ("hybrid", "dense"):
                lists.append([int(i) for i in dense[qi] if i >= 0])
            cache[f"{a}|||{b}"] = [ix.chunks[i]["chunk_id"] for i in rrf(lists, config.TOP_K)]
        dump(cache, A / "retrieval" / f"{vname}.json")
        empty = sum(1 for v in cache.values() if not v)
        print(f"{vname}: {len(cache)} queries, {empty} empty", flush=True)


def step_drugbank(args):
    from .drugbank import load_interactions, validate
    table = load_interactions(args.drugbank)
    lookup = load(A / "vocab" / "drug_lookup.json")
    suffix = "" if args.cohort == "novel" else "_old"
    pairs = list(csv.DictReader(open(A / "ood" / f"ood{suffix}_pairs.csv")))
    rows, summary = validate(pairs, table, lookup)
    dump(summary, A / "ood" / f"drugbank_validation{suffix}_summary.json")
    with open(A / "ood" / f"drugbank_validation{suffix}.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(json.dumps(summary, indent=1))


def step_bundle(args):
    chunks = load(A / "index" / "all_chunks.json")
    used = set()
    caches = {}
    for vname in VARIANTS:
        c = load(A / "retrieval" / f"{vname}.json")
        caches[vname] = c
        for v in c.values():
            used.update(v)
    texts = {str(i): chunks[i]["text"] for i in sorted(used)}
    ood = list(csv.DictReader(open(A / "ood" / "ood_pairs.csv")))
    old_path = A / "ood" / "ood_old_pairs.csv"
    ood_old = list(csv.DictReader(open(old_path))) if old_path.exists() else []
    payload = {"chunk_text": texts, "retrieval": caches, "ood_pairs": ood, "ood_old_pairs": ood_old}
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(out, "wt") as f:
        json.dump(payload, f)
    print(f"{out}: {out.stat().st_size / 1e6:.2f} MB, {len(texts)} chunk texts, {len(ood)} OOD pairs, "
          f"{len(ood_old)} older-drug pairs")


def step_logreg(args):
    from . import logreg
    from .metrics import binary_f1, macro_f1
    chunks = load(A / "index" / "all_chunks.json")
    emb = np.load(A / "index" / "embeddings.npy")
    cache = load(A / "retrieval" / "hybrid.json")
    tr, te, _ = _pair_lists()
    ood = list(csv.DictReader(open(A / "ood" / "ood_pairs.csv")))

    def feats(pairs):
        rows = []
        for a, b in pairs:
            ids = cache.get(f"{a}|||{b}") or cache.get(f"{b}|||{a}") or []
            rows.append(emb[ids].mean(axis=0) if ids else np.zeros(emb.shape[1]))
        return np.array(rows)

    Xtr = feats([(p["drug_a"], p["drug_b"]) for p in tr])
    Xte = feats([(p["drug_a"], p["drug_b"]) for p in te])
    Xood = feats([(r["ood_drug"], r["semeval_drug"]) for r in ood])
    scaler, clf = logreg.fit(Xtr, [p["label_id"] for p in tr], config.PRIMARY_SEED)
    pte, pood = logreg.predict(scaler, clf, Xte), logreg.predict(scaler, clf, Xood)
    yte = [p["label_id"] for p in te]
    from .inputs import ood_as_pairs, pairs_hash
    out = {"system": "b4", "seed": config.PRIMARY_SEED, "ood_hash": pairs_hash(ood_as_pairs(ood)),
           "test_preds": pte, "ood_preds": pood,
           "test_macro_f1": macro_f1(yte, pte), "test_binary_f1": binary_f1(yte, pte)}
    dump(out, config.RESULTS / "corrected" / "preds" / "b4_s42.json")
    print({k: v for k, v in out.items() if not k.endswith("preds")})


def step_controls(_):
    from .metrics import binary_f1, extended
    from .textnorm import mentions
    chunks = load(A / "index" / "all_chunks.json")
    cache = load(A / "retrieval" / "hybrid.json")
    ood = list(csv.DictReader(open(A / "ood" / "ood_pairs.csv")))
    y = [int(r["label"]) for r in ood]
    out = {"n": len(y), "n_pos": sum(y), "all_positive": extended(y, [1] * len(y))}
    for name, chars in (("partner_named_in_top5_full_text", None), ("partner_named_in_top5_first_100_chars", 100)):
        preds = []
        for r in ood:
            ids = cache.get(f"{r['ood_drug']}|||{r['semeval_drug']}") or []
            text = " ".join(chunks[i]["text"][:chars] if chars else chunks[i]["text"] for i in ids).lower()
            preds.append(int(mentions(r["semeval_drug"], text)))
        out[name] = extended(y, preds)
    own = []
    for r in ood:
        ids = cache.get(f"{r['ood_drug']}|||{r['semeval_drug']}") or []
        own.append(int(any(chunks[i]["drug"] == r["ood_drug"] for i in ids)))
    out["top5_contains_novel_drug_label_chunk_rate"] = {"pos": sum(o for o, t in zip(own, y) if t) / max(1, sum(y)),
                                                         "neg": sum(o for o, t in zip(own, y) if not t) / max(1, len(y) - sum(y))}
    dump(out, config.RESULTS / "corrected" / "controls.json")
    print(json.dumps({k: (round(v["binary_f1"], 4), round(v["mcc"], 4)) if isinstance(v, dict) and "mcc" in v else v
                      for k, v in out.items()}, indent=1))


def step_ood_old(args):
    from .ood import build_pairs, novel_drugs, summarize, write_csv
    store = LabelStore(offline=args.offline)
    lookup = load(A / "vocab" / "drug_lookup.json")
    cov = load(A / "labels" / "coverage.json")
    old, rejected = novel_drugs(config.NME_CSV, _excluded_names(lookup), min_year=1985,
                                prior_csv=config.PRIOR_APPROVALS_CSV)
    old = [d for d in old if d["first_approval_year"] <= args.max_year]
    if not args.offline:
        store.prefetch([d["drug"] for d in old], fields=("openfda.generic_name", "openfda.substance_name"))

    class Store:
        def get(self, name, fields=None):
            return _novel_label(store, name)

    pairs, report = build_pairs(old, Store(), lookup, cov["vocab_label_found"], max_pos_per_drug=10,
                                negatives="partner")
    rand, _ = build_pairs(old, Store(), lookup, cov["vocab_label_found"], max_pos_per_drug=10, negatives="random")
    write_csv(rand, A / "ood" / "ood_old_pairs_random_negatives.csv")
    sha = write_csv(pairs, A / "ood" / "ood_old_pairs.csv")
    summary = {**summarize(pairs), "sha256": sha, "first_approval_years": [1985, args.max_year],
               "candidate_drugs": len(old), "rejected": rejected}
    dump(report, A / "ood" / "ood_old_construction_report.json")
    dump(summary, A / "ood" / "ood_old_summary.json")
    print(json.dumps(summary, indent=1))


def step_baselines(_):
    from . import baselines, stats
    from .metrics import extended
    ctx = baselines.Context(load(A / "vocab" / "drug_lookup.json"))
    cor = config.RESULTS / "corrected"
    db_path = A / "ood" / "drugbank_validation.csv"
    db_rows = list(csv.DictReader(open(db_path))) if db_path.exists() else None
    out = {"seed": config.BOOTSTRAP_SEED, "n_bootstrap": config.N_BOOTSTRAP,
           "bootstrap": "two-way cluster over novel drugs and partner drugs",
           "threshold_rule": "binary baselines at 0.5; prior baselines predict positive when score exceeds the set mean",
           "vocab_labels_with_di": ctx.vocab_n}
    for set_name, fname, rows in (("novel", "ood_pairs.csv", db_rows), ("older", "ood_old_pairs.csv", None),
                                  ("novel_random_negatives", "ood_pairs_random_negatives.csv", None),
                                  ("older_random_negatives", "ood_old_pairs_random_negatives.csv", None)):
        pairs = baselines.read_pairs(cor / fname)
        y = np.array([int(p["label"]) for p in pairs])
        g1 = [p["ood_drug"] for p in pairs]
        g2 = [p["semeval_drug"] for p in pairs]
        res = {}
        for name, score in baselines.score_all(pairs, ctx, rows).items():
            pred = baselines.binarize(name, score)
            m = extended(y, pred)
            res[name] = {
                "auroc": stats.auroc(y, score),
                "auroc_ci95": stats.two_way_bootstrap(stats.auroc, y, score, g1, g2,
                                                      config.N_BOOTSTRAP, config.BOOTSTRAP_SEED),
                "auprc": stats.auprc(y, score), "prevalence": stats.prevalence(y),
                "binary_f1": m["binary_f1"], "mcc": m["mcc"], "balanced_accuracy": m["balanced_accuracy"],
                "confusion": {k: m[k] for k in ("tp", "fp", "fn", "tn")}}
        if set_name == "novel":
            res["drugbank_lookup_reference"]["note"] = "tier A label is the FDA label; circular for tier B"
        out[set_name] = {"n": len(y), "n_pos": int(y.sum()), "baselines": res}
    dump(out, cor / "baselines.json")
    for set_name in ("novel", "older"):
        for name, r in out[set_name]["baselines"].items():
            ci = r["auroc_ci95"]
            print(f"{set_name:6s} {name:28s} auroc {r['auroc']:.3f} [{ci['lower']:.3f},{ci['upper']:.3f}] "
                  f"auprc {r['auprc']:.3f} prev {r['prevalence']:.3f} f1 {r['binary_f1']:.3f} "
                  f"mcc {r['mcc']:.3f} bacc {r['balanced_accuracy']:.3f} {r['confusion']}")


def main(argv=None):
    ap = argparse.ArgumentParser(prog="python -m ddiood.pipeline")
    sp = ap.add_subparsers(dest="step", required=True)
    sp.add_parser("data")
    sp.add_parser("vocab")
    p = sp.add_parser("labels")
    p.add_argument("--offline", action="store_true")
    p = sp.add_parser("ood")
    p.add_argument("--max-pos-per-drug", type=int, default=10)
    sp.add_parser("index")
    sp.add_parser("retrieve")
    p = sp.add_parser("drugbank")
    p.add_argument("--drugbank", required=True)
    p.add_argument("--cohort", choices=["novel", "old"], default="novel")
    p = sp.add_parser("bundle")
    p.add_argument("--out", default=str(A / "bundle" / "inputs.json.gz"))
    sp.add_parser("logreg")
    sp.add_parser("controls")
    p = sp.add_parser("ood_old")
    p.add_argument("--max-year", type=int, default=2012)
    p.add_argument("--offline", action="store_true")
    sp.add_parser("baselines")
    a = ap.parse_args(argv)
    {"data": step_data, "vocab": step_vocab, "labels": step_labels, "ood": step_ood, "index": step_index,
     "retrieve": step_retrieve, "drugbank": step_drugbank, "bundle": step_bundle, "logreg": step_logreg, "controls": step_controls, "ood_old": step_ood_old,
     "baselines": step_baselines}[a.step](a)


if __name__ == "__main__":
    main()
