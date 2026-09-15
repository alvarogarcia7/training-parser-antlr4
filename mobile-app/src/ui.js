/* Main UI controller for Training Parser PWA */

import { getSharedTextFromUrl, shareResults, onSharedText } from './share.js';
import * as gitSync from './git-sync.js';

let worker = null;
let pendingRequests = {};
let requestId = 0;
let lastParseResult = null;
let pyodideReady = false;
let logMessages = [];
let minLogLevel = 0; // DEBUG by default for troubleshooting (0=DEBUG, 1=INFO, 2=WARN, 3=ERROR)

// --- Unified Logger ---

class Logger {
  constructor() {
    this.levels = { DEBUG: 0, INFO: 1, WARN: 2, ERROR: 3 };
  }

  log(message, level = 'INFO', elapsed = 0) {
    const levelNum = this.levels[level] || 1;

    // Console logging with appropriate method
    const consoleMethod = level.toLowerCase();
    const consoleFunc = console[consoleMethod] || console.log;
    consoleFunc(`[${level}] ${message}${elapsed ? ` (${elapsed}ms)` : ''}`);

    // UI logging
    const now = new Date();
    const timestamp = `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}:${String(now.getSeconds()).padStart(2, '0')}`;
    logMessages.push({ message, level, elapsed, timestamp });
    renderLogs();
  }

  debug(msg, elapsed = 0) { this.log(msg, 'DEBUG', elapsed); }
  info(msg, elapsed = 0) { this.log(msg, 'INFO', elapsed); }
  warn(msg, elapsed = 0) { this.log(msg, 'WARN', elapsed); }
  error(msg, elapsed = 0) { this.log(msg, 'ERROR', elapsed); }
}

const logger = new Logger();

// --- localStorage persistence ---

const STORAGE_KEYS = {
  input: 'workout-input-text',
  date: 'workout-date',
  time: 'workout-time-minutes',
  parseResult: 'workout-parse-result',
};

function saveToStorage(key, value) {
  try {
    localStorage.setItem(key, JSON.stringify(value));
  } catch (e) {
    console.warn('[storage] Failed to save:', key, e);
  }
}

function loadFromStorage(key, defaultValue = null) {
  try {
    const value = localStorage.getItem(key);
    return value ? JSON.parse(value) : defaultValue;
  } catch (e) {
    console.warn('[storage] Failed to load:', key, e);
    return defaultValue;
  }
}

function restoreSessionData() {
  const inputText = loadFromStorage(STORAGE_KEYS.input);
  const dateValue = loadFromStorage(STORAGE_KEYS.date);
  const timeValue = loadFromStorage(STORAGE_KEYS.time);
  const savedResult = loadFromStorage(STORAGE_KEYS.parseResult);

  if (inputText) {
    document.getElementById('workout-input').value = inputText;
    console.log('[storage] Restored input text');
  }
  if (dateValue) {
    document.getElementById('workout-date').value = dateValue;
    console.log('[storage] Restored date');
  }
  if (timeValue) {
    document.getElementById('time-input').value = timeValue;
    console.log('[storage] Restored time');
  }
  if (savedResult) {
    lastParseResult = savedResult;
    renderParseResult(savedResult);
    calculateStats(timeValue || 0);
    console.log('[storage] Restored parse result');
  }
}

// --- Worker communication ---

function callWorker(type, data = {}) {
  return new Promise((resolve, reject) => {
    const id = ++requestId;
    pendingRequests[id] = { resolve, reject };
    worker.postMessage({ type, id, ...data });
    setTimeout(() => {
      if (pendingRequests[id]) {
        delete pendingRequests[id];
        reject(new Error('Worker timeout'));
      }
    }, 60000);
  });
}

function handleWorkerMessage(event) {
  const { type, id, result, message, level, elapsed } = event.data;

  if (type === 'log') {
    logger.log(message, level || 'INFO', elapsed || 0);
    return;
  }

  if (type === 'loading') {
    setStatus(message, 'loading');
    console.log('[loading] ' + message);
    return;
  }

  if (type === 'ready') {
    pyodideReady = true;
    setStatus('Ready', 'ready');
    console.log('[ready] Python runtime ready');
    return;
  }

  if (type === 'sync_requested') {
    gitSync.push().then(r => {
      if (r.ok) setStatus('Synced to remote', 'ready');
    });
    return;
  }

  const pending = pendingRequests[id];
  if (!pending) return;
  delete pendingRequests[id];

  if (type === 'error') {
    pending.reject(new Error(message));
  } else {
    pending.resolve(result);
  }
}

// --- Logging ---

