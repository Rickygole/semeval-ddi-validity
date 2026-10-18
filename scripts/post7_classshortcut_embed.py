import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from post7_classshortcut_atc import OUT, needed_names

MODEL = "microsoft/BiomedNLP-BiomedBERT-base-uncased-abstract-fulltext"


def embed(names, batch=64):
    import torch
    from transformers import AutoModel, AutoTokenizer
    tok = AutoTokenizer.from_pretrained(MODEL, local_files_only=True)
    model = AutoModel.from_pretrained(MODEL, local_files_only=True).eval()
    vecs = []
    with torch.no_grad():
        for i in range(0, len(names), batch):
            enc = tok(names[i:i + batch], padding=True, truncation=True, max_length=32, return_tensors="pt")
            h = model(**enc).last_hidden_state
            m = enc["attention_mask"].clone()
            m[:, 0] = 0
            lengths = enc["attention_mask"].sum(1) - 1
            m[torch.arange(len(m)), lengths] = 0
            m = m.unsqueeze(-1).float()
            vecs.append(((h * m).sum(1) / m.sum(1).clamp(min=1)).numpy())
    v = np.vstack(vecs)
    return v / np.linalg.norm(v, axis=1, keepdims=True)


def main():
    names = needed_names()
    v = embed(names)
    OUT.mkdir(parents=True, exist_ok=True)
    np.save(OUT / "name_embeddings.npy", v.astype(np.float32))
    (OUT / "name_embeddings_index.json").write_text(json.dumps({"model": MODEL, "pooling": "mean of last layer over name tokens, CLS and SEP excluded", "names": names}, indent=1) + "\n")
    print(v.shape)


if __name__ == "__main__":
    main()
