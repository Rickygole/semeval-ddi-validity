import hashlib
import json
import random
import re

import numpy as np

from . import amend7_llm as al
from . import amend7_prompts as pr

OLMO = "allenai/OLMo-2-1124-7B-Instruct"
OLMO_REVISION = "470b1fba1ae01581f270116362ee4aa1b97f4c84"
OLMO_LICENSE = "apache-2.0"
WORDS = ["no", "yes", "unsure"]
SAMPLE_SEED = 17
SAMPLE_PLAN = (("older", 1, 75), ("older", 0, 75), ("novel", 1, 50), ("novel", 0, 50))
MAX_PROMPT_TOKENS = 4000
NON_ANSWER_MASS = 0.5
EXPECTED_ITEMS_SHA256 = "2f4410cb00e0a8bb3b098493e4a5d15460e2d1f3da2112bac44a6a4f96097cf4"
EXPECTED_PROMPT_SHA256 = "eade2527898604e24481e235a7ea17e73a23fa64b05e823fb18edda0f6a29d93"
CHUNK_RULE = "sentence-boundary chunks that fit the context; the item takes the chunk with the highest probability of yes"

PROMPT = """Read the Drug Interactions section of a drug label and answer one question about it, using only the text below.

Drug Interactions section for {drug}:
{section}

Question: Does this section state a clinically relevant interaction between {drug} and {partner}? Answer with one word only: yes, no or unsure.

Answer:"""


def prompt_sha256():
    blob = json.dumps({"prompt": PROMPT, "words": WORDS, "max": MAX_PROMPT_TOKENS, "mass": NON_ANSWER_MASS,
                       "chunk": CHUNK_RULE, "model": OLMO, "revision": OLMO_REVISION, "role": pr.CHAT_ROLE}, sort_keys=True)
    return hashlib.sha256(blob.encode()).hexdigest()


def items_sha256(items):
    return hashlib.sha256(json.dumps(items, sort_keys=True).encode()).hexdigest()


def assert_frozen(items):
    got = items_sha256(items)
    if got != EXPECTED_ITEMS_SHA256:
        raise RuntimeError(f"item list sha256 {got} differs from the frozen {EXPECTED_ITEMS_SHA256}")
    got = prompt_sha256()
    if got != EXPECTED_PROMPT_SHA256:
        raise RuntimeError(f"prompt sha256 {got} differs from the frozen {EXPECTED_PROMPT_SHA256}")


def build_prompt(drug, section, partner):
    return PROMPT.format(drug=drug, section=section, partner=partner)


def audit_items(sheet):
    out = []
    for r in sheet:
        out.append({"item_id": r["item_id"], "set": "audit", "cohort": r["cohort"], "ood_drug": r["ood_drug"],
                    "partner": r["partner"], "current_label": int(r["current_label"])})
    if len(out) != len({x["item_id"] for x in out}):
        raise ValueError("duplicate audit item ids")
    return out


def random_items(ood_rows, old_rows, excluded, seed=SAMPLE_SEED):
    pools = {"novel": ood_rows, "older": [r for r in old_rows if r["drug_a"] not in excluded]}
    rng = random.Random(seed)
    out = []
    for cohort, y, n in SAMPLE_PLAN:
        cand = [r for r in pools[cohort] if r["y"] == y]
        if len(cand) < n:
            raise ValueError(f"{cohort} class {y} has {len(cand)} pairs, fewer than {n}")
        for r in rng.sample(cand, n):
            out.append({"set": "random", "cohort": cohort, "ood_drug": r["drug_a"], "partner": r["drug_b"],
                        "current_label": int(r["y"])})
    for i, x in enumerate(out, 1):
        x["item_id"] = f"S{i:03d}"
    return out


def all_items(sheet, ood_rows, old_rows, excluded, seed=SAMPLE_SEED):
    return audit_items(sheet) + random_items(ood_rows, old_rows, excluded, seed)


def unique_keys(items):
    seen, keys = set(), []
    for x in items:
        k = (x["ood_drug"], x["partner"])
        if k not in seen:
            seen.add(k)
            keys.append(k)
    return keys


def n_tokens(tok, text):
    return len(tok(text, add_special_tokens=False)["input_ids"])


def split_sentences(text):
    return [s for s in re.split(r"(?<=[.!?])\s+", text) if s]


def fit_chunks(tok, drug, section, partner, limit=MAX_PROMPT_TOKENS):
    def prompt_len(sec):
        return n_tokens(tok, pr.chat(tok, build_prompt(drug, sec, partner)))

    if prompt_len(section) <= limit:
        return [section]
    overhead = prompt_len("")
    budget = limit - overhead - 8
    while budget > 16:
        chunks, cur, used = [], [], 0
        for s in split_sentences(section):
            ids = tok(s, add_special_tokens=False)["input_ids"]
            if len(ids) > budget:
                if cur:
                    chunks.append(" ".join(cur))
                    cur, used = [], 0
                for i in range(0, len(ids), budget):
                    chunks.append(tok.decode(ids[i:i + budget]))
                continue
            if used + len(ids) + 1 > budget and cur:
                chunks.append(" ".join(cur))
                cur, used = [], 0
            cur.append(s)
            used += len(ids) + 1
        if cur:
            chunks.append(" ".join(cur))
        if all(prompt_len(c) <= limit for c in chunks):
            return chunks
        budget = int(budget * 0.95)
    raise RuntimeError(f"could not fit the section of {drug} into {limit} tokens")


