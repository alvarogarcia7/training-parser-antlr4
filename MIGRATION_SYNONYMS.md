# Migration Guide: Configurable Synonyms

This guide helps you migrate to the new configurable synonym loading feature.

## What Changed?

The `StandardizeName` class now supports loading exercise name synonyms from external YAML or JSON configuration files. This allows you to:

- Customize synonym mappings without modifying code
- Support multiple languages through separate config files
- Share and version control synonym configurations

## Backward Compatibility

**Good news!** Your existing code will continue to work without any changes.

The `StandardizeName` class still works the same way when called without arguments:

```python
from parser import StandardizeName

# This still works exactly as before
standardizer = StandardizeName()
standardizer.run("bench")  # Returns "Bench Press"
```

## Optional: Using Custom Synonyms

If you want to use custom synonyms, you can now pass a configuration file:

```python
from parser import StandardizeName

# Load custom synonyms
standardizer = StandardizeName(config_path="path/to/synonyms.yaml")
```

## Configuration File Format

### YAML Example

Create a file `synonyms.yaml`:

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

## Internationalization

To support multiple languages, create language-specific configuration files:

```python
# For English users (default)
standardizer_en = StandardizeName(config_path="data/synonyms.yaml")

# For other languages, create your own config file
standardizer_custom = StandardizeName(config_path="data/synonyms_custom.yaml")
```

Example custom configuration:

```yaml
synonyms:
  - clean: bench press
    synonyms:
      - press de banca
      - banca
      - pb
```

## Example Files Provided

The repository includes example configuration files in the `data/` directory:

- `data/synonyms.yaml` - Default synonyms in YAML format

## Code Examples

See the `examples/` directory for complete working examples:

- `examples/custom_synonyms_example.py` - Comprehensive usage examples

Run the example:

```bash
python examples/custom_synonyms_example.py
```

## Validation

Your configuration file is automatically validated when loaded. The system checks for:

1. **No overlapping synonyms**: Each synonym can only map to one clean name
2. **No duplicate clean names**: Each clean name must be unique
3. **Proper structure**: All required fields must be present and properly typed

If validation fails, you'll get a clear error message explaining what's wrong.

## Best Practices

1. **Keep synonyms lowercase**: While matching is case-insensitive, use lowercase for consistency
2. **Version control your configs**: Track changes to synonym mappings over time
3. **Document your mappings**: Use YAML comments to explain non-obvious synonyms
4. **Test thoroughly**: Verify all synonyms work as expected before deployment
5. **Avoid abbreviation conflicts**: Ensure short forms don't overlap

## Need Help?

- See [data/SYNONYMS_README.md](data/SYNONYMS_README.md) for detailed documentation
- Check [examples/custom_synonyms_example.py](examples/custom_synonyms_example.py) for working code
- Review [parser/test_standardize_name_config.py](parser/test_standardize_name_config.py) for test examples

## Summary

- **No action required** - Existing code continues to work
- **Optional feature** - Use config files only if you need custom synonyms
- **Fully backward compatible** - No breaking changes
