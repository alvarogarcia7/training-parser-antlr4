# Training Parser

ANTLR4-based parser for workout training logs that converts text-based workout entries into structured data.

## Quick Start

### With uv (Recommended)

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Run automated setup script (installs deps and ANTLR)
./setup-uv.sh

# Or manually:
uv venv
source .venv/bin/activate
uv sync --all-extras
python3 scripts/download_antlr.py  # Downloads ANTLR jar if not present
make install-githooks
```

## Usage

### CLI Commands

After installation, the following commands are available:

- `training-parser` - Run the sample parser
- `training-splitter <file> [--output <file>]` - Split and parse training data
- `validate-bench-centric` - Validate bench-centric schema
- `validate-set-centric` - Validate set-centric schema
- `json-validator <schema> <files...>` - Validate JSON files against schema
- `download-antlr` - Download ANTLR jar file if not present
- `training-lsp` - Start the Language Server Protocol server
- `training-lsp-cli` - CLI tool for testing LSP features

### Development Commands

- `make compile-grammar` - Compile ANTLR4 grammar to Python (downloads ANTLR jar if needed)
- `make install-antlr` - Download ANTLR jar if not present
- `make typecheck` - Run mypy type checking
- `make test` - Run all tests (typecheck + compile-grammar + pytest)
- `make test-python` - Run pytest only
- `python main.py` - Run sample parser directly

**Note**: ANTLR jar is automatically downloaded when needed. The Makefile checks if it exists before downloading.

## Documentation

📚 **[GRAMMAR_DOCUMENTATION_INDEX.md](GRAMMAR_DOCUMENTATION_INDEX.md)** - Complete documentation index and navigation guide

### Quick Start
- **[QUICK_START_GRAMMAR.md](QUICK_START_GRAMMAR.md)** - 5-minute introduction to grammar formats with examples

### Grammar & Syntax
- **[GRAMMAR_FORMATS.md](GRAMMAR_FORMATS.md)** - Complete reference guide to all supported input formats with examples and tests
- **[SYNTAX.md](SYNTAX.md)** - Detailed syntax documentation with use cases and best practices

### Features
- **[LSP_GUIDE.md](LSP_GUIDE.md)** - Language Server Protocol setup and usage
- **[data/SYNONYMS_README.md](data/SYNONYMS_README.md)** - Exercise name synonym configuration

## Features

### 🚀 Language Server Protocol (LSP)

The training-parser now includes a full-featured Language Server Protocol implementation, bringing IDE-like features to your training log editor!

**Key Features:**
- ✅ Real-time syntax validation and error highlighting
- ✅ Intelligent auto-completion for exercises and notation patterns
- ✅ Hover information with exercise statistics and syntax help
- ✅ Code formatting and quick fixes
- ✅ Semantic syntax highlighting

**Quick Start:**
```bash
# Install with LSP support
uv pip install -e ".[dev]"

# Start the LSP server (for editor integration)
training-lsp

# Or use the CLI tool for quick checks
training-lsp-cli check workout.txt
training-lsp-cli format workout.txt
```

**Editor Support:** VS Code, Neovim, Emacs, Vim, Sublime Text, and any LSP-compatible editor.

📖 **See [LSP_GUIDE.md](LSP_GUIDE.md) for complete setup and usage instructions.**

### Configurable Exercise Name Synonyms

The parser supports loading custom exercise name mappings from YAML or JSON files, enabling:

- **Customization without code changes**: Define your own exercise name synonyms
- **Internationalization**: Create language-specific synonym files
- **Easy maintenance**: Version control and share synonym configurations

**Quick Example:**

```python
from parser import StandardizeName

# Use default synonyms
standardizer = StandardizeName()
standardizer.run("bench")  # Returns "Bench Press"

