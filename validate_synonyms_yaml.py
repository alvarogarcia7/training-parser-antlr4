#!/usr/bin/env python3
"""
Validate data/synonyms.yaml against schema/exercise_synonyms.schema.json
"""

import json
import sys
import yaml
import jsonschema


def validate_yaml_against_schema() -> None:
    """Validate the YAML file against the JSON Schema."""

    # Load the schema
    with open('schema/exercise_synonyms.schema.json', 'r') as f:
        schema = json.load(f)

    # Load the YAML file
    with open('data/synonyms.yaml', 'r') as f:
        data = yaml.safe_load(f)

    # Validate
    try:
        jsonschema.validate(data, schema)
        print('✓ data/synonyms.yaml is valid according to schema/exercise_synonyms.schema.json')
    except jsonschema.exceptions.ValidationError as e:
        print(f'✗ Validation error: {e}')
        sys.exit(1)
    except jsonschema.exceptions.SchemaError as e:
        print(f'✗ Schema error: {e}')
        sys.exit(1)


if __name__ == '__main__':
    validate_yaml_against_schema()
