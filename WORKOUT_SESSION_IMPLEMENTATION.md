# Workout Session Testing - Implementation Summary

## Overview

Implemented comprehensive testing and examples for **complete workout sessions**, moving beyond individual exercise series to test full training scenarios with multiple exercises, error recovery, and session-level analytics.

## Files Created

### 1. Test Suite: `parser/test_workout_sessions.py`

**17 comprehensive test cases** covering:

- ✅ Complete valid workout sessions (5+ exercises)
- ✅ Sessions with partial errors (some exercises fail, others succeed)
- ✅ Sessions with all errors
- ✅ Mixed format sessions (various notation styles)
- ✅ Sessions with accents and special characters
- ✅ Error recovery and continuation
- ✅ Error line number tracking
- ✅ RIR (Reps In Reserve) values
- ✅ Progressive overload tracking
- ✅ Weight variations (with/without 'k', decimals)
- ✅ Volume calculations for complete sessions
- ✅ Session validation
- ✅ Standard exercise names from grammar

**Key Features Tested:**
- Parse 5-6 exercise sessions successfully
- Handle 2-3 errors while preserving valid data
- Track errors to specific line numbers
- Calculate total volume across all exercises
- Validate all exercises in a session
- Support multiple weight notations

### 2. Examples: `examples/error_handling_example.py`

**6 comprehensive workout session examples:**

#### Example 1: Full Workout Session with Errors
- 6-exercise push day workout
- 2 incomplete exercises (errors)
- 4 successfully parsed exercises
- Shows exercise-level statistics (sets, volume)
- Displays error locations

#### Example 2: Complete Valid Workout
- 6-exercise pull day (all valid)
- Calculates total sets, reps, volume
- Shows average reps per set
- Exercise breakdown with statistics

#### Example 3: Weekly Training Split
- 3 workout sessions (Monday/Wednesday/Friday)
- Push/Pull/Legs split
- Aggregates weekly statistics
- Tracks errors across multiple sessions
- Shows success rate

#### Example 4: Progression Tracking
- 3 weeks of training data
- Week-over-week weight increases
- Handles missing data from errors
- Shows progression analysis

#### Example 5: Error Summary for Workout
- 7-exercise session with 3 errors
- Detailed error reporting
- Successfully logged exercises
- Actionable feedback

#### Example 6: Workout Validation
- 4-exercise session with RIR values
- Volume calculations
- Max weight detection
- Complete workout analysis

### 3. Real-World Scenarios: `examples/workout_session_examples.py`

**7 training methodology examples:**

#### 1. Powerlifting Session
- Competition lifts (Squat, Bench, Deadlift)
- Max weight tracking
- Volume per lift
- Main lifts + accessory work

#### 2. Hypertrophy Session (Chest & Triceps)
- 6-exercise bodybuilding session
- Total sets: 18, Total reps: 180+
- Volume calculations
- Average reps per set

#### 3. CrossFit WOD (21-15-9)
- Descending rep scheme
- Mixed modal exercises
- Total WOD volume
- Rep pattern analysis

#### 4. Strength Cycle (5/3/1)
- Progressive intensity sets
- RIR-based training
- Multiple squat variations
- Intensity analysis

#### 5. Olympic Weightlifting
- Technical session
- Snatch progression
- Clean & Jerk progression
- Volume distribution

#### 6. Deload Week
- Recovery-focused session
- Reduced volume tracking
- Moderate intensity
- All main lifts included

#### 7. Error Recovery Demo
- 7 exercises with 3 errors
- Visual error markers (⚠/✓)
- Shows recovered data
- Provides actionable fixes

### 4. Sample Data: `examples/sample_workouts.txt`

**15+ complete workout templates:**
- Powerlifting competition prep
- Bodybuilding splits (Push/Pull/Legs)
- CrossFit WODs
- Strength programs (5/3/1)
- Olympic weightlifting
- Deload weeks
- Beginner full body
- Upper/Lower splits
- Advanced volume/intensity blocks
- Sport-specific training
- Sessions with intentional errors
- Mixed format sessions

### 5. Documentation

#### `WORKOUT_SESSION_TESTING.md`
- Complete testing approach
- Test coverage details
- Example descriptions
- Usage patterns
- Benefits and features

#### `examples/__init__.py`
- Package documentation
- Module exports
- Quick reference

## Key Improvements

### From Single Exercise Testing to Full Sessions

