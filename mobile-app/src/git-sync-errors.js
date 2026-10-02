/**
 * Unified error classification for git-sync operations
 * Fixes Bug #6: Proper error classification using both .code field and message patterns
 */

export class GitSyncError extends Error {
  constructor(message, code, originalError = null) {
    super(message);
    this.name = 'GitSyncError';
    this.code = code;
    this.originalError = originalError;
  }

  /**
   * Classify an error from any source into a GitSyncError with typed code
   * @param {Error|string} error - Error to classify
   * @returns {GitSyncError} Classified error with code
   */
  static classifyError(error) {
    const message = error?.message || String(error);
    const code = error?.code;

    // First, check for error.code field (isomorphic-git pattern)
    if (code) {
      if (code.includes('NotFound') || code === 'ENOENT') {
        return new GitSyncError(
          `Not found: ${message}`,
          'ERR_NOT_FOUND',
          error
        );
      }
      if (code.includes('Unauthorized') || code.includes('Auth')) {
        return new GitSyncError(
          `Authentication failed: ${message}`,
          'ERR_AUTH_FAILED',
          error
        );
      }
      if (code === 'ECONNREFUSED' || code === 'ECONNRESET') {
        return new GitSyncError(
          `Network error: ${message}`,
          'ERR_NETWORK',
          error
        );
      }
      if (code.includes('Conflict') || code.includes('CONFLICT')) {
        return new GitSyncError(
          `Conflict: ${message}`,
          'ERR_CONFLICTS',
          error
        );
      }
    }

    // Fall back to message string matching
    const msgLower = message.toLowerCase();

    if (msgLower.includes('401') || msgLower.includes('403') ||
        msgLower.includes('unauthorized') || msgLower.includes('authentication failed') ||
        msgLower.includes('invalid credentials')) {
      return new GitSyncError(
        `Authentication failed: ${message}`,
        'ERR_AUTH_FAILED',
        error
      );
    }

    if (msgLower.includes('404') || msgLower.includes('not found') ||
        msgLower.includes('no such') || msgLower.includes('does not exist')) {
      return new GitSyncError(
        `Not found: ${message}`,
        'ERR_NOT_FOUND',
        error
      );
    }

    if (msgLower.includes('cors') || msgLower.includes('access-control') ||
        msgLower.includes('cross-origin') || msgLower.includes('cross origin')) {
      return new GitSyncError(
        `CORS error: ${message}`,
        'ERR_CORS',
        error
      );
    }

    if (msgLower.includes('unrelated histories') || msgLower.includes('unrelated')) {
      return new GitSyncError(
        `Unrelated histories: ${message}`,
        'ERR_UNRELATED_HISTORIES',
        error
      );
    }

    if (msgLower.includes('conflict') || msgLower.includes('merge conflict') ||
        msgLower.includes('diverged')) {
      return new GitSyncError(
        `Conflict: ${message}`,
        'ERR_CONFLICTS',
        error
      );
    }

    if (msgLower.includes('non-fast-forward') || msgLower.includes('fast-forward')) {
      return new GitSyncError(
        `Not fast-forward: ${message}`,
        'ERR_NOT_FAST_FORWARD',
        error
      );
    }

    if (msgLower.includes('network') || msgLower.includes('econnrefused') ||
        msgLower.includes('econnreset') || msgLower.includes('timeout') ||
        msgLower.includes('fetch failed') || msgLower.includes('connection')) {
      return new GitSyncError(
        `Network error: ${message}`,
        'ERR_NETWORK',
        error
      );
    }

    // Default: generic server error
    return new GitSyncError(
      message,
      'ERR_SERVER',
      error
    );
  }

  /**
   * Get user-friendly error message based on error code
   * @returns {string} User-friendly message
   */
  getUserMessage() {
    switch (this.code) {
      case 'ERR_NOT_FOUND':
        return 'Repository or file not found. Check the URL.';
      case 'ERR_AUTH_FAILED':
        return 'Authentication failed. Check your credentials.';
      case 'ERR_CORS':
        return 'CORS blocked. Use a different backend or proxy.';
      case 'ERR_UNRELATED_HISTORIES':
        return 'Incompatible history. Try pulling a different branch.';
      case 'ERR_CONFLICTS':
        return 'Merge conflict detected. Resolve manually.';
      case 'ERR_NOT_FAST_FORWARD':
        return 'Branch has diverged. Pull before pushing.';
      case 'ERR_NETWORK':
        return 'Network connection failed. Check your connection.';
      case 'ERR_SERVER':
        return `Server error: ${this.message}`;
      default:
        return this.message;
    }
  }
}
