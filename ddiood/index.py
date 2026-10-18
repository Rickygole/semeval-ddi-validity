import json
import pickle
import re
from pathlib import Path

import numpy as np

from . import config
from .openfda import section_text
from .textnorm import drug_tokenize

DI_PATTERNS = [
    re.compile(r"\bdrug[- ]interactions\b", re.IGNORECASE),
    re.compile(r"\b7\b.{0,20}\bdrug[- ]interactions\b", re.IGNORECASE),
]


def device():
    import torch
    if torch.cuda.is_available():
        return "cuda"
    if torch.backends.mps.is_available():
        return "mps"
    return "cpu"


def chunk_words(text, size=config.CHUNK_WORDS, overlap=config.CHUNK_OVERLAP):
    words = text.split()
    i = 0
    while i < len(words):
        yield " ".join(words[i:i + size])
        i += size - overlap


def leaks(chunk):
    norm = re.sub(r"\s+", " ", chunk.lower())
    return any(p.search(norm) for p in DI_PATTERNS)


def build_chunks(labels, sections=config.INDEX_SECTIONS, leakage_control=True):
    if leakage_control and config.HOLDOUT_SECTION in sections:
        raise RuntimeError("drug_interactions cannot be indexed when leakage control is on")
    chunks, leak_log = [], []
    for drug, label in labels.items():
        for section in sections:
            text = section_text(label, section)
            for chunk in chunk_words(text):
                if leakage_control and leaks(chunk):
                    leak_log.append({"drug": drug, "section": section, "snippet": chunk[:200]})
                    continue
                chunks.append({"chunk_id": len(chunks), "drug": drug, "section": section, "text": chunk})
    if leakage_control:
        for c in chunks:
            if leaks(c["text"]) or c["section"] == config.HOLDOUT_SECTION:
                raise RuntimeError(f"leakage assertion failed on chunk {c['chunk_id']}")
    return chunks, leak_log


class Encoder:
    def __init__(self, name=config.RETRIEVAL_ENCODER, dev=None, batch_size=32):
        import torch
        from transformers import AutoModel, AutoTokenizer
        self.torch = torch
        self.dev = dev or device()
        self.tok = AutoTokenizer.from_pretrained(name)
        self.model = AutoModel.from_pretrained(name).to(self.dev).eval()
        self.batch_size = batch_size

    def __call__(self, texts):
        out = []
        for i in range(0, len(texts), self.batch_size):
            enc = self.tok(texts[i:i + self.batch_size], padding=True, truncation=True,
                           max_length=512, return_tensors="pt").to(self.dev)
            with self.torch.no_grad():
                h = self.model(**enc).last_hidden_state
            m = enc["attention_mask"].unsqueeze(-1).to(h.dtype)
            v = ((h * m).sum(dim=1) / m.sum(dim=1)).float().cpu().numpy()
            out.append(v / np.linalg.norm(v, axis=1, keepdims=True))
        return np.vstack(out) if out else np.zeros((0, 768), dtype="float32")


class HybridIndex:
    def __init__(self, chunks, bm25, faiss_index, encoder=None):
        self.chunks = chunks
        self.bm25 = bm25
        self.faiss = faiss_index
        self.encoder = encoder

    @classmethod
    def build(cls, chunks, encoder):
        import faiss
        from rank_bm25 import BM25Okapi
        bm25 = BM25Okapi([drug_tokenize(c["text"]) for c in chunks])
        vecs = encoder([c["text"] for c in chunks]).astype("float32")
        idx = faiss.IndexFlatL2(vecs.shape[1])
        idx.add(vecs)
        return cls(chunks, bm25, idx, encoder)

    def save(self, out):
        import faiss
        out = Path(out)
        out.mkdir(parents=True, exist_ok=True)
        (out / "chunks.json").write_text(json.dumps(self.chunks))
        with open(out / "bm25.pkl", "wb") as f:
            pickle.dump(self.bm25, f)
        faiss.write_index(self.faiss, str(out / "faiss.index"))

    @classmethod
    def load(cls, path, encoder=None):
        import faiss
        path = Path(path)
        chunks = json.loads((path / "chunks.json").read_text())
        with open(path / "bm25.pkl", "rb") as f:
            bm25 = pickle.load(f)
        return cls(chunks, bm25, faiss.read_index(str(path / "faiss.index")), encoder)

    def search_many(self, queries, k=config.TOP_K, mode="hybrid", pool=config.CANDIDATES_PER_RETRIEVER):
        dense = None
        if mode in ("hybrid", "dense"):
            vecs = self.encoder(queries).astype("float32")
            _, dense = self.faiss.search(vecs, pool)
        results = []
        for qi, q in enumerate(queries):
            lists = []
            if mode in ("hybrid", "bm25"):
                scores = self.bm25.get_scores(drug_tokenize(q))
                lists.append([int(i) for i in np.argsort(-scores)[:pool] if scores[i] > 0])
            if mode in ("hybrid", "dense"):
                lists.append([int(i) for i in dense[qi] if i >= 0])
            results.append(rrf(lists, k))
        return [[self.chunks[i]["text"] for i in ids] for ids in results]


def rrf(ranked_lists, k=config.TOP_K, rrf_k=config.RRF_K):
    score = {}
    for lst in ranked_lists:
        for rank, cid in enumerate(lst):
            score[cid] = score.get(cid, 0.0) + 1.0 / (rrf_k + rank + 1)
    return [cid for cid, _ in sorted(score.items(), key=lambda x: (-x[1], x[0]))[:k]]


def query(a, b):
    return config.QUERY_TEMPLATE.format(a=a, b=b)


def retrieve_pairs(index, pairs, k=config.TOP_K, mode="hybrid", batch=256):
    cache = {}
    todo = sorted({(p["drug_a"], p["drug_b"]) for p in pairs})
    for i in range(0, len(todo), batch):
        part = todo[i:i + batch]
        hits = index.search_many([query(a, b) for a, b in part], k=k, mode=mode)
        for (a, b), h in zip(part, hits):
            cache[f"{a}|||{b}"] = h
    return cache


def passages_for(cache, a, b):
    return cache.get(f"{a}|||{b}") or cache.get(f"{b}|||{a}") or []