function renderLogs() {
  const logsSection = document.getElementById('logs-section');
  const logsList = document.getElementById('logs-list');
  const levelNum = { DEBUG: 0, INFO: 1, WARN: 2, ERROR: 3 };

  const filtered = logMessages.filter(entry => {
    const entryLevel = levelNum[entry.level] || 1;
    return entryLevel >= minLogLevel;
  });

  logsList.innerHTML = filtered.map(entry => {
    const level = entry.level || 'INFO';
    return `<div class="log-entry ${level}"><span class="log-time">${entry.timestamp}</span><span class="log-badge">${level}</span> ${entry.message}</div>`;
  }).join('');

  logsSection.hidden = logMessages.length === 0;
  if (logMessages.length > 0) {
    logsList.parentElement.scrollTop = logsList.parentElement.scrollHeight;
  }
}

function setLogLevel(level) {
  minLogLevel = parseInt(level);
  renderLogs();
}

// --- Status bar ---

function setStatus(text, state = 'idle') {
  const el = document.getElementById('status');
  el.textContent = text;
  el.className = `status status--${state}`;
}

// --- Formatting ---

function formatVolume(volume) {
  return Math.round(volume).toLocaleString();
}

// --- Parse ---

async function parseWorkout() {
  const text = document.getElementById('workout-input').value.trim();
  if (!text) return;
  if (!pyodideReady) {
    setStatus('Python runtime still loading...', 'loading');
    return;
  }

  setStatus('Parsing...', 'loading');

  try {
    const result = await callWorker('parse', { text });
    lastParseResult = result;
    renderParseResult(result);
    saveToStorage(STORAGE_KEYS.parseResult, result);
    setStatus(result.is_valid ? 'Parsed successfully' : `Parsed with ${result.errors.length} error(s)`, result.is_valid ? 'ready' : 'error');
  } catch (e) {
    setStatus('Parse error: ' + e.message, 'error');
  }
}

function renderParseResult(result) {
  const section = document.getElementById('results-section');
  section.hidden = false;

  // Errors
  const errEl = document.getElementById('errors-list');
  errEl.innerHTML = '';
  for (const err of result.errors) {
    const li = document.createElement('li');
    li.textContent = `Line ${err.line}:${err.column} — ${err.message}`;
    errEl.appendChild(li);
  }
  document.getElementById('errors-section').hidden = result.errors.length === 0;

  // Calculate volumes
  let totalVolume = 0;
  let totalSets = 0;
  const exerciseVolumes = [];

  for (const ex of result.exercises) {
    let exVolume = 0;
    for (const s of ex.sets) {
      exVolume += s.weight.amount * s.repetitions;
      totalVolume += s.weight.amount * s.repetitions;
    }
    exerciseVolumes.push(exVolume);
    totalSets += ex.sets.length;
  }

  // Summary
  document.getElementById('summary-text').textContent =
    `${result.total_exercises} exercise(s), ${totalSets} set(s), ${formatVolume(totalVolume)} kg total`;

  // Exercises table
  const tbody = document.getElementById('exercises-body');
  tbody.innerHTML = '';
  for (let i = 0; i < result.exercises.length; i++) {
    const ex = result.exercises[i];
    const tr = document.createElement('tr');
    const setsText = ex.sets.map(s => `${s.repetitions}×${s.weight.amount}${s.weight.unit}`).join(', ');
    const volumeText = formatVolume(exerciseVolumes[i]);
    tr.innerHTML = `<td>${ex.name}</td><td>${ex.sets.length}</td><td>${volumeText} kg</td><td>${setsText}</td>`;
    tbody.appendChild(tr);
  }

  // Footer row with totals
  const tfoot = document.getElementById('exercises-footer');
  tfoot.innerHTML = '';
  const footerRow = document.createElement('tr');
  footerRow.style.borderTop = '2px solid var(--surface2)';
  footerRow.style.fontWeight = '600';
  footerRow.innerHTML = `<td colspan="1"><strong>Total</strong></td><td>${totalSets}</td><td>${formatVolume(totalVolume)} kg</td><td></td>`;
  tfoot.appendChild(footerRow);

  // Auto-calculate stats with 0 time
  calculateStats(0);
}

// --- Statistics ---

async function calculateStats(timeMinutes) {
  if (!lastParseResult || !pyodideReady) return;

  const exercisesJson = JSON.stringify(lastParseResult.exercises);
  try {
    const stats = await callWorker('stats', { exercisesJson, timeMinutes });
    renderStats(stats, timeMinutes);
  } catch (e) {
    console.error('Stats error:', e);
  }
}

