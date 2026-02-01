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

from parser.display import print_workout


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
        workout_volume = print_workout(workout)
        total_volume_all += workout_volume

    print(f"Total volume for all workouts: {total_volume_all}")


if __name__ == "__main__":
    main()
