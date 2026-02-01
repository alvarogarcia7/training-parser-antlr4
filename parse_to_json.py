"""
Parse training data from text file into JSON format.

Step 1 of 2-step process:
- Read text file
- Parse exercises using ANTLR
- Replace/standardize exercise names
- Output as JSON
"""
import json
import os
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
from zoneinfo import ZoneInfo

from parser import Exercise
from splitter import Splitter


@dataclass
class ParsedWorkoutSession:
    """Parsed workout with exercises and metadata."""
    date: str
    parsed: list[Exercise]
    notes: str

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'date': self.date,
            'parsed': self.parsed,
            'notes': self.notes
        }


class ParseToJson:
    """Parse training data to JSON format using Splitter's parsing logic."""

    def __init__(self) -> None:
        self.splitter = Splitter()

    def main(self, file: str) -> list[ParsedWorkoutSession]:
        """Read, parse, and standardize names from a training file."""
        # Use Splitter's main method to parse the file
        parsed_sessions = self.splitter.main(file)

        # Convert to ParsedWorkoutSession dataclass format
        result: list[ParsedWorkoutSession] = []
        for session in parsed_sessions:
            result.append(ParsedWorkoutSession(
                date=session['date'],
                parsed=session['parsed'],
                notes=session['notes']
            ))
        return result

    @staticmethod
    def _serialize_exercise(exercise: Exercise) -> dict[str, Any]:
        """Convert an Exercise object to a JSON-serializable dict."""
        sets = []
        for idx, set_ in enumerate(exercise.sets_, start=1):
            sets.append({
                "setNumber": idx,
                "repetitions": set_.repetitions,
                "weight": {
                    "amount": set_.weight.amount,
                    "unit": set_.weight.unit
                }
            })

        return {
            "name": exercise.name,
            "equipment": "other",
            "sets": sets
        }

    @staticmethod
    def _serialize_workout(workout: ParsedWorkoutSession) -> dict[str, Any]:
        """Convert a ParsedWorkoutSession to a JSON-serializable dict."""
        workout_id = f"w_{workout.date.replace('-', '')}_000000"

        exercise_blocks = [
            ParseToJson._serialize_exercise(exercise)
            for exercise in workout.parsed
        ]

        return {
            "workout_id": workout_id,
            "type": "set-centric",
            "date": workout.date,
            "location": "",
            "notes": workout.notes,
            "statistics": {},
            "exercises": exercise_blocks
        }

    def to_json(self, workouts: list[ParsedWorkoutSession], output_file: str) -> None:
        """Write parsed workouts to JSON file."""
        # Get timezone from TZ environment variable, default to UTC
        tz_str = os.environ.get('TZ', 'UTC')
        try:
            tz = ZoneInfo(tz_str)
        except KeyError:
            tz = timezone.utc

        timestamp = datetime.now(tz)

        workout_list = [
            self._serialize_workout(workout)
            for workout in workouts
        ]

        output = {
            "export_timestamp": timestamp.isoformat(),
            "workouts": workout_list
        }

        with open(output_file, 'w') as f:
            json.dump(output, f, indent=2)


def main() -> None:
    """Parse training file and export to JSON."""
    if len(sys.argv) < 2:
        print("Usage: python3 parse_to_json.py <input_file> [--output <output_file>]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[3] if len(sys.argv) >= 4 and sys.argv[2] == '--output' else 'output.json'

    parser = ParseToJson()
    workouts = parser.main(input_file)
    parser.to_json(workouts, output_file)

    print(f"Exported to: {output_file}")


if __name__ == "__main__":
    main()
