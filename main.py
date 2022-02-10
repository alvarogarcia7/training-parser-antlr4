from pprint import pprint

from antlr4 import FileStream, CommonTokenStream

from dist.trainingLexer import trainingLexer
from dist.trainingParser import trainingParser
from parser import Formatter


def main() -> None:
    file_name = 'training-sample_initial.txt'
    input_stream = FileStream(file_name)
    print('input_stream:')
    print(input_stream)
    print()
    lexer = trainingLexer(input_stream)
    token_stream = CommonTokenStream(lexer)
    token_stream.fill()
    print('tokens:')
    for tk in token_stream.tokens:
        print(tk)
    print()
    parser = trainingParser(token_stream)
    tree = parser.sessions()

    print('visitor:')
    formatter = Formatter()
    formatter.visit(tree)
    result = formatter.result
    pprint(result)
    print()


if __name__ == "__main__":
    main()
