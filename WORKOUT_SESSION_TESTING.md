# Workout Session Testing

This document describes the comprehensive testing approach for full workout sessions, not just individual exercise series.

## Overview

The training parser now includes extensive tests and examples for complete workout sessions, covering real-world training scenarios with multiple exercises, error recovery, and session-level statistics.

## Test Coverage

### `parser/test_workout_sessions.py`

Comprehensive test suite with 17 test cases covering:

#### 1. **Complete Valid Workout Sessions**
- `test_complete_valid_workout_session`: Parse a full workout with 5 exercises
- `test_workout_session_with_standard_exercise_names`: Test grammar-defined exercise names
- `test_workout_session_multiple_sets_same_weight`: Verify multiple sets at consistent weight

#### 2. **Error Handling in Sessions**
- `test_workout_session_with_partial_errors`: Some exercises valid, some with errors
- `test_workout_session_all_errors`: All exercises fail to parse
- `test_workout_session_error_recovery`: Parser recovers and continues after errors
- `test_workout_session_error_line_tracking`: Errors correctly mapped to line numbers

#### 3. **Mixed Format Sessions**
- `test_workout_session_mixed_formats`: Various exercise notation styles in one session
- `test_workout_session_with_accents_and_special_chars`: International characters and hyphens
- `test_workout_session_weight_variations`: Different weight notations (with/without 'k', decimals)

#### 4. **Advanced Features**
- `test_workout_session_with_rir`: RIR (Reps In Reserve) values
- `test_workout_session_progressive_overload`: Progressive weight increases
- `test_workout_session_with_empty_lines`: Handling whitespace between exercises

#### 5. **Session Analytics**
- `test_workout_session_get_total_volume`: Calculate total training volume
- `test_workout_session_validate_all_exercises`: Validate complete sessions
- `test_workout_session_complex_with_errors`: Complex multi-exercise sessions with various errors

## Examples

### `examples/error_handling_example.py`

Updated with 6 comprehensive workout session examples:

#### Example 1: Full Workout Session with Errors
```python
"""Push Day workout with intentional errors"""
Bench press 75k: 4, 4x5
Incline bench: 5x          # Error: incomplete
Overhead press: 5x5x40k
Lateral raises 10k: 12, 12, 12
Tricep pushdown: 10x       # Error: incomplete
Dips 20k: 12, 10, 8
```
- Shows partial parsing (4 of 6 exercises)
- Displays error locations
- Calculates session statistics

#### Example 2: Complete Valid Workout
```python
"""Pull Day - all valid exercises"""
Deadlift 100k: 5, 5, 5
Pull-ups 20k: 10, 8, 6
Barbell row 70k: 8, 8, 8
Lat pulldown 50k: 12, 10, 8
Face pulls 15k: 15, 15, 15
Bicep curls: 12xx15, 17.5, 20
```
- Calculates total sets, volume
- Shows session-level statistics

#### Example 3: Weekly Training Split
- Monday: Push workout
- Wednesday: Pull workout
- Friday: Legs workout
- Aggregates weekly statistics
- Tracks errors across multiple sessions

#### Example 4: Progression Tracking
- Week-over-week progression
- Weight increases over time
- Handles missing data from parsing errors

#### Example 5: Error Summary for Workout
- Detailed error reporting
- Exercise-level success/failure
- Actionable feedback

#### Example 6: Workout Validation
- RIR tracking
- Volume calculations
- Max weight detection

### `examples/workout_session_examples.py`

Real-world training scenario examples:

#### 1. **Powerlifting Session**
```python
Squat 140k: 3, 3, 3
Bench press 100k: 3, 3, 3
Deadlift 180k: 1, 1, 1
```
- Competition lift tracking
- Max weight and volume per lift

#### 2. **Hypertrophy Session**
```python
Bench press 80k: 10, 10, 10, 10
Incline dumbbell press: 12xx25, 27.5, 30
Cable flyes 20k: 15, 15, 15
```
- High volume training
- Total reps and volume analysis

