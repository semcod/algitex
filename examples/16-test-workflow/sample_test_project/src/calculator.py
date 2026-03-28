
def add(x, y) -> Any:
    """Add two numbers."""
    return x + y

def subtract(x, y) -> Any:
    """Subtract y from x."""
    return x - y

def multiply(x, y) -> Any:
    """Multiply two numbers."""
    return x * y

def divide(x, y):
    """Divide x by y."""
    if y == 0:
        raise ValueError("Cannot divide by zero")
    return x / y
