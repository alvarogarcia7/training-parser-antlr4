"""Season detection for training logs.

A season is a continuous training period: consecutive sessions belong to the
same season as long as the break between them (days without any training
session) is shorter than the configured minimum break.

Example with ``min_break_days: 14``::

    2023-01-01, 2023-01-05, 2023-01-10   -> season 1
    (break of 30 days without training)
    2023-02-10, 2023-02-12               -> season 2

For every season, each exercise gets an estimated 1RM (Brzycki formula, best
set of the season) and every set is expressed as a percentage of that 1RM.
"""

import datetime
import json
import re
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Any, Iterable

import jsonschema
import yaml

from src.one_rep_max import BRZYCKI_MAX_REPS, brzycki_1rm, percentage_of_1rm

DEFAULT_CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "seasons.yaml"
SEASON_REPORT_SCHEMA_PATH = Path(__file__).resolve().parent.parent / "schema" / "season_report.schema.json"

_DATE_LINE = re.compile(r"^(\d{4}-\d{2}-\d{2})(?!\d)")


@dataclass(frozen=True)
class SeasonConfig:
    """Configuration for season detection."""

    min_break_days: int = 21
    min_sessions: int = 1
    max_reps_for_1rm: int = 10

    def __post_init__(self) -> None:
        """Validate configuration."""
        if self.min_break_days < 1:
            raise ValueError("min_break_days must be at least 1")
        if self.min_sessions < 1:
            raise ValueError("min_sessions must be at least 1")
        if not 1 <= self.max_reps_for_1rm <= BRZYCKI_MAX_REPS:
            raise ValueError(f"max_reps_for_1rm must be between 1 and {BRZYCKI_MAX_REPS}")

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SeasonConfig":
        """Build a configuration from a dictionary (e.g., parsed YAML)."""
        known = {"min_break_days", "min_sessions", "max_reps_for_1rm"}
        unknown = set(data) - known
        if unknown:
            raise ValueError(f"Unknown season config keys: {', '.join(sorted(unknown))}")
        values: dict[str, int] = {}
        for key in known & set(data):
            value = data[key]
            if isinstance(value, bool) or not isinstance(value, int):
                raise ValueError(f"{key} must be an integer, got {value!r}")
            values[key] = value
        return cls(**values)

    @classmethod
    def load(cls, path: Path) -> "SeasonConfig":
        """Load the configuration from a YAML file."""
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        if not isinstance(data, dict):
            raise ValueError(f"Season config must be a mapping: {path}")
        return cls.from_dict(data)


@dataclass(frozen=True)
class TrainingSet:
    """A single set performed in a session."""

    exercise: str
    repetitions: int
    weight: float
    unit: str


@dataclass(frozen=True)
class TrainingSession:
    """A training day and the sets performed on it."""

    date: datetime.date
    sets: tuple[TrainingSet, ...] = ()


@dataclass(frozen=True)
class SetIntensity:
    """A set expressed as a percentage of the season 1RM."""

    date: datetime.date
    repetitions: int
    weight: float
    percentage_1rm: float

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "date": self.date.isoformat(),
            "repetitions": self.repetitions,
            "weight": self.weight,
            "percentage_1rm": round(self.percentage_1rm, 1),
        }


@dataclass(frozen=True)
class ExerciseIntensity:
    """Estimated 1RM of an exercise in a season, and the intensity of each set."""

    exercise: str
    unit: str
    one_rep_max: float
    best_set: SetIntensity
    sets: tuple[SetIntensity, ...]

    @property
    def average_percentage_1rm(self) -> float:
        """Mean %1RM over all sets of the season."""
        return sum(s.percentage_1rm for s in self.sets) / len(self.sets)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "exercise": self.exercise,
            "unit": self.unit,
            "one_rep_max": round(self.one_rep_max, 1),
            "best_set": self.best_set.to_dict(),
            "average_percentage_1rm": round(self.average_percentage_1rm, 1),
            "sets": [s.to_dict() for s in self.sets],
        }


@dataclass(frozen=True)
class Season:
    """A continuous training period."""

    start: datetime.date
    end: datetime.date
    sessions: tuple[datetime.date, ...]
    break_before_days: int | None
    exercises: tuple[ExerciseIntensity, ...] = field(default=())

    @property
    def session_count(self) -> int:
        """Number of training days in the season."""
        return len(self.sessions)

    @property
    def duration_days(self) -> int:
        """Calendar days from the first to the last session, inclusive."""
        return (self.end - self.start).days + 1

    @property
    def longest_break_days(self) -> int:
        """Longest run of days without training inside the season."""
        return max(
            (rest_days(prev, nxt) for prev, nxt in zip(self.sessions, self.sessions[1:])),
            default=0,
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "start": self.start.isoformat(),
            "end": self.end.isoformat(),
            "sessions": self.session_count,
            "duration_days": self.duration_days,
            "longest_break_days": self.longest_break_days,
            "break_before_days": self.break_before_days,
            "exercises": [exercise.to_dict() for exercise in self.exercises],
        }


