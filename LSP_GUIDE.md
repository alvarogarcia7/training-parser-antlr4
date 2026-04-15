# Training Language Server Protocol Guide

This guide explains how to use and configure the Language Server Protocol (LSP) implementation for the training workout DSL.

## Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Editor Integration](#editor-integration)
  - [Visual Studio Code](#visual-studio-code)
  - [Neovim](#neovim)
  - [Emacs](#emacs)
  - [Other Editors](#other-editors)
- [Features](#features)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)

## Overview

The training language server provides intelligent editing features for workout log files, including:

- **Real-time error checking** - Instant feedback on syntax errors
- **Auto-completion** - Suggestions for exercise names and notation patterns
- **Hover documentation** - Information about exercises and syntax
- **Code formatting** - Automatic formatting for consistent style
- **Syntax highlighting** - Semantic colorization of workout logs
- **Quick fixes** - Automatic corrections for common issues

## Installation

### Prerequisites

- Python 3.12 or higher
- The training-parser package installed

### Install the LSP Server

Using uv (recommended):

```bash
# Install in development mode with LSP dependencies
uv pip install -e ".[dev]"
```

Using pip:

```bash
pip install -e ".[dev]"
```

Verify installation:

```bash
which training-lsp
# Should output: /path/to/.venv/bin/training-lsp (or similar)
```

Test the server:

```bash
training-lsp --version
# or
echo '{}' | training-lsp
# Server should start and wait for LSP messages
```

## Quick Start

### Command Line

Start the language server:

```bash
training-lsp
```

The server communicates via stdin/stdout using the LSP protocol. It's not meant to be used directly from the command line, but through an editor.

### Sample Workout File

Create a file named `workout.training`:

```
Bench press: 3x8x75k
Squat: 5x10x100k
Overhead press: 5x5x40k
```

Open it in your LSP-enabled editor to see features in action.

## Editor Integration

### Visual Studio Code

#### Option 1: Using the Extension (Recommended)

1. Install the extension from source:
   ```bash
   cd lsp/vscode-extension
   npm install
   npm run compile
   ```

2. Install in VS Code:
   - Open Command Palette (`Cmd+Shift+P` or `Ctrl+Shift+P`)
   - Run "Developer: Install Extension from Location"
   - Select the `lsp/vscode-extension` directory

3. Configure (optional) in `.vscode/settings.json`:
   ```json
   {
     "trainingLanguageServer.enable": true,
     "trainingLanguageServer.serverPath": "training-lsp"
   }
   ```

4. Open any `.training`, `.workout`, or `training*.txt` file

#### Option 2: Manual Configuration

Add to `.vscode/settings.json`:

```json
{
  "training.languageServer": {
    "enabled": true,
    "command": "training-lsp"
  }
}
```

### Neovim

#### Using nvim-lspconfig

Add to your Neovim configuration (`~/.config/nvim/init.lua` or `~/.config/nvim/lua/lsp.lua`):

```lua
local lspconfig = require('lspconfig')
local configs = require('lspconfig.configs')

-- Register training LSP
if not configs.training_lsp then
  configs.training_lsp = {
    default_config = {
      cmd = {'training-lsp'},
      filetypes = {'training'},
      root_dir = function(fname)
        return lspconfig.util.find_git_ancestor(fname) or vim.fn.getcwd()
      end,
      settings = {},
    },
  }
end

-- Setup the server
lspconfig.training_lsp.setup{
  on_attach = function(client, bufnr)
    -- Enable completion triggered by <c-x><c-o>
    vim.api.nvim_buf_set_option(bufnr, 'omnifunc', 'v:lua.vim.lsp.omnifunc')

    -- Keybindings (optional)
    local bufopts = { noremap=true, silent=true, buffer=bufnr }
    vim.keymap.set('n', 'gd', vim.lsp.buf.definition, bufopts)
    vim.keymap.set('n', 'K', vim.lsp.buf.hover, bufopts)
    vim.keymap.set('n', '<space>f', vim.lsp.buf.format, bufopts)
  end,
}

-- Auto-detect training files
vim.api.nvim_create_autocmd({"BufRead", "BufNewFile"}, {
  pattern = {"*.training", "*.workout", "training*.txt"},
  callback = function()
    vim.bo.filetype = "training"
  end,
})
```

#### Using coc.nvim

Add to `:CocConfig`:

```json
{
  "languageserver": {
    "training": {
      "command": "training-lsp",
      "filetypes": ["training"],
      "rootPatterns": [".git/"]
    }
  }
}
```

### Emacs

#### Using lsp-mode

Add to your Emacs configuration (`~/.emacs.d/init.el` or `~/.emacs`):

```elisp
(require 'lsp-mode)

;; Define training major mode
(define-derived-mode training-mode fundamental-mode "Training"
  "Major mode for editing training workout files."
  (setq-local comment-start "#"))

;; Associate file patterns with training-mode
(add-to-list 'auto-mode-alist '("\\.training\\'" . training-mode))
(add-to-list 'auto-mode-alist '("\\.workout\\'" . training-mode))
(add-to-list 'auto-mode-alist '("training.*\\.txt\\'" . training-mode))

;; Register training language with lsp-mode
(add-to-list 'lsp-language-id-configuration '(training-mode . "training"))

;; Register the training LSP client
(lsp-register-client
 (make-lsp-client
  :new-connection (lsp-stdio-connection "training-lsp")
  :major-modes '(training-mode)
  :server-id 'training-lsp))

;; Enable LSP in training-mode
(add-hook 'training-mode-hook #'lsp)
```

#### Using eglot

```elisp
(require 'eglot)

;; Define training major mode
(define-derived-mode training-mode fundamental-mode "Training"
  "Major mode for editing training workout files.")

;; Associate file patterns
(add-to-list 'auto-mode-alist '("\\.training\\'" . training-mode))
(add-to-list 'auto-mode-alist '("\\.workout\\'" . training-mode))

;; Add training LSP server
(add-to-list 'eglot-server-programs '(training-mode . ("training-lsp")))

;; Enable eglot in training-mode
(add-hook 'training-mode-hook #'eglot-ensure)
```

### Other Editors

Any editor with LSP support can use this server:

#### Sublime Text (LSP package)

Add to LSP settings:

```json
{
  "clients": {
    "training-lsp": {
      "enabled": true,
      "command": ["training-lsp"],
      "selector": "source.training"
    }
  }
}
```

#### Vim (using vim-lsp)

```vim
if executable('training-lsp')
    au User lsp_setup call lsp#register_server({
        \ 'name': 'training-lsp',
        \ 'cmd': {server_info->['training-lsp']},
        \ 'allowlist': ['training'],
        \ })
endif

autocmd BufNewFile,BufRead *.training,*.workout,training*.txt set filetype=training
```

## Features

### 1. Diagnostics (Error Checking)

Syntax errors are highlighted in real-time:

```
Bench press 75k 4, @#$
                   ^^^
                   Error: extraneous input '@'
```

The server validates:
- Exercise name syntax
- Notation pattern correctness
- Weight format
- Overall structure

### 2. Auto-Completion

**Exercise Names:**

Type the first few letters of an exercise:
```
Ben<Tab>
→ Bench press:
```

Available exercises include:
- Bench press, Squat, Deadlift, Overhead press
- Pull-up, Chin-up, Dips
- Barbell row, Dumbbell press
- And many more...

**Notation Patterns:**

After typing an exercise name and colon:
```
Bench press: <Tab>
```

Suggestions:
- `3x8x75k` - Whole set notation
- `75k: 3x8` - Group of reps
- `75k: 8,7,6` - Single rep notation
- `8xx60k,70k,80k` - Fixed reps, multiple weights

### 3. Hover Information

**On Exercise Lines:**

Hover over a complete exercise to see:
- Exercise name
- Number of sets
- Total volume
- Set-by-set breakdown

Example:
```
Bench press: 3x8x75k
             ↑ hover here

Shows:
━━━━━━━━━━━━━━━━━━━━
Bench press
Sets: 3
Total Volume: 1800.0 kg

Set Breakdown:
- Set 1: 8 reps @ 75kg
- Set 2: 8 reps @ 75kg
- Set 3: 8 reps @ 75kg
━━━━━━━━━━━━━━━━━━━━
```

**On Notation Patterns:**

Hover over specific patterns for syntax help:
```
3x8x75k
↑ hover here

Shows:
━━━━━━━━━━━━━━━━━━━━
Whole Set Notation
3x8x75k = 3 sets of 8 reps at 75kg
This is the most compact notation.
━━━━━━━━━━━━━━━━━━━━
```

### 4. Code Formatting

Format your document or selection:
- Adds spaces after colons
- Ensures consistent comma spacing
- Removes extra whitespace

**Before:**
```
Bench press:3x8x75k
Squat 70k:5x10
```

**After formatting:**
```
Bench press: 3x8x75k
Squat 70k: 5x10
```

### 5. Syntax Highlighting

Semantic tokens provide precise colorization:
- **Exercise names** - Highlighted as classes/types
- **Numbers** - Distinct color for reps, sets, weights
- **Operators** (x, xx, :) - Highlighted as keywords
- **Units** (k) - Special highlighting

### 6. Code Actions (Quick Fixes)

Select text or place cursor on a line to see available actions:

**Add Missing Colon:**
```
Bench press 75k 3x8
→ Quick Fix: Add colon after exercise name
→ Bench press 75k: 3x8
```

**Fix Spacing:**
```
Bench press:3x8x75k
→ Quick Fix: Fix colon spacing
→ Bench press: 3x8x75k
```

**Convert Notation:**
```
Bench press 75k: 3x8
→ Refactor: Convert to whole set notation
→ Bench press: 3x8x75k
```

## Configuration

### Server Settings

The LSP server can be configured through your editor's settings. Common options:

**Enable/Disable:**
```json
{
  "trainingLanguageServer.enable": true
}
```

**Server Path:**
```json
{
  "trainingLanguageServer.serverPath": "/custom/path/to/training-lsp"
}
```

**Trace Level:**
```json
{
  "trainingLanguageServer.trace.server": "verbose"
}
```

Options: `"off"`, `"messages"`, `"verbose"`

## Troubleshooting

### Server Not Starting

**Check if command is in PATH:**
```bash
which training-lsp
```

**If not found:**
- Ensure virtual environment is activated
- Check installation: `pip list | grep training-parser`
- Reinstall: `uv pip install -e ".[dev]"`

### No Completions Appearing

**Check:**
1. LSP server is connected (check editor status bar)
2. File is recognized as training type
3. Cursor is in valid position for completions

**Debug in editor:**
- VS Code: Check "Output" panel → "Training Language Server"
- Neovim: `:LspInfo` to see server status
- Emacs: `M-x lsp-describe-session`

### Diagnostics Not Showing

**Verify:**
1. ANTLR grammar is compiled: `make compile-grammar`
2. Check `dist/` directory exists with generated files
3. Try opening/closing the file
4. Check LSP server logs

**Recompile grammar:**
```bash
make compile-grammar
```

### Features Not Working

**Try:**
1. Restart LSP server (editor command varies)
2. Reload editor window
3. Check server logs for errors
4. Verify Python version: `python --version` (should be 3.12+)

**Test server manually:**
```bash
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}' | training-lsp
```

Should receive JSON response.

### Performance Issues

If the server is slow:
1. Reduce trace level to "off"
2. Check file size (very large files may be slow)
3. Ensure only one server instance is running

## Advanced Usage

### Custom Exercise Names

The server provides default exercise name completions, but you can add your own by editing `lsp/completion.py`:

```python
EXERCISE_NAMES = [
    "Bench press",
    "Your Custom Exercise",
    # ... more exercises
]
```

### Custom Diagnostics

To add custom validation rules, edit `lsp/diagnostics.py` and extend the `DiagnosticErrorListener` class.

### Custom Code Actions

Add new quick fixes by creating functions in `lsp/code_actions.py` following the existing patterns.

## Development

See `lsp/README.md` for detailed development information.

## Support

For issues, questions, or contributions:
1. Check this guide and `lsp/README.md`
2. Review existing issues in the project repository
3. Create a new issue with details about your setup and problem

## License

Same as the training-parser project.
