from lexer import Lexer
from basicParser import Parser
from interpreter import Interpreter, Context, Number, SymbolTable, BuiltInFunction

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
        elif result:
            if len(result.elements) == 1:
                print(result.elements[0])
            else:
                print(result)