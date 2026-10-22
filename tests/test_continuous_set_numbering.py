"""Tests for CR2: sets are not shared between exercises by default.

Set numbers run continuously across the whole workout, so each exercise owns a
distinct contiguous range of set numbers:

    Smith Machine Squat -> series 1, 2, 3
    Squat               -> series 4, 5, 6

Reusing the same set numbers across exercises is reserved for superseries
(no rest between exercises) and must be specified explicitly; it must not fall
out of per-exercise numbering that happens to restart at 1.
"""

from datetime import datetime, timezone
from typing import Any

from src.data_access import DataParser
from src.parser.model import Exercise, Set_, Weight
from src.parser.serializer import serialize_to_set_centric

TIMESTAMP = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)


def _set_numbers(result: dict[str, Any], exercise_index: int) -> list[int]:
    return [s["setNumber"] for s in result["exercises"][exercise_index]["sets"]]


class TestContinuousSetNumbering:
    def test_example_smith_machine_squat_then_squat(self) -> None:
        exercises = DataParser.parse_raw_text(
            "Smith Machine Squat: 3x5x100\nSquat: 3x5x80\n"
        )
        result = serialize_to_set_centric(exercises, TIMESTAMP)

        assert result["exercises"][0]["name"] == "Smith Machine Squat"
        assert _set_numbers(result, 0) == [1, 2, 3]
        assert result["exercises"][1]["name"] == "Squat"
        assert _set_numbers(result, 1) == [4, 5, 6]

    def test_numbering_is_continuous_not_reset(self) -> None:
        exercises = [
            Exercise("A", [Set_(10, Weight(50, "kg")), Set_(10, Weight(50, "kg"))]),
            Exercise("B", [Set_(5, Weight(80, "kg"))]),
            Exercise("C", [Set_(8, Weight(60, "kg")), Set_(8, Weight(60, "kg"))]),
        ]
        result = serialize_to_set_centric(exercises, TIMESTAMP)

        assert _set_numbers(result, 0) == [1, 2]
        assert _set_numbers(result, 1) == [3]
        assert _set_numbers(result, 2) == [4, 5]

    def test_set_numbers_are_globally_unique(self) -> None:
        exercises = [
            Exercise("A", [Set_(10, Weight(50, "kg")) for _ in range(3)]),
            Exercise("B", [Set_(5, Weight(80, "kg")) for _ in range(4)]),
        ]
        result = serialize_to_set_centric(exercises, TIMESTAMP)

        all_numbers = [
            s["setNumber"]
            for block in result["exercises"]
            for s in block["sets"]
        ]
        assert all_numbers == list(range(1, len(all_numbers) + 1))
        assert len(set(all_numbers)) == len(all_numbers)

    def test_single_exercise_still_starts_at_one(self) -> None:
        exercises = [Exercise("Solo", [Set_(10, Weight(50, "kg")), Set_(9, Weight(55, "kg"))])]
        result = serialize_to_set_centric(exercises, TIMESTAMP)
        assert _set_numbers(result, 0) == [1, 2]
