import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

import jsonschema

from parser.model import Exercise


def serialize_to_bench_centric(exercises: list[Exercise], timestamp: Optional[datetime] = None) -> dict[str, Any]:
    """
    Serialize exercises to bench-centric JSON format and validate against schema.

    Args:
        exercises: List of Exercise objects to serialize
        timestamp: Optional timestamp for the workout (defaults to current time)

    Returns:
        Dictionary in bench-centric format, validated against JSON schema

    Raises:
        jsonschema.ValidationError: If the generated JSON doesn't match the schema
    """
    if timestamp is None:
        timestamp = datetime.now(timezone.utc)

    workout_id = f"w_{timestamp.strftime('%Y%m%d_%H%M%S')}"

    exercise_blocks = []
    for exercise in exercises:
        sets = []
        for set_ in exercise.sets_:
            set_dict: dict[str, Any] = {
                "reps": set_.repetitions,
                "weight": set_.weight.amount,
                "unit": set_.weight.unit
            }
            if set_.rir is not None:
                set_dict["rir"] = set_.rir
            sets.append(set_dict)

        exercise_blocks.append({
            "name": exercise.name,
            "equipment": "other",
            "sets": sets
        })

    result = {
        "workout_id": workout_id,
        "type": "bench-centric",
        "date": timestamp.isoformat(),
        "location": "",
        "notes": "",
        "statistics": {},
        "exercises": exercise_blocks
    }

    # Validate against JSON schema
    schema_path = Path(__file__).parent.parent / "schema" / "bench-centric.schema.json"
    common_defs_path = Path(__file__).parent.parent / "schema" / "common-definitions.schema.json"

    with open(schema_path, 'r') as f:
        schema = json.load(f)

    with open(common_defs_path, 'r') as f:
        common_defs = json.load(f)

    # Create a resolver for $ref references
    store = {
        common_defs["$id"]: common_defs
    }
    resolver = jsonschema.RefResolver.from_schema(schema, store=store)

    # Validate the result
    validator = jsonschema.Draft202012Validator(schema, resolver=resolver)
    validator.validate(result)

    return result


def serialize_to_set_centric(exercises: list[Exercise], timestamp: Optional[datetime] = None) -> dict[str, Any]:
    """
    Serialize exercises to set-centric JSON format and validate against schema.

    Args:
        exercises: List of Exercise objects to serialize
        timestamp: Optional timestamp for the workout (defaults to current time)

    Returns:
        Dictionary in set-centric format, validated against JSON schema

    Raises:
        jsonschema.ValidationError: If the generated JSON doesn't match the schema
    """
    if timestamp is None:
        timestamp = datetime.now(timezone.utc)

    workout_id = f"w_{timestamp.strftime('%Y%m%d_%H%M%S')}"

    exercise_blocks = []
    for exercise in exercises:
        sets = []
        for idx, set_ in enumerate(exercise.sets_, start=1):
            set_dict: dict[str, Any] = {
                "setNumber": idx,
                "repetitions": set_.repetitions,
                "weight": {
                    "amount": set_.weight.amount,
                    "unit": set_.weight.unit
                }
            }
            if set_.rir is not None:
                set_dict["rir"] = set_.rir
            sets.append(set_dict)

        exercise_blocks.append({
            "name": exercise.name,
            "equipment": "other",
            "sets": sets
        })

    result = {
        "workout_id": workout_id,
        "type": "set-centric",
        "date": timestamp.isoformat(),
        "location": "",
        "notes": "",
        "statistics": {},
        "exercises": exercise_blocks
    }

    # Validate against JSON schema
    schema_path = Path(__file__).parent.parent / "schema" / "set-centric.schema.json"
    common_defs_path = Path(__file__).parent.parent / "schema" / "common-definitions.schema.json"

    with open(schema_path, 'r') as f:
        schema = json.load(f)

    with open(common_defs_path, 'r') as f:
        common_defs = json.load(f)

    # Create a resolver for $ref references
    store = {
        common_defs["$id"]: common_defs
    }
    resolver = jsonschema.RefResolver.from_schema(schema, store=store)

    # Validate the result
    validator = jsonschema.Draft202012Validator(schema, resolver=resolver)
    validator.validate(result)

    return result