@dataclass(frozen=True)
class SeasonReport:
    """Result of season detection."""

    config: SeasonConfig
    seasons: tuple[Season, ...]
    ignored: tuple[Season, ...]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "config": {
                "min_break_days": self.config.min_break_days,
                "min_sessions": self.config.min_sessions,
                "max_reps_for_1rm": self.config.max_reps_for_1rm,
            },
            "seasons": [season.to_dict() for season in self.seasons],
            "ignored": [season.to_dict() for season in self.ignored],
        }


def validate_report_dict(data: dict[str, Any]) -> None:
    """Validate a season report dict against schema/season_report.schema.json.

    Raises jsonschema.exceptions.ValidationError if `data` does not match the
    schema, or jsonschema.exceptions.SchemaError if the schema itself is invalid.
    """
    schema = json.loads(SEASON_REPORT_SCHEMA_PATH.read_text(encoding="utf-8"))
    jsonschema.validate(data, schema)


def rest_days(previous: datetime.date, following: datetime.date) -> int:
    """Number of days without training strictly between two session dates."""
    return max((following - previous).days - 1, 0)


def detect_seasons(dates: Iterable[datetime.date], config: SeasonConfig) -> SeasonReport:
    """Split training session dates into seasons.

    Dates may be unsorted and contain duplicates (several sessions on one day
    count as one training day).
    """
    unique = sorted(set(dates))
    groups: list[tuple[list[datetime.date], int | None]] = []

    for date in unique:
        if groups:
            gap = rest_days(groups[-1][0][-1], date)
            if gap < config.min_break_days:
                groups[-1][0].append(date)
                continue
            groups.append(([date], gap))
        else:
            groups.append(([date], None))

    seasons: list[Season] = []
    ignored: list[Season] = []
    for sessions, break_before in groups:
        season = Season(
            start=sessions[0],
            end=sessions[-1],
            sessions=tuple(sessions),
            break_before_days=break_before,
        )
        if season.session_count >= config.min_sessions:
            seasons.append(season)
        else:
            ignored.append(season)

    return SeasonReport(config=config, seasons=tuple(seasons), ignored=tuple(ignored))


def exercise_intensities(
    sessions: Iterable[TrainingSession],
    start: datetime.date,
    end: datetime.date,
    max_reps_for_1rm: int = 10,
) -> tuple[ExerciseIntensity, ...]:
    """Compute the 1RM and per-set %1RM of every exercise trained between start and end.

    The 1RM is the highest Brzycki estimate among the sets of the period with
    at most `max_reps_for_1rm` repetitions (Brzycki overestimates for high
    repetitions). If an exercise has no such set, sets up to BRZYCKI_MAX_REPS
    are used instead. Every set is still reported as a %1RM. Exercises
    without any load (e.g., bodyweight at 0) are skipped.
    """
    by_exercise: dict[tuple[str, str], list[tuple[datetime.date, TrainingSet]]] = {}
    for session in sorted(sessions, key=lambda s: s.date):
        if not start <= session.date <= end:
            continue
        for training_set in session.sets:
            key = (training_set.exercise, training_set.unit)
            by_exercise.setdefault(key, []).append((session.date, training_set))

    result = []
    for (exercise, unit), performed in sorted(by_exercise.items()):
        estimates = [
            (brzycki_1rm(ts.weight, ts.repetitions), date, ts)
            for date, ts in performed
            if ts.repetitions <= max_reps_for_1rm
        ] or [
            (brzycki_1rm(ts.weight, ts.repetitions), date, ts)
            for date, ts in performed
            if ts.repetitions <= BRZYCKI_MAX_REPS
        ]
        if not estimates:
            continue
        one_rep_max, best_date, best = max(estimates, key=lambda e: e[0])
        if one_rep_max <= 0:
            continue
        sets = tuple(
            SetIntensity(date, ts.repetitions, ts.weight, percentage_of_1rm(ts.weight, one_rep_max))
            for date, ts in performed
        )
        best_set = SetIntensity(
            best_date, best.repetitions, best.weight, percentage_of_1rm(best.weight, one_rep_max)
        )
        result.append(ExerciseIntensity(exercise, unit, one_rep_max, best_set, sets))
    return tuple(result)


def analyse_seasons(sessions: Iterable[TrainingSession], config: SeasonConfig) -> SeasonReport:
    """Detect seasons and compute the per-exercise %1RM within each season."""
    sessions = list(sessions)
    report = detect_seasons((s.date for s in sessions), config)

    def with_exercises(season: Season) -> Season:
        return replace(season, exercises=exercise_intensities(
            sessions, season.start, season.end, config.max_reps_for_1rm))

    return replace(
        report,
        seasons=tuple(with_exercises(s) for s in report.seasons),
        ignored=tuple(with_exercises(s) for s in report.ignored),
    )


