import re

REJECT_TERMS = [
    "phosphate", "histamine", "calcium", "magnesium", "aluminum",
    "iron", "bismuth", "dopamine", "glucose", "ethanol",
]

DOSAGE_FORMS = [
    "extended release", "tablet", "tablets", "capsule", "capsules",
    "solution", "injection", "er", "xr", "sr",
]

SALT_SUFFIXES = [
    "hydrochloride", "sodium", "potassium", "acetate", "succinate", "tartrate",
    "phosphate", "mesylate", "fumarate", "maleate", "besylate", "tosylate", "hydrate",
]

GENERIC_TERMS = {
    "drug", "drugs", "agent", "agents", "compound", "compounds", "substance", "substances",
    "product", "products", "medication", "medications", "medicine", "medicines", "treatment",
    "treatments", "therapy", "therapies", "lead", "iron", "calcium", "magnesium", "aluminum",
    "zinc", "bismuth", "phosphate", "glucose", "alcohol", "ethanol", "water", "oxygen", "sodium",
    "potassium", "chloride", "fluoride", "gold", "acid", "salt", "salts", "histamine", "dopamine",
    "serotonin", "norepinephrine", "epinephrine", "inhibitor", "inhibitors", "inducer", "inducers",
    "blocker", "blockers", "agonist", "agonists", "antagonist", "antagonists", "receptor",
    "receptors", "antacid", "antacids", "hormone", "hormones", "vitamin", "vitamins", "insulin",
    "toxin", "toxins", "vaccine", "vaccines", "contrast", "charcoal", "food", "milk", "caffeine",
}

ANCHOR_TOKENS = [
    "contraindicated", "avoid", "coadministration", "concomitant", "inhibits", "induces",
    "increases auc", "decreases auc", "increases exposure", "decreases exposure",
    "qt prolongation", "bleeding risk", "strong inhibitor", "strong inducer",
]

RISK_PATTERNS = [
    r"\bavoid\b", r"\bcontraindicat(ed|ion|ions)?\b", r"\bdo not use\b",
    r"\bstrong\b.{0,20}\b(inhibitor|inducer)\b", r"\bqtc?\b", r"\bbleeding risk\b",
    r"\bnarrow therapeutic index\b",
]

DRUG_TO_CLASSES = {
    "lisinopril": {"ace_i"}, "enalapril": {"ace_i"}, "captopril": {"ace_i"}, "ramipril": {"ace_i"},
    "quinapril": {"ace_i"}, "benazepril": {"ace_i"}, "fosinopril": {"ace_i"}, "perindopril": {"ace_i"},
    "metoprolol": {"bb"}, "atenolol": {"bb"}, "carvedilol": {"bb"}, "propranolol": {"bb"},
    "bisoprolol": {"bb"}, "labetalol": {"bb"}, "nebivolol": {"bb"}, "nadolol": {"bb"},
    "ketoconazole": {"cyp3a_i"}, "itraconazole": {"cyp3a_i"}, "clarithromycin": {"cyp3a_i"},
    "erythromycin": {"cyp3a_i"}, "ritonavir": {"cyp3a_i"}, "fluconazole": {"cyp3a_i"},
    "rifampin": {"cyp3a_ind"}, "rifampicin": {"cyp3a_ind"}, "carbamazepine": {"cyp3a_ind"},
    "phenytoin": {"cyp3a_ind"}, "phenobarbital": {"cyp3a_ind"},
    "fluoxetine": {"cyp2d6_i"}, "paroxetine": {"cyp2d6_i"}, "bupropion": {"cyp2d6_i"}, "quinidine": {"cyp2d6_i"},
    "ibuprofen": {"nsaid"}, "naproxen": {"nsaid"}, "indomethacin": {"nsaid"}, "celecoxib": {"nsaid"},
    "diclofenac": {"nsaid"}, "aspirin": {"nsaid", "aplt"},
    "warfarin": {"ac"}, "heparin": {"ac"}, "enoxaparin": {"ac"}, "apixaban": {"ac"},
    "rivaroxaban": {"ac"}, "dabigatran": {"ac"},
    "clopidogrel": {"aplt"}, "ticlopidine": {"aplt"}, "prasugrel": {"aplt"},
    "furosemide": {"ld"}, "torsemide": {"ld"}, "bumetanide": {"ld"},
    "spironolactone": {"ksd"}, "eplerenone": {"ksd"}, "triamterene": {"ksd"}, "amiloride": {"ksd"},
    "amlodipine": {"ccb"}, "diltiazem": {"ccb"}, "verapamil": {"ccb"}, "nifedipine": {"ccb"}, "felodipine": {"ccb"},
    "amiodarone": {"qt"}, "sotalol": {"qt"}, "haloperidol": {"qt"}, "methadone": {"qt"},
    "azithromycin": {"qt"}, "chloroquine": {"qt"},
}

CLASS_SURFACE_TERMS = {
    "ace_i": ["ace inhibitor", "ace-inhibitor", "angiotensin converting enzyme inhibitor"],
    "bb": ["beta blocker", "beta-blocker", "beta adrenergic"],
    "cyp3a_i": ["cyp3a inhibitor", "cyp3a4 inhibitor", "strong cyp3a"],
    "cyp3a_ind": ["cyp3a inducer", "cyp3a4 inducer"],
    "cyp2d6_i": ["cyp2d6 inhibitor", "strong cyp2d6"],
    "nsaid": ["nsaid", "non-steroidal anti-inflammatory", "nonsteroidal anti-inflammatory"],
    "ac": ["anticoagulant", "blood thinner"],
    "aplt": ["antiplatelet", "anti-platelet"],
    "ld": ["loop diuretic"],
    "ksd": ["potassium-sparing diuretic", "potassium sparing diuretic"],
    "ccb": ["calcium channel blocker", "calcium channel antagonist"],
    "qt": ["qt prolonging", "qt-prolonging", "qt interval", "qtc prolongation"],
}


def normalize(name):
    name = name.lower().strip()
    name = re.sub(r"[^\w\s\-]", "", name)
    return re.sub(r"\s+", " ", name).strip()


def canonicalize(name):
    name = normalize(name)
    for form in sorted(DOSAGE_FORMS, key=len, reverse=True):
        name = re.sub(rf"\b{re.escape(form)}\b", " ", name)
    tokens = [t for t in name.split() if t not in SALT_SUFFIXES]
    return re.sub(r"\s+", " ", " ".join(tokens)).strip()


def drug_tokenize(text):
    return re.findall(r"[a-z0-9]+(?:-[a-z0-9]+)*", text.lower())


def mentions(term, text):
    return re.search(r"(?<![\w-])" + re.escape(term) + r"(?![\w-])", text) is not None


def split_sentences(text):
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9(])", re.sub(r"\s+", " ", text).strip())
    return [p for p in parts if p]


def guardrail_excluded(drug, text_lower):
    for cls in DRUG_TO_CLASSES.get(drug, set()):
        if any(term in text_lower for term in CLASS_SURFACE_TERMS[cls]):
            return True
    return False


def has_risk_signal(text_lower):
    return any(re.search(p, text_lower) for p in RISK_PATTERNS)
