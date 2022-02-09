from dist.training_mineLexer import training_mineLexer
from dist.training_mineParser import training_mineParser
from dist.training_mineVisitor import *

from antlr4 import FileStream, CommonTokenStream


def main() -> None:
    file_name = 'training-sample_initial.txt'
    input_stream = FileStream(file_name)
    print('input_stream:')
    print(input_stream)
    print()
    lexer = training_mineLexer(input_stream)
    token_stream = CommonTokenStream(lexer)
    token_stream.fill()
    print('tokens:')
    for tk in token_stream.tokens:
        print(tk)
    print()
    parser = training_mineParser(token_stream)
    tree = parser.sessions()

    print('tree:')
    lisp_tree_str = tree.toStringTree(recog=parser)
    print(lisp_tree_str)
    print()


if __name__ == "__main__":
    main()