def parse_date(value: str) -> datetime.date:
    """Parse a date from an ISO date or datetime string (e.g., '2023-05-04T18:00:00Z')."""
    match = _DATE_LINE.match(value.strip())
    if not match:
        raise ValueError(f"Not a date: {value!r}")
    return datetime.date.fromisoformat(match.group(1))


def session_from_set_centric(data: Any, source: str = "<json>") -> TrainingSession:
    """Build a session from a set-centric workout, bare or wrapped in an envelope.

    Envelope: ``{"type": "set-centric.v1", "payload": {...}}``.
    Workout: ``{"type": "set-centric", "date": ..., "exercises": [{"name", "sets": [...]}]}``.
    """
    if not isinstance(data, dict):
        raise ValueError(f"{source}: expected a set-centric JSON object")
    envelope_type = data.get("type")
    if "payload" in data:
        if not (isinstance(envelope_type, str) and envelope_type.startswith("set-centric")):
            raise ValueError(f"{source}: not a set-centric envelope (type={envelope_type!r})")
        data = data["payload"]
        if not isinstance(data, dict):
            raise ValueError(f"{source}: payload must be a JSON object")
    if data.get("type", "set-centric") != "set-centric":
        raise ValueError(f"{source}: not a set-centric workout (type={data.get('type')!r})")
    if not isinstance(data.get("date"), str):
        raise ValueError(f"{source}: missing workout 'date'")

    try:
        sets = tuple(
            TrainingSet(
                str(exercise["name"]),
                int(s["repetitions"]),
                float(s["weight"]["amount"]),
                str(s["weight"]["unit"]),
            )
            for exercise in data.get("exercises", [])
            for s in exercise["sets"]
        )
    except (KeyError, TypeError) as e:
        raise ValueError(f"{source}: malformed exercise or set ({e})") from e
    return TrainingSession(parse_date(data["date"]), sets)


def sessions_from_directory(directory: Path) -> list[TrainingSession]:
    """Read every set-centric JSON file (``*.json``) in a directory and its subdirectories.

    Each file holds one set-centric workout, or a JSON array of them.
    """
    if not directory.is_dir():
        raise NotADirectoryError(f"Input is not a directory: {directory}")
    files = sorted(directory.rglob("*.json"))
    if not files:
        raise ValueError(f"No JSON files found in {directory}")

    sessions: list[TrainingSession] = []
    for path in files:
        data = json.loads(path.read_text(encoding="utf-8"))
        workouts = data if isinstance(data, list) else [data]
        sessions.extend(session_from_set_centric(workout, str(path)) for workout in workouts)
    return sessions


def format_report(report: SeasonReport) -> str:
    """Format a season report for console output."""
    output = [
        "=" * 70,
        "TRAINING SEASONS",
        f"(min break: {report.config.min_break_days} days,"
        f" min sessions: {report.config.min_sessions},"
        f" 1RM from sets <= {report.config.max_reps_for_1rm} reps)",
        "=" * 70,
    ]
    if not report.seasons:
        output.append("No seasons detected.")
    for index, season in enumerate(report.seasons, start=1):
        if season.break_before_days is not None:
            output.append(f"  ... {season.break_before_days} days without training ...")
        output.append(
            f"Season {index}: {season.start} -> {season.end}"
            f"  sessions={season.session_count}"
            f"  duration={season.duration_days}d"
            f"  longest_break={season.longest_break_days}d"
        )
        output.extend(_format_exercises(season))
    if report.ignored:
        output.append("-" * 70)
        output.append(f"Ignored (fewer than {report.config.min_sessions} sessions):")
        for season in report.ignored:
            output.append(f"  {season.start} -> {season.end}  sessions={season.session_count}")
    return "\n".join(output)


def _format_exercises(season: Season) -> list[str]:
    """Format the %1RM of each exercise of a season, grouping equal consecutive sets."""
    lines = []
    for exercise in season.exercises:
        best = exercise.best_set
        lines.append(
            f"    {exercise.exercise}: 1RM={exercise.one_rep_max:.1f}{exercise.unit}"
            f" (Brzycki, {best.weight:g}{exercise.unit} x {best.repetitions} on {best.date})"
            f"  avg={exercise.average_percentage_1rm:.1f}%"
        )
        groups: list[list[SetIntensity]] = []
        for s in exercise.sets:
            last = groups[-1][0] if groups else None
            if last and (last.date, last.repetitions, last.weight) == (s.date, s.repetitions, s.weight):
                groups[-1].append(s)
            else:
                groups.append([s])
        by_date: dict[datetime.date, list[str]] = {}
        for group in groups:
            s = group[0]
            by_date.setdefault(s.date, []).append(
                f"{len(group)}x{s.repetitions}x{s.weight:g}{exercise.unit} {s.percentage_1rm:.0f}%"
            )
        for date, entries in by_date.items():
            lines.append(f"      {date}: {', '.join(entries)}")
    return lines
