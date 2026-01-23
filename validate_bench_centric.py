#!/usr/bin/env python3
"""
Validate bench-centric example against its schema.
"""

import sys
from pathlib import Path

from schema_validator import validate_json_with_schema


def validate_bench_centric() -> int:
    """Validate the bench-centric example against its schema."""
    schema_path = Path("schema/bench-centric.schema.json")
    data_path = Path("data/bench-centric-example.json")
    common_defs_path = Path("schema/common-definitions.schema.json")
    
    success, message = validate_json_with_schema(
        schema_path,
        data_path,
        common_defs_path
    )
    
    if success:
        print(message)
        return 0
    else:
        print(message, file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(validate_bench_centric())
