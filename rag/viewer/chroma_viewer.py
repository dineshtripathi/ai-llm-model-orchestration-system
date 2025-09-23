import os
import sys

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))


from rag.vector_store.chroma_manager import ChromaManager


class ChromaViewer:
    def __init__(self):
        self.chroma = ChromaManager()

    def show_collection_info(self):
        """Display basic collection information"""
        stats = self.chroma.get_collection_stats()
        print("=== ChromaDB Collection Info ===")
        print(f"Total documents: {stats['total_documents']}")
        print(f"Collection name: {stats['collection_name']}")
        print(f"Storage location: {stats['persist_directory']}")

    def browse_documents(self, limit: int = 10):
        """Browse documents in the collection"""
        print(f"\n=== First {limit} Documents ===")

        # Get documents using ChromaDB's get method
        results = self.chroma.collection.get(
            limit=limit, include=["documents", "metadatas"]
        )

        for i, (doc, metadata) in enumerate(
            zip(results["documents"], results["metadatas"])
        ):
            print(f"\n--- Document {i+1} ---")
            print(f"Source: {metadata.get('source', 'Unknown')}")
            print(f"Title: {metadata.get('title', 'No title')}")
            print(f"Source Type: {metadata.get('source_type', 'Unknown')}")
            print(f"Content: {doc[:200]}...")
            print("-" * 50)

    def search_by_source_type(self, source_type: str):
        """Find documents by source type"""
        print(f"\n=== Documents from {source_type} ===")

        # Search using metadata filtering
        results = self.chroma.collection.get(
            where={"source_type": source_type}, include=["documents", "metadatas"]
        )

        print(f"Found {len(results['documents'])} documents from {source_type}")

        for i, (doc, metadata) in enumerate(
            zip(results["documents"], results["metadatas"])
        ):
            print(f"\n{i+1}. {metadata.get('title', 'No title')}")
            print(f"   URL: {metadata.get('source', 'No URL')}")
            print(f"   Content: {doc[:150]}...")

    def show_source_types(self):
        """Show all available source types"""
        results = self.chroma.collection.get(include=["metadatas"])

        source_types = {}
        for metadata in results["metadatas"]:
            source_type = metadata.get("source_type", "unknown")
            source_types[source_type] = source_types.get(source_type, 0) + 1

        print("\n=== Available Source Types ===")
        for source_type, count in sorted(source_types.items()):
            print(f"{source_type}: {count} documents")

    def search_content(self, query: str, n_results: int = 5):
        """Search content semantically"""
        print(f"\n=== Search Results for: '{query}' ===")

        results = self.chroma.search_documents(query, n_results)

        for i, (doc, distance, metadata) in enumerate(
            zip(
                results["documents"], results["distances"], results.get("metadatas", [])
            )
        ):
            similarity = 1 - distance
            print(f"\n{i+1}. Similarity: {similarity:.3f}")
            print(f"   Source: {metadata.get('source_type', 'unknown')}")
            print(f"   Title: {metadata.get('title', 'No title')}")
            print(f"   Content: {doc[:200]}...")


if __name__ == "__main__":
    viewer = ChromaViewer()

    # Show collection overview
    viewer.show_collection_info()

    # Show source types
    viewer.show_source_types()

    # Browse some documents
    viewer.browse_documents(5)

    # Show documents by source
    viewer.search_by_source_type("stackoverflow")

    # Search content
    viewer.search_content("python programming", 3)
