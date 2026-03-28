# AutoFix Module Documentation

The `algitex.tools.autofix` module provides automated code fixing capabilities by reading TODO items and applying fixes using multiple backends.

## Overview

AutoFix parses TODO.md files and automatically fixes issues using various LLM backends:
- **Ollama** - Direct local LLM usage
- **Aider CLI** - Using aider command-line tool
- **LiteLLM Proxy** - Via OpenAI-compatible proxy

## Architecture

The module is organized with a clean separation of concerns:

### Core Classes

- `Task` - Represents a single TODO item with file path, line number, and description
- `FixResult` - Contains the result of a fix operation with timing and error info
- `AutoFix` - Main class that orchestrates the fixing process

### Backend Methods

Each backend is implemented as a separate method with helper functions for better organization:

#### `fix_with_ollama()`
- Uses the OllamaService for direct LLM interaction
- Automatically selects the best available model
- Clean and simple implementation

#### `fix_with_aider()`
- Refactored into helper methods:
  - `_ensure_git_repo()` - Ensures git repository exists
  - `_build_aider_prompt()` - Constructs the prompt
  - `_build_aider_command()` - Builds the CLI command
  - `_run_aider_subprocess()` - Handles subprocess execution

#### `fix_with_proxy()`
- Refactored into helper methods:
  - `_read_file_content()` - Reads file content
  - `_build_proxy_prompt()` - Builds the API prompt
  - `_call_proxy_api()` - Makes the API call
  - `_extract_code_from_response()` - Extracts code from response
  - `_write_fixed_file()` - Writes the fixed file

## Usage Examples

### Basic Usage

```python
from algitex.tools.autofix import AutoFix

# Initialize with TODO file path
autofix = AutoFix("TODO.md")

# Fix all pending issues
results = autofix.fix_all(limit=5)

# Fix specific issue
result = autofix.fix_issue("TASK-001")

# Dry run to see what would be fixed
autofix.dry_run = True
results = autofix.fix_all()
```

### Using with Project Class

```python
from algitex import Project

p = Project(".")
tasks = p.list_todo_tasks()
result = p.fix_issues(limit=5, backend="auto")
```

### Backend Selection

```python
# Auto-select best backend
autofix.fix_all()

# Use specific backend
autofix.fix_all(backend="ollama")
autofix.fix_all(backend="aider")
autofix.fix_all(backend="litellm-proxy")
```

## Configuration

### Environment Variables

- `OLLAMA_URL` - Ollama API endpoint (default: http://localhost:11434)
- `LITELLM_URL` - LiteLLM proxy URL (default: http://localhost:4000)

### AutoFix Options

```python
autofix = AutoFix(
    todo_file="TODO.md",
    ollama_service=custom_ollama_service,
    proxy_url="http://localhost:4000",
    dry_run=False
)
```

## TODO Format

AutoFix supports multiple TODO formats:

### GitHub-style Checkboxes
```markdown
## Current Issues

- [ ] src/main.py:42 - Fix undefined variable
- [ ] utils.py:15 - Add type hints
```

### Prefact Format
```markdown
file.py:line - description
```

## Backend Details

### Ollama Backend
- Direct communication with local Ollama instance
- Uses OllamaService.auto_fix_file() method
- Automatic model selection from recommended list

### Aider CLI Backend
- Requires git repository
- Creates repo if not exists
- Uses aider command-line tool
- Handles all subprocess errors gracefully

### LiteLLM Proxy Backend
- Communicates via OpenAI-compatible API
- Requires requests module
- Extracts code from markdown responses
- Handles API errors and timeouts

## Error Handling

Each fix operation returns a `FixResult` with:
- `success` - Whether the fix succeeded
- `method` - Which backend was used
- `time_ms` - Time taken in milliseconds
- `error` - Error message if failed

## Best Practices

1. **Always Dry Run First**
   ```python
   autofix.dry_run = True
   autofix.fix_all()
   ```

2. **Use Limits for Large Projects**
   ```python
   autofix.fix_all(limit=10)
   ```

3. **Filter by File When Needed**
   ```python
   autofix.fix_all(filter_file="src/main.py")
   ```

4. **Check Results**
   ```python
   results = autofix.fix_all()
   failed = [r for r in results if not r.success]
   if failed:
       print(f"Failed to fix {len(failed)} issues")
   ```

## Integration with Other Tools

AutoFix integrates seamlessly with:
- **Service Checker** - Verifies backend availability
- **Ollama Service** - Provides model management
- **Todo Parser** - Parses various TODO formats
- **IDE Integration** - Can be triggered from IDE commands

## Troubleshooting

### Common Issues

1. **"No file path specified"**
   - TODO items must include file paths
   - Use format: `file.py:line - description`

2. **"requests module not installed"**
   - Install with: `pip install requests`
   - Required for LiteLLM proxy backend

3. **"Aider not found"**
   - Install with: `pip install aider-chat`
   - Required for Aider CLI backend

4. **"Ollama not running"**
   - Start with: `ollama serve`
   - Required for Ollama backend

### Debug Mode

Enable verbose output:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Recent Improvements

The module has been refactored for better maintainability:
- Large methods broken into focused helper functions
- Consistent error handling patterns
- Improved code organization
- Better separation of concerns

This refactoring makes the code more:
- **Testable** - Individual components can be unit tested
- **Maintainable** - Each function has a single responsibility
- **Readable** - Clear workflow and structure
- **Extensible** - Easy to add new backends or features
