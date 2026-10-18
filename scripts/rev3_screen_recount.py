import copy
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import post8_common as pc
import post8_screen as ps
import rev3_common as rc

DROPPED = ("n12", "n13", "n14")
OUT = ROOT / "results" / "revision" / "rev3"


def flag_counts(rows, screens):
    out = {}
    for c in ("novel", "older"):
        y = np.array([int(r["label"]) for r in rows[c]])
        f = np.array([0 if s is None else s["flag"] for s in screens[c]])
        g = [r["ood_drug"] for r in rows[c]]
        subsets = {"all": np.ones(len(y), bool)}
        if c == "older":
            sub = np.array([ps.subset(d) for d in g])
            subsets["older_clean"] = sub != "artifact"
            subsets["older_primary"] = sub == "primary"
        for name, m in subsets.items():
            pos = m & (y == 1)
            out[f"{c}/{name}"] = {"positives": int(pos.sum()), "rule_flags": int(f[pos].sum())}
    return out


def main():
    crit, rows, rule, screens = pc.screens_for_run()
    full = flag_counts(rows, screens)
    stored = json.loads((pc.OUT / "screen.json").read_text())["counts"]
    for k, v in full.items():
        if v["rule_flags"] != stored[k]["rule_flags"]:
            raise SystemExit(f"full rule does not reproduce screen.json for {k}")
    reduced = copy.deepcopy(crit)
    reduced["rule"]["noninteraction_patterns"] = [p for p in crit["rule"]["noninteraction_patterns"] if p[0] not in DROPPED]
    rule2 = pc.load_rule(reduced)
    red = flag_counts(rows, pc.screen_all(rule2, rows))
    res = {"status": "post hoc and descriptive; recount of the frozen post8 screen with the dose-adjustment patterns removed; changes no decision",
           "plan_sha256": rc.plan_sha256(), "plan_note": "not specified in docs/POSTHOC_REV3_PLAN.md; a recount requested by the round 2 red team, reported as post hoc",
           "dropped_patterns": list(DROPPED),
           "dropped_pattern_text": [p for p in crit["rule"]["noninteraction_patterns"] if p[0] in DROPPED],
           "full_rule_reproduces_screen_json": True, "full_rule": full, "without_dropped_patterns": red}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "screen_recount.json").write_text(json.dumps(res, indent=1) + "\n")
    lines = ["# Screen recount without the dose-adjustment patterns", "", res["status"] + ".", "",
             "Dropped patterns: " + ", ".join(DROPPED) + ". The full rule reproduces results/revision/post8/screen.json.", "",
             "| cohort | positives | flags, full rule | flags, without n12 to n14 |", "| --- | --- | --- | --- |"]
    for k in full:
        lines.append(f"| {k} | {full[k]['positives']} | {full[k]['rule_flags']} | {red[k]['rule_flags']} |")
    (OUT / "screen_recount.md").write_text("\n".join(lines) + "\n")
    print(OUT / "screen_recount.md")


if __name__ == "__main__":
    main()
