#!/usr/bin/env python3
"""Development server for the Training Parser PWA.

Serves from the project root so the Pyodide worker can fetch Python
source files via relative paths (../parser/model.py etc.).

PWA is at: http://localhost:<port>/mobile-app/

Adds COOP/COEP headers required by Pyodide's SharedArrayBuffer.

Usage:
    uv run python3 serve.py          # port 8080
    uv run python3 serve.py 9000     # custom port
"""

import sys
import webbrowser
from http.server import HTTPServer, SimpleHTTPRequestHandler
from functools import partial


class PWAHandler(SimpleHTTPRequestHandler):
    """HTTP handler with COOP/COEP headers and useful logging."""

    def end_headers(self) -> None:
        # Required for Pyodide SharedArrayBuffer (threads)
        self.send_header("Cross-Origin-Opener-Policy", "same-origin")
        self.send_header("Cross-Origin-Embedder-Policy", "require-corp")
        # Prevent caching during development
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        super().end_headers()

    def log_message(self, fmt: str, *args: object) -> None:
        # Suppress .py source file noise; show everything else
        path = str(args[0]) if args else ""
        if not (path.endswith(".py") or path.endswith(".yaml")):
            super().log_message(fmt, *args)


def main() -> None:
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    handler = partial(PWAHandler, directory=".")
    server = HTTPServer(("", port), handler)

    url = f"http://localhost:{port}/mobile-app/"
    print(f"\n  Training Parser PWA")
    print(f"  -------------------")
    print(f"  Open: {url}")
    print(f"\n  Ctrl+C to stop\n")

    try:
        webbrowser.open(url)
    except Exception:
        pass

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")


if __name__ == "__main__":
    main()
