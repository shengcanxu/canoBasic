class Error:
    def __init__(self, pos_start, pos_end, error_name, details):
        self.pos_start = pos_start
        self.pos_end = pos_end
        self.error_name = error_name
        self.details = details

    def as_string(self):
        result = f'{self.error_name}: {self.details}'
        result += f', File {self.pos_start.filename}, line {self.pos_start.ln+1} column {self.pos_start.col}'
        return result

class IllegalCharError(Error):
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, 'Illegal Character', details)

class InvalidSyntaxError(Error):
    def __init__(self, pos_start, pos_end, details=""):
        super().__init__(pos_start, pos_end, "Invid Syntax", details)

class ExpectedCharError(Error):
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, "Expected Character: ", details)

class RTError(Error):
    def __init__(self, pos_start, pos_end, details, context):
        super().__init__(pos_start, pos_end, "Runtime Error", details)
        self.context = context

    def as_string(self):
        result = self.generate_traceback()
        result += f'{self.error_name}: {self.details}'
        result += f', File {self.pos_start.filename}, line {self.pos_start.ln+1} column {self.pos_start.col}'
        return result

    def generate_traceback(self):
        result = ""
        pos = self.pos_start
        ctx = self.context

        while ctx:
            result = f' File {pos.filename}, line {str(pos.ln+1)}, in {ctx.display_name}\n'
            pos = ctx.parent_entry_pos
            ctx = ctx.parent
        return 'Traceback: \n' + result

class Position:
    def __init__(self, idx, ln, col, filename=None, text=None):
        self.idx = idx
        self.ln = ln
        self.col = col
        self.filename = filename
        self.text = text

    def advance(self, current_char=None):
        self.idx += 1
        self.col += 1

        if current_char == '\n':
            self.ln += 1
            self.col = 0
        return self

    def copy(self):
        return Position(self.idx, self.ln, self.col, self.filename, self.text)