**Before:**
```python
# Test individual exercise
result = Parser.from_string('Bench press 75k: 4, 4x5\n').parse_sessions()
```

**After:**
```python
# Test complete workout session
workout = """
Bench press 75k: 4, 4x5
Squat 70k: 5x10
Overhead press: 5x5x40k
Deadlift 60k: 20, 15, 8, 8
Row en maquina 41k: 15, 8
"""
result = Parser.from_string(workout).parse()

# Session-level analytics
total_volume = sum(ex.total_volume() for ex in result.exercises)
total_sets = sum(len(ex.sets_) for ex in result.exercises)
success_rate = len(result.exercises) / total_exercises
```

### Session-Level Features

1. **Multi-Exercise Parsing**
   - Handle 5-15 exercises per session
   - Mixed exercise types
   - Various notation formats

2. **Error Recovery**
   - Continue parsing after errors
   - Preserve valid exercises
   - Identify error locations
   - Calculate partial statistics

3. **Analytics**
   - Total volume calculations
   - Total sets and reps
   - Average intensity
   - Success rates
   - Progression tracking

4. **Real-World Scenarios**
   - Powerlifting protocols
   - Bodybuilding splits
   - CrossFit programming
   - Strength cycles
   - Olympic weightlifting
   - Sport-specific training

## Testing Coverage

### Unit Tests (17 tests)
- Valid sessions: 4 tests
- Error handling: 4 tests
- Mixed formats: 3 tests
- Advanced features: 3 tests
- Analytics: 3 tests

### Integration Examples (13 examples)
- Error handling examples: 6
- Real-world scenarios: 7

### Sample Data
- 15+ complete workout templates
- Multiple training methodologies
- Various experience levels

## Usage Examples

### Basic Session Logging
```python
from parser import Parser

workout = """
Bench press 80k: 5, 5, 5
Squat 100k: 5, 5, 5
Deadlift 120k: 5, 5, 5
"""

result = Parser.from_string(workout).parse()

if result.is_valid:
    print(f"Logged {len(result.exercises)} exercises")
    total_volume = sum(ex.total_volume() for ex in result.exercises)
    print(f"Total volume: {total_volume}kg")
```

### Error-Tolerant Logging
```python
result = Parser.from_string(workout).parse()

# Save successful exercises
for exercise in result.exercises:
    database.save(exercise)

# Report errors
if result.has_errors:
    for error in result.errors:
        logger.warning(f"Line {error.line}: {error.message}")
```

### Weekly Progression
```python
weeks = [week1_workout, week2_workout, week3_workout]
progression = {}

for week_num, workout in enumerate(weeks, 1):
    result = Parser.from_string(workout).parse()

    for exercise in result.exercises:
        if exercise.name not in progression:
            progression[exercise.name] = []

        avg_weight = sum(s.weight.amount for s in exercise.sets_) / len(exercise.sets_)
        progression[exercise.name].append((week_num, avg_weight))

# Analyze progression
for exercise_name, weights in progression.items():
    initial = weights[0][1]
    final = weights[-1][1]
    improvement = final - initial
    print(f"{exercise_name}: {initial}kg → {final}kg (+{improvement}kg)")
```

## Benefits

1. **Realistic Testing**: Tests reflect actual workout logging scenarios
2. **Complete Context**: Full sessions, not isolated exercises
3. **Error Resilience**: Partial data is preserved and usable
4. **Real Methodologies**: Examples from actual training programs
5. **Analytics Support**: Session-level statistics and tracking
6. **Progress Monitoring**: Multi-session progression analysis
7. **Multiple Use Cases**: Covers various training styles and goals

## Running the Tests

```bash
# Run workout session tests
python -m pytest parser/test_workout_sessions.py -v

# Run all parser tests
python -m pytest parser/ -v

# Run examples
python examples/error_handling_example.py
python examples/workout_session_examples.py

# Parse sample workouts file
python examples/parse_with_errors.py examples/sample_workouts.txt
```

## Statistics

- **Test Cases**: 17 comprehensive session tests
- **Examples**: 13 real-world scenarios
- **Sample Workouts**: 15+ complete templates
- **Training Styles**: 8+ different methodologies
- **Code Coverage**: Session parsing, error recovery, analytics
- **Documentation**: 3 markdown files, inline docs

## Conclusion

The workout session testing implementation provides comprehensive coverage for real-world training scenarios, ensuring the parser can handle complete workout sessions with multiple exercises, gracefully recover from errors, and provide meaningful analytics for training tracking and progression monitoring.
