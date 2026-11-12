import math
import unittest

from voc.model import TextClassifier
from voc.pipeline import canonicalize
from voc.roadmap import scenario_scores


class CoreTests(unittest.TestCase):
    def test_classifier_abstains_on_unseen_vocabulary(self):
        model = TextClassifier.fit([("red rose", "flower"), ("blue sky", "weather")])
        self.assertEqual(model.predict("red rose")[0], "flower")
        self.assertEqual(model.predict("mountain")[0], "review")

    def test_dedup_keeps_first_source_and_recovers_known_identity(self):
        common = {"account_id": "A1", "thread_key": "T1", "text": "approval froze"}
        rows = [
            dict(common, event_id="E1", user_id="", date="2026-07-01"),
            dict(common, event_id="E2", user_id="U1", date="2026-07-02"),
            dict(common, event_id="E3", user_id="", thread_key="T2", date="2026-07-02"),
        ]
        retained, audit = canonicalize(rows)
        self.assertEqual([row["event_id"] for row in retained], ["E1", "E3"])
        self.assertEqual(retained[0]["user_id"], "U1")
        self.assertEqual(audit, [{"event_id": "E2", "canonical_event_id": "E1"}])

    def test_rice_units_and_monotonic_bounds(self):
        candidate = dict(eligible_low=.5, eligible_base=.75, eligible_high=1,
                         impact_low=1, impact_base=2, impact_high=3,
                         confidence_low=.5, confidence_base=.8, confidence_high=.9,
                         effort_low=2, effort_base=4, effort_high=5)
        scores = scenario_scores(100, candidate)
        self.assertTrue(math.isclose(scores["base"], 30))
        self.assertLess(scores["low"], scores["base"])
        self.assertLess(scores["base"], scores["high"])
