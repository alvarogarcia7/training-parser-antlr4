"""
Example demonstrating error handling with incorrect input in full workout sessions.
Shows how to parse partially correct workout data and display errors with line/column information.
"""

from parser import Parser


def print_separator(title: str = "") -> None:
    """Print a formatted separator."""
    if title:
        print(f"\n{'=' * 60}")
        print(f"  {title}")
        print('=' * 60)
    else:
        print('-' * 60)


def example_complete_workout_with_errors() -> None:
    """Parse a complete workout session with intentional errors and display results."""

    print_separator("Example 1: Full Workout Session with Errors")

    # Complete workout session with some errors:
    # Day 1 - Push workout with mixed valid/invalid exercises
    training_input = """Bench press 75k: 4, 4x5
Incline bench: 5x
Overhead press: 5x5x40k
Lateral raises 10k: 12, 12, 12
Tricep pushdown: 10x
Dips 20k: 12, 10, 8
"""

    print("\nWorkout Session - Push Day:")
    print_separator()
    for i, line in enumerate(training_input.strip().split('\n'), 1):
        print(f"  {i}: {line}")
    print_separator()

    parser = Parser.from_string(training_input)
    result = parser.parse()

    print("\n📊 WORKOUT SUMMARY:")
    print(f"  • Total exercises attempted: 6")
    print(f"  • Successfully parsed: {len(result.exercises)} exercise(s)")
    print(f"  • Errors found: {len(result.errors)} error(s)")
    print(f"  • Session valid: {result.is_valid}")

    print("\n✅ Successfully Parsed Exercises:")
    if result.exercises:
        for i, exercise in enumerate(result.exercises, 1):
            total_sets = len(exercise.sets_)
            volume = exercise.total_volume()
            print(f"  {i}. {exercise.name}")
            print(f"     Sets: {total_sets}, Volume: {volume}kg")
            print(f"     Details: {exercise}")
    else:
        print("  (none)")

    print("\n❌ Parsing Errors:")
    if result.has_errors:
        for i, error in enumerate(result.errors, 1):
            print(f"  {i}. {error}")
        print(f"\n  ⚠ {len(result.errors)} exercise(s) could not be parsed")
        print(f"  ✓ {len(result.exercises)} exercise(s) successfully saved")
    else:
        print("  ✓ No errors found")


def example_complete_valid_workout() -> None:
    """Parse a complete valid workout session."""

    print_separator("Example 2: Complete Valid Workout Session")

    # Complete pull workout - all valid
    training_input = """Deadlift 100k: 5, 5, 5
Pull-ups 20k: 10, 8, 6
Barbell row 70k: 8, 8, 8
Lat pulldown 50k: 12, 10, 8
Face pulls 15k: 15, 15, 15
Bicep curls: 12xx15, 17.5, 20
"""

    print("\nWorkout Session - Pull Day:")
    print_separator()
    for i, line in enumerate(training_input.strip().split('\n'), 1):
        print(f"  {i}: {line}")
    print_separator()

    parser = Parser.from_string(training_input)
    result = parser.parse()

    print("\n📊 WORKOUT SUMMARY:")
    print(f"  • Total exercises: {len(result.exercises)}")
    print(f"  • Errors: {len(result.errors)}")
    print(f"  • Session valid: {result.is_valid}")

    # Calculate workout statistics
    total_sets = sum(len(ex.sets_) for ex in result.exercises)
    total_volume = sum(ex.total_volume() for ex in result.exercises)

    print(f"  • Total sets: {total_sets}")
    print(f"  • Total volume: {total_volume}kg")

    print("\n✅ Workout Exercises:")
    for i, exercise in enumerate(result.exercises, 1):
        sets_count = len(exercise.sets_)
        volume = exercise.total_volume()
        print(f"  {i}. {exercise.name}: {sets_count} sets, {volume}kg volume")

    if result.has_errors:
        print("\n❌ Parsing Errors:")
        for error in result.errors:
            print(f"  ✗ {error}")
    else:
        print("\n✓ Perfect session - all exercises logged successfully!")


def example_weekly_training_split() -> None:
    """Parse multiple workout sessions from a training week."""

    print_separator("Example 3: Weekly Training Split with Errors")

    # Monday - Push
    monday_workout = """Bench press 80k: 5, 5, 5
Overhead press 50k: 8, 8, 8
Incline dumbbell: 10x
Lateral raises 12k: 15, 15, 15
"""

    # Wednesday - Pull
    wednesday_workout = """Deadlift 120k: 3, 3, 3
Pull-ups 25k: 8, 6, 5
Barbell row: 5x
Bicep curls 15k: 12, 10, 8
"""

    # Friday - Legs
    friday_workout = """Squat 100k: 5, 5, 5
Romanian deadlift 80k: 8, 8, 8
Leg press 150k: 10, 10, 10
Leg curl: 12x
Calf raises 40k: 15, 15, 15
"""

    workouts = [
        ("Monday - Push", monday_workout),
        ("Wednesday - Pull", wednesday_workout),
        ("Friday - Legs", friday_workout)
    ]

    weekly_stats = {
        'total_exercises': 0,
        'total_valid': 0,
        'total_errors': 0,
        'total_volume': 0.0
    }

    for day, workout in workouts:
        print(f"\n{day}:")
        print_separator()

        result = Parser.from_string(workout).parse()

        weekly_stats['total_exercises'] += len(workout.strip().split('\n'))
        weekly_stats['total_valid'] += len(result.exercises)
        weekly_stats['total_errors'] += len(result.errors)
        weekly_stats['total_volume'] += sum(ex.total_volume() for ex in result.exercises)

        print(f"  Exercises logged: {len(result.exercises)}")
        print(f"  Errors: {len(result.errors)}")

        if result.has_errors:
            for error in result.errors:
                print(f"    ⚠ Line {error.line}: {error.message}")

    print("\n" + "=" * 60)
    print("WEEKLY SUMMARY:")
    print("=" * 60)
    print(f"  Total exercises attempted: {weekly_stats['total_exercises']}")
    print(f"  Successfully logged: {weekly_stats['total_valid']}")
    print(f"  Failed to parse: {weekly_stats['total_errors']}")
    print(f"  Total training volume: {weekly_stats['total_volume']:.1f}kg")
    print(f"  Success rate: {weekly_stats['total_valid']/weekly_stats['total_exercises']*100:.1f}%")


