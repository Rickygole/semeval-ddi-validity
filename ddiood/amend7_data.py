import csv
import gzip
import hashlib
import json
from pathlib import Path

from . import amend7_inputs as ai
from . import inputs, semeval
from .inputs import ood_as_pairs

CORRECTED_HASH = "8ff6794627912f5bbeb0d35f26beefdd39ebc51141fad88e13cbf9c94134155b"


def merge_corrected(inputs_gz, delta_gz):
    b = json.load(gzip.open(inputs_gz, "rt"))
    d = json.loads(gzip.open(delta_gz, "rt").read())
    for v, ch in d["retrieval"].items():
        b["retrieval"][v].update(ch)
    for v, ks in d["drop_retrieval"].items():
        for k in ks:
            b["retrieval"][v].pop(k, None)
    b["chunk_text"].update(d["chunk_text"])
    for k in d["drop_chunks"]:
        b["chunk_text"].pop(k, None)
    h = hashlib.sha256(json.dumps({"retrieval": b["retrieval"], "chunk_text": b["chunk_text"]},
                                  sort_keys=True).encode()).hexdigest()
    if h != CORRECTED_HASH:
        raise RuntimeError(f"corrected bundle hash mismatch: {h}")
    with gzip.open(inputs_gz, "wt") as f:
        json.dump(b, f)
    return h


def read_rows_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


class Data:
    def __init__(self, workdir, smoke=False, need_semeval=True):
        workdir = Path(workdir)
        a7 = workdir / "amend7"
        self.a7 = a7
        self.smoke = smoke
        self.manifest = json.loads((a7 / "manifest.json").read_text())
        base = json.load(gzip.open(workdir / "inputs.json.gz", "rt"))
        h = hashlib.sha256(json.dumps({"retrieval": base["retrieval"], "chunk_text": base["chunk_text"]},
                                      sort_keys=True).encode()).hexdigest()
        if h != CORRECTED_HASH:
            raise RuntimeError("inputs.json.gz is not the corrected bundle; run the merge step first")
        self.ood_full = ood_as_pairs(base["ood_pairs"])
        self.old_full = ood_as_pairs(base["ood_old_pairs"])
        self.ood_hash = inputs.pairs_hash(self.ood_full)
        self.old_hash = inputs.pairs_hash(self.old_full)
        if self.ood_hash != self.manifest["ood_hash"] or self.old_hash != self.manifest["ood_old_hash"]:
            raise RuntimeError("OOD pair sets in inputs.json.gz differ from the sets the bundle was built for")
        r = json.loads((a7 / "retrieval.json").read_text())
        self.new_retrieval = r["retrieval"]
        self.chunk_text = {**base["chunk_text"], **r["chunk_text"]}
        self.chunk_meta = r["chunk_meta"]
        self.base_retrieval = {"contaminated": base["retrieval"]["contaminated"], "clean": base["retrieval"]["hybrid"]}
        self.lookup = json.loads((a7 / "lookup.json").read_text())
        self.train_full = [self._train_row(x) for x in read_rows_csv(a7 / "train_pairs.csv")]
        if inputs.pairs_hash([{"drug_a": x["drug_a"], "drug_b": x["drug_b"], "y": x["y"]} for x in self.train_full]) \
                != self.manifest["train_hash"]:
            raise RuntimeError("training pairs differ from the manifest")
        self.train_semeval = self.test = None
        if need_semeval:
            semeval.download()
            from . import amend7_panel as pn
            self.train_semeval = pn.attach_offsets(semeval.load_pairs("train"), pn.load_offsets("train"))
            self.test = pn.attach_offsets(semeval.load_pairs("test"), pn.load_offsets("test"))
            self.semeval_test_full = self.test
        self.train, self.ood, self.ood_old = self.train_full, self.ood_full, self.old_full
        if smoke:
            self.train = self.train_full[::max(len(self.train_full) // 40, 1)][:40]
            self.ood, self.ood_old = self.ood_full[::22][:20], self.old_full[::97][:20]
            if self.test:
                self.test = self.test[::140][:20]
                self.train_semeval = self.train_semeval[::700][:20]
        self.fixed = ai.FixedBuilder(self.lookup, self.chunk_text, self.chunk_meta)
        self.coverage = self.assert_coverage()
        self.sets = json.loads((a7 / "primary_sets.json").read_text())

    @staticmethod
    def _train_row(x):
        y = int(x["y"])
        return {"drug_a": x["drug_a"], "drug_b": x["drug_b"], "y": y, "label_id": y, "group": x["drug_a"],
                "sentence": x["cooccurrence_sentence"]}

    def assert_coverage(self):
        groups = {"train": self.train_full, "novel": self.ood_full, "older": self.old_full}
        if self.test is not None:
            groups["test"] = self.semeval_test_full
        report = {}
        for g, rows in groups.items():
            keys = {f"{r['drug_a']}|||{r['drug_b']}" for r in rows}
            for arm in ("contaminated", "clean", "other", "ownlabel"):
                cache = self.cache(g, arm)
                missing = [k for k in keys if not cache.get(k)]
                if missing:
                    raise RuntimeError(f"{g}/{arm}: {len(missing)} of {len(keys)} queries have no passages")
                ids = {str(i) for k in keys for i in cache[k][:ai.K]}
                gone = [i for i in ids if i not in self.chunk_text or i not in self.chunk_meta]
                if gone:
                    raise RuntimeError(f"{g}/{arm}: {len(gone)} retrieved chunks have no text or metadata")
                report[f"{g}/{arm}"] = f"{len(keys)}/{len(keys)}"
        return report

    def cache(self, group, arm):
        if arm == "ownlabel" and group == "test":
            return self.base_retrieval["contaminated"]
        if group in ("novel", "test") and arm in ("contaminated", "clean"):
            return self.base_retrieval[arm]
        return self.new_retrieval[group][arm]

    def text_fn(self, kind, arm):
        if kind == "names":
            return lambda rows, group: inputs.b1(rows)
        if kind == "h5":
            return lambda rows, group: ai.krag_h5(rows, self.cache(group, arm), self.chunk_text)
        return lambda rows, group: self.fixed.encoder_inputs(rows, self.cache(group, arm))

    def audit(self):
        return json.loads((self.a7 / "input_audit.json").read_text())
