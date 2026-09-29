"""Shared display and formatting logic for workout data."""
from typing import Any

from parser.model import Exercise, Set_, Weight
from src.data_access import VolumeFormatter


def format_volume_for_display(total_volume: float) -> tuple[str, int | float]:
  """Format volume for display output.

  Converts float volumes that are whole numbers to integers, then formats with thousands separator.

  Args:
    total_volume: The raw volume as a float

  Returns:
    Tuple of (formatted_display, raw_value_for_parentheses)
  """
  total_volume_for_workout = int(total_volume) if total_volume == int(total_volume) else total_volume
  total_volume_display = VolumeFormatter.format_volume_thousands(total_volume_for_workout)
  return total_volume_display, total_volume_for_workout


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
        volume_display, volume_raw = format_volume_for_display(exercise_volume)
        print(f"  {exercise.__repr__()}; subtotal: {volume_display} ({volume_raw})")

    exercise_count = len(workout['exercises'])
    print(f"  # Stats for this session")
    print(f"  Total number of exercises: {exercise_count}")
    total_volume_display, total_volume_raw = format_volume_for_display(total_volume)
    print(f"  Total volume this workout: {total_volume_display} ({total_volume_raw})")

    return total_volume
