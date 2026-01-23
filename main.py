from pprint import pprint

from antlr4 import FileStream, CommonTokenStream

from dist.trainingLexer import trainingLexer
from dist.trainingParser import trainingParser
from parser import Formatter, Exercise
from parser.error_listener import TrainingErrorListener, format_error_message


class ParsingException(Exception):
    """Exception raised when parsing errors are detected."""
    pass


def parse_file(file_path: str) -> list[Exercise]:
    input_stream = FileStream(file_path)
    lexer = trainingLexer(input_stream)

    # Instantiate error listener
    error_listener = TrainingErrorListener()

    # Remove default error listeners and attach custom error listener to lexer
    lexer.removeErrorListeners()
    lexer.addErrorListener(error_listener)

    token_stream = CommonTokenStream(lexer)
    parser = trainingParser(token_stream)

    # Remove default error listeners and attach custom error listener to parser
    parser.removeErrorListeners()
    parser.addErrorListener(error_listener)

    tree = parser.sessions()

    # Check if errors were collected
    if error_listener.errors:
        # Read the input text for context
        with open(file_path, 'r') as f:
            input_text = f.read()

        # Display formatted error messages with full context
        print("Parsing errors detected:\n")
        for error in error_listener.errors:
            formatted_message = format_error_message(error, input_text)
            print(formatted_message)
            print()

        # Raise exception to prevent invalid parse tree processing
        raise ParsingException(f"Found {len(error_listener.errors)} parsing error(s)")

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
