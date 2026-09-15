"""Python API layer for the Training Parser PWA.

This module is loaded inside a Pyodide Web Worker. It exposes
parse/validate/stats functions that are called from JavaScript.
All I/O uses in-memory strings (no real filesystem access needed).
"""

import json
from typing import Any


def parse_workout_text(text: str) -> str:
    """Parse workout text and return JSON with exercises and errors."""
    from antlr4 import CommonTokenStream, InputStream
    from dist.trainingLexer import trainingLexer
    from dist.trainingParser import trainingParser as TrainingParser
    from parser.parser import Formatter
    from parser.error_listener import TrainingErrorListener
    from parser.standardize_name import StandardizeName

    input_stream = InputStream(text)
    lexer = trainingLexer(input_stream)
    stream = CommonTokenStream(lexer)
    tp = TrainingParser(stream)

    error_listener = TrainingErrorListener()
    lexer.removeErrorListeners()
    lexer.addErrorListener(error_listener)
    tp.removeErrorListeners()
    tp.addErrorListener(error_listener)

    tree = tp.workout()
    formatter = Formatter()
    formatter.visit(tree)

    standardizer = StandardizeName('data/synonyms.yaml')

    exercises_out = []
    for ex in formatter.result:
        sets_out = []
        for s in ex.sets_:
            sets_out.append({
                "repetitions": s.repetitions,
                "weight": {
                    "amount": s.weight.amount,
                    "unit": s.weight.unit,
                },
                "rir": s.rir,
            })
        exercises_out.append({
            "name": standardizer.run(ex.name),
            "sets": sets_out,
        })

    errors_out = [
        {
            "line": e.line,
            "column": e.column,
            "message": e.message,
        }
        for e in error_listener.errors
    ]

    return json.dumps({
        "exercises": exercises_out,
        "errors": errors_out,
        "is_valid": len(errors_out) == 0,
        "total_exercises": len(exercises_out),
        "total_sets": sum(len(ex["sets"]) for ex in exercises_out),
    })


def get_statistics(exercises_json: str, time_minutes: float) -> str:
    """Calculate workout statistics from exercises JSON."""
    from src.statistics import StatisticsCalculator, WorkoutStats

    exercises_data = json.loads(exercises_json)
    stats = StatisticsCalculator.from_json_workouts(
        [{"exercises": exercises_data}],
        time_minutes=time_minutes,
    )
    return json.dumps(stats.to_dict())


def format_statistics(exercises_json: str, time_minutes: float) -> str:
    """Return human-readable statistics string."""
    from src.statistics import StatisticsCalculator

    exercises_data = json.loads(exercises_json)
    stats = StatisticsCalculator.from_json_workouts(
        [{"exercises": exercises_data}],
        time_minutes=time_minutes,
    )
    return StatisticsCalculator.format_stats(stats)


def serialize_to_set_centric_json(exercises_json: str, date_str: str) -> str:
    """Serialize parsed exercises to set-centric JSON format (no schema validation)."""
    exercises_data = json.loads(exercises_json)
    exercise_blocks = []
    for ex_data in exercises_data:
        sets = []
        for idx, s in enumerate(ex_data["sets"], start=1):
            w = s["weight"]
            set_dict: dict[str, Any] = {
                "setNumber": idx,
                "repetitions": s["repetitions"],
                "weight": {"amount": w["amount"], "unit": w["unit"]},
            }
            if s.get("rir") is not None:
                set_dict["rir"] = s["rir"]
            sets.append(set_dict)
        exercise_blocks.append({
            "name": ex_data["name"],
            "equipment": "other",
            "sets": sets,
        })

    result: dict[str, Any] = {
        "type": "set-centric",
        "date": date_str,
        "location": "",
        "notes": "",
        "statistics": {},
        "exercises": exercise_blocks,
    }
    return json.dumps(result, indent=2)
