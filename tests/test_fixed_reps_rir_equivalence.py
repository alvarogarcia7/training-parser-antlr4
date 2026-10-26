"""Tests for CR1: per-weight RIR in fixed-reps multi-weight (v1) notation.

The shorthand form, where bare weights share the leading fixed rep count, must
be equivalent to the explicit form that restates the rep count on every weight:

    D: 10..50-4,65-4,65-4,65-3        (shorthand, bare weights)
    D: 10..50-4,10.65-4,10.65-4,10.65-3   (explicit reps.weight restatement)

Both describe 10 reps @ 50kg then 10 reps @ 65kg x3, i.e.
10 * (50 + 65 * 3) = 2450 kg, with per-weight RIR 4, 4, 4, 3.
"""

from src.data_access import DataParser
from src.parser.model import Set_, Weight, Units


def _sets(text: str) -> list[Set_]:
    exercises = DataParser.parse_raw_text(text + "\n")
    assert len(exercises) == 1, f"expected one exercise, got {exercises}"
    return exercises[0].sets_


class TestFixedRepsPerWeightRir:
    SHORTHAND = "D: 10..50-4,65-4,65-4,65-3"
    EXPLICIT = "D: 10..50-4,10.65-4,10.65-4,10.65-3"

    def _expected(self) -> list[Set_]:
        kg = Units.KILOGRAM
        return [
            Set_(10, Weight(50, kg), rir=4),
            Set_(10, Weight(65, kg), rir=4),
            Set_(10, Weight(65, kg), rir=4),
            Set_(10, Weight(65, kg), rir=3),
        ]

    def test_shorthand_volume_is_2450(self) -> None:
        exercises = DataParser.parse_raw_text(self.SHORTHAND + "\n")
        assert exercises[0].total_volume() == 2450

    def test_explicit_volume_is_2450(self) -> None:
        exercises = DataParser.parse_raw_text(self.EXPLICIT + "\n")
        assert exercises[0].total_volume() == 2450

    def test_shorthand_and_explicit_are_equivalent(self) -> None:
        assert _sets(self.SHORTHAND) == _sets(self.EXPLICIT)

    def test_shorthand_sets_match_expected(self) -> None:
        assert _sets(self.SHORTHAND) == self._expected()

    def test_per_weight_rir_is_preserved(self) -> None:
        rirs = [s.rir for s in _sets(self.SHORTHAND)]
        assert rirs == [4, 4, 4, 3]

    def test_lone_trailing_rir_applies_to_all_weights(self) -> None:
        # A single RIR on the final weight is a set-wide trailing RIR.
        sets_ = _sets("D: 5xx80,90,100-3")
        assert [s.rir for s in sets_] == [3, 3, 3]
        assert [s.weight.amount for s in sets_] == [80, 90, 100]
        assert all(s.repetitions == 5 for s in sets_)

    def test_dotted_decimal_weight_still_parses_as_weight(self) -> None:
        # Regression: a dotted number whose leading int does NOT restate the
        # fixed rep count remains a decimal weight (8 reps @ 60.5kg, not 60@5).
        sets_ = _sets("Squat: 8xx60.5,70.5,80.5")
        assert [s.weight.amount for s in sets_] == [60.5, 70.5, 80.5]
        assert all(s.repetitions == 8 for s in sets_)