def label_ids(tok, words=WORDS):
    ids = {}
    for i, w in enumerate(words):
        cands = set()
        for form in pr.case_forms(w):
            enc = tok(form, add_special_tokens=False)["input_ids"]
            if enc:
                cands.add(enc[0])
        ids[i] = sorted(cands)
    flat = [t for v in ids.values() for t in v]
    if len(flat) != len(set(flat)):
        raise RuntimeError(f"label first tokens collide: {ids}")
    return ids


def score(tok, model, texts, ids, token_budget=16384, max_length=MAX_PROMPT_TOKENS + 64, log=None):
    import torch
    toks = al.tokenize_all(tok, texts, max_length)
    pad = tok.pad_token_id if tok.pad_token_id is not None else tok.eos_token_id
    flat = sorted({t for v in ids.values() for t in v})
    out = [None] * len(texts)
    dev = next(model.parameters()).device
    done = 0
    for batch in al.batches_by_budget([len(t) for t in toks], token_budget):
        width = max(len(toks[i]) for i in batch)
        x = torch.full((len(batch), width), pad, dtype=torch.long)
        m = torch.zeros((len(batch), width), dtype=torch.long)
        for r, i in enumerate(batch):
            x[r, width - len(toks[i]):] = torch.tensor(toks[i])
            m[r, width - len(toks[i]):] = 1
        pos = (m.cumsum(-1) - 1).clamp(min=0)
        x, m, pos = x.to(dev), m.to(dev), pos.to(dev)
        with torch.no_grad():
            try:
                logits = model(input_ids=x, attention_mask=m, position_ids=pos, logits_to_keep=1,
                               use_cache=False).logits[:, -1, :]
            except TypeError:
                logits = model(input_ids=x, attention_mask=m, position_ids=pos, use_cache=False).logits[:, -1, :]
            logits = logits.float()
            lse = torch.logsumexp(logits, dim=-1)
            lab = torch.stack([torch.logsumexp(logits[:, ids[c]], dim=-1) for c in range(len(ids))], dim=1)
            q = torch.softmax(lab, dim=1)
            mass = torch.exp(torch.logsumexp(logits[:, flat], dim=-1) - lse)
        for r, i in enumerate(batch):
            out[i] = {"q": q[r].cpu().tolist(), "mass": float(mass[r]), "tokens": len(toks[i])}
        done += len(batch)
        if log:
            log(f"scored {done}/{len(texts)}")
    return out


def decide(q):
    return WORDS[int(np.argmax(q))]


def adjudicate(tok, model, items, sections, log=None):
    keys = unique_keys(items)
    texts, owner, n_chunks = [], [], {}
    for k, (drug, partner) in enumerate(keys):
        if drug not in sections:
            raise KeyError(f"no Drug Interactions section for {drug}")
        chunks = fit_chunks(tok, drug, sections[drug]["text"], partner)
        n_chunks[k] = len(chunks)
        for c in chunks:
            texts.append(pr.chat(tok, build_prompt(drug, c, partner)))
            owner.append(k)
    scores = score(tok, model, texts, label_ids(tok), log=log)
    best = {}
    for s, k in zip(scores, owner):
        if k not in best or s["q"][1] > best[k]["q"][1]:
            best[k] = s
    by_key = {keys[k]: {**best[k], "n_chunks": n_chunks[k]} for k in best}
    out = []
    for x in items:
        s = by_key[(x["ood_drug"], x["partner"])]
        out.append({**x, "q_no": round(s["q"][0], 6), "q_yes": round(s["q"][1], 6), "q_unsure": round(s["q"][2], 6),
                    "decision": decide(s["q"]), "mass": round(s["mass"], 6), "tokens": s["tokens"],
                    "n_chunks": s["n_chunks"], "non_answer": bool(s["mass"] < NON_ANSWER_MASS)})
    return out, scores, len(keys)


def load_olmo(revision=OLMO_REVISION):
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
    q = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4", bnb_4bit_compute_dtype=torch.bfloat16,
                           bnb_4bit_use_double_quant=True)
    tok = AutoTokenizer.from_pretrained(OLMO, revision=revision)
    model = AutoModelForCausalLM.from_pretrained(OLMO, revision=revision, quantization_config=q, torch_dtype=torch.bfloat16,
                                                 device_map="auto").eval()
    return tok, model


def load_tiny(path):
    from transformers import AutoModelForCausalLM, AutoTokenizer
    return AutoTokenizer.from_pretrained(path), AutoModelForCausalLM.from_pretrained(path).eval()
