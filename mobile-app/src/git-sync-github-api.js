/**
 * GitHub REST API backend for git-sync
 * Fixes Bugs #2, #4, #5 related to GitHub integration
 */

import { GitSyncBackend } from './git-sync-backend-base.js';
import { GitSyncError } from './git-sync-errors.js';
import { GitSyncStorage } from './git-sync-storage.js';
import { GitSyncLockManager } from './git-sync-lock.js';

export class GitHubAPIBackend extends GitSyncBackend {
  constructor(config) {
    super(config);

    // Parse GitHub URL: https://github.com/owner/repo.git
    const match = config.remoteUrl.match(
      /github\.com[:/]([^/]+)\/([^/.]+)(\.git)?$/
    );

    if (!match) {
      throw new Error(
        `Invalid GitHub URL: ${config.remoteUrl}. ` +
        `Expected format: https://github.com/owner/repo.git or https://github.com/owner/repo`
      );
    }

    this.owner = match[1];
    this.repo = match[2];
    this.apiBase = 'https://api.github.com';
    this.storage = new GitSyncStorage(null, '/workout-data');
    this.lockManager = new GitSyncLockManager();
  }

  /**
   * Get Authorization header with Basic auth
   * Bug #5 fix: Token never embedded in URL
   * @private
   * @returns {Object} Headers object with Authorization
   */
  _getAuthHeaders() {
    if (!this.config.username || !this.config.token) {
      return {};
    }

    // Use GitHub token auth format: username:token
    const credentials = `${this.config.username}:${this.config.token}`;
    const encoded = typeof btoa !== 'undefined'
      ? btoa(credentials)
      : Buffer.from(credentials).toString('base64');

    return {
      'Authorization': `Basic ${encoded}`,
      'Accept': 'application/vnd.github.v3+json'
    };
  }

  /**
   * Make authenticated API request
   * @private
   * @param {string} endpoint - API endpoint path (without base)
   * @param {Object} options - Fetch options
   * @returns {Promise<Response>} Response object
   */
  async _apiRequest(endpoint, options = {}) {
    const url = `${this.apiBase}${endpoint}`;
    const headers = {
      ...this._getAuthHeaders(),
      ...(options.headers || {})
    };

    const response = await fetch(url, {
      ...options,
      headers
    });

    return response;
  }

  /**
   * Test connection to GitHub repository
   * @returns {Promise<{ok: boolean, message: string}>}
   */
  async testConnection() {
    try {
      const response = await this._apiRequest(
        `/repos/${this.owner}/${this.repo}`
      );

      if (response.status === 200) {
        const data = await response.json();
        return {
          ok: true,
          message: `Connected to ${data.full_name} (${data.default_branch})`
        };
      } else if (response.status === 404) {
        return {
          ok: false,
          message: 'Repository not found'
        };
      } else if (response.status === 401 || response.status === 403) {
        return {
          ok: false,
          message: 'Authentication failed. Check username and token.'
        };
      } else {
        return {
          ok: false,
          message: `GitHub API error: ${response.status}`
        };
      }
    } catch (error) {
      const classified = GitSyncError.classifyError(error);
      return {
        ok: false,
        message: classified.getUserMessage()
      };
    }
  }

  /**
   * Detect default branch on GitHub
   * Bug #4 fix: Uses GitHub API default_branch field directly
   * @returns {Promise<string|null>} Branch name or null
   */
  async detectRemoteDefaultBranch() {
    try {
      const response = await this._apiRequest(
        `/repos/${this.owner}/${this.repo}`
      );

      if (response.ok) {
        const data = await response.json();
        return data.default_branch;
      }

      return null;
    } catch (error) {
      return null;
    }
  }

  /**
   * List files in a directory on GitHub
   * @private
   * @param {string} path - Path in repository
   * @returns {Promise<Array>} Array of file entries
   */
  async _listRemoteFiles(path = '') {
    try {
      const endpoint = `/repos/${this.owner}/${this.repo}/contents/${path}`;
      const response = await this._apiRequest(endpoint);

      if (!response.ok) {
        if (response.status === 404) {
          return [];
        }
        throw new Error(`GitHub API error: ${response.status}`);
      }

      const data = await response.json();
      if (!Array.isArray(data)) {
        return [];
      }

      return data.filter(item => item.type === 'file' && item.name.endsWith('.json'));
    } catch (error) {
      throw GitSyncError.classifyError(error);
    }
  }

  /**
   * Get file contents from GitHub
   * @private
   * @param {string} path - Path in repository
   * @returns {Promise<string|null>} File content or null if not found
   */
  async _getRemoteFile(path) {
    try {
      const endpoint = `/repos/${this.owner}/${this.repo}/contents/${path}`;
      const response = await this._apiRequest(endpoint);

      if (!response.ok) {
        if (response.status === 404) {
          return null;
        }
        throw new Error(`GitHub API error: ${response.status}`);
      }

      const data = await response.json();

      // Content is base64 encoded by GitHub API
      if (data.content) {
        const decoded = typeof atob !== 'undefined'
          ? atob(data.content)
          : Buffer.from(data.content, 'base64').toString('utf-8');
        return decoded;
      }

      return null;
    } catch (error) {
      throw GitSyncError.classifyError(error);
    }
  }

