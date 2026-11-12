PRAGMA foreign_keys = ON;

CREATE TABLE account (
    account_id TEXT PRIMARY KEY,
    segment TEXT NOT NULL,
    region TEXT NOT NULL
);
CREATE TABLE member (
    user_id TEXT PRIMARY KEY,
    account_id TEXT NOT NULL REFERENCES account,
    UNIQUE (user_id, account_id)
);
CREATE TABLE feedback (
    event_id TEXT PRIMARY KEY,
    thread_key TEXT NOT NULL,
    date TEXT NOT NULL,
    channel TEXT NOT NULL CHECK (channel IN ('Support', 'In-app', 'Review')),
    account_id TEXT NOT NULL REFERENCES account,
    user_id TEXT,
    text TEXT NOT NULL,
    topic TEXT NOT NULL,
    sentiment TEXT NOT NULL CHECK (sentiment IN ('negative', 'neutral', 'positive', 'review')),
    severity TEXT NOT NULL CHECK (severity IN ('low', 'moderate', 'blocking', 'review')),
    needs_review INTEGER NOT NULL CHECK (needs_review IN (0, 1)),
    review_reason TEXT NOT NULL,
    FOREIGN KEY (user_id, account_id) REFERENCES member (user_id, account_id)
);
CREATE TABLE duplicate_audit (
    event_id TEXT PRIMARY KEY,
    canonical_event_id TEXT NOT NULL REFERENCES feedback(event_id)
);
CREATE INDEX feedback_scope ON feedback(date, channel, account_id, topic);

CREATE VIEW evidence AS
SELECT f.*, a.segment, a.region, substr(f.date, 1, 7) AS month
FROM feedback f JOIN account a USING (account_id);
