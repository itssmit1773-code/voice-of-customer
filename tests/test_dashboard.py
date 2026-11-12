import unittest
from datetime import date

from streamlit.testing.v1 import AppTest

from voc.generate import ROOT


class DashboardTests(unittest.TestCase):
    def setUp(self):
        self.app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=20).run()
        self.assertFalse(self.app.exception)

    def test_default_numbers_and_intersecting_filters(self):
        self.assertEqual(self.app.metric[0].value, "1,854")
        self.app.sidebar.multiselect[0].set_value(["Enterprise"])
        self.app.sidebar.multiselect[1].set_value(["APAC"])
        self.app.sidebar.multiselect[2].set_value(["Support"])
        self.app.run()
        self.assertFalse(self.app.exception)
        self.assertGreater(int(self.app.metric[0].value.replace(",", "")), 0)
        self.assertLess(int(self.app.metric[0].value.replace(",", "")), 393)
        self.app.toggle[0].set_value(True).run()
        self.assertFalse(self.app.exception)

    def test_empty_date_range(self):
        self.app.sidebar.date_input[0].set_value((date(2026, 7, 1),)).run()
        self.assertFalse(self.app.exception)
        self.assertIn("Select a start and end date", self.app.info[0].value)

    def test_roadmap_and_model_quality_views(self):
        self.app.sidebar.radio[0].set_value("Roadmap").run()
        self.assertFalse(self.app.exception)
        self.assertIn("Prototype approval recovery", self.app.subheader[0].value)
        self.app.get("segmented_control")[0].set_value("High").run()
        self.assertFalse(self.app.exception)
        self.assertTrue(any("95% eligible" in item.value for item in self.app.markdown))
        self.app.sidebar.radio[0].set_value("Model quality").run()
        self.assertFalse(self.app.exception)
        self.assertIn("Classification quality", self.app.title[0].value)
        self.app.selectbox[0].set_value("Statistical baseline (same audit)").run()
        self.assertFalse(self.app.exception)
