import unittest
from test.share import run_tokenize, run_interpreter, run_parser

class TestEP2(unittest.TestCase):
    def test_parse1(self):
        self.assertEqual(
            run_parser("1 + 3"),
            "(1,PLS,3)"
        )

    def test_parse2(self):
        self.assertEqual(
            run_parser("1 +  2 + 3 + 4"),
            "(((1,PLS,2),PLS,3),PLS,4)"
        )

    def test_parse3(self):
        self.assertEqual(
            run_parser("1 3 +"),
            "Invalid Syntax: Expected int or float, File <basic>, line 1 column 2"
        )

    def test_parse4(self):
        self.assertEqual(
            run_parser("-5"),
            "(MIS, 5)"
        )

    def test_parse5(self):
        self.assertEqual(
            run_parser("--5"),
            "(MIS, (MIS, 5))"
        )

    def test_parse6(self):
        self.assertEqual(
            run_parser("1 + 2 *3 "),
            "(1,PLS,(2,MUL,3))"
        )

    def test_parse7(self):
        self.assertEqual(
            run_parser("(2 - 3 ) * 5"),
            "((2,MIS,3),MUL,5)"
        )

    def test_parse8(self):
        self.assertEqual(
            run_parser("1 + (2+3) * 2"),
            "(1,PLS,((2,PLS,3),MUL,2))"
        )

    def test_parse9(self):
        self.assertEqual(
            run_parser("(1+2+3"),
            "Invalid Syntax: Expected ')', File <basic>, line 1 column 6"
        )

    def test_parse10(self):
        self.assertEqual(
            run_parser("1+2)+3"),
            "Invalid Syntax: Expected int or float, File <basic>, line 1 column 3"
        )

if __name__ == '__main__':
    unittest.main()
