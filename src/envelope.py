"""
Envelope utility for wrapping and unwrapping data payloads with schema validation.

Provides functionality to:
- Wrap payloads in an envelope with type, schema URL, and payload
- Unwrap envelopes, validate against schema, and extract payload
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional, Tuple, Union, cast

import jsonschema
from jsonschema import RefResolver, ValidationError


class Envelope:
    """Represents an envelope containing a typed payload with schema information."""

    BENCH_CENTRIC_V1 = "bench-centric.v1"
    SET_CENTRIC_V1 = "set-centric.v1"

    SCHEMA_URLS = {
        BENCH_CENTRIC_V1: "http://com.trainingparser/bench-centric_v1.schema.json",
        SET_CENTRIC_V1: "http://com.trainingparser/set-centric_v1.schema.json",
    }

    def __init__(self, envelope_type: str, payload: Dict[str, Any]):
        """Initialize an envelope.

        Args:
            envelope_type: Type identifier (e.g., 'bench-centric.v1')
            payload: The data payload to wrap
        """
        if envelope_type not in self.SCHEMA_URLS:
            raise ValueError(f"Unknown envelope type: {envelope_type}")
        self.type = envelope_type
        self.schema = self.SCHEMA_URLS[envelope_type]
        self.payload = payload

    def to_dict(self) -> Dict[str, Any]:
        """Convert envelope to dictionary format."""
        return {
            "type": self.type,
            "schema": self.schema,
            "payload": self.payload,
        }

    def to_json(self, indent: int = 2) -> str:
        """Convert envelope to JSON string."""
        return json.dumps(self.to_dict(), indent=indent)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Envelope":
        """Create envelope from dictionary."""
        if not isinstance(data, dict):
            raise ValueError("Envelope data must be a dictionary")
        if "type" not in data or "schema" not in data or "payload" not in data:
            raise ValueError("Envelope must contain 'type', 'schema', and 'payload' fields")
        return cls(data["type"], data["payload"])

    @classmethod
    def from_json(cls, json_str: str) -> "Envelope":
        """Create envelope from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)


def wrap_payload(payload: Dict[str, Any], envelope_type: str) -> Dict[str, Any]:
    """Wrap a payload in an envelope.

    Args:
        payload: The data to wrap
        envelope_type: Type identifier (e.g., 'bench-centric.v1')

    Returns:
        Dictionary with envelope structure
    """
    envelope = Envelope(envelope_type, payload)
    return envelope.to_dict()


def unwrap_and_validate(
    envelope_data: Dict[str, Any],
    payload_schema_path: Union[str, Path],
    common_defs_path: Optional[Union[str, Path]] = None,
) -> Tuple[bool, Dict[str, Any], str]:
    """Unwrap envelope, validate payload against schema, and extract payload.

    Args:
        envelope_data: Dictionary containing envelope structure
        payload_schema_path: Path to the JSON schema file for validating the payload
        common_defs_path: Optional path to common definitions schema for $ref resolution

    Returns:
        Tuple of (success: bool, payload: Dict, message: str)
    """
    try:
        envelope = Envelope.from_dict(envelope_data)
    except ValueError as e:
        return False, {}, f"Invalid envelope structure: {e}"

    payload_schema_path = Path(payload_schema_path)
    if common_defs_path is not None:
        common_defs_path = Path(common_defs_path)

    if not payload_schema_path.exists():
        return False, {}, f"Payload schema file not found: {payload_schema_path}"

    if common_defs_path is not None and not common_defs_path.exists():
        return False, {}, f"Common definitions file not found: {common_defs_path}"

    try:
        payload_schema = _load_json_file(payload_schema_path)
        jsonschema.validators.validator_for(payload_schema).check_schema(payload_schema)

        resolver: Optional[RefResolver] = None
        if common_defs_path is not None:
            common_defs = _load_json_file(common_defs_path)
            store = {common_defs["$id"]: common_defs}
            resolver = RefResolver.from_schema(payload_schema, store=store)

        validator_class = jsonschema.validators.validator_for(payload_schema)
        if resolver is not None:
            validator = validator_class(payload_schema, resolver=resolver)
        else:
            validator = validator_class(payload_schema)

        validator.validate(envelope.payload)
        message = f"✓ Envelope validation successful! Type: {envelope.type}"
        return True, envelope.payload, message

    except jsonschema.SchemaError as e:
        return False, {}, f"✗ Invalid schema: {e.message}"
    except ValidationError as e:
        error_msg = f"✗ Payload validation failed: {e.message}"
        if e.absolute_path:
            path = ".".join(str(p) for p in e.absolute_path)
            error_msg += f" (at {path})"
        return False, {}, error_msg
    except json.JSONDecodeError as e:
        return False, {}, f"✗ JSON decode error: {e}"
    except Exception as e:
        return False, {}, f"✗ Unexpected error: {e}"


def _load_json_file(file_path: Path) -> Dict[str, Any]:
    """Load and parse a JSON file."""
    with open(file_path, "r", encoding="utf-8") as f:
        return cast(Dict[str, Any], json.load(f))
