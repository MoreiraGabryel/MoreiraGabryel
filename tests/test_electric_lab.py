from datetime import datetime, timedelta, timezone
from pathlib import Path
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from electric_lab import build, normalize, render_hero
from freeze_snake import adaptive, freeze


class ElectricLabTests(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2026, 1, 10, 12, tzinfo=timezone.utc)
        self.days = [
            {"date": (self.now.date() - timedelta(days=i)).isoformat(), "contributionCount": i % 4}
            for i in range(-2, 35)
        ]
        self.user = {
            "contributionsCollection": {"contributionCalendar": {"weeks": [{"contributionDays": self.days}]}},
            "repositories": {"nodes": [
                {"name": "MoreiraGabryel", "url": "https://github.com/MoreiraGabryel/MoreiraGabryel",
                 "pushedAt": "2026-01-10T10:00:00Z", "isArchived": False},
                {"name": "archived", "url": "https://github.com/example/archived",
                 "pushedAt": "2026-01-09T10:00:00Z", "isArchived": True},
                {"name": "project", "url": "https://github.com/example/project",
                 "pushedAt": "2026-01-08T10:00:00Z", "isArchived": False},
            ]},
        }

    def test_exact_window_across_year_boundary(self):
        data = normalize(self.user, "MoreiraGabryel", self.now)
        self.assertEqual(len(data["days"]), 30)
        self.assertEqual(data["days"][0]["date"], "2025-12-12")
        self.assertEqual(data["days"][-1]["date"], "2026-01-10")
        self.assertEqual(data["total"], sum(i % 4 for i in range(30)))
        self.assertEqual(data["active_days"], sum(i % 4 > 0 for i in range(30)))
        self.assertEqual(data["latest_repository"]["name"], "project")

    def test_missing_data_does_not_publish_invented_zeros(self):
        self.days.pop(10)
        with self.assertRaises(ValueError):
            normalize(self.user, "MoreiraGabryel", self.now)

    def test_empty_activity_and_no_projects(self):
        for day in self.days:
            day["contributionCount"] = 0
        self.user["repositories"]["nodes"] = []
        data = normalize(self.user, "MoreiraGabryel", self.now)
        self.assertEqual(data["total"], 0)
        self.assertIsNone(data["latest_repository"])
        self.assertNotIn("nan", render_hero(data).lower())
        ET.fromstring(render_hero(data))

    def test_escape_api_text_and_generate_every_variant(self):
        self.user["repositories"]["nodes"][-1]["name"] = '<script>&"test"'
        data = normalize(self.user, "MoreiraGabryel", self.now)
        with tempfile.TemporaryDirectory() as directory:
            build(data, Path(directory))
            assets = list(Path(directory).glob("*.svg"))
            self.assertEqual(len(assets), 4)
            for asset in assets:
                source = asset.read_text()
                root = ET.fromstring(source)
                self.assertFalse(root.findall(".//{http://www.w3.org/2000/svg}script"))
                self.assertIn("&lt;script&gt;", source)
                self.assertIn("@media (prefers-color-scheme: light)", source)
                if "static" in asset.name:
                    self.assertNotIn("@keyframes", source)
                else:
                    self.assertIn("prefers-reduced-motion", source)

    def test_freeze_preserves_snake_geometry(self):
        source = '<svg xmlns="http://www.w3.org/2000/svg"><style>@keyframes a {to {opacity:0}}</style><rect width="10" height="10"/></svg>'
        result = freeze(adaptive(source))
        root = ET.fromstring(result)
        self.assertEqual(len(root.findall("{http://www.w3.org/2000/svg}rect")), 1)
        self.assertIn("animation: none !important", result)
        self.assertIn("--cs:#8C6200", result)


if __name__ == "__main__":
    unittest.main()
