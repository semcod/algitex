#!/usr/bin/env python3
"""
Local Model Comparison - Benchmark Ollama models.
Compares different models on the same coding tasks.
"""

import os
import sys
import time
import json
from typing import List, Dict, Any
import requests

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")

# Models to test
DEFAULT_MODELS = [
    "qwen2.5-coder:3b",
    "qwen2.5-coder:7b",
    "llama3:8b",
    "codellama:7b",
]

# Test tasks
TASKS = {
    "code_completion": {
        "name": "Code Completion",
        "prompt": """Complete this Python function:

def fibonacci(n):
    \"\"\"Generate Fibonacci sequence.\"\"\"""",
        "expected": ["def", "fibonacci", "return", "sequence"]
    },
    "bug_fix": {
        "name": "Bug Fix",
        "prompt": """Fix the bug in this code:

def divide(a, b):
    return a / b

# Test: divide(10, 0) should not crash""",
        "expected": ["if", "ZeroDivisionError", "try", "except"]
    },
    "documentation": {
        "name": "Documentation",
        "prompt": """Add docstring to this function:

def process_data(data, transform):
    result = []
    for item in data:
        result.append(transform(item))
    return result""",
        "expected": ["Args:", "Returns:", "docstring"]
    }
}


def check_ollama():
    """Check if Ollama is running."""
    try:
        r = requests.get(f"{OLLAMA_URL}/api/tags", timeout=2)
        return r.status_code == 200, r.json().get("models", []) if r.status_code == 200 else []
    except:
        return False, []


def check_models_available(available_models: List[Dict]) -> List[str]:
    """Check which models from DEFAULT_MODELS are available."""
    available_names = [m["name"] for m in available_models]
    found = []
    for model in DEFAULT_MODELS:
        if any(model in name for name in available_names):
            found.append(model)
    return found


def run_benchmark(model: str, task: Dict) -> Dict[str, Any]:
    """Run single benchmark."""
    prompt = task["prompt"]
    expected_keywords = task["expected"]
    
    start_time = time.time()
    
    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "num_predict": 300
                }
            },
            timeout=120
        )
        
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            generated_text = data.get("response", "")
            
            # Quality scoring
            quality_score = 0
            for keyword in expected_keywords:
                if keyword.lower() in generated_text.lower():
                    quality_score += 1
            quality = (quality_score / len(expected_keywords)) * 5  # 0-5 scale
            
            return {
                "success": True,
                "time": elapsed,
                "tokens": len(generated_text.split()),  # Rough estimate
                "quality": min(5, quality),
                "response": generated_text[:200] + "..." if len(generated_text) > 200 else generated_text
            }
        else:
            return {
                "success": False,
                "time": elapsed,
                "error": f"HTTP {response.status_code}"
            }
    except Exception as e:
        return {
            "success": False,
            "time": time.time() - start_time,
            "error": str(e)
        }


def run_all_benchmarks(models: List[str]) -> Dict[str, Dict]:
    """Run benchmarks for all models on all tasks."""
    results = {}
    
    for model in models:
        print(f"\nTesting: {model}")
        results[model] = {}
        
        for task_id, task in TASKS.items():
            print(f"  Task: {task['name']}...", end=" ")
            result = run_benchmark(model, task)
            results[model][task_id] = result
            
            if result["success"]:
                print(f"✅ {result['time']:.1f}s, quality: {result['quality']:.1f}/5")
            else:
                print(f"❌ {result.get('error', 'Unknown')}")
    
    return results


def print_results_table(results: Dict):
    """Print results as table."""
    print()
    print("=" * 80)
    print("Model Comparison Results")
    print("=" * 80)
    
    for task_id, task in TASKS.items():
        print()
        print(f"Task: {task['name']}")
        print("-" * 80)
        print(f"{'Model':<25} {'Time':>8} {'Tokens':>8} {'Quality':>8} {'Tok/s':>8}")
        print("-" * 80)
        
        for model, model_results in results.items():
            result = model_results.get(task_id, {})
            if result.get("success"):
                time_s = result["time"]
                tokens = result["tokens"]
                quality = result["quality"]
                tok_per_sec = tokens / time_s if time_s > 0 else 0
                quality_stars = "⭐" * int(quality)
                
                print(f"{model:<25} {time_s:>7.1f}s {tokens:>8} {quality_stars:>8} {tok_per_sec:>7.1f}")
            else:
                print(f"{model:<25} {'FAILED':>8} {'-':>8} {'-':>8} {'-':>8}")
        
        print("-" * 80)


def save_results(results: Dict):
    """Save results to JSON."""
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = f"benchmark_{timestamp}.json"
    
    with open(filename, 'w') as f:
        json.dump({
            "timestamp": timestamp,
            "ollama_url": OLLAMA_URL,
            "tasks": list(TASKS.keys()),
            "results": results
        }, f, indent=2)
    
    print(f"\nResults saved to: {filename}")


def main():
    print("=" * 80)
    print("Example 25: Local Model Comparison")
    print("=" * 80)
    print()
    
    # Check Ollama
    ollama_ok, available_models = check_ollama()
    if not ollama_ok:
        print("❌ Ollama not running")
        print("   Start: ollama serve")
        return 1
    
    print(f"✅ Ollama running")
    print(f"   Available models: {len(available_models)}")
    
    # Check which models we can test
    models_to_test = check_models_available(available_models)
    
    if not models_to_test:
        print()
        print("❌ No benchmark models found!")
        print("   Install models:")
        for model in DEFAULT_MODELS:
            print(f"      ollama pull {model}")
        return 1
    
    print(f"   Models to test: {', '.join(models_to_test)}")
    print()
    
    # Run benchmarks
    print("Running benchmarks...")
    print("(This may take a few minutes)")
    
    results = run_all_benchmarks(models_to_test)
    
    # Print results
    print_results_table(results)
    
    # Summary
    print()
    print("=" * 80)
    print("Summary")
    print("=" * 80)
    
    for task_id, task in TASKS.items():
        print(f"\n{task['name']}:")
        
        # Find best model for this task
        best_model = None
        best_score = -1
        
        for model, model_results in results.items():
            result = model_results.get(task_id, {})
            if result.get("success"):
                # Score = quality / time (faster + better = higher score)
                score = result["quality"] / max(result["time"], 0.1)
                if score > best_score:
                    best_score = score
                    best_model = model
        
        if best_model:
            print(f"   🏆 Best: {best_model}")
    
    # Save
    save_results(results)
    
    print()
    print("Next steps:")
    print("  - Review benchmark_*.json for detailed results")
    print("  - Use the best model for your specific tasks")
    print("  - Consider: 3B for speed, 7B+ for quality")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
