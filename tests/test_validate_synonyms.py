"""Tests for the synonyms validator used by the pre-commit hook."""

import tempfile
import unittest
from pathlib import Path

from validate_synonyms_yaml import main


class TestValidateSynonyms(unittest.TestCase):
    """The validator reuses StandardizeName's configuration checks."""

    def test_repository_synonyms_are_valid(self) -> None:
        self.assertEqual(main([]), 0)

    def test_rejects_recursive_synonym(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "synonyms.yaml"
            path.write_text("synonyms:\n  - clean: bench press\n    synonyms:\n      - bench\n      - bp\n")
            self.assertEqual(main([str(path)]), 1)

    def test_rejects_overlapping_synonyms(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "synonyms.yaml"
            path.write_text(
                "synonyms:\n"
                "  - clean: squat\n    synonyms: [s]\n"
                "  - clean: deadlift\n    synonyms: [s]\n"
            )
            self.assertEqual(main([str(path)]), 1)
