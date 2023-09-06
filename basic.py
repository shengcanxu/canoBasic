from lexer import Lexer
from basicParser import Parser

def run(text, filename):
    lexer = Lexer(text, filename)
    tokens, error = lexer.make_tokens()
    if error: return None, error

    # generate AST
    parser = Parser(tokens)
    res = parser.parse()

    return res.node, res.error


if __name__ == "__main__":
    while True:
        text = input('basic> ')
        result, error = run(text, "<basic>")

        if error:
            print(error.as_string())
        else:
            print(result)