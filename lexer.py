from error import IllegalCharError, Position, ExpectedCharError
from basicToken import Token, CONSTANT, TT_DIGITS, TT_LETTERS, TT_LETTERS_DIGITS, KEYWORDS
from util import global_classes


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
            elif self.current_char == '#':
                self.skip_comment()
            elif self.current_char in ';\n':
                tokens.append(Token(CONSTANT.NEWLINE, pos_start=self.pos))
                self.advance()
            elif self.current_char in TT_DIGITS:
                tokens.append(self.make_numbers())
            elif self.current_char in TT_LETTERS:
                tokens.append(self.make_identify())
            elif self.current_char == '"':
                tokens.append(self.make_strings())
            elif self.current_char == '+':
                tokens.append(Token(CONSTANT.PLUS, pos_start=self.pos))
                self.advance()
            elif self.current_char == '-':
                tokens.append(self.make_minus_or_arrow())
            elif self.current_char == '*':
                tokens.append(Token(CONSTANT.MUL, pos_start=self.pos))
                self.advance()
            elif self.current_char == '/':
                tokens.append(Token(CONSTANT.DIV, pos_start=self.pos))
                self.advance()
            elif self.current_char == '^':
                tokens.append(Token(CONSTANT.POW, pos_start=self.pos))
                self.advance()
            elif self.current_char == '(':
                tokens.append(Token(CONSTANT.LPAREN, pos_start=self.pos))
                self.advance()
            elif self.current_char == ')':
                tokens.append(Token(CONSTANT.RPAREN, pos_start=self.pos))
                self.advance()
            elif self.current_char == '[':
                tokens.append(Token(CONSTANT.LSQUARE, pos_start=self.pos))
                self.advance()
            elif self.current_char == ']':
                tokens.append(Token(CONSTANT.RSQUARE, pos_start=self.pos))
                self.advance()
            elif self.current_char == ',':
                tokens.append(Token(CONSTANT.COMMA, pos_start=self.pos))
                self.advance()
            elif self.current_char == '=':
                tok, error = self.make_equal()
                if error: return [], error
                tokens.append(tok)
            elif self.current_char == '!':
                tok, error = self.make_not_equal()
                if error: return [], error
                tokens.append(tok)
            elif self.current_char == '<':
                tok, error = self.make_less_than()
                if error: return [], error
                tokens.append(tok)
            elif self.current_char == '>':
                tok, error = self.make_great_than()
                if error: return [], error
                tokens.append(tok)
            else:
                # return error
                pos_start = self.pos.copy()
                char = self.current_char
                self.advance()
                return [], IllegalCharError(pos_start, self.pos, "'" + char + "'")

        tokens.append(Token(CONSTANT.EOF, pos_start=self.pos))
        return tokens, None

    def skip_comment(self):
        self.advance()
        while self.current_char != '\n':
            self.advance()
        self.advance()

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

    def make_identify(self):
        id_str = ''
        pos_start = self.pos.copy()

        valid_letters = TT_LETTERS_DIGITS + "_"
        while self.current_char is not None and self.current_char in valid_letters:
            id_str += self.current_char
            self.advance()

        tok_type = CONSTANT.KEYWORD if id_str in KEYWORDS else CONSTANT.IDENTIFIER
        return Token(tok_type, id_str, pos_start, self.pos)

    def make_strings(self):
        string = ''
        pos_start = self.pos.copy()
        escape_character = False
        self.advance()

        escape_characters = {
            'n': '\n',
            't': '\t'
        }
        while self.current_char is not None and (self.current_char != '"' or escape_character):
            if escape_character:
                string += escape_characters.get(self.current_char, self.current_char)
            else:
                if self.current_char == "\\":
                    escape_character = True
                else:
                    string += self.current_char
            self.advance()
            escape_character = False

        self.advance()
        return Token(CONSTANT.STRING, string, pos_start, self.pos)

    def make_minus_or_arrow(self):
        tok_type = CONSTANT.MINUS
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == ">":
            tok_type = CONSTANT.ARROW
            self.advance()
        return Token(tok_type, pos_start=pos_start, pos_end=self.pos)

    def make_not_equal(self):
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == '=':
            self.advance()
            return Token(CONSTANT.NE, pos_start=pos_start, pos_end=self.pos), None
        self.advance()
        return None,  ExpectedCharError(pos_start, self.pos, "'=' (after '!')")

    def make_equal(self):
        tok_type = CONSTANT.EQ
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == '=':
            self.advance()
            tok_type = CONSTANT.EE
        return Token(tok_type, pos_start=pos_start, pos_end=self.pos), None

    def make_less_than(self):
        tok_type = CONSTANT.LT
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == '=':
            self.advance()
            tok_type = CONSTANT.LTE
        return Token(tok_type, pos_start=pos_start, pos_end=self.pos), None

    def make_great_than(self):
        tok_type = CONSTANT.GT
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == '=':
            self.advance()
            tok_type = CONSTANT.GTE
        return Token(tok_type, pos_start=pos_start, pos_end=self.pos), None


global_classes["Lexer"] = Lexer