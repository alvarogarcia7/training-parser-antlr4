"""PWA API bridge: exposes parser/statistics functions to pyodide-worker.js."""
import json
import datetime
from datetime import timezone

from parser.parser import TrainingParser
from parser.model import Exercise, Set_, Weight
from parser.serializer import serialize_to_set_centric
from src.statistics import StatisticsCalculator
from antlr4 import InputStream


def _parse(text: str):
    """Return (exercises, errors_list) from raw text."""
    from parser.parser import TrainingParser
    p = TrainingParser(InputStream(text))
    result = p.parse()
    errors = [
        {"line": e.line, "column": e.column, "message": e.message}
        for e in result.errors
    ]
    return result.exercises, errors


def _exercises_to_payload_list(exercises):
    """Convert Exercise list to set-centric payload exercises format."""
    out = []
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
        out.append({"name": ex.name, "equipment": "other", "sets": sets})
    return out


def _compute_totals(exercises):
    """Compute totals + per_exercise breakdown for ui.js renderParseResult."""
    per_exercise = []
    total_sets = 0
    total_volume = 0.0
    for ex in exercises:
        flat_list = ex.flatten()
        for flat_ex in flat_list:
            sets = flat_ex.sets_
            vol = sum(s.weight.amount * s.repetitions for s in sets)
            details = ", ".join(
                f"{s.repetitions}\u00d7{s.weight.amount}{s.weight.unit}" for s in sets
            )
            per_exercise.append({
                "name": flat_ex.name,
                "sets": len(sets),
                "volume_kg": vol,
                "details": details,
            })
            total_sets += len(sets)
            total_volume += vol
    return {
        "total_exercises": len(per_exercise),
        "total_sets": total_sets,
        "total_volume_kg": total_volume,
        "per_exercise": per_exercise,
    }


def _make_tsv(exercises, date_str: str) -> str:
    """Build a tab-separated export row per exercise group."""
    today = datetime.date.today().isoformat()
    rows = ["\t".join(["Date", "Exercise", "Sets", "Avg Reps", "Weight", "Notes"])]
    for ex in exercises:
        for flat_ex in ex.flatten():
            reps = [s.repetitions for s in flat_ex.sets_]
            avg_reps = int(sum(reps) / len(reps)) if reps else 0
            weight = flat_ex.sets_[0].weight.amount if flat_ex.sets_ else 0
            rows.append("\t".join([
                date_str,
                flat_ex.name,
                str(len(reps)),
                str(avg_reps),
                f"{weight:.1f}".replace(".", ","),
                f"Origen=training-parser (ANTLR) ({today}.txt)",
            ]))
    return "\n".join(rows)


def parse_and_export(text: str, date_str: str = "") -> str:
    exercises, errors = _parse(text)

    ts = None
    if date_str:
        try:
            ts = datetime.datetime.fromisoformat(date_str).replace(tzinfo=timezone.utc)
        except ValueError:
            pass
    if ts is None:
        ts = datetime.datetime.now(timezone.utc)

    payload = serialize_to_set_centric(exercises, ts)

    envelope = {
        "type": "set-centric.v1",
        "schema": "http://com.trainingparser/set-centric_v1.schema.json",
        "payload": payload,
    }

    totals = _compute_totals(exercises)
    tsv = _make_tsv(exercises, date_str or ts.date().isoformat())

    result = {
        "envelope": envelope,
        "envelope_pretty": json.dumps(envelope, indent=2),
        "errors": errors,
        "is_valid": len(errors) == 0,
        "totals": totals,
        "tsv": tsv,
    }
    return json.dumps(result)


def parse_workout_text(text: str) -> str:
    exercises, errors = _parse(text)
    out = []
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
        out.append({"name": ex.name, "sets": sets})
    return json.dumps(out)


def get_statistics(exercises_json: str, time_minutes: float) -> str:
    workouts = json.loads(exercises_json)
    if isinstance(workouts, list) and workouts and "name" in workouts[0]:
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
    ts = None
    if date_str:
        try:
            ts = datetime.datetime.fromisoformat(date_str).replace(tzinfo=timezone.utc)
        except ValueError:
            pass
    if ts is None:
        ts = datetime.datetime.now(timezone.utc)

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
