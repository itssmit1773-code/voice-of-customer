"""Build the local evidence warehouse and decision exports."""
import argparse
import hashlib
import json
import re
import sqlite3
from collections import defaultdict
from contextlib import closing
from pathlib import Path
from tempfile import TemporaryDirectory

from voc.evaluate import AXES, comparison, metrics
from voc.generate import DATA, END, ROOT, SEED, START, generate, library, read_csv, write_csv
from voc.metrics import query, sql_file
from voc.model import TextClassifier
from voc.roadmap import ranked_candidates, sensitivity
from voc.taxonomy import labels as taxonomy_labels

DEFAULT_OUTPUT = ROOT / "artifacts"
THRESHOLDS = {"topic": .95, "sentiment": .85, "severity": .85}
ACCESS_PATTERN = re.compile(
    r"\b(guest|outside collaborator|external reviewer)\b.{0,55}\b(private|restricted|wrong project|read-only)\b",
    re.IGNORECASE,
)


def canonicalize(rows):
    """Collapse exact normalized copies within a source-matched thread and account."""
    groups = defaultdict(list)
    for row in rows:
        normalized = " ".join(row["text"].casefold().split())
        groups[row["account_id"], row["thread_key"], normalized].append(row)
    retained, audit = [], []
    for group in groups.values():
        known_ids = {row["user_id"] for row in group if row["user_id"]}
        if len(known_ids) > 1:
            raise ValueError("Conflicting identities in a duplicate group")
        first = min(group, key=lambda row: (row["date"], row["event_id"]))
        canonical = dict(first, user_id=next(iter(known_ids), ""))
        # Keep the earliest source attribution and recover identity from a confirmed copy.
        retained.append(canonical)
        audit.extend({"event_id": row["event_id"], "canonical_event_id": canonical["event_id"]}
                     for row in group if row["event_id"] != canonical["event_id"])
    return retained, audit


def fit_models(source):
    topics = [(text, label) for label, entry in source["topics"].items() for text in entry["train"]]
    models = {"topic": TextClassifier.fit(topics)}
    for axis, lexicon in source["modifiers"].items():
        models[axis] = TextClassifier.fit(
            (cue, label) for label, cues in lexicon.items() for cue in cues
        )
    return models


def classify(text, models=None):
    labels = (taxonomy_labels(text) if models is None else
              {axis: models[axis].predict(text, THRESHOLDS[axis])[0] for axis in AXES})
    reasons = [f"Uncertain {axis}" for axis in AXES if labels[axis] == "review"]
    if labels["severity"] == "blocking":
        reasons.append("Possible blocker")
    if ACCESS_PATTERN.search(text):
        reasons.append("Possible access exposure")
    return {**labels, "needs_review": int(bool(reasons)), "review_reason": " · ".join(reasons)}


def insert(connection, table, rows, fields):
    placeholders = ", ".join("?" for _ in fields)
    connection.executemany(
        f"INSERT INTO {table} ({', '.join(fields)}) VALUES ({placeholders})",
        ([row[key] for key in fields] for row in rows),
    )


def build_database(path, accounts, members, feedback, audit):
    with closing(sqlite3.connect(path)) as connection, connection:
        connection.executescript(sql_file("schema"))
        insert(connection, "account", accounts, ("account_id", "segment", "region"))
        insert(connection, "member", members, ("user_id", "account_id"))
        insert(connection, "feedback", (dict(row, user_id=row["user_id"] or None) for row in feedback),
               ("event_id", "thread_key", "date", "channel", "account_id", "user_id", "text",
                "topic", "sentiment", "severity", "needs_review", "review_reason"))
        insert(connection, "duplicate_audit", audit, ("event_id", "canonical_event_id"))


def write_json(path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def build(output=DEFAULT_OUTPUT):
    output = Path(output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(dir=output.parent) as temporary:
        stage = Path(temporary)
        raw = generate(stage)
        raw_feedback = read_csv(raw / "feedback.csv")
        accounts = read_csv(raw / "accounts.csv")
        members = read_csv(raw / "members.csv")
        truth = {row["thread_key"]: row for row in read_csv(raw / "simulation_truth.csv")}
        feedback, audit = canonicalize(raw_feedback)
        models = fit_models(library())
        classified = [dict(row, **classify(row["text"])) for row in feedback]
        simulated = [comparison(row["event_id"], row["text"], truth[row["thread_key"]],
                                row, row["channel"]) for row in classified]
        challenge = [comparison(row["case_id"], row["text"], row, classify(row["text"]))
                     for row in read_csv(DATA / "challenge.csv")]
        audit_cases = [comparison(row["case_id"], row["text"], row, classify(row["text"]))
                       for row in read_csv(DATA / "audit.csv")]
        evaluation = {
            name: {axis: metrics(rows, axis) for axis in AXES}
            for name, rows in [("audit", audit_cases), ("challenge", challenge), ("simulation", simulated),
                               *[(channel, [row for row in simulated if row["channel"] == channel])
                                 for channel in ("Support", "In-app", "Review")]]
        }
        baseline_rows = [
            comparison(row["case_id"], row["text"], row, classify(row["text"], models))
            for row in read_csv(DATA / "audit.csv")
        ]
        evaluation["baseline_audit"] = {axis: metrics(baseline_rows, axis) for axis in AXES}
        write_json(stage / "evaluation.json", evaluation)
        write_csv(stage / "challenge_predictions.csv", challenge)
        write_csv(stage / "audit_predictions.csv", audit_cases)
        write_csv(stage / "baseline_audit_predictions.csv", baseline_rows)
        errors = [row for row in simulated if any(row[f"expected_{axis}"] != row[f"predicted_{axis}"]
                                                    for axis in AXES)]
        write_csv(stage / "simulation_errors.csv", errors, list(simulated[0]))

        database = stage / "voc.sqlite"
        build_database(database, accounts, members, classified, audit)
        write_csv(stage / "duplicate_audit.csv", audit, ["event_id", "canonical_event_id"])
        for name in ("overview", "theme", "trend", "segments", "reach"):
            write_csv(stage / f"{name}.csv", query(database, name, START, END))
        write_csv(stage / "history.csv", query(database, "trend", "2026-04-01", END))
        candidates = ranked_candidates(database)
        write_csv(stage / "roadmap.csv", candidates)
        write_csv(stage / "sensitivity.csv", sensitivity(candidates))
        write_json(stage / "manifest.json", {
            "synthetic": True, "seed": SEED, "reporting_period": [START, END],
            "accounts": len(accounts), "members": len(members), "raw_rows": len(raw_feedback),
            "canonical_rows": len(classified), "duplicate_rows": len(audit),
            "sha256": {file.relative_to(stage).as_posix(): hashlib.sha256(file.read_bytes()).hexdigest()
                       for file in sorted(stage.rglob("*")) if file.is_file()},
            "source_sha256": {file.name: hashlib.sha256(file.read_bytes()).hexdigest()
                              for file in sorted(DATA.iterdir()) if file.is_file()},
        })
        for file in sorted(stage.rglob("*")):
            if file.is_file():
                target = output / file.relative_to(stage)
                target.parent.mkdir(parents=True, exist_ok=True)
                file.replace(target)
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    print(f"Built {build(parser.parse_args().output)}")
