#!/usr/bin/env python3
"""
Example demonstrating custom synonym loading for exercise names.

This script shows how to:
1. Use default synonyms (built-in)
2. Load custom synonyms from YAML
3. Error handling
"""

from pathlib import Path
from parser import StandardizeName


def example_default_synonyms() -> None:
    """Example using default built-in synonyms."""
    print("=== Example 1: Default Synonyms ===")
    standardizer = StandardizeName()

    test_names = ["bench", "oh", "lat pull-down", "Custom Exercise Name"]

    for name in test_names:
        result = standardizer.run(name)
        print(f"  '{name}' -> '{result}'")
    print()


def example_yaml_config() -> None:
    """Example loading synonyms from YAML file."""
    print("=== Example 2: YAML Configuration ===")
    config_path = Path("data/synonyms.yaml")

    if not config_path.exists():
        print(f"  Warning: {config_path} not found")
        return

    standardizer = StandardizeName(config_path=config_path)

    test_names = ["bench", "bp", "overhead"]

    for name in test_names:
        result = standardizer.run(name)
        print(f"  '{name}' -> '{result}'")
    print()


def example_error_handling() -> None:
    """Example demonstrating error handling."""
    print("=== Example 3: Error Handling ===")

    # Try to load non-existent file
    try:
        standardizer = StandardizeName(config_path="nonexistent.yaml")
    except FileNotFoundError as e:
        print(f"  ✓ Caught expected error: {e}")

    # Try to load unsupported format
    try:
        standardizer = StandardizeName(config_path="data/test.txt")
    except (ValueError, FileNotFoundError) as e:
        print(f"  ✓ Caught expected error: {e}")

    print()


def main() -> None:
    """Run all examples."""
    print("\nCustom Synonyms Loading Examples")
    print("=" * 50)
    print()

    example_default_synonyms()
    example_yaml_config()
    example_error_handling()

    print("All examples completed!")
    print("\nFor more information, see data/SYNONYMS_README.md")


if __name__ == "__main__":
    main()
