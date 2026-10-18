import re
import xml.etree.ElementTree as ET

import numpy as np

from . import config, inputs, semeval

BACKBONES = [
    ("bertbase", "bert-base-uncased"),
    ("biobert", "dmis-lab/biobert-base-cased-v1.2"),
    ("biomedbert_abs", "microsoft/BiomedNLP-BiomedBERT-base-uncased-abstract"),
    ("biomedbert_full", config.ENCODER),
    ("biolinkbert", "michiyasunaga/BioLinkBERT-base"),
    ("scibert", "allenai/scibert_scivocab_uncased"),
    ("clinicalbert", "emilyalsentzer/Bio_ClinicalBERT"),
    ("roberta", "FacebookAI/roberta-base"),
    ("deberta", "microsoft/deberta-v3-base"),
    ("electra", "google/electra-base-discriminator"),
]
FORMATS = ("pair", "marker")
MASKED_BACKBONES = ("biomedbert_full", "bertbase")
EPOCHS = config.MAX_EPOCHS
SEED = config.PRIMARY_SEED
ANGLE = ("<e1>", "</e1>", "<e2>", "</e2>")
BRACKET = ("[E1]", "[/E1]", "[E2]", "[/E2]")


def spans(sentence, name):
    pat = re.compile(r"(?<![\w-])" + re.escape(name) + r"(?![\w-])", re.IGNORECASE)
    return [m.span() for m in pat.finditer(sentence)]


def _entity_span(e):
    first = e.get("charOffset").split(";")[0]
    s, t = first.split("-")
    return int(s), int(t) + 1


def load_offsets(split):
    out = {}
    for path in semeval.split_files(split):
        root = ET.parse(path).getroot()
        for sent in root.iter("sentence"):
            ents = {e.get("id"): e for e in sent.iter("entity")}
            for pair in sent.iter("pair"):
                e1, e2 = ents[pair.get("e1")], ents[pair.get("e2")]
                if e1.get("type") not in config.ENTITY_TYPES or e2.get("type") not in config.ENTITY_TYPES:
                    continue
                out[pair.get("id")] = (_entity_span(e1), _entity_span(e2))
    return out


def attach_offsets(rows, offsets):
    for r in rows:
        r["spans"] = offsets.get(r.get("pair_id"))
    return rows


def _valid_spans(sentence, a, b, sp):
    if not sp:
        return False
    (s1, t1), (s2, t2) = sp
    if t1 <= s1 or t2 <= s2 or t1 > len(sentence) or t2 > len(sentence):
        return False
    if not (t1 <= s2 or t2 <= s1):
        return False
    return sentence[s1:t1].lower() == a.lower() and sentence[s2:t2].lower() == b.lower()


def mark(sentence, a, b, tags=ANGLE, annotated=None):
    if _valid_spans(sentence, a, b, annotated):
        (s1, t1), (s2, t2) = annotated
        found = [(s1, t1, tags[0], tags[1]), (s2, t2, tags[2], tags[3])]
    else:
        found = None
        for x in spans(sentence, a):
            for y in spans(sentence, b):
                if x[1] <= y[0] or y[1] <= x[0]:
                    found = [(x[0], x[1], tags[0], tags[1]), (y[0], y[1], tags[2], tags[3])]
                    break
            if found:
                break
        if not found:
            return None
    found.sort()
    out, last = [], 0
    for s0, t0, open_tag, close_tag in found:
        out.append(sentence[last:s0] + open_tag + sentence[s0:t0] + close_tag)
        last = t0
    out.append(sentence[last:])
    return "".join(out)


def template(tags):
    return tags[0] + "{a}" + tags[1] + " and " + tags[2] + "{b}" + tags[3] + "."


def marker_names(pairs, tags=ANGLE):
    return [template(tags).format(a=p["drug_a"], b=p["drug_b"]) for p in pairs]


def marker_sentence(pairs, tags=ANGLE):
    out, ok = [], []
    for p in pairs:
        m = mark(p["sentence"], p["drug_a"], p["drug_b"], tags, p.get("spans")) if p["sentence"] else None
        ok.append(m is not None)
        out.append(m if m is not None else template(tags).format(a=p["drug_a"], b=p["drug_b"]) + " " + p["sentence"])
    return out, ok


def formats(fmt, sep="[SEP]"):
    if fmt == "pair":
        return {"sentence": lambda rows: ([(p["sentence"], f"{p['drug_a']} {sep} {p['drug_b']}") for p in rows], [True] * len(rows)),
                "names": lambda rows: [("", f"{p['drug_a']} {sep} {p['drug_b']}") for p in rows]}
    if fmt == "marker":
        return {"sentence": marker_sentence, "names": marker_names}
    if fmt == "masked":
        masked_names = f"{inputs.MASK} {sep} {inputs.MASK}"
        return {"sentence": lambda rows: ([(inputs.masked_sentence(p), masked_names) for p in rows], [True] * len(rows)),
                "names": lambda rows: [("", masked_names) for _ in rows]}
    raise ValueError(fmt)


def registry_rows():
    rows = []
    for bid, repo in BACKBONES:
        for fmt in FORMATS:
            rows.append((bid, repo, fmt))
    for bid in MASKED_BACKBONES:
        rows.append((bid, dict(BACKBONES)[bid], "masked"))
    return rows


def codes(x):
    return np.unique(np.asarray(x), return_inverse=True)[1].ravel()


