import os
import sys

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from typing import Optional

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from orchestration.core.orchestrator import ModelOrchestrator

# Add project root to Python path


app = FastAPI(title="AI Model Orchestration API", version="1.0.0")
# rest of code...

# Initialize orchestrator
orchestrator = ModelOrchestrator(max_concurrent_requests=3)


class QueryRequest(BaseModel):
    query: str
    priority: str = "balanced"
    user_preference: Optional[str] = None
    timeout: int = 60
    timeout: int = 60


class QueryResponse(BaseModel):
    response: str
    model_used: str
    response_time: float
    success: bool
    category: str
    orchestration_stats: dict


@app.post("/orchestrate", response_model=QueryResponse)
async def orchestrate_query(request: QueryRequest):
    try:
        result = orchestrator.process_request_sync(
            query=request.query,
            priority=request.priority,
            user_preference=(
                request.user_preference if request.user_preference is not None else ""
            ),
            timeout=request.timeout,
        )

        if result.get("success", False):
            return QueryResponse(
                response=result["response"],
                model_used=result["model"],
                response_time=result["response_time"],
                success=True,
                category="auto-detected",
                orchestration_stats=orchestrator.get_system_status(),
            )
        else:
            raise HTTPException(
                status_code=500, detail=result.get("error", "Unknown error")
            )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/system/status")
async def get_system_status():
    return orchestrator.get_system_status()


@app.get("/system/health")
async def health_check():
    return orchestrator.health_check_all_models()


@app.get("/recommendations/{query}")
async def get_recommendations(query: str):
    return orchestrator.get_routing_recommendations(query)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