function renderStats(stats, timeMinutes) {
  const el = document.getElementById('stats-section');
  el.hidden = false;

  const fmt = (n, d = 2) => typeof n === 'number' ? n.toFixed(d) : n;

  document.getElementById('stats-totals').innerHTML = `
    <tr><td>Exercises</td><td>${stats.totals.exercises}</td></tr>
    <tr><td>Sets</td><td>${stats.totals.sets}</td></tr>
    <tr><td>Total weight</td><td>${fmt(stats.totals.weight_kg)} kg</td></tr>
  `;

  const ratesEl = document.getElementById('stats-rates');
  if (timeMinutes > 0) {
    ratesEl.closest('section').hidden = false;
    ratesEl.innerHTML = `
      <tr><td>Exercises/h</td><td>${fmt(stats.rates.exercises_per_hour)}</td></tr>
      <tr><td>Sets/h</td><td>${fmt(stats.rates.sets_per_hour)}</td></tr>
      <tr><td>Weight/h</td><td>${fmt(stats.rates.weight_per_hour_kg)} kg</td></tr>
    `;
  } else {
    ratesEl.closest('section').hidden = true;
  }

  document.getElementById('stats-averages').innerHTML = `
    <tr><td>Weight/set</td><td>${fmt(stats.averages.weight_per_set_kg)} kg</td></tr>
    <tr><td>Sets/exercise</td><td>${fmt(stats.averages.sets_per_exercise)}</td></tr>
  `;
}

// --- Save & sync ---

async function saveWorkout() {
  if (!lastParseResult || !lastParseResult.is_valid) return;

  const settings = gitSync.loadSettings();
  if (!settings.remoteUrl) {
    setStatus('Git not configured — offline mode only', 'idle');
    return;
  }

  const dateStr = document.getElementById('workout-date').value || new Date().toISOString().split('T')[0];

  try {
    setStatus('Saving...', 'loading');
    const serialized = await callWorker('serialize', {
      exercisesJson: JSON.stringify(lastParseResult.exercises),
      dateStr,
    });
    await gitSync.initGit();
    await gitSync.saveWorkout(dateStr, serialized);
    setStatus('Saved locally (will sync when online)', 'ready');
    refreshHistory();
  } catch (e) {
    setStatus('Save error: ' + e.message, 'error');
  }
}

async function syncNow() {
  const settings = gitSync.loadSettings();
  if (!settings.remoteUrl) {
    setStatus('Git not configured', 'error');
    return;
  }

  setStatus('Pushing to remote...', 'loading');
  const result = await gitSync.push();
  if (result.ok) {
    setStatus('Synced to remote', 'ready');
  } else {
    setStatus('Sync failed: ' + result.message, 'error');
  }
}

// --- History ---

async function refreshHistory() {
  const settings = gitSync.loadSettings();
  const historySection = document.getElementById('history-section');

  if (!settings.remoteUrl) {
    historySection.hidden = true;
    return;
  }

  const list = document.getElementById('history-list');
  const files = await gitSync.listWorkouts();
  list.innerHTML = '';
  for (const f of files) {
    const li = document.createElement('li');
    li.textContent = f.replace('.json', '');
    li.addEventListener('click', () => loadHistoryEntry(f));
    list.appendChild(li);
  }
  historySection.hidden = files.length === 0;
}

async function loadHistoryEntry(filename) {
  const data = await gitSync.loadWorkout(filename);
  document.getElementById('workout-input').value = `# Loaded: ${filename}\n# (view-only)`;
  lastParseResult = {
    exercises: data.exercises || [],
    errors: [],
    is_valid: true,
    total_exercises: (data.exercises || []).length,
    total_sets: (data.exercises || []).reduce((a, ex) => a + (ex.sets || []).length, 0),
  };
  renderParseResult(lastParseResult);
}

// --- Share ---

async function shareCurrentResults() {
  if (!lastParseResult) return;
  const time = parseFloat(document.getElementById('time-input').value) || 0;

  let statsText = '';
  if (pyodideReady) {
    try {
      statsText = await callWorker('format_stats', {
        exercisesJson: JSON.stringify(lastParseResult.exercises),
        timeMinutes: time,
      });
    } catch {}
  }

  const jsonBlob = new Blob(
    [JSON.stringify(lastParseResult, null, 2)],
    { type: 'application/json' }
  );

  await shareResults({
    title: 'Workout Results',
    statsText,
    jsonBlob,
    filename: 'workout.json',
  });
}

// --- Settings modal ---

function openSettings() {
  console.log('[openSettings] Opening settings modal...');
  const settings = gitSync.loadSettings();
  document.getElementById('settings-remote').value = settings.remoteUrl || '';
  document.getElementById('settings-username').value = settings.username || '';
  document.getElementById('settings-token').value = settings.token || '';
  document.getElementById('settings-author').value = settings.author || '';
  const modal = document.getElementById('settings-modal');
  modal.hidden = false;
  console.log('[openSettings] Modal opened:', { hidden: modal.hidden, display: modal.style.display });
}

function closeModal() {
  const modal = document.getElementById('settings-modal');
  console.log('[closeModal] Before:', { hidden: modal?.hidden, display: modal?.style.display });
  if (modal) {
    modal.hidden = true;
    console.log('[closeModal] After:', { hidden: modal.hidden, display: modal.style.display });
  } else {
    console.warn('[closeModal] Modal element not found');
  }
}

