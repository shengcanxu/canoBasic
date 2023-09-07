import unittest
from test.share import run_tokenize, run_interpreter, run_parser


class TestEP10(unittest.TestCase):
    def test_parse1(self):
        self.assertEqual(
            run_tokenize("[1,2,3,4]"),
            "[TT_LSQUARE, TT_INT:1, TT_COMMA, TT_INT:2, TT_COMMA, TT_INT:3, TT_COMMA, TT_INT:4, TT_RSQUARE, TT_EOF]"
        )

    def test_parse2(self):
        self.assertEqual(
            run_parser("[1,2,3,4]"),
            "[TT_INT:1,TT_INT:2,TT_INT:3,TT_INT:4]"
        )

    def test_parse3(self):
        run_interpreter("var a = [1, 2, 3, 4]")
        self.assertEqual(
            run_interpreter("a"),
            "[1,2,3,4]"
        )

    def test_pars4(self):
        run_interpreter("var a = [1, 2, 3, 4]")
        run_interpreter("var b = a + 5")
        self.assertEqual(
            run_interpreter("b"),
            "[1,2,3,4,5]"
        )

    def test_pars5(self):
        run_interpreter("var a = [1, 2, 3, 4]")
        run_interpreter("var b = a * [5, 6]")
        self.assertEqual(
            run_interpreter("b"),
            "[1,2,3,4,5,6]"
        )

    def test_parse6(self):
        run_interpreter("var a = [1, 2, 3, 4]")
        run_interpreter("var b = a / 0")
        self.assertEqual(
            run_interpreter("b"),
            "1"
        )
        self.assertEqual(
            run_interpreter("var b = a / 5"),
            "Traceback: \n" +
            " File <basic>, line 1, in <Program>\n" +
            "Runtime Error: remove fails because index is not in the list, File <basic>, line 1 column 12"
        )

    def test_parse7(self):
        run_interpreter("var a = [1, 2, 3, 4]")
        run_interpreter("var b = a - 2")
        self.assertEqual(
            run_interpreter("b"),
            "[1,2,4]"
        )

    def test_parse8(self):
        self.assertEqual(
            run_interpreter("for i=1 to 9 then 2 ^ i"),
            "[2.0,4.0,8.0,16.0,32.0,64.0,128.0,256.0]"
        )
        run_interpreter("var a = 5")
        self.assertEqual(
            run_interpreter("while a >= 0 then var a = a - 1"),
            "[4,3,2,1,0,-1]"
        )

    def test_parse9(self):
        self.assertEqual(
            run_parser("[1, 2  3, 4]"),
            "Invid Syntax: Expected ',' or ']', File <basic>, line 1 column 7"
        )
        self.assertEqual(
            run_parser("[1, 2, "),
            "Invid Syntax: Expected 'VAR', int, float, fun, for, while, identifier, '+', '-', '[' or '(', File <basic>, line 1 column 7"
        )
        self.assertEqual(
            run_parser("[1, 2, 3, 4"),
            "Invid Syntax: Expected ',' or ']', File <basic>, line 1 column 11"
        )

if __name__ == '__main__':
    unittest.main()
