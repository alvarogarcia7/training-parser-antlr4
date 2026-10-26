"""Tests for validate-then-insert into the database (bin/insert_data_to_db.py).

A training file is inserted into the database only after it validates; a file
that fails to parse/validate leaves the database untouched and the process
exits non-zero (exit code 0 on success, so it can gate automation).
"""

import json
import subprocess
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, cast

from bin.insert_data_to_db import validate_and_insert

REPO_ROOT = Path(__file__).resolve().parent.parent

VALID_WORKOUT = """2025-01-01
Bench press 75k: 4, 5x3
Squat 70k: 5x10
"""

VALID_TWO_SESSIONS = """2025-01-01
Bench press 75k: 4, 5x3

2025-01-02
Deadlift 100k: 5
"""

# A session with content that cannot be parsed as any exercise.
INVALID_WORKOUT = """2025-01-01
@@@ this is not a workout @@@
"""


class TestValidateAndInsert(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.output_dir = self.tmp / "parsed"
        (self.output_dir / "set").mkdir(parents=True)
        (self.output_dir / "bench").mkdir(parents=True)
        self.db = self.output_dir / "database.json"

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def _file(self, content: str, name: str = "data.txt") -> Path:
        path = self.tmp / name
        path.write_text(content)
        return path

    def _workouts(self) -> list[dict[str, Any]]:
        return cast("list[dict[str, Any]]", json.loads(self.db.read_text())["workouts"])

    def test_valid_file_inserts_and_exits_zero(self) -> None:
        rc = validate_and_insert(self._file(VALID_WORKOUT), self.output_dir, self.db)
        self.assertEqual(rc, 0)
        self.assertTrue(self.db.exists())
        self.assertEqual(len(self._workouts()), 1)
        # set-/bench-centric files were written too.
        self.assertEqual(len(list((self.output_dir / "set").glob("*.json"))), 1)
        self.assertEqual(len(list((self.output_dir / "bench").glob("*.json"))), 1)

    def test_each_session_becomes_a_workout(self) -> None:
        rc = validate_and_insert(self._file(VALID_TWO_SESSIONS), self.output_dir, self.db)
        self.assertEqual(rc, 0)
        self.assertEqual(len(self._workouts()), 2)

    def test_rerun_upserts_without_duplicating(self) -> None:
        data = self._file(VALID_WORKOUT)
        self.assertEqual(validate_and_insert(data, self.output_dir, self.db), 0)
        self.assertEqual(validate_and_insert(data, self.output_dir, self.db), 0)
        self.assertEqual(len(self._workouts()), 1)

    def test_invalid_file_exits_nonzero_and_leaves_db_untouched(self) -> None:
        rc = validate_and_insert(self._file(INVALID_WORKOUT), self.output_dir, self.db)
        self.assertEqual(rc, 1)
        self.assertFalse(self.db.exists())

    def test_invalid_file_does_not_corrupt_existing_db(self) -> None:
        # Seed the DB with a valid workout, then a bad file must not change it.
        self.assertEqual(validate_and_insert(self._file(VALID_WORKOUT), self.output_dir, self.db), 0)
        before = self.db.read_text()
        rc = validate_and_insert(self._file(INVALID_WORKOUT, "bad.txt"), self.output_dir, self.db)
        self.assertEqual(rc, 1)
        self.assertEqual(self.db.read_text(), before)

    def test_missing_file_exits_nonzero(self) -> None:
        rc = validate_and_insert(self.tmp / "nope.txt", self.output_dir, self.db)
        self.assertEqual(rc, 1)
        self.assertFalse(self.db.exists())


class TestInsertCli(unittest.TestCase):
    """End-to-end check of the CLI entry point and its exit code."""

    def test_cli_on_sample_exits_zero_and_writes_db(self) -> None:
        with TemporaryDirectory() as tmp:
            output_dir = Path(tmp) / "parsed"
            db = output_dir / "database.json"
            result = subprocess.run(
                [
                    sys.executable, "bin/insert_data_to_db.py",
                    "data.txt.sample", "-o", str(output_dir), "-d", str(db),
                ],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(db.exists())
            self.assertGreater(len(json.loads(db.read_text())["workouts"]), 0)


if __name__ == "__main__":
    unittest.main()
