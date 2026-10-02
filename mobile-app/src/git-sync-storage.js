/**
 * Unified storage layer for local workout files
 * Fixes Bug #7: Unique file naming to prevent same-day conflicts
 */

export class GitSyncStorage {
  constructor(fs, gitDir) {
    this.fs = fs;
    this.gitDir = gitDir;
  }

  /**
   * Generate a session ID for same-day conflict avoidance
   * Format: first 8 chars of SHA256 hash of current timestamp
   * @returns {string} Session ID
   */
  static generateSessionId() {
    // Use timestamp + random for uniqueness
    const entropy = `${Date.now()}-${Math.random()}`;
    // Simple hash: convert to hex
    const hash = entropy.split('').reduce((acc, char) => {
      return ((acc << 5) - acc) + char.charCodeAt(0);
    }, 0).toString(16);
    return hash.substring(0, 8);
  }

  /**
   * Get the storage path for a workout file
   * Format: YYYY-MM-DD.json or YYYY-MM-DD-<sessionId>.json
   * @param {string} dateStr - Date in YYYY-MM-DD format
   * @param {string} sessionId - Optional session ID for same-day edits
   * @returns {string} Relative path within gitDir
   */
  getWorkoutPath(dateStr, sessionId = null) {
    if (sessionId) {
      return `${dateStr}-${sessionId}.json`;
    }
    return `${dateStr}.json`;
  }

  /**
   * Save a workout file to storage
   * @param {string} dateStr - Date in YYYY-MM-DD format
   * @param {Object} content - Workout content object
   * @param {string} sessionId - Optional session ID for same-day edits
   * @returns {Promise<string>} Filename written
   */
  async saveWorkoutFile(dateStr, content, sessionId = null) {
    const filename = this.getWorkoutPath(dateStr, sessionId);
    const filepath = `${this.gitDir}/${filename}`;

    try {
      const jsonContent = JSON.stringify(content, null, 2);
      await this.fs.promises.writeFile(filepath, jsonContent, 'utf8');
      return filename;
    } catch (error) {
      throw new Error(`Failed to save workout file ${filename}: ${error.message}`);
    }
  }

  /**
   * Load a workout file from storage
   * @param {string} filename - Filename to load
   * @returns {Promise<Object>} Parsed workout content
   */
  async loadWorkoutFile(filename) {
    const filepath = `${this.gitDir}/${filename}`;

    try {
      const content = await this.fs.promises.readFile(filepath, 'utf8');
      return JSON.parse(content);
    } catch (error) {
      if (error.code === 'ENOENT') {
        throw new Error(`Workout file not found: ${filename}`);
      }
      throw new Error(`Failed to load workout file ${filename}: ${error.message}`);
    }
  }

  /**
   * List all workout files in storage, sorted by date (newest first)
   * @returns {Promise<string[]>} Array of filenames
   */
  async listWorkoutFiles() {
    try {
      const files = await this.fs.promises.readdir(this.gitDir);
      return files
        .filter(f => f.endsWith('.json'))
        .sort()
        .reverse();
    } catch (error) {
      if (error.code === 'ENOENT') {
        return [];
      }
      throw new Error(`Failed to list workout files: ${error.message}`);
    }
  }

  /**
   * Get the most recent workout file for a given date
   * If multiple files exist for same date (e.g., YYYY-MM-DD.json and YYYY-MM-DD-abc123.json),
   * returns the one with session ID (most recent)
   * @param {string} dateStr - Date in YYYY-MM-DD format
   * @returns {Promise<string|null>} Most recent filename or null
   */
  async getMostRecentWorkoutForDate(dateStr) {
    try {
      const files = await this.fs.promises.readdir(this.gitDir);
      const dateFiles = files
        .filter(f => f.startsWith(dateStr) && f.endsWith('.json'))
        .sort()
        .reverse();

      return dateFiles.length > 0 ? dateFiles[0] : null;
    } catch (error) {
      return null;
    }
  }

  /**
   * Check if a file exists
   * @param {string} filename - Filename to check
   * @returns {Promise<boolean>} True if file exists
   */
  async fileExists(filename) {
    try {
      const filepath = `${this.gitDir}/${filename}`;
      await this.fs.promises.access(filepath);
      return true;
    } catch (error) {
      return false;
    }
  }

  /**
   * Delete a workout file
   * @param {string} filename - Filename to delete
   * @returns {Promise<void>}
   */
  async deleteWorkoutFile(filename) {
    const filepath = `${this.gitDir}/${filename}`;

    try {
      await this.fs.promises.unlink(filepath);
    } catch (error) {
      if (error.code !== 'ENOENT') {
        throw new Error(`Failed to delete workout file ${filename}: ${error.message}`);
      }
    }
  }
}
