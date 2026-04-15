# Training LSP Quick Reference

## Commands

```bash
# Start LSP server (for editor integration)
training-lsp

# CLI commands
training-lsp-cli check <file>       # Check syntax
training-lsp-cli format <file>      # Format file
training-lsp-cli complete <text>    # Test completions
training-lsp-cli hover <file>       # Get hover info
training-lsp-cli stats <file>       # Show statistics
```

## Features at a Glance

| Feature | Trigger | What You Get |
|---------|---------|--------------|
| **Diagnostics** | On save/change | Red squiggles on errors |
| **Completion** | Type or `Ctrl+Space` | Exercise names, patterns |
| **Hover** | Mouse over | Stats, syntax help |
| **Formatting** | Format command | Consistent spacing |
| **Highlighting** | Automatic | Colored syntax |
| **Quick Fix** | Lightbulb icon | Fix spacing, add colons |

## Completion Examples

```
Ben<Tab>          → Bench press:
Bench press: <Tab> → 3x8x75k, 75k: 3x8, ...
```

## Notation Patterns

| Pattern | Example | Meaning |
|---------|---------|---------|
| Whole set | `3x8x75k` | 3 sets of 8 reps at 75kg |
| Group of reps | `75k: 3x8` | 3 sets of 8 reps at 75kg |
| Single reps | `75k: 8,7,6` | 3 sets with varying reps |
| Fixed reps | `8xx60k,70k` | 8 reps at different weights |

## Editor Shortcuts

### VS Code
- Completion: `Ctrl+Space`
- Hover: Mouse hover
- Format: `Shift+Alt+F`
- Quick Fix: `Ctrl+.`

### Neovim
- Completion: `Ctrl+X Ctrl+O` or plugin binding
- Hover: `K`
- Format: `:lua vim.lsp.buf.format()`
- Code Action: `:lua vim.lsp.buf.code_action()`

### Emacs
- Completion: `M-x completion-at-point`
- Hover: `M-x lsp-describe-thing-at-point`
- Format: `M-x lsp-format-buffer`
- Code Action: `M-x lsp-execute-code-action`

## Common Issues

**Server not starting?**
```bash
which training-lsp  # Check if installed
uv pip install -e ".[dev]"  # Reinstall
```

**No completions?**
- Check LSP is connected (status bar)
- Verify file type is detected
- Try manual trigger (Ctrl+Space)

**Errors not showing?**
```bash
make compile-grammar  # Recompile parser
```

## File Extensions

The LSP activates for:
- `*.training`
- `*.workout`
- `training*.txt`
- `*-training.txt`

## Configuration

### VS Code (settings.json)
```json
{
  "trainingLanguageServer.enable": true,
  "trainingLanguageServer.serverPath": "training-lsp",
  "trainingLanguageServer.trace.server": "off"
}
```

### Neovim (init.lua)
```lua
require('lspconfig').training_lsp.setup{}
```

### Emacs (init.el)
```elisp
(lsp-register-client
 (make-lsp-client :new-connection (lsp-stdio-connection "training-lsp")
                  :major-modes '(training-mode)
                  :server-id 'training-lsp))
```

## Example Workout

```training
# Morning session
Bench press: 3x8x75k
Squat: 5x10x100k
Overhead press: 5x5x40k

# Afternoon session
Deadlift 60k: 20, 15, 8, 8
Row: 8xx40k,50k,60k
```

## Help & Documentation

- Quick Start: `lsp/QUICKSTART.md`
- Full Guide: `LSP_GUIDE.md`
- Features: `LSP_FEATURES.md`
- Dev Docs: `lsp/README.md`

## Support

Report issues with:
- Python version: `python --version`
- LSP status: Check editor LSP panel
- Error logs: From editor LSP output
