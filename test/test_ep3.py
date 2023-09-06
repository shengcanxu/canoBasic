import unittest

from basicParser import Parser
from interpreter import Interpreter, Context
from lexer import Lexer

class TestInterpreter(unittest.TestCase):
    def run_interpreter(self, text, filename="<basic>"):
        lexer = Lexer(text, filename)
        tokens, error = lexer.make_tokens()
        if error: return error.as_string()

        parser = Parser(tokens)
        ast = parser.parse()

        interpreter = Interpreter()
        context = Context("<Program>")
        res = interpreter.visit(ast.node, context)
        return res.error.as_string() if res.error else res.value.as_string()

    def test_parse1(self):
        self.assertEqual(
            self.run_interpreter("1 + 3"),
            "4"
        )

    def test_parse2(self):
        self.assertEqual(
            self.run_interpreter("1 +  2 + 3 + 4"),
            "10"
        )

    def test_parse3(self):
        self.assertEqual(
            self.run_interpreter("10 - 6 / 3"),
            "8.0"
        )

    def test_parse6(self):
        self.assertEqual(
            self.run_interpreter("-1 + 2 *3 "),
            "5"
        )

    def test_parse7(self):
        self.assertEqual(
            self.run_interpreter("(2 - 3 ) * 5"),
            "-5"
        )

    def test_parse8(self):
        self.assertEqual(
            self.run_interpreter("1 + (2+3) * (-2)"),
            "-9"
        )

    def test_parse9(self):
        self.assertEqual(
            self.run_interpreter("3.2*1.3/2.0-3+5"),
            "4.08"
        )

    def test_parse10(self):
        self.assertEqual(
            self.run_interpreter("10/0"),
            "Traceback: \n" +
            " File <basic>, line 1, in <Program>\n" +
            "Runtime Error: Division by zero, File <basic>, line 1 column 3"
        )

if __name__ == '__main__':
    unittest.main()
