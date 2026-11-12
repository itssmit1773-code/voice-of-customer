"""Multinomial Naive Bayes with a vocabulary and score-margin review gate."""
import math
import re
from collections import Counter, defaultdict
from dataclasses import dataclass


def features(text):
    words = re.findall(r"[a-z0-9]+", text.casefold())
    return words + [f"{left} {right}" for left, right in zip(words, words[1:])]


@dataclass
class TextClassifier:
    counts: dict
    totals: dict
    vocabulary: set
    priors: dict

    @classmethod
    def fit(cls, examples):
        counts = defaultdict(Counter)
        document_counts = Counter()
        vocabulary = set()
        for text, label in examples:
            tokens = features(text)
            counts[label].update(tokens)
            document_counts[label] += 1
            vocabulary.update(tokens)
        total_documents = sum(document_counts.values())
        return cls(dict(counts), {label: sum(count.values()) for label, count in counts.items()},
                   vocabulary, {label: math.log(n / total_documents)
                                for label, n in document_counts.items()})

    def predict(self, text, margin_threshold=0.65):
        tokens = Counter(token for token in features(text) if token in self.vocabulary)
        if not tokens:
            return "review", 0.0, ""
        scores = {}
        for label, counts in self.counts.items():
            denominator = self.totals[label] + len(self.vocabulary)
            scores[label] = self.priors[label] + sum(
                amount * math.log((counts[token] + 1) / denominator)
                for token, amount in tokens.items()
            )
        ordered = sorted(scores, key=lambda label: (-scores[label], label))
        best, second = ordered[:2]
        margin = scores[best] - scores[second]
        return (best if margin >= margin_threshold else "review"), margin, best
