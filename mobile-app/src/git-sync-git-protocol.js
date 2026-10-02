/**
 * Git-protocol backend using isomorphic-git
 * Fixes Bugs #1, #2, #3, #4 related to git operations
 */

import { GitSyncBackend } from './git-sync-backend-base.js';
import { GitSyncError } from './git-sync-errors.js';
import { GitSyncStorage } from './git-sync-storage.js';
import { GitSyncLockManager } from './git-sync-lock.js';

export class GitProtocolBackend extends GitSyncBackend {
  constructor(config, fs, gitDir) {
    super(config);
    this.fs = fs;
    this.gitDir = gitDir;
    this.storage = new GitSyncStorage(fs, gitDir);
    this.lockManager = new GitSyncLockManager();
  }

  /**
   * Get CORS proxy URL based on environment
   * @private
   * @returns {string} CORS proxy URL
   */
  _getCorsProxy() {
    // Check for localStorage override (set by developer)
    try {
      const override = localStorage.getItem('cors_proxy_url');
      if (override) {
        return override;
      }
    } catch (error) {
      // localStorage might be unavailable
    }

    // Development environment uses local proxy
    if (typeof window !== 'undefined' &&
        (window.location.hostname === 'localhost' ||
         window.location.hostname === '127.0.0.1')) {
      return 'http://localhost:8081';
    }

    // Production uses public CORS proxy
    return 'https://cors.isomorphic-git.org';
  }

  /**
   * Get git instance from window or global context
   * @private
   * @returns {Object} isomorphic-git module
   */
  _getGit() {
    if (typeof window !== 'undefined' && window.git) {
      return window.git;
    }
    // For Node.js environment (testing)
    try {
      return require('isomorphic-git');
    } catch (e) {
      throw new Error('isomorphic-git not available');
    }
  }

  /**
   * Get HTTP handler from window or global context
   * @private
   * @returns {Object} HTTP handler
   */
  _getHttpHandler() {
    if (typeof window !== 'undefined' && window.GitHttp) {
      return window.GitHttp;
    }
    // For Node.js environment (testing)
    try {
      const http = require('isomorphic-git/http/node');
      return http.default || http;
    } catch (e) {
      throw new Error('isomorphic-git HTTP handler not available');
    }
  }

  /**
   * Test connection to remote repository
   * Fixes Bug #3: Proper array handling for listServerRefs
   * @returns {Promise<{ok: boolean, message: string}>}
   */
  async testConnection() {
    try {
      const git = this._getGit();
      const http = this._getHttpHandler();

      const refs = await git.listServerRefs({
        http,
        url: this.config.remoteUrl,
        corsProxy: this._getCorsProxy(),
        onAuth: () => ({
          username: this.config.username,
          password: this.config.token
        })
      });

      // Bug #3 fix: Handle both array and object responses properly
      let branches = [];
      if (Array.isArray(refs)) {
        branches = refs
          .filter(ref => ref?.ref?.startsWith('refs/heads/'))
          .map(ref => ref.ref.replace('refs/heads/', ''));
      } else if (refs && typeof refs === 'object') {
        branches = Object.keys(refs)
          .filter(ref => ref.startsWith('refs/heads/'))
          .map(ref => ref.replace('refs/heads/', ''));
      }

      if (branches.length === 0) {
        return {
          ok: true,
          message: 'Connected but repository is empty. Initialize it first.'
        };
      }

      return {
        ok: true,
        message: `Connected! Found branches: ${branches.join(', ')}`
      };
    } catch (error) {
      const classified = GitSyncError.classifyError(error);
      return {
        ok: false,
        message: classified.getUserMessage()
      };
    }
  }

