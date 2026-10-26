---
id: TP-14
title: Equipment classification from a configuration file
status: Done
assignee: []
created_date: '2026-10-24 11:00'
updated_date: '2026-10-24 11:00'
labels: []
dependencies: []
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Classify each exercise's equipment from its name using a configuration file,
instead of hard-coding `"other"`. An exercise name that includes an equipment
keyword implies that equipment ("Smith Machine ..." -> smith machine,
"Dumbbell ..." -> dumbbell, "Barbell ..." -> barbell, ...). Exercises with no
keyword match that are known barbell lifts (squat, bench press, deadlift,
overhead press) default to barbell. Everything else is "other".
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Equipment rules live in a configuration file (data/config/equipment.yaml)
- [x] #2 A keyword in the exercise name maps it to that equipment
- [x] #3 Keyword match wins over the barbell fallback ("Smith Machine Squat" -> smith machine)
- [x] #4 squat / bench press / deadlift / overhead press default to barbell
- [x] #5 Unknown exercises are "other"; the result is always a valid schema enum value
- [x] #6 Set-centric and bench-centric serialization emit the resolved equipment
- [x] #7 Tests cover classification and serialization integration
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
- `data/config/equipment.yaml`: ordered keyword rules + `barbell_defaults` list.
- `src/parser/equipment.py`: `EquipmentClassifier` / `classify_equipment()`;
  config resolved relative to the module so it works from any cwd, and a missing
  config degrades gracefully to "other".
- Serialization (`src/parser/serializer.py`) and compact display
  (`src/parser/display.py`) call `classify_equipment(exercise.name)`.
- `schema/common-definitions.schema.json`: `equipment` enum extended with
  `smith machine`.
- Resolution order (case-insensitive): keyword-in-name -> barbell default ->
  other. Entries are tried in order, so more specific keywords (e.g.
  `smith machine` before `machine`) come first.
- Tests: `tests/test_equipment.py`.
- Shipped in PR #25 (merged to master); the dedicated `smith machine` type was a
  follow-up refinement on master.
<!-- SECTION:NOTES:END -->
