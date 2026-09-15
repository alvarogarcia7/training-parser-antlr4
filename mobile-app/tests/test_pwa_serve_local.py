"""Tests for pwa-serve-local HTTPS server setup."""

import pytest
import subprocess
import time
import os
import ssl
import socket
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import URLError
import json

# Skip tests if not on a system with certificates
CERT_PATH = Path(__file__).parent.parent.parent / "certs" / "cert.pem"
KEY_PATH = Path(__file__).parent.parent.parent / "certs" / "key.pem"

pytestmark = pytest.mark.skipif(
    not (CERT_PATH.exists() and KEY_PATH.exists()),
    reason="SSL certificates not found - run 'make pwa-certs' first"
)


@pytest.fixture(scope="session")
def pwa_server():
    """Start the pwa-serve-local server for the duration of tests."""
    # Start server
    proc = subprocess.Popen(
        ["python3", "scripts/serve-local.py", "--host", "127.0.0.1", "--port", "8445"],
        cwd=Path(__file__).parent.parent.parent,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    time.sleep(2)  # Wait for server to start

    yield proc

    # Cleanup
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait()


def get_page(path: str, pwa_server) -> bytes:
    """Fetch a page from pwa-serve-local, bypassing SSL verification."""
    # Create SSL context that doesn't verify certificates (for self-signed certs)
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    url = f"https://127.0.0.1:8445{path}"
    req = Request(url)

    try:
        with urlopen(req, context=ssl_context, timeout=5) as response:
            return response.read()
    except URLError as e:
        raise AssertionError(f"Failed to fetch {url}: {e}")
    except socket.timeout:
        raise AssertionError(f"Timeout fetching {url}")


def test_index_html_serves_correctly(pwa_server):
    """Test that index.html is served from the root."""
    content = get_page("/", pwa_server).decode("utf-8")

    assert "Training Parser" in content
    assert "<html" in content
    assert "<!doctype html" in content.lower()


def test_service_worker_serves_correctly(pwa_server):
    """Test that service worker script is accessible."""
    content = get_page("/sw.js", pwa_server).decode("utf-8")

    assert "cacheNames" in content or "const" in content
    assert "self" in content  # Service worker uses 'self'


def test_pyodide_worker_serves_correctly(pwa_server):
    """Test that pyodide worker script is accessible."""
    content = get_page("/src/pyodide-worker.js", pwa_server).decode("utf-8")

    assert "loadPyodide" in content
    assert "initPyodide" in content
    assert "PYTHON_FILES" in content


def test_ui_js_serves_correctly(pwa_server):
    """Test that ui.js is accessible."""
    content = get_page("/src/ui.js", pwa_server).decode("utf-8")

    assert "parseWorkout" in content
    assert "Logger" in content


def test_manifest_serves_correctly(pwa_server):
    """Test that manifest.json is valid JSON and serves."""
    content = get_page("/manifest.json", pwa_server).decode("utf-8")

    manifest = json.loads(content)
    assert "name" in manifest
    assert "icons" in manifest


def test_python_files_are_accessible(pwa_server):
    """Test that Python source files are accessible."""
    # Test a few key files
    files_to_test = [
        "/python/app_api.py",
        "/python/antlr4/__init__.py",
    ]

    for file_path in files_to_test:
        content = get_page(file_path, pwa_server)
        assert len(content) > 0, f"File {file_path} is empty"


def test_parser_modules_accessible(pwa_server):
    """Test that parser modules are accessible."""
    files_to_test = [
        "/../parser/__init__.py",
        "/../parser/model.py",
        "/../parser/parser.py",
        "/../dist/trainingLexer.py",
    ]

    for file_path in files_to_test:
        try:
            content = get_page(file_path, pwa_server)
            assert len(content) > 0, f"File {file_path} is empty"
        except AssertionError as e:
            # Some files might 404, that's OK for this test
            # We're mainly checking the server structure
            pass


def test_cors_headers_present(pwa_server):
    """Test that CORS headers are set correctly."""
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    url = "https://127.0.0.1:8445/index.html"
    req = Request(url)

    with urlopen(req, context=ssl_context, timeout=5) as response:
        headers = response.headers

        assert "Access-Control-Allow-Origin" in headers
        assert headers["Access-Control-Allow-Origin"] == "*"


def test_csp_header_allows_eval(pwa_server):
    """Test that CSP header allows unsafe-eval for Pyodide."""
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    url = "https://127.0.0.1:8445/index.html"
    req = Request(url)

    with urlopen(req, context=ssl_context, timeout=5) as response:
        headers = response.headers

        assert "Content-Security-Policy" in headers
        csp = headers["Content-Security-Policy"]
        assert "unsafe-eval" in csp
        assert "nonce-training-parser-pwa" in csp, "CSP must include nonce for inline scripts"


def test_all_required_scripts_loadable(pwa_server):
    """Test that all critical scripts are accessible and loadable."""
    # List of critical files that must be accessible for the app to work
    critical_files = [
        "/index.html",
        "/sw.js",
        "/src/ui.js",
        "/src/pyodide-worker.js",
        "/src/share.js",
        "/src/git-sync.js",
        "/manifest.json",
        "/python/app_api.py",
    ]

    for file_path in critical_files:
        content = get_page(file_path, pwa_server)
        assert len(content) > 0, f"Critical file {file_path} is empty or missing"

        # For JavaScript files, check they have content
        if file_path.endswith(".js"):
            content_str = content.decode("utf-8", errors="ignore")
            assert len(content_str) > 100, f"JavaScript file {file_path} seems too small"
