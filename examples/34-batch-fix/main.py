"""Przykład użycia BatchFix — grupowanie i optymalizacja fixów.

Ten przykład pokazuje jak użyć BatchFix do naprawy wielu podobnych
problemów w jednym wywołaniu LLM.

Użycie:
    python main.py --dry-run    # Symulacja
    python main.py --execute    # Wykonaj fixy
"""

from pathlib import Path
import argparse


def demo_batch_dry_run():
    """Demonstracja trybu dry-run."""
    print("=" * 60)
    print("Demo: BatchFix Dry-Run")
    print("=" * 60)
    
    # Symulacja: zobacz co zostanie zbatchowane
    print("\n$ algitex todo batch --dry-run")
    print("""
📦 BatchFix: 20 zadań → 4 grupy

  🔧 string_concat: 8 plików
     • examples/file1.py (line 47)
     • examples/file2.py (line 32)
     ... i 6 więcej
     [DRY-RUN] Symulacja — brak zmian
  
  🔧 magic_number: 5 plików
     • examples/config.py (line 15)
     • examples/main.py (line 88)
     ... i 3 więcej
     [DRY-RUN] Symulacja — brak zmian
  
  🔧 unused_import: 4 pliki
     • src/module1.py (line 3)
     • src/module2.py (line 5)
     ... i 2 więcej
     [DRY-RUN] Symulacja — brak zmian
  
  🔧 single: 3 pliki (indywidualne fixy)
     • src/complex.py (line 120)
     • src/edge_case.py (line 45)
     • src/special.py (line 200)

════════════════════════════════════════════════════════════
  BATCH FIX SUMMARY
════════════════════════════════════════════════════════════

  ✅ Success: 20
  ❌ Failed:  0
  📊 Total:   20

[DRY-RUN] Żadne zmiany nie zostały wprowadzone
    """)


def demo_batch_execute():
    """Demonstracja trybu execute."""
    print("=" * 60)
    print("Demo: BatchFix Execute")
    print("=" * 60)
    
    print("\n$ algitex todo batch --execute")
    print("""
⚡ EXECUTE — Fixy zostaną zastosowane

📋 Znaleziono 20 zadań
📦 BatchFix: 20 zadań → 4 grupy

  🔧 string_concat: 8 plików
     • examples/file1.py
     • examples/file2.py
     ... i 6 więcej
     
     Wywołanie LLM (batch fix)...
     ✓ Batch fix: 8 plików w 42.3s
  
  🔧 magic_number: 5 plików
     • examples/config.py
     • examples/main.py
     ... i 3 więcej
     
     Wywołanie LLM (batch fix)...
     ✓ Batch fix: 5 plików w 38.7s
  
  🔧 unused_import: 4 pliki
     • src/module1.py
     • src/module2.py
     ... i 2 więcej
     
     Wywołanie LLM (batch fix)...
     ✓ Batch fix: 4 pliki w 35.1s
  
  🔧 single: 3 pliki (indywidualne fixy)
     • Individual fix: complex.py
     • Individual fix: edge_case.py
     • Individual fix: special.py
     ✓ 3 fixy w 95.4s

════════════════════════════════════════════════════════════
  BATCH FIX SUMMARY
════════════════════════════════════════════════════════════

  ✅ Success: 20
  ❌ Failed:  0
  📊 Total:   20

✓ Zaktualizowano 20 plików

Porównanie:
  • Pojedyncze fixy: ~600s (10 min)
  • BatchFix: ~211s (3.5 min)
  • Oszczędność: 65%

TODO.md zaktualizowane — zadania oznaczone jako zakończone.
    """)


def demo_custom_batch_size():
    """Demonstracja niestandardowego rozmiaru batch."""
    print("=" * 60)
    print("Demo: Custom Batch Size")
    print("=" * 60)
    
    print("\n$ algitex todo batch -s 3 --dry-run")
    print("""
Batch size: 3 (domyślnie 5)

📦 BatchFix: 15 zadań → 5 grup

  🔧 string_concat: 9 plików
     → 3 batch-e po 3 pliki
     
  Batch 1/3:
     • file1.py, file2.py, file3.py
     
  Batch 2/3:
     • file4.py, file5.py, file6.py
     
  Batch 3/3:
     • file7.py, file8.py, file9.py

Mniejszy batch = więcej wywołań API
Ale: mniejsze zużycie pamięci LLM
    """)


def demo_comparison():
    """Porównanie podejść."""
    print("=" * 60)
    print("Demo: BatchFix vs Individual Fixes")
    print("=" * 60)
    
    print("""
Scenariusz: 50 zadań f-string w różnych plikach

┌────────────────────────────────────────────────────────────┐
│  METODA           │  CZAS      │  KOSZT  │  WYWOŁANIA API │
├────────────────────────────────────────────────────────────┤
│  Pojedyncze fixy  │  1500s     │  $1.00  │     50        │
│  (1 min/zadanie)  │  (25 min)  │         │               │
├────────────────────────────────────────────────────────────┤
│  BatchFix (5)     │  300s      │  $0.20  │     10        │
│  (10 batch × 30s) │  (5 min)   │         │               │
├────────────────────────────────────────────────────────────┤
│  OSZCZĘDNOŚĆ      │  80%       │  80%    │     80%       │
└────────────────────────────────────────────────────────────┘

Wnioski:
  ✓ BatchFix jest 5× szybszy
  ✓ BatchFix kosztuje 5× mniej
  ✓ BatchFix generuje mniej obciążenia API
    """)


def main():
    parser = argparse.ArgumentParser(
        description="BatchFix Example — grupowanie fixów"
    )
    parser.add_argument(
        "--dry-run", 
        action="store_true",
        help="Pokaż demo trybu dry-run"
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Pokaż demo trybu execute"
    )
    parser.add_argument(
        "--custom-size",
        action="store_true",
        help="Pokaż demo niestandardowego batch size"
    )
    parser.add_argument(
        "--compare",
        action="store_true",
        help="Pokaż porównanie metod"
    )
    
    args = parser.parse_args()
    
    if not any([args.dry_run, args.execute, args.custom_size, args.compare]):
        # Default: pokaż wszystko
        args.dry_run = True
        args.execute = True
        args.custom_size = True
        args.compare = True
    
    if args.dry_run:
        demo_batch_dry_run()
        print("\n")
    
    if args.execute:
        demo_batch_execute()
        print("\n")
    
    if args.custom_size:
        demo_custom_batch_size()
        print("\n")
    
    if args.compare:
        demo_comparison()
        print("\n")
    
    print("=" * 60)
    print("Przykłady BatchFix zakończone!")
    print("=" * 60)
    print("\nUżyj:")
    print("  algitex todo batch --help")
    print("  algitex todo batch --dry-run")
    print("  algitex todo batch --execute")


if __name__ == "__main__":
    main()
