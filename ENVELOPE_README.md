# Envelope Pattern Implementation

## Overview

This project now implements an **envelope pattern** for wrapping and validating JSON payloads with schema metadata. The envelope structure provides:

- **Type identification**: Explicit declaration of data format (bench-centric.v1, set-centric.v1)
- **Schema validation**: Automatic validation of payloads against declared schemas
- **Schema discovery**: URLs pointing to schemas for client-side validation
- **Clean separation**: Envelope metadata kept separate from payload

## Quick Start

### Writing (Creating Envelopes)

```python
from envelope import wrap_payload
import json

payload = {"workout_id": "w001", "date": "2026-01-23T18:45:00Z", "exercises": [...]}
envelope = wrap_payload(payload, "bench-centric.v1")

with open("output.json", "w") as f:
    json.dump(envelope, f, indent=2)
```

### Reading (Consuming Envelopes)

```python
from envelope import unwrap_and_validate
from pathlib import Path
import json

with open("data.json") as f:
    envelope_data = json.load(f)

success, payload, msg = unwrap_and_validate(
    envelope_data,
    Path("schema/bench-centric.schema.json"),
    Path("schema/common-definitions.schema.json")
)

if success:
    # Use payload directly
    workout_id = payload["workout_id"]
else:
    print(f"Validation error: {msg}")
```

## Envelope Structure

```json
{
  "type": "bench-centric.v1",
  "schema": "http://com.trainingparser/bench-centric_v1.schema.json",
  "payload": {
    "workout_id": "w_2026_01_23",
    "type": "bench-centric",
    "date": "2026-01-23T18:45:00Z",
    "exercises": [...]
  }
}
```

## Components

### Core Module (`envelope.py`)
- **Envelope class**: Wrap/unwrap payloads with metadata
- **wrap_payload()**: Convert raw data to envelope
- **unwrap_and_validate()**: Extract payload and validate against schema

### CLI Tool (`envelope_tool.py`)
```bash
python envelope_tool.py wrap <input> <output> <type>     # Wrap payload
python envelope_tool.py unwrap <input> <output>          # Unwrap payload
python envelope_tool.py validate <env> <schema> [defs]   # Validate
python envelope_tool.py convert <input> <output>         # Auto-convert
```

### Validation Scripts
- `validate_envelope_bench_centric.py` - Validate bench-centric example
- `validate_envelope_set_centric.py` - Validate set-centric example

### Schema Files
- `schema/envelope-base.schema.json` - Envelope structure
- `schema/envelope-bench-centric.schema.json` - Bench-centric envelope
- `schema/envelope-set-centric.schema.json` - Set-centric envelope

### Example Data
- `data/bench-centric-example.json` - Wrapped bench-centric data
- `data/set-centric-example.json` - Wrapped set-centric data

## Documentation

- **ENVELOPE_IMPLEMENTATION.md** - Complete reference with examples and API docs
- **ENVELOPE_QUICK_REFERENCE.md** - Quick lookup for common tasks
- **This file** - Overview and quick start

## Supported Envelope Types

| Type | Schema URL |
|------|-----------|
| `bench-centric.v1` | `http://com.trainingparser/bench-centric_v1.schema.json` |
| `set-centric.v1` | `http://com.trainingparser/set-centric_v1.schema.json` |

## Workflow

### When Writing
1. Create payload data
2. **Wrap** in envelope using `wrap_payload()`
3. Write to JSON file

### When Reading
1. Load JSON file
2. **Unwrap and validate** using `unwrap_and_validate()`
3. Use extracted payload in your application

## Benefits

✓ **Type Safety**: Explicit envelope type prevents format confusion
✓ **Automatic Validation**: Payload validated against schema on unwrap
✓ **Schema Discovery**: Schema URL included for client-side validation
✓ **Backward Compatible**: Original schema files unchanged
✓ **Extensible**: Easy to add new envelope types with versioning
✓ **Clean Interface**: Simple Python API and CLI tools

## Validation Results

```
✓ Bench-centric envelope validation successful! Type: bench-centric.v1
✓ Set-centric envelope validation successful! Type: set-centric.v1
```

Both example files validate successfully against their respective payload schemas.

## Integration Steps

1. **For Writing**:
   ```python
   from envelope import wrap_payload

   # Before: json.dump(payload, f)
   # After:
   envelope = wrap_payload(payload, "bench-centric.v1")
   json.dump(envelope, f)
   ```

2. **For Reading**:
   ```python
   from envelope import unwrap_and_validate

   # Before: payload = json.load(f)
   # After:
   success, payload, msg = unwrap_and_validate(env_data, schema_path, common_defs_path)
   if success:
       # Use payload
   ```

## CLI Examples

```bash
# Wrap a payload file
python envelope_tool.py wrap raw.json wrapped.json bench-centric.v1

# Unwrap to get payload
python envelope_tool.py unwrap wrapped.json payload.json

# Validate envelope + payload
python envelope_tool.py validate wrapped.json schema/bench-centric.schema.json schema/common-definitions.schema.json

# Auto-detect and convert between formats
python envelope_tool.py convert data.json output.json
```

## Testing

Run the validation scripts to test the implementation:

```bash
# Validate bench-centric envelope
python validate_bench_centric.py

# Validate set-centric envelope
python validate_set_centric.py
```

Both should output:
```
✓ Envelope validation successful! Type: [type].v1
```

## File Structure

```
├── envelope.py                              # Core module
├── envelope_tool.py                         # CLI tool
├── validate_envelope_bench_centric.py       # Validation script
├── validate_envelope_set_centric.py         # Validation script
├── ENVELOPE_README.md                       # This file
├── ENVELOPE_IMPLEMENTATION.md               # Full documentation
├── ENVELOPE_QUICK_REFERENCE.md              # Quick reference
├── schema/
│   ├── envelope-base.schema.json            # Envelope structure
│   ├── envelope-bench-centric.schema.json   # Bench-centric envelope
│   ├── envelope-set-centric.schema.json     # Set-centric envelope
│   ├── bench-centric.schema.json            # (unchanged)
│   ├── set-centric.schema.json              # (unchanged)
│   └── common-definitions.schema.json       # (unchanged)
└── data/
    ├── bench-centric-example.json           # Updated with envelope
    └── set-centric-example.json             # Updated with envelope
```

## Key Design Decisions

1. **Minimal Envelope**: Only contains type, schema, and payload fields
2. **Payload Validation**: Uses original schema files, not envelope schemas
3. **Schema URLs**: Enable schema discovery and client-side validation
4. **Version Identifiers**: Type includes version (e.g., `.v1`) for future compatibility
5. **Backward Compatible**: All changes are additive, existing code can be updated gradually

## Next Steps

1. Use `wrap_payload()` when creating workout JSON files
2. Use `unwrap_and_validate()` when reading workout JSON files
3. Reference schema URLs in envelope for downstream consumers
4. Create new envelope types for future format changes (e.g., `bench-centric.v2`)

## Support

For detailed API reference and advanced usage, see:
- **ENVELOPE_IMPLEMENTATION.md** - Complete documentation
- **ENVELOPE_QUICK_REFERENCE.md** - Quick lookup guide
