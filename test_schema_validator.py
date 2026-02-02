import json
import tempfile
from pathlib import Path
from typing import Any, Dict

import pytest

from schema_validator import (
    validate_json_with_schema,
    _load_json_file,
    _format_success_output,
    _format_schema_error,
    _format_validation_error,
    _format_json_decode_error,
)
from jsonschema import SchemaError, ValidationError
from typing import Generator


@pytest.fixture  # type: ignore[untyped-decorator]
def temp_dir(tmp_path: Path) -> Path:
    return tmp_path


@pytest.fixture  # type: ignore[untyped-decorator]
def valid_schema(temp_dir: Path) -> Path:
    schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer"}
        },
        "required": ["name"]
    }
    schema_path = temp_dir / "test_schema.json"
    schema_path.write_text(json.dumps(schema))
    return schema_path


@pytest.fixture  # type: ignore[untyped-decorator]
def common_definitions_schema(temp_dir: Path) -> Path:
    common_defs = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "https://example.com/common-defs.json",
        "$defs": {
            "address": {
                "type": "object",
                "properties": {
                    "street": {"type": "string"},
                    "city": {"type": "string"},
                    "zipcode": {"type": "string"}
                },
                "required": ["city"]
            },
            "status": {
                "type": "string",
                "enum": ["active", "inactive", "pending"]
            }
        }
    }
    defs_path = temp_dir / "common_defs.json"
    defs_path.write_text(json.dumps(common_defs))
    return defs_path


@pytest.fixture  # type: ignore[untyped-decorator]
def schema_with_refs(temp_dir: Path) -> Path:
    schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "address": {
                "$ref": "https://example.com/common-defs.json#/$defs/address"
            },
            "status": {
                "$ref": "https://example.com/common-defs.json#/$defs/status"
            }
        },
        "required": ["name", "address"]
    }
    schema_path = temp_dir / "schema_with_refs.json"
    schema_path.write_text(json.dumps(schema))
    return schema_path


class TestSuccessfulValidation:
    def test_valid_data_passes_validation(self, temp_dir: Path, valid_schema: Path) -> None:
        data_path = temp_dir / "valid_data.json"
        data_path.write_text('{"name": "John", "age": 30}')

        success, message = validate_json_with_schema(valid_schema, data_path)

        assert success is True
        assert "✓ Validation successful!" in message
        assert str(valid_schema) in message
        assert str(data_path) in message

    def test_minimal_valid_data(self, temp_dir: Path, valid_schema: Path) -> None:
        data_path = temp_dir / "minimal_data.json"
        data_path.write_text('{"name": "Jane"}')

        success, message = validate_json_with_schema(valid_schema, data_path)

        assert success is True
        assert "✓ Validation successful!" in message

    def test_validation_with_extra_properties(self, temp_dir: Path, valid_schema: Path) -> None:
        data_path = temp_dir / "extra_props.json"
        data_path.write_text('{"name": "Bob", "age": 25, "extra": "value"}')

        success, message = validate_json_with_schema(valid_schema, data_path)

        assert success is True


class TestSchemaReferences:
    def test_successful_validation_with_schema_references(
        self,
        temp_dir: Path,
        schema_with_refs: Path,
        common_definitions_schema: Path
    ) -> None:
        data_path = temp_dir / "data_with_refs.json"
        data = {
            "name": "John Doe",
            "address": {
                "street": "123 Main St",
                "city": "New York",
                "zipcode": "10001"
            },
            "status": "active"
        }
        data_path.write_text(json.dumps(data))

        success, message = validate_json_with_schema(
            schema_with_refs,
            data_path,
            common_definitions_schema
        )

        assert success is True
        assert "✓ Validation successful!" in message

    def test_validation_with_refs_minimal_data(
        self,
        temp_dir: Path,
        schema_with_refs: Path,
        common_definitions_schema: Path
    ) -> None:
        data_path = temp_dir / "minimal_refs.json"
        data = {
            "name": "Jane Smith",
            "address": {
                "city": "Boston"
            }
        }
        data_path.write_text(json.dumps(data))

        success, message = validate_json_with_schema(
            schema_with_refs,
            data_path,
            common_definitions_schema
        )

        assert success is True

    def test_validation_with_refs_fails_on_missing_required_field_in_ref(
        self,
        temp_dir: Path,
        schema_with_refs: Path,
        common_definitions_schema: Path
    ) -> None:
        data_path = temp_dir / "invalid_refs.json"
        data = {
            "name": "John Doe",
            "address": {
                "street": "123 Main St"
            }
        }
        data_path.write_text(json.dumps(data))

        success, message = validate_json_with_schema(
            schema_with_refs,
            data_path,
            common_definitions_schema
        )

        assert success is False
        assert "✗ Validation failed:" in message
        assert "'city' is a required property" in message

    def test_validation_with_refs_fails_on_invalid_enum_value(
        self,
        temp_dir: Path,
        schema_with_refs: Path,
        common_definitions_schema: Path
    ) -> None:
        data_path = temp_dir / "invalid_enum.json"
        data = {
            "name": "John Doe",
            "address": {"city": "New York"},
            "status": "invalid_status"
        }
        data_path.write_text(json.dumps(data))

        success, message = validate_json_with_schema(
            schema_with_refs,
            data_path,
            common_definitions_schema
        )

        assert success is False
        assert "✗ Validation failed:" in message


