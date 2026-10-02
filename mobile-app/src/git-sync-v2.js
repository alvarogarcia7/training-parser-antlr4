/**
 * Git sync module v2 - Unified interface for dual backends
 * Provides backward compatible API while using new modular backends
 * Fixes all 9 known bugs from original implementation
 */

import { GitSyncFactory } from './git-sync-factory.js';

// State management
let backend = null;
let fs = null;
let gitReady = false;

// Settings persistence (reuse from original module)
const SETTINGS_KEY = 'git_settings';

/**
 * Load settings from localStorage
 * @returns {Object} Settings object
 */
export function loadSettings() {
  const raw = localStorage.getItem(SETTINGS_KEY);
  return raw ? JSON.parse(raw) : {
    remoteUrl: '',
    username: '',
    token: '',
    author: 'Training Parser'
  };
}

/**
 * Save settings to localStorage
 * @param {Object} settings - Settings object
 */
export function saveSettings(settings) {
  localStorage.setItem(SETTINGS_KEY, JSON.stringify(settings));
}

/**
 * Initialize git system
 * Creates LightningFS instance and backend
 */
export async function initGit() {
  if (gitReady) {
    return;
  }

  try {
    const settings = loadSettings();

    // Create LightningFS instance for git-protocol backend
    if (typeof window !== 'undefined' && window.LightningFS) {
      fs = new window.LightningFS('workout-git');
    }

    // Create backend adapter
    backend = GitSyncFactory.create(
      settings.remoteUrl,
      settings,
      fs,
      '/workout-data'
    );

    gitReady = true;
  } catch (error) {
    gitReady = false;
    throw error;
  }
}

/**
 * Test connection to remote repository
 * @returns {Promise<{ok: boolean, message: string}>}
 */
export async function testConnection() {
  try {
    const settings = loadSettings();

    if (!settings.remoteUrl) {
      return {
        ok: false,
        message: 'No remote URL configured'
      };
    }

    if (!backend) {
      backend = GitSyncFactory.create(
        settings.remoteUrl,
        settings,
        fs,
        '/workout-data'
      );
    }

    return await backend.testConnection();
  } catch (error) {
    return {
      ok: false,
      message: error.message || 'Connection test failed'
    };
  }
}

/**
 * Push local changes to remote
 * @returns {Promise<{ok: boolean, message?: string}>}
 */
export async function push() {
  if (!gitReady) {
    await initGit();
  }

  if (!backend) {
    return {
      ok: false,
      message: 'Backend not initialized'
    };
  }

  try {
    return await backend.push();
  } catch (error) {
    return {
      ok: false,
      message: error.message || 'Push failed'
    };
  }
}

/**
 * Pull remote changes to local
 * @returns {Promise<{ok: boolean, message?: string}>}
 */
export async function pull() {
  if (!gitReady) {
    await initGit();
  }

  if (!backend) {
    return {
      ok: false,
      message: 'Backend not initialized'
    };
  }

  try {
    return await backend.pull();
  } catch (error) {
    return {
      ok: false,
      message: error.message || 'Pull failed'
    };
  }
}

/**
 * Save a workout to local storage
 * @param {string} dateStr - Date in YYYY-MM-DD format
 * @param {Object} content - Workout content
 * @returns {Promise<string>} Filename written
 */
export async function saveWorkout(dateStr, content) {
  if (!gitReady) {
    await initGit();
  }

  if (!backend) {
    throw new Error('Backend not initialized');
  }

  try {
    // Generate session ID for same-day conflict avoidance
    const sessionId = Math.random().toString(36).substring(2, 10);
    return await backend.saveWorkout(dateStr, content, sessionId);
  } catch (error) {
    throw new Error(`Failed to save workout: ${error.message}`);
  }
}

/**
 * List available workouts
 * @returns {Promise<string[]>} Array of filenames
 */
export async function listWorkouts() {
  if (!gitReady) {
    await initGit();
  }

  if (!backend) {
    return [];
  }

  try {
    return await backend.listWorkouts();
  } catch (error) {
    return [];
  }
}

/**
 * Load a workout by filename
 * @param {string} filename - Filename to load
 * @returns {Promise<Object>} Parsed workout content
 */
export async function loadWorkout(filename) {
  if (!gitReady) {
    await initGit();
  }

  if (!backend) {
    throw new Error('Backend not initialized');
  }

  try {
    return await backend.loadWorkout(filename);
  } catch (error) {
    throw new Error(`Failed to load workout: ${error.message}`);
  }
}

/**
 * Get backend info (for debugging)
 * @returns {Object} Backend configuration and info
 */
export function getBackendInfo() {
  if (!backend) {
    return { initialized: false };
  }

  return {
    initialized: true,
    backendInfo: backend.getBackendInfo ? backend.getBackendInfo() : {}
  };
}
