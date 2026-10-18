import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ddiood import config
from ddiood.index import build_chunks, leaks, rrf
from ddiood.metrics import binary_f1, bootstrap_f1, extended
from ddiood.ood import moieties, novel_drugs
from ddiood.textnorm import canonicalize, drug_tokenize, mentions


def test_tokenizer_keeps_hyphenated_names():
    assert drug_tokenize("5-FU and N-acetylcysteine") == ["5-fu", "and", "n-acetylcysteine"]


def test_canonicalize_strips_salts_and_forms():
    assert canonicalize("Metformin Hydrochloride Extended Release Tablet") == "metformin"


def test_mentions_word_boundary():
    assert mentions("warfarin", "coadministration with warfarin increases inr")
    assert not mentions("co", "coadministration")


def test_leakage_patterns():
    assert leaks("see 7 DRUG INTERACTIONS for details")
    assert not leaks("pharmacokinetics were linear")


def test_build_chunks_refuses_holdout_section():
    with pytest.raises(RuntimeError):
        build_chunks({}, sections=config.INDEX_SECTIONS + [config.HOLDOUT_SECTION])


def test_build_chunks_skips_leaking_text():
    label = {"clinical_pharmacology": ["metabolized by cyp3a4. see drug interactions (7.1)."],
             "pharmacokinetics": ["half life is 12 hours."]}
    chunks, log = build_chunks({"x": label})
    assert [c["section"] for c in chunks] == ["pharmacokinetics"]
    assert len(log) == 1


def test_rrf_prefers_items_in_both_lists():
    assert rrf([[1, 2, 3], [3, 4, 5]], k=1) == [3]


def test_binary_collapse_and_extended():
    y, p = [0, 1, 2, 0], [0, 3, 0, 4]
    assert binary_f1(y, p) == pytest.approx(0.5)
    e = extended(y, p)
    assert (e["tp"], e["fp"], e["fn"], e["tn"]) == (1, 1, 1, 1)


def test_bootstrap_is_deterministic():
    y, p = [0, 1] * 50, [0, 1, 1, 0] * 25
    assert bootstrap_f1(y, p) == bootstrap_f1(y, p)


def test_moieties_split_combinations():
    assert moieties("nirmatrelvir; ritonavir (co-packaged)") == ["nirmatrelvir", "ritonavir"]
    assert moieties("olanzapine and samidorphan") == ["olanzapine", "samidorphan"]


def test_novel_drugs_uses_first_approval_year(tmp_path):
    csv_path = tmp_path / "nme.csv"
    csv_path.write_text("Proprietary  Name,Active Ingredient/Moiety,Approval Year,FDA Approval Date\n"
                        "Zyprexa,olanzapine,1996,1996-09-30\n"
                        "Lybalvi,olanzapine and samidorphan,2021,2021-05-28\n"
                        "Nurtec,rimegepant,2020,2020-02-27\n")
    drugs, _ = novel_drugs(csv_path, excluded_names=set())
    assert [d["drug"] for d in drugs] == ["rimegepant", "samidorphan"]


def test_novel_drugs_excludes_semeval_vocabulary(tmp_path):
    csv_path = tmp_path / "nme.csv"
    csv_path.write_text("Proprietary  Name,Active Ingredient/Moiety,Approval Year,FDA Approval Date\n"
                        "A,newdrugumab,2022,x\nB,warfarin,2021,x\n")
    drugs, rejected = novel_drugs(csv_path, excluded_names={"warfarin"})
    assert [d["drug"] for d in drugs] == ["newdrugumab"]
    assert rejected["in_semeval_vocabulary"] == 1


@pytest.mark.skipif(not (ROOT / "results/submitted/phase6/all_raw_predictions.json").exists(), reason="no artifacts")
def test_submitted_numbers_reproduce():
    sys.path.insert(0, str(ROOT / "scripts"))
    import reproduce_submitted
    rows, audit, _ = reproduce_submitted.main(ROOT / "results/submitted")
    bad = [r["check"] for r in rows if r["status"] == "MISMATCH"]
    assert set(bad) == {"table1 krag drop", "phase5 notebook KnowledgeRAG-DDI OOD F1 (seed 42)"}, bad
    assert audit["rebuilt_600_matches_saved_file"]
    assert audit["ood_drugs_in_semeval_training_vocabulary"] == audit["n_ood_drugs"]


def test_repository_hygiene():
    banned = [chr(0x2014), chr(0x2013), "\\" + "u2014", "\\" + "u2013", "cla" + "ude"]
    skip = {".git", ".venv", "data", "artifacts", "__pycache__", ".pytest_cache"}
    hits = []
    for p in ROOT.rglob("*"):
        if p.is_dir() or any(part in skip for part in p.relative_to(ROOT).parts):
            continue
        if p.suffix in {".png", ".pdf", ".gz", ".npy", ".pkl", ".index"}:
            continue
        text = p.read_text(encoding="utf-8", errors="ignore")
        low = text.lower()
        hits += [f"{p.relative_to(ROOT)}: {b!r}" for b in banned if b in (low if b.startswith("cla") else text)]
        if p.suffix == ".py":
            for i, line in enumerate(text.splitlines(), 1):
                if line.lstrip().startswith("#"):
                    hits.append(f"{p.relative_to(ROOT)}:{i} comment")
    assert not hits, hits


def test_combination_and_foreign_labels_are_rejected():
    from ddiood.ood import label_identity
    combo = {"openfda": {"substance_name": ["NIRMATRELVIR", "RITONAVIR"]}}
    other = {"openfda": {"substance_name": ["BICTEGRAVIR SODIUM"]}}
    single = {"openfda": {"substance_name": ["RITLECITINIB TOSYLATE"]}}
    assert label_identity(combo, "nirmatrelvir") == "combination_product_label"
    assert label_identity(other, "lenacapavir") == "label_is_for_another_moiety"
    assert label_identity(single, "ritlecitinib") is None


def test_null_effect_sentences_are_detected():
    from ddiood.ood import NULL_EFFECT
    assert NULL_EFFECT.search("Ciprofloxacin No clinically relevant effect")
    assert NULL_EFFECT.search("clearance was not impacted by concomitant methotrexate")
    assert not NULL_EFFECT.search("Concomitant use with rifampin decreases AUC by 70%")


def test_llm_parse_reads_first_word():
    from ddiood.llm import parse
    assert parse(" false interaction") == (0, True)
    assert parse("Advise caution") == (3, True)
    assert parse("int") == (4, True)
    assert parse("interaction") == (0, False)


def test_mask_names_hides_partner_only_as_whole_word():
    from ddiood.inputs import mask_names
    assert mask_names("Rifampin lowers AUC; rifampin-like agents", ["rifampin"]) == "@DRUG$ lowers AUC; rifampin-like agents"


def test_swapped_does_not_cascade():
    from ddiood.inputs import swapped
    p = {"sentence": "Aspirin increases warfarin levels.", "drug_a": "aspirin", "drug_b": "warfarin"}
    assert swapped(p, "warfarin x", "aspirin y")["sentence"] == "warfarin x increases aspirin y levels."


def test_mcc_and_balanced_accuracy():
    e = extended([1, 1, 0, 0], [1, 0, 0, 0])
    assert e["balanced_accuracy"] == pytest.approx(0.75)
    assert e["mcc"] == pytest.approx(1 / 3 ** 0.5)