def pair_structure(y, g, q):
    y = np.asarray(y)
    gc, qc = codes(g), codes(q)
    pos, neg, dr = [], [], []
    for k in np.unique(gc):
        m = np.where(gc == k)[0]
        P, N = m[y[m] == 1], m[y[m] == 0]
        if len(P) and len(N):
            pos.append(np.repeat(P, len(N)))
            neg.append(np.tile(N, len(P)))
            dr.append(np.full(len(P) * len(N), k))
    pos, neg, dr = np.concatenate(pos), np.concatenate(neg), np.concatenate(dr)
    return {"pos": pos, "neg": neg, "drug": dr, "qpos": qc[pos], "qneg": qc[neg], "k1": int(gc.max()) + 1,
            "k2": int(qc.max()) + 1}


def win_values(p, st):
    d = np.asarray(p, float)[st["pos"]] - np.asarray(p, float)[st["neg"]]
    return (d > 0) + 0.5 * (d == 0)


def spearman(x, y):
    from scipy.stats import spearmanr
    x, y = np.asarray(x, float), np.asarray(y, float)
    if np.ptp(x) == 0 or np.ptp(y) == 0:
        return float("nan")
    r = spearmanr(x, y)
    return float(r.statistic if hasattr(r, "statistic") else r[0])


def panel_stats(models, n_boot=1000, seed=42, bound=0.60):
    st = pair_structure(models[0]["y"], models[0]["groups"], models[0]["partners"])
    for m in models:
        if not (np.array_equal(m["y"], models[0]["y"]) and np.array_equal(m["groups"], models[0]["groups"])
                and np.array_equal(m["partners"], models[0]["partners"])):
            raise ValueError("panel models are scored on different rows")
    W = np.stack([win_values(m["p"], st) for m in models])
    point = W.mean(1)
    rng = np.random.RandomState(seed)
    draws = np.zeros((n_boot, len(models)))
    x = np.array([m["semeval"] for m in models], float)
    rhos = np.zeros(n_boot)
    for b in range(n_boot):
        w1 = np.bincount(rng.randint(0, st["k1"], st["k1"]), minlength=st["k1"])
        w2 = np.bincount(rng.randint(0, st["k2"], st["k2"]), minlength=st["k2"])
        w = w1[st["drug"]] * w2[st["qpos"]] * w2[st["qneg"]]
        draws[b] = (W * w).sum(1) / max(w.sum(), 1e-12)
        rhos[b] = spearman(x, draws[b])
    between = float(np.var(point, ddof=1))
    within = float(np.mean(np.var(draws, axis=0, ddof=1)))
    lo95, hi95 = np.percentile(draws, 2.5, axis=0), np.percentile(draws, 97.5, axis=0)
    ok = rhos[~np.isnan(rhos)]
    return {"names": [m["name"] for m in models], "auroc": point.tolist(), "lo95": lo95.tolist(), "hi95": hi95.tolist(),
            "upper_at_most_bound": (hi95 <= bound).tolist(), "bound": bound, "rho": spearman(x, point),
            "rho_lo95": float(np.percentile(ok, 2.5)) if len(ok) else float("nan"),
            "rho_hi95": float(np.percentile(ok, 97.5)) if len(ok) else float("nan"),
            "between_variance": between, "mean_within_bootstrap_variance": within,
            "variance_ratio": between / within if within else None, "n_models": len(models),
            "n_drugs": st["k1"], "bootstrap": "two-way over OOD drugs and partner drugs, draws shared by all models",
            "seed": seed}


EXTERNAL = [{"repo": "wesin/pubmedbert-relation-extraction", "tags": BRACKET}]
EXTERNAL_TRAIN_SAMPLE = 3000


def majority_class(pred_classes):
    from collections import Counter
    return Counter(pred_classes).most_common(1)[0][0]


def static_checks(facts):
    banned = {"tac", "tac2018", "tac-2018", "drugbank"}
    trained = {str(x).lower() for x in facts.get("train_corpora", [])}
    return {"training_data_stated": bool(trained), "no_tac_or_drugbank": bool(trained) and not (trained & banned),
            "input_format_documented": bool(facts.get("input_format_documented")),
            "label_set_has_negative": bool(facts.get("negative_label"))}


WEIGHT_PATTERNS = (["*.json", "*.txt", "*.model", "*.safetensors"], ["*.json", "*.txt", "*.model", "*.bin"])


def snapshot(repo, revision):
    from pathlib import Path
    from huggingface_hub import snapshot_download
    for patterns in WEIGHT_PATTERNS:
        path = Path(snapshot_download(repo, revision=revision, allow_patterns=patterns))
        if any(path.glob("*.safetensors")) or any(path.glob("*.bin")):
            return path
    raise RuntimeError(f"{repo}@{revision}: no PyTorch weights")


def prepare_model(repo, revision, dest, do_lower_case):
    import json
    import shutil
    from pathlib import Path
    path = snapshot(repo, revision)
    if do_lower_case is not False:
        return str(path)
    dest = Path(dest)
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(path, dest, symlinks=False)
    cfg_path = dest / "tokenizer_config.json"
    cfg = json.loads(cfg_path.read_text()) if cfg_path.exists() else {}
    cfg["do_lower_case"] = False
    cfg_path.write_text(json.dumps(cfg))
    return str(dest)
