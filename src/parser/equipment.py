"""Equipment classification for exercises (CR3).

Resolves an exercise name to an equipment type using a YAML configuration
(``data/config/equipment.yaml`` by default):

    1. keyword match - if the name contains a configured keyword, use its type
       (e.g. "Smith Machine Squat" -> machine, "Dumbbell Curl" -> dumbbell).
    2. barbell fallback - if nothing matched and the name is a configured
       barbell default (squat, bench press, deadlift, overhead press) -> barbell.
    3. otherwise -> other.

The resolved type is always one of the values allowed by the JSON schema's
``equipment`` enum.
"""

import json
from pathlib import Path
from typing import TypedDict

import yaml

# Values allowed by schema/common-definitions.schema.json#/$defs/equipment.
VALID_EQUIPMENT = frozenset(
    {"smith machine","barbell", "dumbbell", "machine", "bodyweight", "cable", "kettlebell", "other"}
)
DEFAULT_EQUIPMENT = "other"
BARBELL = "barbell"

# Repo-root/data/config/equipment.yaml, resolved relative to this module so it
# works regardless of the current working directory (as the serializer does for
# its JSON schema files).
DEFAULT_CONFIG_PATH = (
    Path(__file__).resolve().parent.parent.parent / "data" / "config" / "equipment.yaml"
)


class EquipmentRule(TypedDict):
    type: str
    keywords: list[str]


class EquipmentClassifier:
    def __init__(self, config_path: Path | str = DEFAULT_CONFIG_PATH) -> None:
        self._rules, self._barbell_defaults = self._load_from_file(config_path)

    def _load_from_file(
        self, config_path: Path | str
    ) -> tuple[list[EquipmentRule], set[str]]:
        path = Path(config_path) if isinstance(config_path, str) else config_path

        # A missing config must not break serialization: fall back to "other".
        if not path.exists():
            return [], set()

        with open(path, "r", encoding="utf-8") as f:
            suffix = path.suffix.lower()
            if suffix == ".json":
                data = json.load(f)
            elif suffix in (".yaml", ".yml"):
                data = yaml.safe_load(f)
            else:
                raise ValueError(
                    f"Unsupported file format: {suffix}. Use .json, .yaml, or .yml"
                )

        if not isinstance(data, dict):
            raise ValueError("Equipment configuration must be a mapping at the root level")

        rules: list[EquipmentRule] = []
        for item in data.get("equipment", []) or []:
            if not isinstance(item, dict) or "type" not in item or "keywords" not in item:
                raise ValueError("Each equipment entry must have 'type' and 'keywords'")
            equipment_type = item["type"]
            keywords = item["keywords"]
            if equipment_type not in VALID_EQUIPMENT:
                raise ValueError(
                    f"Unknown equipment type '{equipment_type}'. "
                    f"Allowed: {sorted(VALID_EQUIPMENT)}"
                )
            if not isinstance(keywords, list) or not all(isinstance(k, str) for k in keywords):
                raise ValueError("'keywords' must be a list of strings")
            rules.append({"type": equipment_type, "keywords": [k.casefold() for k in keywords]})

        barbell_defaults = {
            str(name).casefold() for name in (data.get("barbell_defaults", []) or [])
        }
        return rules, barbell_defaults

    def classify(self, exercise_name: str) -> str:
        """Return the equipment type for ``exercise_name``."""
        normalized = exercise_name.strip().casefold()

        for rule in self._rules:
            if any(keyword in normalized for keyword in rule["keywords"]):
                return rule["type"]

        if normalized in self._barbell_defaults:
            return BARBELL

        return DEFAULT_EQUIPMENT


_default_classifier: EquipmentClassifier | None = None


def classify_equipment(exercise_name: str) -> str:
    """Classify an exercise name using the default (repo) equipment config."""
    global _default_classifier
    if _default_classifier is None:
        _default_classifier = EquipmentClassifier()
    return _default_classifier.classify(exercise_name)
