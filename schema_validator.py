"""
Schema validation module for JSON data.

Provides functionality to validate JSON data against JSON schemas with support
for external references ($ref) and detailed error reporting.
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, Optional, Tuple, Union, cast

import jsonschema
from jsonschema import RefResolver, ValidationError


def validate_json_with_schema(
    schema_path: Union[str, Path],
    data_path: Union[str, Path],
    common_defs_path: Optional[Union[str, Path]] = None
) -> Tuple[bool, str]:
    """
    Validate JSON data against a JSON schema.

    Args:
        schema_path: Path to the JSON schema file
        data_path: Path to the JSON data file to validate
        common_defs_path: Optional path to common definitions schema for $ref resolution

    Returns:
        Tuple of (success: bool, message: str) where success is True if validation
        passed, False otherwise. The message contains formatted validation results
        or error details.

    Example:
        >>> success, message = validate_json_with_schema(
        ...     "schema/set-centric.schema.json",
        ...     "data/set-centric-example.json",
        ...     "schema/common-definitions.schema.json"
        ... )
        >>> if success:
        ...     print(message)
        ... else:
        ...     print("Validation failed:", message, file=sys.stderr)
    """
    schema_path = Path(schema_path)
    data_path = Path(data_path)
    if common_defs_path is not None:
        common_defs_path = Path(common_defs_path)

    if not schema_path.exists():
        return False, f"Schema file not found: {schema_path}"

    if not data_path.exists():
        return False, f"Data file not found: {data_path}"

    if common_defs_path is not None and not common_defs_path.exists():
        return False, f"Common definitions file not found: {common_defs_path}"

    try:
        schema = _load_json_file(schema_path)
        data = _load_json_file(data_path)

        jsonschema.validators.validator_for(schema).check_schema(schema)

        resolver: Optional[RefResolver] = None
        if common_defs_path is not None:
            common_defs = _load_json_file(common_defs_path)
            store = {
                common_defs["$id"]: common_defs
            }
            resolver = RefResolver.from_schema(schema, store=store)

        validator_class = jsonschema.validators.validator_for(schema)
        if resolver is not None:
            validator = validator_class(schema, resolver=resolver)
        else:
            validator = validator_class(schema)

        validator.validate(data)

        success_message = _format_success_output(schema_path, data_path)
        return True, success_message

    except jsonschema.SchemaError as e:
        error_message = _format_schema_error(e)
        return False, error_message
    except ValidationError as e:
        error_message = _format_validation_error(e)
        return False, error_message
    except json.JSONDecodeError as e:
        error_message = _format_json_decode_error(e)
        return False, error_message
    except Exception as e:
        error_message = f"Unexpected error: {e}"
        return False, error_message


def _load_json_file(file_path: Path) -> Dict[str, Any]:
    """Load and parse a JSON file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return cast(Dict[str, Any], json.load(f))


def _format_success_output(schema_path: Path, data_path: Path) -> str:
    """Format a success message for validation."""
    lines = [
        "✓ Validation successful!",
        f"  Schema: {schema_path}",
        f"  Data:   {data_path}"
    ]
    return "\n".join(lines)


def _format_schema_error(error: jsonschema.SchemaError) -> str:
    """Format a schema error message."""
    return f"✗ Invalid schema: {error.message}"


def _format_validation_error(error: ValidationError) -> str:
    """Format a validation error message with path information."""
    lines = ["✗ Validation failed:", f"  Error: {error.message}"]
    if error.absolute_path:
        path = '.'.join(str(p) for p in error.absolute_path)
        lines.append(f"  Path:  {path}")
    return "\n".join(lines)


def _format_json_decode_error(error: json.JSONDecodeError) -> str:
    """Format a JSON decode error message."""
    return f"✗ JSON decode error: {error}"
