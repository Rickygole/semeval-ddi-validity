import json
from pathlib import Path

import numpy as np

from . import config
from .index import chunk_words, leaks, query, rrf
from .openfda import section_text
from .pipeline import _novel_label, _variant_ids
from .textnorm import drug_tokenize

ARMS = {"contaminated": ("contaminated", "all"), "clean": ("clean", "all"), "other": ("clean", "exclude_own"),
        "ownlabel": ("contaminated", "only_own")}


def older_chunks(names, store, first_id):
    out = []
    for drug in sorted(names):
        label = _novel_label(store, drug)
        if not label:
            continue
        for section in config.INDEX_SECTIONS + [config.HOLDOUT_SECTION]:
            for text in chunk_words(section_text(label, section)):
                out.append({"chunk_id": first_id + len(out), "drug": drug, "section": section, "text": text,
                            "leaks": leaks(text)})
    return out


def load_base(artifacts=config.ARTIFACTS):
    chunks = json.loads((Path(artifacts) / "index" / "all_chunks.json").read_text())
    emb = np.load(Path(artifacts) / "index" / "embeddings.npy")
    return chunks, emb


class QueryVectors:
    def __init__(self, encoder):
        self.encoder = encoder
        self.cache = {}

    def get(self, pairs):
        todo = sorted({(p["drug_a"], p["drug_b"]) for p in pairs if (p["drug_a"], p["drug_b"]) not in self.cache})
        if todo:
            vecs = self.encoder([query(a, b) for a, b in todo]).astype("float32")
            for k, v in zip(todo, vecs):
                self.cache[k] = v
        return self.cache


def _dense_rows(q, x, x2, excl_rows, k):
    d = x2[None, :] - 2 * q @ x.T
    for r, pos in enumerate(excl_rows):
        if len(pos):
            d[r, pos] = np.inf
    k = min(k, d.shape[1] - 1)
    part = np.argpartition(d, k, axis=1)[:, :k]
    order = np.take_along_axis(d, part, 1).argsort(1, kind="stable")
    idx = np.take_along_axis(part, order, 1)
    return np.where(np.isfinite(np.take_along_axis(d, idx, 1)), idx, -1)


def retrieve_arm(chunks, emb, qv, pairs, universe, arm, batch=512, lookup=None):
    from rank_bm25 import BM25Okapi
    from .amend7_evidence import partner_forms
    index_name, mode = ARMS[arm]
    if mode == "only_own" and lookup is None:
        raise RuntimeError("own-label retrieval needs the vocabulary lookup for partner forms")
    ids = [i for i in _variant_ids(chunks, index_name) if universe[i]]
    sub = [chunks[i] for i in ids]
    bm25 = BM25Okapi([drug_tokenize(c["text"]) for c in sub])
    x = emb[ids]
    x2 = (x ** 2).sum(1)
    by_drug = {}
    for j, c in enumerate(sub):
        by_drug.setdefault(c["drug"], []).append(j)
    todo = sorted({(p["drug_a"], p["drug_b"]) for p in pairs})
    vecs = qv.get(pairs)
    out = {}
    for i in range(0, len(todo), batch):
        part = todo[i:i + batch]
        q = np.stack([vecs[k] for k in part])
        excl = []
        for a, _ in part:
            own = np.array(by_drug.get(a, []), dtype=int)
            if mode == "exclude_own":
                excl.append(own)
            elif mode == "only_own":
                if not len(own):
                    raise RuntimeError(f"no chunks for the label of {a}")
                excl.append(np.setdiff1d(np.arange(len(sub)), own))
            else:
                excl.append(np.array([], dtype=int))
        dense = _dense_rows(q, x, x2, excl, config.CANDIDATES_PER_RETRIEVER)
        for r, (a, b) in enumerate(part):
            q_text = " ".join(partner_forms(b, lookup)) if mode == "only_own" else query(a, b)
            s = bm25.get_scores(drug_tokenize(q_text))
            if len(excl[r]):
                s[excl[r]] = -1.0
            lists = [[int(j) for j in np.argsort(-s)[:config.CANDIDATES_PER_RETRIEVER] if s[j] > 0],
                     [int(j) for j in dense[r] if j >= 0]]
            out[f"{a}|||{b}"] = [sub[j]["chunk_id"] for j in rrf(lists, config.TOP_K)]
    return out


def universe_mask(chunks, drugs_excluded=(), only_below=None):
    m = np.ones(len(chunks), bool)
    ex = set(drugs_excluded)
    for c in chunks:
        if c["drug"] in ex or (only_below is not None and c["chunk_id"] >= only_below):
            m[c["chunk_id"]] = False
    return m
