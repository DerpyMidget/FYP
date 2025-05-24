# ReturnException is a custom exception used to signal a return
# from within a function body, carrying the return value.

class ReturnException(Exception):
    def __init__(self, value):
        # Store the return value so it can be caught and used
        self.value = value
