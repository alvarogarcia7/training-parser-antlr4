"""Shared display and formatting logic for workout data."""
from typing import Any

from parser.model import Exercise, Set_, Weight


def reconstruct_exercise(exercise_data: dict[str, Any]) -> Exercise:
    """Reconstruct an Exercise object from serialized JSON dict."""
    sets = []
    for set_data in exercise_data["sets"]:
        weight = Weight(
            amount=set_data["weight"]["amount"],
            unit=set_data["weight"]["unit"]
        )
        set_obj = Set_(
            repetitions=set_data["repetitions"],
            weight=weight
        )
        sets.append(set_obj)

    return Exercise(name=exercise_data["name"], sets_=sets)


def serialize_exercise(exercise: Exercise) -> dict[str, Any]:
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


def print_workout(workout: dict[str, Any]) -> float:
    """
    Print a single workout in compact form.

    Returns:
        total_volume for this workout
    """
    print(f"## {workout['date']}")

    if workout['notes']:
        print(f"  Notes: {workout['notes']}")

    total_volume = 0.0
    for exercise_data in workout['exercises']:
        exercise = reconstruct_exercise(exercise_data)
        exercise_volume = exercise.total_volume()
        total_volume += exercise_volume
        print(f"  {exercise.__repr__()}; subtotal: {exercise_volume}")

    exercise_count = len(workout['exercises'])
    print(f"  # Stats for this session")
    print(f"  Total number of exercises: {exercise_count}")
    print(f"  Total volume this workout: {total_volume}")

    return total_volume
