from basicToken import CONSTANT, Token, TT_DIGITS
from error import Position


def archieve_nodes(node, filepath):
    str_list = []
    text = node.save(str_list)
    with open(filepath, "w") as f:
        for string in str_list:
            f.write(string + "\n")
        f.write("#%%#\n")
        f.write(text)
    return text, str_list

def restore_nodes(filepath):
    tokens = read_nodes_str(filepath)
    print(tokens)

    ast, _ = restore_node(tokens)
    return ast

def restore_node(tokens):
    className = StringNode
    node_name = tokens[0]
    if node_name == 'None':
        tokens = tokens[1:]
        return None, tokens
    elif node_name == 'False':
        tokens = tokens[1:]
        return False, tokens
    elif node_name == 'True':
        tokens = tokens[1:]
        return True, tokens
    elif node_name[0] == '#':
        className = NumberNode
    elif node_name[0] == '@':
        className = StringNode
    elif node_name[0] == '$':
        className = Token
    else:
        if node_name not in Node_Name_Map:
            raise Exception("No such Node name")
        else:
            className = Node_Name_Map[node_name]

    node, tokens = className.restore(tokens)
    return node, tokens

def read_nodes_str(filepath):
    with open(filepath, "r") as f:
        code_start = False
        str_list = []

        line = f.readline()
        while line is not None and len(line) > 0:
            if line.strip() == "#%%#":
                code_start = True
            if code_start:
                code = line.strip()
            else:
                str_list.append(line)

            line = f.readline()

    tokens = code.split(',')
    for idx in range(len(tokens)):
        token = tokens[idx]
        if token[0] == '@':
            str_idx = int(token[1:])
            string = str_list[str_idx]
            string = string[:len(string)-1]
            tokens[idx] = '@' + string

    return tokens

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

    @classmethod
    def restore(cls, tokens):
        numstr = tokens[0][1:]
        tokens = tokens[1:]
        if numstr.find('.') >= 0:
            token = Token(CONSTANT.FLOAT, float(numstr), Position(0,0,0))
        else:
            token = Token(CONSTANT.INT, int(numstr), Position(0,0,0))

        return cls(token), tokens

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

    @classmethod
    def restore(cls, tokens):
        string = tokens[0][1:]
        tokens = tokens[1:]
        tok = Token(CONSTANT.STRING, string, Position(0,0,0))
        return cls(tok), tokens

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
        return f'BO,{left},{op},{right}'

    @classmethod
    def restore(cls, tokens):
        tokens = tokens[1:]
        left, tokens = restore_node(tokens)
        op_tok, tokens = Token.restore(tokens, type_=tokens[0])
        right, tokens = restore_node(tokens)
        return cls(left, op_tok, right), tokens

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
        return f"UO,{op},{node}"

    @classmethod
    def restore(cls, tokens):
        tokens = tokens[1:]
        op_tok, tokens = Token.restore(tokens, type_=tokens[0])
        node, tokens = restore_node(tokens)
        return cls(op_tok, node), tokens

class VarAccessNode:
    def __init__(self, var_name_tok):
        self.var_name_tok = var_name_tok
        self.pos_start = self.var_name_tok.pos_start
        self.pos_end = self.var_name_tok.pos_end

    def __repr__(self):
        return f"(VC:{self.var_name_tok})"

    def save(self, str_list):
        name = self.var_name_tok.save(str_list)
        return f"VC,{name}"

    @classmethod
    def restore(cls, tokens):
        tokens = tokens[1:]
        name, tokens = Token.restore(tokens)
        return cls(name), tokens

