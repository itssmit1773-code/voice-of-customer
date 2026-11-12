"""RICE ranks discretionary product work using a reporter-based reach proxy."""
import json
from itertools import product

from voc.generate import DATA, END, START
from voc.metrics import query

SCENARIOS = ("low", "base", "high")
EFFORT_CASE = {"low": "high", "base": "base", "high": "low"}


def scenario_scores(reporter_count, candidate):
    scores = {}
    for case in SCENARIOS:
        reach = reporter_count * candidate[f"eligible_{case}"]
        impact = candidate[f"impact_{case}"]
        confidence = candidate[f"confidence_{case}"]
        effort = candidate[f"effort_{EFFORT_CASE[case]}"]
        scores[case] = reach * impact * confidence / effort
    return scores


def ranked_candidates(database):
    reach = {row["topic"]: row for row in query(database, "reach", START, END)}
    candidates = json.loads((DATA / "candidates.json").read_text(encoding="utf-8"))
    rows = []
    for candidate in candidates:
        observed = reach.get(candidate["topic"], dict(observed_reporters=0, observed_accounts=0,
                                                      reports=0, anonymous_reports=0))
        scores = scenario_scores(observed["observed_reporters"], candidate)
        rows.append({**candidate, **observed,
                     "base_eligible_reporters": observed["observed_reporters"] * candidate["eligible_base"],
                     **{f"rice_{case}": score for case, score in scores.items()}})
    rows.sort(key=lambda row: (-row["rice_base"], row["topic"]))
    for rank, row in enumerate(rows, 1):
        row["rank"] = rank
    return rows


def sensitivity(rows):
    """Enumerate input scenarios, without interpreting them as probabilities."""
    results = []
    for field in ("eligible", "impact", "confidence", "effort"):
        for level in ("low", "high"):
            stressed = []
            for row in rows:
                candidate = dict(row)
                candidate[f"{field}_base"] = row[f"{field}_{level}"]
                stressed.append((scenario_scores(row["observed_reporters"], candidate)["base"], row["name"]))
            order = sorted(stressed, key=lambda entry: (-entry[0], entry[1]))
            results.append({"changed_input": field, "level": level, "winner": order[0][1],
                            "winner_score": order[0][0], "runner_up": order[1][1],
                            "runner_up_score": order[1][0]})
    top, second = rows[:2]
    for first_case, second_case in product(SCENARIOS, repeat=2):
        left, right = top[f"rice_{first_case}"], second[f"rice_{second_case}"]
        results.append({"changed_input": "top two joint stress", "level": f"{first_case} / {second_case}",
                        "winner": top["name"] if left >= right else second["name"],
                        "winner_score": max(left, right),
                        "runner_up": second["name"] if left >= right else top["name"],
                        "runner_up_score": min(left, right)})
    return results
