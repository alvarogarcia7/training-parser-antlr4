#!/usr/bin/env python3
"""
Bulk export utilities for training parser data.

Every input file is parsed exactly once and mapped to exactly one set-centric
file and one bench-centric file. Both files (and the database entry) are built
from that single parse, so the three can never disagree with each other, and
nothing is shared between different input files.
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
from src.data_access import DataAccess

DATE_LINE = re.compile(r'^\d{4}-\d{2}-\d{2}$')


class ExportedFile(NamedTuple):
    """Result of exporting one input file."""
    input_file: Path
    set_file: Path
    bench_file: Path
    workout: dict[str, Any]


def _path_digest(path: Path) -> str:
    return hashlib.sha1(str(path.resolve()).encode()).hexdigest()[:8]


def assign_output_stems(input_files: list[Path]) -> dict[Path, str]:
    """Give every input file its own output stem.

    The stem is the file's basename without extension. When two inputs would
    end up with the same stem (``a/day.txt`` and ``b/day.txt``, or ``day.txt``
    and ``day.md``) a digest of the input path is appended, so they can never
    overwrite each other's output.
    """
    stems: dict[Path, str] = {}
    taken: set[str] = set()
    for input_file in input_files:
        stem = input_file.stem
        if stem in taken:
            stem = f"{stem}-{_path_digest(input_file)}"
        taken.add(stem)
        stems[input_file] = stem
    return stems


def read_session_dates(input_file: Path) -> list[str]:
    """Return the YYYY-MM-DD lines found in a training file."""
    return [
        line.strip()
        for line in input_file.read_text(encoding='utf-8').splitlines()
        if DATE_LINE.match(line.strip())
    ]


def workout_timestamp(input_file: Path) -> datetime:
    """Workout timestamp: the date written in the file, else the current time.

    If the file has several dates, the earliest one is used; the caller is
    warned about that separately.
    """
    dates = read_session_dates(input_file)
    if dates:
        return datetime.strptime(min(dates), '%Y-%m-%d').replace(tzinfo=timezone.utc)
    return datetime.now(timezone.utc)


def workout_id(input_file: Path, timestamp: datetime) -> str:
    """Workout id that is unique per input file (the timestamp alone is not)."""
    return f"w_{timestamp.strftime('%Y%m%d_%H%M%S')}_{_path_digest(input_file)}"


def _write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding='utf-8')


def export_file(input_file: Path, output_dir: Path, stem: str) -> ExportedFile:
    """Parse ``input_file`` once and write its set-centric and bench-centric files."""
    exercises = DataAccess().parse_single_file(str(input_file))
    timestamp = workout_timestamp(input_file)
    wid = workout_id(input_file, timestamp)

    set_data = serialize_to_set_centric(exercises, timestamp)
    bench_data = serialize_to_bench_centric(exercises, timestamp)
    set_data["workout_id"] = bench_data["workout_id"] = wid

    set_file = output_dir / f"{stem}_set.json"
    bench_file = output_dir / f"{stem}_bench.json"
    _write_json(set_file, set_data)
    _write_json(bench_file, bench_data)

    workout = {**set_data, "source_file": str(input_file)}
    return ExportedFile(input_file, set_file, bench_file, workout)


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

    stems = assign_output_stems(inputs)
    exported: list[ExportedFile] = []
    for input_file in inputs:
        print(f"Processing: {input_file}")
        try:
            dates = read_session_dates(input_file)
            if len(dates) > 1:
                print(
                    f"Warning: {input_file} has {len(dates)} dated sessions; "
                    f"they are merged into one workout dated {min(dates)}",
                    file=sys.stderr
                )
            result = export_file(input_file, args.output_dir, stems[input_file])
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
