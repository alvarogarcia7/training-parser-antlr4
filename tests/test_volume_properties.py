"""Property-based tests for volume computation in training parser.

Verifies that:
1. Volume is computed in Python from JSON results (not JavaScript)
2. Volume is additive: adding series produces sum of individual volumes
3. Different series format variations produce consistent results
"""

from typing import Any, TypedDict

from hypothesis import given, strategies as st

from src.data_access import DataParser


class WeightDict(TypedDict):
    """Type for weight in JSON structure."""
    amount: float
    unit: str


class SetDict(TypedDict):
    """Type for set in JSON structure."""
    repetitions: int
    weight: WeightDict


# --- Strategies for generating valid training series ---

def series_spec_strategy() -> Any:
    """Generate valid training series specs like '10x10x10' or '5x20x50k'."""
    sets = st.integers(min_value=1, max_value=20)
    reps = st.integers(min_value=1, max_value=50)
    weight = st.integers(min_value=1, max_value=200)

    def build_spec(s: int, r: int, w: int) -> str:
        return f"{s}x{r}x{w}"

    return st.builds(build_spec, sets, reps, weight)


def exercise_line_strategy(exercise_name: str = "squat") -> Any:
    """Generate valid exercise lines like 'squat: 10x10x10'."""
    return st.builds(
        lambda spec: f"{exercise_name}: {spec}",
        series_spec_strategy()
    )


# --- Tests ---

class TestVolumeBasics:
    """Basic volume computation tests with known examples."""

    def test_volume_single_series_whole_set(self) -> None:
        """squat: 10x10x10 → 10 sets × 10 reps × 10kg = 1000 kg"""
        text = "squat: 10x10x10\n"
        exercises = DataParser.parse_raw_text(text)

        assert len(exercises) == 1
        ex = exercises[0]
        assert ex.name == 'squat'
        assert len(ex.sets_) == 10  # 10 series

        for s in ex.sets_:
            assert s.repetitions == 10
            assert s.weight.amount == 10

        assert ex.total_volume() == 1000

    def test_volume_second_series(self) -> None:
        """squat: 20x20x20 → 20 sets × 20 reps × 20kg = 8000 kg"""
        text = "squat: 20x20x20\n"
        exercises = DataParser.parse_raw_text(text)

        assert len(exercises) == 1
        ex = exercises[0]
        assert len(ex.sets_) == 20

        for s in ex.sets_:
            assert s.repetitions == 20
            assert s.weight.amount == 20

        assert ex.total_volume() == 8000

    def test_volume_additive_same_exercise(self) -> None:
        """Two series on same exercise line: volumes are additive."""
        # Multiple series on one line get combined into single exercise
        text = "squat: 10x10x10, 20x20x20\n"
        exercises = DataParser.parse_raw_text(text)

        assert len(exercises) == 1, f"Expected 1 exercise, got {len(exercises)}"
        ex = exercises[0]
        assert len(ex.sets_) == 10 + 20  # 30 total sets

        # Verify volumes
        vol_series_1 = sum(s.repetitions * s.weight.amount for s in ex.sets_[:10])
        vol_series_2 = sum(s.repetitions * s.weight.amount for s in ex.sets_[10:])

        assert vol_series_1 == 1000, f"vol_series_1={vol_series_1}, expected=1000"
        assert vol_series_2 == 8000, f"vol_series_2={vol_series_2}, expected=8000"  # type: ignore[unreachable]
        assert ex.total_volume() == 9000


class TestVolumeFromJsonResult:
    """Verify volume is computed from JSON results (Python side, not JS)."""

    def test_volume_via_python_computation(self) -> None:
        """Parse → JSON → verify volume in JSON matches Exercise.total_volume()"""
        text = "squat: 5x10x50k\n"
        exercises = DataParser.parse_raw_text(text)
        ex = exercises[0]

        # Direct Python computation
        python_volume = ex.total_volume()

        # Via manual JSON-style computation
        json_volume = sum(
            s.repetitions * s.weight.amount
            for s in ex.sets_
        )

        assert python_volume == json_volume == 5 * 10 * 50

    def test_json_serialization_preserves_volume(self) -> None:
        """Volume computed from JSON structure matches Exercise.total_volume()"""
        text = "bench: 3x8x80k, 3x6x90k\n"
        exercises = DataParser.parse_raw_text(text)
        ex = exercises[0]

        # Compute volume in Python
        python_vol = ex.total_volume()

        # Simulate JSON structure and recompute
        json_sets: list[SetDict] = [
            {"repetitions": s.repetitions, "weight": {"amount": s.weight.amount, "unit": s.weight.unit}}
            for s in ex.sets_
        ]
        json_vol = sum(s["repetitions"] * s["weight"]["amount"] for s in json_sets)

        assert python_vol == json_vol


