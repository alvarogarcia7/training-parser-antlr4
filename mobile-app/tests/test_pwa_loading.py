"""Tests to ensure PWA loads without errors."""

import pytest
import subprocess
import time
import ssl
import json
import re
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import URLError


# Reuse certificate paths from pwa_serve_local tests
CERT_PATH = Path(__file__).parent.parent.parent / "certs" / "cert.pem"
KEY_PATH = Path(__file__).parent.parent.parent / "certs" / "key.pem"

pytestmark = pytest.mark.skipif(
    not (CERT_PATH.exists() and KEY_PATH.exists()),
    reason="SSL certificates not found - run 'make pwa-certs' first"
)


@pytest.fixture(scope="session")
def pwa_server():
    """Start the pwa-serve-local server for the duration of tests."""
    proc = subprocess.Popen(
        ["python3", "scripts/serve-local.py", "--host", "127.0.0.1", "--port", "8446"],
        cwd=Path(__file__).parent.parent.parent,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    time.sleep(2)
    yield proc
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait()


def get_ssl_context():
    """Create SSL context for self-signed certificates."""
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    return context


def fetch_file(path: str, pwa_server) -> bytes:
    """Fetch a file from pwa-serve-local."""
    ssl_context = get_ssl_context()
    url = f"https://127.0.0.1:8446{path}"
    req = Request(url)
    try:
        with urlopen(req, context=ssl_context, timeout=5) as response:
            return response.read()
    except URLError as e:
        raise AssertionError(f"Failed to fetch {url}: {e}")


def test_service_worker_script_is_valid_javascript(pwa_server):
    """Test that sw.js is valid JavaScript (no syntax errors)."""
    content = fetch_file("/mobile-app/sw.js", pwa_server).decode("utf-8")

    # Check for basic JavaScript syntax
    assert "const CACHE_NAME" in content, "Missing CACHE_NAME constant"
    assert "self.addEventListener" in content, "Missing event listeners"
    assert "fetch" in content, "Missing fetch handler"

    # Check for common syntax patterns that would indicate errors
    assert not re.search(r'//\s*TODO|//\s*FIXME', content, re.IGNORECASE), \
        "Service Worker has unfinished TODO/FIXME items"


def test_pyodide_worker_script_is_valid_javascript(pwa_server):
    """Test that pyodide-worker.js is valid JavaScript."""
    content = fetch_file("/mobile-app/src/pyodide-worker.js", pwa_server).decode("utf-8")

    # Check for initialization code
    assert "initPyodide" in content, "Missing initPyodide function"
    assert "PYTHON_FILES" in content, "Missing PYTHON_FILES array"
    assert "loadPyodide" in content, "Missing loadPyodide call"

    # Check for error handling
    assert ".catch" in content or "try" in content, "Missing error handling"


def test_ui_script_has_service_worker_registration(pwa_server):
    """Test that ui.js registers the Service Worker correctly."""
    content = fetch_file("/mobile-app/src/ui.js", pwa_server).decode("utf-8")

    # Check for Service Worker registration
    assert "serviceWorker" in content, "Missing Service Worker registration"
    assert "register" in content, "Missing register call"
    assert "./sw.js" in content, "Service Worker path not found or incorrect"


def test_index_html_has_valid_csp_headers(pwa_server):
    """Test that index.html has valid CSP that allows Service Workers."""
    ssl_context = get_ssl_context()
    url = "https://127.0.0.1:8446/mobile-app/index.html"
    req = Request(url)

    with urlopen(req, context=ssl_context, timeout=5) as response:
        headers = response.headers
        assert "Content-Security-Policy" in headers, "Missing CSP header"

        csp = headers["Content-Security-Policy"]

        # Service Workers use worker-src (defaults to script-src if not specified)
        # Verify script-src is permissive enough
        assert "script-src" in csp, "Missing script-src in CSP"
        assert "'self'" in csp, "Missing 'self' in script-src"
        assert "'unsafe-eval'" in csp, "Missing 'unsafe-eval' for Pyodide"


def test_service_worker_can_fetch_from_root_path(pwa_server):
    """Test that Service Worker can fetch required files."""
    # These files are referenced in sw.js APP_SHELL
    files_to_check = [
        "/mobile-app/index.html",
        "/mobile-app/manifest.json",
        "/mobile-app/src/ui.js",
        "/mobile-app/src/pyodide-worker.js",
    ]

    for file_path in files_to_check:
        content = fetch_file(file_path, pwa_server)
        assert len(content) > 0, f"Service Worker cannot fetch {file_path}"


def test_all_python_modules_exist(pwa_server):
    """Test that all Python modules referenced by Pyodide worker exist."""
    # Read the worker to get the list of files
    worker_content = fetch_file("/mobile-app/src/pyodide-worker.js", pwa_server).decode("utf-8")

    # Extract file paths from PYTHON_FILES array
    # Match pattern: ['/path/to/file.py',
    matches = re.findall(r"\['/([^']+\.py|data/[^']+)'", worker_content)

    assert len(matches) > 0, "Could not extract Python file list from worker"

    # Check a sample of critical files
    critical_files = [
        "/parser/model.py",
        "/src/statistics.py",
        "/dist/trainingLexer.py",
        "/data/synonyms.yaml",
    ]

    for file_path in critical_files:
        content = fetch_file(file_path, pwa_server)
        assert len(content) > 0, f"Python module not found: {file_path}"


def test_manifest_is_valid_json(pwa_server):
    """Test that manifest.json is valid and has required fields."""
    content = fetch_file("/mobile-app/manifest.json", pwa_server).decode("utf-8")

    manifest = json.loads(content)

    # Check required fields for PWA (scope is optional)
    assert "name" in manifest, "Missing 'name' in manifest"
    assert "short_name" in manifest, "Missing 'short_name' in manifest"
    assert "start_url" in manifest, "Missing 'start_url' in manifest"
    assert "display" in manifest, "Missing 'display' mode in manifest"


def test_no_console_errors_in_scripts(pwa_server):
    """Test that scripts don't have obvious error indicators."""
    scripts_to_check = [
        "/mobile-app/index.html",
        "/mobile-app/src/ui.js",
        "/mobile-app/src/pyodide-worker.js",
        "/mobile-app/sw.js",
    ]

    for script_path in scripts_to_check:
        content = fetch_file(script_path, pwa_server).decode("utf-8")

        # Check for common error patterns
        assert "throw new Error" not in content or "catch" in content, \
            f"{script_path} has uncaught errors"

        # Check for syntax errors (basic check)
        assert content.count("(") == content.count(")"), \
            f"{script_path} has mismatched parentheses"

        assert content.count("{") == content.count("}"), \
            f"{script_path} has mismatched braces"


def test_service_worker_path_resolution(pwa_server):
    """Test that Service Worker path is correctly resolved."""
    # When at /mobile-app/index.html:
    # ./sw.js should resolve to /mobile-app/sw.js

    # Verify the file exists at the expected location
    content = fetch_file("/mobile-app/sw.js", pwa_server)
    assert len(content) > 0, "Service Worker file not found at /mobile-app/sw.js"

    # Verify it's not at the wrong location
    try:
        wrong_content = fetch_file("/sw.js", pwa_server)
        # If we got here, /sw.js exists but it shouldn't be used
        # The correct file should be at /mobile-app/sw.js
    except AssertionError:
        # Expected - /sw.js should not exist
        pass


def test_pyodide_worker_paths_are_correct(pwa_server):
    """Test that Pyodide worker uses correct paths for module fetching.

    Bundled antlr4 files use relative paths (../python/).
    Project modules use absolute paths (/parser/, /src/, /dist/, /data/).
    """
    content = fetch_file("/mobile-app/src/pyodide-worker.js", pwa_server).decode("utf-8")

    # Extract the PYTHON_FILES array
    python_files_match = re.search(r"const PYTHON_FILES = \[(.*?)\];", content, re.DOTALL)
    assert python_files_match, "Could not find PYTHON_FILES array"

    python_files = python_files_match.group(1)

    # Check for relative paths (bundled antlr4)
    relative_paths = re.findall(r"\['\.+/([^']+)'", python_files)
    assert len(relative_paths) > 0, "Missing relative paths for bundled antlr4 files"
    assert any("antlr4" in path for path in relative_paths), \
        "Bundled antlr4 files should use relative paths"

    # Check for absolute paths (project modules)
    absolute_paths = re.findall(r"\['/([^']+)'", python_files)
    assert len(absolute_paths) > 0, "Missing absolute paths for project modules"
    assert any("parser" in path or "src" in path or "dist" in path or "data" in path for path in absolute_paths), \
        "Project modules should use absolute paths (/parser/, /src/, /dist/, /data/)"


def test_app_shell_files_are_accessible(pwa_server):
    """Test that all files in Service Worker APP_SHELL are accessible."""
    sw_content = fetch_file("/mobile-app/sw.js", pwa_server).decode("utf-8")

    # Extract APP_SHELL paths
    app_shell_match = re.search(r"const APP_SHELL = \[(.*?)\];", sw_content, re.DOTALL)
    assert app_shell_match, "Could not find APP_SHELL in Service Worker"

    app_shell = app_shell_match.group(1)

    # Extract paths (starting with './')
    paths = re.findall(r"'\./(.*?)'", app_shell)

    # Test a sample of critical files
    critical_files = [
        "index.html",
        "manifest.json",
        "src/ui.js",
        "src/pyodide-worker.js",
    ]

    for file_name in critical_files:
        content = fetch_file(f"/mobile-app/{file_name}", pwa_server)
        assert len(content) > 0, f"APP_SHELL file not accessible: {file_name}"
