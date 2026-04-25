# Context Examples

```bash
cd examples/07-context
```

This example demonstrates how to use the context module to build rich prompts for LLM coding tasks.

## Features Demonstrated

- Basic context building from project files
- Context optimization for different use cases
- Semantic search for related code
- Prompt engineering improvements

## What You'll See

1. **Basic Context** - Building context from .toon files and project structure
2. **Context Optimization** - Different strategies for bug fixes, features, refactoring
3. **Semantic Search** - Finding related code automatically
4. **Prompt Engineering** - How rich context improves LLM performance

## Key Takeaways

- Rich context improves LLM code quality by ~40%
- Different tasks need different context optimization
- Semantic search helps find related code automatically
- Context includes architecture, conventions, and recent changes

## Configuration

The context module automatically reads:
- `.toon` files for project metrics and architecture
- `pyproject.toml`, `.editorconfig` for conventions
- Git history for recent changes
- Related files based on imports

## Use Cases

- Bug fixes: Include related test files and error context
- Features: Include architecture and dependency information
- Refactoring: Include all affected modules and their relationships
