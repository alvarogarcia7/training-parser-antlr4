"""Basic PWA functionality tests using Playwright."""

import pytest
import subprocess
import time
import os
from pathlib import Path
from playwright.sync_api import sync_playwright, expect


@pytest.fixture(scope="session")
def server():
    """Start the dev server for the duration of tests."""
    # Start server
    proc = subprocess.Popen(
        ["python3", "serve.py", "8765"],
        cwd=Path(__file__).parent.parent.parent,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    time.sleep(2)  # Wait for server to start
    yield proc
    # Cleanup
    proc.terminate()
    proc.wait(timeout=5)


@pytest.fixture
def page(server):
    """Get a Playwright page for testing."""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        yield page
        browser.close()


def test_pwa_loads(page):
    """Test that the PWA loads and shows initial UI."""
    page.goto("http://localhost:8765/mobile-app/")

    # Check basic elements exist
    expect(page.locator("h1")).to_contain_text("Training Parser")
    expect(page.locator("#workout-input")).to_be_visible()
    expect(page.locator("#parse-btn")).to_be_visible()
    expect(page.locator("#status")).to_be_visible()


def test_parse_button_enabled(page):
    """Test that parse button is clickable."""
    page.goto("http://localhost:8765/mobile-app/")

    button = page.locator("#parse-btn")
    expect(button).to_be_enabled()


def test_textarea_accepts_input(page):
    """Test that the textarea accepts input."""
    page.goto("http://localhost:8765/mobile-app/")

    textarea = page.locator("#workout-input")
    textarea.fill("Bench press 4x75kg")

    expect(textarea).to_have_value("Bench press 4x75kg")


def test_date_input_exists(page):
    """Test that date input has today's date by default."""
    page.goto("http://localhost:8765/mobile-app/")

    from datetime import date
    today = date.today().isoformat()

    date_input = page.locator("#workout-date")
    expect(date_input).to_have_value(today)


def test_settings_modal_can_open_close(page):
    """Test that settings modal opens and closes."""
    page.goto("http://localhost:8765/mobile-app/")

    settings_btn = page.locator("#settings-btn")
    settings_btn.click()

    modal = page.locator("#settings-modal")
    expect(modal).to_be_visible()

    # Close via cancel button
    cancel_btn = page.locator("#settings-cancel-btn")
    cancel_btn.click()

    expect(modal).not_to_be_visible()


def test_logs_panel_hidden_initially(page):
    """Test that logs panel is hidden on page load."""
    page.goto("http://localhost:8765/mobile-app/")

    logs_section = page.locator("#logs-section")
    expect(logs_section).to_have_attribute("hidden", "")


def test_log_level_filter_exists(page):
    """Test that log level filter dropdown exists."""
    page.goto("http://localhost:8765/mobile-app/")

    filter_select = page.locator("#log-level-filter")
    expect(filter_select).to_be_visible()

    # Check options
    options = filter_select.locator("option")
    expect(options).to_have_count(4)


def test_localStorage_persistence(page):
    """Test that input is saved to localStorage."""
    page.goto("http://localhost:8765/mobile-app/")

    # Set values
    textarea = page.locator("#workout-input")
    textarea.fill("Squat 10x70kg")
    textarea.blur()  # Trigger change event

    date_input = page.locator("#workout-date")
    date_input.fill("2026-09-12")
    date_input.blur()

    # Reload page
    page.reload()

    # Check values persisted
    expect(textarea).to_have_value("Squat 10x70kg")
    expect(date_input).to_have_value("2026-09-12")


def test_share_button_visible(page):
    """Test that share button is present."""
    page.goto("http://localhost:8765/mobile-app/")

    share_btn = page.locator("#share-btn")
    expect(share_btn).to_be_visible()
