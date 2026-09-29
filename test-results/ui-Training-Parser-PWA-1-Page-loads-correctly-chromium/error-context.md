# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: ui.spec.js >> Training Parser PWA >> 1. Page loads correctly
- Location: e2e/ui.spec.js:14:7

# Error details

```
Error: expect(page).toHaveTitle(expected) failed

Expected: "Training Parser"
Received: "Directory listing for /"
Timeout:  5000ms

Call log:
  - Expect "toHaveTitle" with timeout 5000ms
    9 × locator resolved to <html lang="en">…</html>
      - unexpected value "Directory listing for /"

```

```yaml
- heading "Directory listing for /" [level=1]
- separator
- list:
  - listitem:
    - link ".actrc":
      - /url: .actrc
  - listitem:
    - link ".env.local.example":
      - /url: .env.local.example
  - listitem:
    - link ".env.sh":
      - /url: .env.sh
  - listitem:
    - link ".git":
      - /url: .git
  - listitem:
    - link ".github/":
      - /url: .github/
  - listitem:
    - link ".gitignore":
      - /url: .gitignore
  - listitem:
    - link ".hypothesis/":
      - /url: .hypothesis/
  - listitem:
    - link ".mypy_cache/":
      - /url: .mypy_cache/
  - listitem:
    - link ".npmrc":
      - /url: .npmrc
  - listitem:
    - link ".pre-commit-config.yaml":
      - /url: .pre-commit-config.yaml
  - listitem:
    - link ".pytest_cache/":
      - /url: .pytest_cache/
  - listitem:
    - link ".python-version":
      - /url: .python-version
  - listitem:
    - link ".venv/":
      - /url: .venv/
  - listitem:
    - link "__pycache__/":
      - /url: __pycache__/
  - listitem:
    - link "AGENTS.md":
      - /url: AGENTS.md
  - listitem:
    - link "antlr-4.9.3-complete.jar":
      - /url: antlr-4.9.3-complete.jar
  - listitem:
    - link "backlog/":
      - /url: backlog/
  - listitem:
    - link "CHANGELOG_DOT_NOTATION.md":
      - /url: CHANGELOG_DOT_NOTATION.md
  - listitem:
    - link "CHANGELOG_SYNONYMS.md":
      - /url: CHANGELOG_SYNONYMS.md
  - listitem:
    - link "CLAUDE.md":
      - /url: CLAUDE.md
  - listitem:
    - link "cli.py":
      - /url: cli.py
  - listitem:
    - link "compact_from_json.py":
      - /url: compact_from_json.py
  - listitem:
    - link "COMPLIANCE_CHECKLIST.md":
      - /url: COMPLIANCE_CHECKLIST.md
  - listitem:
    - link "CORS_LIMITATIONS.md":
      - /url: CORS_LIMITATIONS.md
  - listitem:
    - link "CORS_PROXY_TESTING.md":
      - /url: CORS_PROXY_TESTING.md
  - listitem:
    - link "data/":
      - /url: data/
  - listitem:
    - link "data.txt.sample":
      - /url: data.txt.sample
  - listitem:
    - link "DEV_CREDENTIALS.md":
      - /url: DEV_CREDENTIALS.md
  - listitem:
    - link "dist/":
      - /url: dist/
  - listitem:
    - link "Dockerfile":
      - /url: Dockerfile
  - listitem:
    - link "e2e/":
      - /url: e2e/
  - listitem:
    - link "envelope.py":
      - /url: envelope.py
  - listitem:
    - link "ENVELOPE_IMPLEMENTATION.md":
      - /url: ENVELOPE_IMPLEMENTATION.md
  - listitem:
    - link "ENVELOPE_QUICK_REFERENCE.md":
      - /url: ENVELOPE_QUICK_REFERENCE.md
  - listitem:
    - link "ENVELOPE_README.md":
      - /url: ENVELOPE_README.md
  - listitem:
    - link "envelope_tool.py":
      - /url: envelope_tool.py
  - listitem:
    - link "ERROR_HANDLING.md":
      - /url: ERROR_HANDLING.md
  - listitem:
    - link "examples/":
      - /url: examples/
  - listitem:
    - link "GIT_SYNC_TROUBLESHOOTING.md":
      - /url: GIT_SYNC_TROUBLESHOOTING.md
  - listitem:
    - link "GITHUB_PAGES_SETUP.md":
      - /url: GITHUB_PAGES_SETUP.md
  - listitem:
    - link "GITHUB_SETUP.md":
      - /url: GITHUB_SETUP.md
  - listitem:
    - link "GRAMMAR_DOCUMENTATION_INDEX.md":
      - /url: GRAMMAR_DOCUMENTATION_INDEX.md
  - listitem:
    - link "GRAMMAR_DOT_NOTATION.md":
      - /url: GRAMMAR_DOT_NOTATION.md
  - listitem:
    - link "GRAMMAR_FORMATS.md":
      - /url: GRAMMAR_FORMATS.md
  - listitem:
    - link "GRAMMAR_QUICK_REFERENCE.md":
      - /url: GRAMMAR_QUICK_REFERENCE.md
  - listitem:
    - link "GRAMMAR_TESTING_SUMMARY.md":
      - /url: GRAMMAR_TESTING_SUMMARY.md
  - listitem:
    - link "IMPLEMENTATION_ERROR_HANDLING.md":
      - /url: IMPLEMENTATION_ERROR_HANDLING.md
  - listitem:
    - link "IMPLEMENTATION_SUMMARY.md":
      - /url: IMPLEMENTATION_SUMMARY.md
  - listitem:
    - link "json_validator.py":
      - /url: json_validator.py
  - listitem:
    - link "launch_nvim_test.sh":
      - /url: launch_nvim_test.sh
  - listitem:
    - link "LOCAL_GIT_TESTING.md":
      - /url: LOCAL_GIT_TESTING.md
  - listitem:
    - link "LOCAL_NETWORK.md":
      - /url: LOCAL_NETWORK.md
  - listitem:
    - link "lsp/":
      - /url: lsp/
  - listitem:
    - link "LSP_FEATURES.md":
      - /url: LSP_FEATURES.md
  - listitem:
    - link "LSP_GUIDE.md":
      - /url: LSP_GUIDE.md
  - listitem:
    - link "LSP_IMPLEMENTATION_SUMMARY.md":
      - /url: LSP_IMPLEMENTATION_SUMMARY.md
  - listitem:
    - link "main.py":
      - /url: main.py
  - listitem:
    - link "main_export.py":
      - /url: main_export.py
  - listitem:
    - link "Makefile":
      - /url: Makefile
  - listitem:
    - link "makefiles/":
      - /url: makefiles/
  - listitem:
    - link "MANIFEST.in":
      - /url: MANIFEST.in
  - listitem:
    - link "MIGRATION_SYNONYMS.md":
      - /url: MIGRATION_SYNONYMS.md
  - listitem:
    - link "MISSING_FIELDS.md":
      - /url: MISSING_FIELDS.md
  - listitem:
    - link "mobile-app/":
      - /url: mobile-app/
  - listitem:
    - link "mypy.ini":
      - /url: mypy.ini
  - listitem:
    - link "nats_subscriber.py":
      - /url: nats_subscriber.py
  - listitem:
    - link "node_modules/":
      - /url: node_modules/
  - listitem:
    - link "NVIM_LSP_SETUP.md":
      - /url: NVIM_LSP_SETUP.md
  - listitem:
    - link "package-lock.json":
      - /url: package-lock.json
  - listitem:
    - link "package.json":
      - /url: package.json
  - listitem:
    - link "parse_to_json.py":
      - /url: parse_to_json.py
  - listitem:
    - link "parser/":
      - /url: parser/
  - listitem:
    - link "PHASE2_ACCEPTANCE_VERIFICATION.md":
      - /url: PHASE2_ACCEPTANCE_VERIFICATION.md
  - listitem:
    - link "playwright-report/":
      - /url: playwright-report/
  - listitem:
    - link "playwright.config.js":
      - /url: playwright.config.js
  - listitem:
    - link "PRD-training-notation-grammar.md":
      - /url: PRD-training-notation-grammar.md
  - listitem:
    - link "PRD_DOT_NOTATION.md":
      - /url: PRD_DOT_NOTATION.md
  - listitem:
    - link "PRD_RIR_SUPPORT.md":
      - /url: PRD_RIR_SUPPORT.md
  - listitem:
    - link "PRD_VALIDATION.md":
      - /url: PRD_VALIDATION.md
  - listitem:
    - link "PRD_VALIDATION_SUMMARY.md":
      - /url: PRD_VALIDATION_SUMMARY.md
  - listitem:
    - link "programmer.py":
      - /url: programmer.py
  - listitem:
    - link "PWA_DEBUG_LOGGING.md":
      - /url: PWA_DEBUG_LOGGING.md
  - listitem:
    - link "PWA_DEPLOYMENT.md":
      - /url: PWA_DEPLOYMENT.md
  - listitem:
    - link "PWA_SYNC_GUIDE.md":
      - /url: PWA_SYNC_GUIDE.md
  - listitem:
    - link "PWA_SYNC_QUICK_START.md":
      - /url: PWA_SYNC_QUICK_START.md
  - listitem:
    - link "pyproject.toml":
      - /url: pyproject.toml
  - listitem:
    - link "QUICK_START_ERROR_HANDLING.md":
      - /url: QUICK_START_ERROR_HANDLING.md
  - listitem:
    - link "QUICK_START_GRAMMAR.md":
      - /url: QUICK_START_GRAMMAR.md
  - listitem:
    - link "QUICK_START_SYNONYMS.md":
      - /url: QUICK_START_SYNONYMS.md
  - listitem:
    - link "QUICK_START_WORKOUT_SESSIONS.md":
      - /url: QUICK_START_WORKOUT_SESSIONS.md
  - listitem:
    - link "README-ACT.md":
      - /url: README-ACT.md
  - listitem:
    - link "README.md":
      - /url: README.md
  - listitem:
    - link "requirements/":
      - /url: requirements/
  - listitem:
    - link "requirements.txt":
      - /url: requirements.txt
  - listitem:
    - link "schema/":
      - /url: schema/
  - listitem:
    - link "schema_validator.py":
      - /url: schema_validator.py
  - listitem:
    - link "scripts/":
      - /url: scripts/
  - listitem:
    - link "serve.py":
      - /url: serve.py
  - listitem:
    - link "setup-uv.sh":
      - /url: setup-uv.sh
  - listitem:
    - link "splitter.py":
      - /url: splitter.py
  - listitem:
    - link "src/":
      - /url: src/
  - listitem:
    - link "SYNC_ERROR_FIX.md":
      - /url: SYNC_ERROR_FIX.md
  - listitem:
    - link "SYNTAX.md":
      - /url: SYNTAX.md
  - listitem:
    - link "test-cors-access.js":
      - /url: test-cors-access.js
  - listitem:
    - link "test-results/":
      - /url: test-results/
  - listitem:
    - link "test-results.json":
      - /url: test-results.json
  - listitem:
    - link "TEST_COVERAGE_MATRIX.md":
      - /url: TEST_COVERAGE_MATRIX.md
  - listitem:
    - link "test_diagnostics.py":
      - /url: test_diagnostics.py
  - listitem:
    - link "test_invalid.training":
      - /url: test_invalid.training
  - listitem:
    - link "test_json_validator.py":
      - /url: test_json_validator.py
  - listitem:
    - link "test_schema_validator.py":
      - /url: test_schema_validator.py
  - listitem:
    - link "test_set_to_dict.py":
      - /url: test_set_to_dict.py
  - listitem:
    - link "tests/":
      - /url: tests/
  - listitem:
    - link "training-sample.txt":
      - /url: training-sample.txt
  - listitem:
    - link "training-sample_initial.txt":
      - /url: training-sample_initial.txt
  - listitem:
    - link "training.g4":
      - /url: training.g4
  - listitem:
    - link "uv.lock":
      - /url: uv.lock
  - listitem:
    - link "validate_bench_centric.py":
      - /url: validate_bench_centric.py
  - listitem:
    - link "validate_set_centric.py":
      - /url: validate_set_centric.py
  - listitem:
    - link "validate_synonyms_yaml.py":
      - /url: validate_synonyms_yaml.py
  - listitem:
    - link "VALIDATION_INDEX.md":
      - /url: VALIDATION_INDEX.md
  - listitem:
    - link "weight_parser/":
      - /url: weight_parser/
  - listitem:
    - link "WORKOUT_SESSION_IMPLEMENTATION.md":
      - /url: WORKOUT_SESSION_IMPLEMENTATION.md
  - listitem:
    - link "WORKOUT_SESSION_TESTING.md":
      - /url: WORKOUT_SESSION_TESTING.md
- separator
```

