import os
import sys
from typing import Dict, List

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from rag.vector_store.chroma_manager import ChromaManager


class DocumentProcessor:
    def __init__(self, chroma_manager: ChromaManager = None):
        self.chroma_manager = chroma_manager or ChromaManager()

    def chunk_text(
        self, text: str, chunk_size: int = 500, overlap: int = 50
    ) -> List[str]:
        """Split text into overlapping chunks"""
        words = text.split()
        chunks = []

        for i in range(0, len(words), chunk_size - overlap):
            chunk = " ".join(words[i : i + chunk_size])
            if chunk.strip():
                chunks.append(chunk.strip())

        return chunks

    def process_text_file(self, file_path: str) -> List[Dict]:
        """Process a single text file"""
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()

            chunks = self.chunk_text(content)

            documents = []
            for i, chunk in enumerate(chunks):
                doc_data = {
                    "content": chunk,
                    "metadata": {
                        "source": file_path,
                        "chunk_id": i,
                        "total_chunks": len(chunks),
                        "file_name": os.path.basename(file_path),
                    },
                }
                documents.append(doc_data)

            return documents

        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            return []

    def process_directory(
        self, directory: str, file_extensions: List[str] = [".txt", ".md"]
    ) -> List[Dict]:
        """Process all files in a directory"""
        all_documents = []

        for root, dirs, files in os.walk(directory):
            for file in files:
                if any(file.endswith(ext) for ext in file_extensions):
                    file_path = os.path.join(root, file)
                    docs = self.process_text_file(file_path)
                    all_documents.extend(docs)

        return all_documents

    def ingest_documents(self, documents: List[Dict]) -> bool:
        """Ingest processed documents into ChromaDB"""
        try:
            contents = [doc["content"] for doc in documents]
            metadatas = [doc["metadata"] for doc in documents]
            ids = [
                f"{doc['metadata']['source']}_{doc['metadata']['chunk_id']}"
                for doc in documents
            ]

            # Clean IDs to avoid ChromaDB issues
            ids = [id.replace("/", "_").replace("\\", "_") for id in ids]

            self.chroma_manager.add_documents(contents, metadatas, ids)
            return True

        except Exception as e:
            print(f"Error ingesting documents: {e}")
            return False

    def ingest_from_directory(self, directory: str) -> Dict:
        """Complete pipeline: process directory and ingest to ChromaDB"""
        print(f"Processing documents from: {directory}")

        documents = self.process_directory(directory)

        if not documents:
            return {"success": False, "message": "No documents found to process"}

        success = self.ingest_documents(documents)

        return {
            "success": success,
            "documents_processed": len(documents),
            "files_processed": len(set(doc["metadata"]["source"] for doc in documents)),
        }

    def ingest_crawled_data(self, crawled_data: List[Dict]) -> Dict:
        """Convert crawled data format to document format and ingest"""
        if not crawled_data:
            return {"success": False, "message": "No crawled data to ingest"}

        documents = []

        for item in crawled_data:
            # Convert crawled data format to document format
            content = (
                f"Title: {item.get('title', '')}\n\nContent: {item.get('content', '')}"
            )

            # Create document chunks
            chunks = self.chunk_text(content)

            for i, chunk in enumerate(chunks):
                # Convert tags list to string for ChromaDB compatibility
                tags = item.get("tags", [])
                tags_str = ", ".join(tags) if isinstance(tags, list) else str(tags)

                doc_data = {
                    "content": chunk,
                    "metadata": {
                        "source": item.get("url", ""),
                        "title": item.get("title", ""),
                        "chunk_id": i,
                        "total_chunks": len(chunks),
                        "source_type": item.get("source", "unknown"),
                        "scraped_at": item.get("scraped_at", ""),
                        "tags": tags_str,  # Convert list to string
                        "score": int(item.get("score", 0)) if "score" in item else 0,
                    },
                }
                documents.append(doc_data)

        # Use existing ingest_documents method
        success = self.ingest_documents(documents)

        return {
            "success": success,
            "items_processed": len(crawled_data),
            "documents_created": len(documents),
            "sources": [item.get("source", "unknown") for item in crawled_data],
        }


if __name__ == "__main__":
    # Test document processor
    processor = DocumentProcessor()

    # Create test documents
    os.makedirs("test_docs", exist_ok=True)

    test_files = {
        "test_docs/python_basics.txt": """
        Python is a versatile programming language known for its simplicity and readability.
        It supports multiple programming paradigms including object-oriented, functional, and procedural programming.
        Python is widely used in web development, data science, artificial intelligence, and automation.
        The language features dynamic typing and automatic memory management.
        """,
        "test_docs/machine_learning.txt": """
        Machine learning is a subset of artificial intelligence that enables computers to learn and improve from experience.
        Common algorithms include linear regression, decision trees, neural networks, and support vector machines.
        Applications include image recognition, natural language processing, recommendation systems, and predictive analytics.
        The field requires understanding of statistics, mathematics, and programming.
        """,
        "test_docs/web_development.txt": """
        Web development involves creating applications that run on web browsers.
        Frontend technologies include HTML, CSS, JavaScript, and frameworks like React and Vue.
        Backend development uses languages like Python, Node.js, Java, and frameworks like Django and Express.
        Modern web development often involves APIs, databases, and cloud deployment.
        """,
    }

    # Create test files
    for file_path, content in test_files.items():
        with open(file_path, "w") as f:
            f.write(content.strip())

    # Process and ingest
    result = processor.ingest_from_directory("test_docs")
    print(f"Ingestion result: {result}")

    # Test search
    search_results = processor.chroma_manager.search_documents(
        "What is Python used for?", n_results=3
    )
    print("\nSearch Results:")
    for i, doc in enumerate(search_results["documents"]):
        print(f"{i+1}. {doc}")

    # Cleanup
    import shutil

    shutil.rmtree("test_docs")
