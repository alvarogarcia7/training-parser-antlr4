"""Parse per-session health statistics from ``# stats:`` metadata lines.

Training files may carry device-reported session metadata on comment lines, e.g.::

    # stats: (apple watch) 500 total kcal, 402 active kcal, 50 min, 111 average bpm, 71-162 range bpm
    # stats: (polar) 355 kcal, 50 min, 108-140 bpm, 54% from fat
    # Stats 43 min, 37 zone min, 120-153 bpm, 382 kcal
    # Stats: 59m, 22 zm, 104-146 bpm, 360kcal

A single training session may carry several ``# stats:`` lines (one per device).
A line may name its source in parentheses and lists comma-separated fields. Parsing
is deliberately tolerant: whatever fields are recognised are extracted and the rest
are left unset, so partial, human-typed input still yields as much as possible.

The notation varies a lot across devices and languages, so the parser accepts:

- An optional colon (``# stats:`` or ``# Stats``) and an optional ``#``.
- Minutes written as ``50 min``, ``50m`` or ``10 minutos``.
- Zone minutes as ``37 zone min``, ``zone minutes``, ``min zone``, ``22 zm`` or
  ``66zm``.
- ``kcal`` with or without a space (``360kcal``), optionally ``total``/``active``.
- ``cardio load N``.
- Fat percentage only when the field actually mentions fat (``60% fat``), so a
  ``56% actividad`` is not mistaken for it.

Heart-rate conventions:

- A labelled ``range`` (Apple Watch's ``71-162 range bpm``) is min-max: ``min_bpm``
  71, ``max_bpm`` 162. This is kept distinct from the separately reported
  ``111 average bpm`` so neither value is lost.
- A bare dash range (Polar's ``108-140 bpm``) is average-max: ``avg_bpm`` 108,
  ``max_bpm`` 140.
- A single value (``111 average bpm`` or a bare ``x bpm``) is the average.
- Heart rate has an absolute ceiling of 220 bpm; values above it are discarded
  (they are usually typos, e.g. a kcal figure written as ``746 bpm``). An out-of-
  range reading never overwrites a value already parsed on the same line.

The first recognised value for a metric wins, so a later stray number cannot clobber
an earlier, more specific one.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Iterable

# Heart rate cannot plausibly exceed this; higher readings are treated as noise.
MAX_BPM = 220

_INT = re.compile(r"\d+")
_RANGE = re.compile(r"(\d+)\s*-\s*(\d+)")
# Minutes: "50 min", "50m", "10 minutos" (but not "360kcal").
_MINUTES = re.compile(r"(\d+)\s*(?:minutos?|min|m)\b", re.IGNORECASE)
# Zone minutes written attached to the number: "22zm", "66zm".
_ZM = re.compile(r"(\d+)\s*zm\b", re.IGNORECASE)
# A ``# stats`` line: optional leading '#', then 'stats' with an optional colon.
_STATS_PREFIX = re.compile(r"^\s*#?\s*stats\b\s*:?\s*(.*)$", re.IGNORECASE)
# Leading "(source)" tag, e.g. "(apple watch)".
_SOURCE = re.compile(r"^\(([^)]*)\)\s*(.*)$")


@dataclass
class SessionStat:
    """Device-reported statistics for one training session.

    Every metric is optional: unset fields stay ``None`` so that incomplete,
    human-typed input is preserved rather than rejected.
    """

    source: str | None = None
    total_kcal: int | None = None
    active_kcal: int | None = None
    duration_min: int | None = None
    avg_bpm: int | None = None
    min_bpm: int | None = None
    max_bpm: int | None = None
    zone_minutes: int | None = None
    fat_percent: int | None = None
    cardio_load: int | None = None
    raw: str = field(default="")

    _METRICS = (
        "total_kcal",
        "active_kcal",
        "duration_min",
        "avg_bpm",
        "min_bpm",
        "max_bpm",
        "zone_minutes",
        "fat_percent",
        "cardio_load",
    )

    def has_data(self) -> bool:
        """True if at least one metric was parsed (the source alone doesn't count)."""
        return any(getattr(self, key) is not None for key in self._METRICS)

    def to_dict(self) -> dict[str, Any]:
        """Serialise to a flat dict, omitting metrics that were not present."""
        out: dict[str, Any] = {}
        if self.source is not None:
            out["source"] = self.source
        for key in self._METRICS:
            value = getattr(self, key)
            if value is not None:
                out[key] = value
        return out

    def to_statistics_entry(self) -> dict[str, Any]:
        """Serialise to a ``statsEntry`` as defined in the workout JSON schema.

        Only fields that are present are emitted, and ``bpm``/``kcal`` are
        nested objects so the entry slots directly into a workout's
        ``statistics.entries`` array.
        """
        entry: dict[str, Any] = {}
        if self.source is not None:
            entry["source"] = self.source
        if self.duration_min is not None:
            entry["duration"] = _minutes_to_hms(self.duration_min)

        bpm = {
            "average": self.avg_bpm,
            "min": self.min_bpm,
            "max": self.max_bpm,
        }
        bpm = {k: v for k, v in bpm.items() if v is not None}
        if bpm:
            entry["bpm"] = bpm

        kcal = {"total": self.total_kcal, "active": self.active_kcal}
        kcal = {k: v for k, v in kcal.items() if v is not None}
        if kcal:
            entry["kcal"] = kcal

        if self.fat_percent is not None:
            entry["fat_percent"] = self.fat_percent
        if self.zone_minutes is not None:
            entry["zone_minutes"] = self.zone_minutes
        if self.cardio_load is not None:
            entry["cardio_load"] = self.cardio_load
        return entry


def _minutes_to_hms(minutes: int) -> str:
    """Format a whole-minute duration as ``HH:MM:SS`` (seconds always 00)."""
    hours, mins = divmod(minutes, 60)
    return f"{hours:02d}:{mins:02d}:00"


def _first_int(text: str) -> int | None:
    """Return the first non-negative integer found in ``text``, if any."""
    match = _INT.search(text)
    return int(match.group()) if match else None


def _clamp_bpm(value: int | None) -> int | None:
    """Drop implausible heart-rate readings (> :data:`MAX_BPM`)."""
    if value is None or value > MAX_BPM:
        return None
    return value


def _set(stat: SessionStat, attr: str, value: int | None) -> None:
    """Record ``value`` on ``stat.attr`` only if it is set and not already taken.

    First-wins: a later stray number on the same line cannot clobber an earlier,
    more specific value (and ``None`` never overwrites a real reading)."""
    if value is not None and getattr(stat, attr) is None:
        setattr(stat, attr, value)


def _apply_field(stat: SessionStat, raw_field: str) -> None:
    """Classify a single comma-separated field and record it on ``stat``."""
    low = raw_field.lower()

    if "bpm" in low:
        range_match = _RANGE.search(raw_field)
        if range_match:
            start = _clamp_bpm(int(range_match.group(1)))
            end = _clamp_bpm(int(range_match.group(2)))
            _set(stat, "max_bpm", end)
            if "range" in low:
                # A labelled range is min-max; keep it separate from any
                # separately reported average (e.g. Apple Watch).
                _set(stat, "min_bpm", start)
            else:
                # A bare "a-b bpm" (e.g. Polar) means average-max.
                _set(stat, "avg_bpm", start)
        else:
            # A single value ("111 average bpm" or a bare "x bpm") is the average.
            # An out-of-range typo (e.g. "746 bpm") clamps to None and is ignored.
            _set(stat, "avg_bpm", _clamp_bpm(_first_int(raw_field)))
        return

    if "kcal" in low:
        value = _first_int(raw_field)
        if "active" in low:
            _set(stat, "active_kcal", value)
        else:
            # "500 total kcal", Polar's bare "355 kcal" and "360kcal" are totals.
            _set(stat, "total_kcal", value)
        return

    # Fat percentage, but only when the field actually says "fat"/"grasa" - a
    # "56% actividad" (activity) must not be read as fat.
    if "%" in low and ("fat" in low or "grasa" in low):
        _set(stat, "fat_percent", _first_int(raw_field))
        return

    if "cardio" in low and "load" in low:
        _set(stat, "cardio_load", _first_int(raw_field))
        return

    # Zone minutes: "zone"/"zm" in any spelling ("37 zone min", "min zone",
    # "zone minutes", "22 zm", "66zm").
    zm_match = _ZM.search(raw_field)
    if "zone" in low or zm_match is not None:
        value = int(zm_match.group(1)) if zm_match else _first_int(raw_field)
        _set(stat, "zone_minutes", value)
        return

    minutes = _MINUTES.search(raw_field)
    if minutes is not None:
        _set(stat, "duration_min", int(minutes.group(1)))
        return


def is_stats_line(line: str) -> bool:
    """Return ``True`` if ``line`` is a ``# stats:`` metadata line."""
    return _STATS_PREFIX.match(line) is not None


def parse_stats_line(line: str) -> SessionStat | None:
    """Parse a single ``# stats:`` line into a :class:`SessionStat`.

    Returns ``None`` if the line is not a stats line. Unrecognised fields are
    ignored so that as much valid data as possible is still captured.
    """
    prefix = _STATS_PREFIX.match(line)
    if prefix is None:
        return None

    body = prefix.group(1).strip()
    stat = SessionStat(raw=line.strip())

    source_match = _SOURCE.match(body)
    if source_match:
        stat.source = source_match.group(1).strip() or None
        body = source_match.group(2).strip()

    for raw_field in body.split(","):
        raw_field = raw_field.strip()
        if raw_field:
            _apply_field(stat, raw_field)

    return stat


def parse_session_stats(source: str | Iterable[str]) -> list[SessionStat]:
    """Parse all ``# stats:`` lines from a string or an iterable of lines.

    Non-stats lines are skipped, so this can be handed a whole file or the list
    of comment/notes lines collected for a session.
    """
    lines: Iterable[str]
    lines = source.splitlines() if isinstance(source, str) else source

    stats: list[SessionStat] = []
    for line in lines:
        parsed = parse_stats_line(line)
        if parsed is not None:
            stats.append(parsed)
    return stats


def to_statistics(stats: list[SessionStat]) -> dict[str, Any]:
    """Build a workout ``statistics`` object from parsed session stats.

    Returns ``{}`` when there are no stats (preserving the empty-object default
    used throughout the serializers), otherwise ``{"entries": [...]}`` with one
    ``statsEntry`` per source.
    """
    if not stats:
        return {}
    return {"entries": [stat.to_statistics_entry() for stat in stats]}
