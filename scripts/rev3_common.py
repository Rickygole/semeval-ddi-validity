import hashlib
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from ddiood import evaluate2 as ev

PLAN = ROOT / "docs" / "POSTHOC_REV3_PLAN.md"
OUT = ROOT / "results" / "revision" / "rev3"
RUNS = ROOT / "runs" / "rev3"
STATUS = "post hoc and descriptive; plan in docs/POSTHOC_REV3_PLAN.md was written before computing; changes no preregistered decision"


def plan_sha256():
    if not PLAN.exists():
        raise SystemExit("docs/POSTHOC_REV3_PLAN.md must exist before this analysis runs")
    return hashlib.sha256(PLAN.read_bytes()).hexdigest()


def load(path):
    return json.loads(Path(path).read_text())


def write(name, obj, md):
    OUT.mkdir(parents=True, exist_ok=True)
    obj = {"plan_sha256": plan_sha256(), "status": STATUS, **obj}
    (OUT / f"{name}.json").write_text(json.dumps(ev.clean(obj), indent=1) + "\n")
    if md is not None:
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


def table(header, rows):
    out = ["| " + " | ".join(header) + " |", "| " + " | ".join("---" for _ in header) + " |"]
    out += ["| " + " | ".join(str(x) for x in r) + " |" for r in rows]
    return out
