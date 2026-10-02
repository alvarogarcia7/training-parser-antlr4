#!/bin/bash
# Create app.zip containing application code and data
# Bundles: src/ (parser code), generated parser (dist/), schema/, data/config/synonyms.yaml

set -e

TARGET_DIR="$(cd "${1:-.}" && pwd)"
OUTPUT_ZIP="${TARGET_DIR}/app.zip"

echo "Creating app.zip archive..."

# Create temporary directory for staging
TEMP_DIR=$(mktemp -d)
trap "rm -rf $TEMP_DIR" EXIT

# Copy application sources
mkdir -p "$TEMP_DIR/src"
cp -r src/* "$TEMP_DIR/src/" 2>/dev/null || true

# Copy generated parser files
mkdir -p "$TEMP_DIR/dist"
cp dist/trainingLexer.py "$TEMP_DIR/dist/" 2>/dev/null || true
cp dist/trainingParser.py "$TEMP_DIR/dist/" 2>/dev/null || true
cp dist/trainingListener.py "$TEMP_DIR/dist/" 2>/dev/null || true
cp dist/trainingVisitor.py "$TEMP_DIR/dist/" 2>/dev/null || true
touch "$TEMP_DIR/dist/__init__.py"

# Copy schema files
mkdir -p "$TEMP_DIR/schema"
cp -r schema/*.json "$TEMP_DIR/schema/" 2>/dev/null || true

# Copy data/config
mkdir -p "$TEMP_DIR/data/config"
cp data/config/synonyms.yaml "$TEMP_DIR/data/config/" 2>/dev/null || true

# Create the zip file
cd "$TEMP_DIR"
zip -r -q "$OUTPUT_ZIP" . 2>/dev/null || {
  echo "Error: Failed to create zip file"
  exit 1
}

echo "✓ app.zip created: $OUTPUT_ZIP ($(du -h "$OUTPUT_ZIP" | cut -f1))"
