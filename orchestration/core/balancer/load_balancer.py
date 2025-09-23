import subprocess
import time
from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import dataclass
from queue import Queue
from typing import Dict, Optional


@dataclass
class RequestTask:
    request_id: str
    query: str
    model: str
    priority: str
    timestamp: float
    callback: Optional[callable] = None


class LoadBalancer:
    def __init__(self, max_concurrent_requests: int = 3):
        self.max_concurrent_requests = max_concurrent_requests
        self.request_queue = Queue()
        self.active_requests = {}
        self.executor = ThreadPoolExecutor(max_workers=max_concurrent_requests)
        self.running = False
        self.stats = {
            "total_requests": 0,
            "completed_requests": 0,
            "failed_requests": 0,
            "average_response_time": 0,
            "current_load": 0,
        }

    def start(self):
        """Start the load balancer"""
        self.running = True
        print("Load balancer started")

    def stop(self):
        """Stop the load balancer"""
        self.running = False
        self.executor.shutdown(wait=True)
        print("Load balancer stopped")

    def get_current_load(self) -> float:
        """Get current system load (0.0 to 1.0)"""
        return len(self.active_requests) / self.max_concurrent_requests

    def can_accept_request(self) -> bool:
        """Check if system can accept new requests"""
        return len(self.active_requests) < self.max_concurrent_requests

    def execute_model_request(self, task: RequestTask) -> Dict:
        """Execute a single model request"""
        start_time = time.time()

        try:
            # Execute the model request
            result = subprocess.run(
                ["ollama", "run", task.model, task.query],
                capture_output=True,
                text=True,
                timeout=60,
            )

            end_time = time.time()
            response_time = end_time - start_time

            response = {
                "request_id": task.request_id,
                "query": task.query,
                "model": task.model,
                "response": result.stdout.strip() if result.returncode == 0 else None,
                "error": result.stderr if result.returncode != 0 else None,
                "response_time": response_time,
                "timestamp": start_time,
                "success": result.returncode == 0,
            }

            # Update stats
            self._update_stats(response_time, response["success"])

            return response

        except subprocess.TimeoutExpired:
            end_time = time.time()
            response_time = end_time - start_time

            response = {
                "request_id": task.request_id,
                "query": task.query,
                "model": task.model,
                "response": None,
                "error": "Request timeout",
                "response_time": response_time,
                "timestamp": start_time,
                "success": False,
            }

            self._update_stats(response_time, False)
            return response

        except Exception as e:
            end_time = time.time()
            response_time = end_time - start_time

            response = {
                "request_id": task.request_id,
                "query": task.query,
                "model": task.model,
                "response": None,
                "error": str(e),
                "response_time": response_time,
                "timestamp": start_time,
                "success": False,
            }

            self._update_stats(response_time, False)
            return response

        finally:
            # Remove from active requests
            if task.request_id in self.active_requests:
                del self.active_requests[task.request_id]

    def submit_request(
        self, query: str, model: str, priority: str = "normal"
    ) -> Future:
        """Submit a request for processing"""
        if not self.can_accept_request():
            raise Exception("Load balancer at capacity")

        request_id = f"req_{int(time.time() * 1000)}"
        task = RequestTask(
            request_id=request_id,
            query=query,
            model=model,
            priority=priority,
            timestamp=time.time(),
        )

        # Submit to executor
        future = self.executor.submit(self.execute_model_request, task)
        self.active_requests[request_id] = {
            "task": task,
            "future": future,
            "start_time": time.time(),
        }

        self.stats["total_requests"] += 1
        return future

    def _update_stats(self, response_time: float, success: bool):
        """Update performance statistics"""
        if success:
            self.stats["completed_requests"] += 1
        else:
            self.stats["failed_requests"] += 1

        # Update average response time
        total_completed = self.stats["completed_requests"]
        if total_completed > 0:
            current_avg = self.stats["average_response_time"]
            self.stats["average_response_time"] = (
                current_avg * (total_completed - 1) + response_time
            ) / total_completed

        self.stats["current_load"] = self.get_current_load()

    def get_stats(self) -> Dict:
        """Get current load balancer statistics"""
        return {
            **self.stats,
            "active_requests": len(self.active_requests),
            "max_concurrent": self.max_concurrent_requests,
            "queue_size": self.request_queue.qsize(),
        }


if __name__ == "__main__":
    # Test the load balancer
    balancer = LoadBalancer(max_concurrent_requests=2)
    balancer.start()

    print("Load Balancer Test:")
    print("==================")

    # Submit test requests
    test_requests = [
        ("Hello", "neural-chat:7b-v3.3-q4_0"),
        ("What is AI?", "llama3.1:8b"),
        ("Write Python code", "codellama:13b"),
    ]

    futures = []
    for query, model in test_requests:
        try:
            future = balancer.submit_request(query, model)
            futures.append((query, model, future))
            print(f"Submitted: '{query}' to {model}")
        except Exception as e:
            print(f"Failed to submit '{query}': {e}")

    # Wait for results
    for query, model, future in futures:
        try:
            result = future.result(timeout=30)
            print(f"\nResult for '{query}':")
            print(f"  Model: {result['model']}")
            print(f"  Success: {result['success']}")
            print(f"  Response Time: {result['response_time']:.2f}s")
            if result["response"]:
                print(f"  Response: {result['response'][:100]}...")
        except Exception as e:
            print(f"Error getting result for '{query}': {e}")

    # Show stats
    print(f"\nLoad Balancer Stats:")
    stats = balancer.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")

    balancer.stop()
