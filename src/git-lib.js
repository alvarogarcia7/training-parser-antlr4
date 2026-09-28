/**
 * Isomorphic Git Library
 * Works in both Node.js and browser environments
 * Provides consistent API for git operations
 */

// Detect environment
const isNode = typeof globalThis !== 'undefined' &&
              globalThis.process &&
              globalThis.process.versions &&
              globalThis.process.versions.node;

let isomorphicGit, httpClient, fs, path;

if (isNode) {
  isomorphicGit = require('isomorphic-git');
  httpClient = require('isomorphic-git/http/node');
  fs = require('fs');
  path = require('path');
} else {
  isomorphicGit = window.git;
  httpClient = window.GitHttp;
  fs = require('lightning-fs');
  path = '/';
}

let fsInstance = null;

/**
 * Initialize filesystem - required before any git operations
 * @param {string} workDir - Working directory path
 */
async function initFS(workDir = '/workout-data') {
  if (!isNode) {
    if (!fsInstance) {
      fsInstance = new LightningFS('fs');
      globalThis.lightning = fsInstance;
    }
    return fsInstance;
  }
  return null;
}

/**
 * Clone a repository
 * @param {Object} options - Clone options
 * @param {string} options.url - Repository URL
 * @param {string} options.dir - Local directory
 * @param {string} options.username - Username for auth
 * @param {string} options.password - Password/token for auth
 * @param {string} options.corsProxy - CORS proxy (browser only)
 * @returns {Promise<Object>} Clone result
 */
async function cloneRepository(options) {
  const {
    url,
    dir = '/workout-data',
    username,
    password,
    corsProxy,
    branch = 'main'
  } = options;

  console.log(`[git-lib] Cloning ${url} to ${dir}`);

  const gitOptions = {
    fs: isNode ? fs : fsInstance,
    http: httpClient,
    dir,
    url,
    singleBranch: true,
    depth: 1,
    ref: branch,
  };

  if (corsProxy && !isNode) {
    gitOptions.corsProxy = corsProxy;
  }

  if (username && password) {
    gitOptions.onAuth = () => ({ username, password });
  }

  try {
    await isomorphicGit.clone(gitOptions);
    console.log(`[git-lib] ✓ Cloned successfully`);
    return { ok: true, message: 'Repository cloned' };
  } catch (error) {
    console.error(`[git-lib] ✗ Clone failed:`, error.message);
    return { ok: false, error: error.message };
  }
}

/**
 * Create a new commit
 * @param {Object} options - Commit options
 * @param {string} options.dir - Repository directory
 * @param {string} options.message - Commit message
 * @param {string} options.author - Author name
 * @param {string} options.email - Author email
 * @returns {Promise<Object>} Commit result
 */
async function createCommit(options) {
  const {
    dir = '/workout-data',
    message = 'Add workout data',
    author = 'Training Parser',
    email = 'parser@local'
  } = options;

  console.log(`[git-lib] Creating commit: "${message}"`);

  try {
    // Stage all changes
    await isomorphicGit.add({
      fs: isNode ? fs : fsInstance,
      dir,
      filepath: '.'
    });

    // Get current branch
    let branch = 'main';
    try {
      const currentBranch = await isomorphicGit.currentBranch({
        fs: isNode ? fs : fsInstance,
        dir,
        fullname: false
      });
      if (currentBranch) {
        branch = currentBranch;
      }
    } catch (e) {
      console.log(`[git-lib] Using default branch: ${branch}`);
    }

    // Create commit
    const oid = await isomorphicGit.commit({
      fs: isNode ? fs : fsInstance,
      dir,
      message,
      author: { name: author, email },
      signingKey: undefined
    });

    console.log(`[git-lib] ✓ Commit created: ${oid.substring(0, 7)}`);
    return { ok: true, oid, branch };
  } catch (error) {
    console.error(`[git-lib] ✗ Commit failed:`, error.message);
    return { ok: false, error: error.message };
  }
}

/**
 * Push commits to remote
 * @param {Object} options - Push options
 * @param {string} options.url - Repository URL
 * @param {string} options.dir - Repository directory
 * @param {string} options.username - Username for auth
 * @param {string} options.password - Password/token for auth
 * @param {string} options.corsProxy - CORS proxy (browser only)
 * @param {string} options.branch - Branch to push
 * @returns {Promise<Object>} Push result
 */
