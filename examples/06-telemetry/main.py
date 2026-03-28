"""Example: Using Telemetry module to track costs and performance.

This example demonstrates how to use the telemetry module to:
1. Create spans for operations
2. Track costs, tokens, and time
3. Generate reports
4. Save and push to Langfuse
"""

import time
from typing import Any
from algitex.tools.telemetry import Telemetry


def basic_telemetry_example() -> Any:
    """Basic telemetry tracking example."""
    print("=== Basic Telemetry Example ===\n")
    
    # Create telemetry instance
    tel = Telemetry("my-project")
    
    # Simulate some operations
    print("1. Creating spans for operations...")
    
    # Operation 1: Code analysis
    span1 = tel.span("code-analysis", "vallm")
    time.sleep(0.1)  # Simulate work
    span1.finish(
        status="ok",
        tokens_in=1000,
        tokens_out=500,
        cost_usd=0.01,
        model="claude-3-haiku"
    )
    
    # Operation 2: Code generation
    span2 = tel.span("code-generation", "aider-mcp")
    time.sleep(0.2)  # Simulate work
    span2.finish(
        status="ok",
        tokens_in=2000,
        tokens_out=1500,
        cost_usd=0.05,
        model="claude-sonnet-4"
    )
    
    # Operation 3: Validation (with error)
    span3 = tel.span("validation", "pytest")
    time.sleep(0.05)  # Simulate work
    span3.finish(
        status="error",
        error="Test failed: test_example.py::test_case",
        tokens_in=0,
        tokens_out=0,
        cost_usd=0.0
    )
    
    # Show aggregates
    print("\n2. Telemetry aggregates:")
    print(f"   Total cost: ${tel.total_cost:.4f}")
    print(f"   Total tokens: {tel.total_tokens}")
    print(f"   Total duration: {tel.total_duration:.2f}s")
    print(f"   Error count: {tel.error_count}")
    
    # Generate summary
    print("\n3. Telemetry summary:")
    summary = tel.summary()
    for key, value in summary.items():
        print(f"   {key}: {value}")
    
    # Generate human-readable report
    print("\n4. Human-readable report:")
    print(tel.report())
    
    # Save telemetry
    print("\n5. Saving telemetry...")
    tel.save()
    print(f"   Saved to: .algitex/telemetry/{tel.run_id}.json")
    
    # Try to push to Langfuse (if available)
    print("\n6. Pushing to Langfuse...")
    tel.push_to_langfuse()
    print("   Note: Install langfuse package to enable Langfuse integration")
    
    return tel


def context_manager_example() -> Any:
    """Using telemetry as a context manager."""
    print("\n=== Context Manager Example ===\n")
    
    tel = Telemetry("context-example")
    
    # Using with statement for automatic timing
    with tel.span("database-query", "postgres") as span:
        # Simulate database work
        time.sleep(0.15)
        span.tokens_in = 100
        span.tokens_out = 50
        span.cost_usd = 0.001
        # span.finish() is called automatically with status="ok"
    
    # With error handling
    try:
        with tel.span("api-call", "rest-api") as span:
            time.sleep(0.1)
            raise ValueError("API rate limit exceeded")
    except Exception as e:
        # The context manager doesn't automatically handle errors
        # You need to finish the span manually
        span.finish(status="error", error=str(e))
    
    print(f"Results: {tel.report()}")
    return tel


def multi_model_comparison() -> Any:
    """Compare costs across different models."""
    print("\n=== Multi-Model Cost Comparison ===\n")
    
    tel = Telemetry("model-comparison")
    
    # Simulate same task with different models
    tasks = [
        ("gpt-4-turbo", 0.03, 2000, 1000),
        ("claude-sonnet-4", 0.015, 1500, 800),
        ("gemini-1.5-pro", 0.0025, 1800, 900),
        ("qwen2.5-coder:7b", 0.0005, 1200, 600),
    ]
    
    print("Testing same task across different models:")
    print("-" * 60)
    
    for model, cost, tokens_in, tokens_out in tasks:
        with tel.span(f"generate-code-{model}", "aider-mcp") as span:
            time.sleep(0.05)  # Simulate processing time
            span.model = model
            span.tokens_in = tokens_in
            span.tokens_out = tokens_out
            span.cost_usd = cost
            
        print(f"{model:20} | Cost: ${cost:6.4f} | Tokens: {tokens_in + tokens_out:5d}")
    
    print("-" * 60)
    print(f"\nBest value: qwen2.5-coder:7b at $0.0005 per task")
    print(f"Best quality: gpt-4-turbo at $0.03 per task")
    
    return tel


def budget_tracking_example():
    """Track spending against a budget."""
    print("\n=== Budget Tracking Example ===\n")
    
    BUDGET = 1.0  # $1.00 budget
    tel = Telemetry("budget-tracked-project")
    
    print(f"Project budget: ${BUDGET:.2f}")
    print("-" * 40)
    
    # Simulate a day's work
    operations = [
        ("morning-analysis", 0.10),
        ("bug-fix-1", 0.15),
        ("feature-implementation", 0.30),
        ("code-review", 0.05),
        ("documentation", 0.08),
    ]
    
    for op_name, cost in operations:
        # Check budget before starting
        if tel.total_cost + cost > BUDGET:
            print(f"\n⚠️  Budget exceeded! Skipping {op_name}")
            break
        
        with tel.span(op_name, "aider-mcp") as span:
            time.sleep(0.1)
            span.tokens_in = 1000
            span.tokens_out = 500
            span.cost_usd = cost
        
        print(f"{op_name:25} | Spent: ${tel.total_cost:.2f} | Remaining: ${BUDGET - tel.total_cost:.2f}")
    
    print(f"\nFinal spending: ${tel.total_cost:.2f} / ${BUDGET:.2f}")
    print(f"Budget utilization: {(tel.total_cost / BUDGET * 100):.1f}%")
    
    return tel


if __name__ == "__main__":
    print("Algitex Telemetry Examples")
    print("=" * 50)
    
    # Run all examples
    basic_telemetry_example()
    context_manager_example()
    multi_model_comparison()
    budget_tracking_example()
    
    print("\n" + "=" * 50)
    print("All examples completed!")
    print("\nTo explore the saved telemetry data:")
    print("1. Check .algitex/telemetry/ directory")
    print("2. Install Langfuse: pip install langfuse")
    print("3. Set LANGFUSE_DATABASE_URL environment variable")
    print("4. Run examples again to see data in Langfuse UI")
