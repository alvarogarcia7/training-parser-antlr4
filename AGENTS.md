# Agent Guide

## Setup
```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Quick setup (recommended)
./setup-uv.sh

# Or manual setup:
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e ".[dev]"
python3 scripts/download_antlr.py  # Downloads ANTLR jar if not present
make install-githooks
```

## Legacy Setup (deprecated)
```bash
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
make install-githooks
```

## Commands
- **Build**: `make compile-grammar` (compiles ANTLR4 grammar to Python)
- **Lint**: `make typecheck` (runs mypy with strict settings)
- **Test**: `make test` (runs typecheck, compile-grammar, and pytest)
- **Dev server**: N/A (parser library, use `python main.py` for sample)

## Tech Stack
Python 3.12 with ANTLR4 for parsing workout training logs. Grammar-driven parser that converts text-based workout entries into structured data. Uses uv for fast, reliable Python package management.

## Architecture
- `training.g4`: ANTLR4 grammar defining workout syntax
- `parser/`: Parser implementation with visitor pattern, model definitions, name standardization
- `dist/`: Generated ANTLR4 lexer/parser (auto-generated, excluded from git)
- `tests/`: Located in `parser/test_*.py` files
- `pyproject.toml`: PEP 621 compliant project metadata and dependencies

## Code Style
- Strict mypy typing with `--strict` flag
- Pre-commit hooks enforce formatting, type checking, and tests
- Virtual environment required in `.venv/` directory (uv) or `venv/` (legacy)
- Follow existing patterns in parser visitor implementations
