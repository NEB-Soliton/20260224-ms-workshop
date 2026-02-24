import unittest
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from pomodoro import create_app


class MainRoutesTests(unittest.TestCase):
    def setUp(self):
        app = create_app({"TESTING": True})
        self.client = app.test_client()

    def test_index_route_returns_200(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_index_route_renders_expected_text(self):
        response = self.client.get("/")
        html = response.get_data(as_text=True)

        self.assertIn("ポモドーロタイマー", html)
        self.assertIn("25:00", html)
        self.assertIn("js/app.js", html)
        self.assertIn("js/timer_engine.js", html)
        self.assertIn("js/ui.js", html)


if __name__ == "__main__":
    unittest.main()
