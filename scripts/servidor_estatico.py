"""Sirve la web generada con compresión y caché como un hosting estático."""
import argparse
import gzip
import mimetypes
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit


class StaticHandler(SimpleHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def __init__(self, *args, directory, **kwargs):
        self.root = Path(directory).resolve()
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
        path = (self.root / unquote(urlsplit(self.path).path).lstrip("/")).resolve()
        if not path.is_relative_to(self.root):
            self.send_error(404)
            return
        if path.is_dir():
            path /= "index.html"
        if not path.is_file():
            self.send_error(404)
            return

        content_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
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
        self.send_header("Cache-Control", "public, max-age=600")
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
    parser.add_argument("--directory", default="_site")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    root = Path(args.directory).resolve()
    if not root.is_dir():
        parser.error(f"No existe el directorio: {root}")
    handler = partial(StaticHandler, directory=root)
    with ThreadingHTTPServer(("127.0.0.1", args.port), handler) as server:
        server.serve_forever()


if __name__ == "__main__":
    main()
