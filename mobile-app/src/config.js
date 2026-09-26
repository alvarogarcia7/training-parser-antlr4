/**
 * Configuration loader for PWA
 * Loads environment-based defaults and user overrides
 */

const CONFIG_KEYS = {
  // CORS Proxy
  CORS_PROXY_URL: 'cors_proxy_url',

  // Git Server Credentials
  GIT_URL: 'git_url',
  GIT_USER: 'git_user',
  GIT_TOKEN: 'git_token',
  GIT_AUTHOR: 'git_author',
};

export class Config {
  /**
   * Get a configuration value
   * Priority: localStorage > environment variable > default
   */
  static get(key, defaultValue = null) {
    // Check localStorage first (user override)
    const stored = localStorage.getItem(`config_${key}`);
    if (stored) {
      return stored;
    }
    return defaultValue;
  }

  /**
   * Set a configuration value in localStorage
   */
  static set(key, value) {
    if (value === null || value === undefined) {
      localStorage.removeItem(`config_${key}`);
    } else {
      localStorage.setItem(`config_${key}`, value);
    }
  }

  /**
   * Load environment variables from .env.local
   * Call this during app initialization to load development defaults
   *
   * In development, you can populate .env.local with credentials,
   * then call this to load them into the PWA.
   *
   * Note: .env files are not accessible to browser code directly.
   * Use the developer console to manually load:
   *
   * window.Config.loadEnvDefaults({
   *   git_url: 'https://github.com/you/repo.git',
   *   git_user: 'your_username',
   *   git_token: 'your_token'
   * })
   */
  static loadEnvDefaults(envVars) {
    for (const [key, value] of Object.entries(envVars)) {
      if (value) {
        console.log(`[Config] Loading ${key} from environment`);
        this.set(key, value);
      }
    }
  }

  /**
   * Get all git credentials for the settings modal
   */
  static getGitSettings() {
    return {
      remoteUrl: this.get(CONFIG_KEYS.GIT_URL, ''),
      username: this.get(CONFIG_KEYS.GIT_USER, ''),
      token: this.get(CONFIG_KEYS.GIT_TOKEN, ''),
      author: this.get(CONFIG_KEYS.GIT_AUTHOR, 'Training Parser'),
    };
  }

  /**
   * Set all git credentials
   */
  static setGitSettings(settings) {
    if (settings.remoteUrl) this.set(CONFIG_KEYS.GIT_URL, settings.remoteUrl);
    if (settings.username) this.set(CONFIG_KEYS.GIT_USER, settings.username);
    if (settings.token) this.set(CONFIG_KEYS.GIT_TOKEN, settings.token);
    if (settings.author) this.set(CONFIG_KEYS.GIT_AUTHOR, settings.author);
  }

  /**
   * Clear all stored configuration
   */
  static clear() {
    for (const key of Object.values(CONFIG_KEYS)) {
      localStorage.removeItem(`config_${key}`);
    }
  }

  /**
   * Export all configuration (for debugging)
   */
  static export() {
    const config = {};
    for (const [name, key] of Object.entries(CONFIG_KEYS)) {
      const value = this.get(key);
      if (value) {
        config[name] = value.startsWith('glpat') || value.startsWith('ghp')
          ? value.substring(0, 10) + '...'
          : value;
      }
    }
    return config;
  }
}

// Expose to window for developer console access
window.Config = Config;
window.CONFIG_KEYS = CONFIG_KEYS;
