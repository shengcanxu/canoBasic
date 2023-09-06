import unittest
from lexer import Lexer
from test.share import run_tokenize, run_interpreter, run_parser

class TestEP1(unittest.TestCase):
    def run_tokenize(self, text, filename="<basic>"):
        lexer = Lexer(text, filename)
        tokens, error = lexer.make_tokens()

        if error:
            return error.as_string()
        else:
            texts = [item.as_string() for item in tokens]
            return '[' + ", ".join(texts) + ']'

    def test_parse_token1(self):
        self.assertEqual(
            run_tokenize("1 + 3"),
            "[TT_INT:1, TT_PLUS, TT_INT:3, TT_EOF]"
        )

    def test_parse_token2(self):
        self.assertEqual(
            run_tokenize(" 1+3 "),
            "[TT_INT:1, TT_PLUS, TT_INT:3, TT_EOF]"
        )

    def test_parse_token3(self):
        self.assertEqual(
            run_tokenize("(3 + 4)*5"),
            "[TT_LPAREN, TT_INT:3, TT_PLUS, TT_INT:4, TT_RPAREN, TT_MUL, TT_INT:5, TT_EOF]"
        )

    def test_parse_token4(self):
        self.assertEqual(
            run_tokenize("23.4"),
            "[TT_FLOAT:23.4, TT_EOF]"
        )

    def test_parse_token5(self):
        self.assertEqual(
            run_tokenize("a%%"),
            "Illegal Character: '%', File <basic>, line 1 column 1"
        )

if __name__ == '__main__':
    unittest.main()
