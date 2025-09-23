import streamlit as st
import requests
import json
import sys
import os
import time

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from rag.retrieval.rag_orchestrator import RAGOrchestrator
from rag.ingestion.document_processor import DocumentProcessor
from rag.crawler.api_crawler import APICrawler

st.set_page_config(
    page_title="Complete AI System Dashboard",
    page_icon="🤖",
    layout="wide"
)

# Initialize components
@st.cache_resource
def init_all_systems():
    return RAGOrchestrator(), DocumentProcessor(), APICrawler()

rag_orchestrator, doc_processor, web_crawler = init_all_systems()

st.title("🤖 Complete AI Orchestration System")

# Enhanced sidebar with all controls
with st.sidebar:
    st.header("System Controls")
    
    # Document Management
    st.subheader("📚 Document Management")
    stats = rag_orchestrator.chroma_manager.get_collection_stats()
    st.metric("Documents in Database", stats["total_documents"])
    
    # File upload
    uploaded_files = st.file_uploader(
        "Upload Documents", 
        accept_multiple_files=True,
        type=['txt', 'md']
    )
    
    if uploaded_files and st.button("Process Uploaded Files"):
        success_count = 0
        for uploaded_file in uploaded_files:
            try:
                temp_path = f"temp_{uploaded_file.name}"
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                docs = doc_processor.process_text_file(temp_path)
                doc_processor.ingest_documents(docs)
                success_count += 1
                os.remove(temp_path)
                
            except Exception as e:
                st.error(f"Error processing {uploaded_file.name}: {e}")
        
        st.success(f"Successfully processed {success_count} files")
        st.rerun()
    
    # Web Crawler Controls
    st.subheader("🕷️ Web Crawler")
    
    crawler_type = st.selectbox(
        "Crawler Type:",
        ["Quick Crawl", "Custom Search", "Comprehensive Crawl"]
    )
    
    if crawler_type == "Custom Search":
        custom_queries = st.text_area(
            "Enter search queries (one per line):",
            placeholder="artificial intelligence\nmachine learning\nfastapi tutorial"
        ).strip().split('\n') if st.text_area(
            "Enter search queries (one per line):",
            placeholder="artificial intelligence\nmachine learning\nfastapi tutorial"
        ).strip() else []
    
    if st.button("🚀 Start Web Crawl", type="primary"):
        if crawler_type == "Quick Crawl":
            with st.spinner("Running quick crawl..."):
                result = web_crawler.comprehensive_crawl([
                    "AI news", "Python programming", "FastAPI"
                ])
                st.session_state.last_crawl = result
        
        elif crawler_type == "Custom Search" and custom_queries:
            with st.spinner("Running custom crawl..."):
                result = web_crawler.comprehensive_crawl(custom_queries)
                st.session_state.last_crawl = result
        
        elif crawler_type == "Comprehensive Crawl":
            with st.spinner("Running comprehensive crawl (this may take a while)..."):
                result = web_crawler.comprehensive_crawl(use_paid_apis=True)
                st.session_state.last_crawl = result
        
        st.rerun()

# Main interface with enhanced tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🔍 RAG Query", 
    "🤖 Model Orchestration", 
    "🕷️ Web Crawler", 
    "📊 System Status",
    "🗄️ Database Explorer"
])

