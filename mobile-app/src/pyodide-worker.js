/* Pyodide Web Worker — loads Python runtime and exposes parse/stats API */

const START_TIME = performance.now();
function log(msg) {
  const elapsed = (performance.now() - START_TIME).toFixed(0);
  console.log(`[pyodide ${elapsed}ms] ${msg}`);
  self.postMessage({ type: 'log', message: `${msg}` });
}

importScripts('https://cdn.jsdelivr.net/pyodide/v0.27.0/full/pyodide.js');

let pyodide = null;
log('Script imported');

const PYTHON_FILES = [
  // [fetch_path, pyodide_fs_path]
  ['../parser/__init__.py',           '/home/pyodide/parser/__init__.py'],
  ['../parser/model.py',              '/home/pyodide/parser/model.py'],
  ['../parser/parser.py',             '/home/pyodide/parser/parser.py'],
  ['../parser/standardize_name.py',   '/home/pyodide/parser/standardize_name.py'],
  ['../parser/serializer.py',         '/home/pyodide/parser/serializer.py'],
  ['../parser/error_listener.py',     '/home/pyodide/parser/error_listener.py'],
  ['../parser/series_builder.py',     '/home/pyodide/parser/series_builder.py'],
  ['../src/__init__.py',              '/home/pyodide/src/__init__.py'],
  ['../src/statistics.py',            '/home/pyodide/src/statistics.py'],
  ['../dist/__init__.py',             '/home/pyodide/dist/__init__.py'],
  ['../dist/trainingLexer.py',        '/home/pyodide/dist/trainingLexer.py'],
  ['../dist/trainingParser.py',       '/home/pyodide/dist/trainingParser.py'],
  ['../dist/trainingListener.py',     '/home/pyodide/dist/trainingListener.py'],
  ['../dist/trainingVisitor.py',      '/home/pyodide/dist/trainingVisitor.py'],
  ['../data/synonyms.yaml',           '/home/pyodide/data/synonyms.yaml'],
  ['./python/app_api.py',             '/home/pyodide/app_api.py'],
];

async function initPyodide() {
  log('initPyodide started');
  self.postMessage({ type: 'loading', message: 'Loading Python runtime...' });

  log('loadPyodide() starting...');
  pyodide = await loadPyodide();
  log(`loadPyodide() done - ${pyodide ? 'success' : 'failed'}`);

  self.postMessage({ type: 'loading', message: 'Installing packages...' });
  log('loadPackage(micropip, pyyaml) starting...');
  await pyodide.loadPackage(['micropip', 'pyyaml']);
  log('loadPackage done, packages loaded');

  log('Importing micropip...');
  const micropip = pyodide.pyimport('micropip');
  log('micropip imported');

  // Try to install antlr4, but skip if it times out
  log('Checking if antlr4 needs install...');
  try {
    pyodide.runPython('import antlr4; print("antlr4 already available")');
    log('antlr4 already available, skipping install');
  } catch (e) {
    log('antlr4 not found, attempting to install...');
    try {
      log('Calling micropip.install...');
      const installPromise = micropip.install('antlr4-python3-runtime==4.9.3');
      log('install() called, awaiting...');

      // Timeout after 15 seconds
      const timeoutPromise = new Promise((_, reject) =>
        setTimeout(() => reject(new Error('Install timeout')), 15000)
      );

      await Promise.race([installPromise, timeoutPromise]);
      log('antlr4 installed successfully');
    } catch (installErr) {
      log(`WARN: antlr4 install failed: ${installErr.message}, skipping`);
    }
  }

  self.postMessage({ type: 'loading', message: 'Loading parser modules...' });
  log('Creating directories...');

  // Create directories in Pyodide FS
  pyodide.FS.mkdir('/home/pyodide/parser');
  pyodide.FS.mkdir('/home/pyodide/src');
  pyodide.FS.mkdir('/home/pyodide/dist');
  pyodide.FS.mkdir('/home/pyodide/data');
  log('Directories created');

  // Write empty __init__.py for packages that don't have one on disk
  const emptyInit = '';
  try { pyodide.FS.writeFile('/home/pyodide/src/__init__.py', emptyInit, { encoding: 'utf8' }); } catch {}
  try { pyodide.FS.writeFile('/home/pyodide/dist/__init__.py', emptyInit, { encoding: 'utf8' }); } catch {}

  // Fetch and write each Python source file
  log(`Fetching ${PYTHON_FILES.length} Python files...`);
  for (const [fetchPath, fsPath] of PYTHON_FILES) {
    try {
      const resp = await fetch(fetchPath);
      if (resp.ok) {
        const text = await resp.text();
        pyodide.FS.writeFile(fsPath, text, { encoding: 'utf8' });
      }
    } catch (e) {
      console.warn(`Could not load ${fetchPath}:`, e);
    }
  }
  log('All Python files written');

  // Put our source root on the Python path
  log('Setting Python path...');
  pyodide.runPython(`
import sys
if '/home/pyodide' not in sys.path:
    sys.path.insert(0, '/home/pyodide')
`);
  log('Python path set');

  log('initPyodide complete - sending ready signal');
  self.postMessage({ type: 'ready' });
}

async function callPython(fn, ...args) {
  const argsJs = args.map(a => typeof a === 'string' ? JSON.stringify(a) : String(a));
  const callStr = `import app_api; app_api.${fn}(${argsJs.join(', ')})`;
  return pyodide.runPythonAsync(callStr);
}

self.onmessage = async (event) => {
  const { type, id, ...data } = event.data;

  try {
    if (type === 'init') {
      log('init message received, starting initPyodide...');
      await initPyodide();
      log('initPyodide complete');
      return;
    }

    if (!pyodide) {
      self.postMessage({ type: 'error', id, message: 'Pyodide not ready' });
      return;
    }

    if (type === 'parse') {
      const result = await pyodide.runPythonAsync(
        `import app_api; app_api.parse_workout_text(${JSON.stringify(data.text)})`
      );
      self.postMessage({ type: 'parse_result', id, result: JSON.parse(result) });

    } else if (type === 'stats') {
      const result = await pyodide.runPythonAsync(
        `import app_api; app_api.get_statistics(${JSON.stringify(data.exercisesJson)}, ${data.timeMinutes})`
      );
      self.postMessage({ type: 'stats_result', id, result: JSON.parse(result) });

    } else if (type === 'format_stats') {
      const result = await pyodide.runPythonAsync(
        `import app_api; app_api.format_statistics(${JSON.stringify(data.exercisesJson)}, ${data.timeMinutes})`
      );
      self.postMessage({ type: 'format_stats_result', id, result });

    } else if (type === 'serialize') {
      const result = await pyodide.runPythonAsync(
        `import app_api; app_api.serialize_to_set_centric_json(${JSON.stringify(data.exercisesJson)}, ${JSON.stringify(data.dateStr)})`
      );
      self.postMessage({ type: 'serialize_result', id, result: JSON.parse(result) });
    }
  } catch (e) {
    self.postMessage({ type: 'error', id, message: e.message || String(e) });
  }
};

// Auto-start
log('Worker script loaded, auto-starting initPyodide...');
initPyodide().catch(e => {
  log(`ERROR in initPyodide: ${e.message}`);
  self.postMessage({ type: 'error', message: 'Failed to initialize: ' + e.message });
});
