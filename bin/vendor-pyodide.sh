#!/bin/bash
# Vendor Pyodide files into dist/vendor/pyodide/
# Downloads Pyodide runtime from CDN once at build time.

set -e

PYODIDE_VERSION="0.27.0"
PYODIDE_URL="https://cdn.jsdelivr.net/pyodide/v${PYODIDE_VERSION}/full"
VENDOR_DIR="dist/vendor/pyodide"

echo "Vendoring Pyodide v${PYODIDE_VERSION}..."
mkdir -p "$VENDOR_DIR"

# Download main JavaScript file
echo "Downloading pyodide.js..."
curl -L -o "$VENDOR_DIR/pyodide.js" "${PYODIDE_URL}/pyodide.js"

# Download the mjs variant (required by newer Pyodide)
echo "Downloading pyodide.mjs..."
curl -L -o "$VENDOR_DIR/pyodide.mjs" "${PYODIDE_URL}/pyodide.mjs"

# Download the WASM files
echo "Downloading WASM files..."
curl -L -o "$VENDOR_DIR/pyodide.asm.js" "${PYODIDE_URL}/pyodide.asm.js"
curl -L -o "$VENDOR_DIR/pyodide.asm.wasm" "${PYODIDE_URL}/pyodide.asm.wasm"
curl -L -o "$VENDOR_DIR/pyodide.asm.wasm.map" "${PYODIDE_URL}/pyodide.asm.wasm.map" || true

# Download Python standard library archive
echo "Downloading python_stdlib.zip..."
curl -L -o "$VENDOR_DIR/python_stdlib.zip" "${PYODIDE_URL}/python_stdlib.zip"

# Download the tar variant (for direct unpack if needed)
echo "Downloading python_stdlib.tar..."
curl -L -o "$VENDOR_DIR/python_stdlib.tar" "${PYODIDE_URL}/python_stdlib.tar" || true

# Download pyodide_py.tar (additional Python resources)
echo "Downloading pyodide_py.tar..."
curl -L -o "$VENDOR_DIR/pyodide_py.tar" "${PYODIDE_URL}/pyodide_py.tar"

# Download package index
echo "Downloading pyodide-lock.json..."
curl -L -o "$VENDOR_DIR/pyodide-lock.json" "${PYODIDE_URL}/pyodide-lock.json"

# Download required Python packages
echo "Resolving and downloading Python packages..."
PACKAGE_FILES=$(python3 - "$VENDOR_DIR/pyodide-lock.json" pyyaml jsonschema <<'PYEOF'
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

echo "Downloading Python packages (pyyaml, jsonschema, and dependencies)..."
while IFS= read -r file_name; do
  [ -z "$file_name" ] && continue
  echo "  ${file_name}..."
  curl -L -o "$VENDOR_DIR/$file_name" "${PYODIDE_URL}/${file_name}"
done <<< "$PACKAGE_FILES"

echo "✓ Pyodide vendored successfully"
echo "  Version: v${PYODIDE_VERSION}"
echo "  Location: $VENDOR_DIR/"
echo "  Runtime ready for PWA offline deployment"
