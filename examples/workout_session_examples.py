"""
Examples of complete workout session parsing with various training scenarios.
Demonstrates real-world use cases for tracking full workouts.
"""

from parser import Parser


def example_powerlifting_session() -> None:
    """Example of a powerlifting training session."""
    print("\n" + "=" * 70)
    print("  POWERLIFTING SESSION - Competition Lifts")
    print("=" * 70)

    workout = """Squat 140k: 3, 3, 3
Bench press 100k: 3, 3, 3
Deadlift 180k: 1, 1, 1
Squat 100k: 5, 5, 5
Bench press 80k: 8, 8, 8
"""

    result = Parser.from_string(workout).parse()

    print("\n📋 Session Log:")
    for i, line in enumerate(workout.strip().split('\n'), 1):
        print(f"  {i}. {line}")

    if result.is_valid:
        print("\n✅ All lifts logged successfully!")

        # Calculate 1RM and volume for each lift
        lifts = {}
        for exercise in result.exercises:
            if exercise.name not in lifts:
                lifts[exercise.name] = {'max_weight': 0.0, 'total_volume': 0.0}

            for set_ in exercise.sets_:
                if set_.weight.amount > lifts[exercise.name]['max_weight']:
                    lifts[exercise.name]['max_weight'] = set_.weight.amount
                lifts[exercise.name]['total_volume'] += set_.weight.amount * set_.repetitions

        print("\n📊 Session Summary:")
        for lift_name, stats in lifts.items():
            print(f"  {lift_name}:")
            print(f"    Max weight: {stats['max_weight']}kg")
            print(f"    Total volume: {stats['total_volume']}kg")
    else:
        print(f"\n⚠ Session has {len(result.errors)} error(s):")
        result.print_errors()


def example_hypertrophy_session() -> None:
    """Example of a bodybuilding hypertrophy session."""
    print("\n" + "=" * 70)
    print("  HYPERTROPHY SESSION - Chest & Triceps")
    print("=" * 70)

    workout = """Bench press 80k: 10, 10, 10, 10
Incline dumbbell press: 12xx25, 27.5, 30
Cable flyes 20k: 15, 15, 15
Tricep pushdown 30k: 12, 12, 12
Overhead extension 20k: 10, 10, 10
Close grip bench 60k: 12, 12, 12
"""

    result = Parser.from_string(workout).parse()

    print("\n📋 Session Log:")
    for i, line in enumerate(workout.strip().split('\n'), 1):
        print(f"  {i}. {line}")

    if result.is_valid:
        total_sets = sum(len(ex.sets_) for ex in result.exercises)
        total_reps = sum(sum(s.repetitions for s in ex.sets_) for ex in result.exercises)
        total_volume = sum(ex.total_volume() for ex in result.exercises)

        print("\n📊 Hypertrophy Metrics:")
        print(f"  Total exercises: {len(result.exercises)}")
        print(f"  Total sets: {total_sets}")
        print(f"  Total reps: {total_reps}")
        print(f"  Total volume: {total_volume}kg")
        print(f"  Average reps/set: {total_reps/total_sets:.1f}")

        print("\n💪 Exercise Breakdown:")
        for exercise in result.exercises:
            sets = len(exercise.sets_)
            reps = sum(s.repetitions for s in exercise.sets_)
            volume = exercise.total_volume()
            print(f"  • {exercise.name}: {sets} sets, {reps} reps, {volume}kg")


def example_crossfit_wod() -> None:
    """Example of a CrossFit WOD (Workout of the Day)."""
    print("\n" + "=" * 70)
    print("  CROSSFIT WOD - Mixed Modal")
    print("=" * 70)

    # Note: Some movements don't fit the format perfectly, showing error handling
    workout = """Deadlift 100k: 21, 15, 9
Front squat 60k: 21, 15, 9
Power clean 50k: 21, 15, 9
Thrusters 40k: 21, 15, 9
"""

    result = Parser.from_string(workout).parse()

    print("\n📋 WOD Structure (21-15-9):")
    for i, line in enumerate(workout.strip().split('\n'), 1):
        print(f"  {i}. {line}")

    if result.is_valid:
        print("\n✅ WOD logged successfully!")

        # Analyze descending rep scheme
        print("\n📊 Rep Scheme Analysis:")
        for exercise in result.exercises:
            reps = [s.repetitions for s in exercise.sets_]
            weight = exercise.sets_[0].weight.amount
            print(f"  {exercise.name} @ {weight}kg: {'-'.join(map(str, reps))}")

        total_volume = sum(ex.total_volume() for ex in result.exercises)
        print(f"\n  Total WOD volume: {total_volume}kg")


