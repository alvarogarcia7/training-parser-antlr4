"""Tests for common definitions schema."""

import json
from pathlib import Path

import jsonschema


def test_common_definitions_schema_is_valid() -> None:
    """Test that the common definitions schema itself is valid."""
    schema_path = Path("schema/common-definitions.schema.json")
    
    with open(schema_path, 'r', encoding='utf-8') as f:
        schema = json.load(f)
    
    validator_class = jsonschema.validators.validator_for(schema)
    validator_class.check_schema(schema)
