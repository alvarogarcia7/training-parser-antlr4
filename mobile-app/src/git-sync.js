/* Git sync module using isomorphic-git + LightningFS */

// Loaded via CDN in index.html
// Expects: window.git (isomorphic-git), window.LightningFS

const GIT_DIR = '/workout-data';
const SETTINGS_KEY = 'git_settings';

let fs = null;
let gitReady = false;

// Detect development environment and use local CORS proxy if available
function getCorsProxy() {
  // Check for override in localStorage (set by admin/developer)
  const overrideProxy = localStorage.getItem('cors_proxy_url');
  if (overrideProxy) {
    console.log('[git-sync] Using override CORS proxy:', overrideProxy);
    return overrideProxy;
  }

  if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    // Development: Use local cors-anywhere on port 8081
    console.log('[git-sync] Using local CORS proxy: http://localhost:8081');
    return 'http://localhost:8081';
  }
  // Production: Use public CORS proxy
  console.log('[git-sync] Using public CORS proxy: https://cors.isomorphic-git.org');
  return 'https://cors.isomorphic-git.org';
}

export function loadSettings() {
  const raw = localStorage.getItem(SETTINGS_KEY);
  return raw ? JSON.parse(raw) : { remoteUrl: '', username: '', token: '', author: 'Training Parser' };
}

export function saveSettings(settings) {
  localStorage.setItem(SETTINGS_KEY, JSON.stringify(settings));
}

