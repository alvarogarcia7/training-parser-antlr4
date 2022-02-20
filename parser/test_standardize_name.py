import unittest

from parser import StandardizeName


class TestStandardizeName(unittest.TestCase):
    def test_title_case(self) -> None:
        self.assertEqual(StandardizeName().run('Overhead press'), 'Overhead Press')

    def test_trim_spaces(self) -> None:
        self.assertEqual(StandardizeName().run('Overhead Press  '), 'Overhead Press')

    def test_allow_short_names(self) -> None:
        self.assertEqual(StandardizeName().run('Oh'), 'Overhead Press')

    def test_allow_short_names_with_spaces(self) -> None:
        self.assertEqual(StandardizeName().run('Oh '), 'Overhead Press')

    def test_allow_short_names_lowercase_does_not_matter(self) -> None:
        self.assertEqual(StandardizeName().run('oh'), 'Overhead Press')

    def test_allow_short_names_lowercase_bench_press(self) -> None:
        self.assertEqual(StandardizeName().run('bench'), 'Bench Press')

    def test_check_non_overlapping_in_same_element(self) -> None:
        with self.assertRaises(AssertionError):
            StandardizeName()._check_synonym_configuration([
                {'clean': 'a', 'synonyms': ['1', '1']}
            ])

    def test_check_non_overlapping_in_different_element(self) -> None:
        with self.assertRaises(AssertionError):
            StandardizeName()._check_synonym_configuration([
                {'clean': 'a', 'synonyms': ['1']},
                {'clean': 'b', 'synonyms': ['1']}
            ])

    def test_check_synonyms_cannot_repeat_clean_names(self) -> None:
        with self.assertRaises(AssertionError):
            StandardizeName()._check_synonym_configuration([
                {'clean': 'a', 'synonyms': ['1']},
                {'clean': 'a', 'synonyms': ['2']}
            ])
