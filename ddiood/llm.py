import re

from . import config
from .index import passages_for

PROMPT_B3 = """Classify the drug interaction. Answer with one word only.

Drug A: {drug_a}
Drug B: {drug_b}

Options: false, mechanism, effect, advice, int

If no interaction exists, answer: false
If interaction mechanism is described, answer: mechanism
If clinical effect is described, answer: effect
If a warning or recommendation is given, answer: advice
If interaction exists but no detail, answer: int

Answer:"""

PROMPT_B5 = """Classify drug-drug interactions from FDA evidence.
Labels: false=no interaction, mechanism=PK/PD mechanism, effect=clinical effect, advice=warning, int=interaction exists

FDA evidence:
{passages}

{drug_a} + {drug_b} →"""

LABEL_WORDS = {"false": 0, "no": 0, "none": 0, "mechanism": 1, "effect": 2, "advice": 3, "advise": 3, "int": 4}
FIRST_WORD = re.compile(r"^[^a-z]*([a-z]+)")


def load(name=config.LLM):
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
    q = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4",
                           bnb_4bit_compute_dtype=torch.float16, bnb_4bit_use_double_quant=True)
    tok = AutoTokenizer.from_pretrained(name)
    tok.truncation_side = "left"
    model = AutoModelForCausalLM.from_pretrained(name, quantization_config=q, device_map="auto").eval()
    return tok, model


def parse(text):
    m = FIRST_WORD.match(text.strip().lower())
    if m and m.group(1) in LABEL_WORDS:
        return LABEL_WORDS[m.group(1)], True
    return 0, False


def _generate(tok, model, prompt, max_length):
    import torch
    enc = tok(prompt, return_tensors="pt", truncation=True, max_length=max_length).to(model.device)
    with torch.no_grad():
        out = model.generate(**enc, max_new_tokens=5, do_sample=False, pad_token_id=tok.eos_token_id)
    return tok.decode(out[0][enc["input_ids"].shape[1]:], skip_special_tokens=True)


def b3(tok, model, a, b):
    return parse(_generate(tok, model, PROMPT_B3.format(drug_a=a, drug_b=b), 512))


def b5(tok, model, a, b, cache):
    ps = passages_for(cache, a, b)
    text = "\n".join(f"[{i + 1}] {p[:150]}" for i, p in enumerate(ps)) if ps else "No evidence."
    return parse(_generate(tok, model, PROMPT_B5.format(passages=text, drug_a=a, drug_b=b), 2048))


SCORE_WORDS = [("false", 0), ("mechanism", 1), ("effect", 2), ("advice", 3), ("int", 4)]


def label_token_ids(tok):
    ids = {}
    for word, lid in SCORE_WORDS:
        cands = set()
        for form in (word, " " + word):
            for t in tok(form, add_special_tokens=False)["input_ids"]:
                if tok.decode([t]).strip():
                    cands.add(t)
                    break
        for piece in ("\u2581" + word, word, "\u0120" + word):
            t = tok.convert_tokens_to_ids(piece)
            if isinstance(t, int) and t != tok.unk_token_id and t is not None:
                cands.add(t)
        ids[lid] = sorted(cands)
    flat = [t for v in ids.values() for t in v]
    if len(flat) != len(set(flat)):
        raise RuntimeError(f"label token ids collide: {ids}")
    return ids


def score(tok, model, prompts, ids, max_length=2048, batch_size=8):
    import torch
    tok.padding_side = "left"
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    out = []
    for i in range(0, len(prompts), batch_size):
        enc = tok(prompts[i:i + batch_size], return_tensors="pt", padding=True, truncation=True,
                  max_length=max_length).to(model.device)
        pos = (enc["attention_mask"].cumsum(-1) - 1).clamp(min=0)
        with torch.no_grad():
            logits = model(**enc, position_ids=pos).logits[:, -1, :].float()
        lab = torch.stack([logits[:, ids[l]].max(dim=1).values for l in range(5)], dim=1)
        out.extend(torch.softmax(lab, dim=1).cpu().tolist())
    return out


def prompt_b3(a, b):
    return PROMPT_B3.format(drug_a=a, drug_b=b)


def prompt_b5(a, b, cache, chars=150):
    ps = passages_for(cache, a, b)
    text = "\n".join(f"[{i + 1}] {p[:chars]}" for i, p in enumerate(ps)) if ps else "No evidence."
    return PROMPT_B5.format(passages=text, drug_a=a, drug_b=b)


def load_any(name):
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
    q = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4",
                           bnb_4bit_compute_dtype=torch.bfloat16, bnb_4bit_use_double_quant=True)
    tok = AutoTokenizer.from_pretrained(name)
    tok.truncation_side = "left"
    model = AutoModelForCausalLM.from_pretrained(name, quantization_config=q, device_map="auto").eval()
    return tok, model
