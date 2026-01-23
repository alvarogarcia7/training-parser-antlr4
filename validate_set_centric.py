#!/usr/bin/env python3
"""
Validate set-centric example against its schema.
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, cast

import jsonschema
from jsonschema import RefResolver, ValidationError


def load_json_file(file_path: Path) -> Dict[str, Any]:
    """Load and parse a JSON file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return cast(Dict[str, Any], json.load(f))


def validate_set_centric() -> int:
    """Validate the set-centric example against its schema."""
    schema_path = Path("schema/set-centric.schema.json")
    data_path = Path("data/set-centric-example.json")
    common_defs_path = Path("schema/common-definitions.schema.json")
    
    if not schema_path.exists():
        print(f"Error: Schema file not found: {schema_path}", file=sys.stderr)
        return 1
    
    if not data_path.exists():
        print(f"Error: Data file not found: {data_path}", file=sys.stderr)
        return 1
    
    try:
        schema = load_json_file(schema_path)
        data = load_json_file(data_path)
        common_defs = load_json_file(common_defs_path)
        
        jsonschema.validators.validator_for(schema).check_schema(schema)
        
        store = {
            common_defs["$id"]: common_defs
        }
        
        resolver = RefResolver.from_schema(schema, store=store)
        validator = jsonschema.validators.validator_for(schema)(schema, resolver=resolver)
        validator.validate(data)
        
        print(f"✓ Validation successful!")
        print(f"  Schema: {schema_path}")
        print(f"  Data:   {data_path}")
        return 0
        
    except jsonschema.SchemaError as e:
        print(f"✗ Invalid schema: {e.message}", file=sys.stderr)
        return 1
    except ValidationError as e:
        print(f"✗ Validation failed:", file=sys.stderr)
        print(f"  Error: {e.message}", file=sys.stderr)
        if e.absolute_path:
            path = '.'.join(str(p) for p in e.absolute_path)
            print(f"  Path:  {path}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as e:
        print(f"✗ JSON decode error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"✗ Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(validate_set_centric())
