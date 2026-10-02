/* Service Worker for Training Parser PWA */

const PYODIDE_VERSION = 'v0.27.0';
let CACHE_VERSION = 'v1';
let PYODIDE_CACHE_NAME = `training-parser-pyodide-${PYODIDE_VERSION}`;

const APP_SHELL = [
  './',
  './index.html',
  './manifest.json',
  './icons/icon.svg',
  './src/ui.js',
  './src/share.js',
  './src/git-sync.js',
  './src/pyodide-worker.js',
  './python/app_api.py',
];

// CDN libraries for git sync and filesystem (immutable, versioned URLs)
const CDN_LIBS = [
  'https://unpkg.com/@isomorphic-git/lightning-fs@4.6.0/dist/lightning-fs.min.js',
  'https://unpkg.com/isomorphic-git@1.27.1/index.umd.min.js',
];

// Pyodide runtime files (large, immutable, versioned URLs)
const PYODIDE_RUNTIME = [
  `https://cdn.jsdelivr.net/pyodide/${PYODIDE_VERSION}/full/pyodide.js`,
  `https://cdn.jsdelivr.net/pyodide/${PYODIDE_VERSION}/full/pyodide.mjs`,
  `https://cdn.jsdelivr.net/pyodide/${PYODIDE_VERSION}/full/pyodide_py.tar`,
  `https://cdn.jsdelivr.net/pyodide/${PYODIDE_VERSION}/full/python_stdlib.tar`,
];

// Archive files (bundled, immutable after deployment)
const VENDOR_ARCHIVES = [
  './vendor/vendor-runtime.tar.gz',
  './vendor/app.zip',
];

// Check version.json on each session to invalidate old caches
let versionCheckDone = false;
let currentVersion = null;

async function checkVersion() {
  if (versionCheckDone) return;

  try {
    const resp = await fetch('./version.json', { cache: 'no-store' });
    if (resp.ok) {
      const data = await resp.json();
      currentVersion = data.version;
      CACHE_VERSION = data.version || 'v1';
      PYODIDE_CACHE_NAME = `training-parser-pyodide-${PYODIDE_VERSION}-${CACHE_VERSION}`;
    }
  } catch (e) {
    console.log('[sw] version.json check failed (non-critical)', e.message);
  }
  versionCheckDone = true;
}

self.addEventListener('install', (event) => {
  event.waitUntil(
    (async () => {
      const cacheName = `training-parser-${CACHE_VERSION}`;
      const cache = await caches.open(cacheName);

      // Cache app shell
      await cache.addAll(APP_SHELL).catch(() => {
        console.log('[sw] Some app shell items failed (non-critical)');
      });

      // Cache vendor archives, CDN libs, and Pyodide runtime in background
      // Don't fail install if these aren't available yet
      Promise.all([
        cache.addAll(VENDOR_ARCHIVES).catch(() => {}),
        cache.addAll(CDN_LIBS).catch(() => {}),
      ]).catch(() => {});

      // Pre-cache Pyodide runtime in separate cache
      const pyodideCache = await caches.open(PYODIDE_CACHE_NAME);
      pyodideCache.addAll(PYODIDE_RUNTIME).catch(() => {
        console.log('[sw] Some Pyodide files failed (non-critical)');
      });
    })()
  );
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    (async () => {
      // Delete old version caches
      const keys = await caches.keys();
      const cachesToDelete = keys.filter(k =>
        !k.includes(CACHE_VERSION) &&
        !k.includes(PYODIDE_VERSION)
      );

      // Delete old Pyodide caches with different versions
      const oldPyodideCaches = keys.filter(k =>
        k.startsWith('training-parser-pyodide-') &&
        !k.startsWith(`training-parser-pyodide-${PYODIDE_VERSION}`)
      );

      await Promise.all([
        ...cachesToDelete.map(k => caches.delete(k)),
        ...oldPyodideCaches.map(k => caches.delete(k)),
      ]);

      // Request storage persistence
      if (navigator.storage && navigator.storage.persist) {
        navigator.storage.persist().catch(e => {
          console.log('[sw] Storage persistence not available:', e.message);
        });
      }
    })()
  );
  self.clients.claim();
});

self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url);

  // Skip /requirements/ (docs)
  if (url.pathname.startsWith('/requirements/')) {
    return;
  }

  // Handle share_target POST
  if (url.pathname.endsWith('/share-target') && event.request.method === 'POST') {
    event.respondWith(handleShareTarget(event.request));
    return;
  }

  // Skip non-GET requests
  if (event.request.method !== 'GET') {
    return;
  }

  // Cache-first for Pyodide CDN and CDN libs (large, immutable, versioned URLs)
  const isPyodideCDN = url.hostname === 'cdn.jsdelivr.net' || url.hostname === 'unpkg.com';
  if (isPyodideCDN) {
    event.respondWith(cacheFirstWithNetwork(event.request, PYODIDE_CACHE_NAME));
    return;
  }

  // Cache-first for hashed/versioned assets (vendor archives, app shell)
  if (url.pathname.includes('/vendor/') ||
      url.pathname === '/' ||
      url.pathname === '/index.html' ||
      url.pathname.endsWith('.svg') ||
      url.pathname.endsWith('.js') ||
      url.pathname.endsWith('.css')) {

    event.respondWith(cacheFirstWithNetwork(event.request));
    return;
  }

  // Network-first for everything else
  event.respondWith(networkFirstWithCache(event.request));
});

async function handleShareTarget(request) {
  const formData = await request.formData();
  const text = formData.get('text') || formData.get('title') || '';

  // Pass shared text to any open client windows
  const clients = await self.clients.matchAll({ type: 'window' });
  for (const client of clients) {
    client.postMessage({ type: 'shared_text', text });
  }

  // Redirect to main page
  return Response.redirect('./', 303);
}

async function cacheFirstWithNetwork(request, cacheName) {
  cacheName = cacheName || `training-parser-${CACHE_VERSION}`;

  try {
    const cached = await caches.match(request);
    if (cached) return cached;
  } catch (e) {
    console.log('[sw] Cache match failed:', e.message);
  }

  try {
    const response = await fetch(request);
    if (response.ok) {
      const cache = await caches.open(cacheName);
      cache.put(request, response.clone()).catch(() => {
        // Silently ignore cache write errors
      });
    }
    return response;
  } catch {
    return new Response('Offline', { status: 503 });
  }
}

async function networkFirstWithCache(request) {
  const cacheName = `training-parser-${CACHE_VERSION}`;

  try {
    const response = await fetch(request);
    if (response.ok) {
      const cache = await caches.open(cacheName);
      cache.put(request, response.clone()).catch(() => {
        // Silently ignore cache write errors
      });
    }
    return response;
  } catch {
    try {
      const cached = await caches.match(request);
      if (cached) return cached;
    } catch (e) {
      console.log('[sw] Cache match failed:', e.message);
    }
    return new Response('Offline', { status: 503 });
  }
}

// Background sync for git push
self.addEventListener('sync', (event) => {
  if (event.tag === 'git-push') {
    event.waitUntil(notifyClientsToSync());
  }
});

async function notifyClientsToSync() {
  const clients = await self.clients.matchAll({ type: 'window' });
  for (const client of clients) {
    client.postMessage({ type: 'sync_requested' });
  }
}

// Message handler for clients
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});

// 20261002
