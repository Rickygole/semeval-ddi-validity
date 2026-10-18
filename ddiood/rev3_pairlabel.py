from . import config
from .ood import NULL_EFFECT, _first_anchor, _window, label_identity, label_text, mention_index, split_sentences
from .openfda import section_text
from .textnorm import guardrail_excluded, has_risk_signal, mentions
from .vocab import surface_forms

POSITIVE, NEGATIVE, UNDECIDED = "positive", "negative", "undecided"


class PairLabeler:
    def __init__(self, lookup, found, store, excluded=None):
        self.lookup = lookup
        self.found = found
        self.store = store
        self.excluded = set(excluded or ())
        self.forms = surface_forms(lookup)
        form_keys = set(self.forms.values())
        self.eligible = {k for k in lookup if found.get(k) and len(k) >= 4 and k in form_keys}
        self.cui = {k: v["rxcui"] for k, v in lookup.items()}
        self._anchor = {}
        self._mentions = {}

    def label(self, k):
        return self.store.get(self.lookup[k]["normalized"])

    def mentions_of(self, k):
        if k not in self._mentions:
            lab = self.label(k)
            self._mentions[k] = set(mention_index(label_text(lab), self.forms)) if lab else set()
        return self._mentions[k]

    def anchor(self, k):
        if k in self._anchor:
            return self._anchor[k]
        rec = {"ok": False, "reason": None}
        self._anchor[k] = rec
        if not self.found.get(k):
            rec["reason"] = "no_label"
            return rec
        label = self.label(k)
        di = section_text(label, config.HOLDOUT_SECTION) if label else ""
        if not di:
            rec["reason"] = "no_di_section"
            return rec
        if label_identity(label, k):
            rec["reason"] = "label_identity"
            return rec
        di_lower = di.lower()
        candidates = {key: f for key, f in mention_index(di, self.forms).items()
                      if f not in k and k not in f and key in self.eligible}
        if not candidates and has_risk_signal(di_lower):
            rec["reason"] = "risk_signal_without_match"
            return rec
        sentences = split_sentences(di)
        lowered = [s.lower() for s in sentences]
        rec.update({"ok": True, "di_lower": di_lower, "sentences": sentences, "lowered": lowered, "candidates": candidates,
                    "mentioned": self.mentions_of(k), "positive": {}})
        mentioned_cuis = {self.cui[x] for x in rec["mentioned"]}
        rec["mentioned_cuis"] = mentioned_cuis
        for key, form in candidates.items():
            for i, s in enumerate(sentences):
                if mentions(form, lowered[i]) and not NULL_EFFECT.search(s) and _first_anchor(_window(sentences, i)):
                    rec["positive"][key] = True
                    break
        rec["info"] = bool(rec["positive"])
        return rec

    def positive_direction(self, x, y):
        a = self.anchor(x)
        return bool(a["ok"] and a["positive"].get(y))

    def negative_direction(self, x, y, require_info=True):
        a = self.anchor(x)
        if not a["ok"] or y not in self.eligible:
            return False
        if require_info and not a["info"]:
            return False
        if y in a["mentioned"] or self.cui[y] in a["mentioned_cuis"] or guardrail_excluded(y, a["di_lower"]):
            return False
        return x not in self.mentions_of(y)

    def pair_state(self, a, b, require_info=True, ood_blocked=None):
        if a in self.excluded or b in self.excluded:
            return UNDECIDED, {"blocked": "excluded_vocab"}
        if ood_blocked is not None and ood_blocked(a, b):
            return UNDECIDED, {"blocked": "ood_pair"}
        pos = self.positive_direction(a, b) or self.positive_direction(b, a)
        if pos:
            return POSITIVE, {}
        neg = self.negative_direction(a, b, require_info) or self.negative_direction(b, a, require_info)
        return (NEGATIVE if neg else UNDECIDED), {}

    def has_di(self, k):
        if not self.found.get(k):
            return False
        label = self.label(k)
        return bool(label and section_text(label, config.HOLDOUT_SECTION))
