# Example 38: Using New Sprint 3 Modules

Demonstrates direct usage of the new classify, repair, and verify modules.

## What it shows

- Using `algitex.todo.classify` for task classification
- Using `algitex.todo.repair` for code repairs
- Using `algitex.todo.verify` for TODO verification
- Combined workflow example

## Running

```bash
cd examples/38-new-modules
python main.py
```

## Key Imports

```python
from algitex.todo.classify import classify_message, KNOWN_MAGIC_CONSTANTS
from algitex.todo.repair import REPAIRERS, repair_unused_import
from algitex.todo.verify import verify_todos, VerifyResult
```
