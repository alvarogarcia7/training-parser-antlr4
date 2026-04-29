#!/usr/bin/env python3
"""
Validate bench-centric example with envelope against its schema.
"""

import sys
from pathlib import Path

from envelope import unwrap_and_validate, _load_json_file


def validate_envelope_bench_centric() -> int:
    """Validate the bench-centric envelope example against its schema."""
    envelope_path = Path("data/bench-centric-example.json")
    payload_schema_path = Path("schema/bench-centric.schema.json")
    common_defs_path = Path("schema/common-definitions.schema.json")

    if not envelope_path.exists():
        print(f"Envelope file not found: {envelope_path}", file=sys.stderr)
        return 1

    try:
        envelope_data = _load_json_file(envelope_path)
        success, payload, message = unwrap_and_validate(
            envelope_data, payload_schema_path, common_defs_path
        )

        if success:
            print(message)
            return 0
        else:
            print(message, file=sys.stderr)
            return 1

    except Exception as e:
        print(f"Error reading envelope: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(validate_envelope_bench_centric())
