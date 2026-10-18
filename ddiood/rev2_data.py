import csv
import gzip
import json
from pathlib import Path

from . import amend7_data as ad
from . import gpu_jobs, inputs
from .inputs import ood_as_pairs


class Rev2Data:
    def __init__(self, workdir, smoke=False, need_semeval=True):
        workdir = Path(workdir)
        self.workdir = workdir
        self.a7 = workdir / "amend7"
        self.smoke = smoke
        self.manifest = json.loads((self.a7 / "manifest.json").read_text())
        base = json.load(gzip.open(workdir / "inputs.json.gz", "rt"))
        self.ood_full = ood_as_pairs(base["ood_pairs"])
        self.old_full = ood_as_pairs(base["ood_old_pairs"])
        self.ood_hash = inputs.pairs_hash(self.ood_full)
        self.old_hash = inputs.pairs_hash(self.old_full)
        if self.ood_hash != self.manifest["ood_hash"] or self.old_hash != self.manifest["ood_old_hash"]:
            raise RuntimeError("OOD pair sets in inputs.json.gz differ from the sets the manifest was built for")
        self.train_full = [ad.Data._train_row(x) for x in ad.read_rows_csv(self.a7 / "train_pairs.csv")]
        key = [{"drug_a": x["drug_a"], "drug_b": x["drug_b"], "y": x["y"]} for x in self.train_full]
        if inputs.pairs_hash(key) != self.manifest["train_hash"]:
            raise RuntimeError("training pairs differ from the manifest")
        self.train = self.train_full[::max(len(self.train_full) // 40, 1)][:40] if smoke else self.train_full
        self.sets = json.loads((self.a7 / "primary_sets.json").read_text())
        self.excluded_older = set(self.sets["older_artifacts"]) | set(self.sets["older_missed_vocabulary_drugs"])
        self.sections = json.loads((self.a7 / "di_sections.json").read_text())
        self.inp = gpu_jobs.Inputs(workdir / "inputs.json.gz", smoke) if need_semeval else None


def read_sheet(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))
