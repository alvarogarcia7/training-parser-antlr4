1→# Agent Guide
2→
3→## Setup
4→```bash
5→python3.12 -m venv venv
6→source venv/bin/activate
7→pip install -r requirements.txt
8→make install-githooks
9→```
10→
11→## Commands
12→- **Build**: `make compile-grammar` (compiles ANTLR4 grammar to Python)
13→- **Lint**: `make typecheck` (runs mypy with strict settings)
14→- **Test**: `make test` (runs typecheck, compile-grammar, and pytest)
15→- **Dev server**: N/A (parser library, use `python main.py` for sample)
16→
17→## Tech Stack
18→Python 3.12 with ANTLR4 for parsing workout training logs. Grammar-driven parser that converts text-based workout entries into structured data.
19→
20→## Architecture
21→- `training.g4`: ANTLR4 grammar defining workout syntax
22→- `parser/`: Parser implementation with visitor pattern, model definitions, name standardization
23→- `dist/`: Generated ANTLR4 lexer/parser (auto-generated, excluded from git)
24→- `tests/`: Located in `parser/test_*.py` files
25→
26→## Code Style
27→- Strict mypy typing with `--strict` flag
28→- Pre-commit hooks enforce formatting, type checking, and tests
29→- Virtual environment required in `venv/` directory
30→- Follow existing patterns in parser visitor implementations
