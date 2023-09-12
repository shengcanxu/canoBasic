import unittest

from basicParser import Parser
from interpreter import Interpreter, Context
from lexer import Lexer
from test.share import run_tokenize, run_interpreter, run_parser


class TestEP6(unittest.TestCase):
    def test_parse1(self):
        self.assertEqual(
            run_tokenize("if 5 > 3 then true"),
            "[if, 5, GT, 3, then, true, EOF]"
        )

    def test_parse2(self):
        self.assertEqual(
            run_parser("if 5 > 3 then true"),
            "(if (5,GT,3) then true)"
        )

    def test_parse3(self):
        self.assertEqual(
            run_interpreter("if 5 > 3 then 3 + 5"),
            "8"
        )

    def test_pars4(self):
        self.assertEqual(
            run_interpreter("if 5 < 3 then 3 + 5 else 4 + 8"),
            "12"
        )

    def test_pars5(self):
        run_interpreter("var a = 3")
        run_interpreter("var b = 5")
        self.assertEqual(
            run_interpreter("if b > a then b - a else b + a"),
            "2"
        )
        self.assertEqual(
            run_interpreter("if b < a then b - a else b + a"),
            "8"
        )

    def test_parse6(self):
        run_interpreter("var a = if 5 < 3 then 3+5 else 4+8")
        self.assertEqual(
            run_interpreter("a"),
            "12"
        )

    def test_parse7(self):
        run_interpreter("var a = 3")
        run_interpreter("var b = 5")
        run_interpreter("var c = 7")
        self.assertEqual(
            run_interpreter("if a>b and a>c then a elif b>a and b>c then b elif c>a and c>b then c else a+b+c"),
            "7"
        )
        run_interpreter("var c = 5")
        self.assertEqual(
            run_interpreter("if a>b and a>c then a elif b>a and b>c then b elif c>a and c>b then c else a+b+c"),
            "13"
        )

    def test_parse8(self):
        self.assertEqual(
            run_interpreter("if 3 > 5"),
            "Invalid Syntax: Expected 'then', File <basic>, line 1 column 8"
        )
        self.assertEqual(
            run_interpreter("if 3 > 5 else 8"),
            "Invalid Syntax: Expected 'then', File <basic>, line 1 column 9"
        )
        self.assertEqual(
            run_interpreter("if 3 > 5 else 8 elif 7"),
            "Invalid Syntax: Expected 'then', File <basic>, line 1 column 9"
        )

if __name__ == '__main__':
    unittest.main()
