from basicParser import Parser
from interpreter import Interpreter, Context, SymbolTable, Number
from lexer import Lexer


def run_tokenize(text, filename="<basic>"):
    lexer = Lexer(text, filename)
    tokens, error = lexer.make_tokens()

    if error:
        return error.as_string()
    else:
        texts = [item.as_string() for item in tokens]
        return '[' + ", ".join(texts) + ']'

def run_parser(text, filename="<basic>"):
    lexer = Lexer(text, filename)
    tokens, error = lexer.make_tokens()
    if error: return error.as_string()

    parser = Parser(tokens)
    res = parser.parse()
    return res.error.as_string() if res.error else res.node.as_string()

global_symbol_table = SymbolTable()
global_symbol_table.set("null", Number(0))
def run_interpreter(text, filename="<basic>"):
    lexer = Lexer(text, filename)
    tokens, error = lexer.make_tokens()
    if error: return error.as_string()

    parser = Parser(tokens)
    ast = parser.parse()
    if ast.error: return ast.error.as_string()

    interpreter = Interpreter()
    context = Context("<Program>")
    context.symbol_table = global_symbol_table
    res = interpreter.visit(ast.node, context)
    return res.error.as_string() if res.error else res.value.as_string()