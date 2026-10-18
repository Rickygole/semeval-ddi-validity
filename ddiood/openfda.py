import json
import time
from pathlib import Path

import requests

from . import config

URL = "https://api.fda.gov/drug/label.json"
BACKOFF = [5, 10, 20, 40, 40]


def _query(field, name, sleep):
    params = {"search": f'{field}:"{name}"', "limit": 1}
    for attempt in range(5):
        try:
            time.sleep(sleep)
            r = requests.get(URL, params=params, timeout=20)
            if r.status_code == 200:
                res = r.json().get("results") or []
                return res[0] if res else None
            if r.status_code == 404:
                return None
            if r.status_code == 429:
                time.sleep(BACKOFF[attempt])
                continue
            return None
        except requests.RequestException:
            time.sleep(BACKOFF[attempt])
    return None


def fetch(name, sleep=0.5, fields=("openfda.generic_name",)):
    for field in fields:
        res = _query(field, name, sleep)
        if res:
            return res
    return None


def section_text(label, section):
    if not label or section not in label:
        return ""
    v = label[section]
    return v[0] if isinstance(v, list) else v


class LabelStore:
    def __init__(self, root=config.FDA_LABEL_DIR, offline=False):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.offline = offline

    def path(self, name):
        return self.root / (name.replace("/", "_") + ".json")

    def get(self, name, fields=("openfda.generic_name",)):
        p = self.path(name)
        if p.exists():
            return json.loads(p.read_text()).get("label")
        if self.offline:
            return None
        label = fetch(name, fields=fields)
        p.write_text(json.dumps({"query": name, "fields": list(fields),
                                 "retrieved": time.strftime("%Y-%m-%d"), "label": label}))
        return label

    def prefetch(self, names, fields=("openfda.generic_name",), workers=4):
        from concurrent.futures import ThreadPoolExecutor
        todo = sorted({n for n in names if not self.path(n).exists()})
        with ThreadPoolExecutor(workers) as ex:
            list(ex.map(lambda n: self.get(n, fields=fields), todo))
