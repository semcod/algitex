#!/usr/bin/env python3
"""Third sample file."""


class BadClass:
    def __init__(self, data=[]):
        self.data = data
    
    def process(self) -> None:
        for item in self.data:
            if item > 0:
                if item < 100:
                    if item % 2 == 0:
                        print(item)


def complex_logic(n) -> Any:
    if n == 0:
        return 1
    if n == 1:
        return 1
    if n == 2:
        return 2
    if n == 3:
        return 6
    return n * complex_logic(n - 1)
