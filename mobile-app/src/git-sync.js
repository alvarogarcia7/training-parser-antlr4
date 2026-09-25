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

async function detectRemoteDefaultBranch() {
  try {
    console.log('[git-sync:detect] Querying remote refs...');
    const refs = await git.listServerRefs({
      http: window.GitHttp,
      url: loadSettings().remoteUrl,
      corsProxy: 'https://cors.isomorphic-git.org',
    });

    console.log('[git-sync:detect] Remote refs:', refs.length, 'found');
    if (refs.length === 0) {
      console.log('[git-sync:detect] Remote repository is empty (no refs)');
      return null;
    }

    // Look for HEAD ref which points to default branch
    const headRef = refs.find(ref => ref.ref === 'HEAD');
    if (headRef && headRef.target) {
      const match = headRef.target.match(/refs\/heads\/(.+)$/);
      if (match) {
        console.log('[git-sync:detect] Remote default branch detected:', match[1]);
        return match[1];
      }
    }
    console.log('[git-sync:detect] HEAD ref found but no branch target');
  } catch (e) {
    console.log('[git-sync:detect] Could not detect remote default branch:', e.message);
  }
  return null;
}

export async function initGit() {
  console.log('[git-sync:init] Initializing git');
  if (gitReady) {
    console.log('[git-sync:init] Git already ready, skipping');
    return;
  }

  try {
    console.log('[git-sync:init] Creating LightningFS instance');
    fs = new LightningFS('workout-git');
    const pfs = fs.promises;

    console.log('[git-sync:init] Creating directory:', GIT_DIR);
    try {
      await pfs.mkdir(GIT_DIR);
      console.log('[git-sync:init] Directory created');
    } catch (e) {
      console.log('[git-sync:init] Directory already exists');
    }

    console.log('[git-sync:init] Checking if repository exists');
    const isRepo = await git.resolveRef({ fs, dir: GIT_DIR, ref: 'HEAD' }).catch(() => null);

    if (!isRepo) {
      console.log('[git-sync:init] No repository found, initializing');
      await git.init({ fs, dir: GIT_DIR });
      console.log('[git-sync:init] Repository initialized');

      // Ensure we're on a branch for the first commit
      try {
        await git.checkout({ fs, dir: GIT_DIR, ref: 'main', create: true });
        console.log('[git-sync:init] Created and checked out main branch');
      } catch (e) {
        console.log('[git-sync:init] Branch setup note:', e.message);
      }
    } else {
      console.log('[git-sync:init] Repository already exists');
    }

    gitReady = true;
    console.log('[git-sync:init] Git initialization complete');
  } catch (e) {
    console.error('[git-sync:init] Initialization failed:', e);
    throw e;
  }
}