#### 3. **CrossFit WOD**
```python
Deadlift 100k: 21, 15, 9
Front squat 60k: 21, 15, 9
```
- Descending rep schemes
- Mixed modal tracking

#### 4. **Strength Cycle (5/3/1)**
```python
Squat 3x5x100k 3
Squat 3x3x110k 2
Squat 3x1x120k 1
```
- RIR-based training
- Intensity progression

#### 5. **Olympic Weightlifting**
```python
Snatch 60k: 3, 3, 3
Clean and jerk 80k: 3, 3
```
- Technical work tracking
- Volume distribution analysis

#### 6. **Deload Week**
```python
Bench press 60k: 8, 8, 8
Squat 80k: 8, 8, 8
```
- Recovery session tracking
- Reduced volume monitoring

#### 7. **Error Recovery Example**
- Incomplete workout logs
- Visual error markers
- Recovered data display
- Actionable fix suggestions

## Session-Level Features

### Statistics Tracking
- **Total Volume**: Sum of (weight × reps) across all exercises
- **Total Sets**: Count of all sets in session
- **Total Reps**: Count of all repetitions
- **Exercise Count**: Number of exercises completed
- **Success Rate**: Percentage of successfully parsed exercises

### Error Recovery
- Parser continues after encountering errors
- Valid exercises are preserved
- Error locations precisely identified
- Partial session data is usable

### Multi-Session Analysis
- Weekly training splits
- Progression tracking across weeks
- Volume periodization
- Success rate monitoring

## Testing Strategy

### Unit Tests
Each test focuses on a specific session scenario:
- Valid complete sessions
- Sessions with errors
- Mixed format sessions
- Advanced feature sessions

### Integration Tests
Examples demonstrate complete workflows:
- Logging workouts
- Tracking progression
- Analyzing training volume
- Recovering from errors

### Real-World Scenarios
Examples cover actual training methodologies:
- Powerlifting protocols
- Bodybuilding splits
- CrossFit programming
- Olympic weightlifting
- Strength cycles

## Usage Patterns

### Basic Session Logging
```python
from parser import Parser

workout = """
Bench press 80k: 5, 5, 5
Squat 100k: 5, 5, 5
Deadlift 120k: 5, 5, 5
"""

result = Parser.from_string(workout).parse()
total_volume = sum(ex.total_volume() for ex in result.exercises)
print(f"Session volume: {total_volume}kg")
```

### Error-Tolerant Logging
```python
result = Parser.from_string(workout).parse()

# Save what we can
for exercise in result.exercises:
    database.save(exercise)

# Report issues
if result.has_errors:
    notify_user(f"Could not save {len(result.errors)} exercises")
    for error in result.errors:
        log.warning(f"Line {error.line}: {error.message}")
```

### Progress Tracking
```python
sessions = [week1, week2, week3]
progression = {}

for week, workout in enumerate(sessions, 1):
    result = Parser.from_string(workout).parse()

    for exercise in result.exercises:
        if exercise.name not in progression:
            progression[exercise.name] = []

        avg_weight = sum(s.weight.amount for s in exercise.sets_) / len(exercise.sets_)
        progression[exercise.name].append((week, avg_weight))
```

## Benefits

1. **Complete Workout Context**: Tests verify entire training sessions, not just individual exercises
2. **Real-World Scenarios**: Examples mirror actual training programs
3. **Error Resilience**: Sessions can be partially saved even with errors
4. **Analytics Support**: Session-level statistics for training analysis
5. **Multi-Session Tracking**: Weekly and monthly progression monitoring

## Running the Tests

```bash
# Run workout session tests
python -m pytest parser/test_workout_sessions.py -v

# Run all parser tests including sessions
python -m pytest parser/test_parser.py parser/test_workout_sessions.py -v

# Run workout session examples
python examples/error_handling_example.py
python examples/workout_session_examples.py
```

## Future Enhancements

Potential additions:
- Session templates (e.g., "5x5 protocol")
- Auto-generated session summaries
- Workout recommendations based on progression
- Volume load calculations (sets × reps × weight)
- Fatigue and recovery metrics
