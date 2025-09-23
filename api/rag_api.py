import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from rag.retrieval.rag_orchestrator import RAGOrchestrator

app = FastAPI(title="RAG + Model Orchestration API", version="1.0.0")
rag_orchestrator = RAGOrchestrator()


class RAGRequest(BaseModel):
    query: str
    use_rag: bool = True
    n_results: int = 3
    priority: str = "balanced"


@app.post("/rag/query")
async def rag_query(request: RAGRequest):
    if request.use_rag:
        result = rag_orchestrator.search_and_generate(
            query=request.query, n_results=request.n_results, priority=request.priority
        )
    else:
        result = rag_orchestrator.simple_chat(request.query, use_rag=False)

    return result


@app.get("/rag/stats")
async def rag_stats():
    return rag_orchestrator.chroma_manager.get_collection_stats()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)
