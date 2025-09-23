#!/usr/bin/env python3
"""Development tools for code quality."""

import subprocess
import sys


def run_command(cmd, description):
    """Run a command and report results."""
    print(f"\n{'='*50}")
    print(f"Running: {description}")
    print(f"{'='*50}")

    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)

    return result.returncode == 0


def main():
    """Run all development tools."""
    commands = [
        ("isort . --check-only --dif", "Import sorting check"),
        ("black . --check --diff", "Code formatting check"),
        ("flake8 .", "Linting check"),
        ("pytest tests/ -v", "Running tests"),
    ]

    all_passed = True
    for cmd, desc in commands:
        if not run_command(cmd, desc):
            all_passed = False

    if all_passed:
        print("\n✅ All checks passed!")
    else:
        print("\n❌ Some checks failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
