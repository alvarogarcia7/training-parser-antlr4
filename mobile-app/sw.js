/* Service Worker for Training Parser PWA */

const CACHE_NAME = 'training-parser-v1';
const PYODIDE_VERSION = 'v0.27.0';

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
  // antlr4 runtime
  './python/antlr4/__init__.py',
  './python/antlr4/BufferedTokenStream.py',
  './python/antlr4/CommonTokenFactory.py',
  './python/antlr4/CommonTokenStream.py',
  './python/antlr4/FileStream.py',
  './python/antlr4/InputStream.py',
  './python/antlr4/IntervalSet.py',
  './python/antlr4/LL1Analyzer.py',
  './python/antlr4/Lexer.py',
  './python/antlr4/ListTokenSource.py',
  './python/antlr4/Parser.py',
  './python/antlr4/ParserInterpreter.py',
  './python/antlr4/ParserRuleContext.py',
  './python/antlr4/PredictionContext.py',
  './python/antlr4/Recognizer.py',
  './python/antlr4/RuleContext.py',
  './python/antlr4/StdinStream.py',
  './python/antlr4/Token.py',
  './python/antlr4/TokenStreamRewriter.py',
  './python/antlr4/Utils.py',
  './python/antlr4/atn/__init__.py',
  './python/antlr4/atn/ATN.py',
  './python/antlr4/atn/ATNConfig.py',
  './python/antlr4/atn/ATNConfigSet.py',
  './python/antlr4/atn/ATNDeserializationOptions.py',
  './python/antlr4/atn/ATNDeserializer.py',
  './python/antlr4/atn/ATNSimulator.py',
  './python/antlr4/atn/ATNState.py',
  './python/antlr4/atn/ATNType.py',
  './python/antlr4/atn/LexerATNSimulator.py',
  './python/antlr4/atn/LexerAction.py',
  './python/antlr4/atn/LexerActionExecutor.py',
  './python/antlr4/atn/ParserATNSimulator.py',
  './python/antlr4/atn/PredictionMode.py',
  './python/antlr4/atn/SemanticContext.py',
  './python/antlr4/atn/Transition.py',
  './python/antlr4/dfa/__init__.py',
  './python/antlr4/dfa/DFA.py',
  './python/antlr4/dfa/DFASerializer.py',
  './python/antlr4/dfa/DFAState.py',
  './python/antlr4/error/__init__.py',
  './python/antlr4/error/DiagnosticErrorListener.py',
  './python/antlr4/error/ErrorListener.py',
  './python/antlr4/error/ErrorStrategy.py',
  './python/antlr4/error/Errors.py',
  './python/antlr4/tree/__init__.py',
  './python/antlr4/tree/Chunk.py',
  './python/antlr4/tree/ParseTreeMatch.py',
  './python/antlr4/tree/ParseTreePattern.py',
  './python/antlr4/tree/ParseTreePatternMatcher.py',
  './python/antlr4/tree/RuleTagToken.py',
  './python/antlr4/tree/TokenTagToken.py',
  './python/antlr4/tree/Tree.py',
  './python/antlr4/tree/Trees.py',
  './python/antlr4/xpath/__init__.py',
  './python/antlr4/xpath/XPath.py',
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

// Pyodide runtime files to pre-cache
const PYODIDE_RUNTIME = [
  `https://cdn.jsdelivr.net/pyodide/${PYODIDE_VERSION}/full/pyodide.js`,
  `https://cdn.jsdelivr.net/pyodide/${PYODIDE_VERSION}/full/pyodide.mjs`,
  `https://cdn.jsdelivr.net/pyodide/${PYODIDE_VERSION}/full/pyodide_py.tar`,
  `https://cdn.jsdelivr.net/pyodide/${PYODIDE_VERSION}/full/python_stdlib.tar`,
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      // Cache app shell immediately
      const shellPromise = cache.addAll(APP_SHELL);

      // Cache Python sources and Pyodide runtime in background
      // Don't fail install if these aren't available yet
      Promise.all([
        cache.addAll(PYTHON_SOURCES).catch(() => {}),
        cache.addAll(PYODIDE_RUNTIME).catch(() => {}),
      ]).catch(() => {});

      return shellPromise;
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

  // Cache-first for everything (app shell, Python sources, Pyodide runtime)
  // Pyodide CDN URLs cached aggressively to avoid re-download on every refresh
  event.respondWith(cacheFirstWithNetwork(event.request));
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
