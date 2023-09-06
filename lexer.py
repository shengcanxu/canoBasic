from error import IllegalCharError, Position

######################################################
# tokens
######################################################
TT_DIGITS = "0123456789"

class CONSTANT:
    INT = "TT_INT"
    FLOAT = "TT_FLOAT"
    PLUS = "TT_PLUS"
    MINUS = "TT_MINUS"
    MUL = "TT_MUL"
    DIV = "TT_DIV"
    LPAREN = "TT_LPAREN"
    RPAREN = "TT_RPAREN"
    EOF = "TT_EOF"


class Token:
    def __init__(self, type_, value=None, pos_start=None, pos_end=None):
        self.type = type_
        self.value = value
        self.pos_start = None
        self.pos_end = None
        if pos_start:
            self.pos_start = pos_start.copy()
            self.pos_end = pos_start.copy()
            self.pos_end.advance()
        if pos_end:
            self.pos_end = pos_end.copy()

    def __repr__(self):
        return self.as_string()

    def as_string(self):
        if self.value: return f"{self.type}:{self.value}"
        return f"{self.type}"


######################################################
# Lexer
######################################################

class Lexer:
    def __init__(self, text, filename):
        self.filename = filename
        self.text = text
        self.pos = Position(-1, 0, -1, filename, text)
        self.current_char = None
        self.advance()

    def advance(self):
        self.pos.advance(self.current_char)
        self.current_char = self.text[self.pos.idx] if self.pos.idx < len(self.text) else None

    def make_tokens(self):
        tokens = []

        while self.current_char is not None:
            if self.current_char in ' \t':
                self.advance()
            elif self.current_char in TT_DIGITS:
                tokens.append(self.make_numbers())
            elif self.current_char == '+':
                tokens.append(Token(CONSTANT.PLUS, pos_start=self.pos))
                self.advance()
            elif self.current_char == '-':
                tokens.append(Token(CONSTANT.MINUS, pos_start=self.pos))
                self.advance()
            elif self.current_char == '*':
                tokens.append(Token(CONSTANT.MUL, pos_start=self.pos))
                self.advance()
            elif self.current_char == '/':
                tokens.append(Token(CONSTANT.DIV, pos_start=self.pos))
                self.advance()
            elif self.current_char == '(':
                tokens.append(Token(CONSTANT.LPAREN, pos_start=self.pos))
                self.advance()
            elif self.current_char == ')':
                tokens.append(Token(CONSTANT.RPAREN, pos_start=self.pos))
                self.advance()
            elif self.current_char == '+':
                tokens.append(Token(CONSTANT.PLUS, pos_start=self.pos))
                self.advance()
            else:
                # return error
                pos_start = self.pos.copy()
                char = self.current_char
                self.advance()
                return [], IllegalCharError(pos_start, self.pos, "'" + char + "'")

        tokens.append(Token(CONSTANT.EOF, pos_start=self.pos))
        return tokens, None

    def make_numbers(self):
        num_str = ''
        dot_count = 0
        pos_start = self.pos.copy()

        DIGITS = TT_DIGITS + '.'
        while self.current_char is not None and self.current_char in DIGITS:
            if self.current_char == '.':
                if dot_count == 1: break
                dot_count += 1
                num_str += '.'
            else:
                num_str += self.current_char
            self.advance()

        if dot_count == 0:
            return Token(CONSTANT.INT, int(num_str), pos_start, self.pos)
        else:
            return Token(CONSTANT.FLOAT, float(num_str), pos_start, self.pos)


