from lexer import CONSTANT
from values import *

class Interpreter:
    def __init__(self):
        self.error = None
        self.func_return_value = None
        self.loop_should_continue = False
        self.loop_should_break = False

    def should_return(self):
        return self.error or \
               self.func_return_value or \
               self.loop_should_continue or \
               self.loop_should_break

    def visit(self, node, context):
        method_name = f'visit_{type(node).__name__}'
        method = getattr(self, method_name, self.no_visit_method)
        return method(node, context)

    def no_visit_method(self, node, context):
        raise Exception(f"No visit_{type(node).__name__} method defined")

    def visit_NumberNode(self, node, context):
        return Number(node.tok.value).set_pos(node.pos_start, node.pos_end).set_context(context)

    def visit_StringNode(self, node, context):
        return String(node.tok.value).set_pos(node.pos_start, node.pos_end).set_context(context)

    def visit_BinOpNode(self, node, context):
        left = self.visit(node.left_node, context)
        if self.should_return(): return None
        right = self.visit(node.right_node, context)
        if self.should_return(): return None

        if node.op_tok.type == CONSTANT.PLUS:
            result, error = left.added_to(right)
        elif node.op_tok.type == CONSTANT.MINUS:
            result, error = left.subbed_by(right)
        elif node.op_tok.type == CONSTANT.MUL:
            result, error = left.multed_by(right)
        elif node.op_tok.type == CONSTANT.DIV:
            result, error = left.dived_by(right)
        elif node.op_tok.type == CONSTANT.POW:
            result, error = left.powed_by(right)
        elif node.op_tok.type == CONSTANT.EE:
            result, error = left.get_comparison_eq(right)
        elif node.op_tok.type == CONSTANT.NE:
            result, error = left.get_comparison_ne(right)
        elif node.op_tok.type == CONSTANT.LT:
            result, error = left.get_comparison_lt(right)
        elif node.op_tok.type == CONSTANT.GT:
            result, error = left.get_comparison_gt(right)
        elif node.op_tok.type == CONSTANT.LTE:
            result, error = left.get_comparison_lte(right)
        elif node.op_tok.type == CONSTANT.GTE:
            result, error = left.get_comparison_gte(right)
        elif node.op_tok.matches(CONSTANT.KEYWORD, 'and'):
            result, error = left.anded_by(right)
        elif node.op_tok.matches(CONSTANT.KEYWORD, 'or'):
            result, error = left.ored_by(right)

        if error:
            self.error = error
            return None
        else:
            return result.set_pos(node.pos_start, node.pos_end)

    def visit_UnaryOpNode(self, node, context):
        number = self.visit(node.node, context)
        if self.should_return(): return None

        error = None
        if node.op_tok.type == CONSTANT.MINUS:
            number, error = number.multed_by(Number(-1))
        elif node.op_tok.matches(CONSTANT.KEYWORD, "not"):
            number, error = number.notted()

        if error:
            self.error = error
            return None
        else:
            return number.set_pos(node.pos_start, node.pos_end)

    def visit_VarAccessNode(self, node, context):
        var_name = node.var_name_tok.value
        value = context.symbol_table.get(var_name)

        if value is None:
            self.error = RTError(
                node.pos_start, node.pos_end,
                f"'{var_name}' is not defined",
                context
            )
            return None

        value = value.copy().set_pos(node.pos_start, node.pos_end).set_context(context)
        return value

    def visit_VarAssignNode(self, node, context):
        var_name = node.var_name_tok.value
        value = self.visit(node.value_node, context)
        if self.should_return(): return None

        context.symbol_table.set(var_name, value)
        return value

    def visit_IfNode(self, node, context):
        for condition, expr, should_return_null in node.cases:
            condition_value = self.visit(condition, context)
            if self.should_return(): return None

            if condition_value.is_true():
                expr_value = self.visit(expr, context)
                if self.should_return(): return None
                return Number.null if should_return_null else expr_value

        if node.else_case is not None:
            expr, should_return_null = node.else_case
            else_value = self.visit(expr, context)
            if self.should_return(): return None
            return Number.null if should_return_null else else_value

        return Number.null

    def visit_WhileNode(self, node, context):
        elements = []
        while True:
            condition_value = self.visit(node.condition, context)
            if self.should_return(): return None
            if not condition_value.is_true(): break

            value = self.visit(node.body_node, context)
            if self.loop_should_continue:
                self.loop_should_continue = False
                continue
            elif self.loop_should_break:
                self.loop_should_break = False
                break
            elif self.should_return():
                return None
            else:
                elements.append(value)

        return Number.null if node.should_return_null \
            else List(elements).set_context(context).set_pos(node.pos_start, node.pos_end)

    def visit_ForNode(self, node, context):
        elements = []

        start_value = self.visit(node.start_node, context)
        if self.should_return(): return None
        end_value = self.visit(node.end_node, context)
        if self.should_return(): return None
        if node.step_node is not None:
            step_value = self.visit(node.step_node, context)
            if self.should_return(): return None
        else:
            step_value = Number(1)

        i = start_value.value
        if step_value.value >= 0:
            condition = lambda: i < end_value.value
        else:
            condition = lambda: i > end_value.value

        while condition():
            context.symbol_table.set(node.var_name_tok.value, Number(i))
            i += step_value.value

            value = self.visit(node.body_node, context)
            if self.loop_should_continue:
                self.loop_should_continue = False
                continue
            elif self.loop_should_break:
                self.loop_should_break = False
                break
            elif self.should_return():
                return None
            else:
                elements.append(value)

        return Number.null if node.should_return_null \
            else List(elements).set_context(context).set_pos(node.pos_start, node.pos_end)

    def visit_FunDefNode(self, node, context):
        func_name = node.var_name_tok.value if node.var_name_tok else None
        body_node = node.body_node
        arg_names = [arg.value for arg in node.arg_name_toks]

        func_value = Function(func_name, arg_names, body_node, node.should_auto_return)\
            .set_context(context).set_pos(node.pos_start, node.pos_end)
        if node.var_name_tok is not None:
            context.symbol_table.set(func_name, func_value)

        return func_value

    def visit_CallNode(self, node, context):
        args = []

        value_to_call = self.visit(node.node_to_call, context)
        if self.should_return(): return None
        value_to_call = value_to_call.copy().set_pos(node.pos_start, node.pos_end)

        for arg_node in node.arg_nodes:
            args.append(self.visit(arg_node, context))
            if self.should_return(): return None

        return_value = value_to_call.execute(args)
        if self.should_return(): return None
        return_value = return_value.copy().set_pos(node.pos_start, node.pos_end).set_context(context)
        return return_value

    def visit_ListNode(self, node, context):
        elements = []

        for element in node.element_nodes:
            elements.append(self.visit(element, context))
            if self.should_return(): return None

        return List(elements).set_context(context).set_pos(node.pos_start, node.pos_end)

    def visit_ReturnNode(self, node, context):
        if node.node_to_return:
            value = self.visit(node.node_to_return, context)
            if self.should_return(): return None
        else:
            value = Number.null

        self.func_return_value = value
        return value

    def visit_ContinueNode(self, node, context):
        self.loop_should_continue = True
        return None

    def visit_BreakNode(self, node, context):
        self.loop_should_break = True
        return None


global_classes["Interpreter"] = Interpreter