export async function saveWorkout(dateStr, setcentricJson) {
  console.log('[git-sync] saveWorkout starting:', { dateStr });
  if (!gitReady) await initGit();
  const pfs = fs.promises;
  const filename = `${dateStr}.json`;
  const filepath = `${GIT_DIR}/${filename}`;

  try {
    console.log('[git-sync] Writing file:', filepath);
    await pfs.writeFile(filepath, JSON.stringify(setcentricJson, null, 2), 'utf8');
    console.log('[git-sync] File written successfully');

    const settings = loadSettings();
    console.log('[git-sync] Adding to git:', filename);
    await git.add({ fs, dir: GIT_DIR, filepath: filename });
    console.log('[git-sync] Committing...');
    await git.commit({
      fs,
      dir: GIT_DIR,
      message: `Add workout ${dateStr}`,
      author: {
        name: settings.author || 'Training Parser',
        email: 'training@local',
      },
    });
    console.log('[git-sync] Commit successful');

    // Queue a background sync if supported
    if ('serviceWorker' in navigator && 'SyncManager' in window) {
      const reg = await navigator.serviceWorker.ready;
      await reg.sync.register('git-push').catch((e) => {
        console.log('[git-sync] Background sync registration skipped:', e.message);
      });
    }

    return filename;
  } catch (e) {
    console.error('[git-sync] saveWorkout failed:', e);
    throw e;
  }
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
  console.log('[git-sync:push] Starting push operation');
  if (!gitReady) {
    console.warn('[git-sync:push] Git not ready');
    return { ok: false, message: 'Git not ready' };
  }

  const settings = loadSettings();
  if (!settings.remoteUrl) {
    console.warn('[git-sync:push] No remote URL configured');
    return { ok: false, message: 'No remote URL configured' };
  }

  console.log('[git-sync:push] Remote URL:', settings.remoteUrl.replace(/https?:\/\/.*@/, 'https://***@'));
  console.log('[git-sync:push] Username:', settings.username);

  try {
    console.log('[git-sync:push] Adding remote origin');
    await git.addRemote({ fs, dir: GIT_DIR, remote: 'origin', url: settings.remoteUrl, force: true });
    console.log('[git-sync:push] Remote added successfully');

    // Determine current/target branch
    let branch = 'main';

    // Try to detect remote default branch first
    const remoteBranch = await detectRemoteDefaultBranch();
    if (remoteBranch) {
      branch = remoteBranch;
      console.log('[git-sync:push] Using remote default branch:', branch);
    } else {
      // Fall back to local current branch
      try {
        const currentBranch = await git.currentBranch({ fs, dir: GIT_DIR, fullname: false });
        if (currentBranch) {
          branch = currentBranch;
          console.log('[git-sync:push] Current branch detected:', branch);
        } else {
          console.log('[git-sync:push] No current branch, using default: main');
        }
      } catch (e) {
        console.log('[git-sync:push] Could not detect branch, using default: main', e.message);
      }
    }

    // Try pushing to the current branch
    console.log('[git-sync:push] Attempting push to branch:', branch);
    try {
      console.log('[git-sync:push] First attempt: push as-is');
      await git.push({
        fs,
        http: window.GitHttp,
        dir: GIT_DIR,
        remote: 'origin',
        ref: branch,
        corsProxy: 'https://cors.isomorphic-git.org',
        onAuth: () => {
          console.log('[git-sync:push] Auth requested for user:', settings.username);
          return { username: settings.username, password: settings.token };
        },
      });
      console.log('[git-sync:push] Push successful on first attempt');
      return { ok: true };
    } catch (pushError) {
      const pushMsg = pushError.message || String(pushError);
      console.warn('[git-sync:push] First push attempt failed:', pushMsg);

      // If push failed, try with force create for new repositories
      if (pushMsg.includes('Could not find') || pushMsg.includes('not found') || pushMsg.includes('no matching')) {
        console.log('[git-sync:push] Branch not found, attempting with force: true');
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
          console.log('[git-sync:push] Push successful with force flag');
          return { ok: true };
        } catch (forceError) {
          const forceMsg = forceError.message || String(forceError);
          console.warn('[git-sync:push] Force push failed:', forceMsg);

          // Last resort: try pushing to alternate branch (main ↔ master)
          if ((forceMsg.includes('Could not find') || forceMsg.includes('not found') || forceMsg.includes('no matching'))) {
            const alternateBranch = branch === 'main' ? 'master' : 'main';
            console.log('[git-sync:push] Attempting fallback to', alternateBranch, 'branch');
            try {
              await git.push({
                fs,
                http: window.GitHttp,
                dir: GIT_DIR,
                remote: 'origin',
                ref: alternateBranch,
                force: true,
                corsProxy: 'https://cors.isomorphic-git.org',
                onAuth: () => ({ username: settings.username, password: settings.token }),
              });
              console.log('[git-sync:push] Push successful to', alternateBranch, 'branch');
              return { ok: true };
            } catch (altError) {
              const altMsg = altError.message || String(altError);
              console.error('[git-sync:push] All push attempts failed. Alternate error:', altMsg);
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
    console.error('[git-sync:push] Push operation failed:', msg);

    if (msg.includes('Could not find') || msg.includes('not found') || msg.includes('no matching')) {
      console.error('[git-sync:push] Diagnosis: Repository not initialized or empty');
      return {
        ok: false,
        message: 'Remote repository has no branches. On GitHub: Add a README file (or any file) to create an initial commit, then retry push.'
      };
    }
    if (msg.includes('authentication') || msg.includes('Unauthorized') || msg.includes('403')) {
      console.error('[git-sync:push] Diagnosis: Authentication error');
      return {
        ok: false,
        message: 'Authentication failed. Check your token and username.'
      };
    }
    if (msg.includes('CORS') || msg.includes('cors')) {
      console.error('[git-sync:push] Diagnosis: CORS error');
      return {
        ok: false,
        message: 'CORS error - try a different network or check repository URL.'
      };
    }
    console.error('[git-sync:push] Returning generic error:', msg);
    return { ok: false, message: msg };
  }
}

export async function pull() {
  console.log('[git-sync:pull] Starting pull operation');
  if (!gitReady) {
    console.warn('[git-sync:pull] Git not ready');
    return { ok: false, message: 'Git not ready' };
  }

  const settings = loadSettings();
  if (!settings.remoteUrl) {
    console.warn('[git-sync:pull] No remote URL configured');
    return { ok: false, message: 'No remote URL configured' };
  }

  console.log('[git-sync:pull] Remote URL:', settings.remoteUrl.replace(/https?:\/\/.*@/, 'https://***@'));
  console.log('[git-sync:pull] Username:', settings.username);

  try {
    console.log('[git-sync:pull] Adding remote origin');
    await git.addRemote({ fs, dir: GIT_DIR, remote: 'origin', url: settings.remoteUrl, force: true });
    console.log('[git-sync:pull] Remote added successfully');

    // Determine current/target branch
    let branch = 'main';

    // Try to detect remote default branch first
    const remoteBranch = await detectRemoteDefaultBranch();
    if (remoteBranch) {
      branch = remoteBranch;
      console.log('[git-sync:pull] Using remote default branch:', branch);
    } else {
      // Fall back to local current branch
      try {
        const currentBranch = await git.currentBranch({ fs, dir: GIT_DIR, fullname: false });
        if (currentBranch) {
          branch = currentBranch;
          console.log('[git-sync:pull] Current branch detected:', branch);
        } else {
          console.log('[git-sync:pull] No current branch, using default: main');
        }
      } catch (e) {
        console.log('[git-sync:pull] Could not detect branch, using default: main', e.message);
      }
    }

    // Try pulling from the current branch
    console.log('[git-sync:pull] Attempting pull from branch:', branch);
    try {
      console.log('[git-sync:pull] First attempt: pull as-is');
      await git.pull({
        fs,
        http: window.GitHttp,
        dir: GIT_DIR,
        remote: 'origin',
        ref: branch,
        corsProxy: 'https://cors.isomorphic-git.org',
        onAuth: () => {
          console.log('[git-sync:pull] Auth requested for user:', settings.username);
          return { username: settings.username, password: settings.token };
        },
        author: {
          name: settings.author || 'Training Parser',
          email: 'training@local',
        },
      });
      console.log('[git-sync:pull] Pull successful on first attempt');
      return { ok: true };
    } catch (pullError) {
      const pullMsg = pullError.message || String(pullError);
      console.warn('[git-sync:pull] First pull attempt failed:', pullMsg);

      // If pulling from current branch failed, try alternate branch (main ↔ master)
      if (pullMsg.includes('Could not find') || pullMsg.includes('not found') || pullMsg.includes('no matching')) {
        const alternateBranch = branch === 'main' ? 'master' : 'main';
        console.log('[git-sync:pull] Branch not found, attempting fallback to', alternateBranch);
        try {
          await git.pull({
            fs,
            http: window.GitHttp,
            dir: GIT_DIR,
            remote: 'origin',
            ref: alternateBranch,
            corsProxy: 'https://cors.isomorphic-git.org',
            onAuth: () => ({ username: settings.username, password: settings.token }),
            author: {
              name: settings.author || 'Training Parser',
              email: 'training@local',
            },
          });
          console.log('[git-sync:pull] Pull successful from', alternateBranch, 'branch');
          return { ok: true };
        } catch (altError) {
          const altMsg = altError.message || String(altError);
          console.error('[git-sync:pull] Pull from', alternateBranch, 'also failed:', altMsg);
          throw pullError;  // Return original error
        }
      } else {
        throw pullError;
      }
    }
  } catch (e) {
    const msg = e.message || String(e);
    console.error('[git-sync:pull] Pull operation failed:', msg);

    if (msg.includes('Could not find') || msg.includes('not found') || msg.includes('no matching')) {
      console.error('[git-sync:pull] Diagnosis: Repository empty or not initialized');
      return {
        ok: false,
        message: 'Nothing to pull. Repository is empty. Push workouts from another device first.'
      };
    }
    if (msg.includes('authentication') || msg.includes('Unauthorized') || msg.includes('403')) {
      console.error('[git-sync:pull] Diagnosis: Authentication error');
      return {
        ok: false,
        message: 'Authentication failed. Check your token and username.'
      };
    }
    if (msg.includes('CORS') || msg.includes('cors')) {
      console.error('[git-sync:pull] Diagnosis: CORS error');
      return {
        ok: false,
        message: 'CORS error - try a different network or check repository URL.'
      };
    }
    console.error('[git-sync:pull] Returning generic error:', msg);
    return { ok: false, message: msg };
  }
}
