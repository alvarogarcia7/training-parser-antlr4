from pprint import pprint

from antlr4 import InputStream

from parser import Parser, ParseResult


def parse_file(file_path: str) -> ParseResult:
    """Parse a file and return both exercises and errors."""
    with open(file_path, 'r') as f:
        content = f.read()

    input_stream = InputStream(content)
    parser = Parser(input_stream, content)
    return parser.parse()


def main() -> None:
    file_name: str = 'training-sample.txt'
    result: ParseResult = parse_file(file_name)

    print("=== Parsed Exercises ===")
    pprint(result.exercises)

    if result.has_errors:
        print("\n=== Parsing Errors ===")
        for error in result.errors:
            print(f"  {error}")
    else:
        print("\n✓ No errors found")


if __name__ == "__main__":
    main()
