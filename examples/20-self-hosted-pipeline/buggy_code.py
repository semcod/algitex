#!/usr/bin/env python3
"""
Przykładowy kod z celowymi błędami do naprawy przez self-hosted pipeline.
Ten plik służy do demonstracji pełnego workflowu: analiza → walidacja → naprawa.
"""

import hashlib  # Błąd: nieużywany
import base64  # Błąd: nieużywany
from collections import defaultdict, Counter  # Błąd: nieużywane

def fetch_user_data(user_id, db_connection):
    """Fetch user data from database."""
    cursor = db_connection.cursor()
    
    # Błąd: SQL injection - string formatting
    cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")
    
    # Błąd: nie zamknięty cursor
    return cursor.fetchone()

def calculate_discount(price, user_type):
    """Calculate discounted price."""
    # Błąd: magic numbers
    if user_type == "premium":
        return price * 0.85  # 15% off
    elif user_type == "gold":
        return price * 0.75  # 25% off
    else:
        # Błąd: brak obsługi nieznanego user_type
        return price

def log_activity(user_id, action):
    """Log user activity."""
    # Błąd: hardcoded path
    with open("/var/log/app/activity.log", "a") as f:
        # Błąd: brak sprawdzania czy katalog istnieje
        f.write(f"{user_id}: {action}\n")

def parse_config(config_string):
    """Parse configuration from string."""
    # Błąd: użycie yaml.safe_load jest lepsze, ale tu mamy yaml.load
    import yaml
    # Błąd: yaml.load bez Loader jest niebezpieczny
    return yaml.load(config_string)

def authenticate_user(username, password):
    """Authenticate user."""
    # Błąd: plaintext password comparison
    stored_password = get_stored_password(username)
    if password == stored_password:  # Błąd: timing attack vulnerability
        return True
    return False

def get_stored_password(username):
    """Get stored password (mock)."""
    return "secret123"  # Błąd: hardcoded credentials

def process_large_file(filepath):
    """Process large file."""
    # Błąd: wczytanie całego pliku do pamięci
    with open(filepath, 'r') as f:
        lines = f.readlines()  # Błąd: memory issue dla dużych plików
    
    results = []
    for line in lines:
        # Błąd: unnecessary list building
        results.append(line.strip().upper())
    
    return results

class UserManager:
    """Manages user operations."""
    
    def __init__(self):
        self.users = {}
        self.lock = None  # Błąd: brak właściwego locku dla wątków
    
    def add_user(self, user_id, data):
        """Add a user."""
        # Błąd: race condition - brak synchronizacji
        if user_id not in self.users:
            self.users[user_id] = data
            return True
        return False
    
    def get_user(self, user_id):
        """Get user data."""
        return self.users[user_id]  # Błąd: KeyError zamiast graceful handling

def generate_report(data, format="json"):
    """Generate report in various formats."""
    # Błąd: eval-like dynamic execution
    if format == "json":
        import json
        return json.dumps(data)
    elif format == "python":
        # Błąd: niebezpieczne - repr może wykonać kod przy deserializacji
        return repr(data)
    else:
        # Błąd: fallback do pickle jest niebezpieczny
        import pickle
        return pickle.dumps(data)  # Błąd: deserialization vulnerability

def cleanup_old_files(directory, days=30):
    """Clean up old files."""
    import os
    import time
    
    # Błąd: path traversal - brak walidacji directory
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        
        # Błąd: brak sprawdzania czy to plik
        file_time = os.path.getmtime(filepath)
        if time.time() - file_time > days * 86400:
            # Błąd: bezpośrednie usunięcie bez potwierdzenia
            os.remove(filepath)  # Błąd: może usunąć katalogi!

if __name__ == "__main__":
    # Demonstracja błędów
    manager = UserManager()
    manager.add_user("1", {"name": "Test"})
    
    # Błąd: próba dostępu do nieistniejącego usera
    try:
        user = manager.get_user("999")
    except KeyError:
        print("User not found")
    
    # Błąd: przetwarzanie dużego pliku
    # process_large_file("/path/to/huge/file.txt")
