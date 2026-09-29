#!/usr/bin/env python3
"""CLI tool for calculating and displaying workout statistics.

Usage:
    python scripts/workout_stats.py <input_file> [--time MINUTES] [--format json|text]
    python scripts/workout_stats.py --database <db_file> [--time MINUTES] [--format json|text]
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from src.statistics import StatisticsCalculator, WorkoutStats


def load_json_file(file_path: Path) -> Any:
    """Load JSON file."""
    try:
        with open(file_path) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading {file_path}: {e}", file=sys.stderr)
        sys.exit(1)


def stats_from_set_centric(data: dict[str, Any], time_minutes: float) -> WorkoutStats:
    """Create stats from set-centric JSON format."""
    exercises = data.get("exercises", [])
    return StatisticsCalculator.from_json_workouts([{"exercises": exercises}], time_minutes)


def stats_from_database(data: dict[str, Any], time_minutes: float) -> WorkoutStats:
    """Create stats from database.json format."""
    workouts = data.get("workouts", [])
    return StatisticsCalculator.from_json_workouts(workouts, time_minutes)


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Calculate and display workout statistics",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Stats for a single parsed workout
  python scripts/workout_stats.py data/parsed/workout_set.json

  # Stats with workout duration
  python scripts/workout_stats.py data/parsed/workout_set.json --time 60

  # Stats for entire database
  python scripts/workout_stats.py --database data/parsed/database.json --time 300

  # Output as JSON
  python scripts/workout_stats.py data/parsed/workout_set.json --format json
        """,
    )

    parser.add_argument(
        "input",
        nargs="?",
        help="Input JSON file (set-centric format)",
    )
    parser.add_argument(
        "-d", "--database",
        type=str,
        help="Path to database.json file",
    )
    parser.add_argument(
        "-t", "--time",
        type=float,
        default=0.0,
        help="Workout duration in minutes (default: 0)",
    )
    parser.add_argument(
        "-f", "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )

    args = parser.parse_args()

    # Validate inputs
    if not args.input and not args.database:
        parser.print_help()
        sys.exit(1)

    # Load data and calculate stats
    if args.database:
        data = load_json_file(Path(args.database))
        stats = stats_from_database(data, args.time)
    else:
        data = load_json_file(Path(args.input))
        stats = stats_from_set_centric(data, args.time)

    # Output
    if args.format == "json":
        print(json.dumps(stats.to_dict(), indent=2))
    else:
        print(StatisticsCalculator.format_stats(stats))


if __name__ == "__main__":
    main()
