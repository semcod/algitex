#!/usr/bin/env python3
"""Sample buggy code for LiteLLM proxy + Ollama testing."""



def calculate(x, y, operation) -> Any:
    # No type hints, no docstring
    if operation == "add":
        return x + y
    elif operation == "sub":
        return x - y
    elif operation == "mul":
        return x * y
    elif operation == "div":
        if y == 0:
            return None
        return x / y
    return None


def process_items(data) -> Any:
    # No docstring, high complexity
    result = []
    for item in data:
        if item and isinstance(item, dict):
            if 'value' in item and item['value'] > 0:
                result.append(item)
    return result


def load_file(path) -> Any:
    # Resource leak
    f = open(path, 'r')
    return f.read()


def divide_numbers(a, b):
    # No error handling
    return a / b


class DataManager:
    def __init__(self, items=[]):
        # Mutable default
        self.items = items
    
    def add(self, item):
        self.items.append(item)


if __name__ == "__main__":
    for i in range(10):
        print("Value: " + str(i))
