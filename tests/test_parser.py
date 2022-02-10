import unittest
from pprint import pprint

from antlr4 import CommonTokenStream, InputStream

from dist.trainingLexer import trainingLexer
from dist.trainingParser import trainingParser
from parser import Formatter, Exercise, Units


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
                         [Exercise('Bench press',
                                  [
                                      {'repetitions': 4, 'weight': {'amount': 10, 'unit': Units.KILOGRAM}},
                                      {'repetitions': 5, 'weight': {'amount': 10, 'unit': Units.KILOGRAM}},
                                      {'repetitions': 5, 'weight': {'amount': 10, 'unit': Units.KILOGRAM}},
                                      {'repetitions': 5, 'weight': {'amount': 10, 'unit': Units.KILOGRAM}},
                                      {'repetitions': 5, 'weight': {'amount': 10, 'unit': Units.KILOGRAM}},
                                      {'repetitions': 5, 'weight': {'amount': 10, 'unit': Units.KILOGRAM}},
                                  ])])
        self.assertEqual(True, True)
