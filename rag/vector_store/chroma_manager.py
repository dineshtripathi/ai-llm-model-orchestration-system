import os
from typing import Dict, List

import chromadb
from sentence_transformers import SentenceTransformer


class ChromaManager:
    def __init__(self, persist_directory: str = "./chroma_db"):
        """Initialize ChromaDB with persistence"""
        self.persist_directory = persist_directory

        # Create directory if it doesn't exist
        os.makedirs(persist_directory, exist_ok=True)

        # Initialize ChromaDB client with persistence
        self.client = chromadb.PersistentClient(path=persist_directory)

        # Initialize embedding model
        self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

        # Default collection name
        self.collection_name = "documents"
        self.collection = None

        # Initialize collection
        self._initialize_collection()

    def _initialize_collection(self):
        """Initialize or get existing collection"""
        try:
            # Try to get existing collection
            self.collection = self.client.get_collection(name=self.collection_name)
            print(
                f"Loaded existing collection '{self.collection_name}' with {self.collection.count()} documents"
            )
        except Exception:
            # Create new collection
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "Document collection for RAG system"},
            )
            print(f"Created new collection '{self.collection_name}'")

    def add_documents(
        self, documents: List[str], metadatas: List[Dict] = None, ids: List[str] = None
    ):
        """Add documents to the collection"""
        if metadatas is None:
            metadatas = [{"source": f"doc_{i}"} for i in range(len(documents))]

        if ids is None:
            ids = [f"doc_{i}_{hash(doc)}" for i, doc in enumerate(documents)]

        # Generate embeddings
        embeddings = self.embedding_model.encode(documents).tolist()

        # Add to collection
        self.collection.add(
            documents=documents, embeddings=embeddings, metadatas=metadatas, ids=ids
        )

        print(f"Added {len(documents)} documents to collection")
        return ids

    def search_documents(self, query: str, n_results: int = 5) -> Dict:
        """Search for relevant documents"""
        # Generate query embedding
        query_embedding = self.embedding_model.encode([query]).tolist()

        # Search in collection
        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=n_results,
            include=["documents", "distances", "metadatas"],
        )

        return {
            "documents": results["documents"][0],
            "distances": results["distances"][0],
            "metadatas": results["metadatas"][0],
            "query": query,
        }

    def get_collection_stats(self) -> Dict:
        """Get collection statistics"""
        return {
            "total_documents": self.collection.count(),
            "collection_name": self.collection_name,
            "persist_directory": self.persist_directory,
        }

    def delete_collection(self):
        """Delete the collection"""
        self.client.delete_collection(name=self.collection_name)
        print(f"Deleted collection '{self.collection_name}'")


if __name__ == "__main__":
    # Test the ChromaManager
    chroma = ChromaManager()

    # Test documents
    test_docs = [
        "Python is a high-level programming language with dynamic semantics.",
        "Machine learning is a subset of artificial intelligence that focuses on algorithms.",
        "FastAPI is a modern, fast web framework for building APIs with Python.",
        "ChromaDB is a vector database designed for AI applications.",
        "Streamlit is an open-source app framework for machine learning projects.",
    ]

    # Add test documents
    chroma.add_documents(test_docs)

    # Test search
    results = chroma.search_documents("What is Python?", n_results=3)

    print("\nSearch Results:")
    for i, (doc, distance) in enumerate(
        zip(results["documents"], results["distances"])
    ):
        print(f"{i+1}. Distance: {distance:.3f}")
        print(f"   Document: {doc}")

    # Show stats
    stats = chroma.get_collection_stats()
    print(f"\nCollection Stats: {stats}")
