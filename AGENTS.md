# Agent Guide

## Setup

### Quick Setup (Recommended)
```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Run the setup script
./setup-uv.sh
```

### Manual Setup
```bash
# Create virtual environment with uv
uv venv

# Activate the environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install project with dev dependencies
uv pip install -e ".[dev]"

# Download ANTLR jar (required for grammar compilation)
python3 scripts/download_antlr.py

# Install pre-commit hooks
make install-githooks
```

## Commands
- **Compile**: `make compile-grammar` (compiles ANTLR4 grammar to Python)
- **Type Check**: `make typecheck` (runs mypy with strict settings)
- **Test**: `make test` (runs typecheck, compile-grammar, pytest, validations, and JSON export test)
- **Export JSON**: `make test-json-export` (tests conversion to set-centric JSON format)
- **Run Parser**: `python main.py` (parses sample training data)
- **Run Splitter**: `python splitter.py <file>` (exports to CSV format)
- **Export to JSON**: `python main_export.py <input.txt> -o <output.json>` (full export pipeline)
- **Validate**: `make validate-set-centric` (validates JSON against schema)

## Tech Stack
- **Language**: Python 3.12+
- **Package Manager**: uv (fast, reliable dependency management)
- **Parser Generator**: ANTLR4 (grammar-driven parsing)
- **Type Checking**: mypy (strict mode)
- **Testing**: pytest
- **Schema Validation**: jsonschema
- **Purpose**: Converts text-based workout training logs into structured set-centric JSON format

## Architecture
- `training.g4`: ANTLR4 grammar defining workout syntax
- `dist/`: Generated ANTLR4 lexer and parser (auto-generated, excluded from git)
- `parser/`: Core parser implementation
  - `model.py`: Data structures (Exercise, Set_, Weight)
  - `parser.py`: ANTLR visitor pattern implementation
  - `serializer.py`: Converts Exercise objects to set-centric JSON
  - `standardize_name.py`: Exercise name normalization
- `main.py`: CLI entry point for parsing
- `main_export.py`: CLI for JSON export with validation
- `splitter.py`: CSV export tool
- `schema/`: JSON schema definitions (set-centric, bench-centric, common-definitions)
- `tests/`: Unit tests and validation tests
- `pyproject.toml`: PEP 621 compliant project metadata and dependencies

## Code Style
- Strict mypy typing with `--strict` flag
- Pre-commit hooks enforce formatting, type checking, and tests
- Virtual environment required in `.venv/` directory (created by uv)
- Follow existing patterns in parser visitor implementations

## Development Workflow
1. Make code changes
2. Run `make typecheck` to verify type safety
3. Run `make test` to run full test suite
4. Commit changes with descriptive messages
5. Push to feature branch

## Troubleshooting
- **ANTLR Compilation Error**: Ensure Java is installed and in PATH
- **Import Errors**: Run `uv pip install -e ".[dev]"` to ensure all dependencies are installed
- **Type Errors**: Run `make typecheck` and fix issues before committing
- **Test Failures**: Run individual test files with `pytest parser/test_*.py`
