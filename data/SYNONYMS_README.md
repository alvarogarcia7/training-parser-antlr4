# Exercise Name Synonyms Configuration

This directory contains configuration files for customizing exercise name mappings in the training parser.

## Overview

The `StandardizeName` class supports loading exercise name synonyms from external YAML or JSON configuration files. This allows you to:

- Customize exercise name mappings without modifying code
- Support internationalization by creating language-specific synonym files
- Maintain different synonym sets for different use cases
- Share and version control synonym configurations

## Usage

### Default Behavior

When no configuration file is specified, `StandardizeName` uses built-in default synonyms:

```python
from parser import StandardizeName

standardizer = StandardizeName()
result = standardizer.run("bp")  # Returns "Bench Press"
```

### Loading Custom Synonyms

Specify a configuration file path to load custom synonyms:

```python
from pathlib import Path
from parser import StandardizeName

# Using YAML
standardizer = StandardizeName(config_path="data/synonyms.yaml")

# Using Path object
standardizer = StandardizeName(config_path=Path("data/synonyms.yaml"))
```

## Configuration File Format

### YAML Format

```yaml
synonyms:
  - clean: overhead press
    synonyms:
      - oh
      - op

  - clean: bench press
    synonyms:
      - bp
```

## Structure Requirements

1. **Root key**: The configuration must have a `synonyms` key at the root level
2. **List of entries**: The `synonyms` value must be a list/array
3. **Entry format**: Each entry must contain:
   - `clean`: The standardized exercise name (string)
   - `synonyms`: A list of alternative names (array of strings)

## Validation Rules

The configuration is validated when the application loads it (`StandardizeName`) to ensure:

1. **No overlapping synonyms**: A synonym cannot appear in multiple entries
2. **No duplicate clean names**: Each clean name must be unique
3. **No recursive expansion**: A synonym cannot appear, as whole words, inside
   any clean name (e.g. `bench` for `bench press`), otherwise its expansion
   contains it again: `bench` -> `bench press` -> `bench press press` -> ...
4. **Proper data types**: All values must be strings

The same checks run when committing (pre-commit hook), see [Validation](#validation).

Invalid configurations will raise descriptive errors:

```python
# This will raise ValueError
standardizer = StandardizeName(config_path="invalid.yaml")
# ValueError: Each synonym entry must have 'clean' and 'synonyms' keys
```

## Internationalization

You can create language-specific synonym files for internationalization by following the same format:

```yaml
# Example: Spanish synonyms (synonyms_custom.yaml)
synonyms:
  - clean: bench press
    synonyms:
      - press de banca
      - banca
      - pb
```

## Example Files

This directory includes:

- `synonyms.yaml` - Default synonyms in YAML format (validated against JSON Schema)

## Validation

`validate_synonyms_yaml.py` validates a synonyms file in two steps:

1. **Structure**: against the JSON Schema in `schema/exercise_synonyms.schema.json`
2. **Validation rules**: it loads the file with `StandardizeName`, so it runs
   exactly the same checks as the application (see [Validation Rules](#validation-rules)),
   including the recursive-expansion check

To validate the YAML file yourself:

```bash
python validate_synonyms_yaml.py                 # data/synonyms.yaml
python validate_synonyms_yaml.py my-synonyms.yaml
make validate-synonyms
```

It also runs automatically as the `validate-synonyms` pre-commit hook whenever
`data/synonyms.yaml`, its schema, `parser/standardize_name.py` or the validator
change, so an invalid configuration cannot be committed.

Example of a rejected configuration:

```yaml
synonyms:
  - clean: bench press
    synonyms:
      - bench   # 'bench' is part of 'bench press': expands recursively
      - bp
```

```
✗ Synonym configuration error in data/synonyms.yaml: Synonym 'bench' expands recursively: it is part of the clean name 'bench press'
```

## Best Practices

1. **Keep synonyms lowercase**: The matching is case-insensitive, but use lowercase for consistency
2. **Avoid abbreviation conflicts**: Ensure short forms don't overlap (e.g., "bp" and "b")
3. **Never use a word of a clean name as a synonym**: e.g. not `bench` or `press`
   for `bench press`, nor for any other clean name containing that word
   (`inclined bench press`); use an abbreviation such as `bp` instead
4. **Document your mappings**: Add comments in YAML files to explain mappings
5. **Version control**: Commit configuration files to track changes over time
6. **Test thoroughly**: Ensure all synonyms map correctly before deploying

## Error Handling

Common errors and solutions:

| Error | Cause | Solution |
|-------|-------|----------|
| `FileNotFoundError` | Config file doesn't exist | Check file path and spelling |
| `ValueError: Unsupported file format` | Wrong file extension | Use `.yaml` or `.yml` |
| `ValueError: 'synonyms' must be a list` | Invalid structure | Ensure synonyms is a list/array |
| `AssertionError` | Overlapping synonyms or duplicate clean names | Check for duplicate synonyms / clean names across entries |
| `AssertionError: Synonym '...' expands recursively` | A synonym is part of a clean name | Replace it with an abbreviation that is not a word of any clean name |

## Integration Example

```python
from pathlib import Path
from parser import StandardizeName, Parser

# Load custom synonyms
config_path = Path("data/synonyms_es.yaml")
standardizer = StandardizeName(config_path=config_path)

# Use in parser
parser = Parser(standardizer=standardizer)

# Parse with Spanish exercise names
result = parser.parse("press de banca: 100kg x 5")
# Exercise name will be standardized to "Bench Press"
```
