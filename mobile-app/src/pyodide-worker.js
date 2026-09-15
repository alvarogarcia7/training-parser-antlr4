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
  importScripts('https://cdn.jsdelivr.net/pyodide/v0.27.0/full/pyodide.js');
  log('Pyodide script imported from CDN', 'INFO');
} catch (e) {
  log(`Failed to import Pyodide script: ${e.message}`, 'ERROR');
  self.postMessage({ type: 'error', message: 'Failed to load Pyodide: ' + e.message });
  throw e;
}

let pyodide = null;
log('Script imports complete', 'DEBUG');

const PYTHON_FILES = [
  // [fetch_path, pyodide_fs_path]
  // antlr4 runtime (bundled in mobile-app/python)
  ['../python/antlr4/__init__.py',             '/home/pyodide/antlr4/__init__.py'],
  ['../python/antlr4/BufferedTokenStream.py',  '/home/pyodide/antlr4/BufferedTokenStream.py'],
  ['../python/antlr4/CommonTokenFactory.py',   '/home/pyodide/antlr4/CommonTokenFactory.py'],
  ['../python/antlr4/CommonTokenStream.py',    '/home/pyodide/antlr4/CommonTokenStream.py'],
  ['../python/antlr4/FileStream.py',           '/home/pyodide/antlr4/FileStream.py'],
  ['../python/antlr4/InputStream.py',          '/home/pyodide/antlr4/InputStream.py'],
  ['../python/antlr4/IntervalSet.py',          '/home/pyodide/antlr4/IntervalSet.py'],
  ['../python/antlr4/LL1Analyzer.py',          '/home/pyodide/antlr4/LL1Analyzer.py'],
  ['../python/antlr4/Lexer.py',                '/home/pyodide/antlr4/Lexer.py'],
  ['../python/antlr4/ListTokenSource.py',      '/home/pyodide/antlr4/ListTokenSource.py'],
  ['../python/antlr4/Parser.py',               '/home/pyodide/antlr4/Parser.py'],
  ['../python/antlr4/ParserInterpreter.py',    '/home/pyodide/antlr4/ParserInterpreter.py'],
  ['../python/antlr4/ParserRuleContext.py',    '/home/pyodide/antlr4/ParserRuleContext.py'],
  ['../python/antlr4/PredictionContext.py',    '/home/pyodide/antlr4/PredictionContext.py'],
  ['../python/antlr4/Recognizer.py',           '/home/pyodide/antlr4/Recognizer.py'],
  ['../python/antlr4/RuleContext.py',          '/home/pyodide/antlr4/RuleContext.py'],
  ['../python/antlr4/StdinStream.py',          '/home/pyodide/antlr4/StdinStream.py'],
  ['../python/antlr4/Token.py',                '/home/pyodide/antlr4/Token.py'],
  ['../python/antlr4/TokenStreamRewriter.py',  '/home/pyodide/antlr4/TokenStreamRewriter.py'],
  ['../python/antlr4/Utils.py',                '/home/pyodide/antlr4/Utils.py'],
  ['../python/antlr4/atn/__init__.py',         '/home/pyodide/antlr4/atn/__init__.py'],
  ['../python/antlr4/atn/ATN.py',              '/home/pyodide/antlr4/atn/ATN.py'],
  ['../python/antlr4/atn/ATNConfig.py',        '/home/pyodide/antlr4/atn/ATNConfig.py'],
  ['../python/antlr4/atn/ATNConfigSet.py',     '/home/pyodide/antlr4/atn/ATNConfigSet.py'],
  ['../python/antlr4/atn/ATNDeserializationOptions.py', '/home/pyodide/antlr4/atn/ATNDeserializationOptions.py'],
  ['../python/antlr4/atn/ATNDeserializer.py',  '/home/pyodide/antlr4/atn/ATNDeserializer.py'],
  ['../python/antlr4/atn/ATNSimulator.py',     '/home/pyodide/antlr4/atn/ATNSimulator.py'],
  ['../python/antlr4/atn/ATNState.py',         '/home/pyodide/antlr4/atn/ATNState.py'],
  ['../python/antlr4/atn/ATNType.py',          '/home/pyodide/antlr4/atn/ATNType.py'],
  ['../python/antlr4/atn/LexerATNSimulator.py', '/home/pyodide/antlr4/atn/LexerATNSimulator.py'],
  ['../python/antlr4/atn/LexerAction.py',      '/home/pyodide/antlr4/atn/LexerAction.py'],
  ['../python/antlr4/atn/LexerActionExecutor.py', '/home/pyodide/antlr4/atn/LexerActionExecutor.py'],
  ['../python/antlr4/atn/ParserATNSimulator.py', '/home/pyodide/antlr4/atn/ParserATNSimulator.py'],
  ['../python/antlr4/atn/PredictionMode.py',  '/home/pyodide/antlr4/atn/PredictionMode.py'],
  ['../python/antlr4/atn/SemanticContext.py',  '/home/pyodide/antlr4/atn/SemanticContext.py'],
  ['../python/antlr4/atn/Transition.py',       '/home/pyodide/antlr4/atn/Transition.py'],
  ['../python/antlr4/dfa/__init__.py',         '/home/pyodide/antlr4/dfa/__init__.py'],
  ['../python/antlr4/dfa/DFA.py',              '/home/pyodide/antlr4/dfa/DFA.py'],
  ['../python/antlr4/dfa/DFASerializer.py',    '/home/pyodide/antlr4/dfa/DFASerializer.py'],
  ['../python/antlr4/dfa/DFAState.py',         '/home/pyodide/antlr4/dfa/DFAState.py'],
  ['../python/antlr4/error/__init__.py',       '/home/pyodide/antlr4/error/__init__.py'],
  ['../python/antlr4/error/DiagnosticErrorListener.py', '/home/pyodide/antlr4/error/DiagnosticErrorListener.py'],
  ['../python/antlr4/error/ErrorListener.py',  '/home/pyodide/antlr4/error/ErrorListener.py'],
  ['../python/antlr4/error/ErrorStrategy.py',  '/home/pyodide/antlr4/error/ErrorStrategy.py'],
  ['../python/antlr4/error/Errors.py',         '/home/pyodide/antlr4/error/Errors.py'],
  ['../python/antlr4/tree/__init__.py',        '/home/pyodide/antlr4/tree/__init__.py'],
  ['../python/antlr4/tree/Chunk.py',           '/home/pyodide/antlr4/tree/Chunk.py'],
  ['../python/antlr4/tree/ParseTreeMatch.py',  '/home/pyodide/antlr4/tree/ParseTreeMatch.py'],
  ['../python/antlr4/tree/ParseTreePattern.py', '/home/pyodide/antlr4/tree/ParseTreePattern.py'],
  ['../python/antlr4/tree/ParseTreePatternMatcher.py', '/home/pyodide/antlr4/tree/ParseTreePatternMatcher.py'],
  ['../python/antlr4/tree/RuleTagToken.py',    '/home/pyodide/antlr4/tree/RuleTagToken.py'],
  ['../python/antlr4/tree/TokenTagToken.py',   '/home/pyodide/antlr4/tree/TokenTagToken.py'],
  ['../python/antlr4/tree/Tree.py',            '/home/pyodide/antlr4/tree/Tree.py'],
  ['../python/antlr4/tree/Trees.py',           '/home/pyodide/antlr4/tree/Trees.py'],
  ['../python/antlr4/xpath/__init__.py',       '/home/pyodide/antlr4/xpath/__init__.py'],
  ['../python/antlr4/xpath/XPath.py',          '/home/pyodide/antlr4/xpath/XPath.py'],
  // training parser modules (../../ because worker is in mobile-app/src/)
  ['/parser/__init__.py',           '/home/pyodide/parser/__init__.py'],
  ['/parser/model.py',              '/home/pyodide/parser/model.py'],
  ['/parser/parser.py',             '/home/pyodide/parser/parser.py'],
  ['/parser/standardize_name.py',   '/home/pyodide/parser/standardize_name.py'],
  ['/parser/serializer.py',         '/home/pyodide/parser/serializer.py'],
  ['/parser/error_listener.py',     '/home/pyodide/parser/error_listener.py'],
  ['/parser/series_builder.py',     '/home/pyodide/parser/series_builder.py'],
  ['/src/__init__.py',              '/home/pyodide/src/__init__.py'],
  ['/src/data_access.py',           '/home/pyodide/src/data_access.py'],
  ['/src/statistics.py',            '/home/pyodide/src/statistics.py'],
  ['/dist/__init__.py',             '/home/pyodide/dist/__init__.py'],
  ['/dist/trainingLexer.py',        '/home/pyodide/dist/trainingLexer.py'],
  ['/dist/trainingParser.py',       '/home/pyodide/dist/trainingParser.py'],
  ['/dist/trainingListener.py',     '/home/pyodide/dist/trainingListener.py'],
  ['/dist/trainingVisitor.py',      '/home/pyodide/dist/trainingVisitor.py'],
  ['/data/synonyms.yaml',           '/home/pyodide/data/synonyms.yaml'],
  ['../python/app_api.py',             '/home/pyodide/app_api.py'],
];

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

  // Create directories in Pyodide FS with error handling
  const dirs = ['/home/pyodide/parser', '/home/pyodide/src', '/home/pyodide/dist', '/home/pyodide/data', '/home/pyodide/antlr4'];
  for (const dir of dirs) {
    try {
      pyodide.FS.mkdir(dir);
    } catch (e) {
      if (!e.message.includes('already exists')) {
        log(`Failed to create ${dir}: ${e.message}`, 'WARN');
      }
    }
  }
  log('Directories created', 'DEBUG');

  // Write empty __init__.py for packages that don't have one on disk
  const emptyInit = '';
  try { pyodide.FS.writeFile('/home/pyodide/src/__init__.py', emptyInit, { encoding: 'utf8' }); } catch {}
  try { pyodide.FS.writeFile('/home/pyodide/dist/__init__.py', emptyInit, { encoding: 'utf8' }); } catch {}

  // Helper to ensure parent directories exist
  function ensureParentDir(fsPath) {
    const parts = fsPath.split('/').filter(p => p);
    let currentPath = '';
    for (const part of parts.slice(0, -1)) {
      currentPath += '/' + part;
      try {
        pyodide.FS.mkdir(currentPath);
      } catch (e) {
        // Directory likely already exists
      }
    }
  }

  // Fetch and write each Python source file
  log(`Fetching ${PYTHON_FILES.length} Python files...`, 'INFO');
  self.postMessage({ type: 'loading', message: `Loading files (0/${PYTHON_FILES.length})...` });

  const failedFiles = [];
  let successCount = 0;

  // Log sample of what we're loading
  log(`Sample files: ${PYTHON_FILES.slice(0, 3).map(f => f[0]).join(', ')}...`, 'DEBUG');

  for (let idx = 0; idx < PYTHON_FILES.length; idx++) {
    const [fetchPath, fsPath] = PYTHON_FILES[idx];
    try {
      let resp;
      try {
        resp = await fetch(fetchPath);
      } catch (fetchErr) {
        throw new Error(`Network error: ${fetchErr.message}`);
      }

      if (resp.ok) {
        let text;
        try {
          text = await resp.text();
        } catch (readErr) {
          throw new Error(`Failed to read response: ${readErr.message}`);
        }

        try {
          ensureParentDir(fsPath);
          pyodide.FS.writeFile(fsPath, text, { encoding: 'utf8' });
          successCount++;

          // Log progress every 10 files and first/last file
          if (successCount === 1 || successCount % 10 === 0 || successCount === PYTHON_FILES.length) {
            log(`Written ${successCount}/${PYTHON_FILES.length}: ${fsPath} (${text.length} bytes)`, 'DEBUG');
            self.postMessage({ type: 'loading', message: `Loading files (${successCount}/${PYTHON_FILES.length})...` });
          }
        } catch (writeErr) {
          failedFiles.push(`${fetchPath} (write failed: ${writeErr.message})`);
          log(`Failed to write ${fsPath}: ${writeErr.message}`, 'ERROR');
        }
      } else {
        failedFiles.push(`${fetchPath} (HTTP ${resp.status})`);
        log(`Failed to fetch ${fetchPath}: HTTP ${resp.status}`, 'ERROR');
      }
    } catch (e) {
      failedFiles.push(fetchPath);
      log(`Could not load ${fetchPath}: ${e.message}`, 'ERROR');
    }
  }
  log(`Loaded ${successCount}/${PYTHON_FILES.length} files`, 'INFO');
  if (failedFiles.length > 0) {
    log(`${failedFiles.length} file(s) failed: ${failedFiles.slice(0, 5).join(', ')}${failedFiles.length > 5 ? '...' : ''}`, 'WARN');
  }

  // List what's actually in /home/pyodide to verify files were written
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
    'parser': os.path.exists('/home/pyodide/parser/__init__.py'),
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
