from pprint import pprint

from antlr4 import FileStream, CommonTokenStream

from dist.trainingLexer import trainingLexer
from dist.trainingParser import trainingParser
from parser import Formatter, Exercise


def parse_file(file_path: str) -> list[Exercise]:
    input_stream = FileStream(file_path)
    lexer = trainingLexer(input_stream)
    token_stream = CommonTokenStream(lexer)
    parser = trainingParser(token_stream)
    tree = parser.sessions()
    
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
