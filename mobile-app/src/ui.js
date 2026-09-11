/* Main UI controller for Training Parser PWA */

import { getSharedTextFromUrl, shareResults, onSharedText } from './share.js';
import * as gitSync from './git-sync.js';

let worker = null;
let pendingRequests = {};
let requestId = 0;
let lastParseResult = null;
let pyodideReady = false;

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
  const { type, id, result, message } = event.data;

  if (type === 'loading') {
    setStatus(message, 'loading');
    return;
  }

  if (type === 'ready') {
    pyodideReady = true;
    setStatus('Ready', 'ready');
    document.getElementById('parse-btn').disabled = false;
    document.getElementById('workout-input').disabled = false;
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

// --- Status bar ---

function setStatus(text, state = 'idle') {
  const el = document.getElementById('status');
  el.textContent = text;
  el.className = `status status--${state}`;
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
  document.getElementById('parse-btn').disabled = true;

  try {
    const result = await callWorker('parse', { text });
    lastParseResult = result;
    renderParseResult(result);
    setStatus(result.is_valid ? 'Parsed successfully' : `Parsed with ${result.errors.length} error(s)`, result.is_valid ? 'ready' : 'error');
  } catch (e) {
    setStatus('Parse error: ' + e.message, 'error');
  } finally {
    document.getElementById('parse-btn').disabled = false;
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

  // Summary
  document.getElementById('summary-text').textContent =
    `${result.total_exercises} exercise(s), ${result.total_sets} set(s)`;

  // Exercises table
  const tbody = document.getElementById('exercises-body');
  tbody.innerHTML = '';
  for (const ex of result.exercises) {
    const tr = document.createElement('tr');
    const setsText = ex.sets.map(s => `${s.repetitions}×${s.weight.amount}${s.weight.unit}`).join(', ');
    tr.innerHTML = `<td>${ex.name}</td><td>${ex.sets.length}</td><td>${setsText}</td>`;
    tbody.appendChild(tr);
  }

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
  const list = document.getElementById('history-list');
  const files = await gitSync.listWorkouts();
  list.innerHTML = '';
  for (const f of files) {
    const li = document.createElement('li');
    li.textContent = f.replace('.json', '');
    li.addEventListener('click', () => loadHistoryEntry(f));
    list.appendChild(li);
  }
  document.getElementById('history-section').hidden = files.length === 0;
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
  const settings = gitSync.loadSettings();
  document.getElementById('settings-remote').value = settings.remoteUrl || '';
  document.getElementById('settings-username').value = settings.username || '';
  document.getElementById('settings-token').value = settings.token || '';
  document.getElementById('settings-author').value = settings.author || '';
  document.getElementById('settings-modal').hidden = false;
}

function saveSettingsFromForm() {
  gitSync.saveSettings({
    remoteUrl: document.getElementById('settings-remote').value.trim(),
    username: document.getElementById('settings-username').value.trim(),
    token: document.getElementById('settings-token').value.trim(),
    author: document.getElementById('settings-author').value.trim() || 'Training Parser',
  });
  document.getElementById('settings-modal').hidden = true;
  setStatus('Settings saved', 'ready');
}

// --- Init ---

export async function init() {
  // Service Worker
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('./sw.js').catch(console.error);
  }

  // Wire up buttons
  document.getElementById('parse-btn').addEventListener('click', parseWorkout);
  document.getElementById('save-btn').addEventListener('click', saveWorkout);
  document.getElementById('sync-btn').addEventListener('click', syncNow);
  document.getElementById('share-btn').addEventListener('click', shareCurrentResults);
  document.getElementById('settings-btn').addEventListener('click', openSettings);
  document.getElementById('settings-save-btn').addEventListener('click', saveSettingsFromForm);
  document.getElementById('settings-cancel-btn').addEventListener('click', () => {
    document.getElementById('settings-modal').hidden = true;
  });
  document.getElementById('time-input').addEventListener('change', () => {
    const t = parseFloat(document.getElementById('time-input').value) || 0;
    calculateStats(t);
  });

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

  // Pre-fetch history
  gitSync.initGit().then(refreshHistory).catch(() => {});

  // Online/offline status
  window.addEventListener('online', () => {
    setStatus('Back online — syncing...', 'loading');
    gitSync.push().then(r => setStatus(r.ok ? 'Synced' : 'Sync failed: ' + r.message, r.ok ? 'ready' : 'error'));
  });
  window.addEventListener('offline', () => setStatus('Offline', 'idle'));
}
