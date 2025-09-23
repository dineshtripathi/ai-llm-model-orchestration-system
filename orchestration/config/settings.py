from dataclasses import dataclass
from typing import Dict


@dataclass
class ModelConfig:
    name: str
    category: str
    size_gb: float
    max_response_time: float
    priority: int


@dataclass
class OrchestrationConfig:
    models: Dict[str, ModelConfig]
    max_concurrent_requests: int = 10
    health_check_interval: int = 300  # 5 minutes
    default_timeout: int = 60
    enable_auto_scaling: bool = True


# Model configurations
MODEL_CONFIGS = {
    "neural-chat:7b-v3.3-q4_0": ModelConfig(
        name="neural-chat:7b-v3.3-q4_0",
        category="fast",
        size_gb=4.1,
        max_response_time=10.0,
        priority=1,
    ),
    "llama3.1:8b": ModelConfig(
        name="llama3.1:8b",
        category="general",
        size_gb=4.9,
        max_response_time=15.0,
        priority=2,
    ),
    "codellama:13b": ModelConfig(
        name="codellama:13b",
        category="coding",
        size_gb=7.4,
        max_response_time=20.0,
        priority=3,
    ),
}

# Default orchestration settings
ORCHESTRATION_CONFIG = OrchestrationConfig(
    models=MODEL_CONFIGS,
    max_concurrent_requests=5,
    health_check_interval=300,
    default_timeout=60,
    enable_auto_scaling=True,
)
