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
uv pip install -e ".[dev]"
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

### Development Commands

- `make compile-grammar` - Compile ANTLR4 grammar to Python (downloads ANTLR jar if needed)
- `make install-antlr` - Download ANTLR jar if not present
- `make typecheck` - Run mypy type checking
- `make test` - Run all tests (typecheck + compile-grammar + pytest)
- `make test-python` - Run pytest only
- `python main.py` - Run sample parser directly

**Note**: ANTLR jar is automatically downloaded when needed. The Makefile checks if it exists before downloading.

## Project Structure

```
.
├── training.g4              # ANTLR4 grammar definition
├── parser/                  # Parser implementation
│   ├── model.py            # Data models
│   ├── parser.py           # Parser and visitor
│   └── standardize_name.py # Exercise name standardization
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
