/* Pyodide Web Worker — loads Python runtime and exposes parse/stats API */

const START_TIME = performance.now();
const LOG_LEVELS = { DEBUG: 0, INFO: 1, WARN: 2, ERROR: 3 };

function log(msg, level = 'INFO') {
  const elapsed = (performance.now() - START_TIME).toFixed(0);
  const prefix = `[pyodide ${elapsed}ms]`;
  const levelStr = level.padEnd(5);
  console.log(`${prefix} ${levelStr} ${msg}`);
  try {
    self.postMessage({ type: 'log', message: msg, level, elapsed: parseInt(elapsed) });
  } catch (e) {
    console.error('Failed to post log message:', e);
  }
}

// Very early logging to detect initialization
console.log('[worker] Script starting, about to load Pyodide...');
log('Worker script started', 'DEBUG');

try {
  // Load Pyodide from vendored location (no CDN fallback - offline-first)
  const pyodidePath = '/vendor/pyodide/pyodide.js';
  log(`Loading Pyodide from vendored location: ${pyodidePath}`, 'INFO');
  importScripts(pyodidePath);
  log(`✓ Pyodide loaded successfully from vendored assets`, 'INFO');
} catch (e) {
  const errorMsg = `Failed to load Pyodide from vendored location (/vendor/pyodide/pyodide.js). Ensure vendor assets are generated with 'make vendor-pyodide'. Error: ${e.message}`;
  log(errorMsg, 'ERROR');
  self.postMessage({ type: 'error', message: errorMsg });
  throw e;
}

let pyodide = null;
log('Script imports complete', 'DEBUG');

