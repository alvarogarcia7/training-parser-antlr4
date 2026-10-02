/**
 * Single-writer lock manager for browser-based coordination
 * Fixes Bug #8: Prevents concurrent writes between tabs
 */

export class GitSyncLockManager {
  constructor(storagePrefix = 'git_sync_lock_') {
    this.prefix = storagePrefix;
    this.locks = new Map();
    this.pollInterval = 100; // ms between lock acquisition attempts
  }

  /**
   * Acquire an exclusive lock for an operation
   * Uses localStorage to coordinate across tabs/windows
   * @param {string} lockId - Unique lock identifier (e.g., 'git-sync-push')
   * @param {number} timeout - Lock timeout in milliseconds
   * @returns {Promise<boolean>} True if lock acquired
   */
  async acquireLock(lockId, timeout = 30000) {
    const lockKey = `${this.prefix}${lockId}`;
    const acquiredTime = Date.now();
    const expirationTime = acquiredTime + timeout;

    return new Promise((resolve, reject) => {
      const startTime = Date.now();

      const attempt = () => {
        const now = Date.now();
        const remaining = expirationTime - now;

        if (remaining <= 0) {
          // Lock acquisition timeout exceeded
          reject(new Error(
            `Failed to acquire lock "${lockId}" after ${timeout}ms ` +
            `(possibly held by another tab)`
          ));
          return;
        }

        try {
          // Read current lock value
          const existing = localStorage.getItem(lockKey);

          if (!existing) {
            // No lock exists - claim it
            localStorage.setItem(lockKey, String(expirationTime));
            this.locks.set(lockId, {
              acquiredTime: now,
              expirationTime,
              lockKey
            });
            resolve(true);
            return;
          }

          const existingExpiry = parseInt(existing);

          if (isNaN(existingExpiry) || existingExpiry < now) {
            // Lock expired - claim it
            localStorage.setItem(lockKey, String(expirationTime));
            this.locks.set(lockId, {
              acquiredTime: now,
              expirationTime,
              lockKey
            });
            resolve(true);
            return;
          }

          // Lock is held by another tab - retry
          setTimeout(attempt, this.pollInterval);
        } catch (error) {
          // localStorage might be unavailable (private browsing) - skip locking
          resolve(true);
        }
      };

      attempt();
    });
  }

  /**
   * Release a lock
   * @param {string} lockId - Lock identifier
   * @returns {void}
   */
  releaseLock(lockId) {
    const lockKey = `${this.prefix}${lockId}`;

    try {
      localStorage.removeItem(lockKey);
    } catch (error) {
      // localStorage might be unavailable
    }

    this.locks.delete(lockId);
  }

  /**
   * Execute a function with a lock held
   * Automatically acquires and releases the lock
   * @param {string} lockId - Lock identifier
   * @param {Function} fn - Async function to execute with lock
   * @param {Object} options - Lock options
   * @param {number} options.timeout - Lock timeout (default 30000ms)
   * @returns {Promise<any>} Result of fn()
   */
  async withLock(lockId, fn, options = {}) {
    const { timeout = 30000 } = options;

    try {
      await this.acquireLock(lockId, timeout);
      return await fn();
    } finally {
      this.releaseLock(lockId);
    }
  }

  /**
   * Check if a lock is currently held
   * @param {string} lockId - Lock identifier
   * @returns {boolean} True if lock is held
   */
  isLocked(lockId) {
    try {
      const lockKey = `${this.prefix}${lockId}`;
      const existing = localStorage.getItem(lockKey);

      if (!existing) {
        return false;
      }

      const expiry = parseInt(existing);
      if (isNaN(expiry) || expiry < Date.now()) {
        return false;
      }

      return true;
    } catch (error) {
      return false;
    }
  }

  /**
   * Clear all locks (useful for testing or cleanup)
   * @returns {void}
   */
  clearAllLocks() {
    try {
      for (const [lockId] of this.locks) {
        const lockKey = `${this.prefix}${lockId}`;
        localStorage.removeItem(lockKey);
      }
    } catch (error) {
      // localStorage might be unavailable
    }

    this.locks.clear();
  }
}
