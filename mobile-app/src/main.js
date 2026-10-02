/**
 * Main initialization module for Training Parser PWA
 * Handles settings UI integration, backend selection, and initialization
 */

// Import git-sync v2 functions
import * as GitSync from './git-sync-v2.js';

// Settings key for localStorage
const GIT_SETTINGS_KEY = 'git_settings';

/**
 * Settings Management Module
 */
export class SettingsManager {
  constructor() {
    this.settings = this.loadSettings();
  }

  /**
   * Load settings from localStorage
   * @returns {Object} Current settings
   */
  loadSettings() {
    const raw = localStorage.getItem(GIT_SETTINGS_KEY);
    return raw ? JSON.parse(raw) : this.getDefaults();
  }

  /**
   * Get default settings
   * @returns {Object} Default settings
   */
  getDefaults() {
    return {
      remoteUrl: '',
      username: '',
      token: '', // Never persisted, will be empty on reload
      author: 'Training Parser User',
      backend: 'auto', // auto, github-api, git-protocol
      corsProxyUrl: 'http://localhost:8081',
      lastSync: null,
      syncStatus: 'unknown' // unknown, synced, dirty, error
    };
  }

  /**
   * Save settings to localStorage
   * @param {Object} settings - Settings to save
   */
  saveSettings(settings) {
    // Never persist token - keep it memory-only
    const toStore = { ...settings };
    delete toStore.token;

    localStorage.setItem(GIT_SETTINGS_KEY, JSON.stringify(toStore));
    this.settings = this.loadSettings();
  }

  /**
   * Clear all settings
   */
  clearSettings() {
    localStorage.removeItem(GIT_SETTINGS_KEY);
    this.settings = this.getDefaults();
  }

  /**
   * Get current setting value
   * @param {string} key - Setting key
   * @returns {any} Setting value
   */
  getSetting(key) {
    return this.settings[key];
  }

  /**
   * Update single setting
   * @param {string} key - Setting key
   * @param {any} value - New value
   */
  setSetting(key, value) {
    this.settings[key] = value;
    this.saveSettings(this.settings);
  }

  /**
   * Test connection with current settings
   * @param {string} token - Token to test (not persisted)
   * @returns {Promise<{ok: boolean, message: string}>}
   */
  async testConnection(token) {
    try {
      // Temporarily set token in memory
      const tempSettings = { ...this.settings, token };

      // Initialize with test settings
      const tempBackend = GitSync.GitSyncFactory.create(
        tempSettings.remoteUrl,
        tempSettings,
        null, // No FS needed for connection test
        '/workout-data'
      );

      // This would be implemented in backends
      if (!tempBackend.testConnection) {
        return {
          ok: false,
          message: 'Backend does not support connection test'
        };
      }

      return await tempBackend.testConnection();
    } catch (error) {
      return {
        ok: false,
        message: error.message || 'Connection test failed'
      };
    }
  }

  /**
   * Get information about active backend
   * @returns {Object} Backend info
   */
  getBackendInfo() {
    return {
      settings: {
        remoteUrl: this.settings.remoteUrl,
        username: this.settings.username,
        author: this.settings.author,
        backend: this.settings.backend,
        corsProxyUrl: this.settings.corsProxyUrl,
        lastSync: this.settings.lastSync,
        syncStatus: this.settings.syncStatus
      },
      tokenConfigured: !!this.settings.token && this.settings.token.length > 0,
      tokenNotPersisted: true // Important: Token not in localStorage
    };
  }
}

/**
 * Settings UI Controller
 * Manages the settings UI in the HTML interface
 */
export class SettingsUI {
  constructor(containerSelector = '#settings-panel') {
    this.container = document.querySelector(containerSelector);
    this.settingsManager = new SettingsManager();
    this.isVisible = false;

    if (!this.container) {
      console.warn(`Settings container not found: ${containerSelector}`);
      return;
    }

    this.setupUI();
    this.attachEventListeners();
  }