function saveSettingsFromForm() {
  console.log('[saveSettingsFromForm] Saving settings...');
  gitSync.saveSettings({
    remoteUrl: document.getElementById('settings-remote').value.trim(),
    username: document.getElementById('settings-username').value.trim(),
    token: document.getElementById('settings-token').value.trim(),
    author: document.getElementById('settings-author').value.trim() || 'Training Parser',
  });
  console.log('[saveSettingsFromForm] Calling closeModal...');
  closeModal();
  setStatus('Settings saved', 'ready');
}

// --- Init ---

export async function init() {
  // Service Worker (use ../sw.js because this module is in /mobile-app/src/)
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('../sw.js', { scope: '/mobile-app/' }).catch(e => {
      logger.error('Service Worker registration failed: ' + e.message);
    });
  }

  // Wire up buttons
  document.getElementById('parse-btn').addEventListener('click', parseWorkout);
  document.getElementById('save-btn').addEventListener('click', saveWorkout);
  document.getElementById('sync-btn').addEventListener('click', syncNow);
  document.getElementById('share-btn').addEventListener('click', shareCurrentResults);
  console.log('[init] Setting up event listeners...');
  document.getElementById('settings-btn').addEventListener('click', () => {
    console.log('[event] Settings button clicked');
    openSettings();
  });
  document.getElementById('settings-save-btn').addEventListener('click', () => {
    console.log('[event] Save button clicked');
    saveSettingsFromForm();
  });
  document.getElementById('settings-cancel-btn').addEventListener('click', () => {
    console.log('[event] Cancel button clicked');
    closeModal();
  });

  // Close modal when clicking backdrop (not on the modal content)
  const modalBackdrop = document.getElementById('settings-modal');
  modalBackdrop.addEventListener('click', (e) => {
    console.log('[event] Modal click:', { currentTarget: e.currentTarget.id, target: e.target.id });
    if (e.currentTarget === e.target) {
      console.log('[event] Backdrop detected (click outside modal), closing');
      closeModal();
    }
  });
  console.log('[init] Event listeners setup complete');

  // Save input text on change
  document.getElementById('workout-input').addEventListener('change', () => {
    const text = document.getElementById('workout-input').value;
    saveToStorage(STORAGE_KEYS.input, text);
  });

  // Save date on change
  document.getElementById('workout-date').addEventListener('change', () => {
    const date = document.getElementById('workout-date').value;
    saveToStorage(STORAGE_KEYS.date, date);
  });

  // Save time and recalculate stats
  document.getElementById('time-input').addEventListener('change', () => {
    const t = parseFloat(document.getElementById('time-input').value) || 0;
    saveToStorage(STORAGE_KEYS.time, t);
    calculateStats(t);
  });

  // Log level filter
  document.getElementById('log-level-filter').addEventListener('change', (e) => {
    setLogLevel(parseInt(e.target.value));
  });

  // Restore previous session data
  restoreSessionData();

  // Handle shared text from URL (iOS Shortcuts) or SW message (Android)
  const sharedText = getSharedTextFromUrl();
  if (sharedText) {
    document.getElementById('workout-input').value = sharedText;
  }
  onSharedText((text) => {
    document.getElementById('workout-input').value = text;
    if (pyodideReady) parseWorkout();
  });

  // Start Pyodide worker
  worker = new Worker('./src/pyodide-worker.js');
  worker.addEventListener('message', handleWorkerMessage);
  worker.addEventListener('error', (e) => setStatus('Worker error: ' + e.message, 'error'));

  setStatus('Loading Python runtime...', 'loading');

  // Set a timeout for initialization (45 seconds max)
  setTimeout(() => {
    if (!pyodideReady) {
      logger.error('Initialization timeout - Pyodide took too long to load (>45s)');
      setStatus('Timeout: Python runtime took >45s - check network and browser console', 'error');
    }
  }, 45000);

  // Show/hide sync features based on git config
  const settings = gitSync.loadSettings();
  const hasSyncConfig = !!settings.remoteUrl;
  document.getElementById('save-btn').hidden = !hasSyncConfig;
  document.getElementById('sync-btn').hidden = !hasSyncConfig;

  // Pre-fetch history if git is configured
  if (hasSyncConfig) {
    gitSync.initGit().then(refreshHistory).catch(() => {});

    // Online/offline status
    window.addEventListener('online', () => {
      setStatus('Back online — syncing...', 'loading');
      gitSync.push().then(r => setStatus(r.ok ? 'Synced' : 'Sync failed: ' + r.message, r.ok ? 'ready' : 'error'));
    });
    window.addEventListener('offline', () => setStatus('Offline', 'idle'));
  }
}
