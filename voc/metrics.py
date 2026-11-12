"""Parameterized, shared SQL for exports and dashboard filters."""
from contextlib import closing
from functools import lru_cache
import sqlite3

from voc.generate import ROOT

SQL = ROOT / "sql"
DIMENSIONS = {"channel", "segment", "region", "topic"}
METRICS = {"overview", "theme", "trend", "segments", "reach"}


@lru_cache
def sql_file(name):
    return (SQL / f"{name}.sql").read_text(encoding="utf-8")


def query(database, metric, start, end, **filters):
    if metric not in METRICS | {"records"} or filters.keys() - DIMENSIONS:
        raise ValueError("Unsupported metric or filter")
    where = ["date BETWEEN ? AND ?"]
    parameters = [str(start), str(end)]
    for dimension, values in filters.items():
        if values:
            where.append(f"{dimension} IN ({', '.join('?' for _ in values)})")
            parameters.extend(values)
    statement = (
        "SELECT event_id, date, channel, segment, region, account_id, user_id, topic, "
        "sentiment, severity, needs_review, review_reason, text "
        "FROM scoped ORDER BY needs_review DESC, date DESC, event_id;"
        if metric == "records" else sql_file(metric)
    )
    cte = "WITH scoped AS (SELECT * FROM evidence WHERE " + " AND ".join(where) + ")"
    if statement.startswith("WITH "):
        statement = cte + ", " + statement.removeprefix("WITH ")
    else:
        statement = cte + " " + statement
    with closing(sqlite3.connect(database.resolve().as_uri() + "?mode=ro", uri=True)) as connection:
        connection.row_factory = sqlite3.Row
        return [dict(row) for row in connection.execute(statement, parameters)]
