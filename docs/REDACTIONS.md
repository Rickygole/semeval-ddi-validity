# Redactions in the public copy

Source commit `a3e1010938fd5ad607f9c5d293f10b92acf4f708`. These files were edited only to remove DrugBank-derived per-drug content; every aggregate value is unchanged. Each file records the removal in a `release_redaction` field or a closing note.

| file | removed | SHA-256 in the source commit | SHA-256 here |
|---|---|---|---|
| `results/revision/post7/classshortcut/classshortcut.json` | per_drug blocks and ATC drugs_without lists | `cdb7a0bb590ac1895b9ff5540565f5be0a0460c8ea7e8f4a35811c1c0065c2e2` | `7744f458a4648b03ac32135bca989274d72c25719b7ddfb7553c381409d5883e` |
| `results/revision/post7/classshortcut/classshortcut.md` | Red-team named drugs table (per-drug ATC classes) | `2807c6a1152446e0390d8272b2ac57ab4c19d31cf3d4844afefbe7ad4da87c06` | `b2f03df89aafbd64b94c3ef1698e291d33497557fdebbbf16d9d026b6ba5a348` |
| `results/revision/sensitivity/drugbank_salts.json` | names of drugs DrugBank did not resolve | `2830aed098155d0217cd90d28ccac1e84142171feceb49244f3b02ec2500afc4` | `e3f1cac937c2266603110375aa0d1e40172ac00fc71b053dadbf5030e61e7d10` |
| `results/revision/sensitivity/drugbank_salts.md` | Unresolved OOD drugs lines | `a5715596acbab17bfaf624b480ba6921a552c610cf01c316a963dc134e6ab92e` | `fd344eab60ff17ca0bf585a82c9a566854021d474934bf78002ce020e4779740` |

Scripts that read these files use only the aggregate fields. Rerun `scripts/post7_classshortcut.py` or `scripts/sens_drugbank_salts.py` with a licensed DrugBank copy to regenerate the full versions.
