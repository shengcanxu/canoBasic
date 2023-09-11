class Context:
    def __init__(self, display_name, parent=None, parent_entry_pos=None):
        self.display_name = display_name
        self.parent = parent
        self.parent_entry_pos = parent_entry_pos
        self.symbol_table = None

class SymbolTable:
    def __init__(self, parent=None):
        self.symbols = {}
        self.parent = parent

    def get(self, name):
        value = self.symbols.get(name, None)
        if value is None and self.parent is not None:
            return self.parent.get(name)
        return value

    def set(self, name, value):
        self.symbols[name] = value

    def remove(self, name):
        del self.symbols[name]
global_symbol_table = SymbolTable()

global_classes = {}
def run_script(text, filename):
    lexer = global_classes["Lexer"](text, filename)
    tokens, error = lexer.make_tokens()
    if error: return None, error

    # generate AST
    parser = global_classes["Parser"](tokens)
    ast, error = parser.parse()
    if error: return ast, error

    # interpreter
    interpreter = global_classes["Interpreter"]()
    context = Context("<pragram>")
    context.symbol_table = global_symbol_table
    value = interpreter.visit(ast, context)

    return value, interpreter.error