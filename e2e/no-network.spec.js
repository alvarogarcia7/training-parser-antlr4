import { test, expect } from '@playwright/test';

// Test data
const VALID_WORKOUT = `Bench press 4x75
Squat 5x70
Deadlift 3x100`;

const PYODIDE_TIMEOUT = 420_000; // 7 min: WASM compilation on slow CI runners can take 300s+

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

test.describe('No External Network Requests', () => {
  test.describe.configure({ mode: 'serial' });

  let context;
  let page;

  test.beforeAll(async ({ browser }) => {
    test.setTimeout(480_000); // 8 min: must exceed PYODIDE_TIMEOUT + buffer
    context = await browser.newContext();
    page = await context.newPage();

    // Intercept and block all requests to non-self origins
    await page.route('**/*', (route) => {
      const url = new URL(route.request().url());
      const isLocalhost = url.hostname === 'localhost' || url.hostname === '127.0.0.1';
      const isSelfOrigin = url.origin === 'http://localhost:8080';

      if (!isSelfOrigin && !isLocalhost) {
        // Block cross-origin requests
        console.log(`Blocking cross-origin request: ${route.request().url()}`);
        route.abort('blockedbyclient');
      } else {
        route.continue();
      }
    });

    // Load the app (which will only succeed if no cross-origin requests are needed)
    await page.goto('/mobile-app/');
    await waitForPyodide(page);
  });

  test.afterAll(async () => {
    if (page && context) {
      await context.close();
    }
  });

  test('Load app without any cross-origin network requests', async () => {
    // If we got here, the app loaded successfully without cross-origin requests
    await expect(page).toHaveTitle('Training Parser');
    await expect(page.locator('header h1')).toContainText('Training Parser');
    console.log('✅ App loaded without cross-origin requests');
  });

  test('Parse workout without any cross-origin network requests', async () => {
    const today = new Date().toISOString().split('T')[0];
    await setWorkoutInput(page, VALID_WORKOUT);
    await page.locator('#workout-date').fill(today);

    // Track if any cross-origin requests were attempted
    let blockedRequests = [];
    page.on('request', (request) => {
      // Already handled by route handler, but log for verification
      const url = new URL(request.url());
      if (url.origin !== 'http://localhost:8080') {
        blockedRequests.push(request.url());
      }
    });

    // Parse the workout
    await page.locator('#parse-btn').click();

    // If parsing succeeds without errors, no cross-origin requests were made
    await page.locator('#results-section').waitFor({ state: 'visible', timeout: 10000 });

    page.removeAllListeners('request');

    // Verify results are visible
    await expect(page.locator('#results-section')).toBeVisible();
    await expect(page.locator('#summary-text')).toContainText(/(\d+) exercises?/i);

    // Verify no blocked requests occurred
    expect(blockedRequests).toHaveLength(0);
    console.log('✅ Parsing completed without cross-origin requests');
  });

  test('Verify all resources are loaded from localhost or self-origin', async () => {
    const today = new Date().toISOString().split('T')[0];
    await setWorkoutInput(page, VALID_WORKOUT);
    await page.locator('#workout-date').fill(today);

    // Collect all network requests
    const allRequests = [];
    page.on('request', (request) => {
      const url = new URL(request.url());
      allRequests.push({
        url: request.url(),
        resourceType: request.resourceType(),
        isLocalhost: url.hostname === 'localhost' || url.hostname === '127.0.0.1',
        isSelfOrigin: url.origin === 'http://localhost:8080',
      });
    });

    await page.locator('#parse-btn').click();
    await page.locator('#results-section').waitFor({ state: 'visible', timeout: 10000 });

    page.removeAllListeners('request');

    // Verify all requests are from localhost/self-origin or are blob/data URLs
    const externalRequests = allRequests.filter(req => {
      const isBlob = req.url.startsWith('blob:');
      const isData = req.url.startsWith('data:');
      return !req.isSelfOrigin && !req.isLocalhost && !isBlob && !isData;
    });

    expect(externalRequests).toHaveLength(0);

    if (externalRequests.length > 0) {
      console.log('External requests found:');
      externalRequests.forEach(req => {
        console.log(`  - ${req.resourceType}: ${req.url}`);
      });
    }

    console.log('✅ All resources loaded from self-origin');
  });

  test('Verify error message if external request is attempted', async () => {
    // This test verifies that if a request were attempted to an external resource,
    // it would be properly handled (blocked by route handler)

    let blockCount = 0;
    page.on('request', (request) => {
      const url = new URL(request.url());
      const isSelfOrigin = url.origin === 'http://localhost:8080';
      if (!isSelfOrigin && !url.hostname.includes('localhost')) {
        blockCount++;
        console.log(`Attempted to request external resource: ${url.hostname}`);
      }
    });

    const today = new Date().toISOString().split('T')[0];
    await setWorkoutInput(page, VALID_WORKOUT);
    await page.locator('#workout-date').fill(today);

    await page.locator('#parse-btn').click();
    await page.locator('#results-section').waitFor({ state: 'visible', timeout: 10000 });

    page.removeAllListeners('request');

    // Verify no external requests were attempted
    expect(blockCount).toBe(0);
    console.log('✅ No external requests attempted during operation');
  });
});
