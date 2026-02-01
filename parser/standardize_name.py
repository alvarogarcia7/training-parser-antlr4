import json
import yaml
from itertools import chain
from pathlib import Path
from typing import TypedDict

Synonym = TypedDict('Synonym', {
    'clean': str,
    'synonyms': list[str],
})


class StandardizeName:
    def __init__(self, config_path: Path | str = "data/synonyms.yaml") -> None:
        self._synonyms = self._load_synonyms_from_file(config_path)
        self._check_synonym_configuration(self._synonyms)

    def _load_synonyms_from_file(self, config_path: Path | str) -> list[Synonym]:
        path = Path(config_path) if isinstance(config_path, str) else config_path

        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        with open(path, 'r', encoding='utf-8') as f:
            file_extension = path.suffix.lower()

            if file_extension == '.json':
                data = json.load(f)
            elif file_extension in ('.yaml', '.yml'):
                data = yaml.safe_load(f)
            else:
                raise ValueError(f"Unsupported file format: {file_extension}. Use .json, .yaml, or .yml")

        if not isinstance(data, dict) or 'synonyms' not in data:
            raise ValueError("Configuration file must contain a 'synonyms' key at the root level")

        synonyms_data = data['synonyms']

        if not isinstance(synonyms_data, list):
            raise ValueError("'synonyms' must be a list")

        synonyms: list[Synonym] = []
        for item in synonyms_data:
            if not isinstance(item, dict):
                raise ValueError("Each synonym entry must be a dictionary")
            if 'clean' not in item or 'synonyms' not in item:
                raise ValueError("Each synonym entry must have 'clean' and 'synonyms' keys")
            if not isinstance(item['clean'], str):
                raise ValueError("'clean' must be a string")
            if not isinstance(item['synonyms'], list):
                raise ValueError("'synonyms' must be a list")
            if not all(isinstance(s, str) for s in item['synonyms']):
                raise ValueError("All synonym values must be strings")

            synonyms.append({'clean': item['clean'], 'synonyms': item['synonyms']})

        return synonyms

    def run(self, raw_name: str) -> str:
        selected_name = self._original_or_synonym(raw_name)
        return selected_name.title().rstrip()

    def _original_or_synonym(self, raw_name: str) -> str:
        parts = []
        for part in raw_name.strip().casefold().split(" "):
            appended = False
            for synonym_group in self._synonyms:
                for synonym in synonym_group['synonyms']:
                    if part.strip() == synonym.casefold():
                        parts.append(synonym_group['clean'])
                        appended = True
            if not appended:
                parts.append(part)
                appended = True
        return " ".join(parts)

    def _check_synonym_configuration(self, synonyms: list[Synonym]) -> None:
        self._check_non_overlapping_synonyms(synonyms)
        self._check_non_repeating_clean_name(synonyms)

    def _check_non_repeating_clean_name(self, synonyms: list[Synonym]) -> None:
        synonym_names = [synonym['clean'] for synonym in synonyms]
        assert self.all_elements_are_different(synonym_names)

    def _check_non_overlapping_synonyms(self, synonyms: list[Synonym]) -> None:
        synonym_elements = [synonym['synonyms'] for synonym in synonyms]
        all_synonyms = list(chain(*synonym_elements))
        assert self.all_elements_are_different(all_synonyms)

    def all_elements_are_different(self, values: list[str]) -> bool:
        return len(set(values)) == len(values)
