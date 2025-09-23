import json
import time

import requests
import streamlit as st

# Configure the page
st.set_page_config(
    page_title="AI Model Orchestration Dashboard", page_icon="🤖", layout="wide"
)

# API endpoint
API_BASE = "http://localhost:8001"


def get_system_status():
    """Get current system status from orchestration API"""
    try:
        response = requests.get(f"{API_BASE}/system/status")
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None


def get_recommendations(query):
    """Get routing recommendations for a query"""
    try:
        response = requests.get(f"{API_BASE}/recommendations/{query}")
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None


def orchestrate_query(query, priority="balanced", timeout=60):
    """Send query to orchestration API"""
    try:
        payload = {"query": query, "priority": priority, "timeout": timeout}
        response = requests.post(f"{API_BASE}/orchestrate", json=payload)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"API Error: {response.status_code}", "success": False}
    except Exception as e:
        return {"error": str(e), "success": False}


# Main dashboard
st.title("AI Model Orchestration Dashboard")

# Sidebar for system status
with st.sidebar:
    st.header("System Status")

    if st.button("Refresh Status"):
        st.rerun()

    status = get_system_status()
    if status:
        st.metric("Available Models", status["model_pool"]["available_models"])
        st.metric("Total Models", status["model_pool"]["total_models"])
        st.metric("System Load", f"{status['system_load']:.2f}")
        st.metric("Total Requests", status["orchestration"]["total_requests"])

        # Model status details
        st.subheader("Model Details")
        for model, data in status["model_pool"]["model_status"].items():
            color = "🟢" if data["status"] == "loaded" else "🔴"
            st.write(f"{color} {model}")
            st.caption(f"Category: {data['category']}, Size: {data['size_gb']}GB")
    else:
        st.error(
            "Unable to connect to orchestration API. Make sure it's running on port 8001."
        )

# Main interface
col1, col2 = st.columns([2, 1])

with col1:
    st.header("Query Interface")

    # Query input
    query = st.text_area("Enter your query:", height=100, placeholder="Ask anything...")

    # Priority selection
    priority = st.selectbox("Priority:", ["balanced", "speed", "accuracy"])

    # Advanced options in expander
    with st.expander("Advanced Options"):
        timeout = st.slider("Timeout (seconds):", 10, 180, 60)
        show_routing = st.checkbox("Show routing recommendations", True)

    # Submit button
    if st.button("Process Query", type="primary"):
        if query.strip():
            # Show routing recommendations if enabled
            if show_routing:
                with st.spinner("Analyzing query..."):
                    recommendations = get_recommendations(query)
                    if recommendations:
                        st.info(
                            f"**Routing Decision:**\n"
                            f"- Recommended Model: {recommendations['recommended_model']}\n"
                            f"- Category: {recommendations['category']}\n"
                            f"- Estimated Wait: {recommendations['estimated_wait_time']:.1f}s"
                        )

            # Process the query
            with st.spinner("Processing query..."):
                start_time = time.time()
                result = orchestrate_query(query, priority, timeout)
                end_time = time.time()

                if result.get("success", False):
                    st.success("Query processed successfully!")

                    # Display results
                    st.subheader("Response")
                    st.write(result["response"])

                    # Performance metrics
                    col_metric1, col_metric2, col_metric3 = st.columns(3)
                    with col_metric1:
                        st.metric("Model Used", result["model_used"])
                    with col_metric2:
                        st.metric("Response Time", f"{result['response_time']:.2f}s")
                    with col_metric3:
                        st.metric("Total Time", f"{end_time - start_time:.2f}s")

                else:
                    st.error(f"Query failed: {result.get('error', 'Unknown error')}")
        else:
            st.warning("Please enter a query.")

with col2:
    st.header("Quick Tests")

    # Predefined test queries
    test_queries = [
        "Hello, how are you?",
        "Write a Python function to sort a list",
        "Explain machine learning in simple terms",
        "Analyze the pros and cons of renewable energy",
        "What is 2 + 2?",
        "Debug this Python code: print('hello world'",
    ]

    st.subheader("Sample Queries")
    for test_query in test_queries:
        if st.button(test_query, key=f"test_{test_query[:10]}"):
            st.session_state.query = test_query
            st.rerun()

    # Performance monitoring
    st.subheader("Performance Monitor")
    if status and status["orchestration"]["total_requests"] > 0:
        success_rate = (
            status["orchestration"]["successful_routes"]
            / status["orchestration"]["total_requests"]
            * 100
        )
        st.metric("Success Rate", f"{success_rate:.1f}%")
        st.metric(
            "Avg Routing Time",
            f"{status['orchestration']['average_routing_time']:.3f}s",
        )

# Auto-populate query from session state
if "query" in st.session_state:
    st.session_state.query = st.session_state.get("query", "")

# Footer
st.markdown("---")
st.caption("AI Model Orchestration System - Enterprise Grade Model Management")