  /**
   * Set up the settings UI HTML structure
   */
  setupUI() {
    if (!this.container) return;

    this.container.innerHTML = `
      <div class="settings-panel">
        <div class="settings-header">
          <h2>Git Sync Settings</h2>
          <button class="settings-close" aria-label="Close settings">&times;</button>
        </div>

        <div class="settings-content">
          <!-- Remote URL -->
          <div class="settings-group">
            <label for="remote-url">Remote URL</label>
            <input
              type="text"
              id="remote-url"
              placeholder="https://github.com/user/repo.git"
              aria-label="Remote repository URL"
            >
            <small>GitHub: https://github.com/user/repo.git | Local: git://localhost:8888/repo.git</small>
          </div>

          <!-- Backend Selection -->
          <div class="settings-group">
            <label for="backend-select">Backend</label>
            <select id="backend-select" aria-label="Git sync backend">
              <option value="auto">Auto (recommended)</option>
              <option value="github-api">GitHub API</option>
              <option value="git-protocol">git-protocol</option>
            </select>
            <small>Auto selects GitHub API for github.com, git-protocol for others</small>
          </div>

          <!-- GitHub Username -->
          <div class="settings-group">
            <label for="username">Username (GitHub)</label>
            <input
              type="text"
              id="username"
              placeholder="your-github-username"
              aria-label="GitHub username"
            >
            <small>Your GitHub username for GitHub API backend</small>
          </div>

          <!-- Token Input -->
          <div class="settings-group">
            <label for="token">Token / Password</label>
            <input
              type="password"
              id="token"
              placeholder="ghp_... or personal access token"
              aria-label="Personal access token (not persisted)"
            >
            <small>🔒 Tokens are NOT saved to disk. Kept in memory only during session.</small>
          </div>

          <!-- CORS Proxy (for git-protocol) -->
          <div class="settings-group">
            <label for="cors-proxy">CORS Proxy URL (optional)</label>
            <input
              type="text"
              id="cors-proxy"
              placeholder="http://localhost:8081"
              aria-label="CORS proxy URL for git-protocol"
            >
            <small>Required for git-protocol from web context. Leave empty if not needed.</small>
          </div>

          <!-- Author Name -->
          <div class="settings-group">
            <label for="author">Author Name</label>
            <input
              type="text"
              id="author"
              placeholder="Your Name"
              aria-label="Author name for commits"
            >
            <small>Name to use in commits to remote</small>
          </div>

          <!-- Connection Test -->
          <div class="settings-group">
            <button id="test-connection-btn" class="btn-primary">
              Test Connection
            </button>
            <div id="connection-status" class="status-message"></div>
          </div>

          <!-- Backend Info -->
          <div class="settings-group info-box">
            <h3>Active Backend Info</h3>
            <div id="backend-info">
              <p>No backend configured</p>
            </div>
          </div>

          <!-- Clear Data -->
          <div class="settings-group danger-zone">
            <h3>Danger Zone</h3>
            <button id="clear-settings-btn" class="btn-danger">
              Clear All Settings
            </button>
            <button id="clear-cache-btn" class="btn-danger">
              Clear Local Cache
            </button>
            <small>⚠️ Clearing cache will remove local workouts. Only do this if they're synced to remote.</small>
          </div>

          <!-- Actions -->
          <div class="settings-actions">
            <button id="save-settings-btn" class="btn-primary">Save Settings</button>
            <button id="close-settings-btn" class="btn-secondary">Close</button>
          </div>
        </div>
      </div>
    `;

    // Load current values
    this.loadUIValues();
  }

  /**
   * Load current settings into UI
   */
  loadUIValues() {
    const settings = this.settingsManager.loadSettings();

    const elements = {
      'remote-url': settings.remoteUrl,
      'backend-select': settings.backend,
      'username': settings.username,
      'token': '', // Never show stored token
      'cors-proxy': settings.corsProxyUrl,
      'author': settings.author
    };

    for (const [id, value] of Object.entries(elements)) {
      const element = document.getElementById(id);
      if (element) {
        element.value = value || '';
      }
    }

    this.updateBackendInfo();
  }

  /**
   * Attach event listeners
   */
  attachEventListeners() {
    if (!this.container) return;

    // Save settings
    const saveBtn = document.getElementById('save-settings-btn');
    if (saveBtn) {
      saveBtn.addEventListener('click', () => this.saveSettings());
    }

    // Test connection
    const testBtn = document.getElementById('test-connection-btn');
    if (testBtn) {
      testBtn.addEventListener('click', () => this.testConnection());
    }

    // Clear settings
    const clearBtn = document.getElementById('clear-settings-btn');
    if (clearBtn) {
      clearBtn.addEventListener('click', () => this.clearSettings());
    }

    // Clear cache
    const cacheBtn = document.getElementById('clear-cache-btn');
    if (cacheBtn) {
      cacheBtn.addEventListener('click', () => this.clearCache());
    }

    // Close buttons
    const closeButtons = [
      document.getElementById('close-settings-btn'),
      document.querySelector('.settings-close')
    ];

    for (const btn of closeButtons) {
      if (btn) {
        btn.addEventListener('click', () => this.hide());
      }
    }

    // Update backend info on input change
    const inputs = this.container.querySelectorAll('input, select');
    for (const input of inputs) {
      input.addEventListener('change', () => this.updateBackendInfo());
    }
  }

  /**
   * Save settings from UI
   */
  saveSettings() {
    const settings = {
      remoteUrl: document.getElementById('remote-url')?.value || '',
      backend: document.getElementById('backend-select')?.value || 'auto',
      username: document.getElementById('username')?.value || '',
      token: document.getElementById('token')?.value || '', // In memory only
      corsProxyUrl: document.getElementById('cors-proxy')?.value || '',
      author: document.getElementById('author')?.value || 'Training Parser User'
    };

    // Preserve timestamps
    const current = this.settingsManager.loadSettings();
    settings.lastSync = current.lastSync;
    settings.syncStatus = current.syncStatus;

    this.settingsManager.saveSettings(settings);
    this.showMessage('Settings saved', 'success');
  }

