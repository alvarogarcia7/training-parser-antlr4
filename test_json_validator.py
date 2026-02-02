#!/usr/bin/env python3

import json
import tempfile
from pathlib import Path
from typing import Any, Dict, Iterator

import pytest

from json_validator import (
    ValidationResult,
    load_json_file,
    validate_json_file,
    expand_glob_patterns,
    format_text_output,
    format_json_output,
    get_error_line_number,
)


@pytest.fixture  # type: ignore[untyped-decorator]
def valid_schema() -> Dict[str, Any]:
    return {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer"},
            "email": {"type": "string", "format": "email"}
        },
        "required": ["name", "age"]
    }


@pytest.fixture  # type: ignore[untyped-decorator]
def temp_dir(tmp_path: Path) -> Path:
    return tmp_path


class TestLoadJsonFile:
    def test_load_valid_json(self, temp_dir: Path) -> None:
        json_file = temp_dir / "valid.json"
        json_file.write_text('{"name": "John", "age": 30}')

        data, error = load_json_file(json_file)

        assert error is None
        assert data == {"name": "John", "age": 30}

    def test_load_invalid_json(self, temp_dir: Path) -> None:
        json_file = temp_dir / "invalid.json"
        json_file.write_text('{"name": "John", "age": 30')

        data, error = load_json_file(json_file)

        assert data is None
        assert error is not None
        assert "JSON decode error" in error
        assert "line" in error

    def test_load_malformed_json(self, temp_dir: Path) -> None:
        json_file = temp_dir / "malformed.json"
        json_file.write_text('{"name": "John",, "age": 30}')

        data, error = load_json_file(json_file)

        assert data is None
        assert error is not None
        assert "JSON decode error" in error

    def test_load_nonexistent_file(self, temp_dir: Path) -> None:
        json_file = temp_dir / "nonexistent.json"

        data, error = load_json_file(json_file)

        assert data is None
        assert error is not None
        assert "Error reading file" in error


class TestValidateJsonFile:
    def test_valid_json_passes_validation(self, temp_dir: Path, valid_schema: Dict[str, Any]) -> None:
        json_file = temp_dir / "valid.json"
        json_file.write_text('{"name": "John", "age": 30}')

        result = validate_json_file(json_file, valid_schema)

        assert result.is_valid is True
        assert result.errors == []
        assert result.file_path == str(json_file)

    def test_invalid_json_fails_to_load(self, temp_dir: Path, valid_schema: Dict[str, Any]) -> None:
        json_file = temp_dir / "invalid.json"
        json_file.write_text('{"name": "John", "age": 30')

        result = validate_json_file(json_file, valid_schema)

        assert result.is_valid is False
        assert len(result.errors) == 1
        assert "JSON decode error" in result.errors[0]['message']
        assert result.errors[0]['path'] is None

    def test_missing_required_field(self, temp_dir: Path, valid_schema: Dict[str, Any]) -> None:
        json_file = temp_dir / "missing_field.json"
        json_file.write_text('{"name": "John"}')

        result = validate_json_file(json_file, valid_schema)

        assert result.is_valid is False
        assert len(result.errors) == 1
        assert "'age' is a required property" in result.errors[0]['message']
        assert result.errors[0]['path'] == '$'

    def test_type_mismatch(self, temp_dir: Path, valid_schema: Dict[str, Any]) -> None:
        json_file = temp_dir / "type_mismatch.json"
        json_file.write_text('{"name": "John", "age": "thirty"}')

        result = validate_json_file(json_file, valid_schema)

        assert result.is_valid is False
        assert len(result.errors) == 1
        assert "'thirty' is not of type 'integer'" in result.errors[0]['message']
        assert result.errors[0]['path'] == '$.age'

    def test_multiple_validation_errors(self, temp_dir: Path, valid_schema: Dict[str, Any]) -> None:
        json_file = temp_dir / "multiple_errors.json"
        json_file.write_text('{"age": "thirty"}')

        result = validate_json_file(json_file, valid_schema)

        assert result.is_valid is False
        assert len(result.errors) >= 1

    def test_nested_object_validation(self, temp_dir: Path) -> None:
        schema = {
            "type": "object",
            "properties": {
                "user": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "settings": {
                            "type": "object",
                            "properties": {
                                "theme": {"type": "string"}
                            },
                            "required": ["theme"]
                        }
                    },
                    "required": ["name", "settings"]
                }
            },
            "required": ["user"]
        }

        json_file = temp_dir / "nested.json"
        json_file.write_text('{"user": {"name": "John", "settings": {}}}')

        result = validate_json_file(json_file, schema)

        assert result.is_valid is False
        assert len(result.errors) == 1
        assert "'theme' is a required property" in result.errors[0]['message']
        assert "settings" in result.errors[0]['path']

    def test_array_validation(self, temp_dir: Path) -> None:
        schema = {
            "type": "object",
            "properties": {
                "items": {
                    "type": "array",
                    "items": {"type": "integer"}
                }
            }
        }

        json_file = temp_dir / "array.json"
        json_file.write_text('{"items": [1, "two", 3]}')

        result = validate_json_file(json_file, schema)

        assert result.is_valid is False
        assert len(result.errors) == 1
        assert "'two' is not of type 'integer'" in result.errors[0]['message']
        assert "items" in result.errors[0]['path']
        assert "[1]" in result.errors[0]['path']


