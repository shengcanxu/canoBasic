import unittest

from basicParser import Parser
from interpreter import Interpreter, Context
from lexer import Lexer
from test.share import run_tokenize, run_interpreter, run_parser


class TestEP4(unittest.TestCase):
    def test_parse1(self):
        self.assertEqual(
            run_tokenize("var a = 3"),
            "[TT_KEYWORD:var, TT_IDENTIFIER:a, TT_EQ, TT_INT:3, TT_EOF]"
        )

    def test_parse2(self):
        self.assertEqual(
            run_parser("var a = 3"),
            "(TT_IDENTIFIER:a, TT_EQ, TT_INT:3)"
        )

    def test_parse3(self):
        run_interpreter("var a = 3")
        self.assertEqual(
            run_interpreter("a"),
            "3"
        )

    def test_pars4(self):
        run_interpreter("var a = 3 + 2 * 3 ^ 2")
        self.assertEqual(
            run_interpreter("a"),
            "21.0"
        )

    def test_parse6(self):
        run_interpreter("var a = 3")
        run_interpreter("var a = 3 + 2 * 3 ^ 2")
        self.assertEqual(
            run_interpreter("a"),
            "21.0"
        )

    def test_parse7(self):
        run_interpreter("var a = 3")
        self.assertEqual(
            run_interpreter("a + 8"),
            "11"
        )

    def test_parse8(self):
        run_interpreter("var a = 3")
        run_interpreter("var b = 3 + 2 * 3 ^ 2")
        self.assertEqual(
            run_interpreter("a + b"),
            "24.0"
        )

    def test_parse9(self):
        run_interpreter("var a = var b = var c = 3")
        self.assertEqual(
            run_interpreter("a + b"),
            "6"
        )

    def test_parse10(self):
        self.assertEqual(
            run_interpreter("var a = var b * 3"),
            "Invid Syntax: expected ‘=’, File <basic>, line 1 column 14"
        )

    def test_parse11(self):
        self.assertEqual(
            run_interpreter("5 + var a = 3"),
            "Invid Syntax: Expected int, float, 'if', 'for', 'while', 'fun',  +, -, or (, File <basic>, line 1 column 4"
        )

if __name__ == '__main__':
    unittest.main()
