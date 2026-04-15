# Quick Start: Workout Session Testing

## Running the Tests

```bash
# Run workout session tests
python -m pytest parser/test_workout_sessions.py -v

# Run all tests including workout sessions
python -m pytest parser/test_parser.py parser/test_workout_sessions.py -v
```

## Running the Examples

```bash
# Full workout session examples with error handling
python examples/error_handling_example.py

# Real-world training scenarios
python examples/workout_session_examples.py

# Parse sample workouts file
python examples/parse_with_errors.py examples/sample_workouts.txt
```

## Basic Usage

### Parse a Complete Workout

```python
from parser import Parser

# Define your workout session
workout = """
Bench press 80k: 5, 5, 5
Squat 100k: 5, 5, 5
Deadlift 120k: 5, 5, 5
"""

# Parse the session
result = Parser.from_string(workout).parse()

# Check results
print(f"Exercises logged: {len(result.exercises)}")
print(f"Errors: {len(result.errors)}")

# Calculate session volume
total_volume = sum(ex.total_volume() for ex in result.exercises)
print(f"Total volume: {total_volume}kg")
```

### Handle Errors in a Session

```python
# Workout with some incomplete exercises
workout = """
Bench press 80k: 5, 5, 5
Squat: 5x
Deadlift 120k: 5, 5, 5
"""

result = Parser.from_string(workout).parse()

# Save what we can
for exercise in result.exercises:
    database.save(exercise)
    print(f"✓ Saved: {exercise.name}")

# Report errors
if result.has_errors:
    print(f"\n⚠ {len(result.errors)} error(s):")
    for error in result.errors:
        print(f"  Line {error.line}: {error.message}")
```

### Track Progression

```python
# Parse multiple weeks
week1 = Parser.from_string("Squat 100k: 5, 5, 5\n").parse()
week2 = Parser.from_string("Squat 105k: 5, 5, 5\n").parse()
week3 = Parser.from_string("Squat 110k: 5, 5, 5\n").parse()

# Analyze progression
weeks = [week1, week2, week3]
for i, result in enumerate(weeks, 1):
    if result.exercises:
        squat = result.exercises[0]
        avg_weight = sum(s.weight.amount for s in squat.sets_) / len(squat.sets_)
        print(f"Week {i}: {avg_weight}kg")
```

## Test Examples

### Test Complete Valid Session
```python
def test_complete_valid_workout_session():
    workout = """
    Bench press 75k: 4, 4x5
    Squat 70k: 5x10
    Overhead press: 5x5x40k
    """
    result = Parser.from_string(workout).parse()

    assert not result.has_errors
    assert len(result.exercises) == 3
```

### Test Session with Errors
```python
def test_workout_session_with_partial_errors():
    workout = """
    Bench press 75k: 4, 4x5
    Squat: 5x
    Overhead press: 5x5x40k
    """
    result = Parser.from_string(workout).parse()

    assert result.has_errors
    assert len(result.exercises) == 2  # Bench and Overhead
    assert len(result.errors) == 1     # Squat error
```

### Test Session Analytics
```python
def test_workout_session_get_total_volume():
    workout = """
    Bench press 3x10x50k
    Squat 5x5x100k
    """
    result = Parser.from_string(workout).parse()

    total_volume = sum(ex.total_volume() for ex in result.exercises)
    assert total_volume == 4000.0  # (3*10*50) + (5*5*100)
```

## File Structure

```
parser/
  test_workout_sessions.py    # 17 comprehensive tests

examples/
  error_handling_example.py   # 6 workout session examples
  workout_session_examples.py # 7 real-world scenarios
  sample_workouts.txt         # 15+ workout templates
  parse_with_errors.py        # CLI utility

docs/
  WORKOUT_SESSION_TESTING.md         # Complete documentation
  WORKOUT_SESSION_IMPLEMENTATION.md  # Implementation details
  QUICK_START_WORKOUT_SESSIONS.md   # This file
```

## Key Features

✅ Parse complete workout sessions (5-15 exercises)
✅ Handle errors while preserving valid data
✅ Calculate session statistics (volume, sets, reps)
✅ Track progression across sessions
✅ Support multiple training methodologies
✅ Identify errors with line numbers
✅ Validate complete sessions

## Sample Workouts Included

- Powerlifting sessions
- Bodybuilding splits (Push/Pull/Legs)
- CrossFit WODs
- Strength programs (5/3/1)
- Olympic weightlifting
- Beginner programs
- Advanced protocols

## Quick Tips

1. **Always use `parse()` instead of `parse_sessions()`** for better error handling
2. **Check `result.has_errors`** before processing
3. **Use `result.exercises`** even when errors occur - partial data is preserved
4. **Track `error.line`** to identify problematic input
5. **Calculate `total_volume()`** for each exercise to track workout intensity

## Next Steps

- Read `WORKOUT_SESSION_TESTING.md` for complete documentation
- Run `python examples/error_handling_example.py` to see examples
- Check `examples/sample_workouts.txt` for workout templates
- Run tests with `python -m pytest parser/test_workout_sessions.py -v`