class TestValidationFailures:
    def test_validation_fails_on_missing_required_field(
        self,
        temp_dir: Path,
        valid_schema: Path
    ) -> None:
        data_path = temp_dir / "missing_field.json"
        data_path.write_text('{"age": 30}')

        success, message = validate_json_with_schema(valid_schema, data_path)

        assert success is False
        assert "✗ Validation failed:" in message
        assert "'name' is a required property" in message

    def test_validation_fails_on_type_mismatch(
        self,
        temp_dir: Path,
        valid_schema: Path
    ) -> None:
        data_path = temp_dir / "type_mismatch.json"
        data_path.write_text('{"name": "John", "age": "thirty"}')

        success, message = validate_json_with_schema(valid_schema, data_path)

        assert success is False
        assert "✗ Validation failed:" in message
        assert "is not of type" in message or "'thirty' is not of type 'integer'" in message

    def test_validation_fails_on_invalid_data_structure(
        self,
        temp_dir: Path,
        valid_schema: Path
    ) -> None:
        data_path = temp_dir / "invalid_structure.json"
        data_path.write_text('["not", "an", "object"]')

        success, message = validate_json_with_schema(valid_schema, data_path)

        assert success is False
        assert "✗ Validation failed:" in message


class TestMissingCommonDefinitions:
    def test_missing_common_definitions_file(
        self,
        temp_dir: Path,
        schema_with_refs: Path
    ) -> None:
        data_path = temp_dir / "data.json"
        data_path.write_text('{"name": "John"}')
        nonexistent_defs = temp_dir / "nonexistent_defs.json"

        success, message = validate_json_with_schema(
            schema_with_refs,
            data_path,
            nonexistent_defs
        )

        assert success is False
        assert "Common definitions file not found" in message
        assert str(nonexistent_defs) in message

    def test_validation_without_common_definitions_when_needed(
        self,
        temp_dir: Path,
        schema_with_refs: Path
    ) -> None:
        data_path = temp_dir / "data.json"
        data = {
            "name": "John Doe",
            "address": {"city": "New York"}
        }
        data_path.write_text(json.dumps(data))

        success, message = validate_json_with_schema(schema_with_refs, data_path)

        assert success is False


class TestInvalidSchemaHandling:
    def test_invalid_schema_file_not_found(
        self,
        temp_dir: Path
    ) -> None:
        nonexistent_schema = temp_dir / "nonexistent_schema.json"
        data_path = temp_dir / "data.json"
        data_path.write_text('{"name": "John"}')

        success, message = validate_json_with_schema(nonexistent_schema, data_path)

        assert success is False
        assert "Schema file not found" in message
        assert str(nonexistent_schema) in message

    def test_invalid_data_file_not_found(
        self,
        temp_dir: Path,
        valid_schema: Path
    ) -> None:
        nonexistent_data = temp_dir / "nonexistent_data.json"

        success, message = validate_json_with_schema(valid_schema, nonexistent_data)

        assert success is False
        assert "Data file not found" in message
        assert str(nonexistent_data) in message

    def test_malformed_json_schema(
        self,
        temp_dir: Path
    ) -> None:
        schema_path = temp_dir / "malformed_schema.json"
        schema_path.write_text('{"type": "object", "properties":')
        data_path = temp_dir / "data.json"
        data_path.write_text('{"name": "John"}')

        success, message = validate_json_with_schema(schema_path, data_path)

        assert success is False
        assert "JSON decode error" in message

    def test_malformed_json_data(
        self,
        temp_dir: Path,
        valid_schema: Path
    ) -> None:
        data_path = temp_dir / "malformed_data.json"
        data_path.write_text('{"name": "John",')

        success, message = validate_json_with_schema(valid_schema, data_path)

        assert success is False
        assert "JSON decode error" in message

    def test_invalid_schema_structure(
        self,
        temp_dir: Path
    ) -> None:
        schema_path = temp_dir / "invalid_schema.json"
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "invalid_type"}
            }
        }
        schema_path.write_text(json.dumps(schema))
        data_path = temp_dir / "data.json"
        data_path.write_text('{"name": "John"}')

        success, message = validate_json_with_schema(schema_path, data_path)

        assert success is False
        assert "✗ Invalid schema:" in message

    def test_schema_with_unsupported_features(
        self,
        temp_dir: Path
    ) -> None:
        schema_path = temp_dir / "unsupported_schema.json"
        schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "if": {"properties": {"country": {"const": "US"}}},
            "then": {"properties": {"zipcode": {"type": "string"}}},
            "additionalProperties": "invalid_value"
        }
        schema_path.write_text(json.dumps(schema))
        data_path = temp_dir / "data.json"
        data_path.write_text('{"country": "US"}')

        success, message = validate_json_with_schema(schema_path, data_path)

        assert success is False
        assert "✗ Invalid schema:" in message


