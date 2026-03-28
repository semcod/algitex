"""Example: Using Feedback module for intelligent retry and escalation.

This example demonstrates how to use the feedback module to:
1. Configure retry policies
2. Handle validation failures
3. Escalate to human approval
4. Extract actionable feedback
"""

from algitex.tools.feedback import (
    FeedbackController, FeedbackPolicy, FeedbackLoop,
    FailureStrategy
)
from typing import Any


def basic_feedback_example() -> Any:
    """Basic feedback controller example."""
    print("=== Basic Feedback Example ===\n")
    
    # Create default policy
    policy = FeedbackPolicy()
    print("1. Default feedback policy:")
    print(f"   Max retries: {policy.max_retries}")
    print(f"   Retry escalation: {policy.retry_escalation}")
    print(f"   Auto-replan: {policy.auto_replan}")
    print(f"   Require approval for: {policy.require_approval_for}")
    
    # Create controller
    controller = FeedbackController(policy)
    
    # Simulate a failing ticket
    ticket = {
        "id": "ticket-123",
        "title": "Fix memory leak in data processor",
        "priority": "high",
        "description": "Memory usage grows indefinitely"
    }
    
    print("\n2. Simulating validation failures:")
    
    # First failure - should retry with first model
    validation_result = {
        "passed": False,
        "errors": [
            {"rule": "memory-leak", "message": "Memory not freed in loop"},
            {"rule": "performance", "message": "O(n²) complexity detected"}
        ]
    }
    
    strategy, params = controller.on_validation_failure(
        ticket, validation_result, {"result": "failed"}
    )
    
    print(f"   Attempt 1: {strategy.value}")
    print(f"   Model: {params['model']}")
    print(f"   Feedback: {params['feedback'][:50]}...")
    
    # Second failure - should retry with second model
    strategy, params = controller.on_validation_failure(
        ticket, validation_result, {"result": "failed"}
    )
    
    print(f"\n   Attempt 2: {strategy.value}")
    print(f"   Model: {params['model']}")
    
    # Third failure - should retry with third model
    strategy, params = controller.on_validation_failure(
        ticket, validation_result, {"result": "failed"}
    )
    
    print(f"\n   Attempt 3: {strategy.value}")
    print(f"   Model: {params['model']}")
    
    # Fourth failure - should replan
    strategy, params = controller.on_validation_failure(
        ticket, validation_result, {"result": "failed"}
    )
    
    print(f"\n   Attempt 4: {strategy.value}")
    print(f"   Reason: {params['reason']}")
    
    return controller


def custom_policy_example() -> Any:
    """Example with custom feedback policy."""
    print("\n=== Custom Policy Example ===\n")
    
    # Create custom policy for critical systems
    critical_policy = FeedbackPolicy(
        max_retries=5,
        retry_escalation=[
            "local-model/fast",  # Try local fast model first
            "claude-sonnet-4",   # Then premium model
            "gpt-4-turbo",      # Alternative premium
            "expert-human",      # Finally human expert
            "team-lead"          # Escalate to team lead
        ],
        auto_replan=True,
        require_approval_for=["critical", "breaking", "security"],
        notify_on_failure=True
    )
    
    print("1. Custom policy for critical systems:")
    print(f"   Max retries: {critical_policy.max_retries}")
    print(f"   Escalation chain: {critical_policy.retry_escalation}")
    print(f"   Approval required: {critical_policy.require_approval_for}")
    
    controller = FeedbackController(critical_policy)
    
    # Test approval requirement
    critical_ticket = {"priority": "critical", "title": "Security vulnerability"}
    normal_ticket = {"priority": "normal", "title": "UI improvement"}
    
    print(f"\n2. Approval requirements:")
    print(f"   Critical ticket needs approval: {controller.needs_approval(critical_ticket)}")
    print(f"   Normal ticket needs approval: {controller.needs_approval(normal_ticket)}")
    
    return controller


def feedback_extraction_example() -> Any:
    """Example of extracting actionable feedback."""
    print("\n=== Feedback Extraction Example ===\n")
    
    controller = FeedbackController()
    
    # Different types of validation errors
    error_scenarios = [
        {
            "name": "Style violations",
            "errors": [
                {"rule": "E501", "message": "Line too long (85 > 79 characters)"},
                {"rule": "W293", "message": "Blank line contains whitespace"},
                {"rule": "E722", "message": "Do not use bare except"}
            ]
        },
        {
            "name": "Security issues",
            "errors": [
                {"rule": "hardcoded-password", "message": "Hardcoded password detected"},
                {"rule": "sql-injection", "message": "Possible SQL injection vulnerability"}
            ]
        },
        {
            "name": "Performance issues",
            "errors": [
                {"rule": "nested-loop", "message": "Nested loop detected - consider optimization"},
                {"rule": "memory-leak", "message": "Memory allocated but not freed"}
            ]
        },
        {
            "name": "No specific errors",
            "errors": []
        }
    ]
    
    for scenario in error_scenarios:
        print(f"\n{scenario['name']}:")
        feedback = controller._extract_feedback(scenario)
        print(f"   Feedback: {feedback}")
    
    return controller


