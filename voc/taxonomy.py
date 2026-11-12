"""Evidence rules for English feedback. Ambiguous or unsupported labels go to review."""
import re

TOPIC_CUES = {
    "approval": r"\b(approv\w*|sign[- ]?off|in[- ]flight approval|backup reviewer|delegate)\b",
    "notifications": r"\b(notifications?|alerts?|digests?|push reminders?)\b",
    "export": r"\b(exports?\w*|csv|spreadsheet|download\w*)\b",
    "permissions": r"\b(guests?|external invite|outside collaborator|permission\w*|read[- ]only)\b",
    "search": r"\b(search\w*|archived results|exact match\w*|known incident number)\b",
    "sync": r"\b(sync\w*|webhooks?|connector\w*|slack|integrations?|api)\b",
    "other": r"\b(invoices?|tax (?:identifier|id|number)|font|keyboard shortcuts?|dark appearance|"
             r"compact layout|translate\w*|toolbar|blank boards?)\b",
}
SENTIMENT_CUES = {
    "negative": r"\b(frustrat\w*|disappoint\w*|awful|unhappy|painful|annoy\w*|miserable|fed up|"
                r"dread|let us down|hate|tired of|wrecking|dismal|furious|irritat\w*|exhaust\w*)\b",
    "neutral": r"\b(for context|for reference|flagging for|what should happen|we saw this|"
               r"could (?:you|we)|would it be|can (?:we|an|you)|is there a way|please check)\b",
    "positive": r"\b(excellent|happy with|appreciat\w*|loves? (?:the|using)|pleased|great|brilliantly|"
                r"fond of|a pleasure|we like|really like|works well|thank you)\b",
}
SEVERITY_CUES = {
    "blocking": r"\b(no workaround|no alternative|block(?:ed|s|ing)|cannot (?:finish|proceed|"
                r"complete|move|reopen|release|run|dispatch|submit|provide)|"
                r"unable to (?:finish|proceed|release)|nobody can (?:sign|do)|"
                r"no other way|release cannot proceed|stops production)\b",
    "moderate": r"\b(manual(?:ly)?|extra (?:time|steps)|repeating some steps|by hand|"
                r"workaround (?:but|is available)|spend\w* .{0,30} clearing)\b",
    "low": r"\b(as normal|as usual|no rush|no urgent|a preference|a small|minor|can wait|"
           r"no deadline|nice to have|nice-to-have|would be (?:nice|helpful)|optional|"
           r"nobody is held up|just (?:a suggestion|an idea)|ignore .{0,25} for now)\b",
}
CLAUSE = re.compile(r"[.!?\n]+")
TOPICS = {label: re.compile(pattern, re.IGNORECASE) for label, pattern in TOPIC_CUES.items()}
SENTIMENT = {label: re.compile(pattern, re.IGNORECASE) for label, pattern in SENTIMENT_CUES.items()}
SEVERITY = {label: re.compile(pattern, re.IGNORECASE) for label, pattern in SEVERITY_CUES.items()}


def matches(text, patterns):
    return {label for label, pattern in patterns.items() if pattern.search(text)}


def labels(text):
    topic = "review"
    for clause in CLAUSE.split(text):
        found = matches(clause, TOPICS)
        if found:
            if len(found) == 1:
                topic = next(iter(found))
            break
    sentiment = matches(text, SENTIMENT)
    expressed = sentiment & {"negative", "positive"}
    if expressed == {"negative", "positive"}:
        tone = "review"
    elif expressed:
        tone = next(iter(expressed))
    else:
        tone = "neutral" if "neutral" in sentiment else "review"
    severity = matches(text, SEVERITY)
    if "blocking" in severity and "moderate" in severity:
        urgency = "review"
    else:
        urgency = next((label for label in ("blocking", "moderate", "low") if label in severity), "review")
    return {"topic": topic, "sentiment": tone, "severity": urgency}
