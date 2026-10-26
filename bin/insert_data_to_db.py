#!/usr/bin/env python3
"""Validate a training file and insert it into the DB if it validates.

Thin CLI over the shared pipeline in ``src/bulk_export.py`` (the same library
``bin/bulk_export.py`` uses). The pipeline parses each session, serializes it to
set-/bench-centric JSON - which validates it against the JSON schema - and
upserts only the validated sessions into the database. This entry point just
adds the "process data.txt into the database" defaults so it can be driven by
``make db-insert``: the input defaults to ``data.txt`` and the database to
``<output-dir>/database.json``.

Exit code: 0 when the file validated and was inserted, non-zero otherwise - so
it can gate automation ("the parsing must finish successfully").
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

from src.bulk_export import REPO_ROOT, run

DEFAULT_INPUT = REPO_ROOT / "data.txt"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "data" / "parsed"


def validate_and_insert(input_file: Path, output_dir: Path, database_file: Path) -> int:
    """Validate ``input_file`` and insert it into ``database_file`` if valid.

    Delegates to :func:`src.bulk_export.run` so the parse/validate/insert logic
    lives in one place. Returns 0 on success and non-zero if the file is missing
    or any session fails to parse/validate; only validated sessions are written.
    """
    return run([input_file], output_dir, database_file)


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate a training file and insert it into the database if valid"
    )
    parser.add_argument(
        "input", nargs="?", type=Path, default=DEFAULT_INPUT,
        help="Training file to process (default: data.txt)",
    )
    parser.add_argument(
        "-o", "--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR,
        help="Output directory for set-/bench-centric files (default: data/parsed)",
    )
    parser.add_argument(
        "-d", "--database", type=Path, default=None,
        help="Database file (default: <output-dir>/database.json)",
    )
    args = parser.parse_args(argv)
    database_file = args.database if args.database is not None else args.output_dir / "database.json"
    return validate_and_insert(args.input, args.output_dir, database_file)


if __name__ == "__main__":
    sys.exit(main())