def example_workout_progression_tracking() -> None:
    """Demonstrate tracking progression across workout sessions."""

    print_separator("Example 4: Progression Tracking with Error Recovery")

    # Week 1
    week1 = """Bench press 75k: 5, 5, 5
Squat 100k: 5, 5, 5
Deadlift 120k: 5, 5, 5
"""

    # Week 2 - some errors
    week2 = """Bench press 77.5k: 5, 5, 5
Squat: 5x
Deadlift 122.5k: 5, 5, 5
"""

    # Week 3
    week3 = """Bench press 80k: 5, 5, 5
Squat 105k: 5, 5, 5
Deadlift 125k: 5, 5, 5
"""

    weeks = [
        ("Week 1", week1),
        ("Week 2", week2),
        ("Week 3", week3)
    ]

    print("\nProgression Tracking:")
    print_separator()

    progression_data: dict[str, list[float]] = {}

    for week_name, workout in weeks:
        result = Parser.from_string(workout).parse()

        print(f"\n{week_name}:")
        for exercise in result.exercises:
            if exercise.name not in progression_data:
                progression_data[exercise.name] = []

            avg_weight = sum(s.weight.amount for s in exercise.sets_) / len(exercise.sets_)
            progression_data[exercise.name].append(avg_weight)
            print(f"  • {exercise.name}: {avg_weight}kg avg")

        if result.has_errors:
            print(f"  ⚠ {len(result.errors)} error(s) - data incomplete")

    print("\n" + "=" * 60)
    print("PROGRESSION ANALYSIS:")
    print("=" * 60)
    for exercise_name, weights in progression_data.items():
        if len(weights) > 1:
            progression = weights[-1] - weights[0]
            print(f"  {exercise_name}: {weights[0]}kg → {weights[-1]}kg (+{progression}kg)")


def example_error_summary_for_workout() -> None:
    """Demonstrate using the error summary methods for a complete workout."""

    print_separator("Example 5: Error Summary for Workout Session")

    training_input = """Bench press 75k: 4, 4x5
Squat: 5x
Overhead press 50k: 8, 8, 8
Deadlift: 10x
Row en maquina 41k: 15, 8
Pull-up: 12x
Dips 20k: 10, 8, 6
"""

    print("\nWorkout Log:")
    print_separator()
    for i, line in enumerate(training_input.strip().split('\n'), 1):
        print(f"  {i}: {line}")
    print_separator()

    result = Parser.from_string(training_input).parse()

    print("\nUsing get_error_summary():")
    print(result.get_error_summary())

    print("\nUsing print_errors():")
    result.print_errors()

    print(f"\n✅ Successfully Logged ({len(result.exercises)} exercises):")
    for i, exercise in enumerate(result.exercises, 1):
        print(f"  {i}. {exercise.name} - {len(exercise.sets_)} sets")

    if result.has_errors:
        print(f"\n⚠ Action Required:")
        print(f"  Please fix {len(result.errors)} exercise(s) in your workout log")


def example_workout_validation() -> None:
    """Demonstrate validating a complete workout session."""

    print_separator("Example 6: Workout Validation and Statistics")

    training_input = """Bench press 3x8x80k 2
Squat 4x5x100k 1
Deadlift 5x3x120k 0
Overhead press 3x10x50k 2
"""

    print("\nWorkout with RIR (Reps In Reserve):")
    print_separator()
    for i, line in enumerate(training_input.strip().split('\n'), 1):
        print(f"  {i}: {line}")
    print_separator()

    result = Parser.from_string(training_input).parse()

    if result.is_valid:
        print("\n✓ All exercises valid!")

        print("\n📊 Workout Analysis:")
        total_volume = 0.0
        total_sets = 0
        max_weight = 0.0

        for exercise in result.exercises:
            sets = len(exercise.sets_)
            volume = exercise.total_volume()
            total_volume += volume
            total_sets += sets

            for set_ in exercise.sets_:
                if set_.weight.amount > max_weight:
                    max_weight = set_.weight.amount

            rir = exercise.sets_[0].rir if exercise.sets_[0].rir is not None else "N/A"
            print(f"  • {exercise.name}")
            print(f"    Sets: {sets}, Volume: {volume}kg, RIR: {rir}")

        print(f"\n  Total sets: {total_sets}")
        print(f"  Total volume: {total_volume}kg")
        print(f"  Max weight: {max_weight}kg")
    else:
        result.print_errors()


def main() -> None:
    """Run all workout session examples."""
    print("\n" + "=" * 60)
    print("  TRAINING PARSER - WORKOUT SESSION EXAMPLES")
    print("=" * 60)

    example_complete_workout_with_errors()
    example_complete_valid_workout()
    example_weekly_training_split()
    example_workout_progression_tracking()
    example_error_summary_for_workout()
    example_workout_validation()

    print("\n" + "=" * 60)
    print("  All Examples Complete!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
