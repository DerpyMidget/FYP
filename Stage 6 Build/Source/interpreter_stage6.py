from parser_stage6 import *

class ReturnException(Exception):
    def __init__(self, value):
        self.value = value

class Environment:
    def __init__(self, parent=None):
        self.vars = {}
        self.parent = parent

    def get(self, name):
        if name in self.vars:
            return self.vars[name]
        elif self.parent:
            return self.parent.get(name)
        raise RuntimeError(f"Undefined variable: {name}")

    def set(self, name, value):
        self.vars[name] = value

class Interpreter:
    def __init__(self):
        self.env = Environment()
        self.functions = {}

    def eval(self, node):
        if isinstance(node, Block):
            return self.eval_block(node, self.env)
        elif isinstance(node, Num):
            return node.val
        elif isinstance(node, Str):
            return node.val
        elif isinstance(node, Bool):
            return node.val
        elif isinstance(node, Var):
            return self.env.get(node.name)
        elif isinstance(node, Assign):
            val = self.eval(node.expr)
            self.env.set(node.name, val)
            return val
        elif isinstance(node, UnaryOp):
            val = self.eval(node.expr)
            if node.op == '-': return -val
            if node.op == '!': return not val
        elif isinstance(node, BinOp):
            l = self.eval(node.l)
            r = self.eval(node.r)
            if node.op == '+':
                return str(l) + str(r) if isinstance(l, str) or isinstance(r, str) else l + r
            elif node.op == '-': return l - r
            elif node.op == '*': return l * r
            elif node.op == '/': return l / r
            elif node.op == '==': return l == r
            elif node.op == '!=': return l != r
            elif node.op == '<': return l < r
            elif node.op == '<=': return l <= r
            elif node.op == '>': return l > r
            elif node.op == '>=': return l >= r
            elif node.op == 'and': return l and r
            elif node.op == 'or': return l or r
        elif isinstance(node, Print):
            val = self.eval(node.expr)
            # Convert float like 2.0 → 2
            if isinstance(val, float) and val.is_integer():
                val = int(val)
            print(val)
        elif isinstance(node, Input):
            prompt = str(self.eval(node.prompt))
            return input(prompt)
        elif isinstance(node, If):
            if self.eval(node.cond):
                return self.eval(node.then_, self.env)
            elif node.else_:
                return self.eval(node.else_, self.env)
        elif isinstance(node, While):
            while self.eval(node.cond):
                self.eval_block(node.body, self.env)
        elif isinstance(node, ListExpr):
            return [self.eval(x) for x in node.items]
        elif isinstance(node, DictExpr):
            return {self.eval(k): self.eval(v) for k, v in node.pairs}
        elif isinstance(node, IndexExpr):
            base = self.eval(node.base)
            index = self.eval(node.index)
            if isinstance(index, float) and index.is_integer():
                index = int(index)
                return base[index]
        elif isinstance(node, FuncDef):
            self.functions[node.name] = node
        elif isinstance(node, Call):
            func = self.functions.get(node.func)
            if not func:
                raise RuntimeError(f"Function '{node.func}' not defined.")
            args = [self.eval(arg) for arg in node.args]
            return self.call_function(func, args)
        elif isinstance(node, Return):
            val = self.eval(node.expr)
            raise ReturnException(val)
        else:
            raise RuntimeError(f"Unknown node type: {type(node)}")

    def eval_block(self, block, env, is_function=False):
        result = None
        prev_env = self.env
        self.env = Environment(parent=env) if is_function else env  # 🔁 no new scope unless in function
        try:
            for stmt in block.stmts:
                result = self.eval(stmt)
        except ReturnException as ret:
            result = ret.value
        finally:
            self.env = prev_env
        return result


    def call_function(self, func_def, args):
        local_env = Environment(parent=self.env)
        for param, arg in zip(func_def.params, args):
            local_env.set(param, arg)
        return self.eval_block(func_def.body, local_env, is_function=True)