class TestBatchValidation:
    def test_validate_multiple_files(self, temp_dir: Path, valid_schema: Dict[str, Any]) -> None:
        file1 = temp_dir / "file1.json"
        file1.write_text('{"name": "John", "age": 30}')

        file2 = temp_dir / "file2.json"
        file2.write_text('{"name": "Jane", "age": 25}')

        results = [
            validate_json_file(file1, valid_schema),
            validate_json_file(file2, valid_schema)
        ]

        assert all(r.is_valid for r in results)
        assert len(results) == 2

    def test_validate_mixed_valid_invalid_files(self, temp_dir: Path, valid_schema: Dict[str, Any]) -> None:
        valid_file = temp_dir / "valid.json"
        valid_file.write_text('{"name": "John", "age": 30}')

        invalid_file = temp_dir / "invalid.json"
        invalid_file.write_text('{"name": "Jane"}')

        results = [
            validate_json_file(valid_file, valid_schema),
            validate_json_file(invalid_file, valid_schema)
        ]

        assert results[0].is_valid is True
        assert results[1].is_valid is False
        assert len(results[1].errors) == 1


class TestExpandGlobPatterns:
    def test_expand_single_file(self, temp_dir: Path) -> None:
        file1 = temp_dir / "test.json"
        file1.write_text('{}')

        files = expand_glob_patterns([str(file1)])

        assert len(files) == 1
        assert files[0] == file1

    def test_expand_glob_pattern(self, temp_dir: Path) -> None:
        (temp_dir / "file1.json").write_text('{}')
        (temp_dir / "file2.json").write_text('{}')
        (temp_dir / "file3.txt").write_text('')

        files = expand_glob_patterns([str(temp_dir / "*.json")])

        assert len(files) == 2
        assert all(f.suffix == '.json' for f in files)

    def test_expand_recursive_glob(self, temp_dir: Path) -> None:
        subdir = temp_dir / "subdir"
        subdir.mkdir()

        (temp_dir / "file1.json").write_text('{}')
        (subdir / "file2.json").write_text('{}')

        files = expand_glob_patterns([str(temp_dir / "**/*.json")])

        assert len(files) == 2

    def test_nonexistent_file_warning(self, temp_dir: Path, capsys: pytest.CaptureFixture[str]) -> None:
        files = expand_glob_patterns([str(temp_dir / "nonexistent.json")])

        assert len(files) == 0
        captured = capsys.readouterr()
        assert "Warning: File not found" in captured.err

    def test_no_matches_returns_empty_list(self, temp_dir: Path) -> None:
        files = expand_glob_patterns([str(temp_dir / "*.json")])

        assert files == []


