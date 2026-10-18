import json
import random
from pathlib import Path

import numpy as np

from . import config
from .metrics import binary_f1, macro_f1, per_class_f1


def set_seed(seed):
    import torch
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def split_train_val(rows, seed, frac=config.VAL_FRACTION):
    by = {}
    for i, r in enumerate(rows):
        by.setdefault(r["label_id"], []).append(i)
    rng = random.Random(seed)
    val = set()
    for idx in by.values():
        idx = idx[:]
        rng.shuffle(idx)
        val.update(idx[:max(1, int(len(idx) * frac))])
    return [r for i, r in enumerate(rows) if i not in val], [r for i, r in enumerate(rows) if i in val]


def _encode(tok, texts, max_length):
    if texts and isinstance(texts[0], tuple):
        a, b = zip(*texts)
        return tok(list(a), list(b), truncation=True, max_length=max_length)
    return tok(list(texts), truncation=True, max_length=max_length)


def _batches(enc, labels, batch_size, shuffle, rng):
    order = list(range(len(enc["input_ids"])))
    if shuffle:
        rng.shuffle(order)
    for i in range(0, len(order), batch_size):
        ids = order[i:i + batch_size]
        feats = [{k: enc[k][j] for k in enc} for j in ids]
        yield feats, [labels[j] for j in ids] if labels is not None else None


def predict(model, tok, texts, batch_size=64, max_length=config.MAX_LENGTH, return_probs=False):
    import torch
    from transformers import DataCollatorWithPadding
    if not texts:
        return ([], []) if return_probs else []
    dev = next(model.parameters()).device
    coll = DataCollatorWithPadding(tok)
    enc = _encode(tok, texts, max_length)
    model.eval()
    out, probs = [], []
    for feats, _ in _batches(enc, None, batch_size, False, None):
        b = {k: v.to(dev) for k, v in coll(feats).items()}
        with torch.no_grad():
            p = torch.softmax(model(**b).logits.float(), -1)
        out.extend(p.argmax(-1).cpu().tolist())
        probs.extend((1 - p[:, 0]).cpu().tolist())
    return (out, probs) if return_probs else out

def train(train_texts, train_labels, val_texts, val_labels, out_dir, seed,
          model_name=config.ENCODER, epochs=config.MAX_EPOCHS, lr=config.LEARNING_RATE,
          batch_size=config.BATCH_SIZE, class_weights=config.CLASS_WEIGHTS, patience=2,
          max_length=config.MAX_LENGTH, save_model=False, log=print):
    import torch
    from transformers import (AutoModelForSequenceClassification, AutoTokenizer, DataCollatorWithPadding,
                              get_linear_schedule_with_warmup)
    from .index import device
    set_seed(seed)
    dev = device()
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    tok = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(
        model_name, num_labels=len(config.LABELS), id2label=config.ID2LABEL, label2id=config.LABEL2ID,
        torch_dtype=torch.float32).to(dev)
    coll = DataCollatorWithPadding(tok)
    enc = _encode(tok, train_texts, max_length)
    steps = epochs * ((len(train_labels) + batch_size - 1) // batch_size)
    opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=config.WEIGHT_DECAY)
    sched = get_linear_schedule_with_warmup(opt, int(config.WARMUP_FRACTION * steps), steps)
    loss_fn = torch.nn.CrossEntropyLoss(weight=torch.tensor(class_weights, dtype=torch.float, device=dev))
    use_amp = dev == "cuda"
    scaler = torch.amp.GradScaler("cuda", enabled=use_amp)
    rng = random.Random(seed)
    best, best_epoch, best_state, bad, history = -1.0, 0, None, 0, []
    for epoch in range(1, epochs + 1):
        model.train()
        total = 0.0
        for feats, labels in _batches(enc, train_labels, batch_size, True, rng):
            b = {k: v.to(dev) for k, v in coll(feats).items()}
            y = torch.tensor(labels, device=dev)
            with torch.autocast(device_type="cuda", dtype=torch.float16, enabled=use_amp):
                loss = loss_fn(model(**b).logits.float(), y)
            opt.zero_grad()
            scaler.scale(loss).backward()
            scaler.unscale_(opt)
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            scaler.step(opt)
            scaler.update()
            sched.step()
            total += loss.item()
        vp = predict(model, tok, val_texts, max_length=max_length)
        vm = macro_f1(val_labels, vp)
        history.append({"epoch": epoch, "loss": total, "val_macro_f1": vm, "val_binary_f1": binary_f1(val_labels, vp)})
        log(json.dumps(history[-1]))
        if vm > best:
            best, best_epoch, bad = vm, epoch, 0
            best_state = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}
        else:
            bad += 1
            if bad >= patience:
                break
    model.load_state_dict(best_state)
    if save_model:
        model.save_pretrained(out_dir / "model")
        tok.save_pretrained(out_dir / "model")
    (out_dir / "history.json").write_text(json.dumps({"best_epoch": best_epoch, "best_val_macro_f1": best,
                                                       "history": history}, indent=1))
    return model, tok


def evaluate(model, tok, texts, labels):
    p = predict(model, tok, texts)
    return p, {"macro_f1": round(macro_f1(labels, p), 4), "binary_f1": round(binary_f1(labels, p), 4),
               "per_class_f1": per_class_f1(labels, p, config.LABELS)}
