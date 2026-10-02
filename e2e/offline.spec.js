import { test, expect } from '@playwright/test';

// Test data
const VALID_WORKOUT = `Bench press 4x75
Squat 5x70
Deadlift 3x100`;

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

test.describe('Offline-First PWA', () => {
  test.describe.configure({ mode: 'serial' });

  let context;
  let page;

  test.beforeAll(async ({ browser }) => {
    test.setTimeout(120_000);
    context = await browser.newContext();
    page = await context.newPage();

    // Load the app while online
    await page.goto('/mobile-app/');
    await waitForPyodide(page);
  });

  test.afterAll(async () => {
    // Restore network connectivity
    if (page && context) {
      await context.setOffline(false);
      await context.close();
    }
  });

  test('Load app online, then setOffline and verify parsing works', async () => {
    // Verify the app loaded successfully
    await expect(page).toHaveTitle('Training Parser');

    // Set up a valid workout
    const today = new Date().toISOString().split('T')[0];
    await setWorkoutInput(page, VALID_WORKOUT);
    await page.locator('#workout-date').fill(today);

    // Parse online
    await page.locator('#parse-btn').click();
    await page.locator('#results-section').waitFor({ state: 'visible', timeout: 10000 });
    await expect(page.locator('#results-section')).toBeVisible();

    // Now take the app offline
    console.log('Going offline...');
    await context.setOffline(true);

    // Verify we can still parse while offline
    // Clear and re-enter the same data
    await setWorkoutInput(page, VALID_WORKOUT);
    await page.locator('#workout-date').fill(today);

    // Parse while offline (should still work since Pyodide is loaded)
    await page.locator('#parse-btn').click();
    await page.locator('#results-section').waitFor({ state: 'visible', timeout: 10000 });

    // Verify parsing succeeded offline
    await expect(page.locator('#results-section')).toBeVisible();
    await expect(page.locator('#summary-text')).toContainText(/(\d+) exercises?/i);
    await expect(page.locator('#errors-section')).not.toBeVisible();

    console.log('✅ Parsing works offline');
  });

  test('Reload page while offline, verify app still loads from cache and parsing works', async () => {
    // At this point, app should already be cached from previous test
    // Keep offline
    await expect(context.offline).toBeDefined();

    const today = new Date().toISOString().split('T')[0];

    // Reload the page while offline
    console.log('Reloading while offline...');
    await page.reload();

    // The page should load from cache (service worker)
    // Wait for the app to be ready
    await page.locator('#workout-input').waitFor({ state: 'visible', timeout: 10000 });
    await page.locator('#status.status--ready').waitFor({ state: 'attached', timeout: 30000 });

    // Enter workout data
    await setWorkoutInput(page, VALID_WORKOUT);
    await page.locator('#workout-date').fill(today);

    // Parse while offline with reloaded app
    await page.locator('#parse-btn').click();
    await page.locator('#results-section').waitFor({ state: 'visible', timeout: 10000 });

    // Verify parsing succeeded
    await expect(page.locator('#results-section')).toBeVisible();
    await expect(page.locator('#summary-text')).toContainText(/(\d+) exercises?/i);

    console.log('✅ App loads from cache and parsing works after reload');
  });

  test('Verify no cross-origin requests made during offline operation', async () => {
    // Collect all requests made while offline
    const offlineRequests = [];

    page.on('request', (request) => {
      const url = new URL(request.url());
      if (url.origin !== 'http://localhost:8080') {
        offlineRequests.push(request.url());
      }
    });

    const today = new Date().toISOString().split('T')[0];
    await setWorkoutInput(page, VALID_WORKOUT);
    await page.locator('#workout-date').fill(today);

    // Parse while offline
    await page.locator('#parse-btn').click();
    await page.locator('#results-section').waitFor({ state: 'visible', timeout: 10000 });

    page.removeAllListeners('request');

    // Verify no cross-origin requests were attempted
    // (Any cross-origin requests would fail offline)
    const crossOriginRequests = offlineRequests.filter(url => {
      return !url.includes('localhost:8080') && !url.includes('blob:') && !url.includes('data:');
    });

    expect(crossOriginRequests).toHaveLength(0);
    console.log('✅ No cross-origin requests made during offline operation');
  });

  test('Restore network and verify app still works online', async () => {
    // Restore network connectivity
    await context.setOffline(false);

    const today = new Date().toISOString().split('T')[0];
    await setWorkoutInput(page, VALID_WORKOUT);
    await page.locator('#workout-date').fill(today);

    // Parse while back online
    await page.locator('#parse-btn').click();
    await page.locator('#results-section').waitFor({ state: 'visible', timeout: 10000 });

    // Verify parsing still works online
    await expect(page.locator('#results-section')).toBeVisible();
    await expect(page.locator('#summary-text')).toContainText(/(\d+) exercises?/i);

    console.log('✅ App works after coming back online');
  });
});
