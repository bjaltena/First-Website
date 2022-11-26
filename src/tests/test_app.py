import unittest

from app import create_app


class TestWebServer(unittest.TestCase):
    """Test class for the flask webserver"""

    def setUp(self) -> None:
        # Create the server and store in the instance
        our_app = create_app()
        self.flask_app = our_app
        self.test_client = our_app.test_client()

    def test_up(self):
        """can we successfully call the up endpoint on the web server?"""
        with self.flask_app.app_context():
            up_check = self.test_client.get("/up")
        self.assertEqual(up_check.json, {"status": "happy"})
        self.assertEqual(up_check.status_code, 200)

    def test_healthz(self):
        """can we successfully call the healthz endpoint on the web server?"""
        with self.flask_app.app_context():
            up_check = self.test_client.get("/healthz")
        self.assertEqual(up_check.json, {"status": "happy"})
        self.assertEqual(up_check.status_code, 200)
