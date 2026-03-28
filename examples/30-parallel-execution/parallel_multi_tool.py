"""Example: Parallel execution with different tools per ticket.

Some tickets are best handled by aider (code edits),
others by ollama (local, cheap), others by Claude Code (complex).
algitex assigns the right tool per ticket based on complexity.
"""
from algitex import Project
from algitex.tools.parallel import ParallelExecutor

def main():
    p = Project("./my-app")

    tickets = [
        {
            "id": "PLF-010",
            "title": "Fix import order",
            "priority": "low",
            "llm_hints": {
                "model_tier": "cheap",
                "files_to_modify": ["src/utils.py"],
            },
        },
        {
            "id": "PLF-011",
            "title": "Refactor auth middleware (CC=25)",
            "priority": "high",
            "llm_hints": {
                "model_tier": "premium",
                "files_to_modify": ["src/auth/middleware.py"],
            },
        },
        {
            "id": "PLF-012",
            "title": "Add input validation",
            "priority": "normal",
            "llm_hints": {
                "model_tier": "balanced",
                "files_to_modify": ["src/api/handlers.py"],
            },
        },
        {
            "id": "PLF-013",
            "title": "Update error messages",
            "priority": "low",
            "llm_hints": {
                "model_tier": "cheap",
                "files_to_modify": ["src/api/errors.py"],
            },
        },
    ]

    # All 4 tickets touch different files → all can run in parallel
    executor = ParallelExecutor("./my-app", max_agents=4)
    results = executor.execute(tickets)

    # Tool selection per agent based on model_tier:
    # Agent 0 (PLF-010): ollama/qwen2.5-coder:7b (cheap, local)
    # Agent 1 (PLF-011): claude-sonnet-4 (premium, complex task)
    # Agent 2 (PLF-012): gemini-2.5-pro (balanced)
    # Agent 3 (PLF-013): ollama/qwen2.5-coder:7b (cheap, local)

    for r in results:
        print(f"  {r.status}: {r.ticket_id}")


if __name__ == "__main__":
    main()
