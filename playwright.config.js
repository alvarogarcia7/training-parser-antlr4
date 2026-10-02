import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',
  fullyParallel: false, // Sequential for git operations
  forbidOnly: !!process.env.CI,
  retries: 0,
  workers: process.env.CI ? 1 : 1,
  reporter: [
    ['html', { outputFolder: 'playwright-report', open: 'never' }],
    ['json', { outputFile: 'test-results.json' }],
    ['list']
  ],
  use: {
    baseURL: 'http://localhost:8080/',
    trace: 'on',
    screenshot: 'on',
  },
  webServer: process.env.CI ? undefined : {
    command: 'uv run python3 bin/serve.py',
    url: 'http://localhost:8080',
    reuseExistingServer: true,
    timeout: 120000,
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
  globalTimeout: 1800000, // 30 minutes
  timeout: process.env.CI ? 30000 : 15000, // individual test timeout (Pyodide loads once in beforeAll)
});
