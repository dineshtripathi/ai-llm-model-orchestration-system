import subprocess
import time
import threading
from datetime import datetime
from typing import Dict, List, Optional
import json

class ModelPool:
    def __init__(self):
        self.models = {
            "neural-chat:7b-v3.3-q4_0": {"category": "fast", "size_gb": 4.1, "status": "unloaded"},
            "llama3.1:8b": {"category": "general", "size_gb": 4.9, "status": "unloaded"},
            "codellama:13b": {"category": "coding", "size_gb": 7.4, "status": "unloaded"},
            "mixtral:8x7b-instruct-v0.1-q4_0": {"category": "analysis", "size_gb": 26, "status": "unloaded"},
            "llama3.1:70b": {"category": "reasoning", "size_gb": 42, "status": "unloaded"}
        }
        
        self.performance_metrics = {}
        self.health_status = {}
        self.last_health_check = {}
        
    def get_model_status(self) -> Dict:
        """Get current status of all models"""
        try:
            result = subprocess.run(['ollama', 'ps'], capture_output=True, text=True)
            active_models = []
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')[1:]  # Skip header
                for line in lines:
                    if line.strip():
                        model_name = line.split()[0]
                        active_models.append(model_name)
            
            # Update model status
            for model in self.models:
                self.models[model]["status"] = "loaded" if model in active_models else "unloaded"
                
            return self.models
            
        except Exception as e:
            print(f"Error checking model status: {e}")
            return self.models
    
    def health_check_model(self, model_name: str) -> Dict:
        """Check health of specific model"""
        start_time = time.time()
        
        try:
            # Simple health check with timeout
            result = subprocess.run(
                ['ollama', 'run', model_name, 'Hello'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            end_time = time.time()
            response_time = end_time - start_time
            
            health_data = {
                "model": model_name,
                "healthy": result.returncode == 0,
                "response_time": round(response_time, 2),
                "timestamp": datetime.now().isoformat(),
                "error": result.stderr if result.returncode != 0 else None
            }
            
            self.health_status[model_name] = health_data
            self.last_health_check[model_name] = datetime.now()
            
            return health_data
            
        except subprocess.TimeoutExpired:
            health_data = {
                "model": model_name,
                "healthy": False,
                "response_time": 30.0,
                "timestamp": datetime.now().isoformat(),
                "error": "Timeout"
            }
            self.health_status[model_name] = health_data
            return health_data
            
        except Exception as e:
            health_data = {
                "model": model_name,
                "healthy": False,
                "response_time": None,
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }
            self.health_status[model_name] = health_data
            return health_data
    
    def get_available_models(self, category: Optional[str] = None) -> List[str]:
        """Get list of available models, optionally filtered by category"""
        self.get_model_status()
        
        available = []
        for model, data in self.models.items():
            if data["status"] == "loaded":
                if category is None or data["category"] == category:
                    # Check if model is healthy (if we have recent health data)
                    if model in self.health_status:
                        if self.health_status[model]["healthy"]:
                            available.append(model)
                    else:
                        available.append(model)  # Assume healthy if no data
        
        return available
    
    def get_model_performance(self, model_name: str) -> Dict:
        """Get performance metrics for a model"""
        return self.performance_metrics.get(model_name, {})
    
    def record_performance(self, model_name: str, response_time: float, success: bool):
        """Record performance metrics for a model"""
        if model_name not in self.performance_metrics:
            self.performance_metrics[model_name] = {
                "total_requests": 0,
                "successful_requests": 0,
                "average_response_time": 0,
                "response_times": []
            }
        
        metrics = self.performance_metrics[model_name]
        metrics["total_requests"] += 1
        
        if success:
            metrics["successful_requests"] += 1
            metrics["response_times"].append(response_time)
            
            # Keep only last 100 response times
            if len(metrics["response_times"]) > 100:
                metrics["response_times"] = metrics["response_times"][-100:]
            
            metrics["average_response_time"] = sum(metrics["response_times"]) / len(metrics["response_times"])

if __name__ == "__main__":
    # Test the model pool
    pool = ModelPool()
    
    print("Current model status:")
    status = pool.get_model_status()
    for model, data in status.items():
        print(f"  {model}: {data['status']} ({data['category']}, {data['size_gb']}GB)")
    
    print("\nAvailable models:")
    available = pool.get_available_models()
    for model in available:
        print(f"  {model}")
    
    # Test health check on first available model
    if available:
        print(f"\nHealth checking {available[0]}...")
        health = pool.health_check_model(available[0])
        print(f"  Healthy: {health['healthy']}")
        print(f"  Response time: {health['response_time']}s")