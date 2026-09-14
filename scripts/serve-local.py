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
import socket
import os
import sys
import argparse
import pathlib
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

# Verify Python version
assert sys.version_info >= (3, 7), "Python 3.7+ required"


class PWARequestHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP request handler with PWA-friendly headers."""

    def __init__(self, *args: Any, directory: Optional[str] = None, **kwargs: Any) -> None:
        self.app_dir = directory or "mobile-app"
        super().__init__(*args, directory=self.app_dir, **kwargs)

    def end_headers(self) -> None:
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

    def log_message(self, format: str, *args: Any) -> None:
        """Log with timestamp."""
        now = datetime.now().strftime("%H:%M:%S")
        print(f"[{now}] {format % args}")


def main() -> None:
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

    # Validate port range
    assert 1 <= args.port <= 65535, f"Invalid port: {args.port} (must be 1-65535)"

    # Validate host
    assert args.host, "Host cannot be empty"

    # Check for mobile-app directory
    app_dir = Path("mobile-app")
    if not app_dir.exists() or not app_dir.is_dir():
        print("❌ Error: mobile-app directory not found")
        print("   Run this script from the project root directory")
        print("   Expected: ./mobile-app/")
        sys.exit(1)

    # Verify index.html exists
    index_file = app_dir / "index.html"
    if not index_file.exists():
        print("❌ Error: index.html not found in mobile-app/")
        print("   The PWA app shell is missing")
        sys.exit(1)

    # Check for certificates with detailed error messages
    cert_path = Path(args.cert)
    key_path = Path(args.key)

    if not cert_path.exists():
        print("❌ SSL certificate not found!")
        print(f"   Expected at: {cert_path.absolute()}")
        print("")
        print("Generate certificates with:")
        print("   chmod +x scripts/create-ssl-certs.sh")
        print("   ./scripts/create-ssl-certs.sh")
        sys.exit(1)

    if not key_path.exists():
        print("❌ SSL private key not found!")
        print(f"   Expected at: {key_path.absolute()}")
        print("")
        print("Generate certificates with:")
        print("   chmod +x scripts/create-ssl-certs.sh")
        print("   ./scripts/create-ssl-certs.sh")
        sys.exit(1)

    # Verify files are readable
    try:
        with open(cert_path, 'r') as f:
            f.read(1)
    except Exception as e:
        print(f"❌ Error: Cannot read certificate file: {e}")
        sys.exit(1)

    try:
        with open(key_path, 'r') as f:
            f.read(1)
    except Exception as e:
        print(f"❌ Error: Cannot read key file: {e}")
        sys.exit(1)

    # Create SSL context (compatible with macOS, Linux, and Python 3.7+)
    try:
        # Use PROTOCOL_TLS (auto-negotiates best version) instead of PROTOCOL_TLS_SERVER
        # for better compatibility across Python versions and platforms
        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        context.load_cert_chain(str(cert_path), str(key_path))
        # Disable SSL/TLSv1.0 for security but allow TLSv1.2+
        context.minimum_version = ssl.TLSVersion.TLSv1_2
    except ssl.SSLError as e:
        print(f"❌ Error loading SSL certificates: {e}")
        print("   Ensure the certificate and key files are valid")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error creating SSL context: {e}")
        sys.exit(1)

    # Create handler with directory
    def handler(*args: Any, **kwargs: Any) -> PWARequestHandler:
        return PWARequestHandler(*args, directory="mobile-app", **kwargs)

    # Create server with error handling
    try:
        server = http.server.HTTPServer((args.host, args.port), handler)
        server.socket = context.wrap_socket(server.socket, server_side=True)
        # Disable Nagle's algorithm for better latency on local network
        server.socket.setsockopt(0, 1, 1)  # TCP_NODELAY
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"❌ Error: Port {args.port} is already in use")
            print("   Try a different port: python3 scripts/serve-local.py --port 9443")
        elif "Permission denied" in str(e):
            print(f"❌ Error: Permission denied for port {args.port}")
            print("   Ports < 1024 require administrator privileges")
            print(f"   Try a port >= 1024: python3 scripts/serve-local.py --port 8443")
        else:
            print(f"❌ Error binding to {args.host}:{args.port}: {e}")
        sys.exit(1)

    # Get actual IP for display (cross-platform: Mac and Linux)
    local_ip = "localhost"
    try:
        # Try to get non-loopback local IP
        hostname = socket.gethostname()
        ips = socket.gethostbyname_ex(hostname)[2]
        # Filter out loopback addresses and use the first real IP
        non_loopback = [ip for ip in ips if not ip.startswith("127.")]
        if non_loopback:
            local_ip = non_loopback[0]
        elif ips:
            local_ip = ips[0]
    except Exception:
        # Fallback: try to connect to an external address (doesn't actually send data)
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
        except Exception:
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
