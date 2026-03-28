#!/usr/bin/env python3
"""
Przykładowy kod z celowymi błędami do naprawy przez Algitex.
Ten plik demonstruje typowe problemy które mogą być wykryte i naprawione.
"""

import os  # Błąd: nieużywany import
import json  # Błąd: nieużywany import
from typing import Dict, List, Any, Optional  # Błąd: nieużywane importy

def calculate_statistics(data):
    """Calculate basic statistics for a dataset."""
    # Błąd: brak sprawdzania czy data jest pusta
    total = 0
    for item in data:
        total += item
    average = total / len(data)  # Błąd: ZeroDivisionError gdy data jest pusta
    
    # Błąd: string concatenation zamiast f-string
    result = "Total: " + str(total) + ", Average: " + str(average)
    return result

def find_user(users, name):
    """Find user by name."""
    for user in users:
        if user['name'] == name:
            return user
    # Błąd: brak return gdy nie znaleziono

def process_file(filename):
    """Process a file."""
    f = open(filename, 'r')  # Błąd: nie zamknięty plik, brak context manager
    content = f.read()
    return content.upper()

def divide_numbers(a, b):
    """Divide two numbers."""
    return a / b  # Błąd: brak sprawdzania dzielenia przez zero

def get_config(key):
    """Get config value."""
    config = {
        'timeout': 30,
        'retries': 3
    }
    return config[key]  # Błąd: brak obsługi KeyError

# Błąd: zmienna nigdy nie używana
temp_value = 42

def complex_function(data):
    """A complex function with multiple issues."""
    result = []
    
    # Błąd: zagnieżdżone pętle z wysoką złożonością
    for i in range(len(data)):
        for j in range(len(data)):
            if i != j:
                if data[i] > data[j]:
                    if data[i] not in result:
                        result.append(data[i])
    
    # Błąd: unreachable code
    return result
    print("This will never print")  # Błąd: kod po return

def bad_error_handling():
    """Function with bad error handling."""
    try:
        risky_operation()
    except:  # Błąd: pusty except, łapie wszystko
        pass  # Błąd: silent failure

if __name__ == "__main__":
    # Błąd: niebezpieczne wywołanie z user input
    user_input = input("Enter filename: ")
    result = process_file(user_input)  # Błąd: path traversal vulnerability
    print(result)
