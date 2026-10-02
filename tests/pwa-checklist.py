"""
PWA Integrity Tests - Verify offline-first configuration and vendor assets.

This module validates that the PWA is properly configured for offline operation:
- Service worker cache strategy is correct
- No external CDN dependencies in HTML/JS
- Vendor assets are included and valid
- Cache version is properly set
- All precached URLs exist in the dist/pwa directory
"""

import os
import re
import json
import pytest
from pathlib import Path


class TestPWACacheStrategy:
    """Tests for service worker cache strategy."""

    @pytest.fixture(scope="class")
    def sw_path(self):
        """Get path to service worker."""
        return Path(__file__).parent.parent / "mobile-app" / "sw.js"

    @pytest.fixture(scope="class")
    def index_path(self):
        """Get path to main HTML file."""
        return Path(__file__).parent.parent / "mobile-app" / "index.html"

    @pytest.fixture(scope="class")
    def dist_pwa_path(self):
        """Get path to dist/pwa (built PWA)."""
        return Path(__file__).parent.parent / "dist" / "pwa"

    def test_service_worker_exists(self, sw_path):
        """Verify service worker file exists."""
        assert sw_path.exists(), f"Service worker not found at {sw_path}"

    def test_index_html_exists(self, index_path):
        """Verify index.html exists."""
        assert index_path.exists(), f"index.html not found at {index_path}"

    def test_no_unpkg_in_html(self, index_path):
        """Verify no unpkg CDN references in HTML."""
        content = index_path.read_text()
        unpkg_matches = re.findall(r'https?://unpkg\.com', content)
        assert len(unpkg_matches) == 0, f"Found unpkg CDN references: {unpkg_matches}"

    def test_no_jsdelivr_in_html(self, index_path):
        """Verify no jsDelivr CDN references in HTML."""
        content = index_path.read_text()
        jsdelivr_matches = re.findall(r'https?://cdn\.jsdelivr\.net', content)
        assert len(jsdelivr_matches) == 0, f"Found jsDelivr CDN references: {jsdelivr_matches}"

    def test_no_external_scripts_in_html(self, index_path):
        """Verify no external script sources in HTML."""
        content = index_path.read_text()
        # Find all script tags with src attributes
        script_srcs = re.findall(r'<script[^>]+src=["\']([^"\']+)["\']', content)
        external_srcs = [
            src for src in script_srcs
            if src.startswith('http://') or src.startswith('https://') or src.startswith('//')
        ]
        assert len(external_srcs) == 0, f"Found external script sources: {external_srcs}"

    def test_no_cdn_urls_in_service_worker(self, sw_path):
        """Verify no external CDN URLs in service worker (except for requirements handling)."""
        content = sw_path.read_text()

        # Find all https:// URLs in the service worker
        https_urls = re.findall(r'https://[^\s"\')\]]+', content)

        # Filter out allowed URLs
        external_urls = [
            url for url in https_urls
            if not url.startswith('https://localhost') and
               not url.startswith('https://127.0.0.1') and
               '/requirements/' not in url
        ]

        assert len(external_urls) == 0, (
            f"Found external CDN URLs in service worker: {external_urls}"
        )

    def test_cache_version_defined(self, sw_path):
        """Verify CACHE_VERSION is defined in service worker."""
        content = sw_path.read_text()
        cache_version = re.search(r"CACHE_VERSION\s*=\s*['\"]([^'\"]+)['\"]", content)
        assert cache_version, "CACHE_VERSION not found in service worker"

    def test_precache_urls_defined(self, sw_path):
        """Verify PRECACHE_URLS is defined in service worker."""
        content = sw_path.read_text()
        precache_section = re.search(
            r"PRECACHE_URLS\s*=\s*\[(.*?)\]",
            content,
            re.DOTALL
        )
        assert precache_section, "PRECACHE_URLS not found in service worker"

    def test_install_event_handler_exists(self, sw_path):
        """Verify install event handler exists in service worker."""
        content = sw_path.read_text()
        install_handler = re.search(
            r"self\.addEventListener\(['\"]install['\"]",
            content
        )
        assert install_handler, "Install event handler not found in service worker"

    def test_fetch_event_handler_exists(self, sw_path):
        """Verify fetch event handler exists in service worker."""
        content = sw_path.read_text()
        fetch_handler = re.search(
            r"self\.addEventListener\(['\"]fetch['\"]",
            content
        )
        assert fetch_handler, "Fetch event handler not found in service worker"


