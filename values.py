import math
import os
from error import RTError
from util import Context, SymbolTable, run_script, global_classes


class Value:
    def __init__(self):
        self.set_pos()
        self.set_context()

    def set_pos(self, pos_start=None, pos_end=None):
        self.pos_start = pos_start
        self.pos_end = pos_end
        return self

    def set_context(self, context=None):
        self.context = context
        return self

    def illegal_operation(self, other=None):
        if not other: other = self
        return RTError(
            self.pos_start, other.pos_end,
            'Illegal operation',
            self.context
        )

class Number(Value):
    def __init__(self, value):
        super().__init__()
        self.value = value

    def as_string(self):
        return f'{self.value}'

    def __repr__(self):
        return self.as_string()

    def is_true(self):
        return self.value != 0

    def added_to(self, other):
        if isinstance(other, Number):
            return Number(self.value + other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def subbed_by(self, other):
        if isinstance(other, Number):
            return Number(self.value - other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def multed_by(self, other):
        if isinstance(other, Number):
            return Number(self.value * other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def dived_by(self, other):
        if isinstance(other, Number):
            if other.value == 0:
                return None, RTError(
                    other.pos_start, other.pos_end,
                    "Division by zero",
                    self.context
                )
            else:
                return Number(self.value / other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def powed_by(self, other):
        if isinstance(other, Number):
            return Number(math.pow(self.value, other.value)).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def get_comparison_eq(self, other):
        if isinstance(other, Number):
            return Number(int(self.value == other.value)).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def get_comparison_ne(self, other):
        if isinstance(other, Number):
            return Number(int(self.value != other.value)).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def get_comparison_lt(self, other):
        if isinstance(other, Number):
            return Number(int(self.value < other.value)).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def get_comparison_gt(self, other):
        if isinstance(other, Number):
            return Number(int(self.value > other.value)).set_context(self.context), None

    def get_comparison_lte(self, other):
        if isinstance(other, Number):
            return Number(int(self.value <= other.value)).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def get_comparison_gte(self, other):
        if isinstance(other, Number):
            return Number(int(self.value >= other.value)).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def anded_by(self, other):
        if isinstance(other, Number):
            return Number(int(self.value and other.value)).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def ored_by(self, other):
        if isinstance(other, Number):
            return Number(int(self.value or other.value)).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def notted(self):
        return Number(1 if self.value == 0 else 0).set_context(self.context), None

    def copy(self):
        copy = Number(self.value)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy

class String(Value):
    def __init__(self, value):
        super().__init__()
        self.value = value

    def as_string(self):
        return f'{self.value}'

    def __repr__(self):
        return self.as_string()

    def is_true(self):
        return len(self.value) > 0

    def added_to(self, other):
        if isinstance(other, String):
            return String(self.value + other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def multed_by(self, other):
        if isinstance(other, Number):
            return String(self.value * other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def copy(self):
        copy = String(self.value)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy

class List(Value):
    def __init__(self, elements):
        super().__init__()
        self.elements = elements

    def __repr__(self):
        return self.as_string()

    def as_string(self):
        elem_strs = [elem.as_string() for elem in self.elements]
        return f"[{','.join(elem_strs)}]"

    def added_to(self, other):
        new_list = self.copy()
        new_list.elements.append(other)
        return new_list, None

    def subbed_by(self, other):
        if isinstance(other, Number):
            new_list = self.copy()
            try:
                new_list.elements.pop(other.value)
                return new_list, None
            except Exception as e:
                return None, RTError(
                    other.pos_start, other.pos_end,
                    "retrieve fails because index is not in the list",
                    self.context
                )
        else:
            return None, Value.illegal_operation(self, other)

    def multed_by(self, other):
        if isinstance(other, List):
            new_list = self.copy()
            new_list.elements.extend(other.elements)
            return new_list, None
        else:
            return None, Value.illegal_operation(self, other)

    def dived_by(self, other):
        if isinstance(other, Number):
            try:
                return self.elements[other.value], None
            except Exception as e:
                return None, RTError(other.pos_start, other.pos_end, "remove fails because index is not in the list", self.context)
        else:
            return None, Value.illegal_operation(self, other)

    def copy(self):
        copy = List(self.elements)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy

class BaseFunction(Value):
    def __init__(self, name):
        super().__init__()
        self.name = name or "<anonymous>"

    def generate_new_context(self):
        new_context = Context(self.name, self.context, self.pos_start)
        new_context.symbol_table = SymbolTable(new_context.parent.symbol_table)
        return new_context

    def check_args(self, arg_names, args):
        if len(args) > len(arg_names):
            return False, RTError(
                self.pos_start, self.pos_end,
                f"{len(args) - len(arg_names)} too many args passed to {self.name}",
                self.context
            )
        elif len(args) < len(arg_names):
            return False, RTError(
                self.pos_start, self.pos_end,
                f"{len(arg_names) - len(args)} too few args passed to {self.name}",
                self.context
            )
        return True, None

    def populate_args(self, arg_names, args, exec_ctx):
        for i in range(len(args)):
            arg_name = arg_names[i]
            arg_value = args[i]
            arg_value.set_context(exec_ctx)
            exec_ctx.symbol_table.set(arg_name, arg_value)

    def check_and_populate_args(self, arg_names, args, exec_ctx):
        succ, error = self.check_args(arg_names, args)
        if succ is False: return False, error
        self.populate_args(arg_names, args, exec_ctx)
        return True, None

class Function(BaseFunction):
    def __init__(self, name, arg_names, body_node, should_auto_return):
        super().__init__(name)
        self.arg_names = arg_names
        self.body_node = body_node
        self.should_auto_return = should_auto_return

    def execute(self, args):
        interpreter = global_classes["Interpreter"]()
        exec_ctx = self.generate_new_context()
        succ, error = self.check_and_populate_args(self.arg_names, args, exec_ctx)
        if succ is False: return None, error

        value = interpreter.visit(self.body_node, exec_ctx)
        if interpreter.should_return() and interpreter.func_return_value is None: 
            return RTError(
                self.pos_start, self.pos_end,
                f"No value returned from function {self.name}",
                self.context
            )
        return_value = (value if self.should_auto_return else None) or interpreter.func_return_value or Number.null
        return return_value

    def copy(self):
        copy = Function(self.name, self.arg_names, self.body_node, self.should_auto_return)
        copy.set_context(self.context)
        copy.set_pos(self.pos_start, self.pos_end)
        return copy

    def __repr__(self):
        return self.as_string()

    def as_string(self):
        return f"<function {self.name}>"

class BuiltInFunction(BaseFunction):
    def __init__(self, name):
        super().__init__(name)

    def execute(self, args):
        exec_ctx = self.generate_new_context()

        method_name = f"execute_{self.name}"
        method = getattr(self, method_name, self.no_visit_method)
        succ, error = self.check_and_populate_args(method.arg_names, args, exec_ctx)
        if succ is False: return error

        return_value, error = method(exec_ctx)
        if error is not None: 
            return error
        else:
            return return_value

    def no_visit_method(self):
        raise Exception(f"No execute_{self.name} method defined")

    def copy(self):
        copy = BuiltInFunction(self.name)
        copy.set_context(self.context)
        copy.set_pos(self.pos_start, self.pos_end)
        return copy

    def __repr__(self):
        return self.as_string()

    def as_string(self):
        return f"<built-in function {self.name}>"

    def execute_print(self, exec_ctx):
        print(str(exec_ctx.symbol_table.get('value')))
        return Number.null, None
    execute_print.arg_names = ["value"]

    def execute_print_ret(self, exec_ctx):
        strObj = String(str(exec_ctx.symbol_table.get('value')))
        return strObj, None
    execute_print_ret.arg_names = ["value"]

    def execute_input(self, exec_ctx):
        text = input()
        return String(text), None
    execute_input.arg_names = []

    def execute_input_int(self, exec_ctx):
        while True:
            try:
                text = input()
                number = int(text)
                break
            except ValueError:
                print(f"'{text}' must be an integer, Try again!")
        return Number(number), None
    execute_input_int.arg_names = []

    def execute_clear(self, exec_ctx):
        os.system("cls" if os.name == 'nt' else "clear")
        return Number.null, None
    execute_clear.arg_names = []

    def execute_is_number(self, exec_ctx):
        is_number = isinstance(exec_ctx.symbol_table.get("value"), Number)
        return Number.true if is_number else Number.false, None
    execute_is_number.arg_names = ['value']

    def execute_is_string(self, exec_ctx):
        is_string = isinstance(exec_ctx.symbol_table.get("value"), String)
        return Number.true if is_string else Number.false, None
    execute_is_string.arg_names = ['value']

    def execute_is_list(self, exec_ctx):
        is_list = isinstance(exec_ctx.symbol_table.get("value"), List)
        return Number.true if is_list else Number.false, None
    execute_is_list.arg_names = ['value']

    def execute_is_function(self, exec_ctx):
        is_function = isinstance(exec_ctx.symbol_table.get("value"), BaseFunction)
        return Number.true if is_function else Number.false, None
    execute_is_function.arg_names = ['value']

    def execute_append(self, exec_ctx):
        list_ = exec_ctx.symbol_table.get("list")
        value = exec_ctx.symbol_table.get("value")

        if not isinstance(list_, List):
            return False, RTError(
                self.pos_start, self.pos_end,
                "First argument must be list",
                exec_ctx
            )
        list_.elements.append(value)
        return Number.null, None
    execute_append.arg_names = ['list', 'value']

    def execute_pop(self, exec_ctx):
        list_ = exec_ctx.symbol_table.get("list")
        index = exec_ctx.symbol_table.get("index")

        if not isinstance(list_, List):
            return False, RTError(
                self.pos_start, self.pos_end,
                "First argument must be list",
                exec_ctx
            )
        if not isinstance(index, Number):
            return False, RTError(
                self.pos_start, self.pos_end,
                "Second argument must be an integer",
                exec_ctx
            )

        try:
            element = list_.elements.pop(index.value)
        except:
            return False, RTError(
                self.pos_start, self.pos_end,
                "Element at this index could not removed from list because index is out of range",
                exec_ctx
            )
        return element, None
    execute_pop.arg_names = ['list', 'index']

    def execute_extend(self, exec_ctx):
        listA = exec_ctx.symbol_table.get("listA")
        listB = exec_ctx.symbol_table.get("listB")

        if not isinstance(listA, List):
            return False, RTError(
                self.pos_start, self.pos_end,
                "First argument must be list",
                exec_ctx
            )
        if not isinstance(listB, List):
            return False, RTError(
                self.pos_start, self.pos_end,
                "Second argument must be list",
                exec_ctx
            )
        listA.elements.extend(listB.elements)
        return Number.null, None
    execute_extend.arg_names = ['listA', 'listB']

    def execute_len(self, exec_ctx):
        list_ = exec_ctx.symbol_table.get("list")
        if not isinstance(list_, List):
            return None, RTError(
                self.pos_start, self.pos_end,
                "Augument must be list",
                exec_ctx
            )
        return Number(len(list_.elements)), None
    execute_len.arg_names = ['list']

    def execute_run(self, exec_ctx):
        filename = exec_ctx.symbol_table.get("filename")
        if not isinstance(filename, String):
            return None, RTError(
                self.pos_start, self.pos_end,
                "Argument must be string",
                exec_ctx
            )
        filename = filename.value

        try:
            with open(filename, "r") as f:
                script = f.read()
        except Exception as e:
            return None, RTError(
                self.pos_start, self.pos_end,
                f"Failed to load script '{filename}'\n" + str(e),
                exec_ctx
            )

        return_value, error = run_script(script, filename)
        if error:
            return None, RTError(
                self.pos_start, self.pos_end,
                f"Failed to finish executing script '{filename}'\n" + error.as_string(),
                exec_ctx
            )
        return return_value, None
    execute_run.arg_names = ['filename']

Number.null = Number(0)
Number.true = Number(1)
Number.false = Number(0)
Number.PI = Number(math.pi)

BuiltInFunction.print = BuiltInFunction("print")
BuiltInFunction.print_ret = BuiltInFunction("print_ret")
BuiltInFunction.input = BuiltInFunction("input")
BuiltInFunction.input_int = BuiltInFunction("input_int")
BuiltInFunction.clear = BuiltInFunction("clear")
BuiltInFunction.is_number = BuiltInFunction("is_number")
BuiltInFunction.is_string = BuiltInFunction("is_string")
BuiltInFunction.is_list = BuiltInFunction("is_list")
BuiltInFunction.is_function = BuiltInFunction("is_function")
BuiltInFunction.append = BuiltInFunction("append")
BuiltInFunction.pop = BuiltInFunction("pop")
BuiltInFunction.extend = BuiltInFunction("extend")
BuiltInFunction.len = BuiltInFunction("len")
BuiltInFunction.run = BuiltInFunction("run")
