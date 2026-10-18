import hashlib
import json
import random
import re
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

BASE = "https://bionlp.nlm.nih.gov/tac2019druginteractions/"
SOURCES = {
    "test1": {"file": "test1Files2018.zip", "bytes": 997847, "sha256": "6eeb22ed905688c10530684a5539e912247000b2b319dd9dc77fe1002203e573"},
    "test2": {"file": "test2Files2018.zip", "bytes": 489371, "sha256": "a41f350ebf9b7e12a8e9d9e0af2eb4b7bf313c680c0dac9bef16f79ea038c213"},
    "train22": {"file": "trainingFiles2018.zip", "bytes": 206595, "sha256": "bb55e63b15444b1f4eb4f7e0b0a85340995c71085f1b4987186baf7466a7e3b7"},
}
PRIMARY_SETS = ("test1", "test2")
SENSITIVITY_SETS = ("train22",)
DI_SECTION = "34073-7"
SAMPLE_SEED = 17
NEGATIVE_RATIO = 2
NO_CODE = {"", "none", "no map", "not_drug"}
UNII = re.compile(r"^[0-9A-Za-z]{10}$")
NUI = re.compile(r"^[Nn]\d{10}$")


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def fetch(dest_dir, only=None):
    dest_dir = Path(dest_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)
    out = {}
    for name, src in SOURCES.items():
        if only and name not in only:
            continue
        zpath = dest_dir / src["file"]
        if not zpath.exists():
            tmp = zpath.with_suffix(".part")
            urllib.request.urlretrieve(BASE + src["file"], tmp)
            tmp.replace(zpath)
        got = sha256_file(zpath)
        if got != src["sha256"] or zpath.stat().st_size != src["bytes"]:
            raise RuntimeError(f"{src['file']}: sha256 {got} or size {zpath.stat().st_size} differs from the recorded values")
        target = dest_dir / name
        target.mkdir(exist_ok=True)
        with zipfile.ZipFile(zpath) as z:
            for info in z.infolist():
                base = Path(info.filename).name
                if info.is_dir() or not base.endswith(".xml") or base.startswith(".") or "__MACOSX" in info.filename:
                    continue
                (target / base).write_bytes(z.read(info))
        out[name] = target
    return out


def norm(text):
    return re.sub(r"\s+", " ", (text or "").strip().lower())


def partner_type(code):
    c = (code or "").strip()
    if c.lower() in NO_CODE or NUI.match(c):
        return "class"
    return "substance" if UNII.match(c) else "class"


def parse_label(path):
    root = ET.parse(path).getroot()
    sections, di_parts = {}, []
    for s in root.iter("Section"):
        text = " ".join((s.text or "").split())
        sections.setdefault(s.get("id"), []).append(text)
        if s.get("id") == DI_SECTION:
            di_parts.append(text)
    positives = {}
    codes = set()
    for sent in root.iter("Sentence"):
        mentions = {m.get("id"): m for m in sent.iter("Mention")}
        for m in mentions.values():
            c = (m.get("code") or "").strip().lower()
            if c not in NO_CODE:
                codes.add(c)
        if sent.get("section") != DI_SECTION:
            continue
        for it in sent.iter("Interaction"):
            m = mentions.get(it.get("precipitant"))
            if m is None:
                continue
            key = norm(m.get("str"))
            if key and key not in positives:
                positives[key] = {"code": (m.get("code") or "").strip(), "type": it.get("type")}
    all_text = norm(" ".join(t for parts in sections.values() for t in parts))
    return {"drug": root.get("drug"), "setid": root.get("setid"), "di_text": " ".join(di_parts), "positives": positives,
            "codes": codes, "all_text": all_text}


def load_set(directory):
    labels = [parse_label(p) for p in sorted(Path(directory).glob("*.xml"))]
    names = [x["drug"] for x in labels]
    if len(names) != len(set(names)):
        raise RuntimeError("duplicate drug names within a TAC set")
    return labels


def build_set_items(set_name, labels, seed=SAMPLE_SEED, ratio=NEGATIVE_RATIO):
    labels = sorted([x for x in labels if x["di_text"]], key=lambda x: x["drug"])
    gold = {(x["drug"], k) for x in labels for k in x["positives"]}
    items = []
    for x in labels:
        for k in sorted(x["positives"]):
            p = x["positives"][k]
            items.append({"set": set_name, "ood_drug": x["drug"], "partner": k, "gold": 1, "partner_type": partner_type(p["code"]),
                          "label_setid": x["setid"], "interaction_type": p["type"]})
    taken = set()
    positives = [i for i in items if i["gold"] == 1]
    by_name = {x["drug"]: x for x in labels}
    for pos in positives:
        k = pos["partner"]
        code = by_name[pos["ood_drug"]]["positives"][k]["code"].strip().lower()
        ok = []
        for d in labels:
            if d["drug"] == pos["ood_drug"] or (d["drug"], k) in taken or (d["drug"], k) in gold:
                continue
            if norm(d["drug"]) == k or k in d["all_text"]:
                continue
            if code not in NO_CODE and code in d["codes"]:
                continue
            ok.append(d["drug"])
        rng = random.Random(f"{seed}:{pos['ood_drug']}:{k}")
        for name in rng.sample(ok, min(ratio, len(ok))):
            taken.add((name, k))
            items.append({"set": set_name, "ood_drug": name, "partner": k, "gold": 0, "partner_type": pos["partner_type"],
                          "label_setid": by_name[name]["setid"], "interaction_type": ""})
    for n, it in enumerate(items, 1):
        it["item_id"] = f"{set_name}-{n:05d}"
    sections = {x["drug"]: {"text": x["di_text"]} for x in labels}
    return items, sections


def build_all(directories, seed=SAMPLE_SEED, ratio=NEGATIVE_RATIO):
    items, sections = [], {}
    for name in PRIMARY_SETS + SENSITIVITY_SETS:
        if name not in directories:
            continue
        its, sec = build_set_items(name, load_set(directories[name]), seed, ratio)
        items += its
        sections[name] = sec
    return items, sections


def items_sha256(items):
    return hashlib.sha256(json.dumps(items, sort_keys=True).encode()).hexdigest()


def summary(items):
    out = {}
    for s in sorted({i["set"] for i in items}):
        sub = [i for i in items if i["set"] == s]
        out[s] = {"items": len(sub), "gold_positive": sum(i["gold"] for i in sub), "gold_negative": sum(1 - i["gold"] for i in sub),
                  "substance_positive": sum(i["gold"] and i["partner_type"] == "substance" for i in sub),
                  "class_positive": sum(i["gold"] and i["partner_type"] == "class" for i in sub),
                  "substance_negative": sum((not i["gold"]) and i["partner_type"] == "substance" for i in sub),
                  "class_negative": sum((not i["gold"]) and i["partner_type"] == "class" for i in sub),
                  "labels": len({i["ood_drug"] for i in sub}), "unique_prompts": len({(i["ood_drug"], i["partner"]) for i in sub})}
    return out
