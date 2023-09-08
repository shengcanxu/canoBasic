from lexer import CONSTANT
from values import *

class Interpreter:
    def __init__(self):
        pass

    def visit(self, node, context):
        method_name = f'visit_{type(node).__name__}'
        method = getattr(self, method_name, self.no_visit_method)
        return method(node, context)

    def no_visit_method(self, node, context):
        raise Exception(f"No visit_{type(node).__name__} method defined")

    def visit_NumberNode(self, node, context):
        return RTResult().success(
            Number(node.tok.value).set_pos(node.pos_start, node.pos_end).set_context(context)
        )

    def visit_StringNode(self, node, context):
        return RTResult().success(
            String(node.tok.value).set_pos(node.pos_start, node.pos_end).set_context(context)
        )

    def visit_BinOpNode(self, node, context):
        res = RTResult()
        left = res.register(self.visit(node.left_node, context))
        if res.should_return(): return res
        right = res.register(self.visit(node.right_node, context))
        if res.should_return(): return res

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
            return res.failure(error)
        else:
            return res.success(result.set_pos(node.pos_start, node.pos_end))

    def visit_UnaryOpNode(self, node, context):
        res = RTResult()
        number = res.register(self.visit(node.node, context))
        if res.should_return(): return res

        error = None
        if node.op_tok.type == CONSTANT.MINUS:
            number, error = number.multed_by(Number(-1))
        elif node.op_tok.matches(CONSTANT.KEYWORD, "not"):
            number, error = number.notted()

        if error:
            return res.failure(error)
        else:
            return res.success(number.set_pos(node.pos_start, node.pos_end))

    def visit_VarAccessNode(self, node, context):
        res = RTResult()
        var_name = node.var_name_tok.value
        value = context.symbol_table.get(var_name)

        if not value:
            return res.failure(RTError(
                node.pos_start, node.pos_end,
                f"'{var_name}' is not defined",
                context
            ))

        value = value.copy().set_pos(node.pos_start, node.pos_end).set_context(context)
        return res.success(value)

    def visit_VarAssignNode(self, node, context):
        res = RTResult()
        var_name = node.var_name_tok.value
        value = res.register(self.visit(node.value_node, context))
        if res.should_return(): return res

        context.symbol_table.set(var_name, value)
        return res.success(value)

    def visit_IfNode(self, node, context):
        res = RTResult()
        for condition, expr, should_return_null in node.cases:
            condition_value = res.register(self.visit(condition, context))
            if res.should_return(): return res

            if condition_value.is_true():
                expr_value = res.register(self.visit(expr, context))
                if res.should_return(): return res
                return res.success(Number.null if should_return_null else expr_value)

        if node.else_case is not None:
            expr, should_return_null = node.else_case
            else_value = res.register(self.visit(expr, context))
            if res.should_return(): return res
            return res.success(Number.null if should_return_null else else_value)

        return res.success(Number.null)

    def visit_WhileNode(self, node, context):
        res = RTResult()
        elements = []

        while True:
            condition_value = res.register(self.visit(node.condition, context))
            if res.should_return(): return res
            if not condition_value.is_true(): break

            value = res.register(self.visit(node.body_node, context))
            if res.should_return() and res.loop_should_break is False and res.loop_should_continue is False:
                return res
            if res.loop_should_continue:
                continue
            if res.loop_should_break:
                break
            elements.append(value)

        return res.success(
            Number.null if node.should_return_null else
            List(elements).set_context(context).set_pos(node.pos_start, node.pos_end)
        )

    def visit_ForNode(self, node, context):
        res = RTResult()
        elements = []

        start_value = res.register(self.visit(node.start_node, context))
        if res.should_return(): return res
        end_value = res.register(self.visit(node.end_node, context))
        if res.should_return(): return res
        if node.step_node is not None:
            step_value = res.register(self.visit(node.step_node, context))
            if res.should_return(): return res
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

            value = res.register(self.visit(node.body_node, context))
            if res.should_return() and res.loop_should_break is False  and res.loop_should_continue is False:
                return res
            if res.loop_should_continue:
                continue
            if res.loop_should_break:
                break
            elements.append(value)

        return res.success(
            Number.null if node.should_return_null else
            List(elements).set_context(context).set_pos(node.pos_start, node.pos_end)
        )

    def visit_FunDefNode(self, node, context):
        res = RTResult()
        func_name = node.var_name_tok.value if node.var_name_tok else None
        body_node = node.body_node
        arg_names = [arg.value for arg in node.arg_name_toks]

        func_value = Function(func_name, arg_names, body_node, node.should_auto_return)\
            .set_context(context).set_pos(node.pos_start, node.pos_end)
        if node.var_name_tok is not None:
            context.symbol_table.set(func_name, func_value)

        return res.success(func_value)

    def visit_CallNode(self, node, context):
        res = RTResult()
        args = []

        value_to_call = res.register(self.visit(node.node_to_call, context))
        if res.should_return(): return res
        value_to_call = value_to_call.copy().set_pos(node.pos_start, node.pos_end)

        for arg_node in node.arg_nodes:
            args.append(res.register(self.visit(arg_node, context)) )
            if res.should_return(): return res

        return_value = res.register(value_to_call.execute(args))
        if res.should_return(): return res
        return_value = return_value.copy().set_pos(node.pos_start, node.pos_end).set_context(context)
        return res.success(return_value)

    def visit_ListNode(self, node, context):
        res = RTResult()
        elements = []

        for element in node.element_nodes:
            elements.append(res.register(self.visit(element, context)))
            if res.should_return(): return res

        return res.success(
            List(elements).set_context(context).set_pos(node.pos_start, node.pos_end)
        )

    def visit_ReturnNode(self, node, context):
        res = RTResult()
        if node.node_to_return:
            value = res.register(self.visit(node.node_to_return, context))
            if res.should_return(): return res
        else:
            value = Number.null
        return res.success_return(value)

    def visit_ContinueNode(self, node, context):
        return RTResult().success_continue()

    def visit_BreakNode(self, node, context):
        return RTResult().success_break()


global_classes["Interpreter"] = Interpreter