async function pushToRemote(options) {
  const {
    url,
    dir = '/workout-data',
    username,
    password,
    corsProxy,
    branch = 'main'
  } = options;

  console.log(`[git-lib] Pushing to ${url} branch: ${branch}`);

  const gitOptions = {
    fs: isNode ? fs : fsInstance,
    http: httpClient,
    dir,
    remote: 'origin',
    ref: branch
  };

  // Add remote if not exists
  try {
    await isomorphicGit.addRemote({
      fs: isNode ? fs : fsInstance,
      dir,
      remote: 'origin',
      url,
      force: true
    });
  } catch (e) {
    console.log(`[git-lib] Remote already exists`);
  }

  if (corsProxy && !isNode) {
    gitOptions.corsProxy = corsProxy;
  }

  if (username && password) {
    gitOptions.onAuth = () => ({ username, password });
  }

  try {
    const result = await isomorphicGit.push(gitOptions);
    console.log(`[git-lib] ✓ Push succeeded`);
    return { ok: true, result };
  } catch (error) {
    console.error(`[git-lib] ✗ Push failed:`, error.message);
    return { ok: false, error: error.message };
  }
}

/**
 * List remote refs (branches)
 * @param {Object} options - Options
 * @param {string} options.url - Repository URL
 * @param {string} options.username - Username
 * @param {string} options.password - Password/token
 * @param {string} options.corsProxy - CORS proxy (browser only)
 * @returns {Promise<Object>} Remote refs
 */
async function listRemoteRefs(options) {
  const {
    url,
    username,
    password,
    corsProxy
  } = options;

  console.log(`[git-lib] Listing remote refs for ${url}`);

  const gitOptions = {
    http: httpClient,
    url
  };

  if (corsProxy && !isNode) {
    gitOptions.corsProxy = corsProxy;
  }

  if (username && password) {
    gitOptions.onAuth = () => ({ username, password });
  }

  try {
    const refs = await isomorphicGit.listServerRefs(gitOptions);
    const branches = Object.keys(refs)
      .filter(r => r.startsWith('refs/heads/'))
      .map(r => r.replace('refs/heads/', ''));
    console.log(`[git-lib] ✓ Found branches:`, branches);
    return { ok: true, refs, branches };
  } catch (error) {
    console.error(`[git-lib] ✗ listServerRefs failed:`, error.message);
    return { ok: false, error: error.message };
  }
}

/**
 * Ensure repository is initialized (create initial commit if empty)
 * @param {Object} options - Options
 * @param {string} options.dir - Repository directory
 * @param {string} options.branch - Branch name
 * @param {string} options.author - Author name
 * @returns {Promise<Object>} Result
 */
async function ensureInitialized(options) {
  const {
    dir = '/workout-data',
    branch = 'main',
    author = 'Training Parser'
  } = options;

  console.log(`[git-lib] Ensuring repo initialized: ${dir}`);

  try {
    // Check if we have any commits
    const log = await isomorphicGit.log({
      fs: isNode ? fs : fsInstance,
      dir,
      ref: branch
    });

    if (log && log.length > 0) {
      console.log(`[git-lib] ✓ Repository has ${log.length} commits`);
      return { ok: true, message: 'Already initialized' };
    }
  } catch (e) {
    console.log(`[git-lib] No commits found, will initialize`);
  }

  // Try to checkout branch
  try {
    await isomorphicGit.checkout({
      fs: isNode ? fs : fsInstance,
      dir,
      ref: branch,
      force: true
    });
  } catch (e) {
    try {
      await isomorphicGit.checkout({
        fs: isNode ? fs : fsInstance,
        dir,
        ref: branch,
        create: true
      });
    } catch (e2) {
      console.error(`[git-lib] Could not create branch:`, e2.message);
      return { ok: false, error: e2.message };
    }
  }

  // Create initial commit
  try {
    const oid = await isomorphicGit.commit({
      fs: isNode ? fs : fsInstance,
      dir,
      message: 'Initial commit',
      author: { name: author, email: 'parser@local' },
      signingKey: undefined
    });
    console.log(`[git-lib] ✓ Created initial commit: ${oid.substring(0, 7)}`);
    return { ok: true, message: 'Initialized', oid };
  } catch (error) {
    console.error(`[git-lib] ✗ Could not create initial commit:`, error.message);
    return { ok: false, error: error.message };
  }
}

/**
 * Get current HEAD commit
 * @param {string} dir - Repository directory
 * @returns {Promise<Object>} Commit info
 */
async function getCurrentCommit(dir = '/workout-data') {
  try {
    const log = await isomorphicGit.log({
      fs: isNode ? fs : fsInstance,
      dir,
      depth: 1
    });
    if (log && log.length > 0) {
      return { ok: true, oid: log[0].oid, message: log[0].commit.message };
    }
    return { ok: false, error: 'No commits found' };
  } catch (error) {
    return { ok: false, error: error.message };
  }
}

module.exports = {
  initFS,
  cloneRepository,
  createCommit,
  pushToRemote,
  listRemoteRefs,
  ensureInitialized,
  getCurrentCommit,
  isNode,
  isomorphicGit
};
