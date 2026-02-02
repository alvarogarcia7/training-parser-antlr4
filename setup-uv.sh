#!/usr/bin/env bash
# Quick setup script for uv-based development environment

set -e

echo "==> Training Parser - uv Setup"
echo ""

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "uv not found. Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    echo ""
    echo "Please restart your shell or run: source ~/.bashrc (or ~/.zshrc)"
    echo "Then run this script again."
    exit 0
fi

echo "==> Creating virtual environment with uv..."
uv venv

echo ""
echo "==> Installing dependencies..."
source .venv/bin/activate
uv sync --all-extras

echo ""
echo "==> Downloading ANTLR jar..."
python3 scripts/download_antlr.py

echo ""
echo "==> Installing pre-commit hooks..."
pre-commit install

echo ""
echo "==> Setup complete!"
echo ""
echo "To activate the virtual environment, run:"
echo "  source .venv/bin/activate"
echo ""
echo "Useful commands:"
echo "  make compile-grammar  - Compile ANTLR4 grammar"
echo "  make typecheck        - Run mypy type checking"
echo "  make test             - Run all tests"
echo "  python main.py        - Run sample parser"
