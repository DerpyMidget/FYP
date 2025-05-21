import re

class Token:
    def __init__(self, type_, value):
        self.type = type_
        self.value = value
    def __repr__(self):
        return f"Token({self.type}, {repr(self.value)})"

class Lexer:
    def __init__(self, text):
        self.text = text

    def tokenize(self):
        keywords = {
            'if': 'IF', 'else': 'ELSE', 'while': 'WHILE',
            'true': 'TRUE', 'false': 'FALSE',
            'print': 'PRINT', 'input': 'INPUT',
            'function': 'FUNCTION', 'return': 'RETURN',
        }

        token_spec = [
            ('NUMBER',     r'\d+(\.\d+)?'),
            ('STRING',     r'"[^"]*"'),
            ('IDENT',      r'[a-zA-Z_]\w*'),
            ('EQ',         r'=='), ('NE',         r'!='),
            ('LE',         r'<='), ('GE',         r'>='),
            ('LT',         r'<'),  ('GT',         r'>'),
            ('ASSIGN',     r'='),
            ('PLUS',       r'\+'), ('MINUS',      r'-'),
            ('MUL',        r'\*'), ('DIV',        r'/'),
            ('LPAREN',     r'\('), ('RPAREN',     r'\)'),
            ('LBRACE',     r'\{'), ('RBRACE',     r'\}'),
            ('LBRACKET',   r'\['), ('RBRACKET',   r'\]'),
            ('COLON',      r':'),  ('COMMA',      r','), 
            ('SEMICOLON',  r';'),
            ('AND',        r'and'), ('OR',         r'or'),
            ('NOT',        r'!'),
            ('COMMENT',    r'\#.*'),
            ('SKIP',       r'[ \t\n]+'),
            ('MISMATCH',   r'.')
        ]

        regex = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in token_spec)
        tokens = []

        for match in re.finditer(regex, self.text):
            kind = match.lastgroup
            value = match.group()

            if kind in ('SKIP', 'COMMENT'):
                continue
            elif kind == 'MISMATCH':
                raise RuntimeError(f"Unexpected character: {value}")
            elif kind == 'STRING':
                tokens.append(Token('STRING', value[1:-1]))
            elif kind == 'NUMBER':
                tokens.append(Token('NUMBER', float(value)))
            elif kind == 'IDENT':
                tok_type = keywords.get(value, 'IDENT')
                if tok_type == 'TRUE':
                    tokens.append(Token('BOOLEAN', True))
                elif tok_type == 'FALSE':
                    tokens.append(Token('BOOLEAN', False))
                else:
                    tokens.append(Token(tok_type, value))
            else:
                tokens.append(Token(kind, value))
        return tokens
