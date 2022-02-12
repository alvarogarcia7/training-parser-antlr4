import unittest
from pprint import pprint

from antlr4 import CommonTokenStream, InputStream

from dist.trainingLexer import trainingLexer
from dist.trainingParser import trainingParser
from parser import Formatter, Exercise, Units, Repetition


class TestParser(unittest.TestCase):
    def test_canary(self) -> None:
        self.assertTrue(True)

    def test_visit_sessions(self) -> None:
        input_stream = InputStream('Bench press 10k: 4, 4x5\n')
        lexer = trainingLexer(input_stream)
        token_stream = CommonTokenStream(lexer)
        token_stream.fill()
        parser = trainingParser(token_stream)
        tree = parser.sessions()

        print('visitor:')
        formatter = Formatter()
        formatter.visit(tree)
        result = formatter.result
        pprint(result)
        print()
        self.assertListEqual(result,
                             [Exercise('Bench press', [self.serie(10, 4)] + [self.serie(10, 5) for _ in range(5)])])
        self.assertEqual(True, True)

    def serie(self, amount: int, repetition: int) -> Repetition:
        return {'repetitions': repetition, 'weight': {'amount': amount, 'unit': Units.KILOGRAM}}
