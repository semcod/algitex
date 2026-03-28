#!/usr/bin/env python3
"""Sample buggy code for Claude Code + Ollama refactoring demo."""

import os  # Unused
import json  # Unused


def calc(x, y, op):
    # No type hints, no docstring
    if op == "+":
        return x + y
    elif op == "-":
        return x - y
    elif op == "*":
        return x * y
    elif op == "/":
        if y != 0:
            return x / y
        return None
    return None


def process(items):
    # High complexity
    result = []
    for item in items:
        if item:
            if isinstance(item, dict):
                if 'val' in item:
                    if item['val'] > 0:
                        result.append(item)
    return result


def load(path):
    # Resource leak
    f = open(path, 'r')
    return f.read()


def divide(a, b):
    # No error handling
    return a / b


class Manager:
    def __init__(self, data=[]):
        # Mutable default
        self.data = data
    
    def add(self, item):
        self.data.append(item)


if __name__ == "__main__":
    # Magic number, string concat
    for i in range(10):
        print("Item: " + str(i))
