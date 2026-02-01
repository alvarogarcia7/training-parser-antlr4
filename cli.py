#!/usr/bin/env python3
"""
Unified CLI program for parsing and exporting training exercise data.

Provides multiple subcommands:
- parse: Parse a training log file and display exercises
- export: Parse and export to JSON format with optional validation
- batch: Parse multi-session file and export to TSV format
"""

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any

from src.data_access import DataAccess, DataSerializer, ParsedWorkoutSession
from schema_validator import validate_json_with_schema


def parse_command(args: Any) -> None:
    """Parse a training log file and display exercises."""
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    try:
        data_access = DataAccess()
        exercises = data_access.parse_single_file(str(input_path))

        if args.format == "json":
            json_data = DataSerializer.to_set_centric_json(exercises)
            output = json.dumps(json_data, indent=2)
        elif args.format == "text":
            output = "\n".join(repr(ex) for ex in exercises)
        else:
            raise ValueError(f"Unknown format: {args.format}")

        print(output)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def export_command(args: Any) -> None:
    """Parse and export to JSON format with optional schema validation."""
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    if args.format not in ["set-centric", "bench-centric"]:
        print(f"Error: Format must be 'set-centric' or 'bench-centric'", file=sys.stderr)
        sys.exit(1)

    try:
        data_access = DataAccess()
        exercises = data_access.parse_single_file(str(input_path))

        # Currently only set-centric is implemented
        json_data = DataSerializer.to_set_centric_json(exercises)
        json_output = json.dumps(json_data, indent=2)

        if args.output:
            output_path = Path(args.output)
            output_path.write_text(json_output, encoding='utf-8')

            if args.validate:
                schema_file = f"schema/{args.format}.schema.json"
                schema_path = Path(schema_file)
                common_defs_path = Path("schema/common-definitions.schema.json")

                if schema_path.exists():
                    success, message = validate_json_with_schema(
                        schema_path,
                        output_path,
                        common_defs_path if common_defs_path.exists() else None
                    )

                    if success:
                        print(message)
                    else:
                        print(message, file=sys.stderr)
                        sys.exit(1)
                else:
                    print(f"Warning: Schema file not found at {schema_path}", file=sys.stderr)
                    print(f"Output written to: {output_path}")
            else:
                print(f"Output written to: {output_path}")
        else:
            print(json_output)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def batch_command(args: Any) -> None:
    """Parse multi-session file and export to TSV or JSON."""
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    try:
        data_access = DataAccess()
        sessions = data_access.parse_multi_session_file(str(input_path))

        if args.format == "tsv":
            rows = DataSerializer.to_tsv_rows(sessions)
            _write_tsv_output(rows, args.output)
        elif args.format == "json":
            _write_json_sessions_output(sessions, args.output)
        else:
            raise ValueError(f"Unknown format: {args.format}")

        if args.output:
            print(f"Output written to: {args.output}")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def _write_tsv_output(rows: list[list[str]], output_path: str | None) -> None:
    """Write TSV rows to file or stdout."""
    if output_path:
        with open(output_path, mode='w+', newline='') as f:
            csv_writer = csv.writer(f, delimiter='\t', quotechar='"')
            csv_writer.writerows(rows)
    else:
        for row in rows:
            print('\t'.join(row))


def _write_json_sessions_output(sessions: list[ParsedWorkoutSession], output_path: str | None) -> None:
    """Convert sessions to JSON format and write to file or stdout."""
    # Convert sessions to JSON-serializable format
    sessions_json = []
    for session in sessions:
        session_dict = {
            'date': session['date'],
            'notes': session['notes'],
            'exercises': [
                {
                    'name': ex.name,
                    'sets': [
                        {
                            'repetitions': s.repetitions,
                            'weight': {
                                'amount': s.weight.amount,
                                'unit': s.weight.unit
                            }
                        }
                        for s in ex.sets_
                    ]
                }
                for ex in session['parsed']
            ]
        }
        sessions_json.append(session_dict)

    output = json.dumps(sessions_json, indent=2)

    if output_path:
        Path(output_path).write_text(output, encoding='utf-8')
    else:
        print(output)


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Parse and export training exercise data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s parse training.txt
  %(prog)s parse training.txt --format json
  %(prog)s export training.txt -o output.json --validate
  %(prog)s batch multi-session.txt -o sessions.tsv
  %(prog)s batch multi-session.txt --format json
        """.strip()
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Parse command
    parse_parser = subparsers.add_parser('parse', help='Parse a single file')
    parse_parser.add_argument('input', help='Input training log file')
    parse_parser.add_argument(
        '--format',
        choices=['text', 'json'],
        default='text',
        help='Output format (default: text)'
    )
    parse_parser.set_defaults(func=parse_command)

    # Export command
    export_parser = subparsers.add_parser('export', help='Export to JSON with validation')
    export_parser.add_argument('input', help='Input training log file')
    export_parser.add_argument(
        '-o', '--output',
        default=None,
        help='Output JSON file (prints to stdout if not provided)'
    )
    export_parser.add_argument(
        '--format',
        choices=['set-centric', 'bench-centric'],
        default='set-centric',
        help='JSON format to export (default: set-centric)'
    )
    export_parser.add_argument(
        '--no-validate',
        action='store_false',
        dest='validate',
        help='Skip schema validation'
    )
    export_parser.set_defaults(func=export_command)

    # Batch command
    batch_parser = subparsers.add_parser('batch', help='Parse multi-session file')
    batch_parser.add_argument('input', help='Input training log file with multiple sessions')
    batch_parser.add_argument(
        '-o', '--output',
        default=None,
        help='Output file (prints to stdout if not provided)'
    )
    batch_parser.add_argument(
        '--format',
        choices=['tsv', 'json'],
        default='tsv',
        help='Output format (default: tsv)'
    )
    batch_parser.set_defaults(func=batch_command)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    args.func(args)


if __name__ == "__main__":
    main()
