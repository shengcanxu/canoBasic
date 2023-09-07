from basicParser import Parser
from interpreter import Interpreter, Context, SymbolTable, Number, BuiltInFunction
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
global_symbol_table.set("null", Number.null)
global_symbol_table.set("true", Number.true)
global_symbol_table.set("false", Number.false)
global_symbol_table.set("PI", Number.PI)

global_symbol_table.set("print", BuiltInFunction.print)
global_symbol_table.set("print_ret", BuiltInFunction.print_ret)
global_symbol_table.set("input", BuiltInFunction.input)
global_symbol_table.set("input_int", BuiltInFunction.input_int)
global_symbol_table.set("clear", BuiltInFunction.clear)
global_symbol_table.set("is_number", BuiltInFunction.is_number)
global_symbol_table.set("is_string", BuiltInFunction.is_string)
global_symbol_table.set("is_list", BuiltInFunction.is_list)
global_symbol_table.set("is_function", BuiltInFunction.is_function)
global_symbol_table.set("append", BuiltInFunction.append)
global_symbol_table.set("pop", BuiltInFunction.pop)
global_symbol_table.set("extend", BuiltInFunction.extend)

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