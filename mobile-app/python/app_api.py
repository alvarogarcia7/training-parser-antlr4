"""PWA API bridge: exposes parser/statistics functions to pyodide-worker.js."""
import json
from datetime import datetime, timezone

from src.data_access import DataParser, DataSerializer
from src.statistics import StatisticsCalculator
from parser.serializer import serialize_to_set_centric


def _exercises_to_json(exercises):
    """Convert Exercise list to JSON-serialisable list of dicts."""
    result = []
    for ex in exercises:
        sets = []
        for i, s in enumerate(ex.sets_, start=1):
            set_dict = {
                "setNumber": i,
                "repetitions": s.repetitions,
                "weight": {"amount": s.weight.amount, "unit": s.weight.unit},
            }
            if s.rir is not None:
                set_dict["rir"] = s.rir
            sets.append(set_dict)
        result.append({"name": ex.name, "sets": sets})
    return result


def parse_workout_text(text: str) -> str:
    exercises = DataParser.parse_raw_text(text)
    return json.dumps(_exercises_to_json(exercises))


def parse_and_export(text: str, date_str: str = "") -> str:
    exercises = DataParser.parse_raw_text(text)
    ts = None
    if date_str:
        try:
            ts = datetime.fromisoformat(date_str).replace(tzinfo=timezone.utc)
        except ValueError:
            pass
    result = serialize_to_set_centric(exercises, ts)
    return json.dumps(result)


def get_statistics(exercises_json: str, time_minutes: float) -> str:
    workouts = json.loads(exercises_json)
    if isinstance(workouts, list) and workouts and "name" in workouts[0]:
        # flat list of exercises
        stats = StatisticsCalculator.from_json_workouts(
            [{"exercises": workouts}], time_minutes
        )
    else:
        stats = StatisticsCalculator.from_json_workouts(workouts, time_minutes)
    return json.dumps(stats.to_dict())


def format_statistics(exercises_json: str, time_minutes: float) -> str:
    workouts = json.loads(exercises_json)
    if isinstance(workouts, list) and workouts and "name" in workouts[0]:
        stats = StatisticsCalculator.from_json_workouts(
            [{"exercises": workouts}], time_minutes
        )
    else:
        stats = StatisticsCalculator.from_json_workouts(workouts, time_minutes)
    return StatisticsCalculator.format_stats(stats)


def serialize_to_set_centric_json(exercises_json: str, date_str: str = "") -> str:
    workouts = json.loads(exercises_json)
    # If already in serialized exercise-dict form, just wrap and return
    ts = None
    if date_str:
        try:
            ts = datetime.fromisoformat(date_str).replace(tzinfo=timezone.utc)
        except ValueError:
            pass
    if ts is None:
        ts = datetime.now(timezone.utc)

    # exercises_json is a list of {name, sets} dicts (from parse_workout_text output)
    # Reconstruct Exercise objects
    from parser.model import Exercise, Set_, Weight
    exercises = []
    for ex_dict in workouts:
        sets = []
        for s in ex_dict.get("sets", []):
            w = s["weight"]
            sets.append(Set_(
                repetitions=s["repetitions"],
                weight=Weight(amount=w["amount"], unit=w["unit"]),
                rir=s.get("rir"),
            ))
        exercises.append(Exercise(name=ex_dict["name"], sets_=sets))

    result = serialize_to_set_centric(exercises, ts)
    return json.dumps(result)
