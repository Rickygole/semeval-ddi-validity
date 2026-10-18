# DrugBank name resolution: salt forms and one-sided pairs

Sensitivity analysis, post hoc. The preregistered files `artifacts/ood/drugbank_validation*.csv` are not changed.

## novel

438 rows. Original resolution reproduces the saved `drugbank_validation.csv`: True.

| variant | OOD drugs unresolved | rows, OOD side unresolved | partners unresolved | rows, partner unresolved | rows, one side only | listed | not listed | unresolvable |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| original | 2 | 21 | 1 | 3 | 22 | 239 | 198 | 1 |
| original_one_sided_unresolvable | 2 | 21 | 1 | 3 | 22 | 239 | 176 | 23 |
| salt_stripped | 2 | 21 | 1 | 3 | 22 | 239 | 198 | 1 |
| salt_stripped_one_sided_unresolvable | 2 | 21 | 1 | 3 | 22 | 239 | 176 | 23 |

| variant | n | drugs | lookup AUROC within | 95% CI | pooled | positive confirmation | positive precision (resolvable) | negative contradiction | kappa margin 0.1 | H1 AUROC | kappa observed |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| original | 438 | 48 | 0.729 | [0.642, 0.808] | 0.767 | 0.899 | 0.899 | 0.367 | 0.438 | 0.523 | 0.101 |
| original_one_sided_unresolvable | 438 | 48 | 0.729 | [0.642, 0.808] | 0.767 | 0.899 | 0.924 | 0.391 | 0.438 | 0.523 | 0.101 |
| salt_stripped | 438 | 48 | 0.729 | [0.642, 0.808] | 0.767 | 0.899 | 0.899 | 0.367 | 0.438 | 0.523 | 0.101 |
| salt_stripped_one_sided_unresolvable | 438 | 48 | 0.729 | [0.642, 0.808] | 0.767 | 0.899 | 0.924 | 0.391 | 0.438 | 0.523 | 0.101 |
| original_excluding_unresolved_ood_drugs | 417 | 46 | 0.737 | [0.640, 0.825] | 0.764 | 0.917 | 0.917 | 0.390 | 0.423 | 0.525 | 0.107 |
| original_excluding_rows_with_an_unresolved_side | 415 | 46 | 0.740 | [0.641, 0.834] | 0.766 | 0.924 | 0.924 | 0.391 | 0.417 | 0.529 | 0.119 |



## older_clean

1832 rows. Original resolution reproduces the saved `drugbank_validation_old.csv`: True.

| variant | OOD drugs unresolved | rows, OOD side unresolved | partners unresolved | rows, partner unresolved | rows, one side only | listed | not listed | unresolvable |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| original | 16 | 243 | 7 | 42 | 281 | 954 | 876 | 2 |
| original_one_sided_unresolvable | 16 | 243 | 7 | 42 | 281 | 954 | 595 | 283 |
| salt_stripped | 2 | 26 | 7 | 42 | 68 | 1091 | 741 | 0 |
| salt_stripped_one_sided_unresolvable | 2 | 26 | 7 | 42 | 68 | 1091 | 673 | 68 |

| variant | n | drugs | lookup AUROC within | 95% CI | pooled | positive confirmation | positive precision (resolvable) | negative contradiction | kappa margin 0.1 | H1 AUROC | kappa observed |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| original | 1832 | 128 | 0.641 | [0.595, 0.689] | 0.680 | 0.763 | 0.763 | 0.404 | 0.708 | 0.452 | -0.342 |
| original_one_sided_unresolvable | 1832 | 128 | 0.641 | [0.595, 0.689] | 0.680 | 0.763 | 0.869 | 0.486 | 0.708 | 0.452 | -0.342 |
| salt_stripped | 1832 | 128 | 0.660 | [0.610, 0.709] | 0.690 | 0.851 | 0.851 | 0.471 | 0.626 | 0.452 | -0.302 |
| salt_stripped_one_sided_unresolvable | 1832 | 128 | 0.660 | [0.610, 0.709] | 0.690 | 0.851 | 0.875 | 0.492 | 0.626 | 0.452 | -0.302 |
| original_excluding_unresolved_ood_drugs | 1589 | 112 | 0.659 | [0.609, 0.709] | 0.686 | 0.846 | 0.846 | 0.474 | 0.629 | 0.447 | -0.337 |
| original_excluding_rows_with_an_unresolved_side | 1549 | 112 | 0.659 | [0.607, 0.709] | 0.691 | 0.869 | 0.869 | 0.486 | 0.630 | 0.448 | -0.330 |



Release note: per-drug DrugBank resolution names are removed from the public copy; the counts above are unchanged. Rerun scripts/sens_drugbank_salts.py with a licensed DrugBank copy to regenerate them.