async function initPyodide() {
  log('initPyodide started', 'INFO');
  self.postMessage({ type: 'loading', message: 'Loading Python runtime...' });

  try {
    log('loadPyodide() starting (this may take 10-20s)...', 'DEBUG');
    self.postMessage({ type: 'loading', message: 'Loading Pyodide... (this takes 10-20 seconds on first load)' });

    // Wrap in timeout to detect hangs
    const loadPromise = loadPyodide();
    const timeoutPromise = new Promise((_, reject) =>
      setTimeout(() => reject(new Error('loadPyodide timeout after 30 seconds')), 30000)
    );

    pyodide = await Promise.race([loadPromise, timeoutPromise]);
    if (!pyodide) throw new Error('loadPyodide returned null');
    log(`loadPyodide() done - Pyodide ready`, 'INFO');
  } catch (e) {
    log(`loadPyodide() failed: ${e.message}`, 'ERROR');
    self.postMessage({ type: 'error', message: 'Pyodide load failed: ' + e.message });
    throw e;
  }

  try {
    log('loadPackage starting...', 'DEBUG');
    self.postMessage({ type: 'loading', message: 'Loading Python packages (pyyaml, jsonschema)...' });

    // Set timeout for package loading
    const pkgPromise = pyodide.loadPackage(['pyyaml', 'jsonschema']);
    const pkgTimeout = new Promise((_, reject) =>
      setTimeout(() => reject(new Error('loadPackage timeout after 20 seconds')), 20000)
    );

    await Promise.race([pkgPromise, pkgTimeout]);
    log('Packages loaded: pyyaml, jsonschema', 'INFO');
  } catch (e) {
    log(`loadPackage failed (non-critical): ${e.message}`, 'WARN');
    // Don't fail hard on package loading - continue
  }

  self.postMessage({ type: 'loading', message: 'Loading parser modules...' });
  log('Creating directories...', 'DEBUG');

  // Create base directory for Pyodide filesystem
  try {
    pyodide.FS.mkdir('/home/pyodide');
  } catch (e) {
    if (!e.message.includes('already exists')) {
      log(`Failed to create /home/pyodide: ${e.message}`, 'WARN');
    }
  }
  log('Base directory created', 'DEBUG');

  // Load vendor archives: vendor-runtime.tar.gz (antlr4 + app_api.py) and app.zip
  self.postMessage({ type: 'loading', message: 'Loading Python runtime archives...' });

  try {
    // Fetch and unpack vendor-runtime.tar.gz (antlr4 runtime)
    log('Fetching vendor-runtime.tar.gz...', 'INFO');
    let vendorRuntimeResp;
    try {
      vendorRuntimeResp = await fetch('/vendor/vendor-runtime.tar.gz');
    } catch (e) {
      // Fallback to relative path for development
      vendorRuntimeResp = await fetch('./vendor/vendor-runtime.tar.gz');
    }

    if (!vendorRuntimeResp.ok) {
      throw new Error(`Failed to fetch vendor-runtime.tar.gz: HTTP ${vendorRuntimeResp.status}`);
    }

    const vendorRuntimeBuffer = await vendorRuntimeResp.arrayBuffer();
    log(`vendor-runtime.tar.gz fetched (${(vendorRuntimeBuffer.byteLength / 1024 / 1024).toFixed(2)} MB)`, 'INFO');

    log('Unpacking vendor-runtime.tar.gz...', 'INFO');
    self.postMessage({ type: 'loading', message: 'Unpacking Python runtime...' });
    await pyodide.unpackArchive(vendorRuntimeBuffer, 'tar');
    log('✓ vendor-runtime.tar.gz unpacked', 'INFO');

  } catch (e) {
    log(`Warning: Failed to load vendor runtime archive: ${e.message}`, 'WARN');
    self.postMessage({ type: 'loading', message: 'Vendor runtime fallback mode...' });
  }

  try {
    // Fetch and unpack app.zip (application code, schema, data)
    log('Fetching app.zip...', 'INFO');
    let appZipResp;
    try {
      appZipResp = await fetch('/vendor/app.zip');
    } catch (e) {
      // Fallback to relative path for development
      appZipResp = await fetch('./vendor/app.zip');
    }

    if (!appZipResp.ok) {
      throw new Error(`Failed to fetch app.zip: HTTP ${appZipResp.status}`);
    }

    const appZipBuffer = await appZipResp.arrayBuffer();
    log(`app.zip fetched (${(appZipBuffer.byteLength / 1024 / 1024).toFixed(2)} MB)`, 'INFO');

    log('Unpacking app.zip...', 'INFO');
    self.postMessage({ type: 'loading', message: 'Unpacking application code...' });
    await pyodide.unpackArchive(appZipBuffer, 'zip');
    log('✓ app.zip unpacked', 'INFO');

  } catch (e) {
    log(`Error: Failed to load app archive: ${e.message}`, 'ERROR');
    self.postMessage({ type: 'error', message: 'Failed to load application code: ' + e.message });
    throw e;
  }

  // List what's actually in /home/pyodide to verify archives were unpacked
  try {
    const pyodideDir = pyodide.FS.readdir('/home/pyodide');
    const pyodideDirContents = pyodideDir.filter(f => f !== '.' && f !== '..');
    log(`Contents of /home/pyodide: ${pyodideDirContents.join(', ')}`, 'DEBUG');
  } catch (e) {
    log(`Cannot read /home/pyodide: ${e.message}`, 'ERROR');
  }

  // Put our source root on the Python path
  log('Setting Python path...', 'DEBUG');
  pyodide.runPython(`
import sys
sys.path.insert(0, '/home/pyodide')
print('Path:', sys.path[:3])
`);
  log('Python path set', 'DEBUG');

  // Verify antlr4 exists
  try {
    const antlr4Path = '/home/pyodide/antlr4/__init__.py';
    const antlr4File = pyodide.FS.readFile(antlr4Path, { encoding: 'utf8' });
    log(`antlr4 found (${antlr4File.length} bytes)`, 'DEBUG');
  } catch (e) {
    log(`antlr4 NOT found: ${e.message}`, 'ERROR');
  }

  // Check if app_api.py exists in filesystem
  try {
    const appApiPath = '/home/pyodide/app_api.py';
    const appApiFile = pyodide.FS.readFile(appApiPath, { encoding: 'utf8' });
    log(`app_api.py found (${appApiFile.length} bytes)`, 'DEBUG');
  } catch (e) {
    log(`app_api.py NOT found: ${e.message}`, 'ERROR');
  }

  log('Testing imports...', 'DEBUG');
  self.postMessage({ type: 'loading', message: 'Testing Python imports...' });

  // Test file existence
  try {
    pyodide.runPython(`
import os
files_exist = {
    'antlr4': os.path.exists('/home/pyodide/antlr4/__init__.py'),
    'app_api': os.path.exists('/home/pyodide/app_api.py'),
    'parser': os.path.exists('/home/pyodide/src/parser/__init__.py'),
}
print("Files exist:", files_exist)
`);
    log('File existence check printed', 'DEBUG');
  } catch (e) {
    log(`File check error: ${e.message}`, 'WARN');
  }

  // Test antlr4 import first (needed by app_api.py)
  try {
    log('Attempting to import antlr4...', 'DEBUG');
    pyodide.runPython('import antlr4; print("✓ antlr4 available")');
    log('antlr4 available', 'INFO');
  } catch (e) {
    log(`antlr4 import error: ${e.message}`, 'ERROR');
    self.postMessage({ type: 'error', message: `antlr4 import failed: ${e.message}` });
    throw e;
  }

  // Import app_api
  try {
    log('Attempting to import app_api...', 'DEBUG');
    pyodide.runPython('import app_api; print("✓ app_api loaded")');
    log('app_api imported successfully', 'INFO');
  } catch (e) {
    log(`app_api import failed: ${e.message}`, 'ERROR');
    self.postMessage({ type: 'error', message: `app_api import failed: ${e.message}` });
    throw e;
  }

  log('initPyodide complete - sending ready signal', 'INFO');
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
      log('init message received, starting initPyodide...', 'DEBUG');
      await initPyodide();
      log('initPyodide complete', 'INFO');
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

    } else if (type === 'parse_and_export') {
      const result = await pyodide.runPythonAsync(
        `import app_api; app_api.parse_and_export(${JSON.stringify(data.text)}, ${JSON.stringify(data.dateStr || '')})`
      );
      self.postMessage({ type: 'parse_and_export_result', id, result: JSON.parse(result) });

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

// Auto-start initialization
console.log('[worker] Worker script fully loaded, auto-starting initPyodide...');
log('Worker script loaded, auto-starting initPyodide...', 'INFO');

initPyodide()
  .then(() => {
    log('✓ Initialization complete and successful', 'INFO');
    console.log('[worker] ✓ Initialization complete');
  })
  .catch(e => {
    const errorMsg = e.message || String(e);
    log(`✗ initPyodide failed: ${errorMsg}`, 'ERROR');
    console.error('[worker] ✗ Initialization failed:', e);
    self.postMessage({ type: 'error', message: 'Initialization failed: ' + errorMsg });
  });
