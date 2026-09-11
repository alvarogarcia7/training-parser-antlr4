/* Service Worker for Training Parser PWA */

const CACHE_NAME = 'training-parser-v1';

const APP_SHELL = [
  './',
  './index.html',
  './manifest.json',
  './icons/icon.svg',
  './src/ui.js',
  './src/share.js',
  './src/git-sync.js',
  './python/app_api.py',
];

const PYTHON_SOURCES = [
  '../parser/__init__.py',
  '../parser/model.py',
  '../parser/parser.py',
  '../parser/standardize_name.py',
  '../parser/serializer.py',
  '../parser/error_listener.py',
  '../parser/series_builder.py',
  '../src/statistics.py',
  '../dist/trainingLexer.py',
  '../dist/trainingParser.py',
  '../dist/trainingListener.py',
  '../dist/trainingVisitor.py',
  '../data/synonyms.yaml',
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll([...APP_SHELL, ...PYTHON_SOURCES].map(url => {
        return new Request(url, { cache: 'no-cache' });
      })).catch(() => {
        // Cache what we can; Python sources may not be available at install time
        return cache.addAll(APP_SHELL);
      });
    })
  );
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)))
    )
  );
  self.clients.claim();
});

self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url);

  // Handle share_target POST
  if (url.pathname.endsWith('/share-target') && event.request.method === 'POST') {
    event.respondWith(handleShareTarget(event.request));
    return;
  }

  // Cache-first for app shell and Python sources, network-first for Pyodide CDN
  if (url.hostname === 'cdn.jsdelivr.net' || url.pathname.includes('pyodide')) {
    event.respondWith(networkFirstWithCache(event.request));
  } else {
    event.respondWith(cacheFirstWithNetwork(event.request));
  }
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

async function cacheFirstWithNetwork(request) {
  const cached = await caches.match(request);
  if (cached) return cached;
  try {
    const response = await fetch(request);
    if (response.ok) {
      const cache = await caches.open(CACHE_NAME);
      cache.put(request, response.clone());
    }
    return response;
  } catch {
    return new Response('Offline', { status: 503 });
  }
}

async function networkFirstWithCache(request) {
  try {
    const response = await fetch(request);
    if (response.ok) {
      const cache = await caches.open(CACHE_NAME);
      cache.put(request, response.clone());
    }
    return response;
  } catch {
    const cached = await caches.match(request);
    return cached || new Response('Offline', { status: 503 });
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
