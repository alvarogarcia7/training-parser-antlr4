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
        self.assertEqual(StandardizeName().run('bp'), 'Bench Press')

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

    def test_multiple_synonyms(self) -> None:
        self.assertEqual(StandardizeName().run('m bp'), 'Machine Bench Press')

    def test_multiple_synonyms_when_there_is_no_synonym_for_the_second_shortcut(self) -> None:
        self.assertEqual(StandardizeName().run('m anotherthing'), 'Machine Anotherthing')

    def test_full_clean_name_is_not_expanded_twice(self) -> None:
        self.assertEqual(StandardizeName().run('Bench press'), 'Bench Press')
        self.assertEqual(StandardizeName().run('bench press'), 'Bench Press')

    def test_clean_name_inside_longer_name_is_not_expanded_twice(self) -> None:
        self.assertEqual(StandardizeName().run('machine bench press'), 'Machine Bench Press')
        self.assertEqual(StandardizeName().run('bench press machine'), 'Bench Press Machine')

    def test_shortcut_followed_by_another_shortcut_should_be_converted_twice(self) -> None:
        self.assertEqual(StandardizeName().run('bp press'), 'Bench Press Press')


    def test_synonym_must_not_be_part_of_its_clean_name(self) -> None:
        with self.assertRaises(AssertionError):
            StandardizeName()._check_synonym_configuration([
                {'clean': 'bench press', 'synonyms': ['bench']}
            ])

    def test_synonym_must_not_be_part_of_another_clean_name(self) -> None:
        with self.assertRaises(AssertionError):
            StandardizeName()._check_synonym_configuration([
                {'clean': 'bench press', 'synonyms': ['bp']},
                {'clean': 'press', 'synonyms': ['bench press']},
            ])

    def test_multi_word_synonym_inside_clean_name_is_recursive(self) -> None:
        with self.assertRaises(AssertionError):
            StandardizeName()._check_synonym_configuration([
                {'clean': 'machine lateral pull-down', 'synonyms': ['Lateral Pull-Down']}
            ])

    def test_synonym_that_is_only_a_substring_of_a_word_is_allowed(self) -> None:
        StandardizeName()._check_synonym_configuration([
            {'clean': 'squat', 'synonyms': ['s', 'squ']}
        ])

    def test_default_synonyms_do_not_expand_recursively(self) -> None:
        standardizer = StandardizeName()
        names = [group['clean'] for group in standardizer._synonyms]
        names += [synonym for group in standardizer._synonyms for synonym in group['synonyms']]
        for name in names:
            once = standardizer.run(name)
            self.assertEqual(standardizer.run(once), once, f"'{name}' expands recursively")

    def test_clean_names_are_unchanged(self) -> None:
        standardizer = StandardizeName()
        for group in standardizer._synonyms:
            self.assertEqual(standardizer.run(group['clean']), group['clean'].title())
