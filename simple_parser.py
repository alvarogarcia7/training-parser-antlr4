"""
Simplified regex-based parser for training logs.
This is a workaround for environments without Java/ANTLR compilation.
Parses the training log format and returns Exercise objects.
"""

import re
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Optional

# Import directly from model module to avoid circular dependencies
# This avoids importing through parser/__init__.py which has ANTLR dependencies
from importlib import import_module

if TYPE_CHECKING:
    from parser.model import Exercise, Weight, Set_
else:
    model_module = import_module('.model', 'parser')
    Exercise = model_module.Exercise  # type: ignore
    Weight = model_module.Weight  # type: ignore
    Set_ = model_module.Set_  # type: ignore


def parse_weight(weight_str: str) -> Weight:
    """Parse a weight string like '75k' or '75' into a Weight object."""
    weight_str = weight_str.strip()
    if weight_str.endswith('k'):
        amount = float(weight_str[:-1])
        unit = 'kg'
    else:
        amount = float(weight_str)
        unit = 'kg'  # Default to kg
    return Weight(amount=amount, unit=unit)


def parse_set_notation(set_str: str) -> list[Set_]:
    """
    Parse a set notation like:
    - '4' -> single set of 4 reps
    - '4x5' -> 4 sets of 5 reps each
    - '4x5x75k' -> 4 sets of 5 reps at 75kg
    - '75k: 4' -> 4 reps at 75kg
    - '75k: 4, 4x5' -> mixed
    """
    sets: list[Set_] = []

    # Clean up the string
    set_str = set_str.strip()

    # Handle format like "75k: 4, 4x5"
    # First check if there's a weight at the beginning
    leading_weight: Optional[Weight] = None
    remaining_str = set_str

    weight_match = re.match(r'^(\d+(?:\.\d+)?k?)\s*:?\s*', set_str)
    if weight_match:
        leading_weight = parse_weight(weight_match.group(1))
        remaining_str = set_str[weight_match.end():].strip()

    # Split by comma for multiple set groups
    parts = [p.strip() for p in remaining_str.split(',')]

    for part in parts:
        part = part.strip()
        if not part:
            continue

        # Try to parse as "5x10" (5 sets of 10 reps)
        if 'xx' in part:
            # Fixed reps with multiple weights: "10xx75k,80k"
            fixed_reps_match = re.match(r'^(\d+)\s*xx\s*(.+)$', part)
            if fixed_reps_match:
                reps = int(fixed_reps_match.group(1))
                weights_str = fixed_reps_match.group(2)
                for weight_str in weights_str.split(','):
                    weight = parse_weight(weight_str.strip())
                    sets.append(Set_(repetitions=reps, weight=weight))
                continue

        # Try "NxMxW" (N sets of M reps at W weight)
        if part.count('x') == 2:
            triple_match = re.match(r'^(\d+)\s*x\s*(\d+)\s*x\s*(\d+(?:\.\d+)?k?)$', part)
            if triple_match:
                num_sets = int(triple_match.group(1))
                reps = int(triple_match.group(2))
                weight = parse_weight(triple_match.group(3))
                for _ in range(num_sets):
                    sets.append(Set_(repetitions=reps, weight=weight))
                continue

        # Try "NxM" (N sets of M reps)
        if 'x' in part and part.count('x') == 1:
            pair_match = re.match(r'^(\d+)\s*x\s*(\d+)$', part)
            if pair_match:
                num_sets = int(pair_match.group(1))
                reps = int(pair_match.group(2))
                if leading_weight:
                    for _ in range(num_sets):
                        sets.append(Set_(repetitions=reps, weight=leading_weight))
                continue

        # Try just a number (single set with that many reps)
        if re.match(r'^\d+$', part):
            reps = int(part)
            if leading_weight:
                sets.append(Set_(repetitions=reps, weight=leading_weight))

    return sets


def parse_exercise_line(line: str) -> Optional[Exercise]:
    """Parse a single exercise line like 'Bench press 75k: 4, 4x5'."""
    line = line.strip()
    if not line:
        return None

    # Common exercise names
    known_exercises = [
        'Deadlift', 'Squat', 'Bench press', 'Overhead press',
        'Row', 'Pull-ups', 'Push-ups', 'Dips', 'Leg press',
        'Leg curl', 'Leg extension', 'Lat pulldown', 'Chest fly',
        'Shoulder press', 'Military press', 'Barbell curl', 'Dumbbell curl'
    ]

    # Try to match exercise name at the start
    exercise_name: Optional[str] = None
    remaining: str = line

    for ex in sorted(known_exercises, key=len, reverse=True):
        if line.lower().startswith(ex.lower()):
            exercise_name = ex
            remaining = line[len(ex):].strip()
            break

    # If no known exercise found, try to extract it differently
    if not exercise_name:
        # Match anything before the first colon or weight notation
        match = re.match(r'^([^:0-9]+?)\s*[:]?\s*(.+)$', line)
        if match:
            exercise_name = match.group(1).strip()
            remaining = match.group(2).strip()
        else:
            return None

    if not exercise_name:
        return None

    # Parse the sets from the remaining string
    sets = parse_set_notation(remaining)

    if sets:
        return Exercise(name=exercise_name, sets_=sets)
    return None


def parse_file(file_path: str) -> list[Exercise]:
    """Parse a training log file and return a list of Exercise objects."""
    content = Path(file_path).read_text(encoding='utf-8')
    exercises: list[Exercise] = []

    lines = content.split('\n')

    for line in lines:
        line = line.strip()

        # Skip empty lines and date lines
        if not line:
            continue

        # Skip date lines (YYYY-MM-DD)
        if re.match(r'^\d{4}-\d{2}-\d{2}$', line):
            continue

        # Try to parse as exercise
        exercise = parse_exercise_line(line)
        if exercise:
            exercises.append(exercise)

    return exercises
