"""
Parse training data from text file into JSON format.

Step 1 of 2-step process:
- Read text file
- Parse exercises using ANTLR
- Replace/standardize exercise names
- Output as JSON
"""
import json
import sys
from datetime import datetime, timezone
from typing import Any, TextIO, TypedDict, List

from antlr4 import InputStream, CommonTokenStream

from dist.trainingLexer import trainingLexer
from dist.trainingParser import trainingParser
from parser import Formatter, Exercise, StandardizeName

RawWorkoutSession = TypedDict('RawWorkoutSession', {
    'date': str,
    'payload': str,
    'notes': str})

ParsedWorkoutSession = TypedDict('ParsedWorkoutSession', {
    'date': str,
    'parsed': list[Exercise],
    'notes': str})


class ParseToJson:
    def main(self, file: str) -> list[ParsedWorkoutSession]:
        """Read, parse, and standardize names from a training file."""
        lines = self._read_all_lines(file)
        raw_exercises = self._group_exercises(lines)
        exercises = self._parse_exercises(raw_exercises)
        exercises = self._rename_exercises(exercises)
        return exercises

    def _parse_exercises(self, jobs: list[RawWorkoutSession]) -> list[ParsedWorkoutSession]:
        """Parse exercise payloads using ANTLR."""
        jobs2: list[ParsedWorkoutSession] = []
        for job in jobs:
            job_tmp: Any = job.copy()
            job_tmp['parsed'] = self._parse(job['payload'])
            jobs2.append(job_tmp)
        return jobs2

    @staticmethod
    def _parse(param: str) -> Any:
        """Parse exercise text using ANTLR grammar."""
        input_stream = InputStream(param)
        lexer = trainingLexer(input_stream)
        token_stream = CommonTokenStream(lexer)
        token_stream.fill()
        parser = trainingParser(token_stream)
        tree = parser.workout()

        formatter = Formatter()
        formatter.visit(tree)
        result = formatter.result
        return result

    @staticmethod
    def _group_exercises(lines: list[str]) -> list[RawWorkoutSession]:
        """Group lines by workout session (separated by blank lines)."""
        jobs: list[RawWorkoutSession] = []
        current: list[Any] = []
        notes: list[str] = []
        date: Any = None
        for idx in range(len(lines)):
            if lines[idx] == '':
                jobs.append(ParseToJson.build_job(current, date, notes))
                notes = []
                current = []
                date = None
                continue
            if lines[idx].startswith('#'):
                notes.append(lines[idx])
                continue
            if date is None:
                date = lines[idx]
                continue
            current.append(lines[idx])

        jobs.append(ParseToJson.build_job(current, date, notes))
        return jobs

    @staticmethod
    def build_job(current: List[Any], date: Any, notes: list[str]) -> RawWorkoutSession:
        """Build a workout session record."""
        current.append("")
        assert date is not None, f"current={current}, date={date}, notes={notes}"
        return {'date': date,
                'payload': "\n".join(current.copy()),
                'notes': "\n".join(notes.copy())
                }

    @staticmethod
    def _read_all_lines(file_name: str) -> list[str]:
        """Read all lines from a file."""
        lines: list[str] = []
        file_path: TextIO
        with open(file_name, 'r') as file_path:
            while True:
                line = file_path.readline()
                if not line:
                    break
                lines.append(line.rstrip())
        return lines

    @staticmethod
    def _rename_exercises(parsing2s: list[ParsedWorkoutSession]) -> list[ParsedWorkoutSession]:
        """Standardize exercise names."""
        renamer = StandardizeName()
        for parsing2 in parsing2s:
            for exercise in parsing2['parsed']:
                exercise.name = renamer.run(exercise.name)
        return parsing2s

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
    def _serialize_workout(workout: ParsedWorkoutSession, timestamp: datetime) -> dict[str, Any]:
        """Convert a ParsedWorkoutSession to a JSON-serializable dict."""
        workout_id = f"w_{workout['date'].replace('-', '')}_000000"

        exercise_blocks = [
            ParseToJson._serialize_exercise(exercise)
            for exercise in workout['parsed']
        ]

        return {
            "workout_id": workout_id,
            "type": "set-centric",
            "date": workout['date'],
            "location": "",
            "notes": workout['notes'],
            "statistics": {},
            "exercises": exercise_blocks
        }

    def to_json(self, workouts: list[ParsedWorkoutSession], output_file: str) -> None:
        """Write parsed workouts to JSON file."""
        timestamp = datetime.now(timezone.utc)

        workout_list = [
            self._serialize_workout(workout, timestamp)
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
