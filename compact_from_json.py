"""
Display training data in compact form with totals and subtotals.

Step 2 of 2-step process:
- Read JSON file (output from parse_to_json.py)
- Reconstruct Exercise objects from JSON
- Display in compact form matching splitter.py behavior
- Compute totals and subtotals
"""
import json
import sys
from typing import Any

from parser.model import Exercise, Set_, Weight


def reconstruct_exercise(exercise_data: dict[str, Any]) -> Exercise:
    """Reconstruct an Exercise object from JSON."""
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


def display_workout_compact(workout: dict[str, Any]) -> tuple[float, int]:
    """
    Display a single workout in compact form.

    Returns:
        (total_volume, exercise_count)
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

    return total_volume, exercise_count


def main() -> None:
    """Read JSON and display in compact form."""
    if len(sys.argv) < 2:
        print("Usage: python3 compact_from_json.py <input_json_file>")
        sys.exit(1)

    input_file = sys.argv[1]

    with open(input_file, 'r') as f:
        data = json.load(f)

    workouts = data.get('workouts', [])

    print("Debug printing.")
    total_volume_all = 0.0

    for workout in workouts:
        workout_volume, _ = display_workout_compact(workout)
        total_volume_all += workout_volume

    print(f"Total volume for all workouts: {total_volume_all}")


if __name__ == "__main__":
    main()