export async function testConnection() {
  console.log('[git-sync:test] Testing connection to remote repository');
  let settings = loadSettings();

  // For development: auto-populate local test server if running on localhost
  if (!settings.remoteUrl && (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1')) {
    console.log('[git-sync:test] Using local test server: http://localhost:8888/test-repo.git');
    settings = {
      remoteUrl: 'http://localhost:8888/test-repo.git',
      username: 'test',
      token: 'test',
      author: 'Training Parser'
    };
  }

  if (!settings.remoteUrl) {
    console.warn('[git-sync:test] No remote URL configured');
    return { ok: false, message: 'Remote URL not configured' };
  }

  if (!settings.username || !settings.token) {
    console.warn('[git-sync:test] Credentials not configured');
    return { ok: false, message: 'Username or token not configured' };
  }

  try {
    console.log('[git-sync:test] Remote URL:', settings.remoteUrl.replace(/https?:\/\/.*@/, 'https://***@'));
    console.log('[git-sync:test] Username:', settings.username);

    let branches = [];
    let usedDirect = false;
    let useProxyFirst = settings.remoteUrl.includes('github.com');

    // Method 1: Try direct access first (no proxy - works for private instances)
    if (useProxyFirst) {
      console.log('[git-sync:test] GitHub detected - using CORS proxy directly');
    } else {
      console.log('[git-sync:test] Attempting direct connection...');
    }

    if (!useProxyFirst) {
      try {
        const refs = await git.listServerRefs({
          http: window.GitHttp,
          url: settings.remoteUrl,
          onAuth: () => {
            console.log('[git-sync:test] Auth requested (direct, no proxy) for user:', settings.username);
            return { username: settings.username, password: settings.token };
          },
        });

      console.log('[git-sync:test] Direct listServerRefs returned');
      console.log('[git-sync:test] Response type:', typeof refs);
      console.log('[git-sync:test] Is array?', Array.isArray(refs));
      console.log('[git-sync:test] Response keys:', refs ? Object.keys(refs).slice(0, 5) : 'null');
      console.log('[git-sync:test] Full response:', JSON.stringify(refs).substring(0, 200));

      usedDirect = true;

      // Handle both array and object returns
      if (Array.isArray(refs)) {
        console.log('[git-sync:test] Processing as array');
        branches = refs.filter(ref => ref && ref.ref && ref.ref.startsWith('refs/heads/')).map(ref => ref.ref.replace('refs/heads/', ''));
      } else if (refs && typeof refs === 'object') {
        console.log('[git-sync:test] Processing as object');
        try {
          const refsKeys = Object.keys(refs || {});
          console.log('[git-sync:test] Object keys count:', refsKeys.length);
          branches = refsKeys.filter(ref => ref.startsWith('refs/heads/')).map(ref => ref.replace('refs/heads/', ''));
        } catch (keyError) {
          console.log('[git-sync:test] Error processing object keys:', keyError.message);
          branches = [];
        }
      } else {
        console.log('[git-sync:test] Response is neither array nor object');
        branches = [];
      }

        console.log('[git-sync:test] Successfully connected (direct). Branches found:', branches.length);
      } catch (directError) {
        console.log('[git-sync:test] Direct access failed:', directError.message);
        console.log('[git-sync:test] Error details:', directError);
        useProxyFirst = true;
      }
    }

    // Method 2: Use CORS proxy if direct failed or GitHub detected
    if (useProxyFirst || branches.length === 0) {
      console.log('[git-sync:test] Using CORS proxy...');
      try {
        const refs = await git.listServerRefs({
          http: window.GitHttp,
          url: settings.remoteUrl,
          corsProxy: getCorsProxy(),
          onAuth: () => {
            console.log('[git-sync:test] Auth requested (via proxy) for user:', settings.username);
            return { username: settings.username, password: settings.token };
          },
        });

        console.log('[git-sync:test] CORS proxy listServerRefs returned');
        console.log('[git-sync:test] Response type:', typeof refs);
        console.log('[git-sync:test] Is array?', Array.isArray(refs));

        if (Array.isArray(refs)) {
          console.log('[git-sync:test] Processing proxy response as array');
          branches = refs.filter(ref => ref && ref.ref && ref.ref.startsWith('refs/heads/')).map(ref => ref.ref.replace('refs/heads/', ''));
        } else if (refs && typeof refs === 'object') {
          console.log('[git-sync:test] Processing proxy response as object');
          try {
            const refsKeys = Object.keys(refs || {});
            branches = refsKeys.filter(ref => ref.startsWith('refs/heads/')).map(ref => ref.replace('refs/heads/', ''));
          } catch (keyError) {
            console.log('[git-sync:test] Error processing proxy response:', keyError.message);
            branches = [];
          }
        }

        console.log('[git-sync:test] Successfully connected (via proxy). Branches found:', branches.length);
      } catch (proxyError) {
        console.log('[git-sync:test] CORS proxy also failed:', proxyError.message);
        console.log('[git-sync:test] Proxy error details:', proxyError);

        // Method 3: Try getRemoteInfo
        try {
          console.log('[git-sync:test] Trying getRemoteInfo fallback...');
          const info = await git.getRemoteInfo({
            http: window.GitHttp,
            url: settings.remoteUrl,
            onAuth: () => ({ username: settings.username, password: settings.token }),
          });
          console.log('[git-sync:test] getRemoteInfo succeeded');
          console.log('[git-sync:test] Info type:', typeof info);
          console.log('[git-sync:test] Info keys:', info ? Object.keys(info).slice(0, 5) : 'null');

          if (info && info.refs) {
            console.log('[git-sync:test] Found refs in info');
            branches = Object.keys(info.refs).filter(ref => ref.startsWith('refs/heads/')).map(ref => ref.replace('refs/heads/', ''));
          } else {
            console.log('[git-sync:test] No refs found in info');
            branches = [];
          }
        } catch (infoError) {
          const msg = infoError.message || String(infoError);
          console.error('[git-sync:test] All methods failed');
          console.error('[git-sync:test] Final error:', infoError);
          if (msg.includes('Unauthorized') || msg.includes('403') || msg.includes('authentication')) {
            throw new Error('Authentication failed: ' + msg);
          }
          throw infoError;
        }
      }
    }

    if (branches.length === 0) {
      console.log('[git-sync:test] Connected but repository is empty (no branches yet)');
      return {
        ok: true,
        message: usedDirect
          ? '✅ Connected directly! Repository is empty. Add a README to initialize it.'
          : '✅ Connected via CORS proxy! Repository is empty. Add a README to initialize it.'
      };
    }

    console.log('[git-sync:test] Available branches:', branches);
    return {
      ok: true,
      message: `✅ Connected! Found ${branches.length} branch(es): ${branches.join(', ')} (${usedDirect ? 'direct' : 'via proxy'})`
    };
  } catch (e) {
    const msg = e.message || String(e);
    console.error('[git-sync:test] Connection failed:', msg);

    if (msg.includes('authentication') || msg.includes('Unauthorized') || msg.includes('403') || msg.includes('Authentication failed')) {
      console.error('[git-sync:test] Diagnosis: Authentication error');
      return {
        ok: false,
        message: '❌ Authentication failed. Check username and token.'
      };
    }
    if (msg.includes('not found') || msg.includes('404') || msg.includes('no such file')) {
      console.error('[git-sync:test] Diagnosis: Repository not found');
      return {
        ok: false,
        message: '❌ Repository not found. Check the URL.'
      };
    }
    if (msg.includes('CORS') || msg.includes('cors') || msg.includes('Access-Control-Allow-Origin')) {
      console.error('[git-sync:test] Diagnosis: CORS error - server does not allow cross-origin requests');
      return {
        ok: false,
        message: '❌ CORS blocked. Private git servers require:\n1) Deploy PWA on same domain, or\n2) Use a local CORS proxy, or\n3) Configure server CORS headers'
      };
    }
    console.error('[git-sync:test] Returning generic error:', msg);
    return { ok: false, message: '❌ Connection failed: ' + msg };
  }
}

async function detectRemoteDefaultBranch() {
  try {
    console.log('[git-sync:detect] Querying remote refs...');
    const refs = await git.listServerRefs({
      http: window.GitHttp,
      url: loadSettings().remoteUrl,
      corsProxy: getCorsProxy(),
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

async function verifyPushSuccess(branch, remoteUrl, corsProxy, settings) {
  // Verify that the push actually succeeded by checking remote commits
  console.log('[git-sync:verify] ========== VERIFICATION START ==========');
  console.log('[git-sync:verify] Checking if branch exists on remote:', branch);
  console.log('[git-sync:verify] Remote URL:', remoteUrl.replace(/https?:\/\/.*@/, 'https://***@'));
  console.log('[git-sync:verify] CORS proxy:', corsProxy.substring(0, 30) + '...');

  try {
    console.log('[git-sync:verify] Calling git.listServerRefs...');
    const remoteRefs = await git.listServerRefs({
      http: window.GitHttp,
      url: remoteUrl,
      corsProxy: corsProxy,
      onAuth: () => {
        console.log('[git-sync:verify] Auth callback invoked');
        return {
          username: settings.username,
          password: settings.token,
        };
      },
    });

    console.log('[git-sync:verify] ✓ git.listServerRefs() succeeded');
    console.log('[git-sync:verify] Remote refs count:', remoteRefs ? Object.keys(remoteRefs).length : 0);

    if (!remoteRefs || Object.keys(remoteRefs).length === 0) {
      console.warn('[git-sync:verify] ❌ No remote refs found');
      return false;
    }

    const allBranches = Object.keys(remoteRefs).filter(r => r.startsWith('refs/heads/'));
    console.log('[git-sync:verify] Branches on remote:', allBranches);

    const expectedRef = `refs/heads/${branch}`;
    if (remoteRefs[expectedRef]) {
      console.log('[git-sync:verify] ✓ Branch found:', branch);
      return true;
    } else {
      console.warn('[git-sync:verify] ❌ Branch not found:', branch);
      return false;
    }
  } catch (e) {
    console.error('[git-sync:verify] ❌ Verification error:', e.message);
    console.error('[git-sync:verify] Error details:', e);
    return false;
  }
}

function buildUrlWithEmbeddedAuth(url, username, token, corsProxy) {
  // For local CORS proxy, rely on Authorization headers (onAuth callback)
  if (corsProxy && corsProxy.includes('localhost')) {
    return url;
  }

  // For public CORS proxy, embed credentials in URL since it doesn't forward Authorization headers properly
  if (corsProxy && corsProxy.includes('cors.isomorphic-git.org')) {
    try {
      const parsed = new URL(url);
      if (username && token) {
        parsed.username = username;
        parsed.password = token;
      }
      return parsed.toString();
    } catch (e) {
      console.log('[git-sync] Could not parse URL for credential embedding:', e.message);
      return url;
    }
  }

  return url;
}

async function ensureInitializedBranch(branch = 'main') {
  console.log('[git-sync] Ensuring branch initialized:', branch);
  try {
    // Check if we have any commits
    const log = await git.log({ fs, dir: GIT_DIR, ref: branch });
    if (log && log.length > 0) {
      console.log('[git-sync] Branch has commits, not initializing');
      return true;
    }
  } catch (e) {
    console.log('[git-sync] Could not read branch log, will initialize:', e.message);
  }

  // Try to check out the branch, if it doesn't exist, create it
  try {
    await git.checkout({ fs, dir: GIT_DIR, ref: branch, force: true });
    console.log('[git-sync] Checked out branch:', branch);
  } catch (e) {
    console.log('[git-sync] Could not checkout branch, creating:', e.message);
    try {
      await git.checkout({ fs, dir: GIT_DIR, ref: branch, create: true });
      console.log('[git-sync] Created new branch:', branch);
    } catch (e2) {
      console.log('[git-sync] Could not create branch:', e2.message);
      return false;
    }
  }

  // Create initial empty commit if no commits exist
  try {
    const log = await git.log({ fs, dir: GIT_DIR, ref: branch });
    if (!log || log.length === 0) {
      console.log('[git-sync] No commits found, creating initial commit');
      await git.commit({
        fs,
        dir: GIT_DIR,
        message: 'Initial commit from Training Parser PWA',
        author: {
          name: 'Training Parser',
          email: 'training@local',
        },
      });
      console.log('[git-sync] Initial commit created');
    }
  } catch (e) {
    console.log('[git-sync] Could not create initial commit:', e.message);
    return false;
  }

  return true;
}

export async function push() {
  console.log('[git-sync:push] ========== PUSH OPERATION START ==========');
  console.log('[git-sync:push] Timestamp:', new Date().toISOString());

  if (!gitReady) {
    console.warn('[git-sync:push] Git not ready');
    return { ok: false, message: 'Git not ready' };
  }

  const settings = loadSettings();
  console.log('[git-sync:push] Settings loaded:', {
    hasRemoteUrl: !!settings.remoteUrl,
    hasUsername: !!settings.username,
    hasToken: !!settings.token,
    author: settings.author,
  });

  if (!settings.remoteUrl) {
    console.warn('[git-sync:push] No remote URL configured');
    return { ok: false, message: 'No remote URL configured' };
  }

  console.log('[git-sync:push] Remote URL:', settings.remoteUrl.replace(/https?:\/\/.*@/, 'https://***@'));
  console.log('[git-sync:push] Username:', settings.username);
  console.log('[git-sync:push] Token provided:', !!settings.token, '(length:', settings.token?.length || 0, ')');

  // Log local commits before push
  try {
    const localLog = await git.log({ fs, dir: GIT_DIR, depth: 10 });
    console.log('[git-sync:push] Local commits (latest 10):', localLog.length, 'commits');
    if (localLog.length > 0) {
      localLog.slice(0, 3).forEach((commit, idx) => {
        console.log(`  [${idx}] ${commit.oid.substring(0, 7)} - ${commit.commit.message}`);
      });
    }
  } catch (e) {
    console.warn('[git-sync:push] Could not read local log:', e.message);
  }

  try {
    // For public CORS proxy, embed credentials in URL since it doesn't forward Authorization headers
    const corsProxy = getCorsProxy();
    let remoteUrl = settings.remoteUrl;
    if (corsProxy.includes('cors.isomorphic-git.org') && settings.username && settings.token) {
      console.log('[git-sync:push] Using public CORS proxy, embedding credentials in URL');
      remoteUrl = buildUrlWithEmbeddedAuth(remoteUrl, settings.username, settings.token, corsProxy);
    }

    console.log('[git-sync:push] Adding remote origin');
    await git.addRemote({ fs, dir: GIT_DIR, remote: 'origin', url: remoteUrl, force: true });
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

    // For new/empty repositories, ensure we have a local branch with at least one commit
    console.log('[git-sync:push] Ensuring local branch is initialized:', branch);
    const branchReady = await ensureInitializedBranch(branch);
    if (!branchReady) {
      console.warn('[git-sync:push] Could not initialize branch');
      return { ok: false, message: 'Could not initialize local branch. Try again.' };
    }

    // Try pushing to the current branch
    console.log('[git-sync:push] Attempting push to branch:', branch);
    console.log('[git-sync:push] Using CORS proxy:', getCorsProxy());

    try {
      console.log('[git-sync:push] First attempt: push as-is');
      console.log('[git-sync:push] git.push() call with params:', {
        dir: GIT_DIR,
        remote: 'origin',
        ref: branch,
        corsProxy: getCorsProxy().substring(0, 30) + '...',
      });

      console.log('[git-sync:push] About to call git.push()...');
      const beforeTime = performance.now();

      const pushResult = await git.push({
        fs,
        http: window.GitHttp,
        dir: GIT_DIR,
        remote: 'origin',
        ref: branch,
        corsProxy: getCorsProxy(),
        onAuth: () => {
          console.log('[git-sync:push] ⚠️  Auth callback invoked during push');
          console.log('[git-sync:push]   Returning username:', settings.username);
          console.log('[git-sync:push]   Token length:', settings.token?.length || 0);
          return { username: settings.username, password: settings.token };
        },
      });

      const afterTime = performance.now();
      console.log('[git-sync:push] ✓ git.push() returned without error (took', (afterTime - beforeTime).toFixed(0), 'ms)');
      console.log('[git-sync:push] Push result type:', typeof pushResult);
      console.log('[git-sync:push] Push result is null/undefined?', pushResult == null);
      console.log('[git-sync:push] Push result value:', pushResult);
      console.log('[git-sync:push] Push result keys:', pushResult ? Object.keys(pushResult) : 'null');
      console.log('[git-sync:push] Push result JSON:', JSON.stringify(pushResult));

      // Verify push actually succeeded by checking remote
      // Use the same remoteUrl (with embedded credentials if needed) that was used for push
      const verified = await verifyPushSuccess(branch, remoteUrl, corsProxy, settings);
      if (!verified) {
        console.warn('[git-sync:push] Push verification failed - commits may not be on remote');
        return { ok: false, message: 'Push appeared successful but commits not found on remote. Check network connection and credentials.' };
      }

      console.log('[git-sync:push] ✓ PUSH SUCCESSFUL');
      console.log('[git-sync:push] ========== PUSH OPERATION END ==========');
      return { ok: true, result: pushResult };
    } catch (pushError) {
      const pushMsg = pushError.message || String(pushError);
      console.error('[git-sync:push] ❌ First push attempt failed');
      console.error('[git-sync:push] Error message:', pushMsg);
      console.error('[git-sync:push] Error type:', pushError.constructor.name);
      console.error('[git-sync:push] Full error:', pushError);
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
            corsProxy: getCorsProxy(),
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
                corsProxy: getCorsProxy(),
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
    console.error('[git-sync:push] ========== PUSH OPERATION FAILED ==========');
    console.error('[git-sync:push] Error message:', msg);
    console.error('[git-sync:push] Error type:', e.constructor.name);
    console.error('[git-sync:push] Full error:', e);
    console.error('[git-sync:push] Error stack:', e.stack);
    console.error('[git-sync:push] Push operation failed:', msg);

    if (msg.includes('Could not find') || msg.includes('not found') || msg.includes('no matching')) {
      console.error('[git-sync:push] Diagnosis: Repository not initialized or empty');
      return {
        ok: false,
        message: 'Remote repository has no branches. On GitHub: Add a README file (or any file) to create an initial commit, then retry push.'
      };
    }
    if (msg.includes('authentication') || msg.includes('Unauthorized') || msg.includes('403') || msg.includes('401')) {
      console.error('[git-sync:push] Diagnosis: Authentication error');
      const corsProxy = getCorsProxy();
      const suggestion = corsProxy.includes('cors.isomorphic-git.org')
        ? ' Try using local CORS proxy: make pwa-cors-proxy'
        : '';
      return {
        ok: false,
        message: `Authentication failed. Check your token and username.${suggestion}`
      };
    }
    if (msg.includes('CORS') || msg.includes('cors') || msg.includes('Access-Control-Allow-Origin')) {
      console.error('[git-sync:push] Diagnosis: CORS error - server does not allow cross-origin requests');
      return {
        ok: false,
        message: 'CORS blocked. For private git servers: deploy PWA on same domain or use local CORS proxy.'
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
    // For public CORS proxy, embed credentials in URL since it doesn't forward Authorization headers
    const corsProxy = getCorsProxy();
    let remoteUrl = settings.remoteUrl;
    if (corsProxy.includes('cors.isomorphic-git.org') && settings.username && settings.token) {
      console.log('[git-sync:pull] Using public CORS proxy, embedding credentials in URL');
      remoteUrl = buildUrlWithEmbeddedAuth(remoteUrl, settings.username, settings.token, corsProxy);
    }

    console.log('[git-sync:pull] Adding remote origin');
    await git.addRemote({ fs, dir: GIT_DIR, remote: 'origin', url: remoteUrl, force: true });
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
        corsProxy: getCorsProxy(),
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
            corsProxy: getCorsProxy(),
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
    if (msg.includes('CORS') || msg.includes('cors') || msg.includes('Access-Control-Allow-Origin')) {
      console.error('[git-sync:pull] Diagnosis: CORS error - server does not allow cross-origin requests');
      return {
        ok: false,
        message: 'CORS blocked. For private git servers: deploy PWA on same domain or use local CORS proxy.'
      };
    }
    console.error('[git-sync:pull] Returning generic error:', msg);
    return { ok: false, message: msg };
  }
}
