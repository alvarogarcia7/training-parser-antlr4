/**
 * Factory for selecting and creating git-sync backends
 * Routes to GitHub API or git-protocol based on URL and environment
 */

import { GitProtocolBackend } from './git-sync-git-protocol.js';
import { GitHubAPIBackend } from './git-sync-github-api.js';

export class GitSyncFactory {
  /**
   * Determine which backend(s) to use for a given URL
   * GitHub.com → GitHub API primary, git-protocol fallback
   * Others → git-protocol
   * @private
   * @param {string} remoteUrl - Remote repository URL
   * @param {Object} config - Configuration object
   * @returns {Object} Selection with {primary, fallback}
   */
  static selectBackends(remoteUrl, config) {
    if (!remoteUrl) {
      return {
        primary: 'git-protocol',
        fallback: null
      };
    }

    // GitHub.com detected
    if (remoteUrl.includes('github.com')) {
      return {
        primary: 'github-api',
        fallback: 'git-protocol'
      };
    }

    // Other git servers use git-protocol
    return {
      primary: 'git-protocol',
      fallback: null
    };
  }

  /**
   * Create a backend instance
   * Returns adapter that tries primary, then fallback
   * @param {string} remoteUrl - Remote repository URL
   * @param {Object} config - Configuration {username, token, author}
   * @param {Object} fsModule - LightningFS instance (for git-protocol)
   * @param {string} gitDir - Git directory path
   * @returns {Object} Backend adapter with unified interface
   */
  static create(remoteUrl, config, fsModule = null, gitDir = '/workout-data') {
    const selection = this.selectBackends(remoteUrl, config);

    // Return adapter that handles both primary and fallback
    return new BackendAdapter(
      selection,
      config,
      fsModule,
      gitDir
    );
  }
}

/**
 * Backend adapter that implements the unified interface
 * Tries primary backend, falls back if it fails
 */
class BackendAdapter {
  constructor(selection, config, fsModule, gitDir) {
    this.selection = selection;
    this.config = config;
    this.fsModule = fsModule;
    this.gitDir = gitDir;
    this.backends = new Map();
    this.lastError = null;
  }

  /**
   * Get or create a backend instance
   * @private
   * @param {string} type - Backend type: 'git-protocol' or 'github-api'
   * @returns {Object} Backend instance
   */
  _getBackend(type) {
    if (this.backends.has(type)) {
      return this.backends.get(type);
    }

    let backend;

    if (type === 'github-api') {
      backend = new GitHubAPIBackend(this.config);
    } else if (type === 'git-protocol') {
      if (!this.fsModule) {
        throw new Error('LightningFS required for git-protocol backend');
      }
      backend = new GitProtocolBackend(
        this.config,
        this.fsModule,
        this.gitDir
      );
    } else {
      throw new Error(`Unknown backend type: ${type}`);
    }

    this.backends.set(type, backend);
    return backend;
  }

  /**
   * Execute a method with fallback strategy
   * @private
   * @param {string} methodName - Method name to call
   * @param {Array} args - Arguments to pass
   * @returns {Promise<any>} Result from backend
   */
  async _withFallback(methodName, args) {
    try {
      const primary = this._getBackend(this.selection.primary);

      if (typeof primary[methodName] !== 'function') {
        throw new Error(
          `Backend ${this.selection.primary} does not implement ${methodName}`
        );
      }

      return await primary[methodName](...args);
    } catch (primaryError) {
      this.lastError = primaryError;

      // Try fallback if available
      if (this.selection.fallback) {
        try {
          const fallback = this._getBackend(this.selection.fallback);

          if (typeof fallback[methodName] !== 'function') {
            throw primaryError; // Fallback doesn't have method either
          }

          return await fallback[methodName](...args);
        } catch (fallbackError) {
          // Both failed - return primary error
          throw primaryError;
        }
      }

      // No fallback, throw primary error
      throw primaryError;
    }
  }

  /**
   * Test connection to remote
   * @returns {Promise<{ok: boolean, message: string}>}
   */
  async testConnection() {
    return this._withFallback('testConnection', []);
  }

  /**
   * Push local changes
   * @param {Object} options - Push options
   * @returns {Promise<{ok: boolean, message?: string}>}
   */
  async push(options = {}) {
    return this._withFallback('push', [options]);
  }

  /**
   * Pull remote changes
   * @param {Object} options - Pull options
   * @returns {Promise<{ok: boolean, message?: string}>}
   */
  async pull(options = {}) {
    return this._withFallback('pull', [options]);
  }

  /**
   * Save a workout
   * @param {string} dateStr - Date in YYYY-MM-DD format
   * @param {Object} content - Workout content
   * @param {string} sessionId - Optional session ID
   * @returns {Promise<string>} Filename
   */
  async saveWorkout(dateStr, content, sessionId = null) {
    return this._withFallback('saveWorkout', [dateStr, content, sessionId]);
  }

  /**
   * List workouts
   * @returns {Promise<string[]>} Array of filenames
   */
  async listWorkouts() {
    return this._withFallback('listWorkouts', []);
  }

  /**
   * Load a workout
   * @param {string} filename - Filename to load
   * @returns {Promise<Object>} Workout content
   */
  async loadWorkout(filename) {
    return this._withFallback('loadWorkout', [filename]);
  }

  /**
   * Detect default branch on remote
   * @returns {Promise<string|null>} Branch name or null
   */
  async detectRemoteDefaultBranch() {
    return this._withFallback('detectRemoteDefaultBranch', []);
  }

  /**
   * Acquire a lock
   * @param {string} lockId - Lock identifier
   * @param {number} timeout - Timeout in milliseconds
   * @returns {Promise<boolean>} True if acquired
   */
  async acquireLock(lockId, timeout = 30000) {
    return this._withFallback('acquireLock', [lockId, timeout]);
  }

  /**
   * Release a lock
   * @param {string} lockId - Lock identifier
   * @returns {Promise<void>}
   */
  async releaseLock(lockId) {
    return this._withFallback('releaseLock', [lockId]);
  }

  /**
   * Get information about the active backend
   * Useful for debugging
   * @returns {Object} Backend info
   */
  getBackendInfo() {
    return {
      selection: this.selection,
      backends: Array.from(this.backends.keys()),
      lastError: this.lastError
    };
  }
}
