# Training Language Server Protocol (LSP)

A Language Server Protocol implementation for the training workout Domain-Specific Language (DSL).

## Features

### 1. **Diagnostics (Error Checking)**
- Real-time syntax validation
- Instant feedback on parsing errors
- Error highlighting in the editor

### 2. **Code Completion**
- Exercise name suggestions
- Set notation pattern snippets
- Context-aware completions

### 3. **Hover Information**
- Exercise details (sets, volume, breakdown)
- Notation pattern explanations
- Quick reference documentation

### 4. **Document Formatting**
- Automatic code formatting
- Consistent spacing around operators
- Standardized colon usage

### 5. **Semantic Syntax Highlighting**
- Exercise names highlighted as classes
- Numbers highlighted distinctly
- Operators (x, xx, :) clearly marked
- Weight units (k) specially colored

### 6. **Code Actions (Quick Fixes)**
- Add missing colons after exercise names
- Fix spacing around operators
- Convert between notation styles (e.g., `75k: 3x8` → `3x8x75k`)

## Installation

The LSP server is installed automatically with the training-parser package:

```bash
uv pip install -e ".[dev]"
```

Or with pip:

```bash
pip install -e ".[dev]"
```

## Usage

### Running the Server

Start the language server:

```bash
training-lsp
```

The server communicates via stdin/stdout using the Language Server Protocol.

### Editor Integration

#### Visual Studio Code

Create or edit `.vscode/settings.json`:

```json
{
  "training-lsp.enable": true,
  "training-lsp.server.path": "training-lsp"
}
```

You can also create a VSCode extension for better integration. See the example extension configuration in `lsp/vscode-extension/`.

#### Neovim

Using `nvim-lspconfig`:

```lua
local lspconfig = require('lspconfig')
local configs = require('lspconfig.configs')

-- Define the training LSP configuration
if not configs.training_lsp then
  configs.training_lsp = {
    default_config = {
      cmd = {'training-lsp'},
      filetypes = {'training'},
      root_dir = lspconfig.util.root_pattern('.git'),
      settings = {},
    },
  }
end

-- Setup the LSP
lspconfig.training_lsp.setup{}

-- Set filetype for .txt files containing training logs
vim.api.nvim_create_autocmd({"BufRead", "BufNewFile"}, {
  pattern = {"training*.txt", "*-training.txt"},
  command = "set filetype=training",
})
```

#### Emacs

Using `lsp-mode`:

```elisp
(require 'lsp-mode)

(add-to-list 'lsp-language-id-configuration '(training-mode . "training"))

(lsp-register-client
 (make-lsp-client
  :new-connection (lsp-stdio-connection "training-lsp")
  :major-modes '(training-mode)
  :server-id 'training-lsp))

(add-hook 'training-mode-hook #'lsp)
```

#### Other Editors

Any editor that supports LSP can use this server. Configure your editor to:
1. Run `training-lsp` command for files matching training patterns
2. Use stdin/stdout for communication
3. Enable LSP features (completion, diagnostics, hover, etc.)

## Features in Detail

### Diagnostics

The server validates your training logs in real-time and reports errors:

```
Bench press 75k 4, 4x5   # Missing colon - diagnostic shown
                ↑
Error: mismatched input '4' expecting {<EOF>, NEWLINE}
```

### Completion

Type to get intelligent suggestions:

```
Ben<cursor>  →  Shows: Bench press, Bench press (incline), ...
```

After typing an exercise and colon:

```
Bench press: <cursor>  →  Shows: 3x8x75k, 75k: 3x8, 75k: 8,7,6, ...
```

### Hover

Hover over an exercise line to see detailed information:

```
Bench press 75k: 3x8

Hover shows:
━━━━━━━━━━━━━━━━━━━━━
**Bench press**

**Sets:** 3
**Total Volume:** 1800.0 kg

**Set Breakdown:**
- Set 1: 8 reps @ 75kg
- Set 2: 8 reps @ 75kg
- Set 3: 8 reps @ 75kg
━━━━━━━━━━━━━━━━━━━━━
```

Hover over notation patterns for syntax help:

```
3x8x75k

Hover shows:
━━━━━━━━━━━━━━━━━━━━━
**Whole Set Notation**

`3x8x75k` = 3 sets of 8 reps at 75kg

This is the most compact notation
for recording consistent sets.
━━━━━━━━━━━━━━━━━━━━━
```

### Code Actions

Select a line to see available quick fixes and refactorings:

1. **Add missing colon:**
   ```
   Bench press 75k 3x8
   → Bench press 75k: 3x8
   ```

2. **Fix spacing:**
   ```
   Bench press:3x8x75k
   → Bench press: 3x8x75k
   ```

3. **Convert notation:**
   ```
   Bench press 75k: 3x8
   → Bench press: 3x8x75k
   ```

## Development

### Project Structure

```
lsp/
├── __init__.py          # Package initialization
├── server.py            # Main LSP server implementation
├── diagnostics.py       # Syntax error detection
├── completion.py        # Code completion provider
├── hover.py             # Hover information provider
├── formatting.py        # Document formatting
├── semantic_tokens.py   # Syntax highlighting tokens
├── code_actions.py      # Quick fixes and refactorings
└── README.md           # This file
```

### Adding New Features

1. **New completion items:** Edit `completion.py` and add to the appropriate list
2. **New diagnostics:** Extend `DiagnosticErrorListener` in `diagnostics.py`
3. **New code actions:** Add functions to `code_actions.py`
4. **New hover info:** Extend pattern matching in `hover.py`

### Testing

Run the LSP server manually to test:

```bash
echo '{"jsonrpc":"2.0","id":0,"method":"initialize","params":{}}' | training-lsp
```

Or use an LSP client testing tool like `lsp-devtools`.

## Troubleshooting

### Server not starting

Check that the command is in your PATH:

```bash
which training-lsp
```

If not found, ensure the package is installed:

```bash
uv pip install -e ".[dev]"
```

### No completions appearing

1. Verify the LSP is connected in your editor
2. Check that file type is correctly detected
3. Review editor LSP logs for connection errors

### Diagnostics not showing

1. Ensure document is saved (some editors require this)
2. Check that ANTLR grammar is compiled: `make compile-grammar`
3. Verify the `dist/` directory contains generated parser files

## Architecture

The LSP implementation follows this flow:

```
Editor ←→ LSP Protocol ←→ Training LSP Server ←→ ANTLR Parser
                              ↓
                         Feature Providers:
                         - Diagnostics
                         - Completion
                         - Hover
                         - Formatting
                         - Semantic Tokens
                         - Code Actions
```

### Key Components

1. **Server (`server.py`)**: Main entry point, handles LSP lifecycle and message routing
2. **Diagnostics (`diagnostics.py`)**: Uses ANTLR error listeners to capture parse errors
3. **Completion (`completion.py`)**: Provides context-aware suggestions
4. **Hover (`hover.py`)**: Shows information about exercises and notation
5. **Formatting (`formatting.py`)**: Formats documents to follow conventions
6. **Semantic Tokens (`semantic_tokens.py`)**: Provides fine-grained syntax highlighting
7. **Code Actions (`code_actions.py`)**: Offers quick fixes and refactorings

## Contributing

When adding new features:

1. Follow the existing code structure
2. Add type hints to all functions
3. Update this README with new features
4. Test with multiple editors if possible
5. Follow the project's mypy strict type checking

## License

Same as the training-parser project.
