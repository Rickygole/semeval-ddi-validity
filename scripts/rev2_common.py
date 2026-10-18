import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from ddiood import evaluate2 as ev

OUT = ROOT / "results" / "revision" / "rev2"
CRITERIA = OUT / "criteria.json"
PANEL = ROOT / "runs" / "preds"
PREDS = ROOT / "results" / "revision" / "preds"
SEEDS = (42, 1, 2, 3, 4)
STATUS = "post hoc and descriptive; criteria in criteria.json were written before computing; changes no preregistered decision"


def require_criteria():
    if not CRITERIA.exists():
        raise SystemExit("results/revision/rev2/criteria.json must be written before this analysis runs")
    return json.loads(CRITERIA.read_text())


def load(path):
    return json.loads(Path(path).read_text())


def panel_files(panel=PANEL):
    out = []
    for path in sorted(Path(panel).glob("a7-panel-*.json")):
        r = load(path)
        if r["config"]["variant"] in ("marker", "pair"):
            out.append(r)
    return out


def write(name, obj, md):
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{name}.json").write_text(json.dumps(ev.clean(obj), indent=1) + "\n")
    (OUT / f"{name}.md").write_text(md)


def f3(v):
    if v is None or (isinstance(v, float) and v != v):
        return "NA"
    return f"{v:.3f}"


def ci(c):
    return "NA" if not c or c[0] is None else f"[{f3(c[0])}, {f3(c[1])}]"


def pct(d, lo=2.5, hi=97.5):
    d = np.asarray(d, float)
    d = d[~np.isnan(d)]
    if not len(d):
        return None
    return [float(np.percentile(d, lo)), float(np.percentile(d, hi))]


def wilson(k, n, z=1.959964):
    if not n:
        return None
    p = k / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return [float(c - h), float(c + h)]
