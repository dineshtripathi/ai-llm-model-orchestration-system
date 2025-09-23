import json
import os
import sys

import requests
import streamlit as st

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from rag.ingestion.document_processor import DocumentProcessor
from rag.retrieval.rag_orchestrator import RAGOrchestrator

st.set_page_config(
    page_title="RAG + Model Orchestration Dashboard", page_icon="🔍", layout="wide"
)


# Initialize components
@st.cache_resource
def init_rag_system():
    return RAGOrchestrator(), DocumentProcessor()


rag_orchestrator, doc_processor = init_rag_system()

st.title("RAG + Model Orchestration Dashboard")

# Sidebar for system management
with st.sidebar:
    st.header("System Controls")

    # Document Management
    st.subheader("Document Management")

    # Show current document stats
    stats = rag_orchestrator.chroma_manager.get_collection_stats()
    st.metric("Documents in Database", stats["total_documents"])

    # File upload for new documents
    uploaded_files = st.file_uploader(
        "Upload Documents", accept_multiple_files=True, type=["txt", "md"]
    )

    if uploaded_files and st.button("Process Uploaded Files"):
        success_count = 0
        for uploaded_file in uploaded_files:
            try:
                # Save uploaded file temporarily
                temp_path = f"temp_{uploaded_file.name}"
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

                # Process the file
                docs = doc_processor.process_text_file(temp_path)
                doc_processor.ingest_documents(docs)
                success_count += 1

                # Clean up
                os.remove(temp_path)

            except Exception as e:
                st.error(f"Error processing {uploaded_file.name}: {e}")

        st.success(f"Successfully processed {success_count} files")
        st.rerun()

# Main interface with tabs
tab1, tab2, tab3, tab4 = st.tabs(
    ["RAG Query", "Document Search", "System Status", "Database Explorer"]
)

with tab1:
    st.header("RAG-Enhanced Query Interface")

    col1, col2 = st.columns([3, 1])

    with col1:
        query = st.text_area("Enter your query:", height=100)

    with col2:
        use_rag = st.checkbox("Use RAG", value=True)
        priority = st.selectbox("Priority:", ["balanced", "speed", "accuracy"])
        n_results = st.slider("Documents to retrieve:", 1, 10, 3)

    if st.button("Submit Query", type="primary"):
        if query.strip():
            with st.spinner("Processing query..."):
                if use_rag:
                    result = rag_orchestrator.search_and_generate(
                        query=query, n_results=n_results, priority=priority
                    )
                else:
                    result = rag_orchestrator.simple_chat(query, use_rag=False)

                if result.get("success", False):
                    # Display response
                    st.subheader("Response")
                    st.write(result["model_response"])

                    # Performance metrics
                    col_metric1, col_metric2, col_metric3 = st.columns(3)
                    with col_metric1:
                        st.metric("Model Used", result["model_used"])
                    with col_metric2:
                        st.metric("Response Time", f"{result['response_time']:.2f}s")
                    with col_metric3:
                        if use_rag:
                            st.metric(
                                "Documents Used",
                                result["rag_metadata"]["n_documents_retrieved"],
                            )
                        else:
                            st.metric("RAG Used", "No")

                    # Show retrieved documents if RAG was used
                    if use_rag and "retrieved_documents" in result:
                        st.subheader("Retrieved Context Documents")
                        for i, (doc, distance) in enumerate(
                            zip(
                                result["retrieved_documents"],
                                result.get("document_distances", []),
                            )
                        ):
                            with st.expander(
                                f"Document {i+1} (Similarity: {1-distance:.3f})"
                            ):
                                st.write(doc)
                else:
                    st.error(f"Query failed: {result.get('error', 'Unknown error')}")

with tab2:
    st.header("Document Search")

    search_query = st.text_input("Search documents:")
    search_results_count = st.slider("Number of results:", 1, 10, 5)

    if st.button("Search Documents"):
        if search_query.strip():
            search_results = rag_orchestrator.chroma_manager.search_documents(
                search_query, n_results=search_results_count
            )

            st.subheader("Search Results")
            for i, (doc, distance) in enumerate(
                zip(search_results["documents"], search_results["distances"])
            ):
                similarity = 1 - distance
                st.write(f"**Result {i+1}** (Similarity: {similarity:.3f})")
                st.write(doc)
                st.divider()

with tab3:
    st.header("System Status")

    # RAG System Stats
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Document Database")
        db_stats = rag_orchestrator.chroma_manager.get_collection_stats()
        st.json(db_stats)

    with col2:
        st.subheader("Model Orchestration")
        orchestration_stats = rag_orchestrator.model_orchestrator.get_system_status()
        st.json(
            {
                "available_models": orchestration_stats["model_pool"][
                    "available_models"
                ],
                "total_requests": orchestration_stats["orchestration"][
                    "total_requests"
                ],
                "system_load": orchestration_stats["system_load"],
            }
        )
# Add this as a new tab in your dashboard
with tab4:  # Add this as the 4th tab
    st.header("Database Explorer")

    # Collection stats
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Collection Overview")
        stats = rag_orchestrator.chroma_manager.get_collection_stats()
        st.metric("Total Documents", stats["total_documents"])

        # Show source type breakdown
        results = rag_orchestrator.chroma_manager.collection.get(include=["metadatas"])
        source_types = {}
        for metadata in results["metadatas"]:
            source_type = metadata.get("source_type", "unknown")
            source_types[source_type] = source_types.get(source_type, 0) + 1

        st.subheader("Source Types")
        for source_type, count in source_types.items():
            st.write(f"**{source_type}**: {count} documents")

    with col2:
        st.subheader("Browse Documents")

        # Filter by source type
        selected_source = st.selectbox(
            "Filter by source:", ["All"] + list(source_types.keys())
        )

        if selected_source == "All":
            docs = rag_orchestrator.chroma_manager.collection.get(
                limit=20, include=["documents", "metadatas"]
            )
        else:
            docs = rag_orchestrator.chroma_manager.collection.get(
                where={"source_type": selected_source},
                limit=20,
                include=["documents", "metadatas"],
            )

        for i, (doc, metadata) in enumerate(zip(docs["documents"], docs["metadatas"])):
            with st.expander(f"{metadata.get('title', 'No title')[:50]}..."):
                st.write(f"**Source:** {metadata.get('source', 'Unknown')}")
                st.write(f"**Type:** {metadata.get('source_type', 'Unknown')}")
                st.write(f"**Content:** {doc[:300]}...")

    # Quick performance test
    st.subheader("System Performance Test")
    if st.button("Run Performance Test"):
        test_queries = [
            "What is Python?",
            "Tell me about machine learning",
            "How to build web apps?",
        ]

        results = []
        for test_query in test_queries:
            result = rag_orchestrator.search_and_generate(test_query, n_results=2)
            results.append(
                {
                    "Query": test_query,
                    "Model": result["model_used"],
                    "Response Time": f"{result['response_time']:.2f}s",
                    "Success": result["success"],
                }
            )

        st.table(results)

        # Add to sidebar in rag_dashboard.py
st.subheader("Web Crawler")
if st.button("Crawl Latest Information"):
    crawler = WebCrawler()
    result = crawler.crawl_and_ingest()
    st.success(
        f"Crawled {result['urls_processed']} sources, created {result['documents_created']} documents"
    )

# Footer
st.markdown("---")
st.caption(
    "RAG + Model Orchestration System - Intelligent Document Retrieval with Multi-Model AI"
)
