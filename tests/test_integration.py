import hashlib
import json
import sqlite3
import unittest
from collections import Counter
from contextlib import closing
from pathlib import Path
from tempfile import TemporaryDirectory

from voc.generate import END, START, read_csv
from voc.metrics import query
from voc.pipeline import build, classify
from voc.roadmap import ranked_candidates


class PipelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = TemporaryDirectory()
        cls.addClassCleanup(cls.temporary.cleanup)
        cls.output = build(Path(cls.temporary.name) / "artifacts")
        cls.database = cls.output / "voc.sqlite"

    def test_source_and_canonical_rows_reconcile(self):
        raw = read_csv(self.output / "raw" / "feedback.csv")
        audit = read_csv(self.output / "duplicate_audit.csv")
        with closing(sqlite3.connect(self.database)) as connection:
            kept = connection.execute("SELECT event_id FROM feedback").fetchall()
            self.assertEqual(connection.execute("PRAGMA integrity_check").fetchone()[0], "ok")
            self.assertEqual(connection.execute("PRAGMA foreign_key_check").fetchall(), [])
        kept_ids = {row[0] for row in kept}
        self.assertTrue(all(row["canonical_event_id"] in kept_ids for row in audit))
        dropped_ids = {row["event_id"] for row in audit}
        self.assertFalse(kept_ids & dropped_ids)
        self.assertEqual(kept_ids | dropped_ids, {row["event_id"] for row in raw})
        self.assertEqual((len(raw), len(kept_ids), len(dropped_ids)), (3933, 3510, 423))

    def test_filtered_sql_reconciles_to_record_grain(self):
        filters = dict(segment=["Enterprise"], region=["APAC"], channel=["Support"])
        rows = query(self.database, "records", START, END, **filters)
        result = query(self.database, "overview", START, END, **filters)[0]
        self.assertGreater(len(rows), 0)
        self.assertTrue(all(row["segment"] == "Enterprise" and row["region"] == "APAC"
                            and row["channel"] == "Support" for row in rows))
        self.assertEqual(result["reports"], len(rows))
        self.assertEqual(result["known_reporters"], len({r["user_id"] for r in rows if r["user_id"]}))
        self.assertEqual(result["anonymous_reports"], sum(r["user_id"] is None for r in rows))
        themes = query(self.database, "theme", START, END, **filters)
        self.assertAlmostEqual(sum(t["report_share"] for t in themes), 1.0, places=4)
        self.assertEqual(Counter({t["topic"]: t["reports"] for t in themes}),
                         Counter(r["topic"] for r in rows))
        trends = query(self.database, "trend", START, END, **filters)
        for month in {t["month"] for t in trends}:
            subset = [t for t in trends if t["month"] == month]
            self.assertAlmostEqual(sum(t["report_share"] for t in subset), 1.0)
            self.assertEqual(sum(t["reports"] for t in subset), subset[0]["total_reports"])
        self.assertEqual(query(self.database, "overview", START, END,
                               region=["' OR 1=1 --"])[0]["reports"], 0)

    def test_published_decision_and_raw_hashes(self):
        rows = ranked_candidates(self.database)
        leader = rows[0]
        self.assertEqual(leader["topic"], "approval")
        self.assertEqual(leader["observed_reporters"], 394)
        self.assertAlmostEqual(leader["rice_base"], 394 * .80 * 2 * .80 / 3.5)
        self.assertGreater(rows[1]["rice_high"], leader["rice_low"])
        manifest = json.loads((self.output / "manifest.json").read_text(encoding="utf-8"))
        for filename, expected in manifest["sha256"].items():
            self.assertEqual(hashlib.sha256((self.output / filename).read_bytes()).hexdigest(), expected)

    def test_review_queue_routes_ambiguity_and_access_exposure(self):
        uncertain = classify("Search and CSV export are inconsistent.")
        self.assertEqual(uncertain["topic"], "review")
        self.assertTrue(uncertain["needs_review"])
        flagged = classify("The guest can open our private board.")
        self.assertIn("Possible access exposure", flagged["review_reason"])

    def test_audit_metrics_reconcile_to_expected_labels(self):
        rows = read_csv(self.output / "audit_predictions.csv")
        evaluation = json.loads((self.output / "evaluation.json").read_text(encoding="utf-8"))["audit"]
        for axis, metrics in evaluation.items():
            correct = sum(row[f"expected_{axis}"] == row[f"predicted_{axis}"] for row in rows)
            accepted = [row for row in rows if row[f"predicted_{axis}"] != "review"]
            self.assertAlmostEqual(metrics["accuracy"], correct / len(rows))
            self.assertAlmostEqual(metrics["coverage"], len(accepted) / len(rows))
            self.assertAlmostEqual(metrics["accepted_accuracy"], sum(
                row[f"expected_{axis}"] == row[f"predicted_{axis}"] for row in accepted) / len(accepted))
