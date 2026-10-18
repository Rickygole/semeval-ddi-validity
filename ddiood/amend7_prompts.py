import hashlib
import json

CLASSES = ["false", "enzyme", "effect", "warning", "interaction"]
BINARY = ["no", "yes"]

P1 = """Classify the drug interaction. Answer with one word only.

Drug A: {drug_a}
Drug B: {drug_b}

Options: false, enzyme, effect, warning, interaction

If no interaction exists, answer: false
If the interaction acts through enzymes, transporters or drug action, answer: enzyme
If a clinical effect is described, answer: effect
If a warning or recommendation is given, answer: warning
If an interaction exists but no detail is known, answer: interaction

Answer:"""

P2 = """Do the two drugs below have a clinically relevant drug-drug interaction? Answer with one word only: yes or no.

Drug A: {drug_a}
Drug B: {drug_b}

Answer:"""

P3 = """Classify the drug interaction. Answer with one word only.

Drug A: {drug_a}
Drug B: {drug_b}

Options: warning, interaction, false, effect, enzyme

If a warning or recommendation is given, answer: warning
If an interaction exists but no detail is known, answer: interaction
If no interaction exists, answer: false
If a clinical effect is described, answer: effect
If the interaction acts through enzymes, transporters or drug action, answer: enzyme

Answer:"""

P4 = """You are given two drugs. Decide whether they interact and, if so, how. Reply with a single word.

First drug: {drug_a}
Second drug: {drug_b}

Allowed replies: false, enzyme, effect, warning, interaction
false means the drugs do not interact.
enzyme means they interact through enzymes, transporters or the way the drugs act.
effect means they interact with a described clinical effect.
warning means a warning or recommendation applies when they are combined.
interaction means they interact without further detail.

Reply:"""

P5 = """Task: drug-drug interaction triage. Reply with one word from this list: false, enzyme, effect, warning, interaction.

Pair under review: {drug_a} and {drug_b}

Use false when no interaction is known. Use enzyme for an interaction explained by enzymes, transporters or how the drugs act. Use effect for an interaction defined by its clinical consequence. Use warning for a pair that carries a warning or dosing recommendation. Use interaction for an interaction with no further detail.

Reply:"""

PRIMARY = "p2_binary"
NAMES_PROMPTS = [("p2_binary", P2, BINARY), ("p1_base", P1, CLASSES), ("p3_shuffled", P3, CLASSES),
                 ("p4_reword_a", P4, CLASSES), ("p5_reword_b", P5, CLASSES)]

EVIDENCE = """Using only the FDA label evidence below, decide whether Drug A and Drug B have a drug-drug interaction. Answer with one word only: yes or no.

FDA label evidence:
{evidence}

Drug A: {drug_a}
Drug B: {drug_b}

Answer:"""

NO_EVIDENCE = "No evidence."

CHAT_ROLE = "user"
EVIDENCE_TOKEN_CAP = 6000
MAX_PROMPT_TOKENS = 8192
NON_ANSWER_MASS = 0.5
SHUFFLE_SEED = 7
SCRAMBLE_SEED = 7
WRONG_ORACLE_SEED = 7


def chat(tok, user):
    return tok.apply_chat_template([{"role": CHAT_ROLE, "content": user}], tokenize=False, add_generation_prompt=True)


def names_prompt(template, a, b):
    return template.format(drug_a=a, drug_b=b)


def evidence_prompt(evidence, a, b):
    return EVIDENCE.format(evidence=evidence, drug_a=a, drug_b=b)


def case_forms(word):
    return [word, word.capitalize(), " " + word, " " + word.capitalize()]


def class_token_ids(tok, words):
    ids = {}
    for i, w in enumerate(words):
        cands = set()
        for form in case_forms(w):
            enc = tok(form, add_special_tokens=False)["input_ids"]
            if len(enc) == 1:
                cands.add(enc[0])
        if not cands:
            raise RuntimeError(f"no whole-word token for label word {w}")
        ids[i] = sorted(cands)
    flat = [t for v in ids.values() for t in v]
    if len(flat) != len(set(flat)):
        raise RuntimeError(f"class token ids collide: {ids}")
    return ids


def frozen_hash():
    blob = json.dumps({"names": [(n, t, c) for n, t, c in NAMES_PROMPTS], "evidence": EVIDENCE,
                       "no_evidence": NO_EVIDENCE, "cap": EVIDENCE_TOKEN_CAP, "max": MAX_PROMPT_TOKENS,
                       "mass": NON_ANSWER_MASS, "seeds": [SHUFFLE_SEED, SCRAMBLE_SEED, WRONG_ORACLE_SEED], "primary": PRIMARY},
                      sort_keys=True)
    return hashlib.sha256(blob.encode()).hexdigest()
