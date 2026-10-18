import random
import re

from .amend7_prompts import (EVIDENCE_TOKEN_CAP, NO_EVIDENCE, SCRAMBLE_SEED, WRONG_ORACLE_SEED)
from .openfda import section_text
from .textnorm import GENERIC_TERMS, mentions, normalize, split_sentences

SUFFIX = re.compile(r"-[a-z]{4}$")

STEMS = sorted({
    "mab", "ximab", "zumab", "umab", "tinib", "nib", "ciclib", "parib", "zomib", "limus", "platin", "rubicin",
    "taxel", "tecan", "vir", "navir", "buvir", "asvir", "tegravir", "previr", "pril", "sartan", "olol", "dipine",
    "statin", "vastatin", "azole", "conazole", "prazole", "tidine", "cillin", "mycin", "floxacin", "oxacin",
    "cycline", "cef", "bactam", "penem", "oxetine", "zepam", "zolam", "triptan", "thiazide", "gliptin",
    "gliflozin", "glitazone", "gliptin", "afil", "setron", "parin", "caine", "barbital", "profen", "coxib",
    "fenac", "cept", "kinra", "terol", "lukast", "olone", "sone", "azine", "apine", "idone", "dronate", "tide",
    "relin", "relix", "phylline", "tadine", "dazole", "pam", "lam", "pine", "zine", "mide", "oxin", "tretin",
    "gestrel", "estradiol", "triptyline", "semide", "fibrate", "formin", "glinide", "sulfa", "vudine", "citabine",
    "poetin", "grastim", "plase", "stim", "cort", "setron", "stat", "xaban", "gatran", "tinib", "ciguat",
}, key=lambda s: (-len(s), s))

CONS, VOW = "bcdfghjklmnprstvz", "aeiou"


def has_stem(token):
    return any(token.endswith(s) and len(token) > len(s) for s in STEMS)


def stem_of(token):
    for s in STEMS:
        if token.endswith(s) and len(token) > len(s) + 1:
            return s
    return None


def _cv(rng, n, start_cons=True):
    out = []
    for i in range(n):
        pool = CONS if (i % 2 == 0) == start_cons else VOW
        out.append(rng.choice(pool))
    return "".join(out)


def _tokens(name):
    return SUFFIX.sub("", name.lower()).split()


def pseudo_keep_stem(name):
    parts, kept = [], []
    for j, tok in enumerate(_tokens(name)):
        s = stem_of(tok)
        rng = random.Random(f"{SCRAMBLE_SEED}:{name}:{j}:keep")
        if s:
            while True:
                p = _cv(rng, max(len(tok) - len(s), 2))
                if not has_stem(p) and (p + s) != tok:
                    break
            parts.append(p + s)
            kept.append(True)
        else:
            while True:
                w = _cv(rng, max(len(tok), 3))
                if not has_stem(w) and w != tok:
                    break
            parts.append(w)
            kept.append(False)
    return " ".join(parts), all(kept)


def pseudo_full(name):
    parts = []
    for j, tok in enumerate(_tokens(name)):
        rng = random.Random(f"{SCRAMBLE_SEED}:{name}:{j}:full")
        while True:
            w = _cv(rng, max(len(tok), 3))
            if not has_stem(w) and w != tok:
                break
        parts.append(w)
    return " ".join(parts)


def pseudo_maps(names):
    keep, full, has = {}, {}, {}
    used_keep, used_full = {}, {}
    for n in sorted(set(names)):
        k, h = pseudo_keep_stem(n)
        f = pseudo_full(n)
        for table, used, val in ((keep, used_keep, k), (full, used_full, f)):
            if val in used and used[val] != n:
                val = val + _cv(random.Random(f"{SCRAMBLE_SEED}:{n}:dup"), 2)
            used[val] = n
            table[n] = val
        has[n] = h
    return keep, full, has


def partner_forms(key, lookup):
    forms = {key}
    v = lookup.get(key)
    if v:
        forms |= {v["normalized"], v["canonicalized"]}
        cui = v["rxcui"]
        for k2, v2 in lookup.items():
            if v2["rxcui"] == cui:
                forms |= {k2, v2["normalized"], v2["canonicalized"]}
    return sorted(f for f in forms if f and (f == key or (len(f) >= 4 and f not in GENERIC_TERMS)))


def grep_hit(text, forms):
    low = text.lower()
    return int(any(f in low and mentions(f, low) for f in forms))


def clean_ws(text):
    return re.sub(r"\s+", " ", text or "").strip()


def di_section(label):
    return clean_ws(section_text(label, "drug_interactions"))


def redact(text, forms):
    kept = [s for s in split_sentences(text) if not any(f in s.lower() and mentions(f, s.lower()) for f in forms)]
    out = " ".join(kept)
    if grep_hit(out, forms):
        pat = "|".join(re.escape(f) for f in sorted(forms, key=len, reverse=True))
        out = re.sub(r"(?<![\w-])(" + pat + r")(?![\w-])", "", out, flags=re.IGNORECASE)
    if grep_hit(out, forms):
        raise RuntimeError("redaction left a partner mention")
    return out


def truncate_tokens(tok, text, cap=EVIDENCE_TOKEN_CAP):
    ids = tok(text, add_special_tokens=False)["input_ids"]
    if len(ids) <= cap:
        return text, len(ids), False
    return tok.decode(ids[:cap]), len(ids), True


