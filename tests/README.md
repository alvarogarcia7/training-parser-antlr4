# Git Integration Tests

Comprehensive testing suite for the isomorphic git library. Tests the library's ability to work with git repositories in different states.

## Overview

The testing suite validates:
- Git library functionality in Node.js and browser environments
- Interaction with different repository configurations
- Commit creation and pushing to remote
- Authentication and CORS proxy handling

## Repository Scenarios

The tests cover three repository scenarios:

### 1. Empty Repository
- **Name**: `test-repo-empty`
- **Branch**: `main`
- **Purpose**: Tests repository initialization
- **Operations**: Initialize, create commit, push

### 2. Repository with Main Branch
- **Name**: `test-repo-main`
- **Branch**: `main`
- **Purpose**: Tests standard workflow
- **Operations**: Clone (if possible), commit, push

### 3. Repository with Master Branch
- **Name**: `test-repo-master`
- **Branch**: `master`
- **Purpose**: Tests alternative default branch
- **Operations**: Initialize, commit, push

## Running Tests

### Locally

```bash
# Install dependencies
npm install

# Run once
make test-git

# Run in watch mode (auto-re-runs on file changes)
make test-git-watch

# Or directly with npm
npm run test:git
npm run test:git:watch
```

### In CI

Tests automatically run on pull requests:
1. Sets up local git server
2. Initializes test repositories
3. Runs test suite
4. Uploads logs as artifacts

See `.github/workflows/ci.yml` for configuration.

## Test Structure

```
tests/
└── git-integration.spec.js    # Main test file
    ├── Setup
    │   ├── Start git server
    │   ├── Initialize test repos
    │   └── Cleanup
    ├── Empty repo tests
    ├── Main branch tests
    ├── Master branch tests
    ├── Remote refs listing
    └── Cleanup
```

## Expected Output

```
[test] ═══════════════════════════════════════════════════════
[test] Git Integration Test Suite
[test] ═══════════════════════════════════════════════════════

[test] Starting local git server...
[test] Setting up test repository: test-repo-empty (branch: main)
[test] ✓ Created bare repo: test-repo-empty
[test] ✓ Initialized test-repo-empty
...
[test] ✓ Push to empty repo
[test] ✓ Push to main branch repo
[test] ✓ Push to master branch repo
[test] Cleaning up test environment...
```

## The Git Library

Located in `src/git-lib.js`, the library provides:

- `initFS(workDir)` - Initialize filesystem abstraction
- `cloneRepository(options)` - Clone a repository
- `createCommit(options)` - Create a new commit
- `pushToRemote(options)` - Push commits to remote
- `listRemoteRefs(options)` - List remote branches
- `ensureInitialized(options)` - Initialize empty repositories
- `getCurrentCommit(dir)` - Get HEAD commit info

### Key Features

- **Isomorphic**: Works in both Node.js and browser
- **Universal**: Works with any git HTTP server
- **Robust**: Handles missing branches, empty repos, authentication
- **Observable**: Detailed console logging for debugging

### Browser Usage

The same library can be used in the PWA:

```javascript
import gitLib from './src/git-lib.js';

// Browser usage
await gitLib.initFS();
await gitLib.cloneRepository({
  url: 'https://github.com/user/repo',
  dir: '/workout-data',
  corsProxy: 'https://cors.isomorphic-git.org'
});
```

### Node.js Usage

```javascript
const gitLib = require('./src/git-lib.js');

// Node.js usage
await gitLib.cloneRepository({
  url: 'http://localhost:8888/repo.git',
  dir: '/tmp/repo',
  username: 'user',
  password: 'token'
});
```

## Troubleshooting

### Tests hang or timeout
- Check if git server is running: `lsof -i :8888`
- Check git server logs: `tail -f /tmp/git-server.log`
- Restart: `pkill -f git-http-server.js && make test-git`

### "Repository not found"
- Ensure test repos are initialized on git server
- Run: `make setup-local-git-server`

### Authentication errors
- Check credentials in test config
- Verify git server is accepting connections
- Try local server first, not remote

### File not found errors
- Ensure test working directories exist
- Check `/tmp/git-integration-test/` permissions
- Run tests as same user who created dirs

## CI/CD Integration

The tests are automatically run on:
- **Pull Requests**: Full test suite
- **Branches**: Only main branch tests
- **Manual**: Use `make ci-babysit` to monitor

### Monitoring Pipeline

```bash
# Watch CI pipeline until it's green (or red)
make ci-babysit

# Requires GitHub CLI: https://cli.github.com
```

## Adding New Tests

1. Add test function to `git-integration.spec.js`
2. Follow existing pattern with setup and assertions
3. Use git library API
4. Test logs will auto-include in CI artifacts

Example:

```javascript
test('Git: My new scenario', async (t) => {
  const workDir = path.join(TEST_DIR, 'my-test');
  fs.mkdirSync(workDir, { recursive: true });

  // Your test here
  const result = await gitLib.someOperation({ dir: workDir });
  assert.ok(result.ok, `Failed: ${result.error}`);
});
```

## Architecture

```
User (developer or CI)
    ↓
make test-git
    ↓
npm run test:git (Node test runner)
    ↓
tests/git-integration.spec.js
    ↓
src/git-lib.js (isomorphic library)
    ↓
isomorphic-git
    ↓
Local Git Server (/tmp/git-server)
```

The same `git-lib.js` library is used in the PWA (`mobile-app/src/git-sync.js`) for consistency.
