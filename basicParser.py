from error import InvalidSyntaxError
from nodes import *
from util import global_classes

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.tok_idx = -1
        self.pre_idx = -1
        self.current_tok = None
        self.advance()
        self.error = None

    def advance(self):
        self.tok_idx += 1
        self._update_current_tok()
        return self.current_tok

    def advance_step(self, value=None):
        self.pre_idx = self.tok_idx
        return value

    def reverse(self):
        self.tok_idx = self.pre_idx
        self._update_current_tok()
        return self.current_tok

    def _update_current_tok(self):
        if 0 <= self.tok_idx < len(self.tokens):
            self.current_tok = self.tokens[self.tok_idx]

    def check_keyword(self, keyword):
        if not self.current_tok.matches(CONSTANT.KEYWORD, keyword):
            self.error = InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                f"Expected '{keyword}'"
            )
            return None
        self.advance()
        return None

    def check_type(self, node_type, err_msg):
        if self.current_tok.type != node_type:
            self.error = InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                f"{err_msg}"
            )
        self.advance()

    def parse(self):
        res = self.statements()
        if self.error is not None:
            return None, self.error
        elif self.current_tok.type != CONSTANT.EOF:
            return None, InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected int or float"
            )
        return res, None

    def atom(self):
        tok = self.current_tok
        if tok.type in (CONSTANT.INT, CONSTANT.FLOAT):
            self.advance()
            return NumberNode(tok)

        elif tok.type == CONSTANT.STRING:
            self.advance()
            return StringNode(tok)

        elif tok.type == CONSTANT.IDENTIFIER:
            self.advance()
            return VarAccessNode(tok)

        elif tok.type == CONSTANT.LPAREN:
            self.advance()
            expr = self.advance_step(self.expr())
            if self.error: return None
            if self.current_tok.type == CONSTANT.RPAREN:
                self.advance()
                return expr
            else:
                self.error = InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected ')'"
                )
                return None

        elif tok.type == CONSTANT.LSQUARE:
            list_expr = self.advance_step(self.list_expr())
            if self.error: return None
            return list_expr

        elif tok.matches(CONSTANT.KEYWORD, "if"):
            if_expr = self.advance_step(self.if_expr())
            if self.error: return None
            return if_expr

        elif tok.matches(CONSTANT.KEYWORD, "for"):
            for_expr = self.advance_step(self.for_expr())
            if self.error: return None
            return for_expr

        elif tok.matches(CONSTANT.KEYWORD, "while"):
            while_expr = self.advance_step(self.while_expr())
            if self.error: return None
            return while_expr

        elif tok.matches(CONSTANT.KEYWORD, "fun"):
            while_expr = self.advance_step(self.fun_def())
            if self.error: return None
            return while_expr

        self.error = InvalidSyntaxError(
            tok.pos_start, tok.pos_end,
            "Invalid token"
        )
        return None

    def power(self):
        return self.bin_op(self.call, (CONSTANT.POW), self.factor)

    def call(self):
        atom = self.advance_step(self.atom())
        if self.error: return None

        if self.current_tok.type == CONSTANT.LPAREN:
            self.advance()

            arg_nodes = []
            if self.current_tok.type == CONSTANT.RPAREN:
                self.advance()
            else:
                arg_nodes.append(self.advance_step(self.expr()))
                if self.error: return None

                while self.current_tok.type == CONSTANT.COMMA:
                    self.advance()

                    arg_nodes.append(self.advance_step(self.expr()))
                    if self.error: return None

                self.check_type(CONSTANT.RPAREN, "Expected ',' or ')'")
                if self.error: return None

            return CallNode(atom, arg_nodes)

        return atom

    def factor(self):
        tok = self.current_tok

        if tok.type in (CONSTANT.PLUS, CONSTANT.MINUS):
            self.advance()
            factor_res = self.advance_step(self.factor())
            if self.error: return None
            return UnaryOpNode(tok, factor_res)
        return self.power()

    def term(self):  # * and /
        return self.bin_op(self.factor, (CONSTANT.MUL, CONSTANT.DIV))

    def comp_expr(self):
        if self.current_tok.matches(CONSTANT.KEYWORD, "not"):
            op_tok = self.current_tok
            self.advance()

            node = self.advance_step(self.comp_expr())
            if self.error: return None
            return UnaryOpNode(op_tok, node)

        node = self.advance_step(self.bin_op(self.arith_expr,
            (CONSTANT.EE, CONSTANT.NE, CONSTANT.LT, CONSTANT.LTE, CONSTANT.GT, CONSTANT.GTE)
        ))
        if self.error: return None
        return node

    def arith_expr(self):
        return self.bin_op(self.term, (CONSTANT.PLUS, CONSTANT.MINUS))

    def statements(self):
        statements = []
        pos_start = self.current_tok.pos_start.copy()

        while self.current_tok.type == CONSTANT.NEWLINE:
            self.advance()
        statement = self.advance_step(self.statement())
        if self.error: return None
        statements.append(statement)

        more_statements = True
        while True:
            newline_count = 0
            while self.current_tok.type == CONSTANT.NEWLINE:
                self.advance()
                newline_count += 1
            if newline_count == 0:
                more_statements = False

            if not more_statements: break
            statement = self.statement()
            if statement is None:
                self.reverse()
                more_statements = False
                self.error = None  # reset the error. it's only try_match
                continue
            self.advance_step()
            statements.append(statement)

        return ListNode(
            statements,
            pos_start, self.current_tok.pos_end.copy()
        )

    def statement(self):
        pos_start = self.current_tok.pos_start.copy()

        if self.current_tok.matches(CONSTANT.KEYWORD, "return"):
            self.advance()

            expr = self.expr()
            if not expr:
                self.reverse()
                self.error = None
            self.advance_step()
            return ReturnNode(expr, pos_start, self.current_tok.pos_start.copy())

        if self.current_tok.matches(CONSTANT.KEYWORD, "continue"):
            self.advance()
            return ContinueNode(pos_start, self.current_tok.pos_end.copy())

        if self.current_tok.matches(CONSTANT.KEYWORD, "break"):
            self.advance()
            return BreakNode(pos_start, self.current_tok.pos_end.copy())

        expr = self.advance_step(self.expr())
        if self.error: return None
        return expr

    def expr(self):
        if self.current_tok.matches(CONSTANT.KEYWORD, "var"):
            self.advance()

            var_name = self.current_tok
            self.check_type(CONSTANT.IDENTIFIER, "expected identifier!")
            if self.error: return None

            self.check_type(CONSTANT.EQ, "expected ‘=’")
            if self.error: return None

            expr = self.advance_step(self.expr())
            if self.error: return None
            return VarAssignNode(var_name, expr)

        node = self.advance_step(self.bin_op(self.comp_expr, ((CONSTANT.KEYWORD,"and"), (CONSTANT.KEYWORD,"or"))) )
        if self.error: return None
        return node

    def bin_op(self, func_a, ops, func_b=None):
        if func_b is None:
            func_b = func_a
        left = self.advance_step(func_a())
        if self.error: return None

        while self.current_tok.type in ops or \
                (type(ops[0]) == tuple and (self.current_tok.type, self.current_tok.value) in ops):
            op_tok = self.current_tok
            self.advance()
            right = self.advance_step(func_b())
            if self.error: return None
            left = BinOpNode(left, op_tok, right)
        return left

    def if_expr(self):
        all_cases = self.advance_step(self.if_expr_cases('if'))
        if self.error: return None

        cases, else_case = all_cases
        return IfNode(cases, else_case)

    def if_expr_cases(self, case_keyword):
        cases = []
        else_case = None

        self.check_keyword(case_keyword)
        if self.error: return None

        condition = self.advance_step(self.expr())
        if self.error: return None
        self.check_keyword("then")
        if self.error: return None

        if self.current_tok.type == CONSTANT.NEWLINE:
            self.advance()

            statements = self.advance_step(self.statements())
            if self.error: return None
            cases.append((condition, statements, True))

            if self.current_tok.matches(CONSTANT.KEYWORD, "end"):
                self.advance()
            else:
                all_cases = self.advance_step(self.if_expr_elif_or_else())
                if self.error: return None
                new_cases, else_case = all_cases
                cases.extend(new_cases)

        else:
            statement = self.advance_step(self.statement())
            if self.error: return None
            cases.append((condition, statement, False))

            all_calse = self.advance_step(self.if_expr_elif_or_else())
            if self.error: return None
            new_cases, else_case = all_calse
            cases.extend(new_cases)

        return cases, else_case

    def if_expr_elif(self):
        return self.if_expr_cases("elif")

    def if_expr_else(self):
        else_case = None
        if self.current_tok.matches(CONSTANT.KEYWORD, "else"):
            self.advance()

            if self.current_tok.type == CONSTANT.NEWLINE:
                self.advance()

                statements = self.advance_step(self.statements())
                if self.error: return None
                else_case = (statements, True)

                self.check_keyword("end")
                if self.error: return None
            else:
                statement = self.advance_step(self.statement())
                if self.error: return None
                else_case = (statement, False)

        return else_case

    def if_expr_elif_or_else(self):
        cases, else_case = [], None

        if self.current_tok.matches(CONSTANT.KEYWORD, "elif"):
            all_cases = self.advance_step(self.if_expr_elif())
            if self.error: return None
            cases, else_case = all_cases
        else:
            else_case = self.advance_step(self.if_expr_else())
            if self.error: return None

        return (cases, else_case)

    def while_expr(self):
        self.check_keyword("while")
        if self.error: return None

        condition = self.advance_step(self.expr())
        if self.error: return None

        self.check_keyword("then")
        if self.error: return None

        if self.current_tok.type == CONSTANT.NEWLINE:
            self.advance()

            body_node = self.advance_step(self.statements())
            if self.error: return None

            self.check_keyword("end")
            if self.error: return None

            return WhileNode(condition, body_node, True)

        body_node = self.advance_step(self.statement())
        if self.error: return None

        if condition is None or body_node is None:
            self.error = InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "condition or expresstion should not be None",
            )
            return None
        return WhileNode(condition, body_node, False)

    def for_expr(self):
        self.check_keyword("for")
        if self.error: return None

        var_name_tok = self.current_tok
        self.check_type(CONSTANT.IDENTIFIER, "Expected identifier")
        if self.error: return None

        self.check_type(CONSTANT.EQ, "Expected '='")
        if self.error: return None

        start_node = self.advance_step(self.expr())
        if self.error: return None

        if self.current_tok.type != CONSTANT.KEYWORD or self.current_tok.value != 'to':
            self.error = InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected 'to'"
            )
            return None
        self.advance()
        end_node = self.advance_step(self.expr())
        if self.error: return None

        step_node = None
        if self.current_tok.type == CONSTANT.KEYWORD and self.current_tok.value == 'step':
            self.advance()
            step_node = self.advance_step(self.expr())
            if self.error: return None

        self.check_keyword("then")
        if self.error: return None

        if self.current_tok.type == CONSTANT.NEWLINE:
            self.advance()

            body_node = self.advance_step(self.statements())
            if self.error: return None

            self.check_keyword("end")
            if self.error: return None

            return ForNode(var_name_tok, start_node, end_node, step_node, body_node, True)

        body_node = self.advance_step(self.statement())
        if self.error: return None
        return ForNode(var_name_tok, start_node, end_node, step_node, body_node, False)

    def fun_def(self):
        self.check_keyword("fun")
        if self.error: return None

        if self.current_tok.type == CONSTANT.IDENTIFIER:
            var_name_tok = self.current_tok
            self.advance()

            self.check_type(CONSTANT.LPAREN, "Expected '('")
            if self.error: return None
        else:
            var_name_tok = None
            self.check_type(CONSTANT.LPAREN, "Expected identifier or '('")
            if self.error: return None

        arg_name_toks = []
        if self.current_tok.type == CONSTANT.IDENTIFIER:
            arg_name_toks.append(self.current_tok)
            self.advance()

            while self.current_tok.type == CONSTANT.COMMA:
                self.advance()

                tok = self.current_tok
                self.check_type(CONSTANT.IDENTIFIER, "Expected identifier")
                if self.error: return None
                arg_name_toks.append(tok)

            self.check_type(CONSTANT.RPAREN, "Expected ',' or ')'")
            if self.error: return None

        else:
            self.check_type(CONSTANT.RPAREN, "Expected identifier or ')'")
            if self.error: return None

        if self.current_tok.type == CONSTANT.ARROW:
            self.advance()

            body_node = self.advance_step(self.expr())
            if self.error: return None
            return FunDefNode(var_name_tok, arg_name_toks, body_node, True)

        self.check_type(CONSTANT.NEWLINE, "Expected newline or '->'")
        if self.error: return None

        body_node = self.advance_step(self.statements())
        if self.error: return None

        self.check_keyword("end")
        if self.error: return None
        return FunDefNode(var_name_tok, arg_name_toks, body_node, False)

    def list_expr(self):
        element_nodes = []
        pos_start = self.current_tok.pos_start.copy()

        self.check_type(CONSTANT.LSQUARE, "Expected '['")
        if self.error: return None

        if self.current_tok.type == CONSTANT.RSQUARE:
            self.advance()
        else:
            element_nodes.append(self.advance_step(self.expr()))
            if self.error: return None

            while self.current_tok.type == CONSTANT.COMMA:
                self.advance()

                element_nodes.append(self.advance_step(self.expr()))
                if self.error: return None

            self.check_type(CONSTANT.RSQUARE, "Expected ',' or ']'")
            if self.error: return None

        return ListNode( element_nodes, pos_start, self.current_tok.pos_end )


global_classes["Parser"] = Parser