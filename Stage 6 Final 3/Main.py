import os
import sys

# Import modular components
from Lexer.Lexer import Lexer
from Parser.Parser import Parser
from Interpreter.Interpreter import Interpreter

def main():
    # Check for correct number of arguments
    if len(sys.argv) != 2:
        print("Usage: python main.py <filename>.mylang")
        return

    filename = sys.argv[1]

    # Ensure the file has the correct .mylang extension
    if not filename.endswith(".mylang"):
        print("❌ Error: Expected a .mylang source file.")
        return

    # Check if the file exists on the filesystem
    if not os.path.exists(filename):
        print(f"❌ File not found: {filename}")
        return

    # Step 1: Read source code
    with open(filename) as f:
        source_code = f.read()

    # Step 2: Lexical Analysis (tokenize the source)
    lexer = Lexer(source_code)
    tokens = lexer.tokenize()

    #  Step 3: Parsing (generate abstract syntax tree from tokens)
    parser = Parser(tokens)
    ast = parser.parse()

    # Step 4: Interpretation (execute the AST)
    interpreter = Interpreter()
    interpreter.eval(ast)

if __name__ == "__main__":
    main()
