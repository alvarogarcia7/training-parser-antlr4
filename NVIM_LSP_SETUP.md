# Neovim LSP Configuration Guide

## Overview

The training parser LSP (Language Server Protocol) has been successfully configured for Neovim. This enables real-time error checking, code completion, hover information, and code actions for training workout files.

## ✅ Configuration Status

### What Has Been Done

1. **Project Setup**
   - Virtual environment created with `uv venv`
   - All dependencies installed via `uv sync --all-extras`
   - ANTLR grammar compiled to generate parser

2. **LSP Installation**
   - `training-lsp` command installed in `.venv/bin/`
   - All LSP features available and functional

3. **Neovim Configuration**
   - `~/.config/nvim/init.lua` configured with `nvim-lspconfig`
   - Training LSP server registered and auto-starts for training files
   - File type auto-detection configured for:
     - `*.training`
     - `*.workout`
     - `training*.txt`

4. **LSP Features Enabled**
   - ✅ Diagnostics (error checking)
   - ✅ Completions (exercise names, notation patterns)
   - ✅ Hover information (set breakdowns, pattern documentation)
   - ✅ Code actions (quick fixes)
   - ✅ Formatting (spacing normalization)
   - ✅ Semantic tokens (syntax highlighting)

## 🚀 How to Use

### Starting Neovim with the LSP

```bash
# Option 1: Set VIRTUAL_ENV before launching nvim
export VIRTUAL_ENV="/path/to/project/.venv"
nvim your_workout.training

# Option 2: Activate venv first
source /path/to/project/.venv/bin/activate
nvim your_workout.training
```

### Keybindings

Once a training file is open in Neovim:

| Keybinding | Action |
|-----------|--------|
| `K` | Show hover information (set breakdown, syntax help) |
| `gd` | Go to definition |
| `<space>f` | Format document |
| `<space>ca` | Code actions (quick fixes) |
| `<c-x><c-o>` | Trigger completions (omnifunc) |

### LSP Status

Check LSP connection and status:

```vim
:LspInfo
```

Restart LSP:

```vim
:LspRestart
```

## 🧪 Verification

### Test with Invalid Dataset

A test file with intentional errors has been created to verify error detection:

```bash
# Create and test with invalid workout data
nvim /tmp/test_invalid.training
```

**Test file content:**
```
Bench press: 3x8x75k         ✓ Valid
Squat 5x10x100k              ✗ Missing colon
Deadlift: invalid @#$        ✗ Invalid characters and syntax
Overhead press: 5x5x40k @invalid  ✗ Invalid suffix
Pull-up: 3x max reps 50k     ✗ Invalid notation
```

### Expected Errors

When opening the test file, you should see **7 diagnostic errors**:

1. **Line 2**: Missing colon after exercise name
2. **Line 3**: Token recognition errors for `@`, `#`, `$`
3. **Line 3**: Mismatched input 'invalid' (expecting number)
4. **Line 3**: Mismatched input at end of line
5. **Line 4**: Token recognition error for `@`
6. **Line 4**: Mismatched input at end of line
7. **Line 5**: Invalid 'max reps' notation

### Direct Diagnostics Test

To test the diagnostics module without Neovim:

```bash
# Activate virtual environment
source .venv/bin/activate

# Run diagnostics test
python /tmp/test_diagnostics.py
```

### Launch Test Script

A convenient test script is available:

```bash
bash /tmp/launch_nvim_test.sh
```

This script:
- Activates the virtual environment
- Sets up required environment variables
- Creates test file with errors
- Shows detected errors
- Launches Neovim

## 📁 Project Structure

### LSP-Related Files

```
lsp/
├── server.py              # Main LSP server implementation
├── cli.py                 # Command-line interface for training-lsp
├── client.py              # LSP client implementation
├── diagnostics.py         # Error detection and reporting
├── completion.py          # Auto-completion suggestions
├── hover.py              # Hover information provider
├── code_actions.py       # Quick fixes and refactorings
├── formatting.py         # Document formatting
├── semantic_tokens.py    # Syntax highlighting tokens
└── vscode-extension/     # VS Code extension (optional)
```

### Neovim Configuration

```
~/.config/nvim/
└── init.lua              # Main configuration with LSP setup
```

## 🔧 Configuration Details

### Neovim LSP Setup

The configuration in `~/.config/nvim/init.lua` does the following:

1. **Installs lazy.nvim** - Plugin manager
2. **Adds nvim-lspconfig** - LSP configuration plugin
3. **Registers training_lsp** - Custom LSP configuration
4. **Sets up auto-commands** - Auto-detects training files
5. **Binds keymaps** - Convenient LSP shortcuts

### Virtual Environment Detection

The LSP command path is determined by:

```lua
local venv_path = os.getenv("VIRTUAL_ENV") or vim.fn.expand("~/.venv")
local training_lsp_cmd = venv_path .. "/bin/training-lsp"
```

**Make sure to set `VIRTUAL_ENV`** when launching Neovim if using a non-standard path:

```bash
export VIRTUAL_ENV="/path/to/project/.venv"
nvim file.training
```

## 🐛 Troubleshooting

### LSP Not Starting

**Check if training-lsp is installed:**

```bash
source .venv/bin/activate
which training-lsp
# Should output: /path/to/.venv/bin/training-lsp
```

**If not found, reinstall:**

```bash
source .venv/bin/activate
uv pip install -e ".[dev]"
```

### No Diagnostics Appearing

1. Check file is recognized as training type:
   ```vim
   :set filetype?
   # Should show: filetype=training
   ```

2. Check LSP is connected:
   ```vim
   :LspInfo
   ```

3. Reload file:
   ```vim
   :e!
   ```

### Grammar Not Compiled

Recompile the ANTLR grammar:

```bash
source .venv/bin/activate
make compile-grammar
```

## 📖 Additional Resources

- **LSP Guide**: See `LSP_GUIDE.md` for detailed documentation
- **LSP Features**: See `LSP_FEATURES.md` for feature details
- **LSP Implementation**: See `LSP_IMPLEMENTATION_SUMMARY.md` for technical details

## ⚙️ Environment Setup

To fully activate the development environment with LSP:

```bash
# One-time setup
bash setup-uv.sh

# Subsequent sessions
source .venv/bin/activate
export VIRTUAL_ENV="$PWD/.venv"
nvim
```

Or add to your shell profile:

```bash
# ~/.bashrc or ~/.zshrc
alias nvim-training='export VIRTUAL_ENV="/path/to/project/.venv" && nvim'
```

Then use:

```bash
nvim-training file.training
```

## 🎯 Next Steps

1. Open a training file: `nvim test.training`
2. Create a file with errors to see diagnostics
3. Use hover (`K`) to see error details
4. Use code actions (`<space>ca`) for quick fixes
5. Test completion with `<c-x><c-o>`

---

**Configuration Date**: April 27, 2026
**Status**: ✅ Verified and Operational