def wrong_donor(drug, drugs, seed=WRONG_ORACLE_SEED):
    pool = sorted(d for d in drugs if d != drug)
    return random.Random(f"{seed}:{drug}").choice(pool)


def numbered(chunk_ids, chunk_text, k=5):
    ps = [chunk_text[str(i)] for i in chunk_ids[:k]]
    return "\n".join(f"[{i + 1}] {p}" for i, p in enumerate(ps)) if ps else NO_EVIDENCE


class EvidenceBuilder:
    def __init__(self, tok, di, lookup, caches, chunk_text, cohort_drugs, donor_exclude=()):
        self.tok, self.di, self.lookup = tok, di, lookup
        self.donor_exclude = set(donor_exclude)
        self.caches, self.chunk_text = caches, chunk_text
        self.cohort_drugs = cohort_drugs
        self._forms = {}
        self._trunc = {}

    def forms(self, key):
        if key not in self._forms:
            self._forms[key] = partner_forms(key, self.lookup)
        return self._forms[key]

    def _truncated(self, drug, forms=None):
        ck = (drug, tuple(forms) if forms else None)
        if ck not in self._trunc:
            text = self.di.get(drug, "")
            if not text:
                self._trunc[ck] = (NO_EVIDENCE, 0, False, 0)
            else:
                if forms:
                    text = redact(text, forms)
                t, n, cut = truncate_tokens(self.tok, text)
                self._trunc[ck] = (t or NO_EVIDENCE, n, cut, len(text))
        return self._trunc[ck]

    def evidence(self, cond, a, b):
        if cond == "oracle":
            t, n, cut, _ = self._truncated(a)
            return t, {"tokens_full": n, "truncated": cut}
        if cond == "wrong":
            d = wrong_donor(a, [x for x in self.cohort_drugs if x not in self.donor_exclude])
            t, n, cut, _ = self._truncated(d)
            return t, {"tokens_full": n, "truncated": cut, "donor": d}
        if cond == "redacted":
            t, n, cut, _ = self._truncated(a, self.forms(b))
            return t, {"tokens_full": n, "truncated": cut}
        variant = {"contam": "contaminated", "clean": "hybrid"}[cond]
        ids = self.caches[variant].get(f"{a}|||{b}", [])
        return numbered(ids, self.chunk_text), {"passages": len(ids)}


TOKEN = re.compile(r"[a-z0-9][a-z0-9\-']*")
MASK_TOKEN = "[DRUG]"
MAX_NAME_TOKENS = 4


def name_tokens(name):
    return TOKEN.findall(normalize(name))


def label_names(label):
    o = (label or {}).get("openfda") or {}
    out = []
    for f in ("brand_name", "generic_name", "substance_name"):
        out.extend(x for x in (o.get(f) or []) if isinstance(x, str))
    return out


def build_name_set(label_dir, extra=()):
    import json
    from pathlib import Path
    names = set(extra)
    for p in Path(label_dir).glob("*.json"):
        names.add(p.stem)
        try:
            label = json.loads(p.read_text()).get("label")
        except ValueError:
            continue
        names.update(label_names(label))
    keep = set()
    for n in names:
        toks = tuple(name_tokens(n))
        if not toks or len(toks) > MAX_NAME_TOKENS:
            continue
        joined = " ".join(toks)
        if len(joined) < 4 or joined in GENERIC_TERMS or (len(toks) == 1 and toks[0] in GENERIC_TERMS):
            continue
        keep.add(toks)
    return keep


def mask_names(text, name_set):
    low = text.lower()
    spans = [(m.start(), m.end()) for m in TOKEN.finditer(low)]
    toks = [low[s:e] for s, e in spans]
    out, i, last = [], 0, 0
    while i < len(toks):
        hit = 0
        for n in range(min(MAX_NAME_TOKENS, len(toks) - i), 0, -1):
            if tuple(toks[i:i + n]) in name_set:
                hit = n
                break
        if hit:
            s, e = spans[i][0], spans[i + hit - 1][1]
            out.append(text[last:s])
            out.append(MASK_TOKEN)
            last = e
            i += hit
        else:
            i += 1
    out.append(text[last:])
    return "".join(out)


def stem_names_for(name, taken, tok):
    base = SUFFIX.sub("", name.lower())
    toks = base.split()
    if len(toks) != 1:
        return None
    t = toks[0]
    s = stem_of(t)
    if not s:
        return None
    prefix_len = max(len(t) - len(s), 2)
    rng = random.Random(f"{SCRAMBLE_SEED}:{name}:stemctl")
    for _ in range(500):
        prefix = _cv(rng, prefix_len)
        kept = prefix + s
        if kept in taken or kept == t or has_stem(prefix):
            continue
        letters = list(s)
        for _ in range(200):
            rng.shuffle(letters)
            perm = "".join(letters)
            scr = prefix + perm
            if perm == s or has_stem(scr) or scr in taken:
                continue
            n1 = len(tok(" " + kept, add_special_tokens=False)["input_ids"])
            n2 = len(tok(" " + scr, add_special_tokens=False)["input_ids"])
            if abs(n1 - n2) <= 1:
                return {"stem": s, "preserved": kept, "scrambled": scr, "prefix": prefix,
                        "tokens_preserved": n1, "tokens_scrambled": n2}
    return None


def mask_forms(text, forms):
    pat = "|".join(re.escape(f) for f in sorted(forms, key=len, reverse=True))
    return re.sub(r"(?<![\w-])(" + pat + r")(?![\w-])", MASK_TOKEN, text, flags=re.IGNORECASE)