class TestHelperFunctions:
    def test_load_json_file_valid(self, temp_dir: Path) -> None:
        json_path = temp_dir / "test.json"
        json_path.write_text('{"key": "value"}')

        data = _load_json_file(json_path)

        assert data == {"key": "value"}

    def test_load_json_file_with_unicode(self, temp_dir: Path) -> None:
        json_path = temp_dir / "unicode.json"
        json_path.write_text('{"name": "José García 日本語"}', encoding='utf-8')

        data = _load_json_file(json_path)

        assert data["name"] == "José García 日本語"

    def test_format_success_output(self, temp_dir: Path) -> None:
        schema_path = Path("schema.json")
        data_path = Path("data.json")

        output = _format_success_output(schema_path, data_path)

        assert "✓ Validation successful!" in output
        assert "schema.json" in output
        assert "data.json" in output

    def test_format_schema_error(self) -> None:
        error = SchemaError("Invalid schema structure")

        output = _format_schema_error(error)

        assert "✗ Invalid schema:" in output
        assert "Invalid schema structure" in output

    def test_format_validation_error_with_path(self) -> None:
        error = ValidationError("'age' is a required property")
        error.absolute_path = ["user", "details"]

        output = _format_validation_error(error)

        assert "✗ Validation failed:" in output
        assert "'age' is a required property" in output
        assert "Path:  user.details" in output

    def test_format_validation_error_without_path(self) -> None:
        error = ValidationError("Invalid data")
        error.absolute_path = []

        output = _format_validation_error(error)

        assert "✗ Validation failed:" in output
        assert "Invalid data" in output
        assert "Path:" not in output

    def test_format_json_decode_error(self) -> None:
        try:
            json.loads('{"invalid": json}')
        except json.JSONDecodeError as e:
            output = _format_json_decode_error(e)

            assert "✗ JSON decode error:" in output


class TestEdgeCases:
    def test_empty_json_object(self, temp_dir: Path) -> None:
        schema_path = temp_dir / "schema.json"
        schema = {"type": "object"}
        schema_path.write_text(json.dumps(schema))
        data_path = temp_dir / "empty.json"
        data_path.write_text('{}')

        success, message = validate_json_with_schema(schema_path, data_path)

        assert success is True

    def test_empty_json_array(self, temp_dir: Path) -> None:
        schema_path = temp_dir / "schema.json"
        schema = {"type": "array"}
        schema_path.write_text(json.dumps(schema))
        data_path = temp_dir / "empty_array.json"
        data_path.write_text('[]')

        success, message = validate_json_with_schema(schema_path, data_path)

        assert success is True

    def test_null_values(self, temp_dir: Path) -> None:
        schema_path = temp_dir / "schema.json"
        schema = {
            "type": "object",
            "properties": {
                "value": {"type": ["string", "null"]}
            }
        }
        schema_path.write_text(json.dumps(schema))
        data_path = temp_dir / "null_data.json"
        data_path.write_text('{"value": null}')

        success, message = validate_json_with_schema(schema_path, data_path)

        assert success is True

    def test_nested_objects_validation(self, temp_dir: Path) -> None:
        schema_path = temp_dir / "schema.json"
        schema = {
            "type": "object",
            "properties": {
                "user": {
                    "type": "object",
                    "properties": {
                        "profile": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"}
                            },
                            "required": ["name"]
                        }
                    },
                    "required": ["profile"]
                }
            },
            "required": ["user"]
        }
        schema_path.write_text(json.dumps(schema))
        data_path = temp_dir / "nested_data.json"
        data_path.write_text('{"user": {"profile": {"name": "John"}}}')

        success, message = validate_json_with_schema(schema_path, data_path)

        assert success is True

    def test_array_of_objects_validation(self, temp_dir: Path) -> None:
        schema_path = temp_dir / "schema.json"
        schema = {
            "type": "object",
            "properties": {
                "users": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "age": {"type": "integer"}
                        },
                        "required": ["name"]
                    }
                }
            }
        }
        schema_path.write_text(json.dumps(schema))
        data_path = temp_dir / "array_data.json"
        data_path.write_text('{"users": [{"name": "John", "age": 30}, {"name": "Jane"}]}')

        success, message = validate_json_with_schema(schema_path, data_path)

        assert success is True

    def test_path_type_conversions(self, temp_dir: Path, valid_schema: Path) -> None:
        data_path = temp_dir / "data.json"
        data_path.write_text('{"name": "John"}')

        success, message = validate_json_with_schema(
            str(valid_schema),
            str(data_path)
        )

        assert success is True
        assert "✓ Validation successful!" in message
