import os
from pathlib import Path

ROOT = Path(os.environ.get("DDIOOD_ROOT", Path(__file__).resolve().parents[1]))
DATA = ROOT / "data"
ARTIFACTS = Path(os.environ.get("DDIOOD_ARTIFACTS", ROOT / "artifacts"))
RESULTS = ROOT / "results"
SUBMITTED = RESULTS / "submitted"

DDI_REPO = "https://github.com/isegura/DDICorpus.git"
DDI_COMMIT = "819b0fa538ed83ab2a8b4f5417bba3c03249b7f3"
DDI_DIR = DATA / "DDICorpus"

FDA_LABEL_DIR = DATA / "fda_labels"
NME_CSV = DATA / "fda_novel_approvals.csv"
PRIOR_APPROVALS_CSV = DATA / "prior_approvals.csv"
DRUGBANK_XML = DATA / "drugbank" / "full_database.xml"

LABELS = ["false", "mechanism", "effect", "advise", "int"]
LABEL2ID = {name: i for i, name in enumerate(LABELS)}
ID2LABEL = {i: name for name, i in LABEL2ID.items()}
ENTITY_TYPES = {"drug", "drug_n"}

ENCODER = "microsoft/BiomedNLP-BiomedBERT-base-uncased-abstract-fulltext"
RETRIEVAL_ENCODER = "microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract-fulltext"
LLM = "BioMistral/BioMistral-7B"

CLASS_WEIGHTS = [0.1, 2.0, 2.5, 4.0, 8.0]
LEARNING_RATE = 2e-5
BATCH_SIZE = 16
MAX_EPOCHS = 5
WEIGHT_DECAY = 0.01
WARMUP_FRACTION = 0.1
VAL_FRACTION = 0.1
MAX_LENGTH = 512

SEEDS = [42, 1, 2, 3, 4]
PRIMARY_SEED = 42

INDEX_SECTIONS = ["mechanism_of_action", "pharmacokinetics", "warnings_and_cautions", "clinical_pharmacology"]
HOLDOUT_SECTION = "drug_interactions"
CHUNK_WORDS = 200
CHUNK_OVERLAP = 50
RRF_K = 60
CANDIDATES_PER_RETRIEVER = 10
TOP_K = 5
PASSAGE_CHARS = 100
QUERY_TEMPLATE = "drug interaction between {a} and {b} pharmacokinetics metabolism contraindication"

OOD_MIN_YEAR = 2020
NEGATIVE_RATIO = 2
N_BOOTSTRAP = 1000
BOOTSTRAP_SEED = 42
