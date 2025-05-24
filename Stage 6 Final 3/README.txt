# README.txt

## Custom Programming Language Interpreter

This interpreter supports:
- Arithmetic and Boolean expressions
- Strings, lists, and dictionaries
- Variable assignment and printing
- User-defined functions with return values
- Conditionals (if/else)
- Loops (while)
- User input

## How to Use

1. Prepare a file using `.mylang` extension (e.g., `mycode.mylang`)
2. Add valid syntax like:

    ```
    x = 5;
    while (x > 0) {
        print x;
        x = x - 1;
    }
    ```

3. Run the interpreter:

    python main_stage6.py mycode.mylang

## Notes

- Statements must end with `;`
- Blocks are defined using `{ ... }`
- All variable types are dynamically assigned
