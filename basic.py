from lexer import Lexer
from basicParser import Parser
from interpreter import Interpreter, Context


def run(text, filename):
    lexer = Lexer(text, filename)
    tokens, error = lexer.make_tokens()
    if error: return None, error

    # generate AST
    parser = Parser(tokens)
    ast = parser.parse()

    # interpreter
    interpreter = Interpreter()
    context = Context("<pragram>")
    result = interpreter.visit(ast.node, context)

    return result.value, result.error


if __name__ == "__main__":
    while True:
        text = input('basic> ')
        result, error = run(text, "<basic>")

        if error:
            print(error.as_string())
        else:
            print(result)