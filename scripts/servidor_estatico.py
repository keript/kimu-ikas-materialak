"""Sirve la web generada con compresión y caché como un hosting estático."""
import argparse
import gzip
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit

CONTENT_TYPES = {
    ".css": "text/css",
    ".html": "text/html",
    ".js": "text/javascript",
    ".json": "application/json",
    ".svg": "image/svg+xml",
    ".txt": "text/plain",
    ".xml": "application/xml",
}


class StaticHandler(SimpleHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def __init__(self, *args, directory, **kwargs):
        self.root = Path(directory).resolve()
        self.files = {
            path.relative_to(self.root).as_posix(): path
            for path in self.root.rglob("*")
            if path.is_file() and path.resolve().is_relative_to(self.root)
        }
        super().__init__(*args, directory=str(self.root), **kwargs)

    def _accepts_gzip(self):
        codings = {}
        for value in self.headers.get("Accept-Encoding", "").lower().split(","):
            parts = [part.strip() for part in value.split(";")]
            try:
                quality = float(parts[1][2:]) if len(parts) > 1 and parts[1].startswith("q=") else 1
            except ValueError:
                quality = 0
            codings[parts[0]] = quality
        return codings.get("gzip", codings.get("*", 0)) > 0

    def _serve_file(self, send_body):
        relative = unquote(urlsplit(self.path).path).lstrip("/")
        if not relative or relative.endswith("/"):
            relative += "index.html"
        path = self.files.get(relative)
        if path is None:
            self.send_error(404)
            return

        content_type = CONTENT_TYPES.get(path.suffix.lower(), "application/octet-stream")
        compressible = content_type.startswith("text/") or content_type in {
            "application/javascript",
            "application/json",
            "image/svg+xml",
        }
        body = path.read_bytes()
        use_gzip = compressible and self._accepts_gzip()
        if use_gzip:
            body = gzip.compress(body)

        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        cache_age = 600 if path.suffix.lower() == ".html" else 31536000
        self.send_header("Cache-Control", f"public, max-age={cache_age}")
        if compressible:
            self.send_header("Vary", "Accept-Encoding")
        if use_gzip:
            self.send_header("Content-Encoding", "gzip")
        self.end_headers()
        if send_body:
            self.wfile.write(body)

    def do_GET(self):
        self._serve_file(send_body=True)

    def do_HEAD(self):
        self._serve_file(send_body=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    root = Path(__file__).resolve().parent.parent / "_site"
    if not root.is_dir():
        parser.error(f"No existe el directorio: {root}")
    handler = partial(StaticHandler, directory=root)
    with ThreadingHTTPServer(("127.0.0.1", args.port), handler) as server:
        server.serve_forever()


if __name__ == "__main__":
    main()
