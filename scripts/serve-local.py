#!/usr/bin/env python3
"""
Local HTTPS server for PWA development and local network deployment.
Serves the mobile-app PWA with proper HTTPS and CORS headers.

Usage:
    python3 scripts/serve-local.py
    python3 scripts/serve-local.py --port 9443
    python3 scripts/serve-local.py --host 0.0.0.0 --port 8443
"""

import http.server
import ssl
import os
import sys
import argparse
import pathlib
from datetime import datetime


class PWARequestHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP request handler with PWA-friendly headers."""

    def __init__(self, *args, directory=None, **kwargs):
        self.app_dir = directory or "mobile-app"
        super().__init__(*args, directory=self.app_dir, **kwargs)

    def end_headers(self):
        """Add security and PWA headers."""
        # Service Worker and manifest must have max-age to prevent stale caches
        path = self.path
        if path.endswith("/sw.js") or path.endswith("manifest.json"):
            self.send_header("Cache-Control", "public, max-age=3600")
        # HTML should be cached but revalidated
        elif path.endswith(".html") or path == "/":
            self.send_header("Cache-Control", "public, max-age=86400")
        # JavaScript, CSS, and other assets can be cached longer
        else:
            self.send_header("Cache-Control", "public, max-age=31536000")

        # CORS headers for local development
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

        # Security headers
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "SAMEORIGIN")

        # Allow eval for Pyodide
        self.send_header(
            "Content-Security-Policy",
            "default-src 'self'; script-src 'self' https://cdn.jsdelivr.net https://unpkg.com 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; img-src 'self' data:; "
            "connect-src 'self' https://cdn.jsdelivr.net https://unpkg.com https://cors.isomorphic-git.org; "
            "object-src 'none'; base-uri 'self';"
        )

        super().end_headers()

    def log_message(self, format, *args):
        """Log with timestamp."""
        now = datetime.now().strftime("%H:%M:%S")
        print(f"[{now}] {format % args}")


def main():
    parser = argparse.ArgumentParser(
        description="Local HTTPS server for Training Parser PWA"
    )
    parser.add_argument(
        "--host", default="0.0.0.0", help="Host to bind to (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port", type=int, default=8443, help="Port to bind to (default: 8443)"
    )
    parser.add_argument(
        "--cert",
        default="certs/cert.pem",
        help="Path to SSL certificate (default: certs/cert.pem)",
    )
    parser.add_argument(
        "--key",
        default="certs/key.pem",
        help="Path to SSL private key (default: certs/key.pem)",
    )
    args = parser.parse_args()

    # Check for certificates
    if not os.path.exists(args.cert) or not os.path.exists(args.key):
        print("❌ SSL certificates not found!")
        print(f"   Certificate: {args.cert}")
        print(f"   Key: {args.key}")
        print("")
        print("Generate them with:")
        print("   chmod +x scripts/create-ssl-certs.sh")
        print("   ./scripts/create-ssl-certs.sh")
        sys.exit(1)

    # Create SSL context
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(args.cert, args.key)

    # Create handler with directory
    def handler(*args, **kwargs):
        return PWARequestHandler(*args, directory="mobile-app", **kwargs)

    # Create server
    server = http.server.HTTPServer((args.host, args.port), handler)
    server.socket = context.wrap_socket(server.socket, server_side=True)

    # Get actual IP for display
    try:
        import socket

        hostname = socket.gethostname()
        local_ips = socket.gethostbyname_ex(hostname)[2]
        local_ip = local_ips[0] if local_ips else "localhost"
    except:
        local_ip = "localhost"

    print("=" * 70)
    print("Training Parser PWA — Local HTTPS Server")
    print("=" * 70)
    print("")
    print("Server running on:")
    print(f"  🔒 https://localhost:{args.port}")
    print(f"  🔒 https://{local_ip}:{args.port}")
    print("")
    print("To access from another device on your local network:")
    print(f"  📱 https://{local_ip}:{args.port}")
    print("")
    print("Note: You'll see a security warning (self-signed certificate).")
    print("      Click 'Advanced' and 'Proceed anyway' or similar to continue.")
    print("")
    print("First load will cache all necessary files (~30-50 MB).")
    print("Subsequent loads work fully offline (no network needed).")
    print("")
    print("Press Ctrl+C to stop the server.")
    print("=" * 70)
    print("")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\nShutting down...")
        server.shutdown()
        print("✓ Server stopped")


if __name__ == "__main__":
    main()