  /**
   * Test connection to remote
   */
  async testConnection() {
    const token = document.getElementById('token')?.value || '';
    const statusDiv = document.getElementById('connection-status');

    if (!statusDiv) return;

    statusDiv.className = 'status-message testing';
    statusDiv.textContent = 'Testing connection...';

    try {
      const result = await this.settingsManager.testConnection(token);

      if (result.ok) {
        statusDiv.className = 'status-message success';
        statusDiv.textContent = `✓ ${result.message}`;
      } else {
        statusDiv.className = 'status-message error';
        statusDiv.textContent = `✗ ${result.message}`;
      }
    } catch (error) {
      statusDiv.className = 'status-message error';
      statusDiv.textContent = `✗ Connection test failed: ${error.message}`;
    }
  }

  /**
   * Update backend info display
   */
  updateBackendInfo() {
    const infoDiv = document.getElementById('backend-info');
    if (!infoDiv) return;

    const backend = document.getElementById('backend-select')?.value || 'auto';
    const url = document.getElementById('remote-url')?.value || '';
    const backendInfo = this.settingsManager.getBackendInfo();

    let html = '<dl>';
    html += `<dt>Backend:</dt><dd>${backend}</dd>`;
    html += `<dt>URL:</dt><dd>${url || 'Not configured'}</dd>`;
    html += `<dt>Token:</dt><dd>${backendInfo.tokenConfigured ? '✓ Configured (not saved)' : '✗ Not configured'}</dd>`;
    html += `<dt>Sync Status:</dt><dd>${backendInfo.settings.syncStatus}</dd>`;
    html += `<dt>Last Sync:</dt><dd>${backendInfo.settings.lastSync || 'Never'}</dd>`;
    html += '</dl>';

    infoDiv.innerHTML = html;
  }

  /**
   * Clear all settings
   */
  clearSettings() {
    if (confirm('Clear all settings? This will not delete local workouts.')) {
      this.settingsManager.clearSettings();
      this.loadUIValues();
      this.showMessage('Settings cleared', 'success');
    }
  }

  /**
   * Clear local cache
   */
  clearCache() {
    if (confirm('Clear all local workouts? This cannot be undone unless you have a remote backup.')) {
      // Clear IndexedDB
      if (window.indexedDB) {
        const req = indexedDB.databases ? indexedDB.databases().then(dbs => {
          dbs.forEach(db => {
            indexedDB.deleteDatabase(db.name);
          });
        }) : Promise.resolve();

        req.then(() => {
          this.showMessage('Cache cleared', 'success');
        });
      } else {
        this.showMessage('Cache cleared', 'success');
      }
    }
  }

  /**
   * Show temporary message
   * @param {string} message - Message text
   * @param {string} type - Type: success, error, warning
   */
  showMessage(message, type = 'info') {
    const statusDiv = document.getElementById('connection-status');
    if (!statusDiv) return;

    const typeClass = `status-message ${type}`;
    const prefix = {
      success: '✓',
      error: '✗',
      warning: '⚠'
    }[type] || 'ℹ';

    statusDiv.className = typeClass;
    statusDiv.textContent = `${prefix} ${message}`;

    setTimeout(() => {
      statusDiv.textContent = '';
      statusDiv.className = 'status-message';
    }, 3000);
  }

  /**
   * Show settings panel
   */
  show() {
    if (!this.container) return;
    this.container.style.display = 'block';
    this.isVisible = true;
    this.loadUIValues();
  }

  /**
   * Hide settings panel
   */
  hide() {
    if (!this.container) return;
    this.container.style.display = 'none';
    this.isVisible = false;
  }

  /**
   * Toggle settings visibility
   */
  toggle() {
    if (this.isVisible) {
      this.hide();
    } else {
      this.show();
    }
  }
}

/**
 * Initialize git sync system
 * Called on app startup
 */
export async function initializeGitSync() {
  try {
    const settings = new SettingsManager().loadSettings();

    // Only initialize if remote is configured
    if (settings.remoteUrl) {
      await GitSync.initGit();
      console.log('Git sync initialized');
    } else {
      console.log('Remote URL not configured, git sync skipped');
    }
  } catch (error) {
    console.error('Failed to initialize git sync:', error.message);
  }
}

/**
 * App initialization function
 * Call this when DOM is ready
 */
export async function initializeApp() {
  // Initialize settings UI
  const settingsUI = new SettingsUI('#settings-panel');

  // Initialize git sync
  await initializeGitSync();

  // Attach settings button to UI
  const settingsBtn = document.querySelector('[data-action="open-settings"]');
  if (settingsBtn) {
    settingsBtn.addEventListener('click', () => settingsUI.show());
  }

  return {
    settings: settingsUI.settingsManager,
    ui: settingsUI,
    sync: GitSync
  };
}

export { GitSync };
