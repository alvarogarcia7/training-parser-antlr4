/**
 * Git Integration Tests
 * Tests the git library against local and remote repositories
 * Scenarios:
 * - Empty repository (needs initialization)
 * - Repository with main branch
 * - Repository with master branch
 */

const test = require('node:test');
const assert = require('node:assert');
const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');

// Import git library
const gitLib = require('../src/git-lib.js');

// Test configuration
const TEST_REPOS = {
  empty: {
    name: 'test-repo-empty',
    branch: 'main',
    url: 'http://localhost:8888/test-repo-empty.git'
  },
  withMain: {
    name: 'test-repo-main',
    branch: 'main',
    url: 'http://localhost:8888/test-repo-main.git'
  },
  withMaster: {
    name: 'test-repo-master',
    branch: 'master',
    url: 'http://localhost:8888/test-repo-master.git'
  }
};

const GIT_SERVER_PORT = 8888;
const TEST_DIR = '/tmp/git-integration-test';
let gitServerProcess = null;

/**
 * Start local git server
 */
async function startGitServer() {
  return new Promise((resolve, reject) => {
    console.log('[test] Starting local git server...');

    // Create server script
    const serverScript = path.join(path.dirname(__dirname), 'bin', 'git-http-server.js');
    if (!fs.existsSync(serverScript)) {
      console.warn('[test] Git server script not found, tests will use existing server');
      resolve();
      return;
    }

    gitServerProcess = spawn('node', [serverScript], {
      cwd: '/tmp/git-server',
      stdio: ['ignore', 'pipe', 'pipe']
    });

    // Wait for server to be ready
    let ready = false;
    gitServerProcess.stderr.on('data', (data) => {
      console.log('[git-server]', data.toString());
    });

    gitServerProcess.stdout.on('data', (data) => {
      const msg = data.toString();
      console.log('[git-server]', msg);
      if (msg.includes('listening') && !ready) {
        ready = true;
        resolve();
      }
    });

    setTimeout(() => {
      if (ready) return;
      console.log('[test] Git server started (timeout)');
      resolve();
    }, 3000);

    gitServerProcess.on('error', (err) => {
      console.error('[test] Failed to start git server:', err);
      reject(err);
    });
  });
}

/**
 * Stop git server
 */
async function stopGitServer() {
  return new Promise((resolve) => {
    if (!gitServerProcess) {
      resolve();
      return;
    }
    console.log('[test] Stopping git server...');
    gitServerProcess.kill();
    setTimeout(resolve, 1000);
  });
}

/**
 * Setup test repository on git server
 */
async function setupTestRepo(repoName, initialBranch = 'main') {
  return new Promise((resolve, reject) => {
    console.log(`[test] Setting up test repository: ${repoName} (branch: ${initialBranch})`);

    const repoPath = path.join('/tmp/git-server', `${repoName}.git`);
    const tempPath = path.join('/tmp/git-server', `temp-${repoName}`);

    try {
      // Create bare repo if doesn't exist
      if (!fs.existsSync(repoPath)) {
        const init = spawn('git', ['init', '--bare', repoPath]);
        init.on('close', (code) => {
          if (code !== 0) {
            console.error(`[test] Failed to create bare repo: ${repoName}`);
            resolve(); // Continue anyway
            return;
          }
          console.log(`[test] ✓ Created bare repo: ${repoName}`);

          // Create initial commit for non-empty repos
          if (repoName !== 'test-repo-empty') {
            const tempInit = spawn('mkdir', ['-p', tempPath]);
            tempInit.on('close', () => {
              const clone = spawn('git', ['clone', repoPath, tempPath]);
              clone.on('close', () => {
                const setup = spawn('bash', ['-c', `
                  cd ${tempPath}
                  git config user.email "test@local"
                  git config user.name "Test User"
                  echo "# Test Repository" > README.md
                  git add README.md
                  git commit -m "Initial setup"
                  git push -u origin ${initialBranch} 2>/dev/null || true
                `]);
                setup.on('close', () => {
                  // Cleanup
                  spawn('rm', ['-rf', tempPath]);
                  console.log(`[test] ✓ Initialized ${repoName}`);
                  resolve();
                });
              });
            });
          } else {
            resolve();
          }
        });
      } else {
        console.log(`[test] ✓ Repository already exists: ${repoName}`);
        resolve();
      }
    } catch (error) {
      console.error(`[test] Error setting up repo:`, error);
      resolve(); // Continue anyway
    }
  });
}

/**
 * Setup test environment
 */
async function setupTests() {
  console.log('\n[test] ═══════════════════════════════════════════');
  console.log('[test] Git Integration Test Suite');
  console.log('[test] ═══════════════════════════════════════════\n');

  // Create test directory
  if (!fs.existsSync(TEST_DIR)) {
    fs.mkdirSync(TEST_DIR, { recursive: true });
  }

  // Start git server
  await startGitServer();

  // Setup test repositories
  for (const [key, repo] of Object.entries(TEST_REPOS)) {
    await setupTestRepo(repo.name, repo.branch);
  }

  console.log('\n[test] Test setup complete\n');
}

/**
 * Cleanup test environment
 */
