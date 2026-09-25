"""Statistics calculator for training workout data.

Computes:
- Total exercises, sets, weight
- Rates: exercises/time, sets/time, weight/time
- Time-based metrics per hour and per minute
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from parser.model import Exercise


@dataclass
class WorkoutStats:
    """Statistics for a workout or collection of workouts."""

    total_exercises: int
    total_sets: int
    total_weight: float
    time_minutes: float

    def __post_init__(self) -> None:
        """Validate statistics."""
        if self.time_minutes < 0:
            raise ValueError("time_minutes must be non-negative")

    @property
    def exercises_per_hour(self) -> float:
        """Exercises per hour."""
        if self.time_minutes == 0:
            return 0.0
        return (self.total_exercises / self.time_minutes) * 60

    @property
    def exercises_per_minute(self) -> float:
        """Exercises per minute."""
        if self.time_minutes == 0:
            return 0.0
        return self.total_exercises / self.time_minutes

    @property
    def sets_per_hour(self) -> float:
        """Sets per hour."""
        if self.time_minutes == 0:
            return 0.0
        return (self.total_sets / self.time_minutes) * 60

    @property
    def sets_per_minute(self) -> float:
        """Sets per minute."""
        if self.time_minutes == 0:
            return 0.0
        return self.total_sets / self.time_minutes

    @property
    def weight_per_hour(self) -> float:
        """Total weight per hour (kg)."""
        if self.time_minutes == 0:
            return 0.0
        return (self.total_weight / self.time_minutes) * 60

    @property
    def weight_per_minute(self) -> float:
        """Total weight per minute (kg)."""
        if self.time_minutes == 0:
            return 0.0
        return self.total_weight / self.time_minutes

    @property
    def avg_weight_per_set(self) -> float:
        """Average weight per set (kg)."""
        if self.total_sets == 0:
            return 0.0
        return self.total_weight / self.total_sets

    @property
    def avg_sets_per_exercise(self) -> float:
        """Average sets per exercise."""
        if self.total_exercises == 0:
            return 0.0
        return self.total_sets / self.total_exercises

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "totals": {
                "exercises": self.total_exercises,
                "sets": self.total_sets,
                "weight_kg": round(self.total_weight, 2),
            },
            "rates": {
                "exercises_per_hour": round(self.exercises_per_hour, 2),
                "exercises_per_minute": round(self.exercises_per_minute, 4),
                "sets_per_hour": round(self.sets_per_hour, 2),
                "sets_per_minute": round(self.sets_per_minute, 4),
                "weight_per_hour_kg": round(self.weight_per_hour, 2),
                "weight_per_minute_kg": round(self.weight_per_minute, 4),
            },
            "averages": {
                "weight_per_set_kg": round(self.avg_weight_per_set, 2),
                "sets_per_exercise": round(self.avg_sets_per_exercise, 2),
            },
            "time": {
                "total_minutes": round(self.time_minutes, 2),
                "total_hours": round(self.time_minutes / 60, 2),
            },
        }


class StatisticsCalculator:
    """Calculate statistics from exercises."""

    @staticmethod
    def from_exercises(
        exercises: list[Exercise],
        time_minutes: float = 0.0,
    ) -> WorkoutStats:
        """Calculate statistics from list of Exercise objects.

        Args:
            exercises: List of Exercise objects
            time_minutes: Duration of workout in minutes (0 if unknown)

        Returns:
            WorkoutStats object with calculated statistics
        """
        total_exercises = len(exercises)
        total_sets = sum(len(ex.sets_) for ex in exercises)
        total_weight = sum(
            set_.weight.amount * set_.repetitions
            for ex in exercises
            for set_ in ex.sets_
        )

        return WorkoutStats(
            total_exercises=total_exercises,
            total_sets=total_sets,
            total_weight=total_weight,
            time_minutes=time_minutes,
        )

    @staticmethod
    def from_json_workouts(
        workouts: list[dict[str, Any]],
        time_minutes: float = 0.0,
    ) -> WorkoutStats:
        """Calculate statistics from JSON workout data.

        Args:
            workouts: List of workout dictionaries (from database.json)
            time_minutes: Duration of all workouts in minutes

        Returns:
            WorkoutStats object with calculated statistics
        """
        total_exercises = 0
        total_sets = 0
        total_weight = 0.0

        for workout in workouts:
            exercises = workout.get("exercises", [])
            total_exercises += len(exercises)

            for exercise in exercises:
                sets = exercise.get("sets", [])
                total_sets += len(sets)

                for set_data in sets:
                    weight = set_data.get("weight", {})
                    reps = set_data.get("repetitions", 0)
                    amount = weight.get("amount", 0.0)
                    total_weight += amount * reps

        return WorkoutStats(
            total_exercises=total_exercises,
            total_sets=total_sets,
            total_weight=total_weight,
            time_minutes=time_minutes,
        )

    @staticmethod
    def format_stats(stats: WorkoutStats) -> str:
        """Format statistics for console output.

        Args:
            stats: WorkoutStats object

        Returns:
            Formatted string representation
        """
        output = []
        output.append("\n" + "=" * 70)
        output.append("WORKOUT STATISTICS")
        output.append("=" * 70)

        output.append("\n📊 TOTALS")
        output.append("-" * 70)
        output.append(f"  Total Exercises: {stats.total_exercises}")
        output.append(f"  Total Sets:      {stats.total_sets}")
        output.append(f"  Total Weight:    {stats.total_weight:.2f} kg")

        output.append("\n⏱️  TIME")
        output.append("-" * 70)
        output.append(f"  Duration:        {stats.time_minutes:.2f} minutes")
        output.append(f"                   {stats.time_minutes / 60:.2f} hours")

        output.append("\n📈 RATES (per minute / per hour)")
        output.append("-" * 70)
        output.append(
            f"  Exercises:       {stats.exercises_per_minute:.4f} / {stats.exercises_per_hour:.2f}"
        )
        output.append(
            f"  Sets:            {stats.sets_per_minute:.4f} / {stats.sets_per_hour:.2f}"
        )
        output.append(
            f"  Weight (kg):     {stats.weight_per_minute:.4f} / {stats.weight_per_hour:.2f}"
        )

        output.append("\n📉 AVERAGES")
        output.append("-" * 70)
        output.append(f"  Weight per Set:       {stats.avg_weight_per_set:.2f} kg")
        output.append(f"  Sets per Exercise:    {stats.avg_sets_per_exercise:.2f}")

        output.append("\n" + "=" * 70 + "\n")

        return "\n".join(output)
