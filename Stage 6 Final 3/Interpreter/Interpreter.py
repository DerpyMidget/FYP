# Interpreter class for evaluating AST nodes
from Parser.Nodes import *
from .Exceptions import ReturnException
from .Environment import Environment

# Interpreter evaluates AST nodes based on their types.
class Interpreter:
    def __init__(self):
        self.env = Environment()
        self.functions = {}

    # Evaluate an AST node.
    def eval(self, node):
        if isinstance(node, Block):
            return self.eval_block(node, self.env)

        # Literal: evaluate numeric node by returning its value
        elif isinstance(node, Num):
            return node.val

        # Literal: evaluate string node
        elif isinstance(node, Str):
            return node.val

        # Literal: evaluate boolean node
        elif isinstance(node, Bool):
            return node.val

        # Variable lookup from environment
        elif isinstance(node, Var):
            return self.env.get(node.name)

        # Assignment: evaluate right-hand side and bind to name
        elif isinstance(node, Assign):
            val = self.eval(node.expr)
            self.env.set(node.name, val)
            return val

        # Unary operation: evaluate subexpression and apply operator (!, -)
        elif isinstance(node, UnaryOp):
            val = self.eval(node.expr)
            if node.op == '-':
                return -val
            if node.op == '!':
                return not val

        # Binary operation: evaluate both sides and apply operator
        elif isinstance(node, BinOp):
            l = self.eval(node.l)
            r = self.eval(node.r)
            if node.op == '+':
                # Normalize float values that are integers (e.g. 5.0 → 5)
                if isinstance(l, float) and l.is_integer():
                    l = int(l)
                if isinstance(r, float) and r.is_integer():
                    r = int(r)
                # Concatenate as string if either operand is a string
                return str(l) + str(r) if isinstance(l, str) or isinstance(r, str) else l + r
            elif node.op == '-':
                return l - r
            elif node.op == '*':
                return l * r
            elif node.op == '/':
                return l / r
            elif node.op == '==':
                return l == r
            elif node.op == '!=':
                return l != r
            elif node.op == '<':
                return l < r
            elif node.op == '<=':
                return l <= r
            elif node.op == '>':
                return l > r
            elif node.op == '>=':
                return l >= r
            elif node.op == 'and':
                return l and r
            elif node.op == 'or':
                return l or r

        # Print statement: evaluate and display the expression
        elif isinstance(node, Print):
            val = self.eval(node.expr)
            if isinstance(val, float) and val.is_integer():
                val = int(val)
            print(val)

        # Input: prompt user and return input value
        elif isinstance(node, Input):
            prompt = str(self.eval(node.prompt))
            return input(prompt)

        # If statement: evaluate condition and execute appropriate branch
        elif isinstance(node, If):
            if self.eval(node.cond):
                return self.eval_block(node.then_, self.env)
            elif node.else_:
                return self.eval_block(node.else_, self.env)

        # While loop: repeatedly evaluate body while condition is true
        elif isinstance(node, While):
            while self.eval(node.cond):
                self.eval_block(node.body, self.env)

        # List literal: evaluate all items and build a list
        elif isinstance(node, ListExpr):
            return [self.eval(x) for x in node.items]

        # Dictionary literal: evaluate all key-value pairs
        elif isinstance(node, DictExpr):
            return {self.eval(k): self.eval(v) for k, v in node.pairs}

        # Indexing: evaluate base and index to extract item
        elif isinstance(node, IndexExpr):
            base = self.eval(node.base)
            index = self.eval(node.index)
            if isinstance(index, float) and index.is_integer():
                index = int(index)
            return base[index]

        # Function definition: store function node by name
        elif isinstance(node, FuncDef):
            self.functions[node.name] = node

        # Function call: resolve and execute user-defined function
        elif isinstance(node, Call):
            func = self.functions.get(node.func)
            if not func:
                raise RuntimeError(f"Function '{node.func}' not defined.")
            args = [self.eval(arg) for arg in node.args]
            return self.call_function(func, args)

        # Return: evaluate expression and signal exit from function
        elif isinstance(node, Return):
            val = self.eval(node.expr)
            raise ReturnException(val)
        
        elif isinstance(node, IndexAssign):
            obj = self.eval(node.obj)
            index = self.eval(node.index)
            value = self.eval(node.value)

            if isinstance(index, float) and index.is_integer():
                index = int(index)

            obj[index] = value
            return value

        elif isinstance(node, Remove):
            container = self.eval(node.obj)
            key = self.eval(node.index)
            
            if isinstance(key, float) and key.is_integer():
                key = int(key)
            
            del container[key]
              
        else:
            raise RuntimeError(f"Unknown node type: {type(node)}")


    # Evaluate a block of statements. Creates a new environment if called from a function.
    def eval_block(self, block, env, is_function=False):
        result = None
        prev_env = self.env
        self.env = Environment(parent=env) if is_function else env
        try:
            for stmt in block.stmts:
                result = self.eval(stmt)
        except ReturnException as ret:
            result = ret.value
        finally:
            self.env = prev_env
        return result

    # Call a user-defined function with arguments.
    def call_function(self, func_def, args):
        local_env = Environment(parent=self.env)
        for param, arg in zip(func_def.params, args):
            local_env.set(param, arg)
        return self.eval_block(func_def.body, local_env, is_function=True)
