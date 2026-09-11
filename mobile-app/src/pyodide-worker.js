/* Pyodide Web Worker — loads Python runtime and exposes parse/stats API */

const START_TIME = performance.now();
const LOG_LEVELS = { DEBUG: 0, INFO: 1, WARN: 2, ERROR: 3 };

function log(msg, level = 'INFO') {
  const elapsed = (performance.now() - START_TIME).toFixed(0);
  const prefix = `[pyodide ${elapsed}ms]`;
  const levelStr = level.padEnd(5);
  console.log(`${prefix} ${levelStr} ${msg}`);
  self.postMessage({ type: 'log', message: msg, level, elapsed: parseInt(elapsed) });
}

importScripts('https://cdn.jsdelivr.net/pyodide/v0.27.0/full/pyodide.js');

let pyodide = null;
log('Script imported', 'DEBUG');

const PYTHON_FILES = [
  // [fetch_path, pyodide_fs_path]
  // antlr4 runtime (bundled in mobile-app/python)
  ['./python/antlr4/__init__.py',             '/home/pyodide/antlr4/__init__.py'],
  ['./python/antlr4/BufferedTokenStream.py',  '/home/pyodide/antlr4/BufferedTokenStream.py'],
  ['./python/antlr4/CommonTokenFactory.py',   '/home/pyodide/antlr4/CommonTokenFactory.py'],
  ['./python/antlr4/CommonTokenStream.py',    '/home/pyodide/antlr4/CommonTokenStream.py'],
  ['./python/antlr4/FileStream.py',           '/home/pyodide/antlr4/FileStream.py'],
  ['./python/antlr4/InputStream.py',          '/home/pyodide/antlr4/InputStream.py'],
  ['./python/antlr4/IntervalSet.py',          '/home/pyodide/antlr4/IntervalSet.py'],
  ['./python/antlr4/LL1Analyzer.py',          '/home/pyodide/antlr4/LL1Analyzer.py'],
  ['./python/antlr4/Lexer.py',                '/home/pyodide/antlr4/Lexer.py'],
  ['./python/antlr4/ListTokenSource.py',      '/home/pyodide/antlr4/ListTokenSource.py'],
  ['./python/antlr4/Parser.py',               '/home/pyodide/antlr4/Parser.py'],
  ['./python/antlr4/ParserInterpreter.py',    '/home/pyodide/antlr4/ParserInterpreter.py'],
  ['./python/antlr4/ParserRuleContext.py',    '/home/pyodide/antlr4/ParserRuleContext.py'],
  ['./python/antlr4/PredictionContext.py',    '/home/pyodide/antlr4/PredictionContext.py'],
  ['./python/antlr4/Recognizer.py',           '/home/pyodide/antlr4/Recognizer.py'],
  ['./python/antlr4/RuleContext.py',          '/home/pyodide/antlr4/RuleContext.py'],
  ['./python/antlr4/StdinStream.py',          '/home/pyodide/antlr4/StdinStream.py'],
  ['./python/antlr4/Token.py',                '/home/pyodide/antlr4/Token.py'],
  ['./python/antlr4/TokenStreamRewriter.py',  '/home/pyodide/antlr4/TokenStreamRewriter.py'],
  ['./python/antlr4/Utils.py',                '/home/pyodide/antlr4/Utils.py'],
  ['./python/antlr4/atn/__init__.py',         '/home/pyodide/antlr4/atn/__init__.py'],
  ['./python/antlr4/atn/ATN.py',              '/home/pyodide/antlr4/atn/ATN.py'],
  ['./python/antlr4/atn/ATNConfig.py',        '/home/pyodide/antlr4/atn/ATNConfig.py'],
  ['./python/antlr4/atn/ATNConfigSet.py',     '/home/pyodide/antlr4/atn/ATNConfigSet.py'],
  ['./python/antlr4/atn/ATNDeserializationOptions.py', '/home/pyodide/antlr4/atn/ATNDeserializationOptions.py'],
  ['./python/antlr4/atn/ATNDeserializer.py',  '/home/pyodide/antlr4/atn/ATNDeserializer.py'],
  ['./python/antlr4/atn/ATNSimulator.py',     '/home/pyodide/antlr4/atn/ATNSimulator.py'],
  ['./python/antlr4/atn/ATNState.py',         '/home/pyodide/antlr4/atn/ATNState.py'],
  ['./python/antlr4/atn/ATNType.py',          '/home/pyodide/antlr4/atn/ATNType.py'],
  ['./python/antlr4/atn/LexerATNSimulator.py', '/home/pyodide/antlr4/atn/LexerATNSimulator.py'],
  ['./python/antlr4/atn/LexerAction.py',      '/home/pyodide/antlr4/atn/LexerAction.py'],
  ['./python/antlr4/atn/LexerActionExecutor.py', '/home/pyodide/antlr4/atn/LexerActionExecutor.py'],
  ['./python/antlr4/atn/ParserATNSimulator.py', '/home/pyodide/antlr4/atn/ParserATNSimulator.py'],
  ['./python/antlr4/atn/PredictionMode.py',  '/home/pyodide/antlr4/atn/PredictionMode.py'],
  ['./python/antlr4/atn/SemanticContext.py',  '/home/pyodide/antlr4/atn/SemanticContext.py'],
  ['./python/antlr4/atn/Transition.py',       '/home/pyodide/antlr4/atn/Transition.py'],
  ['./python/antlr4/dfa/__init__.py',         '/home/pyodide/antlr4/dfa/__init__.py'],
  ['./python/antlr4/dfa/DFA.py',              '/home/pyodide/antlr4/dfa/DFA.py'],
  ['./python/antlr4/dfa/DFASerializer.py',    '/home/pyodide/antlr4/dfa/DFASerializer.py'],
  ['./python/antlr4/dfa/DFAState.py',         '/home/pyodide/antlr4/dfa/DFAState.py'],
  ['./python/antlr4/error/__init__.py',       '/home/pyodide/antlr4/error/__init__.py'],
  ['./python/antlr4/error/DiagnosticErrorListener.py', '/home/pyodide/antlr4/error/DiagnosticErrorListener.py'],
  ['./python/antlr4/error/ErrorListener.py',  '/home/pyodide/antlr4/error/ErrorListener.py'],
  ['./python/antlr4/error/ErrorStrategy.py',  '/home/pyodide/antlr4/error/ErrorStrategy.py'],
  ['./python/antlr4/error/Errors.py',         '/home/pyodide/antlr4/error/Errors.py'],
  ['./python/antlr4/tree/__init__.py',        '/home/pyodide/antlr4/tree/__init__.py'],
  ['./python/antlr4/tree/Chunk.py',           '/home/pyodide/antlr4/tree/Chunk.py'],
  ['./python/antlr4/tree/ParseTreeMatch.py',  '/home/pyodide/antlr4/tree/ParseTreeMatch.py'],
  ['./python/antlr4/tree/ParseTreePattern.py', '/home/pyodide/antlr4/tree/ParseTreePattern.py'],
  ['./python/antlr4/tree/ParseTreePatternMatcher.py', '/home/pyodide/antlr4/tree/ParseTreePatternMatcher.py'],
  ['./python/antlr4/tree/RuleTagToken.py',    '/home/pyodide/antlr4/tree/RuleTagToken.py'],
  ['./python/antlr4/tree/TokenTagToken.py',   '/home/pyodide/antlr4/tree/TokenTagToken.py'],
  ['./python/antlr4/tree/Tree.py',            '/home/pyodide/antlr4/tree/Tree.py'],
  ['./python/antlr4/tree/Trees.py',           '/home/pyodide/antlr4/tree/Trees.py'],
  ['./python/antlr4/xpath/__init__.py',       '/home/pyodide/antlr4/xpath/__init__.py'],
  ['./python/antlr4/xpath/XPath.py',          '/home/pyodide/antlr4/xpath/XPath.py'],
  // training parser modules
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
  log('initPyodide started', 'INFO');
  self.postMessage({ type: 'loading', message: 'Loading Python runtime...' });

  log('loadPyodide() starting...', 'DEBUG');
  pyodide = await loadPyodide();
  log(`loadPyodide() done - ${pyodide ? 'success' : 'failed'}`, 'INFO');

  log('loadPackage(pyyaml) starting...', 'DEBUG');
  self.postMessage({ type: 'loading', message: 'Loading packages...' });
  await pyodide.loadPackage(['pyyaml']);
  log('loadPackage done', 'DEBUG');

  self.postMessage({ type: 'loading', message: 'Loading parser modules...' });
  log('Creating directories...', 'DEBUG');

  // Create directories in Pyodide FS
  pyodide.FS.mkdir('/home/pyodide/parser');
  pyodide.FS.mkdir('/home/pyodide/src');
  pyodide.FS.mkdir('/home/pyodide/dist');
  pyodide.FS.mkdir('/home/pyodide/data');
  log('Directories created', 'DEBUG');

  // Write empty __init__.py for packages that don't have one on disk
  const emptyInit = '';
  try { pyodide.FS.writeFile('/home/pyodide/src/__init__.py', emptyInit, { encoding: 'utf8' }); } catch {}
  try { pyodide.FS.writeFile('/home/pyodide/dist/__init__.py', emptyInit, { encoding: 'utf8' }); } catch {}

  // Fetch and write each Python source file
  log(`Fetching ${PYTHON_FILES.length} Python files...`, 'DEBUG');
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
  log('All Python files written', 'DEBUG');

  // Put our source root on the Python path
  log('Setting Python path...', 'DEBUG');
  pyodide.runPython(`
import sys
sys.path.insert(0, '/home/pyodide')
print('Path updated')
`);
  log('Python path set', 'DEBUG');

  log('Testing imports...', 'DEBUG');
  try {
    // Test antlr4 import first (needed by app_api.py)
    pyodide.runPython('import antlr4; print("✓ antlr4 available")');
    log('antlr4 available', 'INFO');
  } catch (e) {
    log(`antlr4 not available: ${e.message}`, 'WARN');
  }

  try {
    pyodide.runPython('import app_api; print("✓ app_api loaded")');
    log('app_api imported successfully', 'INFO');
  } catch (e) {
    log(`app_api import failed: ${e.message}`, 'ERROR');
    self.postMessage({ type: 'error', message: `Python initialization failed: ${e.message}. antlr4 may not be available in Pyodide.` });
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

// Auto-start
log('Worker script loaded, auto-starting initPyodide...', 'DEBUG');
initPyodide().catch(e => {
  log(`initPyodide failed: ${e.message}`, 'ERROR');
  self.postMessage({ type: 'error', message: 'Failed to initialize: ' + e.message });
});
