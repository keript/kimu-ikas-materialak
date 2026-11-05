import gzip
import tempfile
import threading
import unittest
from functools import partial
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from scripts.servidor_estatico import StaticHandler


class StaticServerTest(unittest.TestCase):
    def setUp(self):
        self.temporal = tempfile.TemporaryDirectory()
        self.root = Path(self.temporal.name)
        (self.root / "index.html").write_text("<h1>Kimu</h1>", encoding="utf-8")
        (self.root / "style.css").write_text("body { color: green; }", encoding="utf-8")
        self.server = ThreadingHTTPServer(
            ("127.0.0.1", 0), partial(StaticHandler, directory=self.root)
        )
        self.thread = threading.Thread(target=self.server.serve_forever)
        self.thread.start()
        self.base_url = f"http://127.0.0.1:{self.server.server_port}"

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()
        self.temporal.cleanup()

    def test_compresses_text_and_sets_static_cache_headers(self):
        request = Request(
            f"{self.base_url}/style.css", headers={"Accept-Encoding": "gzip"}
        )
        with urlopen(request) as response:
            self.assertEqual(response.headers["Content-Encoding"], "gzip")
            self.assertEqual(response.headers["Vary"], "Accept-Encoding")
            self.assertEqual(response.headers["Cache-Control"], "public, max-age=31536000")
            self.assertEqual(gzip.decompress(response.read()), b"body { color: green; }")

    def test_serves_uncompressed_files_and_head_requests(self):
        with urlopen(f"{self.base_url}/index.html") as response:
            self.assertNotIn("Content-Encoding", response.headers)
            self.assertEqual(response.headers["Cache-Control"], "public, max-age=600")
            self.assertEqual(response.read(), b"<h1>Kimu</h1>")
        request = Request(
            f"{self.base_url}/style.css", headers={"Accept-Encoding": "gzip;q=0"}
        )
        with urlopen(request) as response:
            self.assertNotIn("Content-Encoding", response.headers)
        with urlopen(Request(f"{self.base_url}/index.html", method="HEAD")) as response:
            self.assertEqual(response.headers["Content-Length"], "13")
            self.assertEqual(response.read(), b"")

    def test_rejects_paths_outside_the_site_directory(self):
        outside = self.root.parent / f"{self.root.name}-secret.txt"
        outside.write_text("private", encoding="utf-8")
        try:
            with self.assertRaises(HTTPError) as error:
                urlopen(f"{self.base_url}/..%2f{outside.name}")
            self.assertEqual(error.exception.code, 404)
        finally:
            outside.unlink()


if __name__ == "__main__":
    unittest.main()
