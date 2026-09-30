#!/usr/bin/env python3
"""CLI tool for detecting training seasons.

A season ends when there is a break of at least ``min_break_days`` days
without a training session (configured in ``config/seasons.yaml``); the next
session after the break starts a new season.

For each season, every exercise gets an estimated 1RM (Brzycki formula, best
set of the season) and each set is reported as a percentage of that 1RM.

Input: a directory with one or more set-centric JSON files.

Usage:
    python scripts/detect_seasons.py <input_directory> [--config FILE] [--min-break-days N]
                                     [--min-sessions N] [--format text|json]
"""

import argparse
import json
import sys
from dataclasses import replace
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import jsonschema  # noqa: E402

from src.seasons import (  # noqa: E402
    DEFAULT_CONFIG_PATH,
    SeasonConfig,
    SeasonReport,
    analyse_seasons,
    format_report,
    sessions_from_directory,
    validate_report_dict,
)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Detect training seasons separated by breaks without training",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Seasons from a directory of set-centric JSON files
  python scripts/detect_seasons.py data/parsed/

  # Custom config file
  python scripts/detect_seasons.py data/parsed/ --config my-seasons.yaml

  # Override the minimum break from the command line
  python scripts/detect_seasons.py data/parsed/ --min-break-days 30 --format json
        """,
    )
    parser.add_argument(
        "input", type=Path, help="Directory with set-centric JSON files (searched recursively)"
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG_PATH,
        help=f"Season config YAML (default: {DEFAULT_CONFIG_PATH.name} in config/)",
    )
    parser.add_argument("--min-break-days", type=int, help="Override min_break_days from config")
    parser.add_argument("--min-sessions", type=int, help="Override min_sessions from config")
    parser.add_argument(
        "--max-reps-for-1rm", type=int, help="Override max_reps_for_1rm from config"
    )
    parser.add_argument("--format", choices=["text", "json"], default="text")
    return parser.parse_args(argv)


def build_config(args: argparse.Namespace) -> SeasonConfig:
    """Load the season configuration from file or defaults, applying CLI overrides."""
    config = SeasonConfig.load(args.config) if args.config.exists() else SeasonConfig()
    if args.min_break_days is not None:
        config = replace(config, min_break_days=args.min_break_days)
    if args.min_sessions is not None:
        config = replace(config, min_sessions=args.min_sessions)
    if args.max_reps_for_1rm is not None:
        config = replace(config, max_reps_for_1rm=args.max_reps_for_1rm)
    return config


def run_analysis(input_dir: Path, config: SeasonConfig) -> SeasonReport:
    """Parse set-centric JSON sessions from a directory and detect seasons."""
    return analyse_seasons(sessions_from_directory(input_dir), config)


def format_output(report: SeasonReport, data: dict[str, Any], fmt: str) -> str:
    """Render an already-validated season report as text or JSON.

    `data` must be `report.to_dict()`, already validated against the season
    report schema. No parsing, analysis or validation happens here.
    """
    if fmt == "json":
        return json.dumps(data, indent=2)
    return format_report(report)


def main(argv: list[str] | None = None) -> int:
    """Main CLI entry point."""
    args = parse_args(argv)

    try:
        config = build_config(args)
        report = run_analysis(args.input, config)
    except (OSError, ValueError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    data = report.to_dict()
    try:
        validate_report_dict(data)
    except jsonschema.exceptions.ValidationError as e:
        print(f"Error: generated report does not match schema/season_report.schema.json: {e}", file=sys.stderr)
        return 1

    print(format_output(report, data, args.format))
    return 0


if __name__ == "__main__":
    sys.exit(main())