  /**
   * Create or update file on GitHub
   * @private
   * @param {string} path - Path in repository
   * @param {string} content - File content
   * @param {string} message - Commit message
   * @returns {Promise<{ok: boolean, sha?: string}>}
   */
  async _putRemoteFile(path, content, message) {
    try {
      // Get current SHA for update (not needed for create)
      let sha = null;
      try {
        const response = await this._apiRequest(
          `/repos/${this.owner}/${this.repo}/contents/${path}`
        );
        if (response.ok) {
          const data = await response.json();
          sha = data.sha;
        }
      } catch (error) {
        // File doesn't exist, that's OK
      }

      // Encode content to base64
      const encoded = typeof btoa !== 'undefined'
        ? btoa(content)
        : Buffer.from(content).toString('base64');

      const body = {
        message,
        content: encoded
      };

      if (sha) {
        body.sha = sha;
      }

      const response = await this._apiRequest(
        `/repos/${this.owner}/${this.repo}/contents/${path}`,
        {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(body)
        }
      );

      if (response.ok) {
        const data = await response.json();
        return { ok: true, sha: data.content.sha };
      } else if (response.status === 409) {
        // Conflict - file was modified
        throw new GitSyncError(
          'File was modified on GitHub. Pull before pushing.',
          'ERR_CONFLICTS'
        );
      } else if (response.status === 401 || response.status === 403) {
        throw new GitSyncError(
          'Authentication failed. Check token.',
          'ERR_AUTH_FAILED'
        );
      } else {
        throw new Error(`GitHub API error: ${response.status}`);
      }
    } catch (error) {
      if (error instanceof GitSyncError) {
        throw error;
      }
      throw GitSyncError.classifyError(error);
    }
  }

  /**
   * Push local workouts to GitHub
   * @param {Object} options - Push options
   * @returns {Promise<{ok: boolean, message?: string}>}
   */
  async push(options = {}) {
    return this.lockManager.withLock('git-sync-push', async () => {
      try {
        // Get list of local files
        const localFiles = await this.storage.listWorkoutFiles();

        if (localFiles.length === 0) {
          return {
            ok: true,
            message: 'No local workouts to push'
          };
        }

        // Push each file to GitHub
        let pushed = 0;
        for (const filename of localFiles) {
          try {
            const content = await this.storage.loadWorkoutFile(filename);
            const jsonContent = JSON.stringify(content, null, 2);

            await this._putRemoteFile(
              filename,
              jsonContent,
              `Add/update workout: ${filename}`
            );
            pushed++;
          } catch (error) {
            // Continue pushing other files
            if (error.code === 'ERR_CONFLICTS') {
              // Conflict - user needs to pull first
              return {
                ok: false,
                message: 'Conflict: pull from GitHub first'
              };
            }
          }
        }

        return {
          ok: true,
          message: `Pushed ${pushed}/${localFiles.length} files`
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
   * Pull workouts from GitHub
   * @param {Object} options - Pull options
   * @returns {Promise<{ok: boolean, message?: string}>}
   */
  async pull(options = {}) {
    return this.lockManager.withLock('git-sync-pull', async () => {
      try {
        // List remote files
        const remoteFiles = await this._listRemoteFiles();

        if (remoteFiles.length === 0) {
          return {
            ok: true,
            message: 'No workouts on GitHub'
          };
        }

        // Pull each file
        let pulled = 0;
        for (const fileEntry of remoteFiles) {
          try {
            const filename = fileEntry.name;
            const content = await this._getRemoteFile(filename);

            if (content) {
              const parsed = JSON.parse(content);
              await this.storage.saveWorkoutFile(
                filename.replace('.json', ''),
                parsed
              );
              pulled++;
            }
          } catch (error) {
            // Continue pulling other files
          }
        }

        return {
          ok: true,
          message: `Pulled ${pulled}/${remoteFiles.length} files`
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
   * Save a workout (stub - GitHub API doesn't track local files)
   * @param {string} dateStr - Date in YYYY-MM-DD format
   * @param {Object} content - Workout content
   * @param {string} sessionId - Optional session ID
   * @returns {Promise<string>} Filename
   */
  async saveWorkout(dateStr, content, sessionId = null) {
    // GitHub API backend doesn't maintain local files
    // This is handled by the git-protocol backend
    throw new Error('GitHub API backend requires git-protocol for local storage');
  }

  /**
   * List workouts (stub)
   * @returns {Promise<string[]>} Array of filenames
   */
  async listWorkouts() {
    // GitHub API backend doesn't maintain local files
    throw new Error('GitHub API backend requires git-protocol for local storage');
  }

  /**
   * Load a workout (stub)
   * @param {string} filename - Filename to load
   * @returns {Promise<Object>} Workout content
   */
  async loadWorkout(filename) {
    // GitHub API backend doesn't maintain local files
    throw new Error('GitHub API backend requires git-protocol for local storage');
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
