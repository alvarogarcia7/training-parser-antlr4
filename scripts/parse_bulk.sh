#!/bin/bash
set -euo pipefail

# Bulk training file parser
# Parses multiple training log files and exports them to both set-centric and bench-centric JSON
# Results are appended to a database file and sorted

usage() {
    cat <<EOF
Usage: $0 [OPTIONS] <input_files...>

Parse multiple training files and export to JSON (both set-centric and bench-centric formats).
Results are appended to a database file and all JSON files are sorted.

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

# Initialize database file if it doesn't exist
if [ ! -f "$DATABASE_FILE" ]; then
    echo '{"workouts": []}' > "$DATABASE_FILE"
fi

# Function to get base filename without extension
get_base_name() {
    basename "$1" | sed 's/\.[^.]*$//'
}

# Function to sort JSON file
sort_json_file() {
    local file="$1"
    if [ -f "$file" ]; then
        jq -S . "$file" > "${file}.tmp" && mv "${file}.tmp" "$file"
    fi
}

# Function to export set-centric JSON
export_set_centric() {
    local input_file="$1"
    local output_file="$2"
    python3 main_export.py "$input_file" -o "$output_file" 2>/dev/null || true
}

# Function to export bench-centric JSON
export_bench_centric() {
    local input_file="$1"
    local output_file="$2"
    python3 -c "
import sys
sys.path.insert(0, '.')
from scripts.bulk_export import export_bench_centric
export_bench_centric('$input_file', '$output_file')
" || return 1
}

# Function to append to database
append_to_database() {
    local json_file="$1"
    local database_file="$2"
    python3 -c "
import sys
sys.path.insert(0, '.')
from scripts.bulk_export import append_to_database
append_to_database('$json_file', '$database_file')
" || return 1
}

# Process each input file
for input_file in "${INPUT_FILES[@]}"; do
    if [ ! -f "$input_file" ]; then
        echo "Error: File not found: $input_file" >&2
        continue
    fi

    base_name=$(get_base_name "$input_file")
    set_centric_file="$OUTPUT_DIR/${base_name}_set.json"
    bench_centric_file="$OUTPUT_DIR/${base_name}_bench.json"

    echo "Processing: $input_file"

    # Export to set-centric format
    echo "  → Exporting to set-centric: $set_centric_file"
    export_set_centric "$input_file" "$set_centric_file"

    # Export to bench-centric format
    echo "  → Exporting to bench-centric: $bench_centric_file"
    export_bench_centric "$input_file" "$bench_centric_file"

    # Append set-centric results to database
    if [ -f "$set_centric_file" ]; then
        echo "  → Appending to database: $DATABASE_FILE"
        append_to_database "$set_centric_file" "$DATABASE_FILE"
    fi
done

# Sort all JSON files
echo ""
echo "Sorting JSON files..."
for json_file in "$OUTPUT_DIR"/*.json; do
    if [ -f "$json_file" ]; then
        echo "  → Sorting: $json_file"
        sort_json_file "$json_file"
    fi
done

echo ""
echo "✓ Bulk parsing complete!"
echo "  Output directory: $OUTPUT_DIR"
echo "  Database file: $DATABASE_FILE"
