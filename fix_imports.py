#!/usr/bin/env python3
"""Fix common import issues."""

import os
import re


def remove_unused_imports(file_path, unused_imports):
    """Remove unused imports from file."""
    with open(file_path, "r") as f:
        content = f.read()

    for imp in unused_imports:
        # Remove entire import line
        pattern = rf"^import {imp}.*\n"
        content = re.sub(pattern, "", content, flags=re.MULTILINE)

        # Remove from 'from' imports
        pattern = rf", {imp}"
        content = re.sub(pattern, "", content)

        pattern = rf"{imp}, "
        content = re.sub(pattern, "", content)

        # Remove single import from 'from' statement
        pattern = rf"^from .* import {imp}\n"
        content = re.sub(pattern, "", content, flags=re.MULTILINE)

    with open(file_path, "w") as f:
        f.write(content)


# Fix specific files
fixes = {
    "dashboard/orchestration_dashboard.py": ["json"],
    "dashboard/rag_dashboard.py": ["json", "requests"],
    "orchestration/config/settings.py": ["List"],
    "orchestration/core/balancer/load_balancer.py": ["threading", "Empty", "List"],
    "orchestration/core/orchestrator.py": ["List", "Union"],
    "orchestration/core/pool/model_pool.py": ["json", "threading"],
    "orchestration/core/router/model_router.py": ["List"],
    "rag/crawler/api_crawler.py": ["json", "Optional"],
    "rag/crawler/web_crawler.py": ["urljoin", "urlparse"],
    "rag/ingestion/document_processor.py": ["Path", "Optional"],
    "rag/retrieval/rag_orchestrator.py": ["List", "Optional"],
    "rag/vector_store/chroma_manager.py": ["Optional", "Settings"],
    "tests/test_orchestration.py": ["pytest"],
    "tests/test_rag.py": ["pytest", "shutil"],
}

for file_path, imports in fixes.items():
    if os.path.exists(file_path):
        print(f"Fixing {file_path}")
        remove_unused_imports(file_path, imports)
