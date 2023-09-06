from lexer import CONSTANT
from error import InvalidSyntaxError


######################################################
# Nodes
######################################################


class NumberNode:
    def __init__(self, tok):
        self.tok = tok
        self.pos_start = self.tok.pos_start
        self.pos_end = self.tok.pos_end

    def __repr__(self):
        return self.as_string()

    def as_string(self):
        return f'{self.tok}'

class BinOpNode:
    def __init__(self, left_node, op_tok, right_node):
        self.left_node = left_node
        self.op_tok = op_tok
        self.right_node = right_node

        self.pos_start = self.left_node.pos_start
        self.pos_end = self.right_node.pos_end

    def __repr__(self):
        return self.as_string()

    def as_string(self):
        return f'({self.left_node}, {self.op_tok}, {self.right_node})'

class UnaryOpNode:
    def __init__(self, op_tok, node):
        self.op_tok = op_tok
        self.node = node

        self.pos_start = self.op_tok.pos_start
        self.pos_end = self.node.pos_end

    def __repr__(self):
        return self.as_string()

    def as_string(self):
        return f"({self.op_tok}, {self.node})"

class VarAccessNode:
    def __init__(self, var_name_tok):
        self.var_name_tok = var_name_tok
        self.pos_start = self.var_name_tok.pos_start
        self.pos_end = self.var_name_tok.pos_end

    def __repr__(self):
        return self.as_string()

    def as_string(self):
        return f"{self.var_name_tok}"

class VarAssignNode:
    def __init__(self, var_name_tok, value_node):
        self.var_name_tok = var_name_tok
        self.value_node = value_node
        self.pos_start = self.var_name_tok.pos_start
        self.pos_end = self.value_node.pos_end

    def __repr__(self):
        return self.as_string()

    def as_string(self):
        return f"({self.var_name_tok}, {CONSTANT.EQ}, {self.value_node})"

######################################################
# parser result
######################################################

class ParseResult:
    def __init__(self):
        self.error = None
        self.node = None
        self.advance_count = 0

    def register_advance(self):
        self.advance_count += 1

    def register(self, res):
        self.advance_count += res.advance_count
        if res.error: self.error = res.error
        return res.node

    def success(self, node):
        self.node = node
        return self

    def failure(self, error):
        if not self.error or self.advance_count == 0:
            self.error = error
        return self

######################################################
# parser
######################################################

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.tok_idx = -1
        self.current_tok = None
        self.advance()

    def advance(self):
        self.tok_idx += 1
        if self.tok_idx < len(self.tokens):
            self.current_tok = self.tokens[self.tok_idx]
        return self.current_tok

    def parse(self):
        res = self.expr()
        if not res.error and self.current_tok.type != CONSTANT.EOF:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected int or float"
            ))
        return res

    def atom(self):
        res = ParseResult()
        tok = self.current_tok

        if tok.type in (CONSTANT.INT, CONSTANT.FLOAT):
            res.register_advance()
            self.advance()
            return res.success(NumberNode(tok))

        elif tok.type == CONSTANT.IDENTIFIER:
            res.register_advance()
            self.advance()
            return res.success(VarAccessNode(tok))

        elif tok.type == CONSTANT.LPAREN:
            res.register_advance()
            self.advance()
            expr = res.register(self.expr())
            if res.error: return res
            if self.current_tok.type == CONSTANT.RPAREN:
                res.register_advance()
                self.advance()
                return res.success(expr)
            else:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected ')'"
                ))

        return res.failure(InvalidSyntaxError(
            tok.pos_start, tok.pos_end,
            "Expected int, float, +, -, or ("
        ))

    def power(self):
        return self.bin_op(self.atom, (CONSTANT.POW), self.factor)

    def factor(self):
        res = ParseResult()
        tok = self.current_tok

        if tok.type in (CONSTANT.PLUS, CONSTANT.MINUS):
            res.register_advance()
            self.advance()
            factor_res = res.register(self.factor())
            if res.error: return res
            return res.success(UnaryOpNode(tok, factor_res))
        return self.power()

    def term(self):  # * and /
        return self.bin_op(self.factor, (CONSTANT.MUL, CONSTANT.DIV))

    def comp_expr(self):
        res = ParseResult()

        if self.current_tok.matches(CONSTANT.KEYWORD, "not"):
            op_tok = self.current_tok
            res.register_advance()
            self.advance()

            node = res.register(self.comp_expr())
            if res.error: return res
            return res.success(UnaryOpNode(op_tok, node))

        node = res.register(self.bin_op(self.arith_expr,
            (CONSTANT.EE, CONSTANT.NE, CONSTANT.LT, CONSTANT.LTE, CONSTANT.GT, CONSTANT.GTE)
        ))
        if res.error:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected int, float, +, -, ( or 'not'"
            ))
        return res.success(node)

    def arith_expr(self):
        return self.bin_op(self.term, (CONSTANT.PLUS, CONSTANT.MINUS))

    def expr(self):  # + and -
        res = ParseResult()
        if self.current_tok.matches(CONSTANT.KEYWORD, "var"):
            res.register_advance()
            self.advance()
            if self.current_tok.type != CONSTANT.IDENTIFIER:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "expected identifier!"
                ))

            var_name = self.current_tok
            res.register_advance()
            self.advance()
            if self.current_tok.type != CONSTANT.EQ:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "expected ‘=’ "
                ))

            res.register_advance()
            self.advance()
            expr = res.register(self.expr())
            if res.error: return res
            return res.success(VarAssignNode(var_name, expr))

        node = res.register(self.bin_op(self.comp_expr, ((CONSTANT.KEYWORD,"and"), (CONSTANT.KEYWORD,"or"))) )
        if res.error:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected 'VAR', int, float, identifier, '+', '-', or '('"
            ))
        return res.success(node)

    def bin_op(self, func_a, ops, func_b=None):
        if func_b is None:
            func_b = func_a
        res = ParseResult()
        left = res.register(func_a())
        if res.error: return res

        while self.current_tok.type in ops or \
                (type(ops[0]) == tuple and (self.current_tok.type, self.current_tok.value) in ops):
            op_tok = self.current_tok
            res.register_advance()
            self.advance()
            right = res.register(func_b())
            if res.error: return res
            left = BinOpNode(left, op_tok, right)
        return res.success(left)

