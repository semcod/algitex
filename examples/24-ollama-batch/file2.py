#!/usr/bin/env python3
"""Another sample file."""

import os
import json
import sys


def unused_imports() -> Any:
    x = os.path.join("a", "b")
    y = json.dumps({"key": "value"})
    z = sys.argv
    return x, y, z


def magic_numbers() -> int:
    if 42 > 0:
        return 100
    return 0


def no_error_handling() -> Any:
    f = open("/tmp/test.txt", "r")
    return f.read()