class VarAssignNode:
    def __init__(self, var_name_tok, value_node):
        self.var_name_tok = var_name_tok
        self.value_node = value_node
        self.pos_start = self.var_name_tok.pos_start
        self.pos_end = self.value_node.pos_end

    def __repr__(self):
        return f"(VA:{self.var_name_tok},{self.value_node})"

    def save(self, str_list):
        name = self.var_name_tok.save(str_list)
        value = self.value_node.save(str_list)
        return f"VA,{name},{value}"

    @classmethod
    def restore(cls, tokens):
        tokens = tokens[1:]
        name, tokens = restore_node(tokens)
        value, tokens = restore_node(tokens)
        return cls(name, value), tokens

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
        case_list = []
        for condition, expr, should_return_null in self.cases:
            case_list.append(condition.save(str_list))
            case_list.append(expr.save(str_list))
            case_list.append('True' if should_return_null else 'False')
        cases = ','.join(case_list)

        if self.else_case is not None:
            expr, should_return_null = self.else_case
            expr_str = expr.save(str_list)
            else_case = f"{expr_str},{should_return_null}"
        else:
            else_case = "None,None"
        return f"IF,{len(self.cases)}{','+cases if len(self.cases)>0 else ''},{else_case}"

    @classmethod
    def restore(cls, tokens):
        tokens = tokens[1:]
        num = int(tokens[0])
        tokens = tokens[1:]

        cases = []
        for i in range(num):
            condition, tokens = restore_node(tokens)
            expr, tokens = restore_node(tokens)
            should_return_null, tokens = restore_node(tokens)
            cases.append((condition, expr, should_return_null))
        expr, tokens = restore_node(tokens)
        should_return_null, tokens = restore_node(tokens)
        else_case = (expr, should_return_null) if expr is not None and should_return_null is not None else None
        return cls(cases, else_case), tokens

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
        return f"WN,{condition},{body},{self.should_return_null}"

    @classmethod
    def restore(cls, tokens):
        tokens = tokens[1:]
        condition, tokens = restore_node(tokens)
        body, tokens = restore_node(tokens)
        should_return_null, tokens = restore_node(tokens)
        return cls(condition, body, should_return_null), tokens

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
        step = self.step_node.save(str_list) if self.step_node else "None"
        body = self.body_node.save(str_list)
        should_return_null = 'True' if self.should_return_null else 'False'
        return f"FN,{name},{start},{end},{step},{body},{should_return_null}"

    @classmethod
    def restore(cls, tokens):
        tokens = tokens[1:]
        name, tokens = Token.restore(tokens)
        start, tokens = restore_node(tokens)
        end, tokens = restore_node(tokens)
        step, tokens = restore_node(tokens)
        body, tokens = restore_node(tokens)
        should_return_null, tokens = restore_node(tokens)
        return cls(name, start, end, step, body, should_return_null), tokens

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
        return f"FD,{name},{len(self.arg_name_toks)}{','+args if len(self.arg_name_toks)>0 else ''},{body},{self.should_auto_return}"

    @classmethod
    def restore(cls, tokens):
        tokens = tokens[1:]
        # name, tokens = Token.restore(tokens, type_=tokens[0])
        name, tokens = restore_node(tokens)
        num = int(tokens[0])
        tokens = tokens[1:]

        args = []
        for i in range(num):
            arg, tokens = restore_node(tokens)
            args.append(arg)
        body, tokens = restore_node(tokens)
        should_auto_return, tokens = restore_node(tokens)
        return cls(name, args, body, should_auto_return), tokens

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
        return f"CN,{node_to_call},{len(self.arg_nodes)}{','+args if len(self.arg_nodes)>0 else ''}"

    @classmethod
    def restore(cls, tokens):
        tokens = tokens[1:]
        node_to_call, tokens = restore_node(tokens)
        num = int(tokens[0])
        tokens = tokens[1:]

        args = []
        for i in range(num):
            arg, tokens = restore_node(tokens)
            args.append(arg)
        return cls(node_to_call, args), tokens

class ListNode:
    def __init__(self, element_nodes, pos_start, pos_end):
        self.element_nodes = element_nodes
        self.pos_start = pos_start
        self.pos_end = pos_end

    def __repr__(self):
        return f"[{','.join([repr(item) for item in self.element_nodes])}]"

    def save(self, str_list):
        elements = ','.join([item.save(str_list) for item in self.element_nodes])
        return f"LN,{len(self.element_nodes)}{','+elements if len(self.element_nodes)>0 else ''}"

    @classmethod
    def restore(cls, tokens):
        tokens = tokens[1:]
        node_num = int(tokens[0])
        tokens = tokens[1:]

        nodes = []
        for i in range(node_num):
            node, tokens = restore_node(tokens)
            nodes.append(node)
        return cls(nodes, Position(0,0,0), Position(0,0,0)), tokens

class ReturnNode:
    def __init__(self, node_to_return, pos_start, pos_end):
        self.node_to_return = node_to_return
        self.pos_start = pos_start
        self.pos_end = pos_end

    def __repr__(self):
        return "<return>"

    def save(self, str_list):
        node_to_return = self.node_to_return.save(str_list)
        return f"RT,{node_to_return}"

    @classmethod
    def restore(cls, tokens):
        tokens = tokens[1:]
        node_to_return, tokens = restore_node(tokens)
        return cls(node_to_return, Position(0,0,0), Position(0,0,0)), tokens

class ContinueNode:
    def __init__(self, pos_start, pos_end):
        self.pos_start = pos_start
        self.pos_end = pos_end

    def __repr__(self):
        return "<continue>"

    def save(self, str_list):
        return "CT"

    @classmethod
    def restore(cls, tokens):
        tokens = tokens[1:]
        return cls(Position(0,0,0), Position(0,0,0)), tokens

class BreakNode:
    def __init__(self, pos_start, pos_end):
        self.pos_start = pos_start
        self.pos_end = pos_end

    def __repr__(self):
        return "<break>"

    def save(self, str_list):
        return "BK"

    @classmethod
    def restore(cls, tokens):
        tokens = tokens[1:]
        return cls(Position(0,0,0), Position(0,0,0)), tokens

Node_Name_Map = {
    "BO": BinOpNode,
    "UO": UnaryOpNode,
    "VC": VarAccessNode,
    "VA": VarAssignNode,
    "IF": IfNode,
    "WN": WhileNode,
    "FN": ForNode,
    "FD": FunDefNode,
    "CN": CallNode,
    "LN": ListNode,
    "RT": ReturnNode,
    "CT": ContinueNode,
    "BK": BreakNode
}