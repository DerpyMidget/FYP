# Parser converts a list of tokens into an Abstract Syntax Tree (AST).
# It supports control flow (if, while), expressions, functions, and more.

from Parser.Nodes import *  # Import all AST node classes (Num, Var, BinOp, etc.)

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0  # Pointer to current token

    def peek(self):
        # Look at the current token without consuming it
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def advance(self):
        # Move to the next token
        self.pos += 1

    def match(self, *types):
        # Try to match the current token type with one of the expected types
        tok = self.peek()
        if tok and tok.type in types:
            self.advance()
            return tok
        return None

    def parse(self):
        # Parse a sequence of statements into a program block
        stmts = []
        while self.peek():
            stmts.append(self.parse_stmt())
        return Block(stmts)

    def parse_stmt(self):
        token = self.peek()
        if token is None:
            return None

        match token.type:
            case "PRINT":
                self.advance()
                expr = self.parse_expr()
                self.match("SEMICOLON")
                return Print(expr)

            case "IF":
                self.advance()
                self.match("LPAREN")
                cond = self.parse_expr()
                self.match("RPAREN")
                then_block = self.parse_block()
                else_block = self.parse_block() if self.match("ELSE") else None
                return If(cond, then_block, else_block)

            case "WHILE":
                self.advance()
                self.match("LPAREN")
                cond = self.parse_expr()
                self.match("RPAREN")
                return While(cond, self.parse_block())

            case "FUNCTION":
                self.advance()
                name = self.match("IDENT").value
                self.match("LPAREN")
                params = []
                if not self.match("RPAREN"):
                    while True:
                        params.append(self.match("IDENT").value)
                        if self.match("RPAREN"):
                            break
                        self.match("COMMA")
                body = self.parse_block()
                return FuncDef(name, params, body)

            case "RETURN":
                self.advance()
                expr = self.parse_expr()
                self.match("SEMICOLON")
                return Return(expr)

            case "LBRACE":
                return self.parse_block()

            case "DEFINEKW":
                self.advance()
                ident = self.match("IDENT").value
                expr = self.parse_expr()
                self.match("SEMICOLON")
                return Assign(ident, expr)

            case "AMMENDKW":
                self.advance()
                target = self.parse_expr()
                self.match("TOKW")
                value = self.parse_expr()
                self.match("SEMICOLON")
                return IndexAssign(target.base, target.index, value)

            case "REMOVEKW":
                self.advance()
                target = self.parse_expr()
                if not isinstance(target, IndexExpr):
                    raise RuntimeError("REMOVE must target an indexed expression")
                self.match("SEMICOLON")
                return Remove(target.base, target.index)

            case "IDENT":
                if (ident := self.match("IDENT")) and self.match("ASSIGN"):
                    expr = self.parse_expr(); self.match("SEMICOLON")
                    return Assign(ident.value, expr)
            case _:
                # Fallback: treat it as an expression statement
                expr = self.parse_expr()
                self.match("SEMICOLON")
                return expr


    def parse_block(self):
        # Parse a block enclosed in { ... }
        self.match("LBRACE")
        stmts = []
        while not self.match("RBRACE"):
            stmts.append(self.parse_stmt())
        return Block(stmts)

    def parse_expr(self):
        return self.parse_or()

    # --- Operator Precedence Handling (lowest to highest) ---

    def parse_or(self):
        node = self.parse_and()
        while self.match("OR"):
            node = BinOp(node, "or", self.parse_and())
        return node

    def parse_and(self):
        node = self.parse_equality()
        while self.match("AND"):
            node = BinOp(node, "and", self.parse_equality())
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

        # Literal numbers, strings, booleans
        if tok.type == "NUMBER":
            self.advance()
            return Num(tok.value)

        if tok.type == "STRING":
            self.advance()
            return Str(tok.value)

        if tok.type == "BOOLEAN":
            self.advance()
            return Bool(tok.value)

        # Identifiers: variables, function calls, indexing
        if tok.type == "IDENT":
            self.advance()
            if self.match("LPAREN"):
                args = []
                if not self.match("RPAREN"):
                    while True:
                        args.append(self.parse_expr())
                        if self.match("RPAREN"):
                            break
                        self.match("COMMA")
                return Call(tok.value, args)
            elif self.match("LBRACKET"):
                index = self.parse_expr()
                self.match("RBRACKET")
                return IndexExpr(Var(tok.value), index)
            return Var(tok.value)

        # Input expression
        if tok.type == "INPUT":
            self.advance()
            self.match("LPAREN")
            prompt = self.parse_expr()
            self.match("RPAREN")
            return Input(prompt)

        # Parenthesized expression
        if tok.type == "LPAREN":
            self.advance()
            expr = self.parse_expr()
            self.match("RPAREN")
            return expr

        # List literal
        if tok.type == "LBRACKET":
            self.advance()
            items = []
            if not self.match("RBRACKET"):
                while True:
                    items.append(self.parse_expr())
                    if self.match("RBRACKET"):
                        break
                    self.match("COMMA")
            return ListExpr(items)

        # Dictionary literal
        if tok.type == "LBRACE":
            self.advance()
            pairs = []
            if not self.match("RBRACE"):
                while True:
                    k = self.parse_expr()
                    self.match("COLON")
                    v = self.parse_expr()
                    pairs.append((k, v))
                    if self.match("RBRACE"):
                        break
                    self.match("COMMA")
            return DictExpr(pairs)

        raise RuntimeError(f"Unexpected token: {tok}")
       