def example_strength_cycle() -> None:
    """Example of a strength training cycle (5/3/1)."""
    print("\n" + "=" * 70)
    print("  STRENGTH CYCLE - 5/3/1 Week 1")
    print("=" * 70)

    workout = """Squat 3x5x100k 3
Squat 3x3x110k 2
Squat 3x1x120k 1
Squat 5x5x85k
Front squat 3x8x70k
"""

    result = Parser.from_string(workout).parse()

    print("\n📋 Training Session:")
    for i, line in enumerate(workout.strip().split('\n'), 1):
        print(f"  {i}. {line}")

    if result.is_valid:
        print("\n✅ Strength session completed!")

        print("\n📊 Intensity Analysis:")
        squat_sets = [ex for ex in result.exercises if 'squat' in ex.name.lower()]

        for exercise in squat_sets:
            for i, set_ in enumerate(exercise.sets_, 1):
                rir = f", RIR: {set_.rir}" if set_.rir is not None else ""
                print(f"  Set {i}: {set_.repetitions} reps @ {set_.weight.amount}kg{rir}")


def example_olympic_weightlifting() -> None:
    """Example of an Olympic weightlifting session."""
    print("\n" + "=" * 70)
    print("  OLYMPIC WEIGHTLIFTING - Technique Session")
    print("=" * 70)

    workout = """Snatch 60k: 3, 3, 3
Snatch 70k: 2, 2, 2
Snatch 75k: 1, 1, 1
Clean and jerk 80k: 3, 3
Clean and jerk 90k: 2, 2
Clean and jerk 95k: 1, 1
Front squat 100k: 3, 3, 3
"""

    result = Parser.from_string(workout).parse()

    print("\n📋 Session Log:")
    for i, line in enumerate(workout.strip().split('\n'), 1):
        print(f"  {i}. {line}")

    if result.is_valid:
        print("\n✅ Technical session logged!")

        print("\n📊 Volume Distribution:")
        for exercise in result.exercises:
            total_reps = sum(s.repetitions for s in exercise.sets_)
            avg_weight = sum(s.weight.amount for s in exercise.sets_) / len(exercise.sets_)
            print(f"  {exercise.name}:")
            print(f"    Sets: {len(exercise.sets_)}, Reps: {total_reps}, Avg: {avg_weight:.1f}kg")


def example_deload_week() -> None:
    """Example of a deload/recovery week workout."""
    print("\n" + "=" * 70)
    print("  DELOAD WEEK - Recovery Session")
    print("=" * 70)

    workout = """Bench press 60k: 8, 8, 8
Squat 80k: 8, 8, 8
Deadlift 100k: 5, 5
Overhead press 40k: 10, 10
Row 50k: 10, 10
"""

    result = Parser.from_string(workout).parse()

    print("\n📋 Light Session:")
    for i, line in enumerate(workout.strip().split('\n'), 1):
        print(f"  {i}. {line}")

    if result.is_valid:
        total_volume = sum(ex.total_volume() for ex in result.exercises)
        total_sets = sum(len(ex.sets_) for ex in result.exercises)

        print("\n✅ Recovery session completed!")
        print(f"\n📊 Deload Metrics:")
        print(f"  Total volume: {total_volume}kg (reduced)")
        print(f"  Total sets: {total_sets} (moderate)")
        print(f"  Focus: Technique and recovery")


def example_workout_with_errors_recovery() -> None:
    """Example showing error recovery in a workout session."""
    print("\n" + "=" * 70)
    print("  ERROR RECOVERY - Incomplete Workout Log")
    print("=" * 70)

    workout = """Bench press 80k: 5, 5, 5
Incline bench: 5x
Overhead press 50k: 8, 8, 8
Lateral raises: 10x
Tricep pushdown 25k: 12, 12, 12
Dips: 8x
Skull crushers 20k: 10, 10, 10
"""

    result = Parser.from_string(workout).parse()

    print("\n📋 Original Log (with errors):")
    for i, line in enumerate(workout.strip().split('\n'), 1):
        marker = " ⚠" if any(e.line == i for e in result.errors) else " ✓"
        print(f"  {i}. {line}{marker}")

    print(f"\n📊 Parse Results:")
    print(f"  Total exercises: 7")
    print(f"  Successfully parsed: {len(result.exercises)}")
    print(f"  Failed to parse: {len(result.errors)}")

    if result.has_errors:
        print(f"\n❌ Errors Detected:")
        for error in result.errors:
            print(f"  Line {error.line}: {error.message}")

        print(f"\n✅ Recovered Data ({len(result.exercises)} exercises):")
        for exercise in result.exercises:
            print(f"  • {exercise.name}: {len(exercise.sets_)} sets, {exercise.total_volume()}kg")

        print(f"\n💡 Tip: Review lines {', '.join(str(e.line) for e in result.errors)} and add missing weight/rep data")


def main() -> None:
    """Run all workout session examples."""
    print("\n" + "=" * 70)
    print("  WORKOUT SESSION PARSING EXAMPLES")
    print("  Real-world training scenarios with complete sessions")
    print("=" * 70)

    example_powerlifting_session()
    example_hypertrophy_session()
    example_crossfit_wod()
    example_strength_cycle()
    example_olympic_weightlifting()
    example_deload_week()
    example_workout_with_errors_recovery()

    print("\n" + "=" * 70)
    print("  All Examples Complete!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
