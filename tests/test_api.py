import json
import os
import tempfile
import threading
import sys
import unittest
import urllib.error
import urllib.request
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC))
from wsgiref.simple_server import make_server

from app import application


class ApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp_dir = tempfile.TemporaryDirectory()
        os.environ["CALCULATOR_DB_PATH"] = str(Path(cls.temp_dir.name) / "test.db")
        cls.server = make_server("127.0.0.1", 0, application)
        cls.base_url = f"http://127.0.0.1:{cls.server.server_port}"
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.thread.join(timeout=2)
        cls.server.server_close()
        cls.temp_dir.cleanup()
        os.environ.pop("CALCULATOR_DB_PATH", None)

    def setUp(self):
        self._request("/api/history", method="DELETE")

    def _request(self, path, method="GET", payload=None, expected_status=200):
        data = None
        headers = {}
        if payload is not None:
            data = json.dumps(payload).encode("utf-8")
            headers["Content-Type"] = "application/json"
        request = urllib.request.Request(
            f"{self.base_url}{path}", data=data, headers=headers, method=method
        )
        try:
            with urllib.request.urlopen(request, timeout=3) as response:
                status = response.status
                body = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as error:
            status = error.code
            body = json.loads(error.read().decode("utf-8"))
        self.assertEqual(status, expected_status)
        return body

    def test_calculate_and_history(self):
        result = self._request(
            "/api/calculate",
            method="POST",
            payload={"expression": "(2+3)*4"},
            expected_status=201,
        )
        self.assertEqual(result["result"], "20")

        history = self._request("/api/history")
        self.assertEqual(len(history["items"]), 1)
        self.assertEqual(history["items"][0]["expression"], "(2+3)*4")

    def test_delete_history(self):
        result = self._request(
            "/api/calculate",
            method="POST",
            payload={"expression": "1+2"},
            expected_status=201,
        )
        history_id = result["history"]["id"]
        self._request(f"/api/history/{history_id}", method="DELETE")
        self.assertEqual(self._request("/api/history")["items"], [])

    def test_division_by_zero_is_not_saved(self):
        error = self._request(
            "/api/calculate",
            method="POST",
            payload={"expression": "1/0"},
            expected_status=400,
        )
        self.assertEqual(error["code"], "DIVISION_BY_ZERO")
        self.assertEqual(self._request("/api/history")["items"], [])


if __name__ == "__main__":
    unittest.main()
