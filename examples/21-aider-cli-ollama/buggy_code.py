#!/usr/bin/env python3
"""
Przykładowy kod z celowymi błędami do naprawy przez aider + ollama.

Ten plik zawiera typowe problemy które wykryje prefact -a:
- unused imports
- missing type hints
- magic numbers
- string concatenation
- complexity issues
"""

import os  # Błąd: nieużywany import
import json  # Błąd: nieużywany import
import sys  # Błąd: nieużywany import


def calculate_price(qty, price, discount):
    """Calculate final price."""
    # Błąd: brak type hints
    # Błąd: magic number
    if discount > 0.1:  # 10% threshold hardcoded
        return qty * price * (1 - discount)
    return qty * price


def process_users(users):
    """Process user list."""
    # Błąd: brak type hints
    # Błąd: wysoka złożoność (Cyclomatic Complexity)
    result = []
    for user in users:
        if user:
            if isinstance(user, dict):
                if 'name' in user:
                    if user['name']:
                        if len(user['name']) > 2:
                            result.append(user)
    return result


def format_message(name, value):
    """Format message string."""
    # Błąd: string concatenation zamiast f-string
    return "User " + name + " has value " + str(value)


def load_data(filename):
    """Load data from file."""
    # Błąd: niezamknięty plik (no context manager)
    f = open(filename, 'r')
    data = f.read()
    return data  # resource leak!


def divide(a, b):
    """Divide two numbers."""
    # Błąd: brak obsługi dzielenia przez zero
    return a / b


class UserManager:
    """Manage users."""
    
    def __init__(self, users=[]):  # Błąd: mutable default argument
        self.users = users
    
    def add(self, user):
        # Błąd: brak walidacji
        self.users.append(user)
    
    def get(self, user_id):
        # Błąd: brak obsługi błędu (KeyError)
        return self.users[user_id]


def complex_function(data, threshold, multiplier, offset):
    """Process data with many parameters."""
    # Błąd: za dużo parametrów
    # Błąd: za wysoka złożoność
    result = []
    for item in data:
        if item > threshold:
            temp = item * multiplier + offset
            if temp > 100:
                if temp < 1000:
                    if temp % 2 == 0:
                        result.append(temp)
    return result


def bad_error_handling():
    """Example of bad error handling."""
    try:
        risky_operation()
    except:  # Błąd: pusty except
        pass  # Błąd: silent failure


# Błąd: kod na poziomie modułu (nie w funkcji)
temp_data = []
for i in range(10):  # Błąd: magic number 10
    temp_data.append(i * 2)


if __name__ == "__main__":
    # Błąd: input bez walidacji
    user_input = input("Enter number: ")
    num = int(user_input)  # może rzucić ValueError
    result = divide(100, num)
    print("Result: " + str(result))  # Błąd: string concatenation