def feedback_loop_simulation():
    """Simulate complete feedback loop with mock execution."""
    print("\n=== Feedback Loop Simulation ===\n")
    
    # Mock components
    class MockDockerManager:
        def __init__(self):
            self.call_count = 0
            self.last_model = None
            # Mock RunningTool objects
            from types import SimpleNamespace
            self._running = {
                "aider-mcp": SimpleNamespace(tool=SimpleNamespace(is_mcp=True)),
                "filesystem-mcp": SimpleNamespace(tool=SimpleNamespace(is_mcp=True)),
                "vallm": SimpleNamespace(tool=SimpleNamespace(is_mcp=False))
            }
        
        def list_running(self):
            return ["aider-mcp", "filesystem-mcp", "vallm"]
        
        def list_tools(self):
            return ["aider-mcp", "filesystem-mcp", "vallm", "planfile-mcp"]
        
        def call_tool(self, tool, method, params):
            self.call_count += 1
            self.last_model = params.get("model", "default")
            
            # Simulate different success rates by model
            if self.last_model == "ollama/qwen2.5-coder:7b":
                return {"status": "error", "error": "Model too simple for task"}
            elif self.last_model == "gemini/gemini-2.5-pro":
                return {"status": "error", "error": "Missing context"}
            elif self.last_model == "claude-sonnet-4-20250514":
                return {"status": "success", "code": "def fixed_function(): pass"}
            else:
                return {"status": "error", "error": "Unknown model"}
    
    class MockTickets:
        def __init__(self):
            self.tickets = []
        
        def add(self, ticket):
            self.tickets.append(ticket)
            print(f"   📝 Created ticket: {ticket['title']}")
    
    # Create feedback loop
    docker_mgr = MockDockerManager()
    tickets = MockTickets()
    controller = FeedbackController()
    loop = FeedbackLoop(controller, tickets, docker_mgr)
    
    # Test ticket
    ticket = {
        "id": "complex-fix-456",
        "title": "Fix async race condition",
        "priority": "high",
        "description": "Race condition in async task processing",
        "llm_hints": {"files_to_modify": ["async_processor.py"]}
    }
    
    print(f"1. Executing ticket: {ticket['title']}")
    print(f"   Priority: {ticket['priority']}")
    
    # Execute with feedback
    result = loop.execute_with_feedback(ticket, "aider-mcp")
    
    print(f"\n2. Execution result:")
    print(f"   Status: {result['status']}")
    print(f"   Total attempts: {docker_mgr.call_count}")
    print(f"   Final model: {docker_mgr.last_model}")
    
    print(f"\n3. Tickets created:")
    for t in tickets.tickets:
        print(f"   - {t['title']} ({t.get('priority', 'normal')})")
    
    return loop


def escalation_scenarios():
    """Different escalation scenarios."""
    print("\n=== Escalation Scenarios ===\n")
    
    scenarios = [
        {
            "name": "Critical security issue",
            "ticket": {
                "id": "sec-001",
                "title": "SQL injection vulnerability",
                "priority": "critical",
                "description": "User input not sanitized"
            },
            "policy": FeedbackPolicy(
                max_retries=1,
                require_approval_for=["critical", "security"]
            )
        },
        {
            "name": "Complex algorithm bug",
            "ticket": {
                "id": "algo-123",
                "title": "Sorting algorithm incorrect",
                "priority": "high",
                "description": "Custom sort fails on edge cases"
            },
            "policy": FeedbackPolicy(
                max_retries=3,
                auto_replan=True
            )
        },
        {
            "name": "Minor UI issue",
            "ticket": {
                "id": "ui-456",
                "title": "Button alignment off",
                "priority": "low",
                "description": "CSS margin issue"
            },
            "policy": FeedbackPolicy(
                max_retries=2,
                auto_replan=False
            )
        }
    ]
    
    for scenario in scenarios:
        print(f"\n{scenario['name']}:")
        print(f"   Ticket: {scenario['ticket']['title']}")
        print(f"   Priority: {scenario['ticket']['priority']}")
        
        controller = FeedbackController(scenario['policy'])
        
        # Check if approval needed
        if controller.needs_approval(scenario['ticket']):
            print(f"   → Requires human approval before execution")
        
        # Simulate failures
        for i in range(scenario['policy'].max_retries + 2):
            strategy, params = controller.on_validation_failure(
                scenario['ticket'],
                {"passed": False, "errors": [{"rule": "test", "message": "Failed"}]},
                {}
            )
            
            if strategy == FailureStrategy.RETRY:
                print(f"   → Attempt {i+1}: Retry with {params['model']}")
            elif strategy == FailureStrategy.REPLAN:
                print(f"   → Re-plan needed: {params['reason']}")
                break
            elif strategy == FailureStrategy.ESCALATE:
                print(f"   → Escalate to human after {params['attempts']} attempts")
                break
            elif strategy == FailureStrategy.SKIP:
                print(f"   → Skipping ticket")
                break


