import unittest
from test.share import run_tokenize, run_interpreter, run_parser


class TestEP12(unittest.TestCase):
    def test_parse1(self):
        self.assertEqual(
            run_tokenize("print"),
            "[TT_IDENTIFIER:print, TT_EOF]"
        )
        self.assertEqual(
            run_parser("print"),
            "TT_IDENTIFIER:print"
        )

    def test_parse2(self):
        self.assertEqual(
            run_interpreter('PI'),
            "3.141592653589793"
        )
        self.assertEqual(
            run_interpreter('true'),
            "1"
        )
        self.assertEqual(
            run_interpreter('false'),
            "0"
        )
        self.assertEqual(
            run_interpreter('null'),
            "0"
        )

    def test_parse3(self):
        self.assertEqual(
            run_interpreter('is_number("abc")'),
            "0"
        )
        self.assertEqual(
            run_interpreter('is_number(3)'),
            "1"
        )

    def test_pars4(self):
        self.assertEqual(
            run_interpreter('is_number("abc")'),
            "0"
        )
        self.assertEqual(
            run_interpreter('is_number(3)'),
            "1"
        )

    def test_pars5(self):
        run_interpreter("fun test() -> 1 + 2")
        self.assertEqual(
            run_interpreter('is_function(test)'),
            "1"
        )
        self.assertEqual(
            run_interpreter('is_function(3)'),
            "0"
        )

    def test_parse6(self):
        run_interpreter("var a = [1,2,3]")
        self.assertEqual(
            run_interpreter('is_list(a)'),
            "1"
        )
        self.assertEqual(
            run_interpreter('is_list(3)'),
            "0"
        )

    def test_parse7(self):
        run_interpreter("var a = [1, 2, 3, 4]")
        run_interpreter("append(a, 5)")
        self.assertEqual(
            run_interpreter("a"),
            "[1,2,3,4,5]"
        )

    def test_parse8(self):
        run_interpreter("var a = [1, 2, 3, 4]")
        run_interpreter("pop(a, 2)")
        self.assertEqual(
            run_interpreter("a"),
            "[1,2,4]"
        )

    def test_parse9(self):
        run_interpreter("var a = [1, 2, 3, 4]")
        run_interpreter("extend(a, [5,6])")
        self.assertEqual(
            run_interpreter("a"),
            "[1,2,3,4,5,6]"
        )

if __name__ == '__main__':
    unittest.main()
