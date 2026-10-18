import hashlib
import os
import shutil
from pathlib import Path

import numpy as np

from . import amend7_panel as pn
from . import bert, config, inputs

FAMILIES = ("b2mixed", "b2sentence", "marker")
SEEDS = [42, 1, 2, 3, 4]
CHECK_ROWS = 32


def _pred(model, tok, texts):
    p, s = bert.predict(model, tok, texts, return_probs=True)
    return {"preds": p, "p": [round(x, 6) for x in s]}


def _sub(rows, idx):
    return [rows[i] for i in idx]


def train_texts(family, tr, va):
    y_va = [r["label_id"] for r in va]
    if family == "b2mixed":
        f_tr, y_tr = inputs.mixed_training(tr)
        return f_tr, y_tr, inputs.b2_sentence(va), y_va
    if family == "b2sentence":
        return inputs.b2_sentence(tr), [r["label_id"] for r in tr], inputs.b2_sentence(va), y_va
    if family == "marker":
        f_tr, ok_tr = pn.marker_sentence(tr)
        f_va, _ = pn.marker_sentence(va)
        return f_tr, [r["label_id"] for r in tr], f_va, y_va
    raise ValueError(family)


def eval_b2(model, tok, inp, train_pairs):
    ev = {}
    sent_idx = [i for i, p in enumerate(inp.ood) if p["sentence"]]
    old_idx = [i for i, p in enumerate(inp.ood_old) if p["sentence"]]
    ev["test_sentence"] = _pred(model, tok, inputs.b2_sentence(inp.test))
    ev["test_masked"] = _pred(model, tok, inputs.b2_masked(inp.test))
    ev["test_empty"] = _pred(model, tok, inputs.b2_empty(inp.test))
    ev["test_names"] = _pred(model, tok, inputs.b1(inp.test))
    ev["ood_empty"] = _pred(model, tok, inputs.b2_empty(inp.ood))
    ev["ood_names"] = _pred(model, tok, inputs.b1(inp.ood))
    ev["ood_sentence"] = {**_pred(model, tok, inputs.b2_sentence(_sub(inp.ood, sent_idx))), "index": sent_idx}
    ev["ood_swap_sentence"] = {**_pred(model, tok, inputs.b2_sentence(inp.ood_swap)), "y": [p["y"] for p in inp.ood_swap]}
    ev["oodold_empty"] = _pred(model, tok, inputs.b2_empty(inp.ood_old))
    ev["oodold_sentence"] = {**_pred(model, tok, inputs.b2_sentence(_sub(inp.ood_old, old_idx))), "index": old_idx}
    for k, rows in inp.swaps.items():
        ev[f"swap_{k}_sentence"] = _pred(model, tok, inputs.b2_sentence(rows))
    ev["train_empty"] = _pred(model, tok, inputs.b2_empty(train_pairs))
    ev["train_names"] = _pred(model, tok, inputs.b1(train_pairs))
    return ev


def eval_marker(model, tok, inp, train_pairs):
    ev = {}
    t_sent, t_ok = pn.marker_sentence(inp.test)
    ev["test_sentence"] = _pred(model, tok, t_sent)
    ev["test_empty"] = _pred(model, tok, pn.marker_names(inp.test))
    ev["ood_empty"] = _pred(model, tok, pn.marker_names(inp.ood))
    ev["oodold_empty"] = _pred(model, tok, pn.marker_names(inp.ood_old))
    for key, rows in (("ood_sentence", inp.ood), ("oodold_sentence", inp.ood_old)):
        s, ok = pn.marker_sentence(rows)
        idx = [i for i, p in enumerate(rows) if p["sentence"] and ok[i]]
        ev[key] = {**_pred(model, tok, [s[i] for i in idx]), "index": idx}
    ev["train_empty"] = _pred(model, tok, pn.marker_names(train_pairs))
    return ev, int(len(t_ok) - sum(t_ok))


def file_sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def save_weights(src, dest):
    src, dest = Path(src), Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_name(f"{dest.name}.{os.getpid()}.tmp")
    if tmp.exists():
        shutil.rmtree(tmp)
    try:
        shutil.copytree(src, tmp)
        if dest.exists():
            shutil.rmtree(dest)
        os.replace(tmp, dest)
    except BaseException:
        shutil.rmtree(tmp, ignore_errors=True)
        raise
    return dest


def check_reload(dest, model, tok, texts):
    from transformers import AutoModelForSequenceClassification, AutoTokenizer
    from .index import device
    again = AutoModelForSequenceClassification.from_pretrained(dest).to(device()).eval()
    tok2 = AutoTokenizer.from_pretrained(dest)
    a = np.array(bert.predict(model, tok, texts, return_probs=True)[1])
    b = np.array(bert.predict(again, tok2, texts, return_probs=True)[1])
    gap = float(np.abs(a - b).max()) if len(a) else 0.0
    del again
    if gap > 1e-4:
        raise RuntimeError(f"saved weights do not reproduce the in-memory model: max gap {gap}")
    weight_files = sorted(Path(dest).glob("*.safetensors")) + sorted(Path(dest).glob("*.bin"))
    return {"reload_max_abs_gap": gap, "reload_rows": len(texts), "weight_file": weight_files[0].name,
            "weight_sha256": file_sha256(weight_files[0]), "weight_bytes": weight_files[0].stat().st_size}


def encoder_job(data, cfg, local, weights_dir, tiny=None):
    inp = data.inp
    family, seed = cfg["family"], cfg["seed"]
    if family == "marker":
        pn.attach_offsets(inp.train, pn.load_offsets("train"))
        pn.attach_offsets(inp.test, pn.load_offsets("test"))
    if tiny:
        path = tiny
    else:
        repo = config.ENCODER
        path = pn.prepare_model(repo, data.manifest["panel_revisions"][repo], Path(local) / "model_src",
                                data.manifest["panel_lowercase"].get(repo))
    tr, va = bert.split_train_val(inp.train, seed)
    f_tr, y_tr, f_va, y_va = train_texts(family, tr, va)
    model, tok = bert.train(f_tr, y_tr, f_va, y_va, Path(local) / "work", seed, model_name=path,
                            epochs=1 if data.smoke else config.MAX_EPOCHS, save_model=True)
    extra = {"model_path_revision": None if tiny else data.manifest["panel_revisions"][config.ENCODER],
             "n_train_pairs": len(data.train), "train_pairs_hash": data.manifest["train_hash"]}
    if family == "marker":
        ev, extra["marker_fallback_test"] = eval_marker(model, tok, inp, data.train)
        extra["marker_fallback_train"] = int(len(f_tr) - sum(pn.marker_sentence(tr)[1]))
        check_texts = pn.marker_sentence(inp.test)[0][:CHECK_ROWS]
    else:
        ev = eval_b2(model, tok, inp, data.train)
        check_texts = inputs.b2_sentence(inp.test)[:CHECK_ROWS]
    dest = save_weights(Path(local) / "work" / "model", Path(weights_dir) / cfg["name"])
    extra["weights"] = {"path": str(dest), **check_reload(dest, model, tok, check_texts)}
    del model
    return ev, extra
