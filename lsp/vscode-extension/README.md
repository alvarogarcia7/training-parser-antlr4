# Training Language Support for VS Code

This extension provides language support for the training workout DSL in Visual Studio Code.

## Features

- **Syntax Highlighting**: Colorizes exercise names, numbers, operators, and units
- **Error Diagnostics**: Real-time syntax validation with error highlighting
- **IntelliSense**: Auto-completion for exercise names and notation patterns
- **Hover Information**: View exercise details and pattern documentation
- **Code Formatting**: Format documents for consistent style
- **Quick Fixes**: Automatic fixes for common issues

## Installation

### From Source

1. Install the training-parser package with LSP support:
   ```bash
   pip install -e ".[dev]"
   # or
   uv pip install -e ".[dev]"
   ```

2. Build the VSCode extension:
   ```bash
   cd lsp/vscode-extension
   npm install
   npm run compile
   ```

3. Install the extension:
   - Open VS Code
   - Press `Cmd+Shift+P` (Mac) or `Ctrl+Shift+P` (Windows/Linux)
   - Type "Install from VSIX"
   - Select the `.vsix` file (or use Developer: Install Extension from Location)

### Publishing to Marketplace

```bash
cd lsp/vscode-extension
vsce package
vsce publish
```

## Usage

The extension automatically activates for:
- Files with `.training` extension
- Files with `.workout` extension
- Files matching `training*.txt` pattern

### Configuration

Add to your VS Code `settings.json`:

```json
{
  "trainingLanguageServer.enable": true,
  "trainingLanguageServer.serverPath": "training-lsp",
  "trainingLanguageServer.trace.server": "off"
}
```

### Settings

- `trainingLanguageServer.enable`: Enable/disable the language server (default: `true`)
- `trainingLanguageServer.serverPath`: Path to training-lsp executable (default: `"training-lsp"`)
- `trainingLanguageServer.trace.server`: Server trace level: `"off"`, `"messages"`, or `"verbose"` (default: `"off"`)

## Example

```training
Bench press 75k: 4, 4x5
Squat 70k: 5x10
Overhead press: 5x5x40k
Deadlift 60k: 20, 15, 8, 8
```

## Development

### Building

```bash
npm install
npm run compile
```

### Testing

```bash
npm run watch  # Runs TypeScript compiler in watch mode
```

Then press F5 in VS Code to launch Extension Development Host.

## Requirements

- VS Code 1.75.0 or higher
- Python 3.12+
- training-lsp command in PATH

## Known Issues

None at this time. Please report issues at the project repository.

## Release Notes

### 0.1.0

Initial release with:
- Syntax highlighting
- Diagnostics
- Completion
- Hover
- Formatting
- Quick fixes
