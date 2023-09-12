from basicToken import CONSTANT


def archieve_nodes(node):
    str_list = []
    text = node.save(str_list)
    return text, str_list


class NumberNode:
    def __init__(self, tok):
        self.tok = tok
        self.pos_start = self.tok.pos_start
        self.pos_end = self.tok.pos_end

    def __repr__(self):
        return f'{self.tok}'

    def save(self, str_list):
        num = self.tok.save(str_list)
        return f"#{num}"

class StringNode:
    def __init__(self, tok):
        self.tok = tok
        self.pos_start = self.tok.pos_start
        self.pos_end = self.tok.pos_end

    def __repr__(self):
        return f'{self.tok}'

    def save(self, str_list):
        str_list.append(repr(self.tok))
        return f"@{len(str_list) - 1}"

class BinOpNode:
    def __init__(self, left_node, op_tok, right_node):
        self.left_node = left_node
        self.op_tok = op_tok
        self.right_node = right_node

        self.pos_start = self.left_node.pos_start
        self.pos_end = self.right_node.pos_end

    def __repr__(self):
        return f'({self.left_node},{self.op_tok},{self.right_node})'

    def save(self, str_list):
        left = self.left_node.save(str_list)
        op = self.op_tok.save(str_list)
        right = self.right_node.save(str_list)
        return f'(BO:{left},{op},{right})'

class UnaryOpNode:
    def __init__(self, op_tok, node):
        self.op_tok = op_tok
        self.node = node

        self.pos_start = self.op_tok.pos_start
        self.pos_end = self.node.pos_end

    def __repr__(self):
        return f"({self.op_tok}, {self.node})"

    def save(self, str_list):
        op = self.op_tok.save(str_list)
        node = self.node.save(str_list)
        return f"(UO:{op},{node})"

class VarAccessNode:
    def __init__(self, var_name_tok):
        self.var_name_tok = var_name_tok
        self.pos_start = self.var_name_tok.pos_start
        self.pos_end = self.var_name_tok.pos_end

    def __repr__(self):
        return f"{self.var_name_tok}"

    def save(self, str_list):
        name = self.var_name_tok.save(str_list)
        return f"(VA:{name})"

class VarAssignNode:
    def __init__(self, var_name_tok, value_node):
        self.var_name_tok = var_name_tok
        self.value_node = value_node
        self.pos_start = self.var_name_tok.pos_start
        self.pos_end = self.value_node.pos_end

    def __repr__(self):
        return f"({self.var_name_tok},{self.value_node})"

    def save(self, str_list):
        name = self.var_name_tok.save(str_list)
        value = self.value_node.save(str_list)
        return f"(VA:{name},{value})"

class IfNode:
    def __init__(self, cases, else_case=None):
        self.cases = cases
        self.else_case = else_case
        self.pos_start = self.cases[0][0].pos_start
        self.pos_end = (self.else_case or self.cases[len(self.cases) - 1])[0].pos_end

    def __repr__(self):
        text = ""
        for case in self.cases:
            text += f"(if {case[0]} then {case[1]})"
        if self.else_case is not None:
            text = f"({text} else {self.else_case}"
        elif len(self.cases) > 1:
            text = f"({text})"
        return text

    def save(self, str_list):
        cases = ','.join([case.save(str_list) for case in self.cases])
        else_case = self.else_case.save(str_list)
        return f"(IF:{len(self.cases)}{','+cases if len(self.cases)>0 else ''},{else_case})"

class WhileNode:
    def __init__(self, condition, body_node, should_return_null):
        self.condition = condition
        self.body_node = body_node
        self.should_return_null = should_return_null
        self.pos_start = self.condition.pos_start
        self.pos_end = self.body_node.pos_end

    def __repr__(self):
        return f"(while {self.condition} then {self.body_node})"

    def save(self, str_list):
        condition = self.condition.save(str_list)
        body = self.body_node.save(str_list)
        return f"(WN:{condition},{body})"