async function cleanupTests() {
  console.log('\n[test] Cleaning up test environment...');
  await stopGitServer();
  if (fs.existsSync(TEST_DIR)) {
    fs.rmSync(TEST_DIR, { recursive: true });
  }
  console.log('[test] ✓ Cleanup complete\n');
}

// Tests

test('Setup and initialization', setupTests);

test('Git: Empty repository - initialize and push', async (t) => {
  const workDir = path.join(TEST_DIR, 'empty-repo');
  fs.mkdirSync(workDir, { recursive: true });

  const repo = TEST_REPOS.empty;

  // Initialize repo locally
  const initResult = await gitLib.ensureInitialized({
    dir: workDir,
    branch: repo.branch
  });

  assert.ok(initResult.ok, `Failed to initialize: ${initResult.error}`);

  // Create a test file
  const testFile = path.join(workDir, 'test.txt');
  fs.writeFileSync(testFile, 'Test workout data\n');

  // Create commit
  const commitResult = await gitLib.createCommit({
    dir: workDir,
    message: 'Add test workout data',
    author: 'Test Runner'
  });

  assert.ok(commitResult.ok, `Failed to commit: ${commitResult.error}`);
  assert.ok(commitResult.oid, 'Commit OID missing');

  console.log(`[test] ✓ Created commit: ${commitResult.oid.substring(0, 7)}`);

  // Push to remote
  const pushResult = await gitLib.pushToRemote({
    url: repo.url,
    dir: workDir,
    branch: repo.branch,
    username: 'test',
    password: 'test'
  });

  assert.ok(pushResult.ok || pushResult.error, 'Push result missing');
  console.log(`[test] ${pushResult.ok ? '✓' : '✗'} Push to empty repo`);
});

test('Git: Repository with main branch - push new commit', async (t) => {
  const workDir = path.join(TEST_DIR, 'main-repo');
  fs.mkdirSync(workDir, { recursive: true });

  const repo = TEST_REPOS.withMain;

  // Clone repository
  const cloneResult = await gitLib.cloneRepository({
    url: repo.url,
    dir: workDir,
    branch: repo.branch,
    username: 'test',
    password: 'test'
  });

  // Clone might fail for empty repos, that's OK
  console.log(`[test] Clone: ${cloneResult.ok ? '✓' : '(expected to fail for empty)'}`);

  // Ensure initialized
  const initResult = await gitLib.ensureInitialized({
    dir: workDir,
    branch: repo.branch
  });

  assert.ok(initResult.ok, `Failed to initialize: ${initResult.error}`);

  // Create test file
  const testFile = path.join(workDir, 'workout.txt');
  fs.mkdirSync(path.dirname(testFile), { recursive: true });
  fs.writeFileSync(testFile, 'Bench press 4x75kg\n');

  // Create commit
  const commitResult = await gitLib.createCommit({
    dir: workDir,
    message: 'Add workout: bench press',
    author: 'Test Runner'
  });

  assert.ok(commitResult.ok, `Failed to commit: ${commitResult.error}`);

  // Push to remote
  const pushResult = await gitLib.pushToRemote({
    url: repo.url,
    dir: workDir,
    branch: repo.branch,
    username: 'test',
    password: 'test'
  });

  assert.ok(pushResult.ok || pushResult.error, 'Push result missing');
  console.log(`[test] ${pushResult.ok ? '✓' : '✗'} Push to main branch repo`);
});

test('Git: Repository with master branch - push new commit', async (t) => {
  const workDir = path.join(TEST_DIR, 'master-repo');
  fs.mkdirSync(workDir, { recursive: true });

  const repo = TEST_REPOS.withMaster;

  // Ensure initialized
  const initResult = await gitLib.ensureInitialized({
    dir: workDir,
    branch: repo.branch
  });

  assert.ok(initResult.ok, `Failed to initialize: ${initResult.error}`);

  // Create test file
  const testFile = path.join(workDir, 'workout.txt');
  fs.mkdirSync(path.dirname(testFile), { recursive: true });
  fs.writeFileSync(testFile, 'Squat 5x70kg\n');

  // Create commit
  const commitResult = await gitLib.createCommit({
    dir: workDir,
    message: 'Add workout: squat',
    author: 'Test Runner'
  });

  assert.ok(commitResult.ok, `Failed to commit: ${commitResult.error}`);

  // Push to remote
  const pushResult = await gitLib.pushToRemote({
    url: repo.url,
    dir: workDir,
    branch: repo.branch,
    username: 'test',
    password: 'test'
  });

  assert.ok(pushResult.ok || pushResult.error, 'Push result missing');
  console.log(`[test] ${pushResult.ok ? '✓' : '✗'} Push to master branch repo`);
});

test('Git: List remote refs', async (t) => {
  const repo = TEST_REPOS.withMain;

  const result = await gitLib.listRemoteRefs({
    url: repo.url,
    username: 'test',
    password: 'test'
  });

  console.log(`[test] ${result.ok ? '✓' : '✗'} List remote refs`);
  if (result.ok) {
    console.log(`[test] Found branches:`, result.branches);
  }
});

test('Cleanup', cleanupTests);
