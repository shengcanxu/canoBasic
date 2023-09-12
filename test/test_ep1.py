import unittest
from lexer import Lexer
from test.share import run_tokenize, run_interpreter, run_parser

class TestEP1(unittest.TestCase):
    def test_parse_token1(self):
        self.assertEqual(
            run_tokenize("1 + 3"),
            "[1, PLS, 3, EOF]"
        )

    def test_parse_token2(self):
        self.assertEqual(
            run_tokenize(" 1+3 "),
            "[1, PLS, 3, EOF]"
        )

    def test_parse_token3(self):
        self.assertEqual(
            run_tokenize("(3 + 4)*5"),
            "[LP, 3, PLS, 4, RP, MUL, 5, EOF]"
        )

    def test_parse_token4(self):
        self.assertEqual(
            run_tokenize("23.4"),
            "[23.4, EOF]"
        )

    def test_parse_token5(self):
        self.assertEqual(
            run_tokenize("a%%"),
            "Illegal Character: '%', File <basic>, line 1 column 1"
        )

if __name__ == '__main__':
    unittest.main()
