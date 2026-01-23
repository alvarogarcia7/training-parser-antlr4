#!/usr/bin/env python3
"""
Validate set-centric example against its schema.
"""

import sys
from pathlib import Path
from json_validator import load_json_file, validate_json_file


def main() -> int:
    schema_path = Path("schema/set-centric.schema.json")
    data_path = Path("data/set-centric-example.json")
    
    if not schema_path.exists():
        print(f"Error: Schema file not found: {schema_path}", file=sys.stderr)
        return 1
    
    if not data_path.exists():
        print(f"Error: Data file not found: {data_path}", file=sys.stderr)
        return 1
    
    schema, load_error = load_json_file(schema_path)
    if load_error:
        print(f"Error loading schema: {load_error}", file=sys.stderr)
        return 1
    
    print(f"Validating {data_path} against {schema_path}...")
    result = validate_json_file(data_path, schema)
    
    if result.is_valid:
        print(f"✓ {data_path} is VALID")
        return 0
    else:
        print(f"✗ {data_path} is INVALID")
        print("\nValidation errors:")
        for error in result.errors:
            print(f"  - {error['message']}")
            if error['path']:
                print(f"    Path: {error['path']}")
            if error['line']:
                print(f"    Line: {error['line']}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
