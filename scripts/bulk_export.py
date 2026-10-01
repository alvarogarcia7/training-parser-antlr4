#!/usr/bin/env python3
"""
Bulk export utilities for training parser data.

Every input file is parsed exactly once. Each training session in it (a
YYYY-MM-DD line starts a session) is mapped to exactly one set-centric file and
one bench-centric file, so a file with a single session gives one pair and a
file with N dated sessions gives N pairs. The files and the database entry of a
session are built from the same parse, so they can never disagree, and nothing
is shared between different sessions or input files.
"""

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, NamedTuple, Optional

from parser.serializer import serialize_to_bench_centric, serialize_to_set_centric
from parser import StandardizeName
from parser.model import Exercise
from src.data_access import DataAccess

DATE_LINE = re.compile(r'^\d{4}-\d{2}-\d{2}$')
REPO_ROOT = Path(__file__).resolve().parent.parent


class Session(NamedTuple):
    """One training session found in an input file."""
    date: Optional[str]  # YYYY-MM-DD, or None if the file has no date line
    exercises: list[Exercise]


class ExportedSession(NamedTuple):
    """Result of exporting one session of an input file."""
    input_file: Path
    set_file: Path
    bench_file: Path
    workout: dict[str, Any]


def _digest(text: str) -> str:
    return hashlib.sha1(text.encode()).hexdigest()[:8]


def _path_digest(path: Path) -> str:
    return _digest(str(path.resolve()))


def split_sessions(text: str) -> list[tuple[Optional[str], list[str]]]:
    """Split training text into (date, lines) chunks, one per YYYY-MM-DD line.

    Text without any date line is a single undated session. Text before the
    first date line (when the file has dates) is returned as an undated chunk.
    """
    chunks: list[tuple[Optional[str], list[str]]] = [(None, [])]
    for line in text.splitlines():
        if DATE_LINE.match(line.strip()):
            chunks.append((line.strip(), []))
        else:
            chunks[-1][1].append(line)
    if len(chunks) > 1 and not any(line.strip() for line in chunks[0][1]):
        chunks.pop(0)
    return chunks


def read_sessions(input_file: Path) -> list[Session]:
    """Parse every session of ``input_file``; sessions without exercises are skipped."""
    # Anchor the synonyms file to the repository so the script works from any cwd
    data_access = DataAccess(StandardizeName(REPO_ROOT / "data" / "synonyms.yaml"))
    sessions: list[Session] = []
    for date, lines in split_sessions(input_file.read_text(encoding='utf-8')):
        exercises = data_access.parse_text("\n".join(lines))
        if exercises:
            sessions.append(Session(date, exercises))
        elif any(line.strip() and not line.strip().startswith('#') for line in lines):
            # There was content but none of it parsed: failing is better than
            # silently dropping a session from the output.
            raise ValueError(f"session {date or '(undated)'} has content but no exercise could be parsed")
        else:
            print(
                f"Warning: {input_file}: session {date or '(undated)'} has no exercises, skipped",
                file=sys.stderr
            )
    if not sessions:
        raise ValueError("no exercises found")
    return sessions


def assign_output_stems(input_files: list[Path], sessions: dict[Path, list[Session]]) -> dict[tuple[Path, int], str]:
    """Give every (input file, session index) its own output stem.

    A file with one session keeps the plain file stem (``day.txt`` gives
    ``day_set.json``); a file with several is named after each session date
    (``multi_2020-01-01_set.json``). If two sessions would still end up with
    the same stem (same date twice in one file, ``a/day.txt`` and ``b/day.txt``,
    ``day.txt`` and ``day.md``, ...) a digest of the input path and session
    index is appended, so nothing can overwrite anything else.
    """
    stems: dict[tuple[Path, int], str] = {}
    taken: set[str] = set()
    for input_file in input_files:
        for index, session in enumerate(sessions[input_file]):
            stem = input_file.stem
            if len(sessions[input_file]) > 1:
                stem = f"{stem}_{session.date or 'undated'}"
            if stem in taken:
                stem = f"{stem}-{_digest(f'{input_file.resolve()}#{index}')}"
            taken.add(stem)
            stems[(input_file, index)] = stem
    return stems


def session_timestamp(session: Session) -> datetime:
    """Workout timestamp: the session date, else the current time."""
    if session.date:
        return datetime.strptime(session.date, '%Y-%m-%d').replace(tzinfo=timezone.utc)
    return datetime.now(timezone.utc)


