# Quick Start: Custom Synonyms

## Basic Usage

### Default (No Changes Required)
```python
from parser import StandardizeName

standardizer = StandardizeName()
result = standardizer.run("bench")  # Returns "Bench Press"
```

### Load from YAML
```python
standardizer = StandardizeName(config_path="data/synonyms.yaml")
```

## Create Custom Config

### YAML Format
```yaml
synonyms:
  - clean: exercise name
    synonyms:
      - short1
      - short2
```

## Run Example
```bash
python examples/custom_synonyms_example.py
```

## More Info
- Full docs: [data/SYNONYMS_README.md](data/SYNONYMS_README.md)
- Migration: [MIGRATION_SYNONYMS.md](MIGRATION_SYNONYMS.md)
- Changelog: [CHANGELOG_SYNONYMS.md](CHANGELOG_SYNONYMS.md)
