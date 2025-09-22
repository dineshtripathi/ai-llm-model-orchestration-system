import sys
import os
from typing import Dict, List, Optional

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from orchestration.core.orchestrator import ModelOrchestrator
from rag.vector_store.chroma_manager import ChromaManager

class RAGOrchestrator:
    def __init__(self, model_orchestrator: ModelOrchestrator = None, 
                 chroma_manager: ChromaManager = None):
        """Initialize RAG system with model orchestration"""
        self.model_orchestrator = model_orchestrator or ModelOrchestrator()
        self.chroma_manager = chroma_manager or ChromaManager()
        
    def search_and_generate(self, query: str, n_results: int = 3, 
                          priority: str = "balanced") -> Dict:
        """Complete RAG pipeline: retrieve documents and generate response"""
        
        # Step 1: Retrieve relevant documents
        search_results = self.chroma_manager.search_documents(query, n_results)
        
        # Step 2: Build context-enhanced prompt
        context_docs = "\n\n".join([
            f"Document {i+1}: {doc}" 
            for i, doc in enumerate(search_results["documents"])
        ])
        
        enhanced_query = f"""Based on the following context documents, please answer the question.

Context:
{context_docs}

Question: {query}

Please provide a comprehensive answer based on the context provided."""

        # Step 3: Route to appropriate model with enhanced prompt
        result = self.model_orchestrator.process_request_sync(
            query=enhanced_query, 
            priority=priority,
            timeout=60
        )
        
        # Step 4: Combine results
        return {
            "original_query": query,
            "retrieved_documents": search_results["documents"],
            "document_distances": search_results["distances"],
            "enhanced_prompt": enhanced_query,
            "model_response": result.get("response", ""),
            "model_used": result.get("model", ""),
            "response_time": result.get("response_time", 0),
            "success": result.get("success", False),
            "rag_metadata": {
                "n_documents_retrieved": len(search_results["documents"]),
                "total_documents_in_db": self.chroma_manager.get_collection_stats()["total_documents"]
            }
        }
    
    def simple_chat(self, query: str, use_rag: bool = True) -> Dict:
        """Simple chat interface with optional RAG"""
        if use_rag:
            return self.search_and_generate(query)
        else:
            # Direct model call without RAG
            result = self.model_orchestrator.process_request_sync(query)
            return {
                "original_query": query,
                "model_response": result.get("response", ""),
                "model_used": result.get("model", ""),
                "response_time": result.get("response_time", 0),
                "success": result.get("success", False),
                "rag_used": False
            }

if __name__ == "__main__":
    # Test RAG + Model Orchestration
    rag_orchestrator = RAGOrchestrator()
    
    test_queries = [
        "What is Python used for?",
        "Tell me about machine learning algorithms",
        "How do I build web applications?"
    ]
    
    for query in test_queries:
        print(f"\n{'='*50}")
        print(f"Query: {query}")
        print('='*50)
        
        # Test with RAG
        rag_result = rag_orchestrator.search_and_generate(query)
        
        print(f"Model used: {rag_result['model_used']}")
        print(f"Documents retrieved: {rag_result['rag_metadata']['n_documents_retrieved']}")
        print(f"Response time: {rag_result['response_time']:.2f}s")
        print(f"\nResponse:\n{rag_result['model_response']}")