  /**
   * Detect the default branch on the remote
   * Fixes Bug #4: Use symrefs: true to get HEAD target
   * @returns {Promise<string|null>} Branch name or null
   */
  async detectRemoteDefaultBranch() {
    try {
      const git = this._getGit();
      const http = this._getHttpHandler();

      // Bug #4 fix: Use symrefs: true to get symbolic refs
      const refs = await git.listServerRefs({
        http,
        url: this.config.remoteUrl,
        symrefs: true, // Critical for HEAD detection
        corsProxy: this._getCorsProxy(),
        onAuth: () => ({
          username: this.config.username,
          password: this.config.token
        })
      });

      // Find HEAD ref which points to default branch
      let headRef = null;
      if (Array.isArray(refs)) {
        headRef = refs.find(r => r?.ref === 'HEAD');
      } else if (refs && typeof refs === 'object') {
        headRef = refs['HEAD'];
      }

      if (headRef?.target) {
        const match = headRef.target.match(/refs\/heads\/(.+)$/);
        if (match) {
          return match[1];
        }
      }

      return null;
    } catch (error) {
      return null;
    }
  }

  /**
   * Ensure local repository has shared history with remote
   * Fixes Bug #1: Establishes shared history before push/pull
   * @private
   * @param {string} branch - Target branch
   * @returns {Promise<void>}
   */
  async _ensureSharedHistory(branch) {
    const git = this._getGit();
    const http = this._getHttpHandler();

    try {
      // Check if remote has any refs
      const remoteRefs = await git.listServerRefs({
        http,
        url: this.config.remoteUrl,
        corsProxy: this._getCorsProxy(),
        onAuth: () => ({
          username: this.config.username,
          password: this.config.token
        })
      });

      let hasRemoteRefs = false;
      if (Array.isArray(remoteRefs)) {
        hasRemoteRefs = remoteRefs.length > 0;
      } else if (remoteRefs && typeof remoteRefs === 'object') {
        hasRemoteRefs = Object.keys(remoteRefs).length > 0;
      }

      if (!hasRemoteRefs) {
        // Remote is empty - ensure we have at least one commit
        await this._ensureInitialCommit(branch);
        return;
      }

      // Fetch remote history to establish shared base
      try {
        await git.fetch({
          fs: this.fs,
          http,
          dir: this.gitDir,
          remote: 'origin',
          corsProxy: this._getCorsProxy(),
          onAuth: () => ({
            username: this.config.username,
            password: this.config.token
          })
        });
      } catch (fetchError) {
        // Fetch might fail if remote is empty - that's OK
        // We'll try to push anyway
      }
    } catch (error) {
      // Ignore errors here - we'll catch them during push/pull
    }
  }

  /**
   * Ensure repository has at least one commit
   * @private
   * @param {string} branch - Branch name
   * @returns {Promise<void>}
   */
  async _ensureInitialCommit(branch) {
    const git = this._getGit();

    try {
      // Check if branch has any commits
      const log = await git.log({
        fs: this.fs,
        dir: this.gitDir,
        ref: branch
      });

      if (log && log.length > 0) {
        return; // Already has commits
      }
    } catch (error) {
      // Branch doesn't exist yet
    }

    // Create empty initial commit
    try {
      await git.commit({
        fs: this.fs,
        dir: this.gitDir,
        message: 'Initial commit',
        author: {
          name: this.config.author || 'Training Parser',
          email: 'local@training-parser'
        }
      });
    } catch (error) {
      // Commit might fail if branch already has commits
    }
  }

  /**
   * Push local changes to remote
   * Fixes Bug #2: No force-push fallbacks
   * @param {Object} options - Push options
   * @returns {Promise<{ok: boolean, message?: string}>}
   */
  async push(options = {}) {
    return this.lockManager.withLock('git-sync-push', async () => {
      try {
        const git = this._getGit();
        const http = this._getHttpHandler();

        const branch = options.branch ||
          await this.detectRemoteDefaultBranch() || 'main';

        // Ensure shared history with remote
        await this._ensureSharedHistory(branch);

        // Add remote
        try {
          await git.addRemote({
            fs: this.fs,
            dir: this.gitDir,
            remote: 'origin',
            url: this.config.remoteUrl,
            force: true
          });
        } catch (error) {
          // Remote might already exist
        }

        // Push without force flag (Bug #2 fix)
        const result = await git.push({
          fs: this.fs,
          http,
          dir: this.gitDir,
          remote: 'origin',
          ref: branch,
          corsProxy: this._getCorsProxy(),
          onAuth: () => ({
            username: this.config.username,
            password: this.config.token
          })
        });

        return {
          ok: true,
          message: `Pushed ${branch} successfully`
        };
      } catch (error) {
        const classified = GitSyncError.classifyError(error);
        return {
          ok: false,
          message: classified.getUserMessage()
        };
      }
    });
  }

