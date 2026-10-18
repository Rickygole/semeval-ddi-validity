import json
import time
from pathlib import Path

import requests

BASE = "https://rxnav.nlm.nih.gov/REST"
ACCEPTED_TTY = ["IN", "PIN", "MIN"]


def _get(url, params=None, retries=5, sleep=0.2):
    wait = 5
    for _ in range(retries):
        try:
            time.sleep(sleep)
            r = requests.get(url, params=params, timeout=20)
            if r.status_code == 200:
                return r.json()
            if r.status_code == 429:
                time.sleep(wait)
                wait = min(wait * 2, 40)
                continue
            return None
        except requests.RequestException:
            time.sleep(wait)
            wait = min(wait * 2, 40)
    return None


def lookup(name):
    data = _get(f"{BASE}/rxcui.json", {"name": name, "search": 2})
    ids = ((data or {}).get("idGroup") or {}).get("rxnormId") or []
    best = None
    for rxcui in ids:
        props = _get(f"{BASE}/rxcui/{rxcui}/properties.json")
        tty = ((props or {}).get("properties") or {}).get("tty")
        if tty in ACCEPTED_TTY:
            rank = ACCEPTED_TTY.index(tty)
            if best is None or rank < best[2]:
                best = (rxcui, tty, rank)
    if best is None:
        return {"rxcui": None, "tty": None, "status": "no_accepted_tty" if ids else "not_found"}
    return {"rxcui": best[0], "tty": best[1], "status": "ok"}


class CachedRxNorm:
    def __init__(self, path, flush_every=50):
        self.path = Path(path)
        self.flush_every = flush_every
        self.cache = json.loads(self.path.read_text()) if self.path.exists() else {}
        self._dirty = 0

    def __call__(self, name):
        if name not in self.cache:
            self.cache[name] = lookup(name)
            self._dirty += 1
            if self._dirty >= self.flush_every:
                self.flush()
        return self.cache[name]

    def prefetch(self, names, workers=8):
        from concurrent.futures import ThreadPoolExecutor
        todo = sorted({n for n in names if n and n not in self.cache})
        with ThreadPoolExecutor(workers) as ex:
            for name, hit in zip(todo, ex.map(lookup, todo)):
                self.cache[name] = hit
        self.flush()

    def flush(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self.cache, indent=1, sort_keys=True))
        self._dirty = 0
