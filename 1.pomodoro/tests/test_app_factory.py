import unittest
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from pomodoro import create_app


class CreateAppTests(unittest.TestCase):
    def test_create_app_returns_flask_instance(self):
        app = create_app()
        self.assertEqual(app.name, "pomodoro")

    def test_create_app_applies_custom_config(self):
        app = create_app({"TESTING": True, "SECRET_KEY": "unit-test-key"})
        self.assertTrue(app.config["TESTING"])
        self.assertEqual(app.config["SECRET_KEY"], "unit-test-key")

    def test_main_blueprint_is_registered(self):
        app = create_app()
        self.assertIn("main", app.blueprints)


if __name__ == "__main__":
    unittest.main()
