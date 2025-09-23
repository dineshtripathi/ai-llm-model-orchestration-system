import os
import sys

# Add project root to Python path
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
)

import time
from typing import Dict, Optional

from orchestration.core.pool.model_pool import ModelPool


class ModelRouter:
    def __init__(self):
        self.model_pool = ModelPool()
        self.routing_rules = {
            "coding": ["codellama:13b", "llama3.1:8b"],
            "fast": ["neural-chat:7b-v3.3-q4_0", "llama3.1:8b"],
            "analysis": ["mixtral:8x7b-instruct-v0.1-q4_0", "llama3.1:70b"],
            "reasoning": ["llama3.1:70b", "mixtral:8x7b-instruct-v0.1-q4_0"],
            "general": ["llama3.1:8b", "neural-chat:7b-v3.3-q4_0"],
        }

    def analyze_query(self, query: str) -> str:
        """Analyze query to determine best model category"""
        query_lower = query.lower()

        # Coding keywords
        coding_keywords = [
            "python",
            "code",
            "function",
            "class",
            "debug",
            "programming",
            "script",
        ]
        if any(keyword in query_lower for keyword in coding_keywords):
            return "coding"

        # Analysis keywords
        analysis_keywords = ["analyze", "compare", "evaluate", "assessment", "review"]
        if any(keyword in query_lower for keyword in analysis_keywords):
            return "analysis"

        # Complex reasoning keywords
        reasoning_keywords = [
            "explain",
            "complex",
            "detailed",
            "comprehensive",
            "theory",
        ]
        if any(keyword in query_lower for keyword in reasoning_keywords):
            return "reasoning"

        # Speed priority (short queries)
        if len(query.split()) <= 5:
            return "fast"

        return "general"

    def select_best_model(
        self, category: str, priority: str = "balanced"
    ) -> Optional[str]:
        """Select best available model for category and priority"""
        candidate_models = self.routing_rules.get(category, ["llama3.1:8b"])
        available_models = self.model_pool.get_available_models()

        # Find first available model from candidates
        for model in candidate_models:
            if model in available_models:
                # Check model health
                health = self.model_pool.health_status.get(model)
                if health is None or health.get("healthy", True):
                    return model

        # Fallback: any available model
        if available_models:
            return available_models[0]

        # No models available - return first candidate (will trigger loading)
        return candidate_models[0]

    def route_request(self, query: str, priority: str = "balanced") -> Dict:
        """Route request to best model and return routing decision"""

        # Update model status
        self.model_pool.get_model_status()

        # Analyze query
        category = self.analyze_query(query)

        # Select model
        selected_model = self.select_best_model(category, priority)

        # Prepare routing decision
        routing_decision = {
            "query": query,
            "category": category,
            "selected_model": selected_model,
            "priority": priority,
            "available_models": self.model_pool.get_available_models(),
            "timestamp": time.time(),
        }

        return routing_decision


if __name__ == "__main__":
    # Test the router
    router = ModelRouter()

    test_queries = [
        "Write a Python function to sort a list",
        "Hello",
        "Analyze the pros and cons of AI development",
        "What is machine learning?",
        "Hi",
    ]

    print("Model Router Test:")
    print("==================")

    for query in test_queries:
        decision = router.route_request(query)
        print(f"\nQuery: '{query}'")
        print(f"Category: {decision['category']}")
        print(f"Selected Model: {decision['selected_model']}")
        print(f"Available Models: {len(decision['available_models'])}")
