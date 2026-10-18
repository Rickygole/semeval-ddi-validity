import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from ddiood import evaluate2 as ev

OUT = ROOT / "results" / "revision" / "sensitivity"


def write(name, obj, md=None):
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{name}.json").write_text(json.dumps(ev.clean(obj), indent=1) + "\n")
    if md is not None:
        (OUT / f"{name}.md").write_text(md)


def f3(v):
    if v is None or v != v:
        return "NA"
    return f"{v:.3f}"


def ci(c):
    return "NA" if not c else f"[{f3(c[0])}, {f3(c[1])}]"