def workout_id(input_file: Path, index: int, multi: bool, timestamp: datetime) -> str:
    """Workout id that is unique per session (the timestamp alone is not)."""
    key = f"{input_file.resolve()}#{index}" if multi else str(input_file.resolve())
    return f"w_{timestamp.strftime('%Y%m%d_%H%M%S')}_{_digest(key)}"


def _write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding='utf-8')


def export_session(
    input_file: Path, index: int, sessions: list[Session], output_dir: Path, stem: str
) -> ExportedSession:
    """Write the set-centric and bench-centric files of one session."""
    session = sessions[index]
    timestamp = session_timestamp(session)
    wid = workout_id(input_file, index, len(sessions) > 1, timestamp)

    set_data = serialize_to_set_centric(session.exercises, timestamp)
    bench_data = serialize_to_bench_centric(session.exercises, timestamp)
    set_data["workout_id"] = bench_data["workout_id"] = wid

    set_file = output_dir / f"{stem}_set.json"
    bench_file = output_dir / f"{stem}_bench.json"
    _write_json(set_file, set_data)
    _write_json(bench_file, bench_data)

    workout = {**set_data, "source_file": str(input_file)}
    return ExportedSession(input_file, set_file, bench_file, workout)


def upsert_workouts(database_file: Path, workouts: list[dict[str, Any]]) -> None:
    """Add workouts to the database; a workout with a known id replaces the old entry.

    Re-running the pipeline on the same file therefore updates its entry
    instead of duplicating it. Entries are kept ordered by (date, workout_id).
    """
    if database_file.exists():
        db = json.loads(database_file.read_text(encoding='utf-8'))
    else:
        db = {}
    db.setdefault("workouts", [])

    by_id = {w["workout_id"]: w for w in db["workouts"] if "workout_id" in w}
    legacy = [w for w in db["workouts"] if "workout_id" not in w]
    for workout in workouts:
        by_id[workout["workout_id"]] = workout

    db["workouts"] = legacy + sorted(
        by_id.values(), key=lambda w: (w.get("date", ""), w["workout_id"])
    )
    _write_json(database_file, db)


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Bulk export training files to JSON")
    parser.add_argument("inputs", nargs="+", type=Path)
    parser.add_argument("-o", "--output-dir", type=Path, required=True)
    parser.add_argument("-d", "--database", type=Path, required=True)
    parser.add_argument(
        "--manifest", type=Path,
        help="Write the paths of every JSON file produced, one per line"
    )
    args = parser.parse_args(argv)

    args.output_dir.mkdir(parents=True, exist_ok=True)

    inputs: list[Path] = []
    failures = 0
    for input_file in args.inputs:
        if not input_file.is_file():
            print(f"Error: File not found: {input_file}", file=sys.stderr)
            failures += 1
        elif input_file.resolve() not in {p.resolve() for p in inputs}:
            inputs.append(input_file)

    # Parse every input completely before writing anything for it, so a file
    # that fails halfway leaves no partial output behind.
    parsed: dict[Path, list[Session]] = {}
    for input_file in inputs:
        print(f"Processing: {input_file}")
        try:
            parsed[input_file] = read_sessions(input_file)
        except Exception as e:
            print(f"Error processing {input_file}: {e}", file=sys.stderr)
            failures += 1
    good_inputs = [f for f in inputs if f in parsed]

    stems = assign_output_stems(good_inputs, parsed)
    exported: list[ExportedSession] = []
    for input_file in good_inputs:
        sessions = parsed[input_file]
        if len(sessions) > 1:
            print(f"  {len(sessions)} sessions found, exporting one pair per session")
        for index in range(len(sessions)):
            try:
                result = export_session(
                    input_file, index, sessions, args.output_dir, stems[(input_file, index)]
                )
            except Exception as e:
                print(f"Error processing {input_file}: {e}", file=sys.stderr)
                failures += 1
                continue
            print(f"  → set-centric:   {result.set_file}")
            print(f"  → bench-centric: {result.bench_file}")
            exported.append(result)

    if exported:
        upsert_workouts(args.database, [e.workout for e in exported])
        print(f"  → database:      {args.database}")

    if args.manifest:
        produced = [str(p) for e in exported for p in (e.set_file, e.bench_file)]
        if exported:
            produced.append(str(args.database))
        args.manifest.write_text("".join(f"{p}\n" for p in produced), encoding='utf-8')

    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
