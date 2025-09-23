import os
import sys

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))


# Add project root to path

from orchestration.core.pool.model_pool import ModelPool


def test_model_pool_initialization():
    """Test that ModelPool initializes correctly"""
    pool = ModelPool()
    assert hasattr(pool, "models")
    assert len(pool.models) == 5  # We have 5 configured models


def test_model_pool_get_model_status():
    """Test model status retrieval"""
    pool = ModelPool()
    status = pool.get_model_status()
    assert isinstance(status, dict)
    assert len(status) == 5


def test_model_categories():
    """Test that models have correct categories"""
    pool = ModelPool()

    # Check specific model categories
    assert pool.models["neural-chat:7b-v3.3-q4_0"]["category"] == "fast"
    assert pool.models["codellama:13b"]["category"] == "coding"
    assert pool.models["mixtral:8x7b-instruct-v0.1-q4_0"]["category"] == "analysis"
