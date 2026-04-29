#!/usr/bin/env python3
"""
Command-line tool for envelope operations (wrap, unwrap, validate).

Usage:
    python envelope_tool.py wrap <input.json> <output.json> <type>
    python envelope_tool.py unwrap <input.json> <output.json>
    python envelope_tool.py validate <envelope.json> <schema.json> [common-defs.json]
    python envelope_tool.py convert <input.json> <output.json> [--wrap|--unwrap]
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict

from envelope import Envelope, wrap_payload, unwrap_and_validate, _load_json_file


def cmd_wrap(args: argparse.Namespace) -> int:
    """Wrap a payload in an envelope."""
    input_path = Path(args.input)
    output_path = Path(args.output)
    envelope_type = args.type

    if not input_path.exists():
        print(f"Input file not found: {input_path}", file=sys.stderr)
        return 1

    try:
        payload = _load_json_file(input_path)
        envelope_dict = wrap_payload(payload, envelope_type)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(envelope_dict, f, indent=2)

        print(f"✓ Wrapped payload in envelope: {output_path}")
        print(f"  Type: {envelope_type}")
        return 0

    except ValueError as e:
        print(f"✗ Envelope error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        return 1


def cmd_unwrap(args: argparse.Namespace) -> int:
    """Unwrap a payload from an envelope."""
    input_path = Path(args.input)
    output_path = Path(args.output)

    if not input_path.exists():
        print(f"Input file not found: {input_path}", file=sys.stderr)
        return 1

    try:
        envelope_data = _load_json_file(input_path)
        envelope = Envelope.from_dict(envelope_data)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(envelope.payload, f, indent=2)

        print(f"✓ Unwrapped payload from envelope: {output_path}")
        print(f"  Type: {envelope.type}")
        return 0

    except ValueError as e:
        print(f"✗ Invalid envelope: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        return 1


def cmd_validate(args: argparse.Namespace) -> int:
    """Validate an envelope against a schema."""
    envelope_path = Path(args.envelope)
    schema_path = Path(args.schema)
    common_defs_path = Path(args.common_defs) if args.common_defs else None

    if not envelope_path.exists():
        print(f"Envelope file not found: {envelope_path}", file=sys.stderr)
        return 1

    if not schema_path.exists():
        print(f"Schema file not found: {schema_path}", file=sys.stderr)
        return 1

    try:
        envelope_data = _load_json_file(envelope_path)
        success, payload, message = unwrap_and_validate(
            envelope_data, schema_path, common_defs_path
        )

        print(message)
        return 0 if success else 1

    except Exception as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        return 1


def cmd_convert(args: argparse.Namespace) -> int:
    """Convert between envelope and plain JSON formats."""
    input_path = Path(args.input)
    output_path = Path(args.output)

    if not input_path.exists():
        print(f"Input file not found: {input_path}", file=sys.stderr)
        return 1

    try:
        input_data = _load_json_file(input_path)

        # Detect if input is an envelope
        is_envelope = (
            isinstance(input_data, dict)
            and "type" in input_data
            and "schema" in input_data
            and "payload" in input_data
        )

        # Determine operation if not explicitly specified
        if args.wrap is True:
            operation = "wrap"
        elif args.unwrap is True:
            operation = "unwrap"
        else:
            operation = "unwrap" if is_envelope else "wrap"

        output_path.parent.mkdir(parents=True, exist_ok=True)

        if operation == "wrap":
            envelope_dict = wrap_payload(input_data, args.type or "bench-centric.v1")
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(envelope_dict, f, indent=2)
            print(f"✓ Converted to envelope: {output_path}")

        else:  # unwrap
            envelope = Envelope.from_dict(input_data)
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(envelope.payload, f, indent=2)
            print(f"✓ Converted from envelope: {output_path}")

        return 0

    except ValueError as e:
        print(f"✗ Conversion error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        return 1


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Envelope utility for wrapping/unwrapping JSON payloads"
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # wrap command
    wrap_parser = subparsers.add_parser("wrap", help="Wrap a payload in an envelope")
    wrap_parser.add_argument("input", help="Input JSON file")
    wrap_parser.add_argument("output", help="Output envelope file")
    wrap_parser.add_argument(
        "type",
        choices=["bench-centric.v1", "set-centric.v1"],
        help="Envelope type",
    )
    wrap_parser.set_defaults(func=cmd_wrap)

    # unwrap command
    unwrap_parser = subparsers.add_parser(
        "unwrap", help="Unwrap a payload from an envelope"
    )
    unwrap_parser.add_argument("input", help="Input envelope file")
    unwrap_parser.add_argument("output", help="Output payload file")
    unwrap_parser.set_defaults(func=cmd_unwrap)

    # validate command
    validate_parser = subparsers.add_parser(
        "validate", help="Validate an envelope against a schema"
    )
    validate_parser.add_argument("envelope", help="Envelope JSON file")
    validate_parser.add_argument("schema", help="Schema JSON file")
    validate_parser.add_argument(
        "common_defs", nargs="?", help="Common definitions JSON file (optional)"
    )
    validate_parser.set_defaults(func=cmd_validate)

    # convert command
    convert_parser = subparsers.add_parser(
        "convert", help="Convert between envelope and plain JSON"
    )
    convert_parser.add_argument("input", help="Input JSON file")
    convert_parser.add_argument("output", help="Output JSON file")
    convert_parser.add_argument(
        "--wrap", action="store_true", help="Force wrap operation"
    )
    convert_parser.add_argument(
        "--unwrap", action="store_true", help="Force unwrap operation"
    )
    convert_parser.add_argument(
        "--type",
        choices=["bench-centric.v1", "set-centric.v1"],
        default="bench-centric.v1",
        help="Envelope type for wrapping (default: bench-centric.v1)",
    )
    convert_parser.set_defaults(func=cmd_convert)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    return int(args.func(args))


if __name__ == "__main__":
    sys.exit(main())
