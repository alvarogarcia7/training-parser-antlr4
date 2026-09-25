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

    // Determine current/target branch
    let branch = 'main';
    try {
      const currentBranch = await git.currentBranch({ fs, dir: GIT_DIR, fullname: false });
      if (currentBranch) branch = currentBranch;
    } catch {}

    // Try pushing to the current branch
    // First attempt: push as-is (branch might exist on remote)
    try {
      await git.push({
        fs,
        http: window.GitHttp,
        dir: GIT_DIR,
        remote: 'origin',
        ref: branch,
        corsProxy: 'https://cors.isomorphic-git.org',
        onAuth: () => ({ username: settings.username, password: settings.token }),
      });
      return { ok: true };
    } catch (pushError) {
      // If push failed, try with force create for new repositories
      const pushMsg = pushError.message || String(pushError);

      // Try with force create (creates branch if it doesn't exist)
      if (pushMsg.includes('Could not find') || pushMsg.includes('not found') || pushMsg.includes('no matching')) {
        try {
          await git.push({
            fs,
            http: window.GitHttp,
            dir: GIT_DIR,
            remote: 'origin',
            ref: branch,
            force: true,
            corsProxy: 'https://cors.isomorphic-git.org',
            onAuth: () => ({ username: settings.username, password: settings.token }),
          });
          return { ok: true };
        } catch (forceError) {
          // Last resort: try pushing to master if main failed
          if (branch === 'main') {
            try {
              await git.push({
                fs,
                http: window.GitHttp,
                dir: GIT_DIR,
                remote: 'origin',
                ref: 'master',
                force: true,
                corsProxy: 'https://cors.isomorphic-git.org',
                onAuth: () => ({ username: settings.username, password: settings.token }),
              });
              return { ok: true };
            } catch (masterError) {
              // All attempts failed
              throw forceError;
            }
          } else {
            throw forceError;
          }
        }
      } else {
        throw pushError;
      }
    }
  } catch (e) {
    const msg = e.message || String(e);
    if (msg.includes('Could not find') || msg.includes('not found') || msg.includes('no matching')) {
      return {
        ok: false,
        message: 'Repository not initialized. Create it on GitHub with a README, then try again.'
      };
    }
    if (msg.includes('authentication') || msg.includes('Unauthorized') || msg.includes('403')) {
      return {
        ok: false,
        message: 'Authentication failed. Check your token and username.'
      };
    }
    return { ok: false, message: msg };
  }
}

export async function pull() {
  if (!gitReady) return { ok: false, message: 'Git not ready' };
  const settings = loadSettings();
  if (!settings.remoteUrl) return { ok: false, message: 'No remote URL configured' };

  try {
    await git.addRemote({ fs, dir: GIT_DIR, remote: 'origin', url: settings.remoteUrl, force: true });

    // Determine current/target branch
    let branch = 'main';
    try {
      const currentBranch = await git.currentBranch({ fs, dir: GIT_DIR, fullname: false });
      if (currentBranch) branch = currentBranch;
    } catch {}

    // Try pulling from the current branch
    try {
      await git.pull({
        fs,
        http: window.GitHttp,
        dir: GIT_DIR,
        remote: 'origin',
        ref: branch,
        corsProxy: 'https://cors.isomorphic-git.org',
        onAuth: () => ({ username: settings.username, password: settings.token }),
        author: {
          name: settings.author || 'Training Parser',
          email: 'training@local',
        },
      });
      return { ok: true };
    } catch (pullError) {
      // If pulling from main failed, try master
      const pullMsg = pullError.message || String(pullError);

      if ((pullMsg.includes('Could not find') || pullMsg.includes('not found') || pullMsg.includes('no matching')) && branch === 'main') {
        try {
          await git.pull({
            fs,
            http: window.GitHttp,
            dir: GIT_DIR,
            remote: 'origin',
            ref: 'master',
            corsProxy: 'https://cors.isomorphic-git.org',
            onAuth: () => ({ username: settings.username, password: settings.token }),
            author: {
              name: settings.author || 'Training Parser',
              email: 'training@local',
            },
          });
          return { ok: true };
        } catch (masterError) {
          throw pullError;  // Return original error
        }
      } else {
        throw pullError;
      }
    }
  } catch (e) {
    const msg = e.message || String(e);
    if (msg.includes('Could not find') || msg.includes('not found') || msg.includes('no matching')) {
      return {
        ok: false,
        message: 'Nothing to pull. Repository is empty. Push workouts from another device first.'
      };
    }
    if (msg.includes('authentication') || msg.includes('Unauthorized') || msg.includes('403')) {
      return {
        ok: false,
        message: 'Authentication failed. Check your token and username.'
      };
    }
    return { ok: false, message: msg };
  }
}
