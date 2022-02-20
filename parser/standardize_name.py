from itertools import chain
from typing import TypedDict

Synonym = TypedDict('Synonym', {
    'clean': str,
    'synonyms': list[str],
})

class StandardizeName:
    def __init__(self) -> None:
        self._synonyms: list[Synonym] = [
            {'clean': 'overhead press', 'synonyms': ['oh', 'overhead', 'op']},
            {'clean': 'bench press', 'synonyms': ['bench']},
            {'clean': 'lateral pull-down', 'synonyms': ['lat pull-down', 'lat pull down']}
        ]
        self._check_synonym_configuration(self._synonyms)

    def run(self, raw_name: str) -> str:
        selected_name = self._original_or_synonym(raw_name)
        return selected_name.title().rstrip()

    def _original_or_synonym(self, raw_name: str) -> str:
        for synonym_group in self._synonyms:
            for synonym in synonym_group['synonyms']:
                if raw_name.strip().casefold() == synonym.casefold():
                    selected_name = synonym_group['clean']
                    return selected_name
        return raw_name

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
