import unittest
from test.share import run_tokenize, run_interpreter, run_parser


class TestEP8(unittest.TestCase):
    def test_parse1(self):
        self.assertEqual(
            run_tokenize("fun test(a, b) -> a + b"),
            "[TT_KEYWORD:fun, TT_IDENTIFIER:test, TT_LPAREN, TT_IDENTIFIER:a, TT_COMMA, TT_IDENTIFIER:b, TT_RPAREN, TT_ARROW, TT_IDENTIFIER:a, TT_PLUS, TT_IDENTIFIER:b, TT_EOF]"
        )

    def test_parse2(self):
        self.assertEqual(
            run_parser("fun test(a, b) -> a + b"),
            "(fun TT_IDENTIFIER:test(TT_IDENTIFIER:a, TT_IDENTIFIER:b), (TT_IDENTIFIER:a, TT_PLUS, TT_IDENTIFIER:b))"
        )

    def test_parse3(self):
        run_interpreter("var a = var b = 8")
        run_interpreter("fun test() -> 3 + 4")
        self.assertEqual(
            run_interpreter("test()"),
            "7"
        )

    def test_pars4(self):
        run_interpreter("var a = var b = 8")
        run_interpreter("fun test() -> 3*a + 4*b")
        self.assertEqual(
            run_interpreter("test()"),
            "56"
        )

    def test_pars5(self):
        run_interpreter("var a = var b = 8")
        run_interpreter("fun test2() -> (var a = 10)")
        self.assertEqual(
            run_interpreter("a"),
            "8"
        )
        run_interpreter("var a = 10")
        self.assertEqual(
            run_interpreter("a"),
            "10"
        )

    def test_parse6(self):
        run_interpreter("var a = var b = 8")
        run_interpreter("fun test2(a, b) -> a + b")
        self.assertEqual(
            run_interpreter("test2(3, 4)"),
            "7"
        )
        run_interpreter("fun test3(c, d) -> a + b + c + d")
        self.assertEqual(
            run_interpreter("test3(3, 4)"),
            "23"
        )

    def test_parse7(self):
        run_interpreter("fun test(a, b) -> a + b")
        run_interpreter("fun test2(a, b) -> a + b + test(a*2, b*3)")
        self.assertEqual(
            run_interpreter("test2(3, 4)"),
            "25"
        )
        run_interpreter("fun test3(a) -> a * test2(a, a + 1)")
        self.assertEqual(
            run_interpreter("test3(3)"),
            "75"
        )

    def test_parse8(self):
        run_interpreter("fun test(a, b) -> a + b")
        run_interpreter("fun test2(a, b) -> a + b + test(a*2, b*3)")
        run_interpreter("fun test3(a) -> a * test2(a, a + 1)")
        self.assertEqual(
            run_interpreter("test3( test(1, 2) )"),
            "75"
        )

    def test_parse9(self):
        run_interpreter("var test = fun(a, b) -> a + b")
        self.assertEqual(
            run_interpreter("test(3, 4 )"),
            "7"
        )

    def test_parse10(self):
        self.assertEqual(
            run_parser("fun a, b) -> a + b"),
            "Invalid Syntax: Expected '(', File <basic>, line 1 column 5"
        )
        self.assertEqual(
            run_parser("fun test(a, ) -> a + b"),
            "Invalid Syntax: Expected identifier, File <basic>, line 1 column 12"
        )
        self.assertEqual(
            run_parser("fun test(a, b -> a + b"),
            "Invalid Syntax: Expected ',' or ')', File <basic>, line 1 column 14"
        )
        self.assertEqual(
            run_parser("fun test(a, b)  a + b"),
            "Invalid Syntax: Expected newline or '->', File <basic>, line 1 column 16"
        )
        self.assertEqual(
            run_parser("fun test(a, b) -> "),
            "Invalid Syntax: Invalid token, File <basic>, line 1 column 18"
        )

if __name__ == '__main__':
    unittest.main()
