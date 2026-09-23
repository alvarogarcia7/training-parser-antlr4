"""Python API layer for the Training Parser PWA.

This module is loaded inside a Pyodide Web Worker. It exposes
parse/validate/stats functions that are called from JavaScript.
All I/O uses in-memory strings (no real filesystem access needed).
"""

import json
from datetime import datetime, timezone
from typing import Any


ENVELOPE_TYPE = "set-centric.v1"
ENVELOPE_SCHEMA = "http://com.trainingparser/set-centric_v1.schema.json"


def _iso_datetime(date_str: str) -> str:
    """Convert a YYYY-MM-DD (or ISO) string to an ISO date-time string."""
    if not date_str:
        return datetime.now(timezone.utc).isoformat()
    try:
        # Accept plain YYYY-MM-DD
        dt = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        return dt.isoformat()
    except ValueError:
        return date_str  # Assume caller passed a full ISO string


def _parse_to_exercises(text: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Parse workout text; return (exercises_dicts, errors_dicts).

    The exercises_dicts contain: name, sets[{repetitions, weight:{amount,unit}, rir?}].
    """
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

    exercises_out: list[dict[str, Any]] = []
    for ex in formatter.result:
        sets_out = []
        for s in ex.sets_:
            set_dict: dict[str, Any] = {
                "repetitions": s.repetitions,
                "weight": {"amount": s.weight.amount, "unit": s.weight.unit},
            }
            if s.rir is not None:
                set_dict["rir"] = s.rir
            sets_out.append(set_dict)
        exercises_out.append({"name": standardizer.run(ex.name), "sets": sets_out})

    errors_out = [
        {"line": e.line, "column": e.column, "message": e.message}
        for e in error_listener.errors
    ]
    return exercises_out, errors_out


def parse_workout_text(text: str) -> str:
    """Parse workout text and return JSON with exercises and errors."""
    exercises_out, errors_out = _parse_to_exercises(text)
    return json.dumps({
        "exercises": exercises_out,
        "errors": errors_out,
        "is_valid": len(errors_out) == 0,
        "total_exercises": len(exercises_out),
        "total_sets": sum(len(ex["sets"]) for ex in exercises_out),
    })


def _build_set_centric_payload(exercises: list[dict[str, Any]], date_str: str) -> dict[str, Any]:
    """Build the set-centric payload dict from parsed exercise dicts."""
    iso_date = _iso_datetime(date_str)
    workout_id = f"w_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"

    exercise_blocks = []
    for ex in exercises:
        sets = []
        for idx, s in enumerate(ex["sets"], start=1):
            set_dict: dict[str, Any] = {
                "setNumber": idx,
                "repetitions": s["repetitions"],
                "weight": {"amount": s["weight"]["amount"], "unit": s["weight"]["unit"]},
            }
            if s.get("rir") is not None:
                set_dict["rir"] = s["rir"]
            sets.append(set_dict)
        exercise_blocks.append({
            "name": ex["name"],
            "equipment": "other",
            "sets": sets,
        })

    return {
        "workout_id": workout_id,
        "type": "set-centric",
        "date": iso_date,
        "location": "",
        "notes": "",
        "statistics": {},
        "exercises": exercise_blocks,
    }


def _validate_envelope(envelope: dict[str, Any]) -> list[str]:
    """Validate envelope + inner payload against schemas. Returns errors as strings."""
    import jsonschema
    from pathlib import Path

    errors: list[str] = []

    env_schema_path = Path("/home/pyodide/schema/envelope-set-centric.schema.json")
    payload_schema_path = Path("/home/pyodide/schema/set-centric.schema.json")
    common_defs_path = Path("/home/pyodide/schema/common-definitions.schema.json")

    try:
        if env_schema_path.exists():
            with open(env_schema_path) as f:
                env_schema = json.load(f)
            jsonschema.Draft202012Validator(env_schema).validate(envelope)

        if payload_schema_path.exists() and common_defs_path.exists():
            with open(payload_schema_path) as f:
                payload_schema = json.load(f)
            with open(common_defs_path) as f:
                common_defs = json.load(f)
            resolver = jsonschema.RefResolver.from_schema(
                payload_schema, store={common_defs["$id"]: common_defs}
            )
            validator = jsonschema.Draft202012Validator(payload_schema, resolver=resolver)
            validator.validate(envelope["payload"])
    except jsonschema.ValidationError as e:
        errors.append(f"Schema validation: {e.message}")
    except Exception as e:  # noqa: BLE001
        errors.append(f"Validation error: {type(e).__name__}: {e}")

    return errors


def _compute_totals_from_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Compute totals/volumes purely from the JSON payload."""
    exercises = payload.get("exercises", [])
    per_exercise = []
    grand_volume = 0.0
    grand_sets = 0
    for ex in exercises:
        vol = 0.0
        for s in ex["sets"]:
            vol += s["weight"]["amount"] * s["repetitions"]
        per_exercise.append({
            "name": ex["name"],
            "sets": len(ex["sets"]),
            "volume_kg": vol,
            "details": ", ".join(
                f"{s['repetitions']}×{s['weight']['amount']}{s['weight']['unit']}"
                for s in ex["sets"]
            ),
        })
        grand_volume += vol
        grand_sets += len(ex["sets"])
    return {
        "per_exercise": per_exercise,
        "total_exercises": len(exercises),
        "total_sets": grand_sets,
        "total_volume_kg": grand_volume,
    }


def _tsv_from_payload(payload: dict[str, Any]) -> str:
    """Generate TSV output from the JSON payload (mirrors DataSerializer.to_tsv_rows).

    Groups consecutive same-weight, same-rep sets and emits one row each:
    Date, Exercise, Sets, Avg Reps, Weight, Notes
    """
    from itertools import groupby

    today = datetime.now(timezone.utc).date().isoformat()
    date = payload.get("date", "").split("T")[0] or today

    rows: list[list[str]] = [
        ["Date", "Exercise", "Sets", "Avg Reps", "Weight", "Notes"]
    ]

    for ex in payload["exercises"]:
        # Group by (weight_amount, repetitions) to match TSV semantics.
        sets = ex["sets"]
        for _key, group in groupby(
            sets, key=lambda s: (s["weight"]["amount"], s["repetitions"])
        ):
            group_list = list(group)
            reps = [s["repetitions"] for s in group_list]
            weight = group_list[0]["weight"]["amount"]
            rows.append([
                date,
                ex["name"],
                f"{len(group_list):d}",
                f"{int(sum(reps) / len(reps)):d}",
                f"{weight:.1f}".replace(".", ","),
                f"Origen=training-parser (ANTLR) ({today}.txt)",
            ])

    return "\n".join("\t".join(cell for cell in row) for row in rows)


def parse_and_export(text: str, date_str: str) -> str:
    """Full pipeline: parse text → JSON "A" (envelope) → totals & TSV, all from JSON.

    Returns JSON string with:
      - envelope: JSON "A"
      - envelope_pretty: pretty-printed envelope for download
      - totals: computed from payload
      - tsv: spreadsheet-format string
      - errors: parse errors (grammar) + schema errors
      - is_valid: no errors of any kind
    """
    exercises_out, parse_errors = _parse_to_exercises(text)

    payload = _build_set_centric_payload(exercises_out, date_str)
    envelope = {"type": ENVELOPE_TYPE, "schema": ENVELOPE_SCHEMA, "payload": payload}

    schema_errors = _validate_envelope(envelope) if not parse_errors else []
    all_errors = list(parse_errors) + [
        {"line": 0, "column": 0, "message": m} for m in schema_errors
    ]

    totals = _compute_totals_from_payload(payload)
    tsv = _tsv_from_payload(payload)

    return json.dumps({
        "envelope": envelope,
        "envelope_pretty": json.dumps(envelope, indent=2),
        "totals": totals,
        "tsv": tsv,
        "errors": all_errors,
        "is_valid": len(all_errors) == 0,
    })


def get_statistics(exercises_json: str, time_minutes: float) -> str:
    """Calculate workout statistics from exercises JSON."""
    from src.statistics import StatisticsCalculator

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
    payload = _build_set_centric_payload(exercises_data, date_str)
    return json.dumps(payload, indent=2)