class TestErrorFormatting:
    def test_format_text_output_all_valid(self, temp_dir: Path) -> None:
        results = [
            ValidationResult(str(temp_dir / "file1.json"), True, []),
            ValidationResult(str(temp_dir / "file2.json"), True, [])
        ]

        output = format_text_output(results)

        assert "2/2 files valid" in output
        assert "✓ VALID" in output
        assert "2 valid, 0 invalid" in output

    def test_format_text_output_with_errors(self, temp_dir: Path) -> None:
        results = [
            ValidationResult(str(temp_dir / "file1.json"), True, []),
            ValidationResult(str(temp_dir / "file2.json"), False, [
                {'message': 'Test error', 'path': '$.field', 'line': 5}
            ])
        ]

        output = format_text_output(results)

        assert "1/2 files valid" in output
        assert "✗ INVALID" in output
        assert "Test error" in output
        assert "Path: $.field" in output
        assert "Line: 5" in output
        assert "1 valid, 1 invalid" in output

    def test_format_text_output_multiple_errors(self, temp_dir: Path) -> None:
        results = [
            ValidationResult(str(temp_dir / "file.json"), False, [
                {'message': 'Error 1', 'path': '$.field1', 'line': 3},
                {'message': 'Error 2', 'path': '$.field2', 'line': 7}
            ])
        ]

        output = format_text_output(results)

        assert "Error 1" in output
        assert "Error 2" in output
        assert "$.field1" in output
        assert "$.field2" in output

    def test_format_json_output_all_valid(self, temp_dir: Path) -> None:
        results = [
            ValidationResult(str(temp_dir / "file1.json"), True, []),
            ValidationResult(str(temp_dir / "file2.json"), True, [])
        ]

        output = format_json_output(results)
        data = json.loads(output)

        assert data['total_files'] == 2
        assert data['valid_files'] == 2
        assert data['invalid_files'] == 0
        assert len(data['results']) == 2
        assert all(r['valid'] for r in data['results'])

    def test_format_json_output_with_errors(self, temp_dir: Path) -> None:
        results = [
            ValidationResult(str(temp_dir / "file1.json"), True, []),
            ValidationResult(str(temp_dir / "file2.json"), False, [
                {'message': 'Test error', 'path': '$.field', 'line': 5}
            ])
        ]

        output = format_json_output(results)
        data = json.loads(output)

        assert data['total_files'] == 2
        assert data['valid_files'] == 1
        assert data['invalid_files'] == 1
        assert data['results'][0]['valid'] is True
        assert data['results'][1]['valid'] is False
        assert len(data['results'][1]['errors']) == 1
        assert data['results'][1]['errors'][0]['message'] == 'Test error'

    def test_format_json_output_structure(self, temp_dir: Path) -> None:
        results = [
            ValidationResult(str(temp_dir / "file.json"), False, [
                {'message': 'Error message', 'path': '$.field', 'line': 10}
            ])
        ]

        output = format_json_output(results)
        data = json.loads(output)

        assert 'total_files' in data
        assert 'valid_files' in data
        assert 'invalid_files' in data
        assert 'results' in data
        assert isinstance(data['results'], list)
        assert 'file' in data['results'][0]
        assert 'valid' in data['results'][0]
        assert 'errors' in data['results'][0]


