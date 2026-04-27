#!/usr/bin/env python3
"""Test the training parser diagnostics directly."""

import sys
from pathlib import Path

# Add project to path
project_path = Path.home() / "repos/workspaces/.vibe-kanban-workspaces/4808-configure-the-nv/training-parser-antlr4"
sys.path.insert(0, str(project_path))

from lsp.diagnostics import get_diagnostics

# Test content with errors
test_content = """Bench press: 3x8x75k
Squat 5x10x100k
Deadlift: invalid @#$
Overhead press: 5x5x40k @invalid
Pull-up: 3x max reps 50k
"""

print("=" * 70)
print("TRAINING PARSER DIAGNOSTICS TEST")
print("=" * 70)
print("\nTest file content:")
print("-" * 70)
for i, line in enumerate(test_content.strip().split('\n'), 1):
    print(f"{i}: {line}")
print("-" * 70)

# Get diagnostics
print("\nRunning diagnostic check...")
diagnostics = get_diagnostics(test_content)

print(f"\nDiagnostics found: {len(diagnostics)}")
print("=" * 70)

if diagnostics:
    for i, diag in enumerate(diagnostics, 1):
        line = diag.range.start.line
        col = diag.range.start.character
        message = diag.message
        severity = diag.severity  # 1=Error, 2=Warning
        severity_str = "ERROR" if severity == 1 else "WARNING"

        lines = test_content.split('\n')
        code_line = lines[line] if line < len(lines) else ""

        print(f"\nError #{i}")
        print(f"  Location: Line {line + 1}, Column {col + 1}")
        print(f"  Severity: {severity_str}")
        print(f"  Message:  {message}")
        print(f"  Code:     {code_line}")
        print("-" * 70)
else:
    print("No diagnostics found (unexpected)")

print("\nTest completed successfully!")
