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

class IfNode:
    def __init__(self, cases, else_case=None):
        self.cases = cases
        self.else_case = else_case
        self.pos_start = self.cases[0][0].pos_start
        self.pos_end = (self.else_case or self.cases[len(self.cases) - 1][0]).pos_end

    def __repr__(self):
        return self.as_string()

    def as_string(self):
        text = ""
        for case in self.cases:
            text += f"(if {case[0]} then {case[1]})"
        if self.else_case is not None:
            text = f"({text} else {self.else_case}"
        elif len(self.cases) > 1:
            text = f"({text})"
        return text

class whileNode:
    def __init__(self, condition, body_node):
        self.condition = condition
        self.body_node = body_node
        self.pos_start = self.condition.pos_start
        self.pos_end = self.body_node.pos_end

    def __repr__(self):
        return self.as_string()

    def as_string(self):
        return f"(while {self.condition} then {self.body_node})"

class forNode:
    def __init__(self, var_name_tok, start_node, end_node, step_node, body_node):
        self.var_name_tok = var_name_tok
        self.start_node = start_node
        self.end_node = end_node
        self.step_node = step_node
        self.body_node = body_node
        self.pos_start = self.var_name_tok.pos_start
        self.pos_end = self.body_node.pos_end

    def __repr__(self):
        return self.as_string()

    def as_string(self):
        step_text = "" if self.step_node is None else f"step {self.step_node}"
        return f"(for {self.var_name_tok} = {self.start_node} to {self.end_node} {step_text} then {self.body_node})"

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

        elif tok.matches(CONSTANT.KEYWORD, "if"):
            if_expr = res.register(self.if_expr())
            if res.error: return res
            return res.success(if_expr)

        elif tok.matches(CONSTANT.KEYWORD, "for"):
            for_expr = res.register(self.for_expr())
            if res.error: return res
            return res.success(for_expr)

        elif tok.matches(CONSTANT.KEYWORD, "while"):
            while_expr = res.register(self.while_expr())
            if res.error: return res
            return res.success(while_expr)

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

    def if_expr(self):
        res = ParseResult()
        cases = []
        else_case = None

        if not self.current_tok.matches(CONSTANT.KEYWORD, "if"):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected 'if'"
            ))
        res.register_advance()
        self.advance()

        condition = res.register(self.expr())
        if res.error: return res

        if not self.current_tok.matches(CONSTANT.KEYWORD, "then"):
            return  res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected 'then'"
            ))
        res.register_advance()
        self.advance()

        expr = res.register(self.expr())
        if res.error: return res
        cases.append((condition, expr))

        # matching many elif
        while self.current_tok.matches(CONSTANT.KEYWORD, "elif"):
            res.register_advance()
            self.advance()

            condition = res.register(self.expr())
            if res.error: return res

            if not self.current_tok.matches(CONSTANT.KEYWORD, "then"):
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected 'then'"
                ))
            res.register_advance()
            self.advance()

            expr = res.register(self.expr())
            if res.error: return res
            cases.append((condition, expr))

        if self.current_tok.matches(CONSTANT.KEYWORD, "else"):
            res.register_advance()
            self.advance()
            else_case = res.register(self.expr())
            if res.error: return res

        return res.success(IfNode(cases, else_case))

    def while_expr(self):
        res = ParseResult()
        if not self.current_tok.matches(CONSTANT.KEYWORD, "while"):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected 'while'"
            ))
        res.register_advance()
        self.advance()

        condition = res.register(self.expr())
        if res.error: return res

        if not self.current_tok.matches(CONSTANT.KEYWORD, "then"):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected 'then'"
            ))
        res.register_advance()
        self.advance()

        expr = res.register(self.expr())
        if res.error: return res

        if condition is None or expr is None:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "condition or expresstion should not be None",
            ))
        return res.success(whileNode(condition, expr))

    def for_expr(self):
        res = ParseResult()
        step_expr = None

        if not self.current_tok.matches(CONSTANT.KEYWORD, "for"):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected 'for'"
            ))
        res.register_advance()
        self.advance()

        if self.current_tok.type != CONSTANT.IDENTIFIER:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected identifier"
            ))
        var_name_tok = self.current_tok
        res.register_advance()
        self.advance()
        if self.current_tok.type != CONSTANT.EQ:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected '='"
            ))
        res.register_advance()
        self.advance()

        start_node = res.register(self.expr())
        if res.error: return res
        if self.current_tok.type != CONSTANT.KEYWORD or self.current_tok.value != 'to':
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected 'to'"
            ))
        res.register_advance()
        self.advance()
        end_node = res.register(self.expr())
        if res.error: return res

        step_node = None
        if self.current_tok.type == CONSTANT.KEYWORD and self.current_tok.value == 'step':
            res.register_advance()
            self.advance()
            step_node = res.register(self.expr())
            if res.error: return res

        if not self.current_tok.matches(CONSTANT.KEYWORD, "then"):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected 'then'"
            ))
        res.register_advance()
        self.advance()
        body_node = res.register(self.expr())
        if res.error: return res

        return res.success(forNode(var_name_tok, start_node, end_node, step_node, body_node))
