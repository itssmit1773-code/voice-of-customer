"""Deterministic simulator. No real customer records or external requests."""
import csv
import json
import random
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
SEED = 4726
FIRST_MONTH = 4
LAST_MONTH = 9
YEAR = 2026
START = "2026-07-01"
END = "2026-09-30"
CHANNELS = ("Support", "In-app", "Review")
SEGMENTS = ("Small business", "Mid-market", "Enterprise")
REGIONS = ("Americas", "EMEA", "APAC")
PREFIX = {
    "Support": ("Hi team. ", "Could you take a look? ", "Following up here. ", ""),
    "In-app": ("On the project board, ", "For our weekly process, ", "", ""),
    "Review": ("After a few months of use, ", "From our team trial, ", "", ""),
}
CONTEXT = (
    "We saw this while getting a customer rollout ready.",
    "This came up during a weekly operations handover.",
    "Our distributed team noticed it after a workspace change.",
    "We use the board to coordinate work across time zones.",
    "This happened on both a new and an existing project.",
    "We saw it again during the month-end checklist.",
    "I checked with a teammate who saw the same behavior.",
    "",
)


def write_csv(path, rows, fields=None):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fields or list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def read_csv(path):
    with path.open(newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def library():
    return json.loads((DATA / "feedback_library.json").read_text(encoding="utf-8"))


def generate(destination):
    rng = random.Random(SEED)
    source = library()
    raw = destination / "raw"
    accounts, members, feedback, truth = [], [], [], []
    accounts_by_segment = {segment: [] for segment in SEGMENTS}
    users_by_account = {}
    sizes = [(4, 12), (12, 26), (25, 52)]
    for index in range(360):
        segment_index = rng.choices(range(3), weights=(56, 31, 13))[0]
        segment = SEGMENTS[segment_index]
        account = {
            "account_id": f"A{index + 1:04}",
            "segment": segment,
            "region": rng.choices(REGIONS, weights=(45, 33, 22))[0],
        }
        accounts.append(account)
        accounts_by_segment[segment].append(account)
        account_id = account["account_id"]
        users_by_account[account_id] = []
        for _ in range(rng.randint(*sizes[segment_index])):
            user_id = f"U{len(members) + 1:05}"
            members.append({"user_id": user_id, "account_id": account_id})
            users_by_account[account_id].append(user_id)

    for month in range(FIRST_MONTH, LAST_MONTH + 1):
        month_start = date(YEAR, month, 1)
        days = (date(YEAR, month + 1, 1) - month_start).days
        for _ in range(530 + 22 * (month - FIRST_MONTH)):
            segment = rng.choices(SEGMENTS, weights=(40, 38, 22))[0]
            account = rng.choice(accounts_by_segment[segment])
            account_id = account["account_id"]
            user_id = rng.choice(users_by_account[account_id])
            approval_weight = (14 + 4 * (month - FIRST_MONTH)) * (
                1.35 if segment != "Small business" else 0.70)
            topic = rng.choices(list(source["topics"]),
                                weights=(approval_weight, 27, 17, 10, 13, 14, 9))[0]
            channel = rng.choices(CHANNELS, weights=(54, 30, 16))[0]
            sentiment = rng.choices(("negative", "neutral", "positive"),
                                    weights=(62, 29, 9) if channel == "Support" else (48, 36, 16))[0]
            weights = (10, 49, 41) if topic == "approval" else (45, 43, 12)
            if topic == "permissions":
                weights = (25, 40, 35)
            severity = rng.choices(("low", "moderate", "blocking"), weights=weights)[0]
            phrase = rng.choice(source["topics"][topic]["live"])
            cues = [rng.choice(source["variants"][axis][label])
                    for axis, label in (("sentiment", sentiment), ("severity", severity))]
            for index in range(len(cues)):
                if rng.random() < .12:
                    cues[index] = ""
            if rng.random() < .24:
                rng.shuffle(cues)
            context = rng.choice(CONTEXT)
            text = " ".join(part for part in [rng.choice(PREFIX[channel]) + phrase + ".", *cues, context] if part)
            thread = f"T{len(truth) + 1:05}"
            day = month_start + timedelta(days=rng.randrange(days))
            row = {"event_id": f"E{len(feedback) + 1:06}", "thread_key": thread,
                   "date": day.isoformat(), "channel": channel, "account_id": account_id,
                   "user_id": user_id if rng.random() > (.56 if channel == "Review" else .04) else "",
                   "text": text}
            feedback.append(row)
            truth.append({"thread_key": thread, "topic": topic, "sentiment": sentiment,
                          "severity": severity})
            if rng.random() < .12:
                feedback.append(dict(row, event_id=f"E{len(feedback) + 1:06}",
                                     channel=rng.choice([c for c in CHANNELS if c != channel]),
                                     text=" " + text + " ",
                                     user_id=user_id if rng.random() < .65 else row["user_id"]))
    for filename, rows in [("accounts", accounts), ("members", members),
                           ("feedback", feedback), ("simulation_truth", truth)]:
        write_csv(raw / f"{filename}.csv", rows)
    return raw
