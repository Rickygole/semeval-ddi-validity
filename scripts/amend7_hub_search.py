import datetime
import json
import sys
from pathlib import Path

from huggingface_hub import HfApi, hf_hub_download

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ddiood import amend7_panel as pn

OUT = ROOT / "artifacts" / "amend7" / "hub_candidates.json"
QUERIES = ["ddi", "ddi2013", "ddi-2013", "ddi_corpus", "semeval-2013-task-9", "drug-drug interaction", "drug_drug_interaction",
           "ddi extraction", "DDIExtraction", "biobert ddi", "pubmedbert ddi", "relation extraction drug", "drugprot",
           "pubmedbert relation extraction", "biomedical relation extraction"]
NEGATIVE_LABELS = {"no_relation", "none", "negative", "other", "false", "no relation", "noddi", "no_ddi", "no-ddi"}
FORMAT_MARKERS = ("input format", "[e1]", "<e1>", "@drug$", "drug1")
CANDIDATES = {
    "jialicheng/ddi_biobert": "label names are LABEL_0..LABEL_4; model card names no training corpus",
    "jialicheng/ddi-pubmedbert-abstract": "label names are LABEL_0..LABEL_4; model card names no training corpus",
    "jialicheng/ddi-pubmedbert-fulltext": "label names are LABEL_0..LABEL_4; model card names no training corpus",
    "wesin/pubmedbert-relation-extraction": "trained on five corpora jointly; entity-marker format documented",
    "ltmai/Bio_ClinicalBERT_DDI_finetuned": "trained on DrugBank and RxNav interactions from chemical structure, not on DDI Extraction 2013",
    "GooKSL/BioLinkBERT-large-DDI": "feature-extraction checkpoint without a classification head",
    "GooKSL/BioM-BERT-PubMed-PMC-Large-DDI": "feature-extraction checkpoint without a classification head",
    "clinicalnlplab/finetuned-Llama-2-13b-hf-DDI2013_train": "13B generative model, no model card, no documented input format",
    "clinicalnlplab/finetuned-PMCLLaMA-13B-DDI2013_train": "13B generative model, no model card, no documented input format",
    "igorvln/dare_gpt2_ddi_finetuning": "generative GPT-2 for the 2018 task path, no classification head",
    "Zabbonat/DDI": "DDI means data-driven innovation, unrelated to drugs",
    "selmahabib/biobert-finetuned-tac-ddi": "token classification (TAC 2018), no relation head",
    "bprimal/Drug-Drug-Interaction-Classification": "CatBoost on molecular properties, not a text model",
}


def facts_of(repo, info, cfg):
    card = info.card_data.to_dict() if info.card_data else {}
    datasets = card.get("datasets") or []
    try:
        readme = open(hf_hub_download(repo, "README.md", revision=info.sha), encoding="utf8").read().lower()
    except Exception:
        readme = ""
    labels = [str(v).lower() for v in ((cfg or {}).get("id2label") or {}).values()]
    return {"train_corpora": datasets, "input_format_documented": any(m in readme for m in FORMAT_MARKERS),
            "negative_label": any(l in NEGATIVE_LABELS for l in labels)}


def main():
    api = HfApi()
    log = {"searched_on": datetime.date.today().isoformat(), "queries": {}, "candidates": {}}
    for q in QUERIES:
        log["queries"][q] = len([m.id for m in api.list_models(search=q, limit=100)])
    passed, facts_all = [], {}
    for repo, note in CANDIDATES.items():
        info = api.model_info(repo)
        entry = {"sha": info.sha, "tags": info.tags, "pipeline_tag": info.pipeline_tag, "note": note}
        cfg = None
        try:
            cfg = json.loads(Path(hf_hub_download(repo, "config.json", revision=info.sha)).read_text())
            entry["architectures"] = cfg.get("architectures")
            entry["id2label"] = cfg.get("id2label")
        except Exception as e:
            entry["config_error"] = type(e).__name__
        entry["facts"] = facts_of(repo, info, cfg)
        entry["static_checks"] = pn.static_checks(entry["facts"])
        entry["static_pass"] = all(entry["static_checks"].values()) and cfg is not None and entry["pipeline_tag"] in (
            "text-classification", None) and "ForSequenceClassification" in str(entry.get("architectures"))
        if entry["static_pass"]:
            passed.append(repo)
            facts_all[repo] = entry["facts"]
        log["candidates"][repo] = entry
    log["external_subset"] = {
        "rule": "label mapping from the SemEval TRAIN majority class; a negative class exists; no TAC 2018 or DrugBank training stated; input format documented; a sequence classification head",
        "passed_static_checks": passed, "facts": facts_all,
        "revisions": {r: log["candidates"][r]["sha"] for r in passed},
        "excluded": {r: log["candidates"][r]["note"] for r in CANDIDATES if r not in passed}}
    OUT.write_text(json.dumps(log, indent=1))
    print(json.dumps({"searched_on": log["searched_on"], "queries": log["queries"], "passed": passed}, indent=1))
    for r, e in log["candidates"].items():
        print(r, e["static_checks"], e["static_pass"])


if __name__ == "__main__":
    main()
