/**
 * Abstract base class for git-sync backends
 * Defines the interface that all backends must implement
 */

export class GitSyncBackend {
  constructor(config) {
    if (new.target === GitSyncBackend) {
      throw new Error('GitSyncBackend is abstract and cannot be instantiated directly');
    }
    this.config = config; // { remoteUrl, username, token, author }
  }

  /**
   * Test connection to remote repository
   * @returns {Promise<{ok: boolean, message: string}>}
   */
  async testConnection() {
    throw new Error('testConnection() not implemented');
  }

  /**
   * Push local changes to remote
   * @param {Object} options - Push options
   * @param {string} options.branch - Branch to push to
   * @returns {Promise<{ok: boolean, message?: string}>}
   */
  async push(options = {}) {
    throw new Error('push() not implemented');
  }

  /**
   * Pull remote changes to local
   * @param {Object} options - Pull options
   * @param {string} options.branch - Branch to pull from
   * @returns {Promise<{ok: boolean, message?: string}>}
   */
  async pull(options = {}) {
    throw new Error('pull() not implemented');
  }

  /**
   * Save a workout to local storage and stage for commit
   * @param {string} dateStr - Date in YYYY-MM-DD format
   * @param {Object} content - Workout content
   * @param {string} sessionId - Optional session ID for same-day conflicts
   * @returns {Promise<string>} Filename written
   */
  async saveWorkout(dateStr, content, sessionId = null) {
    throw new Error('saveWorkout() not implemented');
  }

  /**
   * List available workouts
   * @returns {Promise<string[]>} Array of filenames
   */
  async listWorkouts() {
    throw new Error('listWorkouts() not implemented');
  }

  /**
   * Load a workout by filename
   * @param {string} filename - Filename to load
   * @returns {Promise<Object>} Parsed workout content
   */
  async loadWorkout(filename) {
    throw new Error('loadWorkout() not implemented');
  }

  /**
   * Detect the default branch on the remote repository
   * @returns {Promise<string|null>} Branch name or null if not detected
   */
  async detectRemoteDefaultBranch() {
    throw new Error('detectRemoteDefaultBranch() not implemented');
  }

  /**
   * Acquire an exclusive lock for write operations
   * @param {string} lockId - Lock identifier
   * @param {number} timeout - Lock timeout in milliseconds
   * @returns {Promise<boolean>} True if lock acquired
   */
  async acquireLock(lockId, timeout = 30000) {
    throw new Error('acquireLock() not implemented');
  }

  /**
   * Release a lock
   * @param {string} lockId - Lock identifier
   * @returns {Promise<void>}
   */
  async releaseLock(lockId) {
    throw new Error('releaseLock() not implemented');
  }
}
