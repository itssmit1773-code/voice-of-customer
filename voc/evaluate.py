"""Evaluate held-out text and produce a row-level review file."""
from collections import Counter

AXES = ("topic", "sentiment", "severity")


def metrics(examples, axis):
    pairs = [(row[f"expected_{axis}"], row[f"predicted_{axis}"]) for row in examples]
    matrix = Counter(pairs)
    labels = sorted({gold for gold, _ in pairs})
    per_class = []
    for label in labels:
        tp = matrix[label, label]
        support = sum(n for (gold, _), n in matrix.items() if gold == label)
        predicted = sum(n for (_, guess), n in matrix.items() if guess == label)
        per_class.append({"label": label, "support": support,
                          "precision": tp / predicted if predicted else 0,
                          "recall": tp / support, "f1": 2 * tp / (support + predicted)})
    covered = sum(n for (_, guess), n in matrix.items() if guess != "review")
    correct_accepted = sum(matrix[label, label] for label in labels if label != "review")
    correct = sum(matrix[label, label] for label in labels)
    return {"n": len(pairs), "accuracy": correct / len(pairs),
            "coverage": covered / len(pairs), "accepted_accuracy": correct_accepted / covered if covered else None,
            "macro_f1": sum(row["f1"] for row in per_class) / len(per_class),
            "majority_accuracy": max(row["support"] for row in per_class) / len(pairs),
            "per_class": per_class,
            "confusion": {label: {guess: matrix[label, guess] for guess in sorted(set(labels) | {"review"})}
                          for label in labels}}


def comparison(identity, text, expected, predicted, channel="Challenge"):
    return {"id": identity, "channel": channel, "text": text,
            **{f"expected_{axis}": expected[axis] for axis in AXES},
            **{f"predicted_{axis}": predicted[axis] for axis in AXES},
            "review_reason": predicted["review_reason"]}
