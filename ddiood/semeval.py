import subprocess
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

from . import config


def download(dest=config.DDI_DIR):
    dest = Path(dest)
    corpus = dest / "DDICorpus"
    if corpus.exists():
        return corpus
    repo = dest / "repo"
    if not repo.exists():
        subprocess.run(["git", "clone", "-q", config.DDI_REPO, str(repo)], check=True)
    subprocess.run(["git", "-C", str(repo), "checkout", "-q", config.DDI_COMMIT], check=True)
    with zipfile.ZipFile(repo / "DDICorpus-2013.zip") as z:
        z.extractall(dest)
    return corpus


def split_files(split, corpus=None):
    corpus = Path(corpus or config.DDI_DIR / "DDICorpus")
    if split == "train":
        roots = [corpus / "Train" / "DrugBank", corpus / "Train" / "MedLine"]
    elif split == "test":
        base = corpus / "Test" / "Test for DDI Extraction task"
        roots = [base / "DrugBank", base / "MedLine"]
    else:
        raise ValueError(split)
    return [p for r in roots for p in sorted(r.glob("*.xml"))]


def load_pairs(split, corpus=None, entity_types=config.ENTITY_TYPES):
    rows = []
    for path in split_files(split, corpus):
        root = ET.parse(path).getroot()
        for sent in root.iter("sentence"):
            ents = {e.get("id"): e for e in sent.iter("entity")}
            for pair in sent.iter("pair"):
                e1, e2 = ents[pair.get("e1")], ents[pair.get("e2")]
                if e1.get("type") not in entity_types or e2.get("type") not in entity_types:
                    continue
                label = pair.get("type") if pair.get("ddi") == "true" else "false"
                rows.append({
                    "pair_id": pair.get("id"),
                    "sentence_id": sent.get("id"),
                    "source": path.parent.name,
                    "sentence": sent.get("text"),
                    "drug_a": e1.get("text").lower(),
                    "drug_b": e2.get("text").lower(),
                    "label": label,
                    "label_id": config.LABEL2ID[label],
                })
    return rows


def load_entities(split, corpus=None, entity_types=config.ENTITY_TYPES):
    counts = {}
    names = []
    for path in split_files(split, corpus):
        root = ET.parse(path).getroot()
        for ent in root.iter("entity"):
            t = ent.get("type")
            counts[t] = counts.get(t, 0) + 1
            if t in entity_types:
                names.append(ent.get("text"))
    return names, counts
