# LSP Quick Start

Get intelligent editing features for your training logs in under 5 minutes.

## Install

```bash
# Using uv (recommended)
uv pip install -e ".[dev]"

# Or using pip
pip install -e ".[dev]"
```

## Verify

```bash
which training-lsp
# Should output the path to the LSP server
```

## Editor Setup

### VS Code

1. Install the extension:
   ```bash
   cd lsp/vscode-extension
   npm install && npm run compile
   ```

2. In VS Code: `Cmd+Shift+P` → "Developer: Install Extension from Location"

3. Open any `.training` or `training*.txt` file

### Neovim

Add to your config:

```lua
require('lspconfig').configs.training_lsp = {
  default_config = {
    cmd = {'training-lsp'},
    filetypes = {'training'},
    root_dir = require('lspconfig').util.find_git_ancestor,
  },
}
require('lspconfig').training_lsp.setup{}

vim.api.nvim_create_autocmd({"BufRead", "BufNewFile"}, {
  pattern = {"*.training", "training*.txt"},
  callback = function() vim.bo.filetype = "training" end,
})
```

### Emacs

Add to your config:

```elisp
(require 'lsp-mode)

(define-derived-mode training-mode fundamental-mode "Training")
(add-to-list 'auto-mode-alist '("\\.training\\'" . training-mode))

(lsp-register-client
 (make-lsp-client :new-connection (lsp-stdio-connection "training-lsp")
                  :major-modes '(training-mode)
                  :server-id 'training-lsp))

(add-hook 'training-mode-hook #'lsp)
```

## Try It

Create `test.training`:

```
Bench press: 3x8x75k
Squat: 5x10x100k
```

You should see:
- ✅ Syntax highlighting
- ✅ Hover for details (hover over "Bench press")
- ✅ Completions (type "Dead" and press Tab)
- ✅ Error checking (try adding `@#$` to see errors)

## Features at a Glance

| Feature | Example |
|---------|---------|
| **Completion** | Type `Ben` → suggests `Bench press:` |
| **Hover** | Hover on exercise → shows sets, volume, breakdown |
| **Diagnostics** | Invalid syntax → red squiggles |
| **Formatting** | `Bench press:3x8` → `Bench press: 3x8` |
| **Quick Fix** | Missing colon → "Add colon" action |

## Need Help?

See [LSP_GUIDE.md](../LSP_GUIDE.md) for detailed documentation.
