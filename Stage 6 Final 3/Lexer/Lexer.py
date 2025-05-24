# Lexer class tokenizes input text into a list of tokens
import re
from .Token import Token

# Lexer converts source code into a list of tokens.
class Lexer:
    def __init__(self, text):
        self.text = text

    def tokenize(self):
        # Reserved keywords in the language
        keywords = {
            'if': 'IF', 'else': 'ELSE', 'while': 'WHILE',
            'true': 'TRUE', 'false': 'FALSE',
            'print': 'PRINT', 'input': 'INPUT',
            'function': 'FUNCTION', 'return': 'RETURN',
            'define': 'DEFINEKW', 'ammend': 'AMMENDKW', 
            'to': 'TOKW', 'remove': 'REMOVEKW'
        }

        # Regular expression patterns for different token types
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
            ('COMMENT',    r'#.*'),
            ('SKIP',       r'[ \t\n]+'),
            ('MISMATCH',   r'.')
        ]

        # Compile all patterns into a single regular expression
        regex = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in token_spec)
        tokens = []

        # Scan through the source text to find all token matches
        for match in re.finditer(regex, self.text):
            kind = match.lastgroup
            value = match.group()

            # Ignore whitespace and comments
            if kind in ('SKIP', 'COMMENT'):
                continue

            # Raise error on unexpected character
            elif kind == 'MISMATCH':
                raise RuntimeError(f"Unexpected character: {value}")

            # Strip quotes from string literals
            elif kind == 'STRING':
                tokens.append(Token('STRING', value[1:-1]))

            # Convert numeric literals to float
            elif kind == 'NUMBER':
                tokens.append(Token('NUMBER', float(value)))

            # Resolve identifiers: keyword or variable name
            elif kind == 'IDENT':
                tok_type = keywords.get(value, 'IDENT')
                if tok_type == 'TRUE':
                    tokens.append(Token('BOOLEAN', True))
                elif tok_type == 'FALSE':
                    tokens.append(Token('BOOLEAN', False))
                else:
                    tokens.append(Token(tok_type, value))

            # Append other matched tokens
            else:
                tokens.append(Token(kind, value))

        return tokens