# Test source

```ts
  1   | import { test, expect } from '@playwright/test';
  2   | import fs from 'fs';
  3   | import path from 'path';
  4   | 
  5   | // Test data
  6   | const VALID_WORKOUT = `Bench press 4x75kg
  7   | Squat 5x70kg
  8   | Deadlift 3x100kg`;
  9   | 
  10  | const INVALID_WORKOUT = `This is not a valid workout format
  11  | Random gibberish here`;
  12  | 
  13  | test.describe('Training Parser PWA', () => {
  14  |   test('1. Page loads correctly', async ({ page }) => {
  15  |     // Navigate to the PWA
  16  |     await page.goto('/');
  17  | 
  18  |     // Assert page title
> 19  |     await expect(page).toHaveTitle('Training Parser');
      |                        ^ Error: expect(page).toHaveTitle(expected) failed
  20  | 
  21  |     // Assert header
  22  |     await expect(page.locator('header h1')).toContainText('Training Parser');
  23  | 
  24  |     // Assert main elements exist
  25  |     await expect(page.locator('#workout-input')).toBeVisible();
  26  |     await expect(page.locator('#parse-btn')).toBeVisible();
  27  |     await expect(page.locator('#save-btn')).toBeVisible();
  28  |     await expect(page.locator('#pull-btn')).toBeVisible();
  29  |     await expect(page.locator('#sync-btn')).toBeVisible();
  30  | 
  31  |     // Assert status indicator
  32  |     const status = page.locator('#status');
  33  |     await status.waitFor({ state: 'visible', timeout: 5000 });
  34  | 
  35  |     // Assert date input is populated with today's date
  36  |     const dateInput = page.locator('#workout-date');
  37  |     const dateValue = await dateInput.inputValue();
  38  |     const today = new Date().toISOString().split('T')[0];
  39  |     expect(dateValue).toBe(today);
  40  |   });
  41  | 
  42  |   test('2. Insert valid line and assert parsing', async ({ page }) => {
  43  |     await page.goto('/');
  44  | 
  45  |     // Wait for page to load
  46  |     await page.locator('#status').waitFor({ state: 'visible', timeout: 5000 });
  47  | 
  48  |     // Input valid workout
  49  |     const workoutInput = page.locator('#workout-input');
  50  |     await workoutInput.fill(VALID_WORKOUT);
  51  | 
  52  |     // Set date
  53  |     const today = new Date().toISOString().split('T')[0];
  54  |     await page.locator('#workout-date').fill(today);
  55  | 
  56  |     // Click parse button
  57  |     await page.locator('#parse-btn').click();
  58  | 
  59  |     // Wait for results to appear
  60  |     await page.locator('#results-section').waitFor({ state: 'visible', timeout: 5000 });
  61  | 
  62  |     // Assert results are shown
  63  |     const resultsSection = page.locator('#results-section');
  64  |     await expect(resultsSection).toBeVisible();
  65  | 
  66  |     // Assert summary shows parsed exercises
  67  |     const summaryText = page.locator('#summary-text');
  68  |     await expect(summaryText).toContainText(/(\d+) exercises?/i);
  69  | 
  70  |     // Assert results table exists with data
  71  |     const resultsTable = page.locator('table');
  72  |     await expect(resultsTable).toBeVisible();
  73  | 
  74  |     // Assert no errors section
  75  |     const errorsSection = page.locator('#errors-section');
  76  |     await expect(errorsSection).not.toBeVisible();
  77  |   });
  78  | 
  79  |   test('3. Insert invalid workout and assert error', async ({ page }) => {
  80  |     await page.goto('/');
  81  | 
  82  |     // Wait for page to load
  83  |     await page.locator('#status').waitFor({ state: 'visible', timeout: 5000 });
  84  | 
  85  |     // Input invalid workout
  86  |     const workoutInput = page.locator('#workout-input');
  87  |     await workoutInput.fill(INVALID_WORKOUT);
  88  | 
  89  |     // Set date
  90  |     const today = new Date().toISOString().split('T')[0];
  91  |     await page.locator('#workout-date').fill(today);
  92  | 
  93  |     // Click parse button
  94  |     await page.locator('#parse-btn').click();
  95  | 
  96  |     // Wait for errors to appear
  97  |     await page.locator('#errors-section').waitFor({ state: 'visible', timeout: 5000 });
  98  | 
  99  |     // Assert errors section is visible
  100 |     const errorsSection = page.locator('#errors-section');
  101 |     await expect(errorsSection).toBeVisible();
  102 | 
  103 |     // Assert error list has items
  104 |     const errorsList = page.locator('#errors-list li');
  105 |     const errorCount = await errorsList.count();
  106 |     expect(errorCount).toBeGreaterThan(0);
  107 | 
  108 |     // Assert results section is not visible (only errors)
  109 |     const resultsSection = page.locator('#results-section');
  110 |     await expect(resultsSection).not.toBeVisible();
  111 |   });
  112 | 
  113 |   test('4. Git sync - pull and push to remote', async ({ page }) => {
  114 |     // This test requires local git server setup
  115 |     // Setup: ensure make setup-local-git-server has been run
  116 | 
  117 |     await page.goto('/');
  118 | 
  119 |     // Wait for page to load
```