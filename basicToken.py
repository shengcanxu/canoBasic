import string

TT_DIGITS = "0123456789"
TT_LETTERS = string.ascii_letters
TT_LETTERS_DIGITS = TT_LETTERS + TT_DIGITS

KEYWORDS = {
    "var",
    "and",
    "or",
    "not",
    "if",
    "then",
    "else",
    "elif",
    "while",
    "for",
    "to",
    "step",
    "fun",
    "end",
    "return",
    "continue",
    "break"
}

class CONSTANT:
    IDENTIFIER = "TT_IDENTIFIER"
    KEYWORD = "TT_KEYWORD"
    STRING = "TT_STRING"
    INT = "TT_INT"
    FLOAT = "TT_FLOAT"
    PLUS = "TT_PLUS"
    MINUS = "TT_MINUS"
    MUL = "TT_MUL"
    DIV = "TT_DIV"
    POW = "TT_POW"
    LPAREN = "TT_LPAREN"
    RPAREN = "TT_RPAREN"
    LSQUARE = "TT_LSQUARE"
    RSQUARE = "TT_RSQUARE"
    EQ = "TT_EQ"
    EE = "TT_EE"
    NE = "TT_NE"
    LT = "TT_LT"
    GT = "TT_GT"
    LTE = "TT_LTE"
    GTE = "TT_GTE"
    COMMA = "TT_COMMA"
    ARROW = "TT_ARROW"
    NEWLINE = "TT_NEWLINE"
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

    def matches(self, type_, value):
        return self.type == type_ and self.value == value

    def __repr__(self):
        return self.as_string()

    def as_string(self):
        if self.value: return f"{self.type}:{self.value}"
        return f"{self.type}"
