#!/usr/bin/env python3
"""CLI tool for parsing body-composition (weight) notes into CSV.

Usage:
    python bin/weight_parser.py <input_file> --year YYYY [--end "Mi Fit"] [-o OUTPUT.csv]
"""

import argparse
import sys
from pathlib import Path

from src.data_access import DataReader
from src.weight_parser import SingleMeasurementWeightParser, WeightParser, write_csv


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Parse body-composition measurements (one note per measurement) into CSV.",
    )
    parser.add_argument("input_file", type=Path, help="Text file with the measurements")
    parser.add_argument("--year", required=True, help="Year of the measurements (the notes only contain day/month)")
    parser.add_argument("--end", default="Mi Fit", help="Marker line that ends a measurement (default: Mi Fit)")
    parser.add_argument("-o", "--output", type=Path, help="Output CSV file (default: <input>.csv)")
    args = parser.parse_args()

    try:
        lines = DataReader.read_lines(str(args.input_file))
        parsed = WeightParser(args.end, SingleMeasurementWeightParser(args.year)).parse(lines)
    except (AssertionError, OSError) as e:
        print(f"Error parsing {args.input_file}: {e}", file=sys.stderr)
        sys.exit(1)

    output = args.output or args.input_file.with_suffix(".csv")
    write_csv(output, parsed)
    print(f"Parsed {len(parsed)} measurements -> {output}")


if __name__ == "__main__":
    main()
