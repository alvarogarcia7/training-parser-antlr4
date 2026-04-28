#!/bin/bash
# Launch Neovim with training LSP configured for testing

set -e

# Get the project directory
PROJECT_DIR="$HOME/repos/workspaces/.vibe-kanban-workspaces/4808-configure-the-nv/training-parser-antlr4"

# Activate virtual environment
source "$PROJECT_DIR/.venv/bin/activate"

# Set VIRTUAL_ENV so nvim config can find training-lsp
export VIRTUAL_ENV="$PROJECT_DIR/.venv"

# Create test file with errors if it doesn't exist
TEST_FILE="/tmp/test_invalid.training"
if [ ! -f "$TEST_FILE" ]; then
    cat > "$TEST_FILE" << 'EOF'
Bench press: 3x8x75k
Squat 5x10x100k
Deadlift: invalid @#$
Overhead press: 5x5x40k @invalid
Pull-up: 3x max reps 50k
EOF
fi

echo "========================================================================"
echo "TRAINING LSP VERIFICATION - NEOVIM TEST"
echo "========================================================================"
echo ""
echo "Configuration:"
echo "  Project: $PROJECT_DIR"
echo "  Virtual environment: $VIRTUAL_ENV"
echo "  LSP command: $(which training-lsp)"
echo "  Test file: $TEST_FILE"
echo ""
echo "Test file content:"
cat "$TEST_FILE" | sed 's/^/  /'
echo ""
echo "========================================================================"
echo "Starting Neovim with training LSP..."
echo ""
echo "Instructions for testing:"
echo "  1. The file should open with error highlights"
echo "  2. Type :LspInfo to see LSP status"
echo "  3. Hover over errors with 'K' to see hover info"
echo "  4. Place cursor on error and press <space>ca for code actions"
echo "  5. Type ':q' to exit"
echo ""
echo "Detected errors (from diagnostics):"
echo "  - Line 2: Missing colon after 'Squat' exercise name"
echo "  - Line 3: Invalid characters (@#$) and wrong syntax"
echo "  - Line 4: Invalid character (@invalid) at end of line"
echo "  - Line 5: Invalid 'max reps' notation"
echo ""
echo "========================================================================"
echo ""

# Launch nvim with the test file
nvim "$TEST_FILE"
