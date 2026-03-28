#!/usr/bin/env python3
"""Sample buggy files for batch processing demo."""


def bad_function_1(x, y) -> Any:
    if x > 0:
        if y > 0:
            return x + y
        else:
            return x
    return 0


def bad_function_2(data) -> Any:
    result = []
    for item in data:
        if item:
            if isinstance(item, str):
                if len(item) > 0:
                    result.append(item.upper())
    return result


def bad_function_3(a, b, c, d, e) -> Any:
    if a > 0:
        if b > 0:
            if c > 0:
                if d > 0:
                    if e > 0:
                        return a + b + c + d + e
    return 0
