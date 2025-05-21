import os
import sys
from lexer_stage6 import Lexer
from parser_stage6 import Parser
from interpreter_stage6 import Interpreter

def main():
    if len(sys.argv) != 2:
        print("Usage: python main_stage6.py <filename>.mylang")
        return

    filename = sys.argv[1]

    # Check for file extension
    if not filename.endswith(".mylang"):
        print("❌ Error: Expected a .mylang source file.")
        return

    if not os.path.exists(filename):
        print(f"❌ File not found: {filename}")
        return

    # Read source code from input file
    with open(filename) as f:
        text = f.read()
    lexer = Lexer(text)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    program = parser.parse()
    interpreter = Interpreter()
    interpreter.eval(program)

if __name__ == "__main__":
    main()
