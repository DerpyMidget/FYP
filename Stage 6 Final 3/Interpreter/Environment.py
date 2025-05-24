# Environment class handles variable scopes for evaluation.
# Supports nested scopes (for example, function-local vs global).

class Environment:
    def __init__(self, parent=None):
        # Dictionary to store variables in the current scope
        self.vars = {}
        # Reference to the parent environment for nested scopes
        self.parent = parent

    def get(self, name):
        # Retrieve the value of a variable by searching in the current scope
        # and then recursively in parent scopes
        if name in self.vars:
            return self.vars[name]
        elif self.parent:
            return self.parent.get(name)
        raise RuntimeError(f"Undefined variable: {name}")

    def set(self, name, value):
        # Set a variable in the current scope
        self.vars[name] = value
