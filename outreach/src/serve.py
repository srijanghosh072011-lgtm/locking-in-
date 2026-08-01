"""Serve the demo template locally, on a port we pick ourselves.

The template is a static export built with a basePath (`/plumbing-Templates-/`),
so its CSS, fonts and images are all referenced from that absolute prefix. Serve
the directory at the filesystem root and every asset 404s and the screenshot
comes out unstyled — so the prefix is mounted here rather than left to the
operator to reproduce with a symlink.

Runs in a thread and shuts down with the `with` block, so `mockups` and `daily`
are single commands with no second terminal.
"""

from __future__ import annotations

import contextlib
import functools
import http.server
import pathlib
import socketserver
import threading


class _Handler(http.server.SimpleHTTPRequestHandler):
    base_path = "/"

    def _strip(self, path: str) -> str:
        base = self.base_path.rstrip("/")
        if base and path.startswith(base):
            return path[len(base):] or "/"
        return path

    def do_GET(self):  # noqa: N802
        self.path = self._strip(self.path)
        super().do_GET()

    def do_HEAD(self):  # noqa: N802
        self.path = self._strip(self.path)
        super().do_HEAD()

    def log_message(self, *a):
        pass  # a request log per asset per lead is pure noise


class _Server(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


@contextlib.contextmanager
def serve(directory: pathlib.Path, base_path: str = "/", port: int = 0):
    """Yield the URL the template's homepage is reachable at.

    port=0 lets the OS pick a free one, so a stale server from an earlier run
    can never collide with this one.
    """
    directory = pathlib.Path(directory).expanduser().resolve()
    if not (directory / "index.html").exists():
        raise FileNotFoundError(
            f"no index.html in {directory} — point [template] dir in config.toml "
            "at the built demo site (the folder containing index.html)"
        )

    # Set after creation, not in the class body: `base_path = base_path` there
    # binds a new class-local name and cannot read the enclosing function's.
    class Bound(_Handler):
        pass

    Bound.base_path = base_path

    bound = functools.partial(Bound, directory=str(directory))

    with _Server(("127.0.0.1", port), bound) as httpd:
        thread = threading.Thread(target=httpd.serve_forever, daemon=True)
        thread.start()
        host, real_port = httpd.server_address[:2]
        try:
            yield f"http://{host}:{real_port}{base_path}"
        finally:
            httpd.shutdown()
            thread.join(timeout=5)
