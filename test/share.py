from basicParser import Parser
from interpreter import Interpreter, Context, SymbolTable, Number, BuiltInFunction
from lexer import Lexer
from nodes import archieve_nodes, restore_nodes


def run_tokenize(text, filename="<basic>"):
    lexer = Lexer(text, filename)
    tokens, error = lexer.make_tokens()

    if error:
        return repr(error)
    else:
        texts = [repr(item) for item in tokens]
        return '[' + ", ".join(texts) + ']'

def run_parser(text, filename="<basic>"):
    lexer = Lexer(text, filename)
    tokens, error = lexer.make_tokens()
    if error: return repr(error)

    parser = Parser(tokens)
    ast, error = parser.parse()

    if error:
        return repr(error)
    elif ast is not None:
        if len(ast.element_nodes) == 1:
            return repr(ast.element_nodes[0])
        else:
            return repr(ast)

def run_save(text, filepath):
    lexer = Lexer(text, "<basic>")
    tokens, error = lexer.make_tokens()
    if error: return repr(error)

    parser = Parser(tokens)
    ast, error = parser.parse()
    if error:
        return repr(error)
    else:
        text, _ = archieve_nodes(ast, filepath)
        return text

def run_restore(filepath):
    ast = restore_nodes(filepath)

    interpreter = Interpreter()
    context = Context("<Program>")
    context.symbol_table = global_symbol_table
    value = interpreter.visit(ast, context)

    if interpreter.error:
        return repr(interpreter.error)
    elif value:
        if len(value.elements) == 1:
            return repr(value.elements[0])
        else:
            return repr(value)

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
global_symbol_table.set("len", BuiltInFunction.len)
global_symbol_table.set("run", BuiltInFunction.run)

def run_interpreter(text, filename="<basic>"):
    lexer = Lexer(text, filename)
    tokens, error = lexer.make_tokens()
    if error: return repr(error)

    parser = Parser(tokens)
    ast,error = parser.parse()
    if error: return repr(error)

    interpreter = Interpreter()
    context = Context("<Program>")
    context.symbol_table = global_symbol_table
    value = interpreter.visit(ast, context)

    if interpreter.error:
        return repr(interpreter.error)
    elif value:
        if len(value.elements) == 1:
            return repr(value.elements[0])
        else:
            return repr(value)