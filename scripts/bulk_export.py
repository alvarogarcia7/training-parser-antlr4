#!/usr/bin/env python3
"""
Bulk export utilities for training parser data.
Exports parsed exercise data to bench-centric and set-centric JSON formats.
"""

import sys
import json
from pathlib import Path
from typing import Any

from src.data_access import DataAccess


def export_bench_centric(input_file: str, output_file: str) -> None:
    """Export training data to bench-centric JSON format.

    Args:
        input_file: Path to input training text file
        output_file: Path to output JSON file

    Raises:
        Exception: If processing fails
    """
    try:
        data_access = DataAccess()
        exercises = data_access.parse_single_file(input_file)

        bench_data: dict[str, Any] = {
            "type": "bench-centric.v1",
            "benches": [
                {
                    "name": "default",
                    "exercises": [
                        {
                            "name": exercise.name,
                            "sets": [
                                {
                                    "reps": set_.repetitions,
                                    "weight": {
                                        "amount": set_.weight.amount,
                                        "unit": set_.weight.unit
                                    }
                                }
                                for set_ in exercise.sets_
                            ]
                        }
                        for exercise in exercises
                    ]
                }
            ]
        }

        Path(output_file).write_text(json.dumps(bench_data, indent=2))
    except Exception as e:
        print(f"Error processing {input_file}: {e}", file=sys.stderr)
        raise


def append_to_database(json_file: str, database_file: str) -> None:
    """Append parsed exercise data to consolidated database.

    Args:
        json_file: Path to JSON file with exercise data
        database_file: Path to database JSON file

    Raises:
        Exception: If appending fails
    """
    try:
        with open(json_file) as f:
            new_data = json.load(f)

        with open(database_file) as f:
            db = json.load(f)

        if "exercises" in new_data:
            db["workouts"].append({
                "source_file": json_file,
                "exercises": new_data["exercises"]
            })

        with open(database_file, 'w') as f:
            json.dump(db, f, indent=2)
    except Exception as e:
        print(f"Error appending to database: {e}", file=sys.stderr)
        raise