class TestGetErrorLineNumber:
    def test_get_line_number_for_root(self, temp_dir: Path) -> None:
        json_file = temp_dir / "test.json"
        json_file.write_text('{\n  "name": "John"\n}')

        line = get_error_line_number(json_file, '$')

        assert line == 1

    def test_get_line_number_for_field(self, temp_dir: Path) -> None:
        json_file = temp_dir / "test.json"
        json_file.write_text('{\n  "name": "John",\n  "age": 30\n}')

        line = get_error_line_number(json_file, '$.age')

        assert line is not None
        assert line > 1

    def test_get_line_number_nested_field(self, temp_dir: Path) -> None:
        json_file = temp_dir / "test.json"
        json_file.write_text('{\n  "user": {\n    "name": "John"\n  }\n}')

        line = get_error_line_number(json_file, '$.user.name')

        assert line is not None

    def test_get_line_number_returns_none_on_error(self, temp_dir: Path) -> None:
        json_file = temp_dir / "nonexistent.json"

        line = get_error_line_number(json_file, '$.field')

        assert line is None

    def test_get_line_number_for_array_element(self, temp_dir: Path) -> None:
        json_file = temp_dir / "test.json"
        json_file.write_text('{\n  "items": [1, 2, 3]\n}')

        line = get_error_line_number(json_file, '$.items[1]')

        assert line is not None


class TestValidationResult:
    def test_validation_result_initialization(self) -> None:
        result = ValidationResult(
            file_path="test.json",
            is_valid=True,
            errors=[]
        )

        assert result.file_path == "test.json"
        assert result.is_valid is True
        assert result.errors == []

    def test_validation_result_with_errors(self) -> None:
        errors = [
            {'message': 'Error 1', 'path': '$.field1', 'line': 5},
            {'message': 'Error 2', 'path': '$.field2', 'line': 10}
        ]
        result = ValidationResult(
            file_path="test.json",
            is_valid=False,
            errors=errors
        )

        assert result.file_path == "test.json"
        assert result.is_valid is False
        assert len(result.errors) == 2
        assert result.errors[0]['message'] == 'Error 1'


class TestEdgeCases:
    def test_empty_json_object(self, temp_dir: Path) -> None:
        schema = {"type": "object"}
        json_file = temp_dir / "empty.json"
        json_file.write_text('{}')

        result = validate_json_file(json_file, schema)

        assert result.is_valid is True

    def test_empty_json_array(self, temp_dir: Path) -> None:
        schema = {"type": "array"}
        json_file = temp_dir / "empty_array.json"
        json_file.write_text('[]')

        result = validate_json_file(json_file, schema)

        assert result.is_valid is True

    def test_null_value(self, temp_dir: Path) -> None:
        schema = {
            "type": "object",
            "properties": {
                "value": {"type": ["string", "null"]}
            }
        }
        json_file = temp_dir / "null.json"
        json_file.write_text('{"value": null}')

        result = validate_json_file(json_file, schema)

        assert result.is_valid is True

    def test_unicode_content(self, temp_dir: Path) -> None:
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"}
            }
        }
        json_file = temp_dir / "unicode.json"
        json_file.write_text('{"name": "José García 日本語 🎉"}', encoding='utf-8')

        result = validate_json_file(json_file, schema)

        assert result.is_valid is True

    def test_very_large_number(self, temp_dir: Path) -> None:
        schema = {
            "type": "object",
            "properties": {
                "value": {"type": "number"}
            }
        }
        json_file = temp_dir / "large_number.json"
        json_file.write_text('{"value": 9999999999999999999}')

        result = validate_json_file(json_file, schema)

        assert result.is_valid is True

    def test_boolean_validation(self, temp_dir: Path) -> None:
        schema = {
            "type": "object",
            "properties": {
                "active": {"type": "boolean"}
            }
        }
        json_file = temp_dir / "boolean.json"
        json_file.write_text('{"active": true}')

        result = validate_json_file(json_file, schema)

        assert result.is_valid is True

    def test_additional_properties_allowed(self, temp_dir: Path) -> None:
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"}
            },
            "additionalProperties": True
        }
        json_file = temp_dir / "extra_props.json"
        json_file.write_text('{"name": "John", "extra": "value"}')

        result = validate_json_file(json_file, schema)

        assert result.is_valid is True

    def test_additional_properties_disallowed(self, temp_dir: Path) -> None:
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"}
            },
            "additionalProperties": False
        }
        json_file = temp_dir / "extra_props.json"
        json_file.write_text('{"name": "John", "extra": "value"}')

        result = validate_json_file(json_file, schema)

        assert result.is_valid is False
        assert len(result.errors) == 1
