import json
import random
from pathlib import Path

import numpy as np

from . import bert, config, stats
from .metrics import binary_f1

CLASS_WEIGHTS = [1.0, 2.0]
EPOCHS = 10
PATIENCE = 2
VAL_FRACTION = 0.1


def grouped_split(rows, seed, frac=VAL_FRACTION):
    groups = sorted({r["group"] for r in rows})
    for attempt in range(1000):
        rng = random.Random(f"{seed}:{attempt}")
        n_val = max(1, int(round(len(groups) * frac)))
        val_g = set(rng.sample(groups, n_val))
        val = [r for r in rows if r["group"] in val_g]
        ys = {r["y"] for r in val}
        if ys == {0, 1} and len({r["group"] for r in val if r["y"] == 1}) >= 2:
            return [r for r in rows if r["group"] not in val_g], val
    raise RuntimeError("could not draw a validation split with both classes")


def val_auroc(y, p, g):
    v = stats.stratified_auroc(np.asarray(y), np.asarray(p, float), np.asarray(g))
    if v != v:
        v = stats.auroc(np.asarray(y), np.asarray(p, float))
    return float(v)


def train_binary(train_texts, train_labels, val_texts, val_labels, val_groups, out_dir, seed, model_name,
                 revision=None, epochs=EPOCHS, lr=config.LEARNING_RATE, batch_size=config.BATCH_SIZE, class_weights=CLASS_WEIGHTS,
                 patience=PATIENCE, max_length=config.MAX_LENGTH, log=print):
    import torch
    from transformers import (AutoModelForSequenceClassification, AutoTokenizer, DataCollatorWithPadding,
                              get_linear_schedule_with_warmup)
    from .index import device
    bert.set_seed(seed)
    dev = device()
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    tok = AutoTokenizer.from_pretrained(model_name, revision=revision)
    model = AutoModelForSequenceClassification.from_pretrained(
        model_name, revision=revision, num_labels=2, id2label={0: "none", 1: "interaction"}, label2id={"none": 0, "interaction": 1}).to(dev)
    coll = DataCollatorWithPadding(tok)
    enc = bert._encode(tok, train_texts, max_length)
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
        for feats, labels in bert._batches(enc, train_labels, batch_size, True, rng):
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
        vp, vs = bert.predict(model, tok, val_texts, max_length=max_length, return_probs=True)
        va = val_auroc(val_labels, vs, val_groups)
        history.append({"epoch": epoch, "loss": total, "val_within_auroc": va, "val_binary_f1": binary_f1(val_labels, vp)})
        log(json.dumps(history[-1]))
        if va > best:
            best, best_epoch, bad = va, epoch, 0
            best_state = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}
        else:
            bad += 1
            if bad >= patience:
                break
    model.load_state_dict(best_state)
    (out_dir / "history.json").write_text(json.dumps({"best_epoch": best_epoch, "best_val_within_auroc": best,
                                                       "history": history}, indent=1))
    return model, tok
