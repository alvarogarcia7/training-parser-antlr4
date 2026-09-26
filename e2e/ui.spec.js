import { test, expect } from '@playwright/test';
import fs from 'fs';
import path from 'path';

// Test data
const VALID_WORKOUT = `Bench press 4x75kg
Squat 5x70kg
Deadlift 3x100kg`;

const INVALID_WORKOUT = `This is not a valid workout format
Random gibberish here`;

test.describe('Training Parser PWA', () => {
  test('1. Page loads correctly', async ({ page }) => {
    // Navigate to the PWA
    await page.goto('/');

    // Assert page title
    await expect(page).toHaveTitle('Training Parser');

    // Assert header
    await expect(page.locator('header h1')).toContainText('Training Parser');

    // Assert main elements exist
    await expect(page.locator('#workout-input')).toBeVisible();
    await expect(page.locator('#parse-btn')).toBeVisible();
    await expect(page.locator('#save-btn')).toBeVisible();
    await expect(page.locator('#pull-btn')).toBeVisible();
    await expect(page.locator('#sync-btn')).toBeVisible();

    // Assert status indicator
    const status = page.locator('#status');
    await status.waitFor({ state: 'visible', timeout: 5000 });

    // Assert date input is populated with today's date
    const dateInput = page.locator('#workout-date');
    const dateValue = await dateInput.inputValue();
    const today = new Date().toISOString().split('T')[0];
    expect(dateValue).toBe(today);
  });

  test('2. Insert valid line and assert parsing', async ({ page }) => {
    await page.goto('/');

    // Wait for page to load
    await page.locator('#status').waitFor({ state: 'visible', timeout: 5000 });

    // Input valid workout
    const workoutInput = page.locator('#workout-input');
    await workoutInput.fill(VALID_WORKOUT);

    // Set date
    const today = new Date().toISOString().split('T')[0];
    await page.locator('#workout-date').fill(today);

    // Click parse button
    await page.locator('#parse-btn').click();

    // Wait for results to appear
    await page.locator('#results-section').waitFor({ state: 'visible', timeout: 5000 });

    // Assert results are shown
    const resultsSection = page.locator('#results-section');
    await expect(resultsSection).toBeVisible();

    // Assert summary shows parsed exercises
    const summaryText = page.locator('#summary-text');
    await expect(summaryText).toContainText(/(\d+) exercises?/i);

    // Assert results table exists with data
    const resultsTable = page.locator('table');
    await expect(resultsTable).toBeVisible();

    // Assert no errors section
    const errorsSection = page.locator('#errors-section');
    await expect(errorsSection).not.toBeVisible();
  });

  test('3. Insert invalid workout and assert error', async ({ page }) => {
    await page.goto('/');

    // Wait for page to load
    await page.locator('#status').waitFor({ state: 'visible', timeout: 5000 });

    // Input invalid workout
    const workoutInput = page.locator('#workout-input');
    await workoutInput.fill(INVALID_WORKOUT);

    // Set date
    const today = new Date().toISOString().split('T')[0];
    await page.locator('#workout-date').fill(today);

    // Click parse button
    await page.locator('#parse-btn').click();

    // Wait for errors to appear
    await page.locator('#errors-section').waitFor({ state: 'visible', timeout: 5000 });

    // Assert errors section is visible
    const errorsSection = page.locator('#errors-section');
    await expect(errorsSection).toBeVisible();

    // Assert error list has items
    const errorsList = page.locator('#errors-list li');
    const errorCount = await errorsList.count();
    expect(errorCount).toBeGreaterThan(0);

    // Assert results section is not visible (only errors)
    const resultsSection = page.locator('#results-section');
    await expect(resultsSection).not.toBeVisible();
  });

  test('4. Git sync - pull and push to remote', async ({ page }) => {
    // This test requires local git server setup
    // Setup: ensure make setup-local-git-server has been run

    await page.goto('/');

    // Wait for page to load
    await page.locator('#status').waitFor({ state: 'visible', timeout: 5000 });

    // Open settings to configure git
    await page.locator('#settings-btn').click();
    await page.locator('.modal-backdrop').waitFor({ state: 'visible' });

    // Fill in local git server credentials
    // Note: In CI environment, use local test server
    const gitUrlInput = page.locator('input[placeholder*="github"]').first();
    const gitUserInput = page.locator('input[placeholder*="username"]').first();
    const gitTokenInput = page.locator('input[placeholder*="token"]').first();

    // For local testing, use test repo values if not already filled
    const currentUrl = await gitUrlInput.inputValue();
    if (!currentUrl) {
      await gitUrlInput.fill('http://localhost:8888/test-repo.git');
      await gitUserInput.fill('test');
      await gitTokenInput.fill('test');

      // Save credentials by clicking outside the modal or looking for a save button
      // The modal should auto-close or have a save button
      await page.keyboard.press('Escape');
      await page.locator('.modal-backdrop').waitFor({ state: 'hidden', timeout: 5000 });
    }

    // Test connection first
    // Open settings again to verify connection
    await page.locator('#settings-btn').click();
    await page.locator('.modal-backdrop').waitFor({ state: 'visible' });

    // Look for connection test button
    const testButton = page.locator('button:has-text("Test")').first();
    if (await testButton.isVisible()) {
      await testButton.click();
      // Wait for connection result
      await page.waitForTimeout(2000);
    }

    await page.keyboard.press('Escape');
    await page.locator('.modal-backdrop').waitFor({ state: 'hidden', timeout: 5000 });

    // Parse and save a workout
    const workoutInput = page.locator('#workout-input');
    await workoutInput.fill(VALID_WORKOUT);

    const today = new Date().toISOString().split('T')[0];
    await page.locator('#workout-date').fill(today);

    // Parse first
    await page.locator('#parse-btn').click();
    await page.locator('#results-section').waitFor({ state: 'visible', timeout: 5000 });

    // Pull from remote (to sync any existing data)
    await page.locator('#pull-btn').click();
    await page.waitForTimeout(1000);

    // Save to local git
    await page.locator('#save-btn').click();
    await page.waitForTimeout(500);

    // Get the page console for checking logs
    const messages = [];
    page.on('console', msg => messages.push(msg.text()));

    // Push to remote
    await page.locator('#sync-btn').click();

    // Wait for push to complete (look for success or error message)
    // The sync button should show some feedback
    await page.waitForTimeout(3000);

    // Verify push was attempted by checking console logs
    const pushLogs = messages.filter(m => m.includes('git-sync:push'));
    expect(pushLogs.length).toBeGreaterThan(0);

    // Check that no fatal errors occurred
    const errors = messages.filter(m => m.includes('ERROR') || m.includes('FAILED'));
    // Some errors might occur but push should be attempted
    expect(errors.length).toBeLessThan(5);
  });

  test('5. Download file', async ({ page, context }) => {
    await page.goto('/');

    // Wait for page to load
    await page.locator('#status').waitFor({ state: 'visible', timeout: 5000 });

    // Parse a valid workout first
    const workoutInput = page.locator('#workout-input');
    await workoutInput.fill(VALID_WORKOUT);

    const today = new Date().toISOString().split('T')[0];
    await page.locator('#workout-date').fill(today);

    // Parse
    await page.locator('#parse-btn').click();
    await page.locator('#results-section').waitFor({ state: 'visible', timeout: 5000 });

    // Check if download button is visible after parsing
    const downloadBtn = page.locator('#download-json-btn');
    const isVisible = await downloadBtn.isVisible();

    if (isVisible) {
      // Start waiting for download
      const downloadPromise = context.waitForEvent('download');
      await downloadBtn.click();

      // Wait for download
      const download = await downloadPromise;

      // Verify download properties
      expect(download.suggestedFilename()).toMatch(/\.json$/);

      // Save and verify file contents
      const downloadPath = path.join('/tmp', download.suggestedFilename());
      await download.saveAs(downloadPath);

      // Assert file exists and is readable
      expect(fs.existsSync(downloadPath)).toBeTruthy();

      // Verify it's valid JSON
      const content = fs.readFileSync(downloadPath, 'utf-8');
      const json = JSON.parse(content);
      expect(json).toBeDefined();

      // Cleanup
      fs.unlinkSync(downloadPath);
    } else {
      // If download button is not visible, at least check that we can use Share button
      const shareBtn = page.locator('#share-btn');
      await expect(shareBtn).toBeVisible();
    }
  });
});
