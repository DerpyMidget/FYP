class Num:    
    def __init__(self, val): self.val = val
class Str:    
    def __init__(self, val): self.val = val
class Bool:   
    def __init__(self, val): self.val = val
class Var:    
    def __init__(self, name): self.name = name
class BinOp:  
    def __init__(self, l, op, r): self.l, self.op, self.r = l, op, r
class UnaryOp: 
    def __init__(self, op, expr): self.op, self.expr = op, expr
class Assign: 
    def __init__(self, name, expr): self.name, self.expr = name, expr
class Print:  
    def __init__(self, expr): self.expr = expr
class Block:  
    def __init__(self, stmts): self.stmts = stmts
class If:     
    def __init__(self, cond, then, else_=None): self.cond, self.then_, self.else_ = cond, then, else_
class While:  
    def __init__(self, cond, body): self.cond, self.body = cond, body
class Input:  
    def __init__(self, prompt): self.prompt = prompt
class FuncDef:
    def __init__(self, name, params, body): self.name, self.params, self.body = name, params, body
class Return: 
    def __init__(self, expr): self.expr = expr
class Call:   
    def __init__(self, func, args): self.func, self.args = func, args
class ListExpr: 
    def __init__(self, items): self.items = items
class DictExpr: 
    def __init__(self, pairs): self.pairs = pairs
class IndexExpr: 
    def __init__(self, base, index): self.base, self.index = base, index

class Parser:
    def __init__(self, tokens): self.tokens = tokens; self.pos = 0
    def peek(self): return self.tokens[self.pos] if self.pos < len(self.tokens) else None
    def advance(self): self.pos += 1
    def match(self, *types):
        tok = self.peek()
        if tok and tok.type in types:
            self.advance()
            return tok
        return None
    def parse(self):
        stmts = []
        while self.peek(): stmts.append(self.parse_stmt())
        return Block(stmts)

    def parse_stmt(self):
        if self.match("PRINT"):
            expr = self.parse_expr(); self.match("SEMICOLON")
            return Print(expr)
        if self.match("IF"):
            self.match("LPAREN"); cond = self.parse_expr(); self.match("RPAREN")
            then_block = self.parse_block()
            else_block = self.parse_block() if self.match("ELSE") else None
            return If(cond, then_block, else_block)
        if self.match("WHILE"):
            self.match("LPAREN"); cond = self.parse_expr(); self.match("RPAREN")
            return While(cond, self.parse_block())
        if self.match("FUNCTION"):
            name = self.match("IDENT").value
            self.match("LPAREN")
            params = []
            if not self.match("RPAREN"):
                while True:
                    params.append(self.match("IDENT").value)
                    if self.match("RPAREN"): break
                    self.match("COMMA")
            body = self.parse_block()
            return FuncDef(name, params, body)
        if self.match("RETURN"):
            expr = self.parse_expr(); self.match("SEMICOLON")
            return Return(expr)
        if self.match("LBRACE"):
            self.pos -= 1
            return self.parse_block()
        if (ident := self.match("IDENT")) and self.match("ASSIGN"):
            expr = self.parse_expr(); self.match("SEMICOLON")
            return Assign(ident.value, expr)
        expr = self.parse_expr(); self.match("SEMICOLON")
        return expr

    def parse_block(self):
        self.match("LBRACE")
        stmts = []
        while not self.match("RBRACE"): stmts.append(self.parse_stmt())
        return Block(stmts)

    def parse_expr(self): return self.parse_or()
    def parse_or(self):
        node = self.parse_and()
        while self.match("OR"): node = BinOp(node, "or", self.parse_and())
        return node
    def parse_and(self):
        node = self.parse_equality()
        while self.match("AND"): node = BinOp(node, "and", self.parse_equality())
        return node
    def parse_equality(self):
        node = self.parse_comparison()
        while self.peek() and self.peek().type in ("EQ", "NE"):
            op = self.match("EQ", "NE").value
            node = BinOp(node, op, self.parse_comparison())
        return node
    def parse_comparison(self):
        node = self.parse_term()
        while self.peek() and self.peek().type in ("LT", "LE", "GT", "GE"):
            op = self.match("LT", "LE", "GT", "GE").value
            node = BinOp(node, op, self.parse_term())
        return node
    def parse_term(self):
        node = self.parse_factor()
        while self.peek() and self.peek().type in ("PLUS", "MINUS"):
            op = self.match("PLUS", "MINUS").value
            node = BinOp(node, op, self.parse_factor())
        return node
    def parse_factor(self):
        node = self.parse_unary()
        while self.peek() and self.peek().type in ("MUL", "DIV"):
            op = self.match("MUL", "DIV").value
            node = BinOp(node, op, self.parse_unary())
        return node
    def parse_unary(self):
        if self.peek() and self.peek().type in ("NOT", "MINUS"):
            op = self.match("NOT", "MINUS").value
            return UnaryOp(op, self.parse_unary())
        return self.parse_primary()

    def parse_primary(self):
        tok = self.peek()
        if tok.type == "NUMBER": self.advance(); return Num(tok.value)
        if tok.type == "STRING": self.advance(); return Str(tok.value)
        if tok.type == "BOOLEAN": self.advance(); return Bool(tok.value)
        if tok.type == "IDENT":
            self.advance()
            if self.match("LPAREN"):
                args = []
                if not self.match("RPAREN"):
                    while True:
                        args.append(self.parse_expr())
                        if self.match("RPAREN"): break
                        self.match("COMMA")
                return Call(tok.value, args)
            elif self.match("LBRACKET"):
                index = self.parse_expr(); self.match("RBRACKET")
                return IndexExpr(Var(tok.value), index)
            return Var(tok.value)
        if tok.type == "INPUT":
            self.advance(); self.match("LPAREN")
            prompt = self.parse_expr(); self.match("RPAREN")
            return Input(prompt)
        if tok.type == "LPAREN":
            self.advance(); expr = self.parse_expr(); self.match("RPAREN")
            return expr
        if tok.type == "LBRACKET":
            self.advance()
            items = []
            if not self.match("RBRACKET"):
                while True:
                    items.append(self.parse_expr())
                    if self.match("RBRACKET"): break
                    self.match("COMMA")
            return ListExpr(items)
        if tok.type == "LBRACE":
            self.advance()
            pairs = []
            if not self.match("RBRACE"):
                while True:
                    k = self.parse_expr()
                    self.match("COLON")
                    v = self.parse_expr()
                    pairs.append((k, v))
                    if self.match("RBRACE"): break
                    self.match("COMMA")
            return DictExpr(pairs)
        raise RuntimeError(f"Unexpected token: {tok}")