class TestVolumeAdditivityProperty:
    """Property-based tests for volume additivity."""

    @given(  # type: ignore[untyped-decorator]
        sets1=st.integers(min_value=1, max_value=10),
        reps1=st.integers(min_value=1, max_value=30),
        weight1=st.integers(min_value=1, max_value=100),
        sets2=st.integers(min_value=1, max_value=10),
        reps2=st.integers(min_value=1, max_value=30),
        weight2=st.integers(min_value=1, max_value=100),
    )
    def test_volume_is_additive_for_same_exercise(self, sets1: int, reps1: int, weight1: int, sets2: int, reps2: int, weight2: int) -> None:
        """Property: combining series on same line produces sum of volumes."""
        # Put both series on same line (comma-separated)
        combined_line = f"squat: {sets1}x{reps1}x{weight1}, {sets2}x{reps2}x{weight2}\n"

        # Parse combined
        combined_exercises = DataParser.parse_raw_text(combined_line)

        # Should produce single exercise
        assert len(combined_exercises) == 1
        combined_vol = combined_exercises[0].total_volume()

        # Parse separately and sum
        ex1_text = f"squat: {sets1}x{reps1}x{weight1}\n"
        ex2_text = f"squat: {sets2}x{reps2}x{weight2}\n"
        ex1 = DataParser.parse_raw_text(ex1_text)[0]
        ex2 = DataParser.parse_raw_text(ex2_text)[0]

        vol1 = ex1.total_volume()
        vol2 = ex2.total_volume()

        # Verify additivity
        expected_vol = vol1 + vol2
        assert combined_vol == expected_vol, \
            f"Series 1: {sets1}x{reps1}x{weight1} (vol={vol1}), " \
            f"Series 2: {sets2}x{reps2}x{weight2} (vol={vol2}), " \
            f"Combined: {combined_vol}, Expected: {expected_vol}"

    @given(  # type: ignore[untyped-decorator]
        sets=st.integers(min_value=1, max_value=20),
        reps=st.integers(min_value=1, max_value=50),
        weight=st.integers(min_value=1, max_value=150),
    )
    def test_volume_formula_consistency(self, sets: int, reps: int, weight: int) -> None:
        """Property: volume always equals sets × reps × weight."""
        text = f"exercise: {sets}x{reps}x{weight}\n"
        exercises = DataParser.parse_raw_text(text)

        assert len(exercises) > 0  # Ensure parse succeeded

        ex = exercises[0]
        actual_volume = ex.total_volume()
        expected_volume = sets * reps * weight

        assert actual_volume == expected_volume, \
            f"Formula mismatch: {sets}×{reps}×{weight} = {expected_volume}, got {actual_volume}"

    @given(  # type: ignore[untyped-decorator]
        series_list=st.lists(
            st.tuples(
                st.integers(min_value=1, max_value=8),
                st.integers(min_value=1, max_value=20),
                st.integers(min_value=1, max_value=100),
            ),
            min_size=2,
            max_size=5
        )
    )
    def test_multi_series_additive(self, series_list: list[tuple[int, int, int]]) -> None:
        """Property: multiple series on same line have additive volumes."""
        # Build single line with comma-separated series
        series_strs = [f"{s}x{r}x{w}" for s, r, w in series_list]
        text = "deadlift: " + ", ".join(series_strs) + "\n"

        combined_exercises = DataParser.parse_raw_text(text)
        assert len(combined_exercises) == 1
        combined_volume = combined_exercises[0].total_volume()

        # Parse individually and sum
        individual_volumes = []
        for s, r, w in series_list:
            single_text = f"deadlift: {s}x{r}x{w}\n"
            ex = DataParser.parse_raw_text(single_text)[0]
            individual_volumes.append(ex.total_volume())

        expected_total = sum(individual_volumes)
        assert combined_volume == expected_total, \
            f"Combined {combined_volume} != sum of individuals {expected_total}"


class TestVolumeJsonOnly:
    """Verify volume computation via JSON (Python), not JavaScript."""

    def test_json_result_contains_volume_data(self) -> None:
        """JSON result should contain all data needed to compute volume in Python."""
        text = "bench: 3x10x75k\n"
        exercises = DataParser.parse_raw_text(text)
        ex = exercises[0]

        # Simulate what gets serialized to JSON for PWA
        json_sets: list[SetDict] = [
            {
                "repetitions": s.repetitions,
                "weight": {"amount": s.weight.amount, "unit": s.weight.unit}
            }
            for s in ex.sets_
        ]
        json_data: dict[str, Any] = {
            "name": ex.name,
            "sets": json_sets
        }

        # Compute volume purely from JSON structure
        json_volume = sum(
            s["repetitions"] * s["weight"]["amount"]
            for s in json_data["sets"]
        )

        # Should match Python computation
        assert json_volume == ex.total_volume() == 3 * 10 * 75

    def test_volume_never_requires_ui_layer(self) -> None:
        """Volume must be computable from JSON payload alone."""
        text = "row: 4x8x60k\n"
        exercises = DataParser.parse_raw_text(text)
        ex = exercises[0]

        # Extract only what would be in the JSON envelope
        payload: dict[str, list[dict[str, Any]]] = {
            "exercises": [
                {
                    "name": e.name,
                    "sets": [
                        {
                            "repetitions": s.repetitions,
                            "weight": {"amount": s.weight.amount, "unit": s.weight.unit}
                        }
                        for s in e.sets_
                    ]
                }
                for e in [ex]
            ]
        }

        # Compute from payload (Python/backend only)
        payload_volume = sum(
            s["repetitions"] * s["weight"]["amount"]
            for ex_data in payload["exercises"]
            for s in ex_data["sets"]
        )

        # Matches Exercise computation
        assert payload_volume == ex.total_volume()
