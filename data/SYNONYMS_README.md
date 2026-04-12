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
result = standardizer.run("bench")  # Returns "Bench Press"
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
      - overhead
      - op

  - clean: bench press
    synonyms:
      - bench
      - bp
```

## Structure Requirements

1. **Root key**: The configuration must have a `synonyms` key at the root level
2. **List of entries**: The `synonyms` value must be a list/array
3. **Entry format**: Each entry must contain:
   - `clean`: The standardized exercise name (string)
   - `synonyms`: A list of alternative names (array of strings)

## Validation Rules

The configuration is validated on load to ensure:

1. **No overlapping synonyms**: A synonym cannot appear in multiple entries
2. **No duplicate clean names**: Each clean name must be unique
3. **Proper data types**: All values must be strings

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

The YAML file is validated against the JSON Schema defined in `schema/exercise_synonyms.schema.json`.

To validate the YAML file yourself:

```bash
python validate_synonyms_yaml.py
```

This ensures the configuration file structure is correct before use.

## Best Practices

1. **Keep synonyms lowercase**: The matching is case-insensitive, but use lowercase for consistency
2. **Avoid abbreviation conflicts**: Ensure short forms don't overlap (e.g., "bp" and "b")
3. **Document your mappings**: Add comments in YAML files to explain mappings
4. **Version control**: Commit configuration files to track changes over time
5. **Test thoroughly**: Ensure all synonyms map correctly before deploying

## Error Handling

Common errors and solutions:

| Error | Cause | Solution |
|-------|-------|----------|
| `FileNotFoundError` | Config file doesn't exist | Check file path and spelling |
| `ValueError: Unsupported file format` | Wrong file extension | Use `.yaml` or `.yml` |
| `ValueError: 'synonyms' must be a list` | Invalid structure | Ensure synonyms is a list/array |
| `AssertionError` | Overlapping synonyms | Check for duplicate synonyms across entries |

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
