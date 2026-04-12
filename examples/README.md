# Examples

This directory contains example scripts demonstrating various features of the training parser.

## Custom Synonyms Example

**File**: `custom_synonyms_example.py`

Demonstrates how to use the configurable synonym loading feature for exercise name standardization.

### Running the Example

```bash
# Make sure you're in the repo root
python examples/custom_synonyms_example.py
```

### What it demonstrates

1. **Default Synonyms**: Using built-in synonym mappings
2. **YAML Configuration**: Loading custom synonyms from a YAML file
3. **Error Handling**: Proper exception handling for invalid configurations

### Expected Output

The script will show how different exercise name inputs are standardized:

```
=== Example 1: Default Synonyms ===
  'bench' -> 'Bench Press'
  'oh' -> 'Overhead Press'
  'lat pull-down' -> 'Machine Lateral Pull-Down'
  'Custom Exercise Name' -> 'Custom Exercise Name'

=== Example 2: YAML Configuration ===
  'bench' -> 'Bench Press'
  'bp' -> 'Bench Press'
  'overhead' -> 'Overhead Press'
...
```

## Creating Your Own Examples

To create a new example:

1. Create a new Python file in this directory
2. Import the necessary modules from the `parser` package
3. Add documentation explaining what the example demonstrates
4. Update this README with a description of your example
