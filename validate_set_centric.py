#!/usr/bin/env python3
"""
Validate set-centric example against its schema.
"""

import sys
from pathlib import Path

from schema_validator import validate_json_with_schema


def validate_set_centric() -> int:
    """Validate the set-centric example against its schema."""
    schema_path = Path("schema/set-centric.schema.json")
    data_path = Path("data/set-centric-example.json")
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
    sys.exit(validate_set_centric())