  /**
   * Pull remote changes to local
   * @param {Object} options - Pull options
   * @returns {Promise<{ok: boolean, message?: string}>}
   */
  async pull(options = {}) {
    return this.lockManager.withLock('git-sync-pull', async () => {
      try {
        const git = this._getGit();
        const http = this._getHttpHandler();

        const branch = options.branch ||
          await this.detectRemoteDefaultBranch() || 'main';

        // Add remote
        try {
          await git.addRemote({
            fs: this.fs,
            dir: this.gitDir,
            remote: 'origin',
            url: this.config.remoteUrl,
            force: true
          });
        } catch (error) {
          // Remote might already exist
        }

        // Pull from remote
        await git.pull({
          fs: this.fs,
          http,
          dir: this.gitDir,
          remote: 'origin',
          ref: branch,
          corsProxy: this._getCorsProxy(),
          onAuth: () => ({
            username: this.config.username,
            password: this.config.token
          }),
          author: {
            name: this.config.author || 'Training Parser',
            email: 'local@training-parser'
          }
        });

        return {
          ok: true,
          message: `Pulled from ${branch} successfully`
        };
      } catch (error) {
        const classified = GitSyncError.classifyError(error);
        return {
          ok: false,
          message: classified.getUserMessage()
        };
      }
    });
  }

  /**
   * Save a workout file
   * @param {string} dateStr - Date in YYYY-MM-DD format
   * @param {Object} content - Workout content
   * @param {string} sessionId - Optional session ID
   * @returns {Promise<string>} Filename written
   */
  async saveWorkout(dateStr, content, sessionId = null) {
    return this.lockManager.withLock('git-sync-save', async () => {
      try {
        const git = this._getGit();
        const filename = await this.storage.saveWorkoutFile(
          dateStr,
          content,
          sessionId
        );

        // Stage the file
        await git.add({
          fs: this.fs,
          dir: this.gitDir,
          filepath: filename
        });

        // Commit
        await git.commit({
          fs: this.fs,
          dir: this.gitDir,
          message: `Add workout ${dateStr}`,
          author: {
            name: this.config.author || 'Training Parser',
            email: 'local@training-parser'
          }
        });

        return filename;
      } catch (error) {
        throw GitSyncError.classifyError(error);
      }
    });
  }

  /**
   * List workout files
   * @returns {Promise<string[]>} Array of filenames
   */
  async listWorkouts() {
    try {
      return await this.storage.listWorkoutFiles();
    } catch (error) {
      throw GitSyncError.classifyError(error);
    }
  }

  /**
   * Load a workout file
   * @param {string} filename - Filename to load
   * @returns {Promise<Object>} Parsed workout content
   */
  async loadWorkout(filename) {
    try {
      return await this.storage.loadWorkoutFile(filename);
    } catch (error) {
      throw GitSyncError.classifyError(error);
    }
  }

  /**
   * Acquire a lock
   * @param {string} lockId - Lock identifier
   * @param {number} timeout - Timeout in milliseconds
   * @returns {Promise<boolean>} True if acquired
   */
  async acquireLock(lockId, timeout = 30000) {
    return await this.lockManager.acquireLock(lockId, timeout);
  }

  /**
   * Release a lock
   * @param {string} lockId - Lock identifier
   * @returns {void}
   */
  async releaseLock(lockId) {
    this.lockManager.releaseLock(lockId);
  }
}