class ForNode:
    def __init__(self, var_name_tok, start_node, end_node, step_node, body_node, should_return_null):
        self.var_name_tok = var_name_tok
        self.start_node = start_node
        self.end_node = end_node
        self.step_node = step_node
        self.body_node = body_node
        self.should_return_null = should_return_null
        self.pos_start = self.var_name_tok.pos_start
        self.pos_end = self.body_node.pos_end

    def __repr__(self):
        step_text = "" if self.step_node is None else f"step {self.step_node}"
        return f"(for {self.var_name_tok} = {self.start_node} to {self.end_node} {step_text} then {self.body_node})"

    def save(self, str_list):
        name = self.var_name_tok.save(str_list)
        start = self.start_node.save(str_list)
        end = self.end_node.save(str_list)
        step = self.step_node.save(str_list)
        body = self.body_node.save(str_list)
        should_return_null = 'T' if self.should_return_null else 'F'
        return f"(FN:{name},{start},{end},{step},{body},{should_return_null})"

class FunDefNode:
    def __init__(self, var_name_tok, arg_name_toks, body_node, should_auto_return):
        self.var_name_tok = var_name_tok
        self.arg_name_toks = arg_name_toks
        self.body_node = body_node
        self.should_auto_return = should_auto_return

        if self.var_name_tok is not None:
            self.pos_start = self.var_name_tok.pos_start
        elif len(self.arg_name_toks) > 0:
            self.pos_start = self.arg_name_toks[0].pos_start
        else:
            self.pos_start = self.body_node.pos_start
        self.pos_end = self.body_node.pos_end

    def __repr__(self):
        name = self.var_name_tok if self.var_name_tok else "unknown"
        args_text = '(' + ', '.join([repr(arg) for arg in self.arg_name_toks]) + ')'
        return f"(fun {name}{args_text}, {self.body_node})"

    def save(self, str_list):
        name = self.var_name_tok.save(str_list)
        args = ','.join([arg.save(str_list) for arg in self.arg_name_toks])
        body = self.body_node.save(str_list)
        return f"(FD:{name},{len(self.arg_name_toks)}{','+args if len(self.arg_name_toks)>0 else ''},{body})"

class CallNode:
    def __init__(self, node_to_call, arg_nodes):
        self.node_to_call = node_to_call
        self.arg_nodes = arg_nodes
        self.pos_start = self.node_to_call.pos_start
        if len(self.arg_nodes) > 0:
            self.pos_end = self.arg_nodes[len(self.arg_nodes) - 1].pos_end
        else:
            self.pos_end = self.node_to_call.pos_end

    def __repr__(self):
        name = self.node_to_call if self.node_to_call else "unknown"
        args_text = '(' + ', '.join([repr(arg) for arg in self.arg_nodes]) + ')'
        return f"(call {name}{args_text})"

    def save(self, str_list):
        node_to_call = self.node_to_call.save(str_list)
        args = ','.join([arg.save(str_list) for arg in self.arg_nodes])
        return f"(CN:{node_to_call},{len(self.arg_nodes)}{','+args if len(self.arg_nodes)>0 else ''})"

class ListNode:
    def __init__(self, element_nodes, pos_start, pos_end):
        self.element_nodes = element_nodes
        self.pos_start = pos_start
        self.pos_end = pos_end

    def __repr__(self):
        return f"[{','.join([repr(item) for item in self.element_nodes])}]"

    def save(self, str_list):
        elements = [item.save(str_list) for item in self.element_nodes]
        return f"(LN:{','.join(elements)})"

class ReturnNode:
    def __init__(self, node_to_return, pos_start, pos_end):
        self.node_to_return = node_to_return
        self.pos_start = pos_start
        self.pos_end = pos_end

    def __repr__(self):
        return "<return>"

    def save(self, str_list):
        return "(RT:)"

class ContinueNode:
    def __init__(self, pos_start, pos_end):
        self.pos_start = pos_start
        self.pos_end = pos_end

    def __repr__(self):
        return "<continue>"

    def save(self, str_list):
        return "(CT:)"

class BreakNode:
    def __init__(self, pos_start, pos_end):
        self.pos_start = pos_start
        self.pos_end = pos_end

    def __repr__(self):
        return "<break>"

    def save(self, str_list):
        return "(BK:)"
