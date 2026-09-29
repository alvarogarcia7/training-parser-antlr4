# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: ui.spec.js >> Training Parser PWA >> 2. Insert valid line and assert parsing
- Location: e2e/ui.spec.js:42:7

# Error details

```
TimeoutError: locator.waitFor: Timeout 5000ms exceeded.
Call log:
  - waiting for locator('#status') to be visible

```

# Page snapshot

```yaml
- generic [active] [ref=e1]:
  - heading "Directory listing for /" [level=1] [ref=e2]
  - separator [ref=e3]
  - list [ref=e4]:
    - listitem [ref=e5]:
      - link ".actrc" [ref=e6] [cursor=pointer]:
        - /url: .actrc
    - listitem [ref=e7]:
      - link ".env.local.example" [ref=e8] [cursor=pointer]:
        - /url: .env.local.example
    - listitem [ref=e9]:
      - link ".env.sh" [ref=e10] [cursor=pointer]:
        - /url: .env.sh
    - listitem [ref=e11]:
      - link ".git" [ref=e12] [cursor=pointer]:
        - /url: .git
    - listitem [ref=e13]:
      - link ".github/" [ref=e14] [cursor=pointer]:
        - /url: .github/
    - listitem [ref=e15]:
      - link ".gitignore" [ref=e16] [cursor=pointer]:
        - /url: .gitignore
    - listitem [ref=e17]:
      - link ".hypothesis/" [ref=e18] [cursor=pointer]:
        - /url: .hypothesis/
    - listitem [ref=e19]:
      - link ".mypy_cache/" [ref=e20] [cursor=pointer]:
        - /url: .mypy_cache/
    - listitem [ref=e21]:
      - link ".npmrc" [ref=e22] [cursor=pointer]:
        - /url: .npmrc
    - listitem [ref=e23]:
      - link ".pre-commit-config.yaml" [ref=e24] [cursor=pointer]:
        - /url: .pre-commit-config.yaml
    - listitem [ref=e25]:
      - link ".pytest_cache/" [ref=e26] [cursor=pointer]:
        - /url: .pytest_cache/
    - listitem [ref=e27]:
      - link ".python-version" [ref=e28] [cursor=pointer]:
        - /url: .python-version
    - listitem [ref=e29]:
      - link ".venv/" [ref=e30] [cursor=pointer]:
        - /url: .venv/
    - listitem [ref=e31]:
      - link "__pycache__/" [ref=e32] [cursor=pointer]:
        - /url: __pycache__/
    - listitem [ref=e33]:
      - link "AGENTS.md" [ref=e34] [cursor=pointer]:
        - /url: AGENTS.md
    - listitem [ref=e35]:
      - link "antlr-4.9.3-complete.jar" [ref=e36] [cursor=pointer]:
        - /url: antlr-4.9.3-complete.jar
    - listitem [ref=e37]:
      - link "backlog/" [ref=e38] [cursor=pointer]:
        - /url: backlog/
    - listitem [ref=e39]:
      - link "CHANGELOG_DOT_NOTATION.md" [ref=e40] [cursor=pointer]:
        - /url: CHANGELOG_DOT_NOTATION.md
    - listitem [ref=e41]:
      - link "CHANGELOG_SYNONYMS.md" [ref=e42] [cursor=pointer]:
        - /url: CHANGELOG_SYNONYMS.md
    - listitem [ref=e43]:
      - link "CLAUDE.md" [ref=e44] [cursor=pointer]:
        - /url: CLAUDE.md
    - listitem [ref=e45]:
      - link "cli.py" [ref=e46] [cursor=pointer]:
        - /url: cli.py
    - listitem [ref=e47]:
      - link "compact_from_json.py" [ref=e48] [cursor=pointer]:
        - /url: compact_from_json.py
    - listitem [ref=e49]:
      - link "COMPLIANCE_CHECKLIST.md" [ref=e50] [cursor=pointer]:
        - /url: COMPLIANCE_CHECKLIST.md
    - listitem [ref=e51]:
      - link "CORS_LIMITATIONS.md" [ref=e52] [cursor=pointer]:
        - /url: CORS_LIMITATIONS.md
    - listitem [ref=e53]:
      - link "CORS_PROXY_TESTING.md" [ref=e54] [cursor=pointer]:
        - /url: CORS_PROXY_TESTING.md
    - listitem [ref=e55]:
      - link "data/" [ref=e56] [cursor=pointer]:
        - /url: data/
    - listitem [ref=e57]:
      - link "data.txt.sample" [ref=e58] [cursor=pointer]:
        - /url: data.txt.sample
    - listitem [ref=e59]:
      - link "DEV_CREDENTIALS.md" [ref=e60] [cursor=pointer]:
        - /url: DEV_CREDENTIALS.md
    - listitem [ref=e61]:
      - link "dist/" [ref=e62] [cursor=pointer]:
        - /url: dist/
    - listitem [ref=e63]:
      - link "Dockerfile" [ref=e64] [cursor=pointer]:
        - /url: Dockerfile
    - listitem [ref=e65]:
      - link "e2e/" [ref=e66] [cursor=pointer]:
        - /url: e2e/
    - listitem [ref=e67]:
      - link "envelope.py" [ref=e68] [cursor=pointer]:
        - /url: envelope.py
    - listitem [ref=e69]:
      - link "ENVELOPE_IMPLEMENTATION.md" [ref=e70] [cursor=pointer]:
        - /url: ENVELOPE_IMPLEMENTATION.md
    - listitem [ref=e71]:
      - link "ENVELOPE_QUICK_REFERENCE.md" [ref=e72] [cursor=pointer]:
        - /url: ENVELOPE_QUICK_REFERENCE.md
    - listitem [ref=e73]:
      - link "ENVELOPE_README.md" [ref=e74] [cursor=pointer]:
        - /url: ENVELOPE_README.md
    - listitem [ref=e75]:
      - link "envelope_tool.py" [ref=e76] [cursor=pointer]:
        - /url: envelope_tool.py
    - listitem [ref=e77]:
      - link "ERROR_HANDLING.md" [ref=e78] [cursor=pointer]:
        - /url: ERROR_HANDLING.md
    - listitem [ref=e79]:
      - link "examples/" [ref=e80] [cursor=pointer]:
        - /url: examples/
    - listitem [ref=e81]:
      - link "GIT_SYNC_TROUBLESHOOTING.md" [ref=e82] [cursor=pointer]:
        - /url: GIT_SYNC_TROUBLESHOOTING.md
    - listitem [ref=e83]:
      - link "GITHUB_PAGES_SETUP.md" [ref=e84] [cursor=pointer]:
        - /url: GITHUB_PAGES_SETUP.md
    - listitem [ref=e85]:
      - link "GITHUB_SETUP.md" [ref=e86] [cursor=pointer]:
        - /url: GITHUB_SETUP.md
    - listitem [ref=e87]:
      - link "GRAMMAR_DOCUMENTATION_INDEX.md" [ref=e88] [cursor=pointer]:
        - /url: GRAMMAR_DOCUMENTATION_INDEX.md
    - listitem [ref=e89]:
      - link "GRAMMAR_DOT_NOTATION.md" [ref=e90] [cursor=pointer]:
        - /url: GRAMMAR_DOT_NOTATION.md
    - listitem [ref=e91]:
      - link "GRAMMAR_FORMATS.md" [ref=e92] [cursor=pointer]:
        - /url: GRAMMAR_FORMATS.md
    - listitem [ref=e93]:
      - link "GRAMMAR_QUICK_REFERENCE.md" [ref=e94] [cursor=pointer]:
        - /url: GRAMMAR_QUICK_REFERENCE.md
    - listitem [ref=e95]:
      - link "GRAMMAR_TESTING_SUMMARY.md" [ref=e96] [cursor=pointer]:
        - /url: GRAMMAR_TESTING_SUMMARY.md
    - listitem [ref=e97]:
      - link "IMPLEMENTATION_ERROR_HANDLING.md" [ref=e98] [cursor=pointer]:
        - /url: IMPLEMENTATION_ERROR_HANDLING.md
    - listitem [ref=e99]:
      - link "IMPLEMENTATION_SUMMARY.md" [ref=e100] [cursor=pointer]:
        - /url: IMPLEMENTATION_SUMMARY.md
    - listitem [ref=e101]:
      - link "json_validator.py" [ref=e102] [cursor=pointer]:
        - /url: json_validator.py
    - listitem [ref=e103]:
      - link "launch_nvim_test.sh" [ref=e104] [cursor=pointer]:
        - /url: launch_nvim_test.sh
    - listitem [ref=e105]:
      - link "LOCAL_GIT_TESTING.md" [ref=e106] [cursor=pointer]:
        - /url: LOCAL_GIT_TESTING.md
    - listitem [ref=e107]:
      - link "LOCAL_NETWORK.md" [ref=e108] [cursor=pointer]:
        - /url: LOCAL_NETWORK.md
    - listitem [ref=e109]:
      - link "lsp/" [ref=e110] [cursor=pointer]:
        - /url: lsp/
    - listitem [ref=e111]:
      - link "LSP_FEATURES.md" [ref=e112] [cursor=pointer]:
        - /url: LSP_FEATURES.md
    - listitem [ref=e113]:
      - link "LSP_GUIDE.md" [ref=e114] [cursor=pointer]:
        - /url: LSP_GUIDE.md
    - listitem [ref=e115]:
      - link "LSP_IMPLEMENTATION_SUMMARY.md" [ref=e116] [cursor=pointer]:
        - /url: LSP_IMPLEMENTATION_SUMMARY.md
    - listitem [ref=e117]:
      - link "main.py" [ref=e118] [cursor=pointer]:
        - /url: main.py
    - listitem [ref=e119]:
      - link "main_export.py" [ref=e120] [cursor=pointer]:
        - /url: main_export.py
    - listitem [ref=e121]:
      - link "Makefile" [ref=e122] [cursor=pointer]:
        - /url: Makefile
    - listitem [ref=e123]:
      - link "makefiles/" [ref=e124] [cursor=pointer]:
        - /url: makefiles/
    - listitem [ref=e125]:
      - link "MANIFEST.in" [ref=e126] [cursor=pointer]:
        - /url: MANIFEST.in
    - listitem [ref=e127]:
      - link "MIGRATION_SYNONYMS.md" [ref=e128] [cursor=pointer]:
        - /url: MIGRATION_SYNONYMS.md
    - listitem [ref=e129]:
      - link "MISSING_FIELDS.md" [ref=e130] [cursor=pointer]:
        - /url: MISSING_FIELDS.md
    - listitem [ref=e131]:
      - link "mobile-app/" [ref=e132] [cursor=pointer]:
        - /url: mobile-app/
    - listitem [ref=e133]:
      - link "mypy.ini" [ref=e134] [cursor=pointer]:
        - /url: mypy.ini
    - listitem [ref=e135]:
      - link "nats_subscriber.py" [ref=e136] [cursor=pointer]:
        - /url: nats_subscriber.py
    - listitem [ref=e137]:
      - link "node_modules/" [ref=e138] [cursor=pointer]:
        - /url: node_modules/
    - listitem [ref=e139]:
      - link "NVIM_LSP_SETUP.md" [ref=e140] [cursor=pointer]:
        - /url: NVIM_LSP_SETUP.md
    - listitem [ref=e141]:
      - link "package-lock.json" [ref=e142] [cursor=pointer]:
        - /url: package-lock.json
    - listitem [ref=e143]:
      - link "package.json" [ref=e144] [cursor=pointer]:
        - /url: package.json
    - listitem [ref=e145]:
      - link "parse_to_json.py" [ref=e146] [cursor=pointer]:
        - /url: parse_to_json.py
    - listitem [ref=e147]:
      - link "parser/" [ref=e148] [cursor=pointer]:
        - /url: parser/
    - listitem [ref=e149]:
      - link "PHASE2_ACCEPTANCE_VERIFICATION.md" [ref=e150] [cursor=pointer]:
        - /url: PHASE2_ACCEPTANCE_VERIFICATION.md
    - listitem [ref=e151]:
      - link "playwright-report/" [ref=e152] [cursor=pointer]:
        - /url: playwright-report/
    - listitem [ref=e153]:
      - link "playwright.config.js" [ref=e154] [cursor=pointer]:
        - /url: playwright.config.js
    - listitem [ref=e155]:
      - link "PRD-training-notation-grammar.md" [ref=e156] [cursor=pointer]:
        - /url: PRD-training-notation-grammar.md
    - listitem [ref=e157]:
      - link "PRD_DOT_NOTATION.md" [ref=e158] [cursor=pointer]:
        - /url: PRD_DOT_NOTATION.md
    - listitem [ref=e159]:
      - link "PRD_RIR_SUPPORT.md" [ref=e160] [cursor=pointer]:
        - /url: PRD_RIR_SUPPORT.md
    - listitem [ref=e161]:
      - link "PRD_VALIDATION.md" [ref=e162] [cursor=pointer]:
        - /url: PRD_VALIDATION.md
    - listitem [ref=e163]:
      - link "PRD_VALIDATION_SUMMARY.md" [ref=e164] [cursor=pointer]:
        - /url: PRD_VALIDATION_SUMMARY.md
    - listitem [ref=e165]:
      - link "programmer.py" [ref=e166] [cursor=pointer]:
        - /url: programmer.py
    - listitem [ref=e167]:
      - link "PWA_DEBUG_LOGGING.md" [ref=e168] [cursor=pointer]:
        - /url: PWA_DEBUG_LOGGING.md
    - listitem [ref=e169]:
      - link "PWA_DEPLOYMENT.md" [ref=e170] [cursor=pointer]:
        - /url: PWA_DEPLOYMENT.md
    - listitem [ref=e171]:
      - link "PWA_SYNC_GUIDE.md" [ref=e172] [cursor=pointer]:
        - /url: PWA_SYNC_GUIDE.md
    - listitem [ref=e173]:
      - link "PWA_SYNC_QUICK_START.md" [ref=e174] [cursor=pointer]:
        - /url: PWA_SYNC_QUICK_START.md
    - listitem [ref=e175]:
      - link "pyproject.toml" [ref=e176] [cursor=pointer]:
        - /url: pyproject.toml
    - listitem [ref=e177]:
      - link "QUICK_START_ERROR_HANDLING.md" [ref=e178] [cursor=pointer]:
        - /url: QUICK_START_ERROR_HANDLING.md
    - listitem [ref=e179]:
      - link "QUICK_START_GRAMMAR.md" [ref=e180] [cursor=pointer]:
        - /url: QUICK_START_GRAMMAR.md
    - listitem [ref=e181]:
      - link "QUICK_START_SYNONYMS.md" [ref=e182] [cursor=pointer]:
        - /url: QUICK_START_SYNONYMS.md
    - listitem [ref=e183]:
      - link "QUICK_START_WORKOUT_SESSIONS.md" [ref=e184] [cursor=pointer]:
        - /url: QUICK_START_WORKOUT_SESSIONS.md
    - listitem [ref=e185]:
      - link "README-ACT.md" [ref=e186] [cursor=pointer]:
        - /url: README-ACT.md
    - listitem [ref=e187]:
      - link "README.md" [ref=e188] [cursor=pointer]:
        - /url: README.md
    - listitem [ref=e189]:
      - link "requirements/" [ref=e190] [cursor=pointer]:
        - /url: requirements/
    - listitem [ref=e191]:
      - link "requirements.txt" [ref=e192] [cursor=pointer]:
        - /url: requirements.txt
    - listitem [ref=e193]:
      - link "schema/" [ref=e194] [cursor=pointer]:
        - /url: schema/
    - listitem [ref=e195]:
      - link "schema_validator.py" [ref=e196] [cursor=pointer]:
        - /url: schema_validator.py
    - listitem [ref=e197]:
      - link "scripts/" [ref=e198] [cursor=pointer]:
        - /url: scripts/
    - listitem [ref=e199]:
      - link "serve.py" [ref=e200] [cursor=pointer]:
        - /url: serve.py
    - listitem [ref=e201]:
      - link "setup-uv.sh" [ref=e202] [cursor=pointer]:
        - /url: setup-uv.sh
    - listitem [ref=e203]:
      - link "splitter.py" [ref=e204] [cursor=pointer]:
        - /url: splitter.py
    - listitem [ref=e205]:
      - link "src/" [ref=e206] [cursor=pointer]:
        - /url: src/
    - listitem [ref=e207]:
      - link "SYNC_ERROR_FIX.md" [ref=e208] [cursor=pointer]:
        - /url: SYNC_ERROR_FIX.md
    - listitem [ref=e209]:
      - link "SYNTAX.md" [ref=e210] [cursor=pointer]:
        - /url: SYNTAX.md
    - listitem [ref=e211]:
      - link "test-cors-access.js" [ref=e212] [cursor=pointer]:
        - /url: test-cors-access.js
    - listitem [ref=e213]:
      - link "test-results/" [ref=e214] [cursor=pointer]:
        - /url: test-results/
    - listitem [ref=e215]:
      - link "test-results.json" [ref=e216] [cursor=pointer]:
        - /url: test-results.json
    - listitem [ref=e217]:
      - link "TEST_COVERAGE_MATRIX.md" [ref=e218] [cursor=pointer]:
        - /url: TEST_COVERAGE_MATRIX.md
    - listitem [ref=e219]:
      - link "test_diagnostics.py" [ref=e220] [cursor=pointer]:
        - /url: test_diagnostics.py
    - listitem [ref=e221]:
      - link "test_invalid.training" [ref=e222] [cursor=pointer]:
        - /url: test_invalid.training
    - listitem [ref=e223]:
      - link "test_json_validator.py" [ref=e224] [cursor=pointer]:
        - /url: test_json_validator.py
    - listitem [ref=e225]:
      - link "test_schema_validator.py" [ref=e226] [cursor=pointer]:
        - /url: test_schema_validator.py
    - listitem [ref=e227]:
      - link "test_set_to_dict.py" [ref=e228] [cursor=pointer]:
        - /url: test_set_to_dict.py
    - listitem [ref=e229]:
      - link "tests/" [ref=e230] [cursor=pointer]:
        - /url: tests/
    - listitem [ref=e231]:
      - link "training-sample.txt" [ref=e232] [cursor=pointer]:
        - /url: training-sample.txt
    - listitem [ref=e233]:
      - link "training-sample_initial.txt" [ref=e234] [cursor=pointer]:
        - /url: training-sample_initial.txt
    - listitem [ref=e235]:
      - link "training.g4" [ref=e236] [cursor=pointer]:
        - /url: training.g4
    - listitem [ref=e237]:
      - link "uv.lock" [ref=e238] [cursor=pointer]:
        - /url: uv.lock
    - listitem [ref=e239]:
      - link "validate_bench_centric.py" [ref=e240] [cursor=pointer]:
        - /url: validate_bench_centric.py
    - listitem [ref=e241]:
      - link "validate_set_centric.py" [ref=e242] [cursor=pointer]:
        - /url: validate_set_centric.py
    - listitem [ref=e243]:
      - link "validate_synonyms_yaml.py" [ref=e244] [cursor=pointer]:
        - /url: validate_synonyms_yaml.py
    - listitem [ref=e245]:
      - link "VALIDATION_INDEX.md" [ref=e246] [cursor=pointer]:
        - /url: VALIDATION_INDEX.md
    - listitem [ref=e247]:
      - link "weight_parser/" [ref=e248] [cursor=pointer]:
        - /url: weight_parser/
    - listitem [ref=e249]:
      - link "WORKOUT_SESSION_IMPLEMENTATION.md" [ref=e250] [cursor=pointer]:
        - /url: WORKOUT_SESSION_IMPLEMENTATION.md
    - listitem [ref=e251]:
      - link "WORKOUT_SESSION_TESTING.md" [ref=e252] [cursor=pointer]:
        - /url: WORKOUT_SESSION_TESTING.md
  - separator [ref=e253]
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
  19  |     await expect(page).toHaveTitle('Training Parser');
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
> 46  |     await page.locator('#status').waitFor({ state: 'visible', timeout: 5000 });
      |                                   ^ TimeoutError: locator.waitFor: Timeout 5000ms exceeded.
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
  120 |     await page.locator('#status').waitFor({ state: 'visible', timeout: 5000 });
  121 | 
  122 |     // Open settings to configure git
  123 |     await page.locator('#settings-btn').click();
  124 |     await page.locator('.modal-backdrop').waitFor({ state: 'visible' });
  125 | 
  126 |     // Fill in local git server credentials
  127 |     // Note: In CI environment, use local test server
  128 |     const gitUrlInput = page.locator('input[placeholder*="github"]').first();
  129 |     const gitUserInput = page.locator('input[placeholder*="username"]').first();
  130 |     const gitTokenInput = page.locator('input[placeholder*="token"]').first();
  131 | 
  132 |     // For local testing, use test repo values if not already filled
  133 |     const currentUrl = await gitUrlInput.inputValue();
  134 |     if (!currentUrl) {
  135 |       await gitUrlInput.fill('http://localhost:8888/test-repo.git');
  136 |       await gitUserInput.fill('test');
  137 |       await gitTokenInput.fill('test');
  138 | 
  139 |       // Save credentials by clicking outside the modal or looking for a save button
  140 |       // The modal should auto-close or have a save button
  141 |       await page.keyboard.press('Escape');
  142 |       await page.locator('.modal-backdrop').waitFor({ state: 'hidden', timeout: 5000 });
  143 |     }
  144 | 
  145 |     // Test connection first
  146 |     // Open settings again to verify connection
```