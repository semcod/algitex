"""Example 42: Duplicate Code Detection and Removal

Demonstrates how algitex detects and helps eliminate duplicate code
using the redup tool and automated refactoring strategies.

Run: python examples/42-duplicate-removal/main.py
"""

from pathlib import Path
import tempfile


def demo_duplicate_problem():
    """Show common duplicate code patterns."""
    print("\n=== The Duplicate Code Problem ===")
    
    code_example = '''
    # auth_service.py
    def validate_token(token):
        parts = token.split('.')
        if len(parts) != 3:
            raise ValueError("Invalid token")
        header = base64decode(parts[0])
        payload = base64decode(parts[1])
        signature = base64decode(parts[2])
        return payload
    
    # api_gateway.py  
    def check_auth(header):
        token = header.replace("Bearer ", "")
        segments = token.split('.')
        if len(segments) != 3:
            raise ValueError("Invalid token")
        hdr = base64decode(segments[0])
        body = base64decode(segments[1])
        sig = base64decode(segments[2])
        return body
    
    # middleware.py
    def extract_user(jwt_string):
        pieces = jwt_string.split('.')
        if len(pieces) != 3:
            raise ValueError("Invalid token")
        h = base64decode(pieces[0])
        p = base64decode(pieces[1])
        s = base64decode(pieces[2])
        return p
    '''
    
    print("\nSame logic, three locations:")
    print("  1. auth_service.validate_token()")
    print("  2. api_gateway.check_auth()")
    print("  3. middleware.extract_user()")
    
    print("\nProblems with duplicates:")
    print("  • Bug fixes must be applied 3 times")
    print("  • Tests must cover 3 implementations")
    print("  • Code review: reviewer may miss inconsistent fix")
    print("  • Cognitive load: which one to use?")
    print("  • Lines of code bloat: ~45 vs ~15 lines")


def demo_detection_with_redup():
    """Show how redup detects duplicates."""
    print("\n=== Duplicate Detection with redup ===")
    
    print("\nCommand: redup ./src --min-lines 5 --similarity 0.8")
    
    print("\nDetection strategy:")
    print("  1. Normalize code (remove comments, normalize whitespace)")
    print("  2. Tokenize into sequences")
    print("  3. Find similar sequences using locality-sensitive hashing")
    print("  4. Report clusters of duplicates")
    
    print("\nExample output:")
    output = """
    Cluster #1: 3 duplicates, ~12 lines each
      File: auth_service.py:45-56
      File: api_gateway.py:23-34
      File: middleware.py:78-89
      Similarity: 94%
      Suggestion: Extract to shared jwt_utils.parse_token()
    """
    print(output)


def demo_extraction_strategy():
    """Show different extraction strategies based on duplicate type."""
    print("\n=== Extraction Strategies ===")
    
    strategies = [
        ("Exact Duplicates", "Extract to shared utility function", "100% identical code"),
        ("Near Duplicates", "Extract with parameters", "Same logic, different data"),
        ("Structural Duplicates", "Abstract into class/strategy", "Same pattern, different types"),
        ("Cross-file Duplicates", "Create shared module", "Duplicates across packages"),
    ]
    
    print("\n{:<20} {:<25} {:<30}".format("Type", "Strategy", "When to Use"))
    print("-" * 80)
    for type_name, strategy, when in strategies:
        print(f"{type_name:<20} {strategy:<25} {when:<30}")
    
    print("\n\nExample: Extracting the JWT parsing logic")
    print("\nBEFORE (45 lines in 3 files):")
    before = """
    # In auth_service.py, api_gateway.py, middleware.py
    def XXX(...):  # 3 different names
        parts = token.split('.')
        if len(parts) != 3: raise ValueError("Invalid token")
        return base64decode(parts[1])
    """
    
    print("\nAFTER (15 lines shared + 3 one-liners):")
    after = """
    # jwt_utils.py
    def parse_jwt(token: str) -> dict:
        parts = token.split('.')
        if len(parts) != 3:
            raise ValueError(f"Invalid JWT: expected 3 parts, got {len(parts)}")
        return {
            'header': base64decode(parts[0]),
            'payload': base64decode(parts[1]),
            'signature': base64decode(parts[2])
        }
    
    # Each file now has:
    from jwt_utils import parse_jwt
    payload = parse_jwt(token)['payload']
    """
    
    print(after)


