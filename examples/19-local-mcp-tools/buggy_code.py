#!/usr/bin/env python3
"""
Przykładowy kod z celowymi błędami do naprawy przez lokalne MCP tools.
"""

from,import  timedelta  # Błąd: nieużywane

def process_items(items) -> Any:
    """Process a list of items."""
    results = []
    
    # Błąd: modyfikacja listy podczas iteracji
    for item in items:
        if item < 0:
            items.remove(item)  # Błąd: mutacja podczas iteracji
        else:
            results.append(item * 2)
    
    return results

def load_data(source) -> Any:
    """Load data from source."""
    # Błąd: SQL injection vulnerability
    query = "SELECT * FROM users WHERE id = " + source
    
    # Błąd: eval z user input
    config = eval(source)  # Błąd: code injection
    
    return config

def cache_result(func) -> Any:
    """Decorator with issues."""
    cache = {}
    
    def wrapper(*args):
        # Błąd: niehashowalne klucze mogą rzucić TypeError
        if args in cache:
            return cache[args]
        result = func(*args)
        cache[args] = result
        return result
    
    return wrapper

def parse_date(date_string):
    """Parse date string."""
    # Błąd: użycie przestarzałego formatu
    parts = date_string.split('/')
    return parts[2] + '-' + parts[0] + '-' + parts[1]  # Błąd: brak walidacji

class BadClass:
    """Class with multiple issues."""
    
    # Błąd: mutable default argument
    def __init__(self, items=[]):
        self.items = items  # Błąd: współdzielona lista między instancjami
    
    def add_item(self, item):
        self.items.append(item)
        return self
    
    # Błąd: __eq__ bez __hash__
    def __eq__(self, other):
        return self.items == other.items

def recursive_function(n):
    """Recursive function without proper termination."""
    # Błąd: brak warunku stopu dla n < 0
    if n == 0:
        return 1
    return n * recursive_function(n - 1)  # Błąd: infinite recursion dla ujemnych

if __name__ == "__main__":
    # Błąd: test z błędnymi danymi
    demo = BadClass()
    demo.add_item("test")
    
    # Błąd: druga instancja dzieli tę samą listę!
    demo2 = BadClass()
    print(f"demo2.items before: {demo2.items}")  # Pokazuje ['test']!
    
    print(f"Result: {recursive_function(-5)}")  # Błąd: RecursionError
