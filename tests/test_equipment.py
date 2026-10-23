"""Tests for CR3: equipment classification from a configuration file.

An exercise name that includes an equipment keyword implies that equipment
("Smith Machine ..." -> smith machine, "Dumbbell ..." -> dumbbell, "Barbell ..." ->
barbell). Exercises with no keyword match that are known barbell lifts (squat,
bench press, deadlift, overhead press) default to barbell. Everything else is
"other".
"""

from datetime import datetime, timezone
from pathlib import Path

import pytest

from src.parser.equipment import (
    DEFAULT_CONFIG_PATH,
    VALID_EQUIPMENT,
    EquipmentClassifier,
    classify_equipment,
)
from src.parser.model import Exercise, Set_, Weight
from src.parser.serializer import serialize_to_set_centric, serialize_to_bench_centric

TIMESTAMP = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)


class TestEquipmentClassifier:
    def test_classify(self) -> None:
        cases = [
            ("Smith Machine Squat", "smith machine"),
            ("smith machine bench press", "smith machine"),
            ("Machine Row", "machine"),
            ("Dumbbell Curl", "dumbbell"),
            ("Barbell Row", "barbell"),
            ("Cable Fly", "cable"),
            ("Kettlebell Swing", "kettlebell"),
            # barbell defaults (no keyword in the name)
            ("Squat", "barbell"),
            ("squat", "barbell"),
            ("Bench Press", "barbell"),
            ("Deadlift", "barbell"),
            ("Overhead Press", "barbell"),
            # unknown -> other
            ("Plank", "other"),
            ("Pull-up", "other"),
        ]
        for name, expected in cases:
            assert classify_equipment(name) == expected, name

    def test_keyword_beats_barbell_default(self) -> None:
        # "squat" is a barbell default, but "smith machine" keyword wins.
        assert classify_equipment("Smith Machine Squat") == "smith machine"

    def test_result_is_always_a_valid_enum_value(self) -> None:
        for name in ["Smith Machine Squat", "Squat", "Dumbbell Curl", "Plank"]:
            assert classify_equipment(name) in VALID_EQUIPMENT

    def test_repository_config_exists_and_loads(self) -> None:
        assert DEFAULT_CONFIG_PATH.exists()
        classifier = EquipmentClassifier()
        assert classifier.classify("Squat") == "barbell"

    def test_missing_config_falls_back_to_other(self, tmp_path: Path) -> None:
        classifier = EquipmentClassifier(tmp_path / "does-not-exist.yaml")
        assert classifier.classify("Smith Machine Squat") == "other"
        assert classifier.classify("Squat") == "other"

    def test_rejects_unknown_equipment_type(self, tmp_path: Path) -> None:
        bad = tmp_path / "equipment.yaml"
        bad.write_text("equipment:\n  - type: spaceship\n    keywords: [laser]\n")
        with pytest.raises(ValueError):
            EquipmentClassifier(bad)


class TestEquipmentInSerialization:
    def test_set_centric_populates_equipment(self) -> None:
        exercises = [
            Exercise("Smith Machine Squat", [Set_(5, Weight(100, "kg"))]),
            Exercise("Squat", [Set_(5, Weight(80, "kg"))]),
            Exercise("Dumbbell Curl", [Set_(12, Weight(12.5, "kg"))]),
            Exercise("Plank", [Set_(1, Weight(0, "kg"))]),
        ]
        result = serialize_to_set_centric(exercises, TIMESTAMP)
        equipments = [e["equipment"] for e in result["exercises"]]
        assert equipments == ["smith machine", "barbell", "dumbbell", "other"]

    def test_bench_centric_populates_equipment(self) -> None:
        exercises = [Exercise("Bench Press", [Set_(5, Weight(80, "kg"))])]
        result = serialize_to_bench_centric(exercises, TIMESTAMP)
        assert result["exercises"][0]["equipment"] == "barbell"
