import unittest

from basicParser import Parser
from interpreter import Interpreter, Context
from lexer import Lexer
from test.share import run_tokenize, run_interpreter, run_parser


class TestEP3_2(unittest.TestCase):
    def test_parse1(self):
        self.assertEqual(
            run_tokenize("2 ^ 3"),
            "[2, POW, 3, EOF]"
        )

    def test_parse2(self):
        self.assertEqual(
            run_parser("2 ^ -"),
            "Invalid Syntax: Invalid token, File <basic>, line 1 column 5"
        )

    def test_parse3(self):
        self.assertEqual(
            run_parser("2 ^ 3"),
            "(2,POW,3)"
        )

    def test_pars4(self):
        self.assertEqual(
            run_parser("2 ^ 3 ^ 2"),
            "(2,POW,(3,POW,2))"
        )

    def test_parse6(self):
        self.assertEqual(
            run_interpreter("2 ^ 3 ^ 2"),
            "512.0"
        )

    def test_parse7(self):
        self.assertEqual(
            run_interpreter("(2 - 3 ) * 5 ^ 2"),
            "-25.0"
        )

    def test_parse8(self):
        self.assertEqual(
            run_interpreter("1 + (2+3) ^ (4-2)"),
            "26.0"
        )

    def test_parse9(self):
        self.assertEqual(
            run_interpreter("1 + (2+3) ^ (2-4)"),
            "1.04"
        )

    def test_parse10(self):
        self.assertEqual(
            run_interpreter("10/(2^0-1)"),
            "Traceback: \n" +
            " File <basic>, line 1, in <Program>\n" +
            "Runtime Error: Division by zero, File <basic>, line 1 column 4"
        )

if __name__ == '__main__':
    unittest.main()
