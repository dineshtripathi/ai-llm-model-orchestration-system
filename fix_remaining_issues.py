#!/usr/bin/env python3
"""Fix remaining linting issues."""

import os
import re


def fix_file_imports(file_path):
    """Move sys.path.append to after standard library imports."""
    if not os.path.exists(file_path):
        return

    with open(file_path, "r") as f:
        lines = f.readlines()

    # Find sys.path.append line
    sys_path_line = None
    sys_path_index = -1

    for i, line in enumerate(lines):
        if "sys.path.append" in line:
            sys_path_line = line
            sys_path_index = i
            break

    if sys_path_line:
        # Remove the sys.path.append line
        lines.pop(sys_path_index)

        # Find where to insert it (after import sys, os)
        insert_index = 0
        for i, line in enumerate(lines):
            if line.strip().startswith("import") and ("sys" in line or "os" in line):
                insert_index = i + 1
                continue
            elif line.strip().startswith("from") and not line.strip().startswith(
                "from ."
            ):
                continue
            elif line.strip() and not line.strip().startswith("#"):
                break

        # Insert sys.path.append after standard imports but before local imports
        lines.insert(insert_index, "\n# Add project root to Python path\n")
        lines.insert(insert_index + 1, sys_path_line)
        lines.insert(insert_index + 2, "\n")

    with open(file_path, "w") as f:
        f.writelines(lines)


# Files to fix
files_to_fix = [
    "api/orchestration_api.py",
    "api/rag_api.py",
    "dashboard/rag_dashboard.py",
    "orchestration/core/orchestrator.py",
    "orchestration/core/router/model_router.py",
    "rag/crawler/api_crawler.py",
    "rag/crawler/web_crawler.py",
    "rag/ingestion/document_processor.py",
    "rag/retrieval/rag_orchestrator.py",
    "rag/viewer/chroma_viewer.py",
    "tests/test_orchestration.py",
    "tests/test_rag.py",
]

for file_path in files_to_fix:
    print(f"Fixing imports in {file_path}")
    fix_file_imports(file_path)

print("Import fixes complete!")
