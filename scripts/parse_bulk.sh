#!/bin/bash
set -euo pipefail

# Bulk training file parser
# Parses multiple training log files and exports them to both set-centric and bench-centric JSON
# Results are appended to a database file and sorted

usage() {
    cat <<EOF
Usage: $0 [OPTIONS] <input_files...>

Parse multiple training files and export to JSON (both set-centric and bench-centric formats).
Each input file gives one <name>_set.json and one <name>_bench.json. A file that contains
several dated sessions (YYYY-MM-DD lines) gives one pair per session, named
<name>_<date>_set.json / <name>_<date>_bench.json.
Results are appended to a database file (one entry per session) and all JSON files are sorted.

OPTIONS:
    -o, --output-dir DIR    Output directory (default: data/parsed)
    -d, --database FILE     Database file to append results to (default: output-dir/database.json)
    -h, --help              Show this help message

EXAMPLES:
    # Parse single file
    $0 training.txt

    # Parse multiple files
    $0 file1.txt file2.txt file3.txt

    # Parse with custom output directory
    $0 -o data/results file1.txt file2.txt

    # Parse with custom database file
    $0 -d data/all_workouts.json file1.txt file2.txt
EOF
    exit 1
}

# Default values
OUTPUT_DIR="data/parsed"
DATABASE_FILE=""
INPUT_FILES=()

# Parse arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        -o|--output-dir)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        -d|--database)
            DATABASE_FILE="$2"
            shift 2
            ;;
        -h|--help)
            usage
            ;;
        -*)
            echo "Error: Unknown option: $1" >&2
            usage
            ;;
        *)
            INPUT_FILES+=("$1")
            shift
            ;;
    esac
done

# Validate inputs
if [ ${#INPUT_FILES[@]} -eq 0 ]; then
    echo "Error: No input files specified" >&2
    usage
fi

# Set default database file if not provided
if [ -z "$DATABASE_FILE" ]; then
    DATABASE_FILE="$OUTPUT_DIR/database.json"
fi

# Create output directory
mkdir -p "$OUTPUT_DIR"

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MANIFEST="$(mktemp)"
trap 'rm -f "$MANIFEST"' EXIT

# Each input file is parsed once and mapped to its own <name>_set.json and
# <name>_bench.json; the database gets one entry per input file.
# Failures for individual files are reported on stderr and do not stop the rest.
status=0
PYTHONPATH="$REPO_ROOT${PYTHONPATH:+:$PYTHONPATH}" python3 "$REPO_ROOT/scripts/bulk_export.py" \
    -o "$OUTPUT_DIR" -d "$DATABASE_FILE" --manifest "$MANIFEST" "${INPUT_FILES[@]}" || status=$?

# Sort only the files produced by this run (the output directory may hold
# unrelated JSON files). Keys are sorted everywhere; database workouts are
# ordered by date, then workout id.
echo ""
echo "Sorting JSON files..."
while IFS= read -r json_file; do
    echo "  → Sorting: $json_file"
    if [ "$json_file" = "$DATABASE_FILE" ]; then
        jq -S '.workouts |= sort_by(.date, .workout_id)' "$json_file" > "${json_file}.tmp"
    else
        jq -S . "$json_file" > "${json_file}.tmp"
    fi
    mv "${json_file}.tmp" "$json_file"
done < "$MANIFEST"

echo ""
if [ "$status" -eq 0 ]; then
    echo "✓ Bulk parsing complete!"
else
    echo "✗ Bulk parsing finished with errors" >&2
fi
echo "  Output directory: $OUTPUT_DIR"
echo "  Database file: $DATABASE_FILE"
exit "$status"
