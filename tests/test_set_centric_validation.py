"""Tests for set-centric validation."""

import json
from pathlib import Path
from typing import Any

import jsonschema
from jsonschema import RefResolver
import pytest


def create_validator(schema: dict[str, Any]) -> jsonschema.protocols.Validator:
    """Create a validator with common definitions schema registered."""
    common_defs_path = Path("schema/common-definitions.schema.json")
    with open(common_defs_path, 'r', encoding='utf-8') as f:
        common_defs = json.load(f)
    
    store = {
        common_defs["$id"]: common_defs
    }
    
    resolver = RefResolver.from_schema(schema, store=store)
    validator_class = jsonschema.validators.validator_for(schema)
    return validator_class(schema, resolver=resolver)


def test_set_centric_schema_is_valid() -> None:
    """Test that the set-centric schema itself is valid."""
    schema_path = Path("schema/set-centric.schema.json")
    
    with open(schema_path, 'r', encoding='utf-8') as f:
        schema = json.load(f)
    
    validator_class = jsonschema.validators.validator_for(schema)
    validator_class.check_schema(schema)


def test_set_centric_example_validates() -> None:
    """Test that the set-centric example validates against the schema."""
    schema_path = Path("schema/set-centric.schema.json")
    data_path = Path("data/set-centric-example.json")
    
    with open(schema_path, 'r', encoding='utf-8') as f:
        schema = json.load(f)
    
    with open(data_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    validator = create_validator(schema)
    validator.validate(data)


def test_set_centric_requires_workout_id() -> None:
    """Test that workout_id is required."""
    schema_path = Path("schema/set-centric.schema.json")
    
    with open(schema_path, 'r', encoding='utf-8') as f:
        schema = json.load(f)
    
    invalid_data = {
        "date": "2026-01-23T18:45:00Z",
        "exercises": [
            {
                "name": "Bench Press",
                "sets": [
                    {
                        "setNumber": 1,
                        "repetitions": 8,
                        "weight": {"amount": 60, "unit": "kg"}
                    }
                ]
            }
        ]
    }
    
    validator = create_validator(schema)
    with pytest.raises(jsonschema.ValidationError):
        validator.validate(invalid_data)


def test_set_centric_requires_date() -> None:
    """Test that date is required."""
    schema_path = Path("schema/set-centric.schema.json")
    
    with open(schema_path, 'r', encoding='utf-8') as f:
        schema = json.load(f)
    
    invalid_data = {
        "workout_id": "w_2026_01_23",
        "exercises": [
            {
                "name": "Bench Press",
                "sets": [
                    {
                        "setNumber": 1,
                        "repetitions": 8,
                        "weight": {"amount": 60, "unit": "kg"}
                    }
                ]
            }
        ]
    }
    
    validator = create_validator(schema)
    with pytest.raises(jsonschema.ValidationError):
        validator.validate(invalid_data)


def test_set_centric_requires_exercises() -> None:
    """Test that exercises array is required."""
    schema_path = Path("schema/set-centric.schema.json")
    
    with open(schema_path, 'r', encoding='utf-8') as f:
        schema = json.load(f)
    
    invalid_data = {
        "workout_id": "w_2026_01_23",
        "date": "2026-01-23T18:45:00Z"
    }
    
    validator = create_validator(schema)
    with pytest.raises(jsonschema.ValidationError):
        validator.validate(invalid_data)


def test_set_centric_validates_weight_minimum() -> None:
    """Test that weight amount must be >= 0."""
    schema_path = Path("schema/set-centric.schema.json")
    
    with open(schema_path, 'r', encoding='utf-8') as f:
        schema = json.load(f)
    
    invalid_data = {
        "workout_id": "w_2026_01_23",
        "date": "2026-01-23T18:45:00Z",
        "exercises": [
            {
                "name": "Bench Press",
                "sets": [
                    {
                        "setNumber": 1,
                        "repetitions": 8,
                        "weight": {"amount": -10, "unit": "kg"}
                    }
                ]
            }
        ]
    }
    
    validator = create_validator(schema)
    with pytest.raises(jsonschema.ValidationError):
        validator.validate(invalid_data)


def test_set_centric_validates_repetitions_minimum() -> None:
    """Test that repetitions must be >= 0."""
    schema_path = Path("schema/set-centric.schema.json")
    
    with open(schema_path, 'r', encoding='utf-8') as f:
        schema = json.load(f)
    
    invalid_data = {
        "workout_id": "w_2026_01_23",
        "date": "2026-01-23T18:45:00Z",
        "exercises": [
            {
                "name": "Bench Press",
                "sets": [
                    {
                        "setNumber": 1,
                        "repetitions": -1,
                        "weight": {"amount": 60, "unit": "kg"}
                    }
                ]
            }
        ]
    }
    
    validator = create_validator(schema)
    with pytest.raises(jsonschema.ValidationError):
        validator.validate(invalid_data)


def test_set_centric_validates_set_number_minimum() -> None:
    """Test that setNumber must be >= 1."""
    schema_path = Path("schema/set-centric.schema.json")
    
    with open(schema_path, 'r', encoding='utf-8') as f:
        schema = json.load(f)
    
    invalid_data = {
        "workout_id": "w_2026_01_23",
        "date": "2026-01-23T18:45:00Z",
        "exercises": [
            {
                "name": "Bench Press",
                "sets": [
                    {
                        "setNumber": 0,
                        "repetitions": 8,
                        "weight": {"amount": 60, "unit": "kg"}
                    }
                ]
            }
        ]
    }
    
    validator = create_validator(schema)
    with pytest.raises(jsonschema.ValidationError):
        validator.validate(invalid_data)


def test_set_centric_validates_unit_enum() -> None:
    """Test that unit must be 'kg' or 'lb'."""
    schema_path = Path("schema/set-centric.schema.json")
    
    with open(schema_path, 'r', encoding='utf-8') as f:
        schema = json.load(f)
    
    invalid_data = {
        "workout_id": "w_2026_01_23",
        "date": "2026-01-23T18:45:00Z",
        "exercises": [
            {
                "name": "Bench Press",
                "sets": [
                    {
                        "setNumber": 1,
                        "repetitions": 8,
                        "weight": {"amount": 100, "unit": "pounds"}
                    }
                ]
            }
        ]
    }
    
    validator = create_validator(schema)
    with pytest.raises(jsonschema.ValidationError):
        validator.validate(invalid_data)


def test_set_centric_validates_equipment_enum() -> None:
    """Test that equipment must be valid enum value."""
    schema_path = Path("schema/set-centric.schema.json")
    
    with open(schema_path, 'r', encoding='utf-8') as f:
        schema = json.load(f)
    
    invalid_data = {
        "workout_id": "w_2026_01_23",
        "date": "2026-01-23T18:45:00Z",
        "exercises": [
            {
                "name": "Bench Press",
                "equipment": "invalid_equipment",
                "sets": [
                    {
                        "setNumber": 1,
                        "repetitions": 8,
                        "weight": {"amount": 100, "unit": "kg"}
                    }
                ]
            }
        ]
    }
    
    validator = create_validator(schema)
    with pytest.raises(jsonschema.ValidationError):
        validator.validate(invalid_data)


def test_set_centric_validates_rpe_range() -> None:
    """Test that RPE must be between 1 and 10."""
    schema_path = Path("schema/set-centric.schema.json")
    
    with open(schema_path, 'r', encoding='utf-8') as f:
        schema = json.load(f)
    
    invalid_data = {
        "workout_id": "w_2026_01_23",
        "date": "2026-01-23T18:45:00Z",
        "exercises": [
            {
                "name": "Bench Press",
                "sets": [
                    {
                        "setNumber": 1,
                        "repetitions": 8,
                        "weight": {"amount": 100, "unit": "kg"},
                        "rpe": 15
                    }
                ]
            }
        ]
    }
    
    validator = create_validator(schema)
    with pytest.raises(jsonschema.ValidationError):
        validator.validate(invalid_data)


def test_set_centric_requires_weight_object() -> None:
    """Test that weight must be an object with amount and unit."""
    schema_path = Path("schema/set-centric.schema.json")
    
    with open(schema_path, 'r', encoding='utf-8') as f:
        schema = json.load(f)
    
    invalid_data = {
        "workout_id": "w_2026_01_23",
        "date": "2026-01-23T18:45:00Z",
        "exercises": [
            {
                "name": "Bench Press",
                "sets": [
                    {
                        "setNumber": 1,
                        "repetitions": 8,
                        "weight": 60
                    }
                ]
            }
        ]
    }
    
    validator = create_validator(schema)
    with pytest.raises(jsonschema.ValidationError):
        validator.validate(invalid_data)
