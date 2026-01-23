# Missing Fields Documentation

This document describes all fields from `schema/set-centric.schema.json` that are not available from the parser output, along with their default values and rationale.

## Workout-Level Fields

### `workout_id` (string, required)
**Default:** Generated from timestamp in format `w_YYYYMMDD_HHMMSS`

**Rationale:** The parser processes workout text logs but has no concept of workout identity. A unique identifier is required by the schema, so we generate it from the current timestamp to ensure uniqueness and provide chronological ordering. The prefix `w_` provides semantic clarity.

### `date` (string, format: date-time, required)
**Default:** Current time in ISO 8601 format (e.g., `2024-01-15T14:30:00+00:00`)

**Rationale:** The parser does not extract date/time information from workout logs. Since workouts are typically logged at or near the time they are performed, defaulting to the current timestamp is a reasonable approximation. The date is required by the schema.

### `type` (string)
**Default:** Hardcoded to `"set-centric"`

**Rationale:** The serializer specifically outputs to the set-centric schema format. This is a structural constraint of the output format rather than parsed data, so it must be hardcoded.

### `location` (string)
**Default:** Empty string `""`

**Rationale:** The parser grammar does not support capturing workout location information. Defaulting to an empty string rather than null maintains type consistency and indicates this field is not applicable to parser-generated data.

### `notes` (string, workout-level)
**Default:** Empty string `""`

**Rationale:** While the grammar could theoretically support workout-level notes, the current implementation only captures exercise names and sets. An empty string indicates no notes are available from the parser.

### `statistics` (object)
**Default:** Empty object `{}`

**Rationale:** The parser extracts only exercise and set data (name, repetitions, weight). Workout statistics like duration, heart rate (bpm), calorie expenditure (kcal), and tracking device are not captured by the grammar. An empty object satisfies the schema while indicating that no statistics are available from parsed data.

**Note:** The schema defines optional statistics fields:
- `tracker` (string): Device/app used to track the workout
- `duration` (string, HH:MM:SS): Workout duration
- `bpm.average/min/max` (integer): Heart rate statistics
- `kcal.total` (integer): Calories burned

## Exercise-Level Fields

### `exercise_id` (string, optional)
**Default:** `null` (field omitted)

**Rationale:** The parser provides exercise names but has no concept of stable exercise identifiers across workouts. Exercise IDs would require a persistent exercise database or UUID generation, which is outside the parser's scope. Omitting this optional field is appropriate.

### `superset_id` (string, optional)
**Default:** `null` (field omitted)

**Rationale:** The parser grammar does not capture superset relationships between exercises. Supersets require either explicit markup in the log format or temporal analysis of exercise ordering, neither of which is currently supported. This optional field is omitted.

### `equipment` (enum, optional)
**Default:** `"other"`

**Rationale:** The parser does not extract equipment type from workout logs. The schema defines specific equipment types: `"barbell"`, `"dumbbell"`, `"machine"`, `"bodyweight"`, `"cable"`, `"kettlebell"`, `"other"`. Without this information, we default to `"other"` as the most neutral catch-all value. This could be enhanced through exercise name pattern matching (e.g., "DB Bench Press" → "dumbbell") or a lookup table.

### `notes` (string, exercise-level)
**Default:** `null` (field omitted)

**Rationale:** The parser does not capture exercise-level notes or annotations. This optional field is omitted rather than set to an empty string to distinguish between "no notes available" (parser limitation) and "explicitly empty notes" (user choice).

## Set-Level Fields

### `rpe` (number, 1-10, optional)
**Default:** `null` (field omitted)

**Rationale:** Rate of Perceived Exertion is subjective feedback not captured by the current parser grammar. RPE requires explicit notation in workout logs (e.g., "@RPE8"). This optional field is omitted as the parser provides no mechanism to extract it.

### `rir` (integer, ≥0, optional)
**Default:** `null` (field omitted)

**Rationale:** Reps in Reserve (how many more reps could be performed) is not captured by the parser. Like RPE, this requires explicit notation that the grammar doesn't support. This optional field is omitted.

### `tempo` (string, pattern: `^[0-9X]{3,4}$`, optional)
**Default:** `null` (field omitted)

**Rationale:** Tempo prescriptions (e.g., "31X1" for 3-second eccentric, 1-second pause, explosive concentric, 1-second pause at top) are not parsed. The grammar focuses on fundamental metrics (reps, weight) and does not capture tempo notation. This optional field is omitted.

### `rest_sec` (integer, ≥0, optional)
**Default:** `null` (field omitted)

**Rationale:** Rest periods between sets are not tracked by the parser. Capturing rest time would require either explicit notation or timestamp analysis across sets, neither of which is currently implemented. This optional field is omitted.

### `completed` (boolean, default: true, optional)
**Default:** `null` (field omitted)

**Rationale:** The parser assumes all logged sets were completed successfully. While the schema provides a `completed` field to distinguish between planned and executed sets, the parser only processes completed workout logs. The schema specifies `true` as the default, so omitting this field is semantically equivalent to marking sets as completed.

## Summary

The parser focuses on core workout data extraction:
- ✅ **Captured:** Exercise names, set count, repetitions, weight amounts, weight units
- ❌ **Not captured:** Identifiers, metadata (date/location/notes), workout statistics, equipment types, superset relationships, intensity metrics (RPE/RIR), tempo, rest periods, completion status

Missing fields fall into three categories:
1. **Generated values** (`workout_id`, `date`, `type`): Required by schema but not in source data
2. **Empty/neutral defaults** (`location`, `notes`, `statistics`, `equipment`): Schema fields without parser support
3. **Omitted optional fields** (`exercise_id`, `superset_id`, `rpe`, `rir`, `tempo`, `rest_sec`, `completed`): Advanced features beyond parser scope

These defaults create valid, minimal set-centric workout documents while clearly indicating which fields represent parsed data versus defaults/omissions.
