from pprint import pprint
import re
from pathlib import Path

from antlr4 import CommonTokenStream, InputStream

from dist.trainingLexer import trainingLexer
from dist.trainingParser import trainingParser
from parser import Formatter, Exercise


def parse_file(file_path: str) -> list[Exercise]:
    # Read the file and filter out date lines
    content = Path(file_path).read_text(encoding='utf-8')
    lines = content.split('\n')

    # Filter out date lines (YYYY-MM-DD) and empty lines
    filtered_lines = []
    for line in lines:
        line = line.strip()
        # Skip date lines and empty lines
        if line and not re.match(r'^\d{4}-\d{2}-\d{2}$', line):
            filtered_lines.append(line)

    # Rejoin the filtered content
    filtered_content = '\n'.join(filtered_lines)

    # Parse using ANTLR
    input_stream = InputStream(filtered_content)
    lexer = trainingLexer(input_stream)
    token_stream = CommonTokenStream(lexer)
    parser = trainingParser(token_stream)
    tree = parser.workout()

    formatter = Formatter()
    formatter.visit(tree)
    result: list[Exercise] = formatter.result
    return result


def main() -> None:
    file_name: str = 'training-sample_initial.txt'
    result: list[Exercise] = parse_file(file_name)
    pprint(result)


if __name__ == "__main__":
    main()
