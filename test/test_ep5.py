import unittest

from basicParser import Parser
from interpreter import Interpreter, Context
from lexer import Lexer
from test.share import run_tokenize, run_interpreter, run_parser


class TestEP4(unittest.TestCase):
    def test_parse1(self):
        self.assertEqual(
            run_tokenize("3 > 2 and 5 <= 6"),
            "[TT_INT:3, TT_GT, TT_INT:2, TT_KEYWORD:and, TT_INT:5, TT_LTE, TT_INT:6, TT_EOF]"
        )

    def test_parse2(self):
        self.assertEqual(
            run_parser("3 > 2 and 5 <= 6"),
            "((TT_INT:3, TT_GT, TT_INT:2), TT_KEYWORD:and, (TT_INT:5, TT_LTE, TT_INT:6))"
        )

    def test_parse3(self):
        self.assertEqual(
            run_parser("3 ! 6"),
            "Expected Character: : '=' (after '!'), File <basic>, line 1 column 2"
        )

    def test_pars4(self):
        self.assertEqual(
            run_interpreter("5 == 5"),
            "1"
        )

    def test_pars5(self):
        self.assertEqual(
            run_interpreter("3 <= 4 and 5 >= 4"),
            "1"
        )

    def test_parse6(self):
        self.assertEqual(
            run_interpreter("3 > 4 or 2 < 4"),
            "1"
        )

    def test_parse7(self):
        run_interpreter("var a = 3")
        run_interpreter("var b = 5")
        self.assertEqual(
            run_interpreter("a <= 8 and b >= 5 and a < b"),
            "1"
        )

    def test_parse8(self):
        run_interpreter("var a = 3")
        run_interpreter("var b = 5")
        self.assertEqual(
            run_interpreter("a > 5 or b > 8 or a > b or a + 3 > b"),
            "1"
        )

    def test_parse9(self):
        run_interpreter("var a = 3")
        run_interpreter("var b = 5")
        self.assertEqual(
            run_interpreter("(a > 2 and b > 6) or ((a < 10) and (b < 10))"),
            "1"
        )

    def test_parse10(self):
        run_interpreter("var a = 3")
        run_interpreter("var b = 5")
        self.assertEqual(
            run_interpreter("a != b and b != a and a + 6 > b"),
            "1"
        )

    def test_parse11(self):
        run_interpreter("var a = 3")
        run_interpreter("var b = 5")
        self.assertEqual(
            run_interpreter("b > 4 > a"),  # b>4 => 0
            "0"
        )

    def test_parse12(self):
        self.assertEqual(
            run_interpreter("not 3 > 5"),  # b>4 => 0
            "1"
        )

if __name__ == '__main__':
    unittest.main()
