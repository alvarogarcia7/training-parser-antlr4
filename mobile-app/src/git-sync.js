/* Git sync module using isomorphic-git + LightningFS */

// Loaded via CDN in index.html
// Expects: window.git (isomorphic-git), window.LightningFS

const GIT_DIR = '/workout-data';
const SETTINGS_KEY = 'git_settings';

let fs = null;
let gitReady = false;

export function loadSettings() {
  const raw = localStorage.getItem(SETTINGS_KEY);
  return raw ? JSON.parse(raw) : { remoteUrl: '', username: '', token: '', author: 'Training Parser' };
}

export function saveSettings(settings) {
  localStorage.setItem(SETTINGS_KEY, JSON.stringify(settings));
}

export async function initGit() {
  if (gitReady) return;

  fs = new LightningFS('workout-git');
  const pfs = fs.promises;

  try {
    await pfs.mkdir(GIT_DIR);
  } catch {}

  const isRepo = await git.resolveRef({ fs, dir: GIT_DIR, ref: 'HEAD' }).catch(() => null);

  if (!isRepo) {
    await git.init({ fs, dir: GIT_DIR });
  }

  gitReady = true;
}

export async function saveWorkout(dateStr, setcentricJson) {
  if (!gitReady) await initGit();
  const pfs = fs.promises;
  const filename = `${dateStr}.json`;
  const filepath = `${GIT_DIR}/${filename}`;

  await pfs.writeFile(filepath, JSON.stringify(setcentricJson, null, 2), 'utf8');

  const settings = loadSettings();
  await git.add({ fs, dir: GIT_DIR, filepath: filename });
  await git.commit({
    fs,
    dir: GIT_DIR,
    message: `Add workout ${dateStr}`,
    author: {
      name: settings.author || 'Training Parser',
      email: 'training@local',
    },
  });

  // Queue a background sync if supported
  if ('serviceWorker' in navigator && 'SyncManager' in window) {
    const reg = await navigator.serviceWorker.ready;
    await reg.sync.register('git-push').catch(() => {});
  }

  return filename;
}

export async function listWorkouts() {
  if (!gitReady) await initGit();
  const pfs = fs.promises;
  try {
    const files = await pfs.readdir(GIT_DIR);
    return files.filter(f => f.endsWith('.json')).sort().reverse();
  } catch {
    return [];
  }
}

export async function loadWorkout(filename) {
  if (!gitReady) await initGit();
  const pfs = fs.promises;
  const content = await pfs.readFile(`${GIT_DIR}/${filename}`, 'utf8');
  return JSON.parse(content);
}

export async function push() {
  if (!gitReady) return { ok: false, message: 'Git not ready' };
  const settings = loadSettings();
  if (!settings.remoteUrl) return { ok: false, message: 'No remote URL configured' };

  try {
    await git.addRemote({ fs, dir: GIT_DIR, remote: 'origin', url: settings.remoteUrl, force: true });
    await git.push({
      fs,
      http: window.GitHttp,
      dir: GIT_DIR,
      remote: 'origin',
      ref: 'main',
      corsProxy: 'https://cors.isomorphic-git.org',
      onAuth: () => ({ username: settings.username, password: settings.token }),
    });
    return { ok: true };
  } catch (e) {
    return { ok: false, message: e.message };
  }
}

export async function pull() {
  if (!gitReady) return { ok: false, message: 'Git not ready' };
  const settings = loadSettings();
  if (!settings.remoteUrl) return { ok: false, message: 'No remote URL configured' };

  try {
    await git.addRemote({ fs, dir: GIT_DIR, remote: 'origin', url: settings.remoteUrl, force: true });
    await git.pull({
      fs,
      http: window.GitHttp,
      dir: GIT_DIR,
      remote: 'origin',
      ref: 'main',
      corsProxy: 'https://cors.isomorphic-git.org',
      onAuth: () => ({ username: settings.username, password: settings.token }),
      author: {
        name: settings.author || 'Training Parser',
        email: 'training@local',
      },
    });
    return { ok: true };
  } catch (e) {
    return { ok: false, message: e.message };
  }
}
