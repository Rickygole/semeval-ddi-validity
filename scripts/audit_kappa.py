import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ddiood import audit

AUDIT = ROOT / "results" / "revision" / "audit"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default=str(AUDIT))
    ap.add_argument("--annotator-1", default="annotator_1.csv")
    ap.add_argument("--annotator-2", default="annotator_2.csv")
    ap.add_argument("--boot", type=int, default=1000)
    a = ap.parse_args()
    d = Path(a.dir)
    paths = [d / a.annotator_1, d / a.annotator_2]
    missing = [p.name for p in paths if not p.exists()]
    if missing:
        raise SystemExit(f"waiting for annotation files: {', '.join(missing)} in {d}")
    rep, tier_c = audit.report(audit.read_csv(paths[0]), audit.read_csv(paths[1]), audit.read_csv(d / "answer_key.csv"),
                               a.boot)
    manifest = json.loads((d / "manifest.json").read_text())
    rep["audit_sheet_sha256"] = manifest["audit_sheet_sha256"]
    (d / "tier_c.json").write_text(json.dumps({"summary": rep, "items": tier_c}, indent=1))
    print(json.dumps(rep, indent=1))


if __name__ == "__main__":
    main()
