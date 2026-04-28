# Envelope Implementation Guide

This document describes the envelope pattern implementation for wrapping and validating workout data payloads with schema metadata.

## Table of Contents
1. [Overview](#overview)
2. [Envelope Structure](#envelope-structure)
3. [Core Components](#core-components)
4. [Usage Patterns](#usage-patterns)
5. [API Reference](#api-reference)
6. [Examples](#examples)

## Overview

The envelope pattern provides a standard way to wrap JSON payloads with metadata about their type and schema. This allows:

- **Type identification**: Explicit declaration of data format (bench-centric.v1, set-centric.v1)
- **Schema validation**: Payload validation against declared schemas
- **Schema discovery**: URL pointing to the schema that validates the payload
- **Extensibility**: Easy to add new envelope types with versioning

## Envelope Structure

All envelopes follow this structure:

```json
{
  "type": "bench-centric.v1",
  "schema": "http://com.trainingparser/bench-centric_v1.schema.json",
  "payload": {
    /* your actual data here */
  }
}
```

### Field Descriptions

| Field | Type | Description |
|-------|------|-------------|
| `type` | string | Envelope type identifier. Examples: `bench-centric.v1`, `set-centric.v1` |
| `schema` | string | URI pointing to the JSON Schema that validates the payload |
| `payload` | object | The actual workout data (validated against the schema) |

### Supported Types

- `bench-centric.v1` - Bench-centric training format with superset support
  - Schema: `http://com.trainingparser/bench-centric_v1.schema.json`
- `set-centric.v1` - Set-centric training format with set numbers
  - Schema: `http://com.trainingparser/set-centric_v1.schema.json`

## Core Components

### 1. envelope.py - Python Module

#### Envelope Class
```python
class Envelope:
    """Represents an envelope containing a typed payload with schema information."""

    BENCH_CENTRIC_V1 = "bench-centric.v1"
    SET_CENTRIC_V1 = "set-centric.v1"
    SCHEMA_URLS = { /* type to URL mapping */ }

    def __init__(self, envelope_type: str, payload: Dict[str, Any])
    def to_dict(self) -> Dict[str, Any]
    def to_json(self, indent: int = 2) -> str
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Envelope"
    @classmethod
    def from_json(cls, json_str: str) -> "Envelope"
```

#### Functions
```python
def wrap_payload(payload: Dict[str, Any], envelope_type: str) -> Dict[str, Any]:
    """Wrap a payload in an envelope."""

def unwrap_and_validate(
    envelope_data: Dict[str, Any],
    payload_schema_path: Union[str, Path],
    common_defs_path: Optional[Union[str, Path]] = None,
) -> Tuple[bool, Dict[str, Any], str]:
    """Unwrap envelope, validate payload, and extract data."""
```

### 2. envelope_tool.py - CLI Tool

Command-line tool for envelope operations:

```bash
envelope_tool.py wrap <input> <output> <type>          # Wrap payload
envelope_tool.py unwrap <input> <output>               # Unwrap payload
envelope_tool.py validate <envelope> <schema> [defs]   # Validate envelope
envelope_tool.py convert <input> <output> [options]    # Auto-convert
```

### 3. Schema Files

- `schema/envelope-base.schema.json` - Base envelope structure validation
- `schema/envelope-bench-centric.schema.json` - Bench-centric envelope
- `schema/envelope-set-centric.schema.json` - Set-centric envelope
- `schema/bench-centric.schema.json` - Payload schema (bench-centric)
- `schema/set-centric.schema.json` - Payload schema (set-centric)

### 4. Validation Scripts

- `validate_envelope_bench_centric.py` - Validates bench-centric examples
- `validate_envelope_set_centric.py` - Validates set-centric examples

## Usage Patterns

### Pattern 1: Writing (Creating Envelopes)

**Step 1**: Create raw payload data
```python
payload = {
    "workout_id": "w_2026_01_23",
    "type": "bench-centric",
    "date": "2026-01-23T18:45:00Z",
    "location": "My Gym",
    "exercises": [...]
}
```

**Step 2**: Wrap in envelope
```python
from envelope import wrap_payload

envelope = wrap_payload(payload, "bench-centric.v1")
# OR
from envelope import Envelope
env = Envelope("bench-centric.v1", payload)
envelope = env.to_dict()
```

**Step 3**: Write to file
```python
import json
with open("workout.json", "w") as f:
    json.dump(envelope, f, indent=2)
```

### Pattern 2: Reading (Consuming Envelopes)

**Step 1**: Load envelope
```python
import json
with open("workout.json", "r") as f:
    envelope_data = json.load(f)
```

**Step 2**: Extract schema from envelope
```python
schema_url = envelope_data["schema"]  # "http://com.trainingparser/..."
envelope_type = envelope_data["type"]  # "bench-centric.v1"
```

**Step 3**: Validate and extract payload
```python
from envelope import unwrap_and_validate
from pathlib import Path

success, payload, message = unwrap_and_validate(
    envelope_data,
    Path("schema/bench-centric.schema.json"),
    Path("schema/common-definitions.schema.json")
)

if success:
    # Use payload in your application
    workout_id = payload["workout_id"]
    exercises = payload["exercises"]
else:
    # Handle validation error
    print(f"Validation failed: {message}")
```

### Pattern 3: Auto-Detection and Conversion

Automatically detect format and convert:
```bash
# Auto-detect and convert envelope to plain JSON
python envelope_tool.py convert workout.json output.json

# Auto-detect and convert plain JSON to envelope
python envelope_tool.py convert payload.json output.json
```

## API Reference

### envelope.wrap_payload()
```python
def wrap_payload(
    payload: Dict[str, Any],
    envelope_type: str
) -> Dict[str, Any]:
```

Wraps a payload dictionary in an envelope structure.

**Parameters:**
- `payload`: The data to wrap
- `envelope_type`: Type identifier ("bench-centric.v1" or "set-centric.v1")

**Returns:** Dictionary with envelope structure

**Raises:** `ValueError` if envelope type is unknown

### envelope.unwrap_and_validate()
```python
def unwrap_and_validate(
    envelope_data: Dict[str, Any],
    payload_schema_path: Union[str, Path],
    common_defs_path: Optional[Union[str, Path]] = None
) -> Tuple[bool, Dict[str, Any], str]:
```

Unwraps envelope, validates payload, and extracts data.

**Parameters:**
- `envelope_data`: The envelope dictionary
- `payload_schema_path`: Path to schema file for payload validation
- `common_defs_path`: Optional path to common definitions for schema references

**Returns:** Tuple of (success, payload, message)
- `success` (bool): True if validation passed
- `payload` (dict): Extracted payload (empty dict if validation failed)
- `message` (str): Status or error message

### Envelope Class

```python
class Envelope:
    def __init__(self, envelope_type: str, payload: Dict[str, Any])
    def to_dict(self) -> Dict[str, Any]
    def to_json(self, indent: int = 2) -> str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Envelope"
    @classmethod
    def from_json(cls, json_str: str) -> "Envelope"
```

## Examples

### Example 1: Wrap a Bench-Centric Workout

```python
from envelope import wrap_payload
import json

# Raw payload
workout = {
    "workout_id": "w001",
    "type": "bench-centric",
    "date": "2026-01-23T18:45:00Z",
    "exercises": [
        {
            "name": "Bench Press",
            "superset_id": "A",
            "equipment": "barbell",
            "sets": [
                {"reps": 8, "weight": 80, "unit": "kg", "rpe": 7}
            ]
        }
    ]
}

# Wrap in envelope
envelope = wrap_payload(workout, "bench-centric.v1")

# Write to file
with open("workout.json", "w") as f:
    json.dump(envelope, f, indent=2)

# Output:
# {
#   "type": "bench-centric.v1",
#   "schema": "http://com.trainingparser/bench-centric_v1.schema.json",
#   "payload": { /* workout data */ }
# }
```

### Example 2: Validate and Extract Envelope

```python
from envelope import unwrap_and_validate
from pathlib import Path
import json

# Load envelope
with open("workout.json", "r") as f:
    envelope = json.load(f)

# Validate and extract
success, payload, message = unwrap_and_validate(
    envelope,
    Path("schema/bench-centric.schema.json"),
    Path("schema/common-definitions.schema.json")
)

if success:
    print(message)
    # Use payload
    for exercise in payload["exercises"]:
        print(f"Exercise: {exercise['name']}")
else:
    print(f"Error: {message}")
```

### Example 3: CLI Usage

```bash
# Wrap a raw payload file
python envelope_tool.py wrap raw_workout.json envelope.json bench-centric.v1

# Unwrap and extract payload
python envelope_tool.py unwrap envelope.json payload.json

# Validate envelope against schema
python envelope_tool.py validate envelope.json schema/bench-centric.schema.json schema/common-definitions.schema.json

# Convert (auto-detect)
python envelope_tool.py convert data.json output.json
```

## Validation Workflow

The `unwrap_and_validate()` function follows this workflow:

1. **Parse Envelope**: Verify envelope structure (type, schema, payload)
2. **Load Payload Schema**: Read the schema file for payload validation
3. **Create Validator**: Initialize JSON schema validator with references
4. **Validate Payload**: Validate payload against schema
5. **Return Result**:
   - Success: Return (True, payload, success_message)
   - Failure: Return (False, {}, error_message)

## Error Handling

The validation functions return detailed error messages for common issues:

```
✗ Invalid envelope structure: ...      # Envelope parsing failed
✗ Payload validation failed: ...       # Payload doesn't match schema
✗ Schema file not found: ...           # Schema path doesn't exist
✗ JSON decode error: ...               # JSON parsing failed
✗ Unexpected error: ...                # Unexpected exception
```

## Integration Points

### With Existing Code

1. **When Writing Data**: Use `wrap_payload()` before saving to JSON
2. **When Reading Data**: Use `unwrap_and_validate()` after loading JSON
3. **Schema Validation**: Leverage existing schema files without changes

### With CLI

```python
# In your application
from envelope import unwrap_and_validate
from pathlib import Path

# When receiving JSON from external sources
success, data, msg = unwrap_and_validate(envelope_json, Path("schema/..."))
if success:
    # Process data
    pass
```

## Schema Discovery

Clients can discover and validate schemas using the URL in the envelope:

```python
envelope = json.load(envelope_file)
schema_url = envelope["schema"]

# Use schema_url to fetch schema from server if needed
# Or validate against local copy at schema/<name>.schema.json
```

## Version Control

Envelope types include version identifiers (e.g., `.v1`), allowing:

- **Breaking Changes**: Create new version (e.g., `bench-centric.v2`)
- **Backward Compatibility**: Keep old versions available
- **Migration**: Read old versions, validate against schema, re-wrap in new version

## Performance Considerations

- **Minimal Overhead**: Envelope structure is small (< 100 bytes)
- **Single Validation**: Payload validated once during unwrap
- **Lazy Loading**: Schemas loaded only when needed
- **Caching**: Consider caching compiled schema validators
