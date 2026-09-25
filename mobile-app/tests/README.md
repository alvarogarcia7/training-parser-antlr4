# PWA Browser Tests

Light integration tests for the Training Parser PWA using Playwright.

## Running Tests

```bash
# Run all PWA tests
make test-webapp

# Run specific test
uv run pytest mobile-app/tests/test_pwa_basic.py::test_pwa_loads -v

# Run with different verbosity
uv run pytest mobile-app/tests/ -vv

# Run tests in headed mode (see browser)
uv run pytest mobile-app/tests/ --headed
```

## What's Tested

✓ Page loads and shows UI elements  
✓ Textarea accepts input  
✓ Date input defaults to today  
✓ Settings modal can open/close  
✓ Log level filter dropdown works  
✓ LocalStorage persistence across page reloads  
✓ Share button exists  

## Pre-commit Integration

When you modify files in `mobile-app/`, the pre-commit hook automatically runs:
- `make test-webapp` - Browser tests (only for mobile-app changes)

When you modify other files:
- `make typecheck` - MyPy strict checking
- `make test-python` - Unit tests

## Setup Requirements

```bash
# Install playwright browsers (one-time)
uv run python3 -m playwright install chromium

# On Linux, you may need additional system libraries:
# sudo apt-get install libatk-1.0-0 libatk-bridge2.0-0 libgbm1 libpango-1.0-0
```

## Test Structure

Each test:
1. Starts the dev server on port 8765
2. Opens the PWA in headless Chromium
3. Interacts with the UI
4. Verifies expected behavior

Tests are isolated per function and share the server process for efficiency.
