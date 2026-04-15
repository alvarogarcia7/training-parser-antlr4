# Language Server Protocol (LSP) Features

The training-parser now includes a full-featured Language Server Protocol implementation, bringing IDE-like features to your training log editor.

## 🚀 Quick Start

```bash
# Install
uv pip install -e ".[dev]"

# Run the server
training-lsp
```

See [LSP_GUIDE.md](LSP_GUIDE.md) for detailed setup instructions.

## ✨ Features

### 1. Real-time Diagnostics
Instant syntax validation with error highlighting.

```
Bench press 75k @#$
                ^^^
                Error: extraneous input '@'
```

### 2. Intelligent Auto-Completion
Context-aware suggestions for exercises and notation patterns.

- **Exercise names**: `Ben` → `Bench press:`
- **Notation patterns**: After `:` → `3x8x75k`, `75k: 3x8`, `8xx60k,70k`

### 3. Rich Hover Information
Detailed information on hover:

- Exercise statistics (sets, volume, breakdown)
- Notation pattern explanations
- Quick syntax reference

### 4. Code Formatting
Automatic formatting for consistent style:
- Adds spaces after colons
- Normalizes comma spacing
- Removes extra whitespace

### 5. Semantic Syntax Highlighting
Precise colorization of:
- Exercise names
- Numbers (sets, reps, weights)
- Operators (`x`, `xx`, `:`)
- Units (`k`)

### 6. Code Actions & Quick Fixes
One-click fixes for:
- Missing colons
- Spacing issues
- Notation conversions

## 🎯 Supported Editors

- ✅ **Visual Studio Code** (via extension)
- ✅ **Neovim** (via nvim-lspconfig or coc.nvim)
- ✅ **Emacs** (via lsp-mode or eglot)
- ✅ **Vim** (via vim-lsp)
- ✅ **Sublime Text** (via LSP package)
- ✅ Any editor with LSP support

## 📦 What's Included

```
lsp/
├── server.py           # Main LSP server
├── diagnostics.py      # Syntax error detection
├── completion.py       # Auto-completion
├── hover.py           # Hover information
├── formatting.py      # Code formatting
├── semantic_tokens.py # Syntax highlighting
├── code_actions.py    # Quick fixes
├── test_lsp.py        # Test suite
└── vscode-extension/  # VS Code extension
```

## 🔧 Architecture

```
Editor ←→ LSP Protocol ←→ training-lsp ←→ ANTLR Parser
                               ↓
                          Feature Providers:
                          • Diagnostics
                          • Completion
                          • Hover
                          • Formatting
                          • Semantic Tokens
                          • Code Actions
```

## 📚 Documentation

- **[LSP_GUIDE.md](LSP_GUIDE.md)** - Complete setup and usage guide
- **[lsp/README.md](lsp/README.md)** - Developer documentation
- **[lsp/QUICKSTART.md](lsp/QUICKSTART.md)** - 5-minute quick start

## 🎓 Example

Create `workout.training`:

```training
Bench press: 3x8x75k
Squat: 5x10x100k
Overhead press: 5x5x40k
Deadlift 60k: 20, 15, 8, 8
```

Open in your LSP-enabled editor to experience:
- Syntax highlighting
- Hover over exercises for details
- Type `Dead` for auto-completion
- Format the document
- Get instant error feedback

## 🛠️ Development

Run tests:
```bash
pytest lsp/
```

Test manually:
```bash
python lsp/example_usage.py
```

Add custom features by extending the providers in `lsp/`.

## 📄 License

Same as the training-parser project.

---

**Ready to enhance your training log editing experience? See [LSP_GUIDE.md](LSP_GUIDE.md) to get started!**