# Load custom synonyms from file
standardizer = StandardizeName(config_path="data/synonyms.yaml")
standardizer.run("press de banca")  # Returns "Bench Press" (Spanish)
```

See [data/SYNONYMS_README.md](data/SYNONYMS_README.md) for detailed documentation and [examples/](examples/) for usage examples.

## Phase 2: iOS-Friendly Keyboard Syntax

The parser now supports Phase 2 iOS-friendly alternatives to standard notation:

- **Dot separator** (`.` = `x`): `5.5.39` instead of `5x5x39`
- **Double-dot separator** (`..` = `xx`): `1..24` instead of `1xx24`
- **Slash weight separator** (`/` = `,`): `20xx40/50/60` instead of `20xx40,50,60`
- **Comma-decimal weights** (`,` as decimal in slash contexts): `27,5` = 27.5kg
- **RIR dash notation** (`-N` instead of space-N): `5.5.39-8` for RIR 8

### Migration from Phase 1

If you have existing logs using Phase 1 space-based RIR syntax, migrate them using:

```bash
# Convert space-RIR to dash-RIR
# Example: "3x5x100k 2" becomes "3x5x100k-2"
sed -E 's/([0-9]+[xX][0-9]+[xX][0-9]+(\.[0-9]+)?k?)\s+([0-9]+)(\s*[,$\n])/\1-\3\4/g' old-log.txt > new-log.txt
```

See [SYNTAX.md](SYNTAX.md) for detailed Phase 2 documentation and examples.

## Project Structure

```
.
├── training.g4              # ANTLR4 grammar definition
├── parser/                  # Parser implementation
│   ├── model.py            # Data models
│   ├── parser.py           # Parser and visitor
│   └── standardize_name.py # Exercise name standardization
├── lsp/                     # Language Server Protocol implementation
│   ├── server.py           # LSP server
│   ├── diagnostics.py      # Error detection
│   ├── completion.py       # Auto-completion
│   ├── hover.py            # Hover information
│   ├── formatting.py       # Code formatting
│   ├── semantic_tokens.py  # Syntax highlighting
│   ├── code_actions.py     # Quick fixes
│   └── vscode-extension/   # VS Code extension
├── data/                    # Configuration files
│   ├── synonyms.yaml       # Default synonyms (YAML)
│   └── SYNONYMS_README.md  # Synonyms documentation
├── examples/                # Example scripts
├── dist/                    # Generated ANTLR4 code (auto-generated)
├── schema/                  # JSON schema definitions
├── tests/                   # Test files
└── pyproject.toml          # Project metadata and dependencies
```

## Requirements

- Python 3.12 or higher
- Java (for ANTLR4 grammar compilation)
- ANTLR4 jar file (automatically downloaded during setup, or run `make install-antlr`)


## Notes and TODOs

**2022-02-20 12:50:08 AGB**

To do:
* Requires more testing around splitter. For now, it needs manual testing.

**2022-07-17 13:02:44 AGB**

To Do:
* Explain which syntax is available, in words / description. Do not only rely on grammar + tests to document it.

**2023-09-15 18:12:20 AGB**

To Do:
* Cleanup the grammar, moving the "moving parts" to a builder.
  * use a 'addSeriesIfComplete'.
* The series is like a ternary operator, in which you can vary any of the three components: weight, repetitions, amount of series

2025-04-09 19:08:50 AGB
To do:

Should be compacted:
58: 8, 10, 8, 10, 10, 12

Equivalent to:
58: 8, 8, 10, 10, 10, 12

The program should reorder/compact the inputs so that there are fewer series

* Make 'm' machine
* make 'sm' smith machine

This input is parsed wrong:

Machine leg press: 1x20x32, 52:10,20, 66: 15
Actual:     Machine Leg Press: 1x20@32.0kg, 1x10@52.0kg, 1x20@52.0kg, 1x15@52.0kg, 1x15@66.0kg; subtotal: 3970.0
Expected:   Machine Leg Press: 1x20@32.0kg, 1x10@52.0kg, 1x20@52.0kg, *<NOTHING >* 1x15@66.0kg; subtotal: XXX
