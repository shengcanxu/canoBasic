import unittest

from basicParser import Parser
from interpreter import Interpreter, Context
from lexer import Lexer
from test.share import run_tokenize, run_interpreter, run_parser


class TestEP7(unittest.TestCase):
    def test_parse1(self):
        self.assertEqual(
            run_tokenize("fun test(a, b) -> a + b"),
            "[TT_KEYWORD:fun, TT_IDENTIFIER:test, TT_LPAREN, TT_IDENTIFIER:a, TT_COMMA, TT_IDENTIFIER:b, TT_RPAREN, TT_ARROW, TT_IDENTIFIER:a, TT_PLUS, TT_IDENTIFIER:b, TT_EOF]"
        )

    def test_parse2(self):
        self.assertEqual(
            run_parser("fun test(a, b) -> a + b"),
            "(while (TT_IDENTIFIER:a, TT_GT, TT_INT:5) then (TT_IDENTIFIER:a, TT_EQ, (TT_IDENTIFIER:a, TT_PLUS, TT_INT:1)))"
        )

    def test_parse3(self):
        run_interpreter("var a = 8")
        run_interpreter("while a>5 then var a = a - 1")
        self.assertEqual(
            run_interpreter("a"),
            "5"
        )

    def test_pars4(self):
        run_interpreter("var a = var b = 8")
        run_interpreter("for i=1 to 5 then var a = a - 1")
        run_interpreter("for i=6 to 1 step -2 then var b = b - 1")
        self.assertEqual(
            run_interpreter("a"),
            "4"
        )
        self.assertEqual(
            run_interpreter("b"),
            "5"
        )

    def test_pars5(self):
        self.assertEqual(
            run_parser("for 1 to 5 then var a = a - 1"),
            "Invid Syntax: Expected identifier, File <basic>, line 1 column 4"
        )
        self.assertEqual(
            run_parser("for a 1 to 3 then var a = a - 1"),
            "Invid Syntax: Expected '=', File <basic>, line 1 column 6"
        )
        self.assertEqual(
            run_parser("for a = 1 then var a = a - 1"),
            "Invid Syntax: Expected 'to', File <basic>, line 1 column 10"
        )
        self.assertEqual(
            run_parser("for a = 1 to 3  var a = a - 1"),
            "Invid Syntax: Expected 'then', File <basic>, line 1 column 16"
        )

    def test_parse6(self):
        self.assertEqual(
            run_interpreter("while a>5 var a = a - 1"),
            "Invid Syntax: Expected 'then', File <basic>, line 1 column 10"
        )

    def test_parse7(self):
        run_interpreter("var a = var b = 8")
        run_interpreter("for i=6 to 1 step -2 then if b >= 6 then var b = b-2 else var b = b-1 ")
        self.assertEqual(
            run_interpreter("b"),
            "3"
        )

    def test_parse8(self):
        run_interpreter("var a = var b = 8")
        run_interpreter("while b >= 5 then if b >= 6 then var b = b-1 else var b = b-2 ")
        self.assertEqual(
            run_interpreter("b"),
            "3"
        )

if __name__ == '__main__':
    unittest.main()
