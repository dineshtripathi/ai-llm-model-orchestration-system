import os
import sys

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import tempfile

from rag.ingestion.document_processor import DocumentProcessor

# Add project root to path


def test_document_chunking():
    """Test text chunking functionality"""
    processor = DocumentProcessor()

    text = "This is a test document. " * 100  # Create long text
    chunks = processor.chunk_text(text, chunk_size=50, overlap=10)

    assert len(chunks) > 1
    assert all(isinstance(chunk, str) for chunk in chunks)


def test_document_processing():
    """Test document processing from file"""
    processor = DocumentProcessor()

    # Create temporary file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("Test content for document processing.")
        temp_file = f.name

    try:
        docs = processor.process_text_file(temp_file)
        assert len(docs) > 0
        assert docs[0]["content"] == "Test content for document processing."
        assert "metadata" in docs[0]
    finally:
        os.unlink(temp_file)