with tab1:
    st.header("RAG-Enhanced Query Interface")
    
    query = st.text_area("Enter your query:", height=100)
    
    col_settings1, col_settings2 = st.columns(2)
    with col_settings1:
        priority = st.selectbox("Priority:", ["balanced", "speed", "accuracy"])
    with col_settings2:
        n_results = st.slider("Documents to retrieve:", 1, 10, 3)
    
    comparison_mode = st.radio(
        "Response Mode:",
        ["RAG Only", "No RAG Only", "Side-by-Side Comparison"]
    )
    
    if st.button("Submit Query", type="primary"):
        if query.strip():
            if comparison_mode == "Side-by-Side Comparison":
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("🔍 With RAG (Context-Enhanced)")
                    with st.spinner("Processing with RAG..."):
                        rag_result = rag_orchestrator.search_and_generate(
                            query=query, n_results=n_results, priority=priority
                        )
                    
                    if rag_result.get("success", False):
                        st.write(rag_result["model_response"])
                        st.caption(f"Model: {rag_result['model_used']} | "
                                 f"Time: {rag_result['response_time']:.2f}s | "
                                 f"Docs: {rag_result['rag_metadata']['n_documents_retrieved']}")
                        
                        with st.expander("📖 Retrieved Context"):
                            for i, doc in enumerate(rag_result["retrieved_documents"]):
                                st.write(f"**Doc {i+1}:** {doc[:200]}...")
                
                with col2:
                    st.subheader("🤖 Without RAG (Model Only)")
                    with st.spinner("Processing without RAG..."):
                        no_rag_result = rag_orchestrator.simple_chat(query, use_rag=False)
                    
                    if no_rag_result.get("success", False):
                        st.write(no_rag_result["model_response"])
                        st.caption(f"Model: {no_rag_result['model_used']} | "
                                 f"Time: {no_rag_result['response_time']:.2f}s")
            
            elif comparison_mode == "RAG Only":
                with st.spinner("Processing with RAG..."):
                    result = rag_orchestrator.search_and_generate(query, n_results, priority)
                
                if result.get("success", False):
                    st.subheader("Response")
                    st.write(result["model_response"])
                    
                    col_metric1, col_metric2, col_metric3 = st.columns(3)
                    with col_metric1:
                        st.metric("Model Used", result["model_used"])
                    with col_metric2:
                        st.metric("Response Time", f"{result['response_time']:.2f}s")
                    with col_metric3:
                        st.metric("Documents Used", result["rag_metadata"]["n_documents_retrieved"])

with tab2:
    st.header("🤖 Model Orchestration")
    
    st.subheader("Direct Model Query")
    direct_query = st.text_area("Query for model orchestration:", height=80)
    
    col1, col2 = st.columns(2)
    with col1:
        orchestration_priority = st.selectbox("Priority:", ["balanced", "speed", "accuracy"], key="orch")
    with col2:
        force_model = st.selectbox("Force specific model (optional):", 
            ["Auto-select"] + list(rag_orchestrator.model_orchestrator.model_pool.models.keys())
        )
    
    if st.button("Execute Query"):
        if direct_query.strip():
            with st.spinner("Processing query..."):
                user_pref = None if force_model == "Auto-select" else force_model
                result = rag_orchestrator.model_orchestrator.process_request_sync(
                    direct_query, orchestration_priority, user_pref
                )
            
            if result.get("success", False):
                st.success(f"Query processed by: {result['model']}")
                st.write(result["response"])
                st.caption(f"Response time: {result['response_time']:.2f}s")

with tab3:
    st.header("🕷️ Web Crawler Status & Results")
    
    # Show last crawl results
    if 'last_crawl' in st.session_state:
        result = st.session_state.last_crawl
        
        if result.get("success", False):
            st.success(f"Last crawl successful!")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Items Processed", result["items_processed"])
            with col2:
                st.metric("Documents Created", result["documents_created"])
            with col3:
                st.metric("APIs Used", len(result.get("used_apis", [])))
            
            # Show which APIs were used
            st.subheader("Data Sources")
            for api in result.get("used_apis", []):
                st.success(f"✅ {api}")
            
            for api in result.get("skipped_apis", []):
                st.warning(f"⏭️ {api} (skipped)")
        
        else:
            st.error(f"Last crawl failed: {result.get('message', 'Unknown error')}")
    
    # Manual crawler controls
    st.subheader("Manual Crawler Operations")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Crawl Tech News"):
            with st.spinner("Crawling tech news..."):
                result = web_crawler.search_duckduckgo("AI technology news", 5)
                if result:
                    web_crawler.document_processor.ingest_crawled_data(result)
                    st.success(f"Crawled {len(result)} tech articles")
    
    with col2:
        if st.button("Crawl Programming Content"):
            with st.spinner("Crawling programming content..."):
                so_result = web_crawler.crawl_stackoverflow_questions(['python', 'fastapi'], 5)
                if so_result:
                    web_crawler.document_processor.ingest_crawled_data(so_result)
                    st.success(f"Crawled {len(so_result)} StackOverflow questions")

