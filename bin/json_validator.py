#!/usr/bin/env python3
"""
JSON Schema Validator CLI

Validates JSON files against a JSON schema with detailed error reporting.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import jsonschema
from jsonschema import ValidationError


class ValidationResult:
    """Stores validation result for a single file."""

    def __init__(self, file_path: str, is_valid: bool, errors: List[Dict[str, Any]]) -> None:
        self.file_path = file_path
        self.is_valid = is_valid
        self.errors = errors


def load_json_file(file_path: Path) -> Tuple[Any, Optional[str]]:
    """
    Load JSON file and return parsed content.

    Returns:
        Tuple of (parsed_data, error_message)
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f), None
    except json.JSONDecodeError as e:
        return None, f"JSON decode error at line {e.lineno}, column {e.colno}: {e.msg}"
    except Exception as e:
        return None, f"Error reading file: {str(e)}"


def get_error_line_number(json_file_path: Path, json_path: str) -> Optional[int]:
    """
    Attempt to determine the line number where the validation error occurred.

    This is a best-effort approach using the error's JSON path.
    """
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        if not json_path or json_path == "$":
            return 1

        path_parts = json_path.replace("$.", "").replace("$", "")
        if not path_parts:
            return 1

        search_terms = []
        for part in path_parts.replace("[", ".").replace("]", "").split("."):
            if part and not part.isdigit():
                search_terms.append(f'"{part}"')

        if search_terms:
            for i, line in enumerate(content.split('\n'), 1):
                if any(term in line for term in search_terms):
                    return i

        return None
    except Exception:
        return None


def validate_json_file(json_file_path: Path, schema: Dict[str, Any]) -> ValidationResult:
    """
    Validate a single JSON file against the schema.

    Returns:
        ValidationResult object containing validation status and errors
    """
    data, load_error = load_json_file(json_file_path)

    if load_error:
        return ValidationResult(
            file_path=str(json_file_path),
            is_valid=False,
            errors=[{
                'message': load_error,
                'path': None,
                'line': None
            }]
        )

    errors = []
    validator = jsonschema.Draft7Validator(schema)

    for error in validator.iter_errors(data):
        json_path = '$.{}'.format('.'.join(
            f'[{p}]' if isinstance(p, int) else p
            for p in error.absolute_path
        )) if error.absolute_path else '$'

        line_number = get_error_line_number(json_file_path, json_path)

        error_info = {
            'message': error.message,
            'path': json_path,
            'line': line_number
        }
        errors.append(error_info)

    if errors:
        return ValidationResult(
            file_path=str(json_file_path),
            is_valid=False,
            errors=errors
        )

    return ValidationResult(
        file_path=str(json_file_path),
        is_valid=True,
        errors=[]
    )


def expand_glob_patterns(patterns: List[str]) -> List[Path]:
    """
    Expand glob patterns to list of file paths.

    Args:
        patterns: List of file paths or glob patterns

    Returns:
        List of resolved Path objects
    """
    files = []
    for pattern in patterns:
        path = Path(pattern)

        if '*' in pattern or '?' in pattern or '[' in pattern:
            parent = Path('.')
            pattern_str = pattern

            if '/' in pattern:
                parts = pattern.split('/')
                for i, part in enumerate(parts):
                    if '*' in part or '?' in part or '[' in part:
                        parent = Path('/'.join(parts[:i])) if i > 0 else Path('.')
                        pattern_str = '/'.join(parts[i:])
                        break

            matched = list(parent.glob(pattern_str))
            files.extend([f for f in matched if f.is_file()])
        else:
            if path.is_file():
                files.append(path)
            elif not path.exists():
                print(f"Warning: File not found: {pattern}", file=sys.stderr)

    return sorted(set(files))


def format_text_output(results: List[ValidationResult]) -> str:
    """Format validation results as human-readable text."""
    output = []
    total_files = len(results)
    valid_files = sum(1 for r in results if r.is_valid)
    invalid_files = total_files - valid_files

    output.append(f"Validation Results: {valid_files}/{total_files} files valid\n")
    output.append("=" * 70)

    for result in results:
        output.append(f"\nFile: {result.file_path}")

        if result.is_valid:
            output.append("  Status: ✓ VALID")
        else:
            output.append("  Status: ✗ INVALID")
            output.append("  Errors:")
            for error in result.errors:
                output.append(f"    - {error['message']}")
                if error['path']:
                    output.append(f"      Path: {error['path']}")
                if error['line']:
                    output.append(f"      Line: {error['line']}")

    output.append("\n" + "=" * 70)
    output.append(f"Summary: {valid_files} valid, {invalid_files} invalid")

    return "\n".join(output)


def format_json_output(results: List[ValidationResult]) -> str:
    """Format validation results as JSON."""
    output: Dict[str, Any] = {
        'total_files': len(results),
        'valid_files': sum(1 for r in results if r.is_valid),
        'invalid_files': sum(1 for r in results if not r.is_valid),
        'results': []
    }

    for result in results:
        output['results'].append({
            'file': result.file_path,
            'valid': result.is_valid,
            'errors': result.errors
        })

    return json.dumps(output, indent=2)


def main() -> int:
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description='Validate JSON files against a JSON schema',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s schema.json data.json
  %(prog)s schema.json file1.json file2.json file3.json
  %(prog)s schema.json data/*.json
  %(prog)s schema.json data/**/*.json --format json
  %(prog)s schema.json data/*.json -o results.txt
        """
    )

    parser.add_argument(
        'schema',
        help='Path to JSON schema file'
    )

    parser.add_argument(
        'files',
        nargs='+',
        help='JSON file paths (supports glob patterns like *.json or **/*.json)'
    )

    parser.add_argument(
        '-f', '--format',
        choices=['text', 'json'],
        default='text',
        help='Output format (default: text)'
    )

    parser.add_argument(
        '-o', '--output',
        help='Output file path (default: stdout)'
    )

    args = parser.parse_args()

    schema_path = Path(args.schema)
    if not schema_path.exists():
        print(f"Error: Schema file not found: {args.schema}", file=sys.stderr)
        return 1

    schema, load_error = load_json_file(schema_path)
    if load_error:
        print(f"Error loading schema: {load_error}", file=sys.stderr)
        return 1

    try:
        jsonschema.Draft7Validator.check_schema(schema)
    except jsonschema.SchemaError as e:
        print(f"Error: Invalid schema: {e.message}", file=sys.stderr)
        return 1

    json_files = expand_glob_patterns(args.files)

    if not json_files:
        print("Error: No JSON files found matching the provided patterns", file=sys.stderr)
        return 1

    results: List[ValidationResult] = []
    for json_file in json_files:
        result = validate_json_file(json_file, schema)
        results.append(result)

    if args.format == 'text':
        output = format_text_output(results)
    else:
        output = format_json_output(results)

    if args.output:
        try:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(output)
            print(f"Results written to {args.output}")
        except Exception as e:
            print(f"Error writing output file: {e}", file=sys.stderr)
            return 1
    else:
        print(output)

    all_valid = all(r.is_valid for r in results)
    return 0 if all_valid else 1


if __name__ == '__main__':
    sys.exit(main())
