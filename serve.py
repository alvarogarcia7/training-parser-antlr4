#!/usr/bin/env python3
"""Development server for the Training Parser PWA.

Serves from the project root so the Pyodide worker can fetch Python
source files via relative paths (../parser/model.py etc.).

PWA is at: http://localhost:<port>/mobile-app/

Adds COOP/COEP headers required by Pyodide's SharedArrayBuffer.
Automatically loads configuration from .env.local for development.

Usage:
    uv run python3 serve.py          # port 8080
    uv run python3 serve.py 9000     # custom port
"""

import sys
import os
import webbrowser
import re
from http.server import HTTPServer, SimpleHTTPRequestHandler
from functools import partial


def load_env_config() -> dict:
    """Load environment configuration from .env.local."""
    config = {}
    env_file = ".env.local"

    if not os.path.exists(env_file):
        return config

    try:
        with open(env_file, "r") as f:
            for line in f:
                line = line.strip()
                # Skip comments and empty lines
                if not line or line.startswith("#"):
                    continue
                # Parse KEY=VALUE
                if "=" in line:
                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip()
                    # Map environment variables to config keys
                    if key.startswith("GITHUB_"):
                        config_key = f"git_{key[7:].lower()}"
                        config[config_key] = value
                    elif key.startswith("GITLAB_"):
                        config_key = f"git_{key[7:].lower()}"
                        config[config_key] = value
                    elif key.startswith("PRIVATE_GIT_"):
                        config_key = f"git_{key[12:].lower()}"
                        config[config_key] = value
                    elif key.startswith("LOCAL_GIT_SERVER_"):
                        config_key = f"git_{key[17:].lower()}"
                        config[config_key] = value
                    elif key.startswith("CORS_"):
                        config_key = key.lower()
                        config[config_key] = value
    except Exception as e:
        print(f"Warning: Could not read .env.local: {e}", file=sys.stderr)

    return config


def inject_config_into_html(html: str, config: dict) -> str:
    """Inject configuration as JavaScript before app loads."""
    if not config:
        return html

    # Create JavaScript that pre-loads configuration
    config_script = "window.__DEV_CONFIG__ = " + str(config).replace("'", '"') + ";"

    # Insert before the main app script
    insertion_point = html.find('<script type="module"')
    if insertion_point > 0:
        html = html[:insertion_point] + f'<script nonce="training-parser-pwa">\n  {config_script}\n</script>\n  ' + html[insertion_point:]

    return html


class PWAHandler(SimpleHTTPRequestHandler):
    """HTTP handler with COOP/COEP headers and useful logging."""

    def end_headers(self) -> None:
        # Required for Pyodide SharedArrayBuffer (threads)
        self.send_header("Cross-Origin-Opener-Policy", "same-origin")
        self.send_header("Cross-Origin-Embedder-Policy", "require-corp")
        # Prevent caching during development
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        super().end_headers()

    def do_GET(self) -> None:
        """Handle GET requests, injecting config into index.html."""
        # Only inject config for index.html
        if self.path == "/mobile-app/" or self.path == "/mobile-app/index.html":
            try:
                # Read the original file
                file_path = os.path.join(self.directory, "mobile-app/index.html")
                with open(file_path, "r") as f:
                    html = f.read()

                # Inject config from .env.local
                config = load_env_config()
                html = inject_config_into_html(html, config)

                # Send response
                self.send_response(200)
                self.send_header("Content-type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(html)))
                self.end_headers()
                self.wfile.write(html.encode())
                return
            except Exception as e:
                print(f"Error serving index.html: {e}", file=sys.stderr)

        # For all other files, use default handler
        super().do_GET()

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
