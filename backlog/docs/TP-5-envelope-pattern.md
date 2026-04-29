# TP-5: Envelope the payload JSONs with the type and schema

**Task ID**: TP-5
**Title**: Envelope the payload JSONs with the type and schema
**Status**: ✅ COMPLETED
**Date**: 2026-04-29
**Commit**: a84aa8a - feat: implement envelope pattern for set-centric and bench-centric data

## Overview

Implemented an envelope pattern for wrapping JSON payloads with schema metadata. This pattern provides explicit type identification and schema validation for both bench-centric and set-centric workout data formats.

## Requirements Met

### Type Identification
- ✅ Envelope contains explicit `type` field identifying the data format
- ✅ Supports `bench-centric.v1` and `set-centric.v1` formats
- ✅ Versioning support for future compatibility (e.g., `v2`, `v3`)

### Schema Metadata
- ✅ Envelope contains `schema` URL pointing to validation schema
- ✅ URLs follow pattern: `http://com.trainingparser/{type}_v1.schema.json`
- ✅ Schema URLs enable client-side schema discovery and validation

### Payload Structure
- ✅ Envelope wraps original payload data unchanged in `payload` field
- ✅ Payload validated against declared schema on unwrap
- ✅ Clean separation of metadata from data

## Implementation Details

### Core Module: `envelope.py`
```python
class Envelope:
    - __init__(envelope_type, payload)
    - to_dict() → Dictionary envelope
    - to_json(indent=2) → JSON string
    - from_dict(data) → Envelope instance
    - from_json(json_str) → Envelope instance

def wrap_payload(payload, envelope_type) → Dict
def unwrap_and_validate(envelope_data, schema_path, common_defs_path) → (bool, Dict, str)
```

### CLI Tool: `envelope_tool.py`
Commands:
- `wrap <input> <output> <type>` - Wrap raw payload in envelope
- `unwrap <input> <output>` - Extract payload from envelope
- `validate <envelope> <schema> [defs]` - Validate envelope + payload
- `convert <input> <output> [--wrap|--unwrap]` - Auto-detect and convert

### Schema Files
- `schema/envelope-base.schema.json` - Base envelope structure (type, schema, payload)
- `schema/envelope-bench-centric.schema.json` - Bench-centric envelope schema
- `schema/envelope-set-centric.schema.json` - Set-centric envelope schema

### Validation Scripts
- `validate_envelope_bench_centric.py` - Validates bench-centric examples
- `validate_envelope_set_centric.py` - Validates set-centric examples

### Updated Example Data
- `data/bench-centric-example.json` - Wrapped in envelope structure
- `data/set-centric-example.json` - Wrapped in envelope structure

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

## Workflow

### Writing (Creating Envelopes)
1. Create payload data
2. Wrap with `wrap_payload()` function
3. Write to JSON file

**Example**:
```python
from envelope import wrap_payload
import json

payload = {...}
envelope = wrap_payload(payload, "bench-centric.v1")
with open("output.json", "w") as f:
    json.dump(envelope, f)
```

### Reading (Consuming Envelopes)
1. Load envelope JSON
2. Extract schema URL from envelope
3. Unwrap and validate with `unwrap_and_validate()`
4. Use extracted payload in application

**Example**:
```python
from envelope import unwrap_and_validate
from pathlib import Path

with open("data.json") as f:
    envelope = json.load(f)

success, payload, msg = unwrap_and_validate(
    envelope,
    Path("schema/bench-centric.schema.json"),
    Path("schema/common-definitions.schema.json")
)

if success:
    # Use payload
    workout_id = payload["workout_id"]
```

## Testing & Validation

All validations passing:
- ✅ `validate_envelope_bench_centric.py` - Bench-centric envelope valid
- ✅ `validate_envelope_set_centric.py` - Set-centric envelope valid
- ✅ 356 unit tests passing
- ✅ MyPy type checking passing
- ✅ Pre-commit hooks passing

## Documentation

- **ENVELOPE_README.md** - Overview and quick start guide
- **ENVELOPE_IMPLEMENTATION.md** - Complete API reference (11KB)
- **ENVELOPE_QUICK_REFERENCE.md** - Quick lookup for common tasks
- **This document** - TP-5 task completion documentation

## Design Decisions

1. **Minimal Envelope** - Only three fields: `type`, `schema`, `payload`
2. **Payload Validation** - Uses original schema files, not envelope schemas
3. **Schema Discovery** - URL enables runtime schema fetching
4. **Backward Compatible** - All changes are additive
5. **Extensible** - Version identifiers allow future format changes

## Integration Points

### With Existing Code
- **Writing**: Use `wrap_payload()` before `json.dump()`
- **Reading**: Use `unwrap_and_validate()` after `json.load()`
- **Tests**: Updated to handle envelope-wrapped examples

### Supported Types
| Type | Schema |
|------|--------|
| `bench-centric.v1` | `http://com.trainingparser/bench-centric_v1.schema.json` |
| `set-centric.v1` | `http://com.trainingparser/set-centric_v1.schema.json` |

## Key Benefits

✅ **Type Safety** - Explicit format identification
✅ **Automatic Validation** - Payload validated on unwrap
✅ **Schema Discovery** - URLs enable client-side validation
✅ **Clean Separation** - Metadata separated from data
✅ **Backward Compatible** - Gradual migration possible
✅ **Extensible** - Easy to add new types and versions

## Files Changed

```
Created:
  ✅ envelope.py (5.4K)
  ✅ envelope_tool.py (7.2K)
  ✅ validate_envelope_bench_centric.py
  ✅ validate_envelope_set_centric.py
  ✅ schema/envelope-base.schema.json
  ✅ schema/envelope-bench-centric.schema.json
  ✅ schema/envelope-set-centric.schema.json
  ✅ ENVELOPE_README.md
  ✅ ENVELOPE_IMPLEMENTATION.md
  ✅ ENVELOPE_QUICK_REFERENCE.md

Modified:
  ✅ data/bench-centric-example.json
  ✅ data/set-centric-example.json
  ✅ tests/test_bench_centric_validation.py
  ✅ tests/test_set_centric_validation.py
```

## Commit Information

**Commit Hash**: a84aa8a
**Branch**: 3277-both-for-set-cen
**Author**: Claude Haiku 4.5
**Date**: 2026-04-29

**Message**:
```
feat: implement envelope pattern for set-centric and bench-centric data

Add envelope wrapper pattern with type identification and schema validation...
[See full commit message for details]
```

## Next Steps

1. **Integration**: Update data writing code to use `wrap_payload()`
2. **Migration**: Update data reading code to use `unwrap_and_validate()`
3. **Documentation**: Link envelope guides in project README
4. **Future Versions**: Create new envelope types as needed (e.g., `v2`)

## Acceptance Criteria

- ✅ Envelope structure defined (type, schema, payload)
- ✅ Python module with wrap/unwrap functionality
- ✅ CLI tool for testing and conversion
- ✅ Schema files created and validated
- ✅ Example data updated with envelopes
- ✅ Tests updated and passing
- ✅ Comprehensive documentation provided
- ✅ All validations passing
- ✅ Backward compatible implementation

## Status

**✅ COMPLETE** - All requirements met, all tests passing, ready for integration
