#!/usr/bin/env python3
"""
Executable script to parse workout training logs and export to JSON format.

Parses a training log file, converts it to set-centric JSON format,
validates against schema, and writes the output.
"""

import argparse
import json
import sys
from pathlib import Path

from main import parse_file
from parser.serializer import serialize_to_set_centric
from schema_validator import validate_json_with_schema


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Parse workout training log and export to JSON format"
    )
    parser.add_argument(
        "input",
        type=str,
        help="Path to the input training log file"
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        default=None,
        help="Path to the output JSON file (optional, prints to stdout if not provided)"
    )
    
    args = parser.parse_args()
    
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)
    
    try:
        exercises = parse_file(str(input_path))
        
        json_data = serialize_to_set_centric(exercises)
        
        json_output = json.dumps(json_data, indent=2)
        
        if args.output:
            output_path = Path(args.output)
            output_path.write_text(json_output, encoding='utf-8')
            
            schema_path = Path("schema/set-centric.schema.json")
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
                print(f"Warning: Schema file not found at {schema_path}, skipping validation", file=sys.stderr)
                print(f"Output written to: {output_path}")
        else:
            print(json_output)
            
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
