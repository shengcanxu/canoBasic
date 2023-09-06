from lexer import Lexer
from basicParser import Parser
from interpreter import Interpreter, Context, Number, SymbolTable

global_symbol_table = SymbolTable()
global_symbol_table.set("null", Number(0))

def run(text, filename):
    lexer = Lexer(text, filename)
    tokens, error = lexer.make_tokens()
    if error: return None, error

    # generate AST
    parser = Parser(tokens)
    ast = parser.parse()
    if ast.error: return ast.node, ast.error

    # interpreter
    interpreter = Interpreter()
    context = Context("<pragram>")
    context.symbol_table = global_symbol_table
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