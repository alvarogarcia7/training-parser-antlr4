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

# Download main WASM file (required for Python runtime)
echo "Downloading pyodide.asm.wasm..."
curl -L -o "$PYODIDE_DIR/pyodide.asm.wasm" "${PYODIDE_URL}/pyodide.asm.wasm"

# Download WASM data file
echo "Downloading pyodide.asm.wasm.map..."
curl -L -o "$PYODIDE_DIR/pyodide.asm.wasm.map" "${PYODIDE_URL}/pyodide.asm.wasm.map" || true

# Download Python standard library
echo "Downloading pyodide-lock.json (Python packages)..."
curl -L -o "$PYODIDE_DIR/pyodide-lock.json" "${PYODIDE_URL}/pyodide-lock.json"

# Download package wheel files (needed for pyyaml and jsonschema)
echo "Downloading Python packages..."
mkdir -p "$PYODIDE_DIR/wheels"

# pyyaml package
curl -L -o "$PYODIDE_DIR/wheels/pyyaml-6.0-cp311-cp311-emscripten_3_1_27_wasm32.whl" \
  "${PYODIDE_URL}/wheels/pyyaml-6.0-cp311-cp311-emscripten_3_1_27_wasm32.whl" || true

# jsonschema package
curl -L -o "$PYODIDE_DIR/wheels/jsonschema-4.19.1-py3-none-any.whl" \
  "${PYODIDE_URL}/wheels/jsonschema-4.19.1-py3-none-any.whl" || true

echo "✓ Pyodide downloaded to $PYODIDE_DIR"
echo "  JavaScript: $PYODIDE_DIR/pyodide.js"
echo "  WASM: $PYODIDE_DIR/pyodide.asm.wasm"
echo ""
echo "These files will be bundled when you run: make pwa-publish"
echo "The PWA will then work offline without CDN dependencies."
