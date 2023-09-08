import unittest
from test.share import run_tokenize, run_interpreter, run_parser


class TestEP12(unittest.TestCase):
    def test_parse1(self):
        self.assertEqual(
            run_tokenize("1+2; 3+4"),
            "[TT_INT:1, TT_PLUS, TT_INT:2, TT_NEWLINE, TT_INT:3, TT_PLUS, TT_INT:4, TT_EOF]"
        )
        self.assertEqual(
            run_tokenize("1+2\n 3+4"),
            "[TT_INT:1, TT_PLUS, TT_INT:2, TT_NEWLINE, TT_INT:3, TT_PLUS, TT_INT:4, TT_EOF]"
        )
        self.assertEqual(
            run_parser("1+2\n 3+4"),
            "[(TT_INT:1, TT_PLUS, TT_INT:2),(TT_INT:3, TT_PLUS, TT_INT:4)]"
        )

    def test_parse2(self):
        self.assertEqual(
            run_interpreter("\n\n1+2; 3+4\n"),
            "[3,7]"
        )

    def test_parse3(self):
        run_interpreter("var a = var b = 8")
        run_interpreter('if a > b then \nvar a = 2\n var b = 3 \nelif a < b then\n var a = 4; var b = 5 \n\n  else \n var a = 6; var b = 7 \nend')
        self.assertEqual(
            run_interpreter("a"),
            "6"
        )

    def test_pars4(self):
        run_interpreter("var a = var b = 8")
        run_interpreter('while a > 5 then\n var a = a - 1\n var b = b - 1\n end')
        self.assertEqual(
            run_interpreter("b"),
            "5"
        )

    def test_pars5(self):
        run_interpreter("var a = var b = 8")
        run_interpreter('for i = 1 to 5 step 2 then\n var a = a - 1\n var b = b - 1\n end')
        self.assertEqual(
            run_interpreter("b"),
            "6"
        )

    def test_parse6(self):
        run_interpreter("var c = 8")
        run_interpreter('fun test(a, b)\n var c = b\n var b = a\n var a = c\n end')
        self.assertEqual(
            run_interpreter("test(3,5)"),
            "0"
        )

    def test_parse7(self):
        run_interpreter("var a = var b = 8")
        self.assertEqual(
            run_interpreter('for i = 1 to 5 step 2 then\n var a = a - 1\n var b = b - 1'),
            "Invalid Syntax: Expected 'end', File <basic>, line 3 column 14"
        )

if __name__ == '__main__':
    unittest.main()
