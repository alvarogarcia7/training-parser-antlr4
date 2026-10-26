#!/usr/bin/env python3
"""Bulk export training files to JSON and append them to the database.

This is the CLI entry point; the reusable pipeline lives in
``src/bulk_export.py`` and is shared with ``bin/insert_data_to_db.py``.
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

from src.bulk_export import run


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Bulk export training files to JSON")
    parser.add_argument("inputs", nargs="+", type=Path)
    parser.add_argument("-o", "--output-dir", type=Path, required=True)
    parser.add_argument("-d", "--database", type=Path, required=True)
    parser.add_argument(
        "--manifest", type=Path,
        help="Write the paths of every JSON file produced, one per line",
    )
    args = parser.parse_args(argv)
    return run(args.inputs, args.output_dir, args.database, args.manifest)


if __name__ == "__main__":
    sys.exit(main())
