import unittest

from basicParser import Parser
from lexer import Lexer

class TestParser(unittest.TestCase):
    def run_parser(self, text, filename="<basic>"):
        lexer = Lexer(text, filename)
        tokens, error = lexer.make_tokens()
        if error: return error.as_string()

        parser = Parser(tokens)
        res = parser.parse()
        return res.error.as_string() if res.error else res.node.as_string()

    def test_parse1(self):
        self.assertEqual(
            self.run_parser("1 + 3"),
            "(TT_INT:1, TT_PLUS, TT_INT:3)"
        )

    def test_parse2(self):
        self.assertEqual(
            self.run_parser("1 +  2 + 3 + 4"),
            "(((TT_INT:1, TT_PLUS, TT_INT:2), TT_PLUS, TT_INT:3), TT_PLUS, TT_INT:4)"
        )

    def test_parse3(self):
        self.assertEqual(
            self.run_parser("1 3 +"),
            "Invid Syntax: Expected int for float, File <basic>, line 1 column 2"
        )

    def test_parse4(self):
        self.assertEqual(
            self.run_parser("-5"),
            "(TT_MINUS, TT_INT:5)"
        )

    def test_parse5(self):
        self.assertEqual(
            self.run_parser("--5"),
            "(TT_MINUS, (TT_MINUS, TT_INT:5))"
        )

    def test_parse6(self):
        self.assertEqual(
            self.run_parser("1 + 2 *3 "),
            "(TT_INT:1, TT_PLUS, (TT_INT:2, TT_MUL, TT_INT:3))"
        )

    def test_parse7(self):
        self.assertEqual(
            self.run_parser("(2 - 3 ) * 5"),
            "((TT_INT:2, TT_MINUS, TT_INT:3), TT_MUL, TT_INT:5)"
        )

    def test_parse8(self):
        self.assertEqual(
            self.run_parser("1 + (2+3) * 2"),
            "(TT_INT:1, TT_PLUS, ((TT_INT:2, TT_PLUS, TT_INT:3), TT_MUL, TT_INT:2))"
        )

    def test_parse9(self):
        self.assertEqual(
            self.run_parser("(1+2+3"),
            "Invid Syntax: Expected ')', File <basic>, line 1 column 6"
        )

    def test_parse10(self):
        self.assertEqual(
            self.run_parser("1+2)+3"),
            "Invid Syntax: Expected int for float, File <basic>, line 1 column 3"
        )

if __name__ == '__main__':
    unittest.main()
