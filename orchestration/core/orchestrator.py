import os
import sys
import time
from concurrent.futures import Future
from typing import Dict

# Add the parent directory to path to find orchestration module
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from orchestration.core.balancer.load_balancer import LoadBalancer
from orchestration.core.pool.model_pool import ModelPool
from orchestration.core.router.model_router import ModelRouter


class ModelOrchestrator:
    def __init__(self, max_concurrent_requests: int = 3):
        self.model_pool = ModelPool()
        self.router = ModelRouter()
        self.load_balancer = LoadBalancer(max_concurrent_requests)
        self.orchestration_stats = {
            "total_requests": 0,
            "successful_routes": 0,
            "failed_routes": 0,
            "average_routing_time": 0,
        }

        # Start the load balancer
        self.load_balancer.start()

    def process_request(
        self, query: str, priority: str = "balanced", user_preference: str = None
    ) -> Future:
        """
        Main orchestration method that processes a user request
        Returns a Future that will contain the response
        """
        start_time = time.time()

        try:
            # Step 1: Route the request
            routing_decision = self.router.route_request(query, priority)

            # Step 2: Override model if user specified preference
            selected_model = (
                user_preference
                if user_preference
                else routing_decision["selected_model"]
            )

            # Step 3: Submit to load balancer
            future = self.load_balancer.submit_request(query, selected_model, priority)

            # Step 4: Update orchestration stats
            routing_time = time.time() - start_time
            self._update_orchestration_stats(routing_time, True)

            return future

        except Exception as e:
            routing_time = time.time() - start_time
            self._update_orchestration_stats(routing_time, False)

            # Return a failed future
            failed_future = self.load_balancer.executor.submit(
                lambda: {
                    "error": f"Orchestration failed: {str(e)}",
                    "success": False,
                    "orchestration": {
                        "routing_time": routing_time,
                        "orchestration_timestamp": start_time,
                    },
                }
            )

            return failed_future

    def process_request_sync(
        self,
        query: str,
        priority: str = "balanced",
        user_preference: str = None,
        timeout: int = 60,
    ) -> Dict:
        """
        Synchronous version of process_request
        """
        future = self.process_request(query, priority, user_preference)
        try:
            return future.result(timeout=timeout)
        except Exception as e:
            return {
                "error": f"Request timeout or failed: {str(e)}",
                "success": False,
                "query": query,
                "timeout": timeout,
            }

    def get_system_status(self) -> Dict:
        """Get comprehensive system status"""
        return {
            "model_pool": {
                "total_models": len(self.model_pool.models),
                "available_models": len(self.model_pool.get_available_models()),
                "model_status": self.model_pool.get_model_status(),
                "health_status": self.model_pool.health_status,
            },
            "load_balancer": self.load_balancer.get_stats(),
            "orchestration": self.orchestration_stats,
            "system_load": self.load_balancer.get_current_load(),
            "timestamp": time.time(),
        }

    def health_check_all_models(self) -> Dict:
        """Perform health check on all models"""
        health_results = {}

        for model_name in self.model_pool.models.keys():
            health_results[model_name] = self.model_pool.health_check_model(model_name)

        return health_results

    def get_routing_recommendations(self, query: str) -> Dict:
        """Get routing recommendations without executing"""
        routing_decision = self.router.route_request(query)
        system_status = self.get_system_status()

        return {
            "query": query,
            "recommended_model": routing_decision["selected_model"],
            "category": routing_decision["category"],
            "alternative_models": routing_decision["available_models"],
            "system_load": system_status["system_load"],
            "estimated_wait_time": self._estimate_wait_time(),
        }

    def _estimate_wait_time(self) -> float:
        """Estimate wait time based on current load"""
        current_load = self.load_balancer.get_current_load()
        avg_response_time = self.load_balancer.stats["average_response_time"]

        if avg_response_time == 0:
            avg_response_time = 10  # Default estimate

        # Simple estimation: more load = longer wait
        wait_multiplier = 1 + current_load
        return avg_response_time * wait_multiplier

    def _update_orchestration_stats(self, routing_time: float, success: bool):
        """Update orchestration statistics"""
        self.orchestration_stats["total_requests"] += 1

        if success:
            self.orchestration_stats["successful_routes"] += 1
        else:
            self.orchestration_stats["failed_routes"] += 1

        # Update average routing time
        total_successful = self.orchestration_stats["successful_routes"]
        if total_successful > 0 and success:
            current_avg = self.orchestration_stats["average_routing_time"]
            self.orchestration_stats["average_routing_time"] = (
                current_avg * (total_successful - 1) + routing_time
            ) / total_successful

    def shutdown(self):
        """Gracefully shutdown the orchestrator"""
        self.load_balancer.stop()
        print("Orchestrator shutdown complete")


if __name__ == "__main__":
    # Test the complete orchestrator
    orchestrator = ModelOrchestrator(max_concurrent_requests=2)

    print("Model Orchestrator Test:")
    print("=======================")

    test_queries = [
        "Hello, how are you?",
        "Write a Python function to calculate fibonacci numbers",
        "Analyze the benefits of renewable energy",
        "What is machine learning?",
    ]

    for query in test_queries:
        print(f"\nProcessing: '{query}'")

        # Get recommendations first
        recommendations = orchestrator.get_routing_recommendations(query)
        print(f"Recommended model: {recommendations['recommended_model']}")
        print(f"Category: {recommendations['category']}")
        print(f"Estimated wait: {recommendations['estimated_wait_time']:.2f}s")

        # Process the request
        result = orchestrator.process_request_sync(query, timeout=30)

        if result.get("success", False):
            print(f"Response time: {result['response_time']:.2f}s")
            print(f"Response: {result['response'][:100]}...")
        else:
            print(f"Failed: {result.get('error', 'Unknown error')}")

    # Show system status
    print(f"\nSystem Status:")
    status = orchestrator.get_system_status()
    print(f"Available models: {status['model_pool']['available_models']}")
    print(f"System load: {status['system_load']:.2f}")
    print(f"Total requests: {status['orchestration']['total_requests']}")

    orchestrator.shutdown()
