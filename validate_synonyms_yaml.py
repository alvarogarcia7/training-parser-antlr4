#!/usr/bin/env python3
"""
Validate synonym configuration files (default: data/config/synonyms.yaml):

1. Structure, against schema/exercise_synonyms.schema.json
2. Consistency, with the same checks StandardizeName runs when the application
   loads the file (no overlapping synonyms, unique clean names, no synonym that
   expands recursively)

Usage: validate_synonyms_yaml.py [SYNONYMS_FILE ...]
"""

import json
import sys
import yaml
import jsonschema

from parser.standardize_name import StandardizeName

DEFAULT_SYNONYMS = 'data/config/synonyms.yaml'
SCHEMA = 'schema/exercise_synonyms.schema.json'


def validate_yaml_against_schema(path: str = DEFAULT_SYNONYMS) -> bool:
    """Validate the YAML file against the JSON Schema."""

    # Load the schema
    with open(SCHEMA, 'r') as f:
        schema = json.load(f)

    # Load the YAML file
    with open(path, 'r') as f:
        data = yaml.safe_load(f)

    # Validate
    try:
        jsonschema.validate(data, schema)
        print(f'✓ {path} is valid according to {SCHEMA}')
        return True
    except jsonschema.exceptions.ValidationError as e:
        print(f'✗ Validation error: {e}')
    except jsonschema.exceptions.SchemaError as e:
        print(f'✗ Schema error: {e}')
    return False


def validate_synonym_configuration(path: str = DEFAULT_SYNONYMS) -> bool:
    """Load the file as the application does, running StandardizeName's configuration checks."""
    try:
        StandardizeName(config_path=path)
        print(f'✓ {path} synonyms are consistent (no overlaps, no duplicates, no recursive expansion)')
        return True
    except (AssertionError, ValueError) as e:
        print(f'✗ Synonym configuration error in {path}: {e or "overlapping or duplicate names"}')
        return False


def main(paths: list[str]) -> int:
    ok = True
    for path in paths or [DEFAULT_SYNONYMS]:
        ok = validate_yaml_against_schema(path) and validate_synonym_configuration(path) and ok
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
