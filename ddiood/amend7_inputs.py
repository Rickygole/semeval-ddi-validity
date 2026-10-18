import re

from .amend7_evidence import grep_hit, mask_forms, partner_forms

WINDOW_CHARS = 320
H5_CHARS = 400
K = 5
MAX_LENGTH = 512


class MissingPassages(RuntimeError):
    pass


def chunk_ids(cache, a, b, k=K):
    ids = cache.get(f"{a}|||{b}") or cache.get(f"{b}|||{a}")
    if not ids:
        raise MissingPassages(f"no retrieved passages for {a} | {b}")
    return ids[:k]


def krag_h5(pairs, cache, chunk_text, chars=H5_CHARS, k=K):
    out = []
    for p in pairs:
        ps = [chunk_text[str(i)] for i in chunk_ids(cache, p["drug_a"], p["drug_b"], k)]
        out.append(f"{p['drug_a']} [SEP] {p['drug_b']} [SEP] " + " [SEP] ".join(x[:chars] for x in ps))
    return out


def first_mention(text, forms):
    low = text.lower()
    best = None
    for f in forms:
        m = re.search(r"(?<![\w-])" + re.escape(f) + r"(?![\w-])", low)
        if m and (best is None or m.start() < best):
            best = m.start()
    return best


def snippet(text, forms, window=WINDOW_CHARS):
    pos = first_mention(text, forms)
    if pos is None:
        return text[:window], False
    start = max(0, pos - window // 2)
    if start > 0:
        sp = text.find(" ", start)
        start = sp + 1 if 0 <= sp < pos else start
    return text[start:start + window], True


def evidence_snippets(a, b, ids, chunk_text, chunk_meta, forms, window=WINDOW_CHARS):
    items = []
    for rank, i in enumerate(ids):
        text, has = snippet(chunk_text[str(i)], forms, window)
        drug, section = chunk_meta[str(i)]
        items.append((0 if has else 1, rank, f"{drug} | {section}: {text}"))
    return [t for _, _, t in sorted(items)]


class FixedBuilder:
    def __init__(self, lookup, chunk_text, chunk_meta, window=WINDOW_CHARS):
        self.lookup, self.chunk_text, self.chunk_meta, self.window = lookup, chunk_text, chunk_meta, window
        self._forms = {}

    def forms(self, key):
        if key not in self._forms:
            self._forms[key] = partner_forms(key, self.lookup)
        return self._forms[key]

    def snippets(self, p, cache, k=K):
        ids = chunk_ids(cache, p["drug_a"], p["drug_b"], k)
        return evidence_snippets(p["drug_a"], p["drug_b"], ids, self.chunk_text, self.chunk_meta,
                                 self.forms(p["drug_b"]), self.window)

    def encoder_inputs(self, pairs, cache, k=K):
        return [f"{p['drug_a']} [SEP] {p['drug_b']} [SEP] " + " [SEP] ".join(self.snippets(p, cache, k)) for p in pairs]


def seen_text(tok, text, max_length=MAX_LENGTH):
    enc = tok(text, truncation=True, max_length=max_length, return_offsets_mapping=True)
    end = max((e for _, e in enc["offset_mapping"]), default=0)
    return text[:end], len(enc["input_ids"])


def evidence_part(text):
    parts = text.split(" [SEP] ", 2)
    return parts[2] if len(parts) == 3 else ""


def reachability(tok, texts, pairs, builder, max_length=MAX_LENGTH):
    hits, truncated = [], 0
    for t, p in zip(texts, pairs):
        seen, n = seen_text(tok, t, max_length)
        full_tokens = len(tok(t, truncation=False)["input_ids"])
        truncated += int(full_tokens > max_length)
        hits.append(grep_hit(evidence_part(seen), builder.forms(p["drug_b"])))
    return hits, truncated


QWEN_COND_ARMS = {"contam": "contaminated", "other": "other", "clean": "clean"}
QWEN_CONDS = ("oracle", "masked", "wrong", "redacted", "contam", "other", "clean")


def qwen_evidence(cond, p, ctx, fixed, caches):
    if cond in QWEN_COND_ARMS:
        snips = fixed.snippets(p, caches[QWEN_COND_ARMS[cond]])
        return "\n".join(f"[{i + 1}] {s}" for i, s in enumerate(snips)), {"passages": len(snips)}
    e, m = ctx.evidence("oracle" if cond == "masked" else cond, p["drug_a"], p["drug_b"])
    if cond == "masked":
        e = mask_forms(e, fixed.forms(p["drug_b"]))
    return e, m
