# Changelog: Configurable Synonym Loading Feature

## Summary

Extended `StandardizeName` to support configurable synonym loading from YAML/JSON files, enabling users to customize exercise name mappings without code changes and supporting internationalization.

## Changes Made

### Core Implementation

#### `parser/standardize_name.py`
- Added optional `config_path` parameter to `__init__()` method accepting `Path | str | None`
- Implemented `_load_synonyms_from_file()` method to load synonyms from YAML or JSON files
- Implemented `_get_default_synonyms()` method to return built-in default synonyms
- Added comprehensive validation for configuration file structure and content
- Supports both `.yaml`, `.yml`, and `.json` file extensions
- Added clear error messages for invalid configurations
- Maintains 100% backward compatibility - existing code works unchanged

### Configuration Files

#### `data/synonyms.yaml`
- Default synonym mappings in YAML format
- Includes all built-in exercise synonyms
- Well-documented with comments
- Validated against JSON Schema

#### `data/SYNONYMS_README.md`
- Comprehensive documentation for the synonym configuration feature
- Usage examples for YAML format
- Validation rules explanation
- Internationalization guide
- Error handling reference
- Best practices

### Documentation

#### `README.md`
- Added new "Features" section highlighting configurable synonyms
- Updated project structure to include `data/` and `examples/` directories
- Added quick example demonstrating the feature

#### `MIGRATION_SYNONYMS.md`
- Migration guide for users upgrading to the new version
- Emphasizes backward compatibility
- Provides configuration file format examples
- Includes internationalization examples
- Best practices and troubleshooting

#### `examples/README.md`
- Documentation for the examples directory
- Instructions for running examples
- Expected output descriptions

### Examples

#### `examples/custom_synonyms_example.py`
- Comprehensive working example demonstrating:
  - Default synonym usage
  - YAML configuration loading
  - Error handling
- Fully executable script with clear output
- Serves as both documentation and test

### Testing

#### `parser/test_standardize_name_config.py`
- Complete test suite for new configuration loading functionality
- Tests YAML file loading
- Tests JSON file loading
- Tests Path object support
- Tests file not found errors
- Tests unsupported file format errors
- Tests missing required keys
- Tests invalid data types
- Tests overlapping synonyms detection
- Tests duplicate clean names detection
- Tests default behavior preservation
- Tests internationalization
- Tests case-insensitive matching
- Tests both `.yaml` and `.yml` extensions
- 16 comprehensive test cases covering all scenarios

### Schema

#### `schema/exercise_synonyms.schema.json`
- JSON Schema for validating synonym configuration files
- Defines required structure and data types
- Can be used with JSON validators for configuration validation
- Documents the expected format formally

### Build Configuration

#### `pyproject.toml`
- Updated `[tool.hatch.build.targets.wheel]` to include:
  - `data/*.yaml`
  - `data/*.yml`
  - `data/*.json`
  - `data/*.md`
  - `examples/*.py`
  - `examples/*.md`
- Updated `[tool.hatch.build.targets.sdist]` to include:
  - `/data`
  - `/examples`
- Ensures configuration and example files are included in distributions

## Features

### 1. **Configurable Synonym Loading**
   - Load synonyms from external YAML or JSON files
   - No code changes required to customize mappings
   - Easy to maintain and version control

### 2. **Internationalization Support**
   - Create language-specific synonym files
   - Support multiple languages simultaneously
   - Example files for Spanish and French included

### 3. **Comprehensive Validation**
   - Validates file structure and data types on load
   - Prevents overlapping synonyms
   - Prevents duplicate clean names
   - Provides clear error messages

### 4. **Backward Compatibility**
   - Existing code continues to work unchanged
   - Default synonyms still available without configuration
   - Optional feature - use only when needed

### 5. **Developer-Friendly**
   - Accepts both `str` and `Path` objects for file paths
   - Supports `.yaml`, `.yml`, and `.json` extensions
   - Type-safe with full mypy compliance
   - Well-documented with examples

## Usage Examples

### Default Usage (Unchanged)
```python
from parser import StandardizeName

standardizer = StandardizeName()
standardizer.run("bench")  # Returns "Bench Press"
```

### Custom YAML Configuration
```python
from parser import StandardizeName

standardizer = StandardizeName(config_path="data/synonyms.yaml")
standardizer.run("bench")  # Returns "Bench Press"
```

### Internationalization
```python
from parser import StandardizeName

# Custom language-specific synonyms
standardizer = StandardizeName(config_path="data/synonyms_custom.yaml")
```

## Files Created/Modified

### New Files (12)
1. `data/synonyms.yaml`
2. `data/SYNONYMS_README.md`
3. `examples/custom_synonyms_example.py`
4. `examples/README.md`
5. `parser/test_standardize_name_config.py`
6. `schema/exercise_synonyms.schema.json`
7. `MIGRATION_SYNONYMS.md`
8. `CHANGELOG_SYNONYMS.md` (this file)
9. `IMPLEMENTATION_SUMMARY.md`
10. `QUICK_START_SYNONYMS.md`
11. `validate_synonyms_yaml.py`

### Modified Files (3)
1. `parser/standardize_name.py` - Core implementation
2. `README.md` - Added feature documentation
3. `pyproject.toml` - Updated build configuration

### Dependencies
- All required dependencies (PyYAML) already present in `pyproject.toml`
- No new dependencies required

## Testing

Run the comprehensive test suite:
```bash
make test  # Runs all tests including new config loading tests
```

Run only the new tests:
```bash
pytest parser/test_standardize_name_config.py -v
```

Run the example:
```bash
python examples/custom_synonyms_example.py
```

## Breaking Changes

**None.** This is a fully backward-compatible addition.

## Future Enhancements (Potential)

- Environment variable support for config path
- Multiple config file merging
- Config file hot-reloading
- Web-based synonym editor
- Auto-generation of config from training logs
- Synonym usage statistics

## Notes

- The feature maintains strict mypy type checking compliance
- All validation happens at initialization time for fail-fast behavior
- Configuration files are loaded once at initialization (not cached globally)
- Each `StandardizeName` instance can use a different configuration
