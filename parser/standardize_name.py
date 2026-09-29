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
        normalized_input = raw_name.strip().casefold()

        # First, try to match the entire input as a synonym
        for synonym_group in self._synonyms:
            for synonym in synonym_group['synonyms']:
                if normalized_input == synonym.casefold():
                    return synonym_group['clean']

        # If no full match, process word by word
        parts = []
        words = normalized_input.split(" ")
        index = 0
        while index < len(words):
            part = words[index]
            index += 1
            clean = self._synonym_for_word(part.strip())
            if clean is None:
                parts.append(part)
                continue
            parts.append(clean)
            # Skip the following words when they already spell the end of the clean name,
            # e.g. "bench press" -> "bench press" instead of "bench press press"
            index += self._repeated_tail_length(clean.casefold().split(), words[index:])
        return " ".join(parts)

    def _synonym_for_word(self, word: str) -> str | None:
        for synonym_group in self._synonyms:
            for synonym in synonym_group['synonyms']:
                if word == synonym.casefold():
                    return synonym_group['clean']
        return None

    @staticmethod
    def _repeated_tail_length(clean_words: list[str], following_words: list[str]) -> int:
        """Longest n such that the next n input words equal the last n words of the clean name."""
        for length in range(min(len(clean_words) - 1, len(following_words)), 0, -1):
            if [w.strip() for w in following_words[:length]] == clean_words[-length:]:
                return length
        return 0

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
