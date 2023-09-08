from error import InvalidSyntaxError
from nodes import *
from util import global_classes


class ParseResult:
    def __init__(self):
        self.error = None
        self.node = None
        self.advance_count = 0
        self.to_reverse_count = 0

    def register_advance(self):
        self.advance_count += 1

    def register(self, res):
        self.advance_count += res.advance_count
        if res.error: self.error = res.error
        return res.node

    def try_register(self, res):
        if res.error:
            self.to_reverse_count = res.advance_count
            return None
        return self.register(res)

    def check(self, res):
        self.advance_count = 1
        if res.error: self.error = res.error
        return self

    def success(self, node):
        self.node = node
        return self

    def failure(self, error):
        if not self.error or self.advance_count == 0:
            self.error = error
        return self

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.tok_idx = -1
        self.current_tok = None
        self.advance()

    def advance(self):
        self.tok_idx += 1
        self.update_current_tok()
        return self.current_tok

    def reverse(self, amount=1):
        self.tok_idx -= amount
        self.update_current_tok()
        return self.current_tok

    def update_current_tok(self):
        if 0 <= self.tok_idx < len(self.tokens):
            self.current_tok = self.tokens[self.tok_idx]

    def parse(self):
        res = self.statements()
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

        elif tok.type == CONSTANT.STRING:
            res.register_advance()
            self.advance()
            return res.success(StringNode(tok))

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

        elif tok.type == CONSTANT.LSQUARE:
            list_expr = res.register(self.list_expr())
            if res.error: return res
            return res.success(list_expr)

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

        elif tok.matches(CONSTANT.KEYWORD, "fun"):
            while_expr = res.register(self.fun_def())
            if res.error: return res
            return res.success(while_expr)

        return res.failure(InvalidSyntaxError(
            tok.pos_start, tok.pos_end,
            "Expected int, float, 'if', 'for', 'while', 'fun',  +, -, or ("
        ))

    def power(self):
        return self.bin_op(self.call, (CONSTANT.POW), self.factor)

    def call(self):
        res = ParseResult()
        atom = res.register(self.atom())
        if res.error: return res

        if self.current_tok.type == CONSTANT.LPAREN:
            res.register_advance()
            self.advance()

            arg_nodes = []
            if self.current_tok.type == CONSTANT.RPAREN:
                res.register_advance()
                self.advance()
            else:
                arg_nodes.append(res.register(self.expr()))
                if res.error:
                    return res.failure(InvalidSyntaxError(
                        self.current_tok.pos_start, self.current_tok.pos_end,
                        "Expected 'var', 'fun' int, float, identifier, '+', '-', or '('"
                    ))

                while self.current_tok.type == CONSTANT.COMMA:
                    res.register_advance()
                    self.advance()

                    arg_nodes.append(res.register(self.expr()))
                    if res.error: return res

                res.check(self.check_type(CONSTANT.RPAREN, "Expected ',' or ')'"))
                if res.error: return res

            return res.success(CallNode(atom, arg_nodes))

        return res.success(atom)

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
                "Expected int, float, '+', '-', '[', '(' or 'not'"
            ))
        return res.success(node)

    def arith_expr(self):
        return self.bin_op(self.term, (CONSTANT.PLUS, CONSTANT.MINUS))

    def statements(self):
        res = ParseResult()
        statements = []
        pos_start = self.current_tok.pos_start.copy()

        while self.current_tok.type == CONSTANT.NEWLINE:
            res.register_advance()
            self.advance()
        statement = res.register(self.statement())
        if res.error: return res
        statements.append(statement)

        more_statements = True
        while True:
            newline_count = 0
            while self.current_tok.type == CONSTANT.NEWLINE:
                res.register_advance()
                self.advance()
                newline_count += 1
            if newline_count == 0:
                more_statements = False

            if not more_statements: break
            statement = res.try_register(self.statement())
            if statement is None:
                self.reverse(res.to_reverse_count)
                more_statements = False
                continue
            statements.append(statement)

        return res.success(ListNode(
            statements,
            pos_start, self.current_tok.pos_end.copy()
        ))

    def statement(self):
        res = ParseResult()
        pos_start = self.current_tok.pos_start.copy()

        if self.current_tok.matches(CONSTANT.KEYWORD, "return"):
            res.register_advance()
            self.advance()

            expr = res.try_register(self.expr())
            if not expr:
                self.reverse(res.to_reverse_count)
            return res.success(ReturnNode(expr, pos_start, self.current_tok.pos_start.copy()))

        if self.current_tok.matches(CONSTANT.KEYWORD, "continue"):
            res.register_advance()
            self.advance()
            return res.success(ContinueNode(pos_start, self.current_tok.pos_end.copy()))

        if self.current_tok.matches(CONSTANT.KEYWORD, "break"):
            res.register_advance()
            self.advance()
            return res.success(BreakNode(pos_start, self.current_tok.pos_end.copy()))

        expr = res.register(self.expr())
        if res.error:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected 'VAR', 'continue', 'break', 'return', int, float, fun, for, while, identifier, '+', '-', '[' or '('"
            ))
        return res.success(expr)

    def expr(self):  # + and -
        res = ParseResult()
        if self.current_tok.matches(CONSTANT.KEYWORD, "var"):
            res.register_advance()
            self.advance()

            var_name = self.current_tok
            res.check(self.check_type(CONSTANT.IDENTIFIER, "expected identifier!"))
            if res.error: return res

            res.check(self.check_type(CONSTANT.EQ, "expected ‘=’"))
            if res.error: return res

            expr = res.register(self.expr())
            if res.error: return res
            return res.success(VarAssignNode(var_name, expr))

        node = res.register(self.bin_op(self.comp_expr, ((CONSTANT.KEYWORD,"and"), (CONSTANT.KEYWORD,"or"))) )
        if res.error:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected 'VAR', int, float, fun, for, while, identifier, '+', '-', '[' or '('"
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

    def check_keyword(self, keyword):
        res = ParseResult()
        if not self.current_tok.matches(CONSTANT.KEYWORD, keyword):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                f"Expected '{keyword}'"
            ))
        res.register_advance()
        self.advance()
        return res.success(None)

    def check_type(self, node_type, err_msg):
        res = ParseResult()
        if self.current_tok.type != node_type:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                f"{err_msg}"
            ))
        res.register_advance()
        self.advance()
        return res.success(None)

    def if_expr(self):
        res = ParseResult()
        all_cases = res.register(self.if_expr_cases('if'))
        if res.error: return res

        cases, else_case = all_cases
        return res.success(IfNode(cases, else_case))

    def if_expr_cases(self, case_keyword):
        res = ParseResult()
        cases = []
        else_case = None

        res.check(self.check_keyword(case_keyword))
        if res.error: return res

        condition = res.register(self.expr())
        if res.error: return res
        res.check(self.check_keyword("then"))
        if res.error: return res

        if self.current_tok.type == CONSTANT.NEWLINE:
            res.register_advance()
            self.advance()

            statements = res.register(self.statements())
            if res.error: return res
            cases.append((condition, statements, True))

            if self.current_tok.matches(CONSTANT.KEYWORD, "end"):
                res.register_advance()
                self.advance()
            else:
                all_cases = res.register(self.if_expr_elif_or_else())
                if res.error: return res
                new_cases, else_case = all_cases
                cases.extend(new_cases)

        else:
            statement = res.register(self.statement())
            if res.error: return res
            cases.append((condition, statement, False))

            all_calse = res.register(self.if_expr_elif_or_else())
            if res.error: return res
            new_cases, else_case = all_calse
            cases.extend(new_cases)

        return res.success((cases, else_case))

    def if_expr_elif(self):
        return self.if_expr_cases("elif")

    def if_expr_else(self):
        res = ParseResult()
        else_case = None
        if self.current_tok.matches(CONSTANT.KEYWORD, "else"):
            res.register_advance()
            self.advance()

            if self.current_tok.type == CONSTANT.NEWLINE:
                res.register_advance()
                self.advance()

                statements = res.register(self.statements())
                if res.error: return res
                else_case = (statements, True)

                res.check(self.check_keyword("end"))
                if res.error: return res
            else:
                statement = res.register(self.statement())
                if res.error: return res
                else_case = (statement, False)

        return res.success(else_case)

    def if_expr_elif_or_else(self):
        res = ParseResult()
        cases, else_case = [], None

        if self.current_tok.matches(CONSTANT.KEYWORD, "elif"):
            all_cases = res.register(self.if_expr_elif())
            if res.error: return res
            cases, else_case = all_cases
        else:
            else_case = res.register(self.if_expr_else())
            if res.error: return res

        return res.success((cases, else_case))

    def while_expr(self):
        res = ParseResult()
        res.check(self.check_keyword("while"))
        if res.error: return res

        condition = res.register(self.expr())
        if res.error: return res

        res.check(self.check_keyword("then"))
        if res.error: return res

        if self.current_tok.type == CONSTANT.NEWLINE:
            res.register_advance()
            self.advance()

            body_node = res.register(self.statements())
            if res.error: return res

            res.check(self.check_keyword("end"))
            if res.error: return res

            return res.success(WhileNode(condition, body_node, True))

        body_node = res.register(self.statement())
        if res.error: return res

        if condition is None or body_node is None:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "condition or expresstion should not be None",
            ))
        return res.success(WhileNode(condition, body_node, False))

    def for_expr(self):
        res = ParseResult()
        res.check(self.check_keyword("for"))
        if res.error: return res

        var_name_tok = self.current_tok
        res.check(self.check_type(CONSTANT.IDENTIFIER, "Expected identifier"))
        if res.error: return res

        res.check(self.check_type(CONSTANT.EQ, "Expected '='"))
        if res.error: return res

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

        res.check(self.check_keyword("then"))
        if res.error: return res

        if self.current_tok.type == CONSTANT.NEWLINE:
            res.register_advance()
            self.advance()

            body_node = res.register(self.statements())
            if res.error: return res

            res.check(self.check_keyword("end"))
            if res.error: return res

            return res.success(
                ForNode(var_name_tok, start_node, end_node, step_node, body_node, True)
            )

        body_node = res.register(self.statement())
        if res.error: return res
        return res.success(
            ForNode(var_name_tok, start_node, end_node, step_node, body_node, False)
        )

    def fun_def(self):
        res = ParseResult()
        res.check(self.check_keyword("fun"))
        if res.error: return res

        if self.current_tok.type == CONSTANT.IDENTIFIER:
            var_name_tok = self.current_tok
            res.register_advance()
            self.advance()

            res.check(self.check_type(CONSTANT.LPAREN, "Expected '('"))
            if res.error: return res
        else:
            var_name_tok = None
            res.check(self.check_type(CONSTANT.LPAREN, "Expected identifier or '('"))
            if res.error: return res

        arg_name_toks = []
        if self.current_tok.type == CONSTANT.IDENTIFIER:
            arg_name_toks.append(self.current_tok)
            res.register_advance()
            self.advance()

            while self.current_tok.type == CONSTANT.COMMA:
                res.register_advance()
                self.advance()

                tok = self.current_tok
                res.check(self.check_type(CONSTANT.IDENTIFIER, "Expected identifier"))
                if res.error: return res
                arg_name_toks.append(tok)

            res.check(self.check_type(CONSTANT.RPAREN, "Expected ',' or ')'"))
            if res.error: return res

        else:
            res.check(self.check_type(CONSTANT.RPAREN, "Expected identifier or ')'"))
            if res.error: return res

        if self.current_tok.type == CONSTANT.ARROW:
            res.register_advance()
            self.advance()

            body_node = res.register(self.expr())
            if res.error: return res
            return res.success(FunDefNode(var_name_tok, arg_name_toks, body_node, True))

        res.check(self.check_type(CONSTANT.NEWLINE, "Expected newline or '->'"))
        if res.error: return res

        body_node = res.register(self.statements())
        if res.error: return res

        res.check(self.check_keyword("end"))
        if res.error: return res
        return res.success(FunDefNode(var_name_tok, arg_name_toks, body_node, False))

    def list_expr(self):
        res = ParseResult()
        element_nodes = []
        pos_start = self.current_tok.pos_start.copy()

        res.check(self.check_type(CONSTANT.LSQUARE, "Expected '['"))
        if res.error: return res

        if self.current_tok.type == CONSTANT.RSQUARE:
            res.register_advance()
            self.advance()
        else:
            element_nodes.append(res.register(self.expr()))
            if res.error:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected 'var', 'fun' int, float, while, for, fun identifier, '+', '-', '(' or '['"
                ))

            while self.current_tok.type == CONSTANT.COMMA:
                res.register_advance()
                self.advance()

                element_nodes.append(res.register(self.expr()))
                if res.error: return res

            res.check(self.check_type(CONSTANT.RSQUARE, "Expected ',' or ']'"))
            if res.error: return res

        return res.success(
            ListNode( element_nodes, pos_start, self.current_tok.pos_end ))


global_classes["Parser"] = Parser