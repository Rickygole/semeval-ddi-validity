import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ddiood import amend7_jobs as aj

PREDS = ROOT / "results" / "revision" / "preds"
OUT = ROOT / "artifacts" / "amend7"
SEMEVAL_TRAIN = 13789
VAL = 0.1


def load(name):
    return json.loads((PREDS / f"{name}.json").read_text())


def per_sample_epoch(name, n_eval):
    r = load(name)
    epochs = len(r["history"]["history"])
    n_train = SEMEVAL_TRAIN * (1 - VAL)
    seconds = r["seconds"]
    return seconds / (n_train * epochs + n_eval / 3.0), epochs, seconds


def main():
    audit = json.loads((OUT / "input_audit.json").read_text())
    long_ref = per_sample_epoch("krag-hybrid-k5-c400-biomedbert-s42", 2810 + 438)
    short_ref = per_sample_epoch("b1names-biomedbert-s42", 2810 + 438 * 2 + 1944 + 3 * 2810)
    panel_ref = {n: per_sample_epoch(n, 2810 * 5 + 438 * 3 + 1944 * 3) for n in
                 ("b2sentence-biomedbert-s42", "b2sentence-bertbase-s42", "b2sentence-biobert-s42")}
    n_tr = audit["training"]["final_pairs"] * 0.9
    n_eval = 2810 + 438 + 1944
    est = {"reference": {"krag_c400_s_per_sample_epoch": long_ref[0], "b1names_s_per_sample_epoch": short_ref[0],
                         "panel_s_per_sample_epoch": {k: v[0] for k, v in panel_ref.items()}}, "jobs": {}}
    for j in aj.registry():
        if j["group"] == "E7":
            a = long_ref[0] if j["input"] != "names" else short_ref[0]
            lo = n_tr * 5 * a + n_eval * a / 3
            hi = n_tr * j["epochs"] * a + n_eval * a / 3
            est["jobs"][j["name"]] = {"low_s": round(lo + 30), "high_s": round(hi + 30)}
    for j in aj.registry():
        if j["group"] == "E9" and j["kind"] == "panel":
            a = sum(v[0] for v in panel_ref.values()) / len(panel_ref)
            mult = 1.6 if j["model"] == "deberta" else 1.0
            lo = SEMEVAL_TRAIN * 0.9 * 3 * a * mult + 60
            hi = SEMEVAL_TRAIN * 0.9 * j["epochs"] * a * mult + 60
            est["jobs"][j["name"]] = {"low_s": round(lo), "high_s": round(hi)}
        if j["group"] == "E9" and j["kind"] == "ext":
            est["jobs"][j["name"]] = {"low_s": 60, "high_s": 180}
    tok_rate = 13000.0
    q = audit["qwen_arms"]
    toks = {c: sum(q[c][k]["tokens_mean"] * q[c][k]["n"] for k in ("novel", "older")) for c in q}
    names_tokens = 5 * 2382 * 170
    stem_tokens = 2 * 1100 * 170
    for j in aj.registry():
        if j["group"] != "E8":
            continue
        t = {"names": names_tokens, "stem_preserved": stem_tokens / 2, "stem_scrambled": stem_tokens / 2}.get(j["variant"])
        t = toks[j["variant"]] if t is None else t
        est["jobs"][j["name"]] = {"tokens": round(t), "low_s": round(t / tok_rate), "high_s": round(t / 5000.0)}
    est["notebooks"] = {}
    for nb, names in aj.notebook_jobs().items():
        lo = sum(est["jobs"][n]["low_s"] for n in names)
        hi = sum(est["jobs"][n]["high_s"] for n in names)
        if nb.startswith("E8"):
            lo, hi = lo + 180, hi + 420
        est["notebooks"][nb] = {"jobs": len(names), "low_h": round(lo / 3600, 2), "high_h": round(hi / 3600, 2)}
    for g in ("E7", "E8", "E9"):
        sel = [v for k, v in est["notebooks"].items() if k.startswith(g)]
        est[g] = {"jobs": sum(v["jobs"] for v in sel), "low_h": round(sum(v["low_h"] for v in sel), 2),
                  "high_h": round(sum(v["high_h"] for v in sel), 2), "notebooks": len(sel)}
    (OUT / "time_estimates.json").write_text(json.dumps(est, indent=1))
    print(json.dumps(est["notebooks"], indent=1))
    print(json.dumps(est["reference"], indent=1))


if __name__ == "__main__":
    main()
