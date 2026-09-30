#!/bin/bash
# Download Pyodide for offline PWA support
# This enables the PWA to work offline by bundling Pyodide locally

set -e

PYODIDE_VERSION="0.27.0"
PYODIDE_URL="https://cdn.jsdelivr.net/pyodide/v${PYODIDE_VERSION}/full"
PYODIDE_DIR="mobile-app/pyodide"

echo "Downloading Pyodide v${PYODIDE_VERSION}..."
mkdir -p "$PYODIDE_DIR"

# Download main JavaScript file
echo "Downloading pyodide.js..."
curl -L -o "$PYODIDE_DIR/pyodide.js" "${PYODIDE_URL}/pyodide.js"

# Download the asm.js glue code (required alongside pyodide.asm.wasm for the
# runtime to boot; without it loadPyodide() hangs indefinitely)
echo "Downloading pyodide.asm.js..."
curl -L -o "$PYODIDE_DIR/pyodide.asm.js" "${PYODIDE_URL}/pyodide.asm.js"

# Download main WASM file (required for Python runtime)
echo "Downloading pyodide.asm.wasm..."
curl -L -o "$PYODIDE_DIR/pyodide.asm.wasm" "${PYODIDE_URL}/pyodide.asm.wasm"

# Download WASM source map (optional, not required to boot)
echo "Downloading pyodide.asm.wasm.map..."
curl -L -o "$PYODIDE_DIR/pyodide.asm.wasm.map" "${PYODIDE_URL}/pyodide.asm.wasm.map" || true

# Download the Python standard library archive (required to boot the
# interpreter)
echo "Downloading python_stdlib.zip..."
curl -L -o "$PYODIDE_DIR/python_stdlib.zip" "${PYODIDE_URL}/python_stdlib.zip"

# Download the package index (needed to resolve package file names/URLs)
echo "Downloading pyodide-lock.json (Python package index)..."
curl -L -o "$PYODIDE_DIR/pyodide-lock.json" "${PYODIDE_URL}/pyodide-lock.json"

# Remove stray artifacts from a previous, broken version of this script
# (a "wheels/" subfolder that pyodide.loadPackage() never looked at).
rm -rf "$PYODIDE_DIR/wheels"

# Resolve the exact package files (and their transitive dependencies) that
# mobile-app/python/app_api.py needs at runtime. app_api.py -> parser.parser
# / parser.serializer pulls in jsonschema, and parser/__init__.py pulls in
# standardize_name.py -> yaml (pyyaml). pyodide-worker.js calls
# pyodide.loadPackage(['pyyaml', 'jsonschema']), and Pyodide resolves those
# package names (plus everything in their "depends" chain) against
# pyodide-lock.json, fetching each package's exact "file_name" directly from
# indexURL (i.e. flat, alongside pyodide.js -- there is no "wheels/"
# subfolder). We mirror that resolution here so the files are already
# present locally and loadPackage() never has to fall back to the network.
echo "Resolving required Python packages from pyodide-lock.json..."
PACKAGE_FILES=$(python3 - "$PYODIDE_DIR/pyodide-lock.json" pyyaml jsonschema <<'PYEOF'
import json
import sys

lock_path = sys.argv[1]
roots = sys.argv[2:]

with open(lock_path) as f:
    lock = json.load(f)

def normalize(name):
    return name.lower().replace("_", "-")

packages = lock["packages"]
by_name = {normalize(name): pkg for name, pkg in packages.items()}

needed = set()
stack = list(roots)
while stack:
    name = normalize(stack.pop())
    if name in needed:
        continue
    pkg = by_name.get(name)
    if pkg is None:
        print(f"WARNING: package '{name}' not found in pyodide-lock.json", file=sys.stderr)
        continue
    needed.add(name)
    stack.extend(pkg.get("depends", []))

for name in sorted(needed):
    print(by_name[name]["file_name"])
PYEOF
)

if [ -z "$PACKAGE_FILES" ]; then
  echo "ERROR: could not resolve any package files from pyodide-lock.json" >&2
  exit 1
fi

echo "Downloading Python packages (pyyaml, jsonschema, and their dependencies)..."
while IFS= read -r file_name; do
  [ -z "$file_name" ] && continue
  echo "  ${file_name}..."
  curl -L -o "$PYODIDE_DIR/$file_name" "${PYODIDE_URL}/${file_name}"
done <<< "$PACKAGE_FILES"

echo "✓ Pyodide downloaded to $PYODIDE_DIR"
echo "  JavaScript: $PYODIDE_DIR/pyodide.js"
echo "  WASM: $PYODIDE_DIR/pyodide.asm.wasm"
echo ""
echo "These files will be bundled when you run: make pwa-publish"
echo "The PWA will then work offline without CDN dependencies."
