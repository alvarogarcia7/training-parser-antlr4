# Data Access Library Guide

This guide describes the new data access library created to unify reading, parsing, and name update functionality across the project.

## Overview

The library provides a clean abstraction for common data access patterns used across `main.py`, `splitter.py`, and `main_export.py`. It eliminates code duplication and makes it easy to reuse these operations in new scripts.

## Architecture

The library is organized into focused modules:

### 1. **DataReader** - File Reading
Handles reading training log files in different formats.

```python
from data_access import DataReader

# Read entire file as string
content = DataReader.read_file('training.txt')

# Read file as lines, preserving structure
lines = DataReader.read_lines('training.txt')
```

### 2. **DataParser** - Text Parsing
Converts text into Exercise objects using ANTLR4.

```python
from data_access import DataParser

# Parse raw exercise text (no date filtering)
exercises = DataParser.parse_raw_text(exercise_text)

# Parse a simple file, filtering out date lines (YYYY-MM-DD)
exercises = DataParser.parse_file_filtered('training.txt')
```

### 3. **SessionGrouper** - Session Extraction
Splits multi-session files into RawWorkoutSession objects.

```python
from data_access import SessionGrouper

lines = DataReader.read_lines('multi-session.txt')
sessions = SessionGrouper.group_by_sessions(lines)
# Each session has: date, payload, notes
```

### 4. **ExerciseParser** - Session Parsing with Standardization
Parses RawWorkoutSessions and standardizes exercise names.

```python
from data_access import ExerciseParser
from parser import StandardizeName

renamer = StandardizeName()
parser = ExerciseParser(renamer)
parsed_sessions = parser.parse_sessions(raw_sessions)
# Each session now has parsed Exercise objects with standardized names
```

### 5. **DataSerializer** - Output Formatting
Converts Exercise objects to different output formats.

```python
from data_access import DataSerializer

# Serialize to set-centric JSON
json_data = DataSerializer.to_set_centric_json(exercises)

# Serialize sessions to TSV rows (for CSV output)
rows = DataSerializer.to_tsv_rows(sessions)
```

### 6. **DataAccess** - High-Level Interface
Main entry point combining all functionality.

```python
from data_access import DataAccess

data_access = DataAccess()

# For simple single-file parsing
exercises = data_access.parse_single_file('training.txt')

# For multi-session files
sessions = data_access.parse_multi_session_file('multi-session.txt')
```

## Type Definitions

```python
# Raw session from file (before parsing)
RawWorkoutSession = TypedDict('RawWorkoutSession', {
    'date': str,
    'payload': str,        # Unparsed exercise text
    'notes': str           # Comment lines starting with #
})

# Parsed session (after exercise parsing)
ParsedWorkoutSession = TypedDict('ParsedWorkoutSession', {
    'date': str,
    'parsed': list[Exercise],  # Parsed and standardized exercises
    'notes': str
})
```

## Usage Examples

### Example 1: Simple File Parsing
```python
from data_access import DataAccess

data = DataAccess()
exercises = data.parse_single_file('training.txt')

for exercise in exercises:
    print(f"{exercise.name}: {len(exercise.sets_)} sets")
```

### Example 2: Multi-Session File with Export
```python
from data_access import DataAccess, DataSerializer
import csv

data = DataAccess()
sessions = data.parse_multi_session_file('all-workouts.txt')

rows = DataSerializer.to_tsv_rows(sessions)

with open('output.tsv', 'w') as f:
    writer = csv.writer(f, delimiter='\t')
    writer.writerows(rows)
```

### Example 3: JSON Export with Validation
```python
from data_access import DataAccess, DataSerializer
import json

data = DataAccess()
exercises = data.parse_single_file('training.txt')

json_data = DataSerializer.to_set_centric_json(exercises)
json_output = json.dumps(json_data, indent=2)

print(json_output)
```

### Example 4: Custom Standardization
```python
from data_access import DataAccess
from parser import StandardizeName

# Create custom standardizer with your rules
class CustomStandardizer(StandardizeName):
    def __init__(self):
        super().__init__()
        # Add or modify synonym mappings
        self._synonyms.append({
            'clean': 'my custom exercise',
            'synonyms': ['custom', 'ce']
        })

data = DataAccess(standardizer=CustomStandardizer())
exercises = data.parse_single_file('training.txt')
```

## Refactored Files

### main.py
**Before**: ~40 lines of ANTLR setup and regex filtering
**After**: ~10 lines using `DataAccess.parse_single_file()`

```python
from data_access import DataAccess

def parse_file(file_path: str) -> list[Exercise]:
    data_access = DataAccess()
    return data_access.parse_single_file(file_path)
```

### splitter.py
**Before**: ~150 lines with duplicate parsing logic
**After**: ~40 lines using reusable library components

```python
class Splitter:
    def __init__(self):
        self.data_access = DataAccess()

    def main(self, file: str) -> list[ParsedWorkoutSession]:
        return self.data_access.parse_multi_session_file(file)
```

### main_export.py
**Before**: Uses `main.parse_file()` directly
**After**: Uses `DataAccess` with serializer

```python
data_access = DataAccess()
exercises = data_access.parse_single_file(str(input_path))
json_data = DataSerializer.to_set_centric_json(exercises)
```

## New CLI Program

A unified CLI program `cli.py` provides multiple subcommands with consistent `--format` options:

### Parse Command
Parse a single file and display exercises.

```bash
python cli.py parse training.txt
python cli.py parse training.txt --format json
```

### Export Command
Parse and export to JSON with optional validation.

```bash
python cli.py export training.txt -o output.json
python cli.py export training.txt -o output.json --format set-centric --validate
python cli.py export training.txt --format bench-centric
```

### Batch Command
Parse multi-session files with flexible output.

```bash
python cli.py batch multi-session.txt -o output.tsv
python cli.py batch multi-session.txt --format json -o sessions.json
python cli.py batch multi-session.txt              # TSV to stdout
```

## Benefits

1. **DRY (Don't Repeat Yourself)**: Eliminates duplicate parsing/reading logic
2. **Composable**: Each component can be used independently or together
3. **Testable**: Smaller, focused modules are easier to unit test
4. **Maintainable**: Changes to parsing logic only need to be made once
5. **Extensible**: Easy to create custom standardizers or add new serialization formats
6. **Consistent**: All programs use the same underlying parsing pipeline

## Integration Checklist

- ✅ Created `data_access.py` with 6 focused classes
- ✅ Refactored `main.py` to use library
- ✅ Refactored `splitter.py` to use library
- ✅ Refactored `main_export.py` to use library
- ✅ Created `cli.py` with unified subcommands
- ✅ Unified output formats with `--format` option across all commands

## Future Enhancements

- Add support for bench-centric JSON serialization
- Add database export format
- Add real-time progress callbacks for large files
- Add filtering/querying capabilities
- Add custom exercise validation hooks
