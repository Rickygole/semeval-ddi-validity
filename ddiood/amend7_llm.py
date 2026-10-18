import numpy as np

from .amend7_prompts import BINARY, MAX_PROMPT_TOKENS, class_token_ids


class PromptTooLong(RuntimeError):
    pass


def tokenize_all(tok, texts, max_length=MAX_PROMPT_TOKENS):
    ids = [tok(t, add_special_tokens=False)["input_ids"] for t in texts]
    over = [i for i, x in enumerate(ids) if len(x) > max_length]
    if over:
        raise PromptTooLong(f"{len(over)} prompts exceed {max_length} tokens, first index {over[0]}")
    return ids


def batches_by_budget(lengths, budget):
    order = sorted(range(len(lengths)), key=lambda i: -lengths[i])
    out, cur, width = [], [], 0
    for i in order:
        w = max(width, lengths[i])
        if cur and w * (len(cur) + 1) > budget:
            out.append(cur)
            cur, w = [], lengths[i]
        cur.append(i)
        width = w
    if cur:
        out.append(cur)
    return out


def score(tok, model, texts, words, token_budget=16384, max_length=MAX_PROMPT_TOKENS, log=None):
    import torch
    ids = class_token_ids(tok, words)
    toks = tokenize_all(tok, texts, max_length)
    pad = tok.pad_token_id if tok.pad_token_id is not None else tok.eos_token_id
    flat = sorted({t for v in ids.values() for t in v})
    out = [None] * len(texts)
    dev = next(model.parameters()).device
    done = 0
    for batch in batches_by_budget([len(t) for t in toks], token_budget):
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
            lab = torch.stack([torch.logsumexp(logits[:, ids[c]], dim=-1) for c in range(len(words))], dim=1)
            q = torch.softmax(lab, dim=1)
            mass = torch.exp(torch.logsumexp(logits[:, flat], dim=-1) - lse)
        for r, i in enumerate(batch):
            out[i] = {"q": q[r].cpu().tolist(), "mass": float(mass[r]), "tokens": len(toks[i])}
        done += len(batch)
        if log:
            log(f"scored {done}/{len(texts)}")
    return out


def to_eval(scores, words):
    if words == BINARY:
        p = [s["q"][1] for s in scores]
        preds = [int(x >= 0.5) for x in p]
    else:
        p = [1 - s["q"][0] for s in scores]
        preds = [int(np.argmax(s["q"])) for s in scores]
    return {"preds": preds, "p": [round(float(x), 6) for x in p]}


def answer_stats(scores, threshold):
    mass = np.array([s["mass"] for s in scores])
    toks = np.array([s["tokens"] for s in scores])
    return {"mean_answer_mass": float(mass.mean()), "min_answer_mass": float(mass.min()),
            "non_answers": int((mass < threshold).sum()), "n": len(scores), "tokens_mean": float(toks.mean()),
            "tokens_max": int(toks.max())}
