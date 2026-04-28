# Envelope Pattern - Quick Reference

## Structure

```json
{
  "type": "bench-centric.v1",
  "schema": "http://com.trainingparser/bench-centric_v1.schema.json",
  "payload": { /* your data */ }
}
```

## Python Usage

### Writing (Wrapping)
```python
from envelope import wrap_payload, Envelope
import json

# Method 1: Using wrap_payload function
payload = {"workout_id": "w001", "date": "...", "exercises": [...]}
envelope = wrap_payload(payload, "bench-centric.v1")
with open("output.json", "w") as f:
    json.dump(envelope, f)

# Method 2: Using Envelope class
env = Envelope("bench-centric.v1", payload)
json_str = env.to_json()
```

### Reading (Unwrapping & Validating)
```python
from envelope import unwrap_and_validate
from pathlib import Path
import json

# Load envelope
with open("data.json") as f:
    envelope_data = json.load(f)

# Unwrap and validate
success, payload, message = unwrap_and_validate(
    envelope_data,
    Path("schema/bench-centric.schema.json"),
    Path("schema/common-definitions.schema.json")
)

if success:
    print(f"✓ {message}")
    # Use payload
    print(payload["workout_id"])
else:
    print(f"✗ {message}")
```

## CLI Usage

### Wrap
```bash
python envelope_tool.py wrap input.json output.json bench-centric.v1
```

### Unwrap
```bash
python envelope_tool.py unwrap envelope.json payload.json
```

### Validate
```bash
python envelope_tool.py validate envelope.json schema/bench-centric.schema.json schema/common-definitions.schema.json
```

### Convert (Auto-detect)
```bash
# Envelope → Payload
python envelope_tool.py convert envelope.json payload.json

# Payload → Envelope (auto-wraps in bench-centric.v1)
python envelope_tool.py convert payload.json envelope.json

# Force specific type
python envelope_tool.py convert payload.json envelope.json --wrap --type set-centric.v1
```

## Validation Scripts

Run pre-configured validations:

```bash
# Validate bench-centric example with envelope
python validate_envelope_bench_centric.py

# Validate set-centric example with envelope
python validate_envelope_set_centric.py
```

## Key Files

| File | Purpose |
|------|---------|
| `envelope.py` | Python module with Envelope class |
| `envelope_tool.py` | CLI tool for envelope operations |
| `data/bench-centric-example.json` | Wrapped bench-centric example |
| `data/set-centric-example.json` | Wrapped set-centric example |
| `schema/envelope-base.schema.json` | Envelope structure schema |
| `schema/envelope-*.schema.json` | Type-specific envelope schemas |
| `ENVELOPE_IMPLEMENTATION.md` | Full documentation |

## Workflow Examples

### Complete Write-Read Cycle
```python
from envelope import wrap_payload, unwrap_and_validate
from pathlib import Path
import json

# 1. Create payload
workout = {
    "workout_id": "w_abc123",
    "type": "bench-centric",
    "date": "2026-01-23T18:45:00Z",
    "exercises": [...]
}

# 2. Wrap in envelope
envelope = wrap_payload(workout, "bench-centric.v1")

# 3. Save to file
with open("workout.json", "w") as f:
    json.dump(envelope, f, indent=2)

# 4. Later: Load and validate
with open("workout.json") as f:
    envelope_data = json.load(f)

success, payload, msg = unwrap_and_validate(
    envelope_data,
    Path("schema/bench-centric.schema.json"),
    Path("schema/common-definitions.schema.json")
)

if success:
    # Use payload
    print(f"Workout ID: {payload['workout_id']}")
```

## Error Messages

| Error | Meaning | Fix |
|-------|---------|-----|
| `Invalid envelope structure: ...` | Missing type/schema/payload | Ensure envelope has all three fields |
| `Payload validation failed: ...` | Data doesn't match schema | Verify payload matches schema requirements |
| `Schema file not found: ...` | Schema path doesn't exist | Check schema file path |
| `JSON decode error: ...` | Invalid JSON | Fix JSON syntax |

## Envelope Types

| Type | Schema |
|------|--------|
| `bench-centric.v1` | `http://com.trainingparser/bench-centric_v1.schema.json` |
| `set-centric.v1` | `http://com.trainingparser/set-centric_v1.schema.json` |

## Integration Checklist

- [ ] Import envelope module where needed
- [ ] Wrap payloads before writing to JSON
- [ ] Unwrap and validate before using data
- [ ] Use schema URLs for schema discovery
- [ ] Handle validation failures gracefully
- [ ] Document envelope type requirements
- [ ] Test with both bench-centric and set-centric data

## Tips

1. **Always validate**: Use `unwrap_and_validate()` even if you created the envelope
2. **Schema discovery**: Extract schema URL from envelope for client-side validation
3. **Versioning**: Add new types (e.g., `bench-centric.v2`) for breaking changes
4. **Error handling**: Check `success` flag before using payload
5. **CLI for testing**: Use envelope_tool.py to test wrap/unwrap cycles