with tab4:
    st.header("📊 Complete System Status")
    
    # Overall system metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("🗄️ Knowledge Base")
        db_stats = rag_orchestrator.chroma_manager.get_collection_stats()
        st.metric("Total Documents", db_stats["total_documents"])
        
        # Show document sources breakdown
        results = rag_orchestrator.chroma_manager.collection.get(include=["metadatas"])
        source_types = {}
        for metadata in results["metadatas"]:
            source_type = metadata.get("source_type", "unknown")
            source_types[source_type] = source_types.get(source_type, 0) + 1
        
        for source_type, count in source_types.items():
            st.caption(f"{source_type}: {count} docs")
    
    with col2:
        st.subheader("🤖 Model Orchestration")
        orch_stats = rag_orchestrator.model_orchestrator.get_system_status()
        st.metric("Available Models", orch_stats["model_pool"]["available_models"])
        st.metric("Total Requests", orch_stats["orchestration"]["total_requests"])
        st.metric("System Load", f"{orch_stats['system_load']:.2f}")
    
    with col3:
        st.subheader("🕷️ Crawler Activity")
        if 'last_crawl' in st.session_state:
            crawl_data = st.session_state.last_crawl
            st.metric("Last Crawl Items", crawl_data.get("items_processed", 0))
            st.metric("Data Sources", len(crawl_data.get("used_apis", [])))
        else:
            st.info("No crawl activity yet")

with tab5:
    st.header("🗄️ Database Explorer")
    
    # Enhanced database browser
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Filter Options")
        
        # Get all source types for filtering
        results = rag_orchestrator.chroma_manager.collection.get(include=["metadatas"])
        source_types = set()
        for metadata in results["metadatas"]:
            source_types.add(metadata.get("source_type", "unknown"))
        
        selected_source = st.selectbox("Filter by source:", ["All"] + sorted(list(source_types)))
        
        # Search functionality
        search_query = st.text_input("Search documents:")
        max_results = st.slider("Max results:", 5, 50, 20)
    
    with col2:
        st.subheader("Document Browser")
        
        if search_query:
            # Semantic search
            search_results = rag_orchestrator.chroma_manager.search_documents(search_query, max_results)
            st.write(f"Found {len(search_results['documents'])} results for: '{search_query}'")
            
            for i, (doc, distance, metadata) in enumerate(zip(
                search_results["documents"],
                search_results["distances"],
                search_results.get("metadatas", [{}] * len(search_results["documents"]))
            )):
                with st.expander(f"Result {i+1} (Similarity: {1-distance:.3f})"):
                    st.write(f"**Source:** {metadata.get('source_type', 'unknown')}")
                    st.write(f"**Title:** {metadata.get('title', 'No title')}")
                    st.write(f"**Content:** {doc}")
        
        else:
            # Browse by source type
            if selected_source == "All":
                docs = rag_orchestrator.chroma_manager.collection.get(
                    limit=max_results, include=["documents", "metadatas"]
                )
            else:
                docs = rag_orchestrator.chroma_manager.collection.get(
                    where={"source_type": selected_source},
                    limit=max_results,
                    include=["documents", "metadatas"]
                )
            
            st.write(f"Showing {len(docs['documents'])} documents")
            
            for i, (doc, metadata) in enumerate(zip(docs["documents"], docs["metadatas"])):
                with st.expander(f"{metadata.get('title', f'Document {i+1}')}"):
                    st.write(f"**Source:** {metadata.get('source_type', 'unknown')}")
                    st.write(f"**URL:** {metadata.get('source', 'N/A')}")
                    st.write(f"**Content:** {doc[:500]}...")

# Footer
st.markdown("---")
st.caption("🤖 Complete AI Orchestration System - Model Management | RAG | Web Crawling | Real-time Data")