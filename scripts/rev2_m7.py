import argparse

import numpy as np

import rev2_common as rc
from amend7_cpu_common import seed_mean
from ddiood import evaluate2 as ev
from ddiood import stats


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--boot", type=int, default=1000)
    a = ap.parse_args()
    crit = rc.require_criteria()
    truth = ev.load_truth()
    s = truth.sets["ood"]
    y, g, q = np.asarray(s["y"]), np.asarray(s["g"]), np.asarray(s["partner"])
    p, n = seed_mean("b2mixed-biomedbert", "ood_empty", seeds=(1, 2, 3, 4, 42))
    if n != 5:
        raise ValueError("the primary endpoint needs five seeds")
    one = ev.boot_auroc(y, p, g, None, a.boot, 42)
    two = ev.boot_auroc(y, p, g, q, a.boot, 42)
    row = {"statistic": "pooled AUROC, b2mixed BiomedBERT, Novel OOD, names only (empty sentence), P(interaction) averaged over seeds 1, 2, 3, 4, 42",
           "n": int(len(y)), "n_pos": int(y.sum()), "n_drugs": int(len(set(g))), "n_seeds": n, "value": ev.auroc(y, p),
           "drug_cluster": {"ci95": list(ev.interval(one)), "ci90": rc.pct(one, 5, 95), "p_tost": ev.tost_p(one), "n_draws": int(len(one))},
           "two_way": {"ci95": list(ev.interval(two)), "ci90": rc.pct(two, 5, 95), "p_tost": ev.tost_p(two), "n_draws": int(len(two))},
           "within_drug_for_reference": stats.stratified_auroc(y, p, g)}
    row["reproduces_tables_md"] = bool(abs(row["value"] - 0.529) < 6e-4 and abs(row["drug_cluster"]["ci95"][0] - 0.457) < 6e-4
                                       and abs(row["drug_cluster"]["ci95"][1] - 0.608) < 6e-4)
    d, t = row["drug_cluster"], row["two_way"]
    text = "\n".join([
        "# M7: the originally preregistered primary endpoint", "", f"Status: {rc.STATUS}.", "",
        "Preregistration, Primary endpoint: AUROC of P(interaction) for `b2mixed` BiomedBERT on Novel OOD, names only, averaged over seeds 1, 2, 3, 4 and 42, "
        "with a 95% bootstrap interval that resamples novel drugs. Amendment 4 replaced it by the within-drug AUROC; Amendment 7 asks for it to be shown with equal prominence.", "",
        "| statistic | n | positives | drugs | AUROC | 95% CI (drug cluster, preregistered) | 90% CI | p_TOST [0.40, 0.60] | 95% CI (two-way) | 90% CI (two-way) | within-drug (H1-novel) |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
        f"| pooled Novel AUROC, names only, 5-seed mean | {row['n']} | {row['n_pos']} | {row['n_drugs']} | {rc.f3(row['value'])} | {rc.ci(d['ci95'])} | {rc.ci(d['ci90'])} | "
        f"{rc.f3(d['p_tost'])} | {rc.ci(t['ci95'])} | {rc.ci(t['ci90'])} | {rc.f3(row['within_drug_for_reference'])} |", "",
        f"1,000 draws, seed 42 (`ddiood.evaluate2.boot_auroc`). Reproduces `results/revision/eval/tables.md` (0.529 [0.457, 0.608]): {row['reproduces_tables_md']}. "
        "The p_TOST is shown for completeness; under the original plan the H1 decision used this interval, and the amended H1 is the within-drug Older-clean test.", ""])
    rc.write("m7_prereg_endpoint", {"status": rc.STATUS, "criteria": crit["m7"], "endpoint": row}, text)
    print(text)


if __name__ == "__main__":
    main()
