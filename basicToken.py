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
    IDENTIFIER = "ID"
    KEYWORD = "KW"
    STRING = "STR"
    INT = "INT"
    FLOAT = "FLT"
    PLUS = "PLS"
    MINUS = "MIS"
    MUL = "MUL"
    DIV = "DIV"
    POW = "POW"
    LPAREN = "LP"
    RPAREN = "RP"
    LSQUARE = "LS"
    RSQUARE = "RS"
    EQ = "EQ"
    EE = "EE"
    NE = "NE"
    LT = "LT"
    GT = "GT"
    LTE = "LTE"
    GTE = "GTE"
    COMMA = "COM"
    ARROW = "ARW"
    NEWLINE = "NL"
    EOF = "EOF"


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
        if self.value: return f"{self.value}"
        return f"{self.type}"

    def save(self, str_list):
        if self.value: return f"{self.value}"
        return f"{self.type}"