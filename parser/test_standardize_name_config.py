import json
import tempfile
import unittest
from pathlib import Path

import yaml

from parser import StandardizeName


class TestStandardizeNameConfigLoading(unittest.TestCase):
    def test_load_from_yaml_file(self) -> None:
        config_data = {
            'synonyms': [
                {'clean': 'overhead press', 'synonyms': ['oh', 'op']},
                {'clean': 'bench press', 'synonyms': ['bench', 'bp']},
            ]
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config_data, f)
            temp_path = f.name

        try:
            standardizer = StandardizeName(config_path=temp_path)
            self.assertEqual(standardizer.run('oh'), 'Overhead Press')
            self.assertEqual(standardizer.run('bench'), 'Bench Press')
            self.assertEqual(standardizer.run('bp'), 'Bench Press')
        finally:
            Path(temp_path).unlink()

    def test_load_from_json_file(self) -> None:
        config_data = {
            'synonyms': [
                {'clean': 'squat', 'synonyms': ['s', 'sq']},
                {'clean': 'deadlift', 'synonyms': ['d', 'dl']},
            ]
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            temp_path = f.name

        try:
            standardizer = StandardizeName(config_path=temp_path)
            self.assertEqual(standardizer.run('s'), 'Squat')
            self.assertEqual(standardizer.run('d'), 'Deadlift')
            self.assertEqual(standardizer.run('dl'), 'Deadlift')
        finally:
            Path(temp_path).unlink()

    def test_load_from_path_object(self) -> None:
        config_data = {
            'synonyms': [
                {'clean': 'pull-up', 'synonyms': ['pu']},
            ]
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config_data, f)
            temp_path = Path(f.name)

        try:
            standardizer = StandardizeName(config_path=temp_path)
            self.assertEqual(standardizer.run('pu'), 'Pull-Up')
        finally:
            temp_path.unlink()

    def test_file_not_found_error(self) -> None:
        with self.assertRaises(FileNotFoundError) as context:
            StandardizeName(config_path='nonexistent_file.yaml')

        self.assertIn('not found', str(context.exception))

    def test_unsupported_file_format(self) -> None:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write('some text')
            temp_path = f.name

        try:
            with self.assertRaises(ValueError) as context:
                StandardizeName(config_path=temp_path)

            self.assertIn('Unsupported file format', str(context.exception))
        finally:
            Path(temp_path).unlink()

    def test_missing_synonyms_key(self) -> None:
        config_data = {
            'exercises': [
                {'clean': 'overhead press', 'synonyms': ['oh']},
            ]
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config_data, f)
            temp_path = f.name

        try:
            with self.assertRaises(ValueError) as context:
                StandardizeName(config_path=temp_path)

            self.assertIn("'synonyms' key", str(context.exception))
        finally:
            Path(temp_path).unlink()

    def test_synonyms_not_a_list(self) -> None:
        config_data = {
            'synonyms': 'not a list'
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config_data, f)
            temp_path = f.name

        try:
            with self.assertRaises(ValueError) as context:
                StandardizeName(config_path=temp_path)

            self.assertIn("must be a list", str(context.exception))
        finally:
            Path(temp_path).unlink()

    def test_synonym_entry_missing_keys(self) -> None:
        config_data = {
            'synonyms': [
                {'clean': 'overhead press'},  # Missing 'synonyms'
            ]
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config_data, f)
            temp_path = f.name

        try:
            with self.assertRaises(ValueError) as context:
                StandardizeName(config_path=temp_path)

            self.assertIn("'clean' and 'synonyms' keys", str(context.exception))
        finally:
            Path(temp_path).unlink()

    def test_clean_not_a_string(self) -> None:
        config_data = {
            'synonyms': [
                {'clean': 123, 'synonyms': ['oh']},
            ]
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            temp_path = f.name

        try:
            with self.assertRaises(ValueError) as context:
                StandardizeName(config_path=temp_path)

            self.assertIn("'clean' must be a string", str(context.exception))
        finally:
            Path(temp_path).unlink()

    def test_synonyms_not_a_list_of_strings(self) -> None:
        config_data = {
            'synonyms': [
                {'clean': 'overhead press', 'synonyms': ['oh', 123]},
            ]
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            temp_path = f.name

        try:
            with self.assertRaises(ValueError) as context:
                StandardizeName(config_path=temp_path)

            self.assertIn("must be strings", str(context.exception))
        finally:
            Path(temp_path).unlink()

    def test_overlapping_synonyms_in_config_file(self) -> None:
        config_data = {
            'synonyms': [
                {'clean': 'overhead press', 'synonyms': ['oh']},
                {'clean': 'bench press', 'synonyms': ['oh']},  # Duplicate 'oh'
            ]
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config_data, f)
            temp_path = f.name

        try:
            with self.assertRaises(AssertionError):
                StandardizeName(config_path=temp_path)
        finally:
            Path(temp_path).unlink()

    def test_duplicate_clean_names_in_config_file(self) -> None:
        config_data = {
            'synonyms': [
                {'clean': 'overhead press', 'synonyms': ['oh']},
                {'clean': 'overhead press', 'synonyms': ['op']},  # Duplicate clean name
            ]
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config_data, f)
            temp_path = f.name

        try:
            with self.assertRaises(AssertionError):
                StandardizeName(config_path=temp_path)
        finally:
            Path(temp_path).unlink()

    def test_default_behavior_with_no_config(self) -> None:
        standardizer = StandardizeName()
        self.assertEqual(standardizer.run('bench'), 'Bench Press')
        self.assertEqual(standardizer.run('oh'), 'Overhead Press')

    def test_internationalization_example(self) -> None:
        config_data = {
            'synonyms': [
                {'clean': 'bench press', 'synonyms': ['press de banca', 'banca']},
                {'clean': 'squat', 'synonyms': ['sentadilla', 'sq']},
            ]
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config_data, f)
            temp_path = f.name

        try:
            standardizer = StandardizeName(config_path=temp_path)
            self.assertEqual(standardizer.run('press de banca'), 'Bench Press')
            self.assertEqual(standardizer.run('sentadilla'), 'Squat')
        finally:
            Path(temp_path).unlink()

    def test_yml_extension_supported(self) -> None:
        config_data = {
            'synonyms': [
                {'clean': 'dumbbell press', 'synonyms': ['db press']},
            ]
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            yaml.dump(config_data, f)
            temp_path = f.name

        try:
            standardizer = StandardizeName(config_path=temp_path)
            self.assertEqual(standardizer.run('db press'), 'Dumbbell Press')
        finally:
            Path(temp_path).unlink()

    def test_case_insensitive_matching_from_file(self) -> None:
        config_data = {
            'synonyms': [
                {'clean': 'overhead press', 'synonyms': ['oh']},
            ]
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config_data, f)
            temp_path = f.name

        try:
            standardizer = StandardizeName(config_path=temp_path)
            self.assertEqual(standardizer.run('OH'), 'Overhead Press')
            self.assertEqual(standardizer.run('Oh'), 'Overhead Press')
            self.assertEqual(standardizer.run('oH'), 'Overhead Press')
        finally:
            Path(temp_path).unlink()