def demo_algitex_integration():
    """Show algitex-specific duplicate handling."""
    print("\n=== algitex Duplicate Handling ===")
    
    print("\n1. Analysis phase (code2llm + redup):")
    print("   $ algitex analyze")
    print("   → Generates project/duplication.toon.yaml")
    
    print("\n2. Planning phase (automatic ticket creation):")
    print("   $ algitex plan --focus duplicates")
    print("   → Creates tickets for high-impact duplicates")
    
    print("\n3. Execution strategies:")
    
    strategies = """
    a) Automated (deterministic duplicates):
       $ algitex todo fix-auto --category duplicate-code
       
       Handles: exact duplicates, simple extractions
       
    b) LLM-assisted (complex duplicates):
       $ algitex todo run --category duplicate-code --tool ollama-mcp
       
       Handles: near-duplicates requiring abstraction decisions
       
    c) Manual (architectural duplicates):
       $ algitex ticket add "Extract JWT parsing" --priority high
       Then use aider/claude-code via MCP
    """
    print(strategies)


def demo_real_world_example():
    """Show a real duplication pattern from algitex codebase."""
    print("\n=== Real Example: algitex Duplicates ===")
    
    print("\nDetected duplicate classes (from analysis.toon.yaml):")
    
    dups = [
        ("ide_base.py:15-30", "ide_claude.py:12-27", "IDEAdapter base", "99%"),
        ("mcp_orchestrator.py:45-60", "tools/mcp.py:50-65", "MCP connection", "97%"),
    ]
    
    print("\n{:<30} {:<30} {:<20} {:<10}".format(
        "Location 1", "Location 2", "Type", "Similarity"
    ))
    print("-" * 95)
    for loc1, loc2, typ, sim in dups:
        print(f"{loc1:<30} {loc2:<30} {typ:<20} {sim:<10}")
    
    print("\n\nResolution approach:")
    print("  1. Extract common base class to shared module")
    print("  2. Make specific implementations inherit from base")
    print("  3. Remove duplicate code")
    print("  4. Update imports")


def demo_prevention_strategies():
    """Show how to prevent duplicates from accumulating."""
    print("\n=== Prevention Strategies ===")
    
    strategies = """
    1. CI/CD Integration:
       - Run redup on every PR
       - Fail build if new duplicates introduced
       
    2. Pre-commit Hooks:
       - Check for duplicates before commit
       - Warn about copy-pasted code
       
    3. Team Practices:
       - Check existing utilities before writing new code
       - Code review: ask "Is this similar to existing code?"
       - Maintain shared utility modules
       
    4. Architecture:
       - Clear module boundaries
       - Shared utilities for cross-cutting concerns
       - Template method pattern for similar algorithms
    """
    print(strategies)
    
    print("\n\nalgitex CI configuration:")
    ci_config = """
    # .github/workflows/quality.yml
    - name: Check for duplicates
      run: |
        pip install redup
        redup ./src --min-lines 5 --fail-on-new
    """
    print(ci_config)


def demo_metrics_and_roi():
    """Show metrics for duplicate removal ROI."""
    print("\n=== Duplicate Removal ROI ===")
    
    print("\nProject metrics (example):")
    metrics = [
        ("Total duplicates found", "47 clusters", "12,800 lines"),
        ("High-impact duplicates", "8 clusters", "2,400 lines"),
        ("Time to fix (automated)", "~2 hours", "600 lines/hour"),
        ("Time to fix (manual)", "~16 hours", "150 lines/hour"),
        ("Bugs prevented (est.)", "~5 bugs/year", "From inconsistent fixes"),
        ("Maintenance reduction", "30%", "Less code to maintain"),
    ]
    
    print("\n{:<25} {:<20} {:<20}".format("Metric", "Value", "Impact"))
    print("-" * 70)
    for metric, value, impact in metrics:
        print(f"{metric:<25} {value:<20} {impact:<20}")
    
    print("\n\nRecommendation: Focus on high-impact duplicates first")
    print("  - Duplicates in core business logic")
    print("  - Duplicates likely to change frequently")
    print("  - Duplicates spanning multiple teams/services")


def main():
    """Run all duplicate removal demos."""
    print("=" * 70)
    print("Example 42: Duplicate Code Detection and Removal")
    print("=" * 70)
    
    demo_duplicate_problem()
    demo_detection_with_redup()
    demo_extraction_strategy()
    demo_algitex_integration()
    demo_real_world_example()
    demo_prevention_strategies()
    demo_metrics_and_roi()
    
    print("\n" + "=" * 70)
    print("Key Takeaway:")
    print("  Duplicates multiply maintenance burden. Detect early with redup,")
    print("  extract shared utilities, prevent with CI checks.")
    print("=" * 70)


if __name__ == "__main__":
    main()
