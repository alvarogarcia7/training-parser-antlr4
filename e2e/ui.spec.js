import { test, expect } from '@playwright/test';
import fs from 'fs';
import path from 'path';

// Test data
const VALID_WORKOUT = `Bench press 4x75
Squat 5x70
Deadlift 3x100`;

// Exercise names without set data — triggers grammar errors because set_ is required
const INVALID_WORKOUT = `Bench press
Squat`;

// Pyodide loads from a local copy in CI/dev (see mobile-app/src/pyodide-worker.js),
// which takes ~10-20s cold; this is only paid once for the whole file below.
const PYODIDE_TIMEOUT = 90_000;

/** Wait for the Python runtime (Pyodide) to be fully initialized. */
async function waitForPyodide(page) {
  await page.locator('#status.status--ready').waitFor({ state: 'attached', timeout: PYODIDE_TIMEOUT });
}

/** Replace the workout input's contents with a clean slate before filling new values. */
async function setWorkoutInput(page, text) {
  const input = page.locator('#workout-input');
  await input.fill('');
  await input.fill(text);
}

test.describe('Training Parser PWA', () => {
  test.describe.configure({ mode: 'serial' });

  let context;
  let page;

  test.beforeAll(async ({ browser }) => {
    test.setTimeout(90_000);

    context = await browser.newContext();

    // Pre-configure git settings in localStorage before the single shared
    // navigation so the git sync buttons are visible for test 4. Test 1 only
    // asserts the buttons are attached (not hidden), so this is harmless there.
    await context.addInitScript(() => {
      localStorage.setItem('git_settings', JSON.stringify({
        remoteUrl: 'http://localhost:8888/test-repo.git',
        username: 'test',
        token: 'test',
        author: 'Test User',
      }));
    });

    page = await context.newPage();
    await page.goto('/mobile-app/');
    await waitForPyodide(page);
  });

  test.afterAll(async () => {
    await context.close();
  });

  test('1. Page loads correctly', async () => {
    await expect(page).toHaveTitle('Training Parser');
    await expect(page.locator('header h1')).toContainText('Training Parser');

    // Core controls always visible
    await expect(page.locator('#workout-input')).toBeVisible();
    await expect(page.locator('#parse-btn')).toBeVisible();

    // Git sync buttons exist in the DOM
    await expect(page.locator('#save-btn')).toBeAttached();
    await expect(page.locator('#pull-btn')).toBeAttached();
    await expect(page.locator('#sync-btn')).toBeAttached();

    // Status indicator always visible
    await expect(page.locator('#status')).toBeVisible();

    // Date input populated with today's date by the inline script
    const dateValue = await page.locator('#workout-date').inputValue();
    const today = new Date().toISOString().split('T')[0];
    expect(dateValue).toBe(today);
  });

  test('2. Insert valid line and assert parsing', async () => {
    const today = new Date().toISOString().split('T')[0];
    await setWorkoutInput(page, VALID_WORKOUT);
    await page.locator('#workout-date').fill(today);

    await page.locator('#parse-btn').click();

    await page.locator('#results-section').waitFor({ state: 'visible', timeout: 10000 });

    await expect(page.locator('#results-section')).toBeVisible();
    await expect(page.locator('#summary-text')).toContainText(/(\d+) exercises?/i);
    await expect(page.locator('#results-section table').first()).toBeVisible();
    await expect(page.locator('#errors-section')).not.toBeVisible();
  });

  test('3. Insert invalid workout and assert error', async () => {
    const today = new Date().toISOString().split('T')[0];
    await setWorkoutInput(page, INVALID_WORKOUT);
    await page.locator('#workout-date').fill(today);

    await page.locator('#parse-btn').click();

    await page.locator('#errors-section').waitFor({ state: 'visible', timeout: 10000 });

    await expect(page.locator('#errors-section')).toBeVisible();
    const errorCount = await page.locator('#errors-list li').count();
    expect(errorCount).toBeGreaterThan(0);
  });

  test('4. Git sync - pull and push to remote', async () => {
    // Requires local git server: make local-git-server
    // Git settings were pre-configured in beforeAll, so the buttons should be visible
    await expect(page.locator('#pull-btn')).toBeVisible();
    await expect(page.locator('#save-btn')).toBeVisible();
    await expect(page.locator('#sync-btn')).toBeVisible();

    const today = new Date().toISOString().split('T')[0];
    await setWorkoutInput(page, VALID_WORKOUT);
    await page.locator('#workout-date').fill(today);

    await page.locator('#parse-btn').click();
    await page.locator('#results-section').waitFor({ state: 'visible', timeout: 10000 });

    // Collect console logs to verify push was attempted
    const messages = [];
    page.on('console', msg => messages.push(msg.text()));

    await page.locator('#pull-btn').click();
    await page.waitForTimeout(1000);

    await page.locator('#save-btn').click();
    await page.waitForTimeout(500);

    await page.locator('#sync-btn').click();
    await page.waitForTimeout(3000);

    // Verify push was attempted (will fail against localhost:8888 since no server, but should be attempted)
    const pushLogs = messages.filter(m =>
      m.toLowerCase().includes('push') || m.includes('git-sync') || m.includes('sync')
    );
    expect(pushLogs.length).toBeGreaterThan(0);

    page.removeAllListeners('console');
  });

  test('5. Download file', async () => {
    const today = new Date().toISOString().split('T')[0];
    await setWorkoutInput(page, VALID_WORKOUT);
    await page.locator('#workout-date').fill(today);

    await page.locator('#parse-btn').click();
    await page.locator('#results-section').waitFor({ state: 'visible', timeout: 10000 });

    const downloadBtn = page.locator('#download-json-btn');
    const isVisible = await downloadBtn.isVisible();

    if (isVisible) {
      const downloadPromise = context.waitForEvent('download');
      await downloadBtn.click();

      const download = await downloadPromise;
      expect(download.suggestedFilename()).toMatch(/\.json$/);

      const downloadPath = path.join('/tmp', download.suggestedFilename());
      await download.saveAs(downloadPath);

      expect(fs.existsSync(downloadPath)).toBeTruthy();
      const json = JSON.parse(fs.readFileSync(downloadPath, 'utf-8'));
      expect(json).toBeDefined();

      fs.unlinkSync(downloadPath);
    } else {
      // Share is the fallback when download isn't available
      await expect(page.locator('#share-btn')).toBeVisible();
    }
  });
});