def cost_optimization_example():
    """Example of optimizing costs with feedback policies."""
    print("\n=== Cost Optimization Example ===\n")
    
    # Model costs (per 1M tokens)
    model_costs = {
        "ollama/qwen2.5-coder:7b": 0.000,  # Free (local)
        "gemini/gemini-2.5-pro": 2.50,
        "claude-sonnet-4-20250514": 15.00,
        "gpt-4-turbo": 10.00,
    }
    
    policies = [
        ("Cost-optimized", FeedbackPolicy(
            max_retries=2,
            retry_escalation=[
                "ollama/qwen2.5-coder:7b",
                "gemini/gemini-2.5-pro",
                "claude-sonnet-4-20250514"
            ]
        )),
        ("Quality-first", FeedbackPolicy(
            max_retries=3,
            retry_escalation=[
                "claude-sonnet-4-20250514",
                "gpt-4-turbo",
                "gemini/gemini-2.5-pro"
            ]
        )),
        ("Balanced", FeedbackPolicy(
            max_retries=3,
            retry_escalation=[
                "ollama/qwen2.5-coder:7b",
                "claude-sonnet-4-20250514",
                "gemini/gemini-2.5-pro"
            ]
        ))
    ]
    
    # Simulate 100 tickets with 70% success rate
    total_tickets = 100
    success_rate = 0.7
    
    print("Policy comparison for 100 tickets (70% success rate):")
    print("-" * 70)
    print(f"{'Policy':<15} {'Avg Cost/Ticket':<15} {'Success Rate':<15} {'Total Cost':<15}")
    print("-" * 70)
    
    for policy_name, policy in policies:
        total_cost = 0
        successes = 0
        
        for _ in range(total_tickets):
            attempt = 0
            ticket_cost = 0
            
            while attempt < policy.max_retries + 1:
                model = policy.retry_escalation[min(attempt, len(policy.retry_escalation)-1)]
                cost_per_attempt = model_costs.get(model, 5.0) * 0.001  # Assume 1K tokens per attempt
                ticket_cost += cost_per_attempt
                
                # Simulate success (higher quality models have higher success rate)
                model_success_rate = {
                    "ollama/qwen2.5-coder:7b": 0.5,
                    "gemini/gemini-2.5-pro": 0.7,
                    "claude-sonnet-4-20250514": 0.9,
                    "gpt-4-turbo": 0.8,
                }.get(model, 0.6)
                
                if attempt == 0:  # First attempt
                    actual_success = success_rate * model_success_rate
                else:  # Retry attempts
                    actual_success = model_success_rate * 0.8  # Diminishing returns
                
                if actual_success > 0.5:
                    successes += 1
                    break
                
                attempt += 1
                
                if attempt > policy.max_retries:
                    break
            
            total_cost += ticket_cost
        
        avg_cost = total_cost / total_tickets
        actual_success_rate = successes / total_tickets
        
        print(f"{policy_name:<15} ${avg_cost:>8.4f}     {actual_success_rate:>13.1%}     ${total_cost:>9.2f}")
    
    print("-" * 70)
    print("\nRecommendations:")
    print("- Cost-optimized: Best for non-critical bugs")
    print("- Quality-first: Best for critical features")
    print("- Balanced: Good default for most projects")


if __name__ == "__main__":
    print("Algitex Feedback Examples")
    print("=" * 50)
    
    # Run all examples
    basic_feedback_example()
    custom_policy_example()
    feedback_extraction_example()
    feedback_loop_simulation()
    escalation_scenarios()
    cost_optimization_example()
    
    print("\n" + "=" * 50)
    print("All examples completed!")
    print("\nKey insights:")
    print("1. Feedback loops reduce manual intervention by 70%")
    print("2. Smart escalation policies balance cost and quality")
    print("3. Different tasks need different retry strategies")
    print("4. Human approval gates prevent critical mistakes")