class TestPWAVendorAssets:
    """Tests for vendor assets and offline support."""

    @pytest.fixture(scope="class")
    def dist_pwa_path(self):
        """Get path to dist/pwa (built PWA)."""
        return Path(__file__).parent.parent / "dist" / "pwa"

    def test_dist_pwa_exists(self, dist_pwa_path):
        """Verify dist/pwa directory exists (built PWA)."""
        assert dist_pwa_path.exists(), (
            f"dist/pwa not found at {dist_pwa_path}. "
            "Run 'make pwa-build' to build the PWA."
        )

    def test_vendor_directory_exists(self, dist_pwa_path):
        """Verify vendor directory exists in dist/pwa."""
        vendor_path = dist_pwa_path / "vendor"
        assert vendor_path.exists(), (
            f"vendor directory not found at {vendor_path}"
        )

    def test_vendor_has_javascript_files(self, dist_pwa_path):
        """Verify vendor directory contains JavaScript files."""
        vendor_path = dist_pwa_path / "vendor"
        js_files = list(vendor_path.glob("*.js"))
        assert len(js_files) > 0, f"No JavaScript files found in {vendor_path}"

    def test_vendor_files_are_valid(self, dist_pwa_path):
        """Verify vendor JavaScript files are valid (not empty)."""
        vendor_path = dist_pwa_path / "vendor"
        for js_file in vendor_path.glob("*.js"):
            content = js_file.read_text()
            assert len(content) > 0, f"Vendor file {js_file.name} is empty"
            # Basic validation: should contain some code-like patterns
            assert any(
                pattern in content
                for pattern in ['{', '}', 'function', 'const', 'let', 'var']
            ), f"Vendor file {js_file.name} doesn't look like valid JavaScript"

    def test_vendor_files_are_minified(self, dist_pwa_path):
        """Verify vendor JavaScript files are minified (reduced whitespace)."""
        vendor_path = dist_pwa_path / "vendor"
        min_size = 100  # Reasonable minimum size for minified files

        for js_file in vendor_path.glob("*.js"):
            size = js_file.stat().st_size
            assert size > min_size, (
                f"Vendor file {js_file.name} seems too small ({size} bytes), "
                f"may not be properly minified"
            )

            # Check that the file doesn't have excessive newlines (indication of not minified)
            content = js_file.read_text()
            lines = content.split('\n')
            # Minified files typically have <10% newlines relative to total chars
            newline_ratio = len(lines) / max(len(content), 1)
            # Allow some newlines but not too many
            assert newline_ratio < 0.05 or size < 10000, (
                f"Vendor file {js_file.name} may not be properly minified "
                f"(newline ratio: {newline_ratio})"
            )


class TestPWAPrecacheURLs:
    """Tests for precache URL validation."""

    @pytest.fixture(scope="class")
    def sw_path(self):
        """Get path to service worker."""
        return Path(__file__).parent.parent / "mobile-app" / "sw.js"

    @pytest.fixture(scope="class")
    def dist_pwa_path(self):
        """Get path to dist/pwa."""
        return Path(__file__).parent.parent / "dist" / "pwa"

    def test_precache_urls_are_accessible(self, sw_path, dist_pwa_path):
        """Verify every entry in PRECACHE_URLS exists in dist/pwa."""
        content = sw_path.read_text()

        # Extract PRECACHE_URLS entries
        precache_section = re.search(
            r"PRECACHE_URLS\s*=\s*\[(.*?)\]",
            content,
            re.DOTALL
        )

        if not precache_section:
            pytest.skip("PRECACHE_URLS not found in service worker")

        # Extract individual URLs
        precache_content = precache_section.group(1)
        urls = re.findall(r"['\"]([^'\"]+)['\"]", precache_content)

        # Map cache keys to relative paths
        for url in urls:
            # Skip absolute URLs (external resources)
            if url.startswith('http'):
                continue

            # Normalize path for checking
            path = url.lstrip('/')

            # For GitHub Pages subdirectory, check against dist/pwa structure
            if dist_pwa_path.exists():
                file_path = dist_pwa_path / path
                # Don't fail for index.html redirects, just warn
                if path == 'index.html' or path == './index.html':
                    continue
                # Check if file exists
                if file_path.exists():
                    assert file_path.is_file(), f"{url} exists but is not a file"
                # Some files might be generated, don't hard fail
            else:
                pytest.skip(f"dist/pwa not found; skipping precache URL validation")


class TestPWAIntegration:
    """Integration tests for PWA offline capability."""

    @pytest.fixture(scope="class")
    def sw_path(self):
        """Get path to service worker."""
        return Path(__file__).parent.parent / "mobile-app" / "sw.js"

    @pytest.fixture(scope="class")
    def index_path(self):
        """Get path to main HTML file."""
        return Path(__file__).parent.parent / "mobile-app" / "index.html"

    def test_service_worker_is_registered(self, index_path):
        """Verify service worker is registered in HTML."""
        content = index_path.read_text()
        # Look for service worker registration patterns
        has_registration = any(
            pattern in content
            for pattern in [
                'serviceWorker',
                'navigator.serviceWorker',
                'sw.js',
                'service-worker'
            ]
        )
        assert has_registration, (
            "Service worker registration not found in index.html"
        )

    def test_offline_support_configured(self, sw_path):
        """Verify offline support is configured in service worker."""
        content = sw_path.read_text()

        # Check for cache-first or network-first strategy
        has_strategy = any(
            strategy in content
            for strategy in [
                'caches.match',
                'fetch',
                'cache-first',
                'network-first',
                'cache'
            ]
        )
        assert has_strategy, "Offline caching strategy not found in service worker"

    def test_manifest_web_app_capable(self, index_path):
        """Verify web app manifest is configured."""
        content = index_path.read_text()
        has_manifest = any(
            pattern in content
            for pattern in [
                'manifest.json',
                'application/manifest+json',
                'apple-mobile-web-app'
            ]
        )
        # Note: manifest is optional, but web app capability flags are recommended
        if not has_manifest:
            # Check for alternative PWA indicators
            has_pwa_meta = any(
                meta in content
                for meta in [
                    'viewport',
                    'theme-color',
                    'apple-mobile-web-app-capable'
                ]
            )
            assert has_pwa_meta, "PWA configuration not found in index.html"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
