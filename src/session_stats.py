"""Parse per-session health statistics from ``# stats:`` metadata lines.

Training files may carry device-reported session metadata on comment lines, e.g.::

    # stats: (apple watch) 500 total kcal, 402 active kcal, 50 min, 111 average bpm, 71-162 range bpm
    # stats: (polar) 355 kcal, 50 min, 108-140 bpm, 54% from fat

A single training session may carry several ``# stats:`` lines (one per device).
Each line names its source in parentheses and lists comma-separated fields. Parsing
is deliberately tolerant: whatever fields are recognised are extracted and the rest
are left unset, so partial, human-typed input still yields as much as possible.

Heart-rate conventions (from the task description):

- A labelled ``range`` (Apple Watch's ``71-162 range bpm``) is min-max: ``min_bpm``
  71, ``max_bpm`` 162. This is kept distinct from the separately reported
  ``111 average bpm`` so neither value is lost.
- A bare dash range (Polar's ``108-140 bpm``) is average-max: ``avg_bpm`` 108,
  ``max_bpm`` 140.
- A single value (``111 average bpm`` or a bare ``x bpm``) is the average.
- ``zm`` means zone minutes.
- Heart rate has an absolute ceiling of 220 bpm; values above it are discarded.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Iterable

# Heart rate cannot plausibly exceed this; higher readings are treated as noise.
MAX_BPM = 220

_INT = re.compile(r"\d+")
_RANGE = re.compile(r"(\d+)\s*-\s*(\d+)")
# A ``# stats:`` line: optional leading '#', then 'stats' and a colon.
_STATS_PREFIX = re.compile(r"^\s*#?\s*stats\s*:\s*(.*)$", re.IGNORECASE)
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
    raw: str = field(default="")

    def to_dict(self) -> dict[str, Any]:
        """Serialise to a dict, omitting metrics that were not present."""
        out: dict[str, Any] = {}
        if self.source is not None:
            out["source"] = self.source
        for key in (
            "total_kcal",
            "active_kcal",
            "duration_min",
            "avg_bpm",
            "min_bpm",
            "max_bpm",
            "zone_minutes",
            "fat_percent",
        ):
            value = getattr(self, key)
            if value is not None:
                out[key] = value
        return out


def _first_int(text: str) -> int | None:
    """Return the first non-negative integer found in ``text``, if any."""
    match = _INT.search(text)
    return int(match.group()) if match else None


def _clamp_bpm(value: int | None) -> int | None:
    """Drop implausible heart-rate readings (> :data:`MAX_BPM`)."""
    if value is None or value > MAX_BPM:
        return None
    return value


def _apply_field(stat: SessionStat, raw_field: str) -> None:
    """Classify a single comma-separated field and record it on ``stat``."""
    low = raw_field.lower()

    if "bpm" in low:
        range_match = _RANGE.search(raw_field)
        if range_match:
            low_start = _clamp_bpm(int(range_match.group(1)))
            high = _clamp_bpm(int(range_match.group(2)))
            stat.max_bpm = high
            if "range" in low:
                # A labelled range is min-max; keep it separate from any
                # separately reported average (e.g. Apple Watch).
                stat.min_bpm = low_start
            else:
                # A bare "a-b bpm" (e.g. Polar) means average-max.
                stat.avg_bpm = low_start
        else:
            # A single value ("111 average bpm" or a bare "x bpm") is the average.
            stat.avg_bpm = _clamp_bpm(_first_int(raw_field))
        return

    if "kcal" in low:
        value = _first_int(raw_field)
        if value is None:
            return
        if "active" in low:
            stat.active_kcal = value
        else:
            # "500 total kcal" and Polar's bare "355 kcal" are both totals.
            stat.total_kcal = value
        return

    if "%" in low or "fat" in low:
        stat.fat_percent = _first_int(raw_field)
        return

    if re.search(r"\bzm\b", low) or "zone" in low:
        stat.zone_minutes = _first_int(raw_field)
        return

    if "min" in low:
        stat.duration_min = _first_int(raw_field)
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
