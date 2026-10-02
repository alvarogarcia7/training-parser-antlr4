#!/bin/bash
# Vendor JavaScript dependencies (isomorphic-git, lightning-fs) into dist/vendor/
# These are downloaded from npm once at build time and served locally.

set -e

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VENDOR_DIR="$PROJECT_ROOT/dist/vendor"
TEMP_DIR="/tmp/training-parser-vendor-$$"

echo "Vendoring JavaScript dependencies..."
mkdir -p "$VENDOR_DIR"
mkdir -p "$TEMP_DIR"

trap "rm -rf $TEMP_DIR" EXIT

# Download isomorphic-git
echo "Downloading isomorphic-git@1.27.1..."
cd "$TEMP_DIR"
npm init -y > /dev/null 2>&1
npm install --no-save isomorphic-git@1.27.1 > /dev/null 2>&1
IGIT_SRC="node_modules/isomorphic-git/index.umd.min.js"
if [ -f "$IGIT_SRC" ]; then
  cp "$IGIT_SRC" "$VENDOR_DIR/isomorphic-git.min.js"
  echo "✓ isomorphic-git vendored to $VENDOR_DIR/isomorphic-git.min.js"
else
  echo "ERROR: Could not find isomorphic-git UMD build"
  exit 1
fi

# Download lightning-fs
echo "Downloading @isomorphic-git/lightning-fs@4.6.0..."
npm install --no-save @isomorphic-git/lightning-fs@4.6.0 > /dev/null 2>&1
LFS_SRC="node_modules/@isomorphic-git/lightning-fs/dist/lightning-fs.min.js"
if [ -f "$LFS_SRC" ]; then
  cp "$LFS_SRC" "$VENDOR_DIR/lightning-fs.min.js"
  echo "✓ lightning-fs vendored to $VENDOR_DIR/lightning-fs.min.js"
else
  echo "ERROR: Could not find lightning-fs UMD build"
  exit 1
fi

cd - > /dev/null

echo "✓ JavaScript dependencies vendored successfully"
echo "  Location: $VENDOR_DIR/"
echo "  Files:"
echo "    - isomorphic-git.min.js"
echo "    - lightning-fs.min.js"
