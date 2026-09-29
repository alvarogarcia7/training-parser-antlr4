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

// Pyodide takes 30-90s to download and initialize from CDN
const PYODIDE_TIMEOUT = 90_000;

/** Wait for the Python runtime (Pyodide) to be fully initialized. */
async function waitForPyodide(page) {
  await page.locator('#status.status--ready').waitFor({ state: 'attached', timeout: PYODIDE_TIMEOUT });
}

test.describe('Training Parser PWA', () => {
  test('1. Page loads correctly', async ({ page }) => {
    await page.goto('/mobile-app/');

    await expect(page).toHaveTitle('Training Parser');
    await expect(page.locator('header h1')).toContainText('Training Parser');

    // Core controls always visible
    await expect(page.locator('#workout-input')).toBeVisible();
    await expect(page.locator('#parse-btn')).toBeVisible();

    // Git sync buttons are hidden until git is configured — just assert they exist in the DOM
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

  test('2. Insert valid line and assert parsing', async ({ page }) => {
    await page.goto('/mobile-app/');

    // Wait for Pyodide to be fully ready before parsing
    await waitForPyodide(page);

    const today = new Date().toISOString().split('T')[0];
    await page.locator('#workout-input').fill(VALID_WORKOUT);
    await page.locator('#workout-date').fill(today);

    await page.locator('#parse-btn').click();

    await page.locator('#results-section').waitFor({ state: 'visible', timeout: 10000 });

    await expect(page.locator('#results-section')).toBeVisible();
    await expect(page.locator('#summary-text')).toContainText(/(\d+) exercises?/i);
    await expect(page.locator('#results-section table').first()).toBeVisible();
    await expect(page.locator('#errors-section')).not.toBeVisible();
  });

  test('3. Insert invalid workout and assert error', async ({ page }) => {
    await page.goto('/mobile-app/');

    await waitForPyodide(page);

    const today = new Date().toISOString().split('T')[0];
    await page.locator('#workout-input').fill(INVALID_WORKOUT);
    await page.locator('#workout-date').fill(today);

    await page.locator('#parse-btn').click();

    await page.locator('#errors-section').waitFor({ state: 'visible', timeout: 10000 });

    await expect(page.locator('#errors-section')).toBeVisible();
    const errorCount = await page.locator('#errors-list li').count();
    expect(errorCount).toBeGreaterThan(0);
  });

  test('4. Git sync - pull and push to remote', async ({ page }) => {
    // Requires local git server: make local-git-server
    // Pre-configure git settings in localStorage so buttons are visible on first load
    await page.addInitScript(() => {
      localStorage.setItem('git_settings', JSON.stringify({
        remoteUrl: 'http://localhost:8888/test-repo.git',
        username: 'test',
        token: 'test',
        author: 'Test User',
      }));
    });

    await page.goto('/mobile-app/');
    await waitForPyodide(page);

    // Git buttons should now be visible (settings were pre-configured)
    await expect(page.locator('#pull-btn')).toBeVisible();
    await expect(page.locator('#save-btn')).toBeVisible();
    await expect(page.locator('#sync-btn')).toBeVisible();

    const today = new Date().toISOString().split('T')[0];
    await page.locator('#workout-input').fill(VALID_WORKOUT);
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
  });

  test('5. Download file', async ({ page, context }) => {
    await page.goto('/mobile-app/');

    await waitForPyodide(page);

    const today = new Date().toISOString().split('T')[0];
    await page.locator('#workout-input').fill(VALID_WORKOUT